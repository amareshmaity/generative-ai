# Dependencies and Project Structure

## What is a dependency in FastAPI?

A dependency is reusable logic that FastAPI can inject into route functions.

Examples:

* current user
* database session
* common query settings
* shared config

## Basic example

```python
from fastapi import Depends, FastAPI

app = FastAPI()


def common_params(limit: int = 10):
    return {"limit": limit}


@app.get("/items")
def get_items(params: dict = Depends(common_params)):
    return params
```

## Why dependencies are useful

They help:

* avoid repeated code
* separate concerns
* keep routes cleaner
* prepare for real project structure

## Example project structure

```text
app/
  main.py
  routers/
    users.py
    chat.py
  schemas/
    chat.py
  services/
    llm_service.py
  core/
    config.py
```

## Why structure matters

Small demos can stay in one file.
Real projects should not.

If you mix routes, business logic, schemas, config, and utilities in one file, the app becomes hard to maintain.

## GenAI-specific example

In a GenAI backend, dependencies may inject:

* API key settings
* vector store client
* current user
* model configuration

## Key takeaway

Dependencies make FastAPI apps cleaner, more reusable, and more ready for production-scale architecture.

