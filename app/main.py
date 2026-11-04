import uuid
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse

from app.config import ALLOWED_EXTENSIONS, OUTPUT_DIR, SUPPORTED_OPERATIONS, UPLOAD_DIR
from app.task_manager import create_task, get_task, get_task_internal

app = FastAPI(
    title="CloudRelay - Task Offloading Server",
    description="A local distributed task-offloading system for image processing.",
    version="0.2.0",
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "healthy", "version": "0.2.0", "phase": "2"}


@app.post("/process-image", status_code=202)
async def process_image_endpoint(
    file: UploadFile = File(...), operation: str = Form(...),
    width: int | None = Form(default=None), height: int | None = Form(default=None),
    quality: int | None = Form(default=None),
) -> JSONResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Invalid file type '{ext}'. Allowed: {sorted(ALLOWED_EXTENSIONS)}")
    if operation not in SUPPORTED_OPERATIONS:
        raise HTTPException(status_code=400, detail=f"Invalid operation '{operation}'. Supported: {list(SUPPORTED_OPERATIONS.keys())}")

    task_id = uuid.uuid4().hex[:12]
    upload_path = UPLOAD_DIR / f"{task_id}_{Path(file.filename).name}"
    result_filename = f"{task_id}_{operation}_{Path(file.filename).stem}{ext}"
    result_path = OUTPUT_DIR / result_filename
    upload_path.write_bytes(await file.read())
    task = create_task(
        task_id=task_id, operation=operation, original_filename=file.filename,
        upload_path=upload_path, result_path=result_path, width=width,
        height=height, quality=quality,
    )
    return JSONResponse(content=task, status_code=202)


@app.get("/tasks/{task_id}")
def task_status(task_id: str) -> dict:
    task = get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.get("/tasks/{task_id}/result")
def task_result(task_id: str) -> FileResponse:
    task = get_task_internal(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    if task["status"] != "completed":
        raise HTTPException(status_code=409, detail=f"Task is not complete (status: {task['status']})")
    if not task["result_path"].exists():
        raise HTTPException(status_code=404, detail="Result file not found")
    return FileResponse(task["result_path"], filename=task["result_filename"])
