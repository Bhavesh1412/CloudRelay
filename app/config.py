from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"

UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS: set[str] = {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp"}

SUPPORTED_OPERATIONS: dict[str, str] = {
    "resize": "Resize image to specified width and height",
    "grayscale": "Convert image to grayscale",
    "compress": "Compress image with reduced quality",
    "edge_detection": "Apply edge detection filter",
}

DEFAULT_RESIZE_WIDTH = 256
DEFAULT_RESIZE_HEIGHT = 256
DEFAULT_COMPRESS_QUALITY = 50
