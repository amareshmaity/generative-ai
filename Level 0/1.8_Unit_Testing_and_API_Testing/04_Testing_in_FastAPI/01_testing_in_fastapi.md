# Testing in FastAPI

## FastAPI testing usually has two layers

A FastAPI project often benefits from both:

* unit tests for small functions and services
* API tests for routes and responses

This combination gives better coverage than only one style.

## TestClient idea

FastAPI commonly uses `TestClient` for API tests.

It lets you send requests to the app in code without running a separate server manually.

Example:

```python
from fastapi.testclient import TestClient

client = TestClient(app)
```

## Example route test

```python
def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

## What should you test in FastAPI apps?

Useful tests include:

* success responses
* validation failures
* missing resources
* authentication failures
* response structure

## Organizing tests

A simple project may use a `tests/` folder such as:

```text
tests/
  test_health.py
  test_chat.py
  test_auth.py
```

## Why service separation helps testing

If route logic and business logic are separated well, testing becomes easier.

Then you can:

* unit test the service logic
* API test the route behavior

## Good beginner habit

Start by testing the most important routes first.

Examples:

* health endpoint
* chat endpoint
* document retrieval endpoint

## Key takeaway

FastAPI testing works best when you combine small logic tests with endpoint-level contract checks.
