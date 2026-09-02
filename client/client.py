"""Simple client script for CloudRelay Phase 1.

Usage:
    python -m client.client <image_path> <operation> [--width W --height H --quality Q]

Examples:
    python -m client.client photo.jpg resize --width 512 --height 512
    python -m client.client photo.png grayscale
    python -m client.client photo.jpg compress --quality 30
    python -m client.client photo.png edge_detection
"""

import argparse
import sys
from pathlib import Path

import requests

DEFAULT_BASE_URL = "http://127.0.0.1:8000"


def check_health(base_url: str) -> bool:
    try:
        resp = requests.get(f"{base_url}/health", timeout=5)
        resp.raise_for_status()
        data = resp.json()
        print(f"Server status: {data['status']} (v{data['version']})")
        return True
    except requests.ConnectionError:
        print("ERROR: Cannot connect to the server. Is it running?")
        print("  Start it with:  uvicorn app.main:app --reload")
        return False
    except Exception as exc:
        print(f"ERROR: Health check failed: {exc}")
        return False


def send_image(
    image_path: Path,
    operation: str,
    base_url: str,
    width: int | None = None,
    height: int | None = None,
    quality: int | None = None,
) -> dict:
    url = f"{base_url}/process-image"

    data: dict = {"operation": operation}
    if width is not None:
        data["width"] = str(width)
    if height is not None:
        data["height"] = str(height)
    if quality is not None:
        data["quality"] = str(quality)

    with open(image_path, "rb") as f:
        files = {"file": (image_path.name, f, "application/octet-stream")}
        resp = requests.post(url, data=data, files=files, timeout=60)

    resp.raise_for_status()
    return resp.json()


def main() -> None:
    parser = argparse.ArgumentParser(description="CloudRelay Client - Upload an image for processing")
    parser.add_argument("image", type=Path, help="Path to the image file")
    parser.add_argument("operation", type=str, help="Operation: resize, grayscale, compress, edge_detection")
    parser.add_argument("--width", type=int, default=None, help="Resize width")
    parser.add_argument("--height", type=int, default=None, help="Resize height")
    parser.add_argument("--quality", type=int, default=None, help="Compression quality (1-100)")
    parser.add_argument("--server", type=str, default=DEFAULT_BASE_URL, help="Server URL")
    args = parser.parse_args()

    base_url = args.server

    if not args.image.exists():
        print(f"ERROR: File not found: {args.image}")
        sys.exit(1)

    if not check_health(base_url):
        sys.exit(1)

    print(f"\nUploading '{args.image.name}' with operation '{args.operation}'...")
    try:
        result = send_image(args.image, args.operation, base_url, args.width, args.height, args.quality)
    except requests.HTTPError as exc:
        print(f"ERROR: {exc}")
        if exc.response is not None:
            print(f"  Response: {exc.response.text}")
        sys.exit(1)

    print("\n--- Server Response ---")
    for key, value in result.items():
        print(f"  {key}: {value}")
    print("-----------------------")
    print(f"\nResult saved to: outputs/{result['result_filename']}")


if __name__ == "__main__":
    main()
