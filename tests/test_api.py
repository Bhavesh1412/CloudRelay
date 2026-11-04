import io
import time

from fastapi.testclient import TestClient
from PIL import Image

from app.main import app

client = TestClient(app)


def _create_test_image(fmt: str = "PNG", size: tuple[int, int] = (100, 100)) -> io.BytesIO:
    img = Image.new("RGB", size, color=(255, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    buf.seek(0)
    return buf


def _submit(operation: str, filename: str = "test.png", **params: str) -> dict:
    resp = client.post(
        "/process-image", data={"operation": operation, **params},
        files={"file": (filename, _create_test_image(), "image/png")},
    )
    assert resp.status_code == 202
    return resp.json()


def _wait_for_completion(task_id: str) -> dict:
    for _ in range(50):
        task = client.get(f"/tasks/{task_id}").json()
        if task["status"] in {"completed", "failed"}:
            return task
        time.sleep(0.01)
    raise AssertionError("Task did not finish in time")


def test_health_returns_phase_two() -> None:
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "healthy", "version": "0.2.0", "phase": "2"}


def test_submit_and_poll_resize() -> None:
    task = _submit("resize", width="64", height="64")
    assert task["status"] in {"pending", "processing", "completed"}
    completed = _wait_for_completion(task["task_id"])
    assert completed["status"] == "completed"
    result = client.get(completed["result_url"])
    assert result.status_code == 200
    assert result.headers["content-type"] == "image/png"


def test_all_operations_complete() -> None:
    for operation, params in [
        ("grayscale", {}), ("compress", {"quality": "30"}), ("edge_detection", {}),
    ]:
        task = _submit(operation, **params)
        assert _wait_for_completion(task["task_id"])["status"] == "completed"


def test_unknown_task_and_invalid_inputs() -> None:
    assert client.get("/tasks/missing").status_code == 404
    assert client.post(
        "/process-image", data={"operation": "blur"},
        files={"file": ("test.png", _create_test_image(), "image/png")},
    ).status_code == 400
    assert client.post(
        "/process-image", data={"operation": "grayscale"},
        files={"file": ("test.exe", io.BytesIO(b"MZ"), "application/octet-stream")},
    ).status_code == 400
