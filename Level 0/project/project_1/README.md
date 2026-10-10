# Project 1: Small FastAPI Service

This project is a beginner-friendly FastAPI backend built for Level 1 practice.

It includes:

* 5 endpoints
* request and response models
* simple API key authentication
* environment-based configuration
* logging
* exception handling
* basic API tests

## Project idea

This is a small document assistant API.

It lets you:

* check service health
* list sample documents
* fetch a document by id
* create a new document
* ask a simple question about a document

## Endpoints

* `GET /health`
* `GET /documents`
* `GET /documents/{document_id}`
* `POST /documents`
* `POST /chat`

## Project structure

```text
project_1/
  app/
    core/
      config.py
      logging_config.py
      security.py
    routers/
      chat.py
      documents.py
      health.py
    schemas/
      chat.py
      document.py
    services/
      chat_service.py
      document_service.py
    main.py
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

## Example headers

Protected endpoints need:

```text
x-api-key: level1-secret-key
```

## Run tests

```bash
pytest
```

## Notes

This project uses an in-memory document store for simplicity.
It is designed for learning backend structure, not for production persistence.
