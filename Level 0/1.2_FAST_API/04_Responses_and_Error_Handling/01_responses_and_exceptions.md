# Responses and Exceptions

## Why this matters

Good APIs are not only about accepting input.
They must also return output in a clear and stable way.

## Basic response

```python
@app.get("/health")
def health():
    return {"status": "ok"}
```

FastAPI automatically returns JSON when you return a dictionary.

## Response model

```python
from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str


@app.get("/health", response_model=HealthResponse)
def health():
    return {"status": "ok"}
```

This helps:

* document the response
* enforce response shape
* keep output consistent

## Status codes

Example:

```python
from fastapi import status


@app.post("/items", status_code=status.HTTP_201_CREATED)
def create_item():
    return {"message": "created"}
```

## Raising exceptions

```python
from fastapi import HTTPException


@app.get("/documents/{document_id}")
def get_document(document_id: int):
    if document_id != 1:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"document_id": document_id}
```

## Good exception mindset

Use exceptions when:

* resource is missing
* request is not allowed
* access should be denied
* validation beyond schema rules fails

## Why this matters in GenAI APIs

Common errors:

* missing document
* invalid prompt input
* model provider timeout
* unsupported model name
* empty file upload

Your API should fail clearly, not mysteriously.

## Key takeaway

A reliable FastAPI app uses response models, meaningful status codes, and clear exceptions to make the API easy to consume and debug.

