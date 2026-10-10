# Revision and Practice Tasks

## Revision checklist

You should now be able to explain:

* what FastAPI is
* why it is popular for AI backends
* how routes work
* path parameters vs query parameters
* request body handling with Pydantic
* response models
* exception handling
* dependency injection
* where advanced topics like middleware and background tasks fit

## Practice tasks

### Task 1

Build a tiny app with:

* `GET /`
* `GET /health`
* `GET /documents/{id}`
* `POST /chat`

### Task 2

Add a Pydantic request model with:

* `question`
* `document_id`
* `temperature`

### Task 3

Return proper errors when:

* document does not exist
* question is empty

### Task 4

Refactor the app into:

* `main.py`
* `routers`
* `schemas`
* `services`

## Interview questions

* Why is FastAPI preferred over some older Python API frameworks for AI use cases?
* What does Pydantic do in FastAPI?
* Difference between path params and query params
* What is `Depends` used for?
* When would you use `async def`?
* How would FastAPI fit in a RAG backend?

## Final note

If these ideas become comfortable, you are in a very good place to start building real GenAI backend projects.

