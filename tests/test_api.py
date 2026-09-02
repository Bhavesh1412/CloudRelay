import io

import pytest
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


class TestHealthEndpoint:
    def test_health_returns_ok(self) -> None:
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert data["version"] == "0.1.0"
        assert data["phase"] == "1"


class TestProcessImageResize:
    def test_resize_success(self) -> None:
        img_buf = _create_test_image()
        resp = client.post(
            "/process-image",
            data={"operation": "resize", "width": "64", "height": "64"},
            files={"file": ("test.png", img_buf, "image/png")},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "completed"
        assert data["operation"] == "resize"
        assert data["original_filename"] == "test.png"
        assert "result_filename" in data
        assert data["processing_time_seconds"] >= 0


class TestProcessImageGrayscale:
    def test_grayscale_success(self) -> None:
        img_buf = _create_test_image()
        resp = client.post(
            "/process-image",
            data={"operation": "grayscale"},
            files={"file": ("photo.jpg", img_buf, "image/jpeg")},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "completed"
        assert data["operation"] == "grayscale"


class TestProcessImageCompress:
    def test_compress_success(self) -> None:
        img_buf = _create_test_image()
        resp = client.post(
            "/process-image",
            data={"operation": "compress", "quality": "30"},
            files={"file": ("big.png", img_buf, "image/png")},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "completed"
        assert data["operation"] == "compress"


class TestProcessImageEdgeDetection:
    def test_edge_detection_success(self) -> None:
        img_buf = _create_test_image()
        resp = client.post(
            "/process-image",
            data={"operation": "edge_detection"},
            files={"file": ("edge.png", img_buf, "image/png")},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "completed"
        assert data["operation"] == "edge_detection"


class TestInvalidOperation:
    def test_invalid_operation_rejected(self) -> None:
        img_buf = _create_test_image()
        resp = client.post(
            "/process-image",
            data={"operation": "blur"},
            files={"file": ("test.png", img_buf, "image/png")},
        )
        assert resp.status_code == 400
        detail = resp.json()["detail"]
        assert "Invalid operation" in detail


class TestInvalidFileType:
    def test_invalid_file_type_rejected(self) -> None:
        resp = client.post(
            "/process-image",
            data={"operation": "grayscale"},
            files={"file": ("test.exe", io.BytesIO(b"MZ"), "application/octet-stream")},
        )
        assert resp.status_code == 400
        detail = resp.json()["detail"]
        assert "Invalid file type" in detail

    def test_no_extension_rejected(self) -> None:
        resp = client.post(
            "/process-image",
            data={"operation": "grayscale"},
            files={"file": ("noext", io.BytesIO(b"data"), "application/octet-stream")},
        )
        assert resp.status_code == 400


class TestNoFilename:
    def test_empty_filename_rejected(self) -> None:
        img_buf = _create_test_image()
        resp = client.post(
            "/process-image",
            data={"operation": "grayscale"},
            files={"file": ("", img_buf, "image/png")},
        )
        assert resp.status_code in (400, 422), f"Expected 400 or 422, got {resp.status_code}"
