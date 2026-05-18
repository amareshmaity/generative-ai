# Logging and Exceptions in FastAPI

## FastAPI needs both clear errors and useful logs

In an API, the user needs a clean response.
At the same time, the backend developer needs enough information to debug failures.

That is why logging and exception handling work together.

## Simple route with logging

```python
import logging
from fastapi import FastAPI

app = FastAPI()
logger = logging.getLogger(__name__)

@app.get("/health")
def health():
    logger.info("Health check called")
    return {"status": "ok"}
```

## Raising API errors

FastAPI commonly uses `HTTPException`.

```python
from fastapi import HTTPException

@app.get("/documents/{document_id}")
def get_document(document_id: int):
    if document_id != 1:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"document_id": document_id}
```

## Useful pattern

A common pattern is:

1. log the start of an operation
2. perform the work
3. log success or failure
4. raise a clean API error when needed

## Example idea

```python
logger.info(f"Fetching document_id={document_id}")
if document_missing:
    logger.warning(f"Missing document_id={document_id}")
    raise HTTPException(status_code=404, detail="Document not found")
```

## Unexpected failures

Sometimes an unexpected internal error happens.

In such cases, the backend may:

* log the technical details
* return a safer message to the client

This is useful because internal stack details should not be exposed casually to API consumers.

## Exception handlers

FastAPI also supports custom exception handlers.

These are useful when you want:

* consistent error responses
* centralized handling of certain exceptions

## Good beginner habit

Return helpful error messages, but do not leak sensitive internal details such as:

* full stack traces
* secret values
* internal infrastructure information

## Why this matters for GenAI APIs

A GenAI route may fail because of:

* invalid document id
* prompt validation issue
* model provider timeout
* rate limit from external API

The API should respond clearly while the logs capture enough detail for debugging.

## Key takeaway

In FastAPI, good exception handling protects the client experience, and good logging protects the developer experience.
