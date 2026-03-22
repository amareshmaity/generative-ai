# Installation and First App

## What is FastAPI?

FastAPI is a modern Python web framework used to build APIs quickly.

It is especially popular for AI and ML backends because it gives:

* clean syntax
* automatic validation
* auto-generated docs
* strong type hints
* async support

## Why FastAPI is popular in GenAI

FastAPI is a strong fit for GenAI systems because it can:

* accept user prompts
* validate request data
* call LLM APIs
* connect to vector databases
* return clean JSON responses

## Install

```bash
pip install fastapi uvicorn
```

## Your first FastAPI app

Create a file named `main.py`.

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def home():
    return {"message": "FastAPI is running"}
```

Run it:

```bash
uvicorn main:app --reload
```

## What happened here?

### `FastAPI()`

Creates the application object.

### `@app.get("/")`

Registers a route for `GET /`.

### `home()`

Runs when the route is called and returns JSON.

## Swagger UI and docs

FastAPI automatically generates docs.

Open:

* `http://127.0.0.1:8000/docs`
* `http://127.0.0.1:8000/redoc`

This is one reason FastAPI is loved by backend and AI teams.

## Common beginner mistakes

* forgetting to install `uvicorn`
* naming the file wrong and running the wrong import path
* forgetting `--reload` during development
* expecting HTML instead of JSON responses

## Why this matters before advanced topics

If the first app becomes clear, later topics like routes, validation, dependencies, and async become much easier.

## Key takeaway

FastAPI gives you a fast way to build Python APIs with very little code, and it is one of the best starting points for AI backend development.

