# Routes and Parameters

## What is a route in FastAPI?

A route maps a URL path and HTTP method to a Python function.

Example:

```python
@app.get("/users")
def get_users():
    return {"users": []}
```

This means:

* HTTP method: `GET`
* path: `/users`
* function: `get_users`

## Path parameters

Use path parameters when the value is part of the resource identity.

Example:

```python
@app.get("/documents/{document_id}")
def get_document(document_id: int):
    return {"document_id": document_id}
```

Here `document_id` is extracted from the URL.

FastAPI also validates the type automatically.

## Query parameters

Use query parameters for optional input like filtering or pagination.

Example:

```python
@app.get("/search")
def search(topic: str, page: int = 1):
    return {"topic": topic, "page": page}
```

Example request:

```http
GET /search?topic=genai&page=2
```

## Combining both

```python
@app.get("/users/{user_id}/posts")
def get_posts(user_id: int, page: int = 1):
    return {"user_id": user_id, "page": page}
```

## Route design tips

* keep names resource-oriented
* use nouns more than verbs
* keep naming consistent
* use type hints clearly

## Common mistakes

* confusing path params with query params
* putting too much logic directly in route functions
* inconsistent route naming

## Key takeaway

Routes are the backbone of a FastAPI app.
Once you understand route definition and parameter handling, you can build meaningful APIs quickly.

