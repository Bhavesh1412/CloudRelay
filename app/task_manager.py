"""In-memory task lifecycle management for asynchronous image jobs."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any

from app.image_processor import process_image

_tasks: dict[str, dict[str, Any]] = {}
_lock = Lock()
_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="cloudrelay-worker")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_task(
    *, task_id: str, operation: str, original_filename: str, upload_path: Path,
    result_path: Path, width: int | None, height: int | None, quality: int | None,
) -> dict[str, Any]:
    task = {
        "task_id": task_id, "status": "pending", "operation": operation,
        "original_filename": original_filename, "result_filename": result_path.name,
        "upload_path": upload_path, "result_path": result_path,
        "width": width, "height": height, "quality": quality, "created_at": _now(),
    }
    with _lock:
        _tasks[task_id] = task
    _executor.submit(_run_task, task_id)
    return public_task(task)


def _run_task(task_id: str) -> None:
    with _lock:
        task = _tasks.get(task_id)
        if task is None:
            return
        task["status"] = "processing"
        task["started_at"] = _now()
    try:
        process_image(
            image_path=task["upload_path"], operation=task["operation"],
            output_path=task["result_path"], width=task["width"],
            height=task["height"], quality=task["quality"],
        )
    except Exception as exc:  # pragma: no cover - exercised through API failure paths
        with _lock:
            task["status"] = "failed"
            task["error"] = str(exc)
            task["finished_at"] = _now()
        return
    with _lock:
        task["status"] = "completed"
        task["finished_at"] = _now()


def get_task(task_id: str) -> dict[str, Any] | None:
    with _lock:
        task = _tasks.get(task_id)
        return public_task(task) if task else None


def get_task_internal(task_id: str) -> dict[str, Any] | None:
    with _lock:
        return _tasks.get(task_id)


def public_task(task: dict[str, Any]) -> dict[str, Any]:
    result = {key: value for key, value in task.items()
              if key not in {"upload_path", "result_path", "width", "height", "quality"}}
    if task.get("status") == "completed":
        result["result_url"] = f"/tasks/{task['task_id']}/result"
    return result
