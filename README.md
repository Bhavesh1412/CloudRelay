# CloudRelay - Local Distributed Task Offloading System

A local distributed task-offloading system that simulates a client with limited resources communicating with a powerful server. The client submits computationally expensive tasks (image processing) to an API server instead of processing them locally.

## Client-Server Offloading Concept

In real-world edge/cloud computing, resource-constrained devices (phones, IoT sensors, embedded systems) offload heavy computation to more powerful servers. This project simulates that pattern locally:

1. **Client** has an image that needs processing
2. Instead of processing locally, the client sends it to the **server**
3. The server processes the image and returns the result
4. Later phases will compare local vs server processing time

## Planned Architecture

```
Client application
    |
API server
    |
Task queue
    |
Load balancer / worker dispatcher
    |
Worker 1, Worker 2, Worker 3
    |
Result storage
    |
Client downloads the result
```

Phase 1 implements only the client and a synchronous single-server baseline.

## Phase 1 - What is Included

- FastAPI server with `/health` and `/process-image` endpoints
- Image processing operations: resize, grayscale, compress, edge detection
- Input validation (file type, operation name)
- A Python client script for uploading images via CLI
- Automated tests for all endpoints
- Simple file-based result storage (`outputs/` directory)

## Future Phases

- **Phase 2:** Asynchronous task processing with status polling
- **Phase 3:** Redis + Celery task queue
- **Phase 4:** Multiple worker processes / Docker containers
- **Phase 5:** Load balancing across workers
- **Phase 6:** Processing-time comparison (local vs server)
- **Phase 7:** Dashboard showing worker activity and performance
- **Phase 8:** Authentication, deployment, and monitoring

## Installation

```bash
# Clone the repository
git clone <repo-url>
cd CloudRelay

# Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

## Running the Server

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The server will start at `http://127.0.0.1:8000`. Interactive API docs are available at `http://127.0.0.1:8000/docs`.

## Using the Client

```bash
# Resize an image
python -m client.client photo.jpg resize --width 512 --height 512

# Convert to grayscale
python -m client.client photo.png grayscale

# Compress an image
python -m client.client photo.jpg compress --quality 30

# Edge detection
python -m client.client photo.png edge_detection
```

Processed images are saved to the `outputs/` directory.

## Running Tests

```bash
pytest tests/ -v
```

## Project Structure

```
CloudRelay/
  app/
    __init__.py
    main.py              # FastAPI server
    image_processor.py   # Image processing functions
    config.py            # Project configuration
  client/
    __init__.py
    client.py            # CLI client script
  tests/
    __init__.py
    test_api.py          # Automated tests
  uploads/               # Uploaded images (runtime)
  outputs/               # Processed results (runtime)
  requirements.txt
  README.md
  .gitignore
```

## Supported Operations

| Operation       | Description                          | Parameters           |
|----------------|--------------------------------------|----------------------|
| resize         | Resize to given dimensions           | width, height        |
| grayscale      | Convert to grayscale                 | -                    |
| compress       | Compress with reduced quality        | quality (1-100)      |
| edge_detection | Apply edge detection filter          | -                    |

## License

This project is for educational and research purposes.
