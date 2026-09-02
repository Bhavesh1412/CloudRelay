import time
import uuid
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from app.config import ALLOWED_EXTENSIONS, OUTPUT_DIR, SUPPORTED_OPERATIONS, UPLOAD_DIR
from app.image_processor import process_image

app = FastAPI(
    title="CloudRelay - Task Offloading Server",
    description="A local distributed task-offloading system for image processing.",
    version="0.1.0",
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "healthy", "version": "0.1.0", "phase": "1"}


@app.post("/process-image")
async def process_image_endpoint(
    file: UploadFile = File(...),
    operation: str = Form(...),
    width: int | None = Form(default=None),
    height: int | None = Form(default=None),
    quality: int | None = Form(default=None),
) -> JSONResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type '{ext}'. Allowed: {sorted(ALLOWED_EXTENSIONS)}",
        )

    if operation not in SUPPORTED_OPERATIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid operation '{operation}'. Supported: {list(SUPPORTED_OPERATIONS.keys())}",
        )

    task_id = uuid.uuid4().hex[:12]
    timestamp = int(time.time())
    upload_path = UPLOAD_DIR / f"{task_id}_{file.filename}"

    contents = await file.read()
    upload_path.write_bytes(contents)

    result_filename = f"{task_id}_{operation}_{Path(file.filename).stem}{ext}"
    result_path = OUTPUT_DIR / result_filename

    start = time.perf_counter()
    try:
        process_image(
            image_path=upload_path,
            operation=operation,
            output_path=result_path,
            width=width,
            height=height,
            quality=quality,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Processing failed: {exc}") from exc
    elapsed = round(time.perf_counter() - start, 4)

    return JSONResponse(
        content={
            "task_id": task_id,
            "status": "completed",
            "operation": operation,
            "original_filename": file.filename,
            "result_filename": result_filename,
            "processing_time_seconds": elapsed,
            "result_path": str(result_path),
        }
    )
