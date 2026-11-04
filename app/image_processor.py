from io import BytesIO
from pathlib import Path
from typing import Any

from PIL import Image, ImageFilter

from app.config import (
    DEFAULT_COMPRESS_QUALITY,
    DEFAULT_RESIZE_HEIGHT,
    DEFAULT_RESIZE_WIDTH,
)


def resize(image: Image.Image, width: int | None = None, height: int | None = None) -> Image.Image:
    w = width or DEFAULT_RESIZE_WIDTH
    h = height or DEFAULT_RESIZE_HEIGHT
    return image.resize((w, h), Image.LANCZOS)


def grayscale(image: Image.Image) -> Image.Image:
    return image.convert("L")


def compress(image: Image.Image, quality: int | None = None) -> Image.Image:
    q = quality or DEFAULT_COMPRESS_QUALITY
    buffer = BytesIO()
    image.convert("RGB").save(buffer, format="JPEG", quality=q)
    buffer.seek(0)
    return Image.open(buffer).copy()


def edge_detection(image: Image.Image) -> Image.Image:
    img = image.convert("L")
    return img.filter(ImageFilter.FIND_EDGES)


OPERATION_MAP: dict[str, Any] = {
    "resize": resize,
    "grayscale": grayscale,
    "compress": compress,
    "edge_detection": edge_detection,
}


def process_image(
    image_path: Path,
    operation: str,
    output_path: Path,
    width: int | None = None,
    height: int | None = None,
    quality: int | None = None,
) -> Path:
    if operation not in OPERATION_MAP:
        raise ValueError(f"Unknown operation: {operation}")

    img = Image.open(image_path)
    handler = OPERATION_MAP[operation]

    kwargs: dict[str, Any] = {}
    if operation == "resize":
        kwargs["width"] = width
        kwargs["height"] = height
    elif operation == "compress":
        kwargs["quality"] = quality

    result = handler(img, **kwargs)

    ext = output_path.suffix.lower()
    if ext in (".jpg", ".jpeg"):
        result = result.convert("RGB")

    result.save(output_path)
    return output_path
