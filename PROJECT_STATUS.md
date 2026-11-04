# PROJECT_STATUS.md

## Project Goal

Build a local distributed task-offloading system that simulates a client with limited resources communicating with a powerful server. The client submits computationally expensive tasks (image processing) to an API server instead of processing them locally, demonstrating client-server communication, computational offloading, load balancing, and performance comparison.

## Current Phase

**Phase 2** - Asynchronous task processing with status polling and result downloads.

## Completed Work

- Project structure created from scratch (empty workspace)
- FastAPI server with `GET /health`, `POST /process-image`, `GET /tasks/{task_id}`, and `GET /tasks/{task_id}/result`
- Image processing module supporting 4 operations: resize, grayscale, compress, edge_detection
- Input validation for file type and operation name
- In-memory task tracking and a four-worker thread pool
- File-based result storage in `outputs/` directory
- CLI client script with argparse for all operations
- 9 automated pytest tests (all passing)
- Manual end-to-end test passed for all 4 operations
- README.md with full documentation
- requirements.txt with all dependencies
- .gitignore for Python project

## Current Architecture

```
Client (CLI)
    |
FastAPI Server (async task submission)
    |
In-memory task manager / worker pool
    |
Image processing (Pillow)
    |
File-based result storage (outputs/)
```

## Files and Their Purposes

| File | Purpose |
|------|---------|
| `app/main.py` | FastAPI server with /health and /process-image endpoints |
| `app/image_processor.py` | Image processing functions (resize, grayscale, compress, edge_detection) |
| `app/config.py` | Project configuration (paths, allowed extensions, supported operations) |
| `app/__init__.py` | Package init |
| `client/client.py` | CLI client script for uploading images |
| `client/__init__.py` | Package init |
| `tests/test_api.py` | 9 automated tests covering all endpoints and validation |
| `tests/__init__.py` | Package init |
| `uploads/` | Stores uploaded images (runtime) |
| `outputs/` | Stores processed results (runtime) |
| `requirements.txt` | Python dependencies |
| `README.md` | Project documentation |
| `.gitignore` | Git ignore rules |
| `PROJECT_STATUS.md` | This file - project handoff summary |

## How to Run the Project

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Start the Server
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
API docs available at: `http://127.0.0.1:8000/docs`

### Run the Client
```bash
python -m client.client photo.jpg resize --width 512 --height 512
python -m client.client photo.png grayscale
python -m client.client photo.jpg compress --quality 30
python -m client.client photo.png edge_detection
```

### Run Tests
```bash
pytest tests/ -v
```

## Tests Completed

All 9 tests pass:
- `TestHealthEndpoint::test_health_returns_ok`
- `TestProcessImageResize::test_resize_success`
- `TestProcessImageGrayscale::test_grayscale_success`
- `TestProcessImageCompress::test_compress_success`
- `TestProcessImageEdgeDetection::test_edge_detection_success`
- `TestInvalidOperation::test_invalid_operation_rejected`
- `TestInvalidFileType::test_invalid_file_type_rejected`
- `TestInvalidFileType::test_no_extension_rejected`
- `TestNoFilename::test_empty_filename_rejected`

## Manual Test Results

All 4 operations successfully tested end-to-end:
- resize: 0.0192s
- grayscale: 0.0025s
- compress: 0.0049s
- edge_detection: 0.002s

## Known Issues

- The `compress` operation creates a temporary file `_temp_compress.jpg` that is not cleaned up after processing.
- PowerShell execution policy on this machine prevents venv activation scripts; dependencies were installed directly via system Python.
- The empty-filename test expects 400 or 422 depending on whether Starlette's multipart parser catches it first.

## Planned Future Phases

1. **Phase 3:** Redis + Celery task queue integration
2. **Phase 4:** Multiple worker processes / Docker containers
3. **Phase 5:** Load balancing across workers
4. **Phase 6:** Processing-time comparison (local vs server)
5. **Phase 7:** Dashboard showing worker activity and performance
6. **Phase 8:** Authentication, deployment, monitoring

## Important Assumptions

- All processing runs synchronously on a single server for Phase 1
- Images are stored locally in `uploads/` and `outputs/` (no database yet)
- The server runs on `127.0.0.1:8000` by default
- Only image files (PNG, JPG, JPEG, BMP, GIF, WEBP) are accepted
- Task IDs are generated using UUID4 (first 12 hex characters)
- Pillow is used for all image processing (no OpenCV yet)

---

## Handoff Summary for the Next Session

Phase 1 of the CloudRelay project is fully complete. The following work has been done so far:

1. **Project created from empty workspace** at `D:\CloudRelay`
2. **FastAPI server** (`app/main.py`) with `GET /health` and `POST /process-image` endpoints. The server validates file types, accepts operation parameters, processes images synchronously, saves results to `outputs/`, and returns JSON with task_id, status, operation, filenames, and processing time.
3. **Image processor** (`app/image_processor.py`) supporting 4 operations: resize (with width/height params), grayscale, compress (with quality param), and edge_detection. Uses Pillow for all processing.
4. **Configuration** (`app/config.py`) with allowed extensions, supported operations, output directories, and defaults.
5. **CLI client** (`client/client.py`) that sends images to the server, accepts all operation parameters, and prints the JSON response. Works via `python -m client.client <image> <operation>`.
6. **9 automated tests** (`tests/test_api.py`) all passing, covering health check, all 4 operations, invalid operation rejection, invalid file type rejection, no-extension rejection, and empty filename rejection.
7. **Documentation** in README.md, requirements.txt, .gitignore, and PROJECT_STATUS.md.
8. **Manual end-to-end test** completed successfully for all 4 operations.

**To continue the project, start with Phase 2: converting the synchronous processing to asynchronous task processing.** This would involve:
- Adding a task status tracking endpoint (e.g., `GET /tasks/{task_id}`)
- Converting the `/process-image` endpoint to accept the task, return immediately with a task_id, and process in background
- Adding a status field (pending, processing, completed, failed) to tasks
- Storing task metadata in memory (dict) initially, then migrating to a database later

All existing code is clean, modular, and ready for extension. The `app/` package structure supports adding new modules (e.g., `app/task_manager.py`, `app/models.py`) without modifying existing files.
