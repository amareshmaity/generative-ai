# Project 2: File Upload API for Document Processing

This project is a beginner-friendly FastAPI backend for uploading and processing documents.

It is designed to practice:

* file uploads
* request and response design
* API key authentication
* environment-based configuration
* logging and exception handling
* simple document processing logic
* API testing

## Project idea

This API accepts documents such as:

* `.txt`
* `.csv`
* `.pdf`

It stores uploaded files locally, tracks metadata, and exposes a small processing workflow.

## Endpoints

* `GET /health`
* `POST /documents/upload`
* `GET /documents`
* `GET /documents/{document_id}`
* `POST /documents/{document_id}/process`

## Project structure

```text
project_2/
  app/
    core/
      config.py
      logging_config.py
      security.py
    routers/
      documents.py
      health.py
    schemas/
      document.py
    services/
      document_service.py
    main.py
  data/
    uploads/
  tests/
    test_app.py
  .env.example
  requirements.txt
  README.md
```

## Setup

```bash
pip install -r requirements.txt
```

Create a local `.env` file if you want custom values.
You can copy from `.env.example`.

## Run the app

```bash
uvicorn app.main:app --reload
```

## Protected endpoints

Document endpoints require:

```text
x-api-key: level1-upload-key
```

## Run tests

```bash
pytest
```

## Notes

This project keeps storage local and simple for learning purposes.
PDF processing here is intentionally lightweight and metadata-focused because real PDF extraction usually needs dedicated libraries and more handling.
