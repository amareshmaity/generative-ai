# Revision and Practice Tasks

## Revision checklist

You should now be able to explain:

* why testing matters
* what a unit test is
* what an API test is
* difference between unit testing and API testing
* how FastAPI endpoints can be tested
* why mocked provider calls are useful in GenAI testing

## Practice tasks

### Task 1

Write a unit test for a function that:

* cleans prompt text
* returns lowercase output
* removes extra spaces

### Task 2

Build a FastAPI app with:

* `GET /health`
* `GET /documents/{id}`

Write API tests for:

* successful health check
* successful document fetch
* missing document error

### Task 3

Create a `POST /chat` route and test:

* valid request body
* missing required field
* empty question handling

### Task 4

Design a testing plan for a small RAG backend.
Decide which parts should use:

* unit tests
* API tests
* mocked external provider calls

## Interview questions

* What is the difference between unit testing and API testing?
* Why are tests useful during refactoring?
* What does `assert` do in a Python test?
* Why is `pytest` popular?
* How does `TestClient` help in FastAPI?
* Why should real LLM provider calls usually be avoided in routine tests?

## Final note

If these ideas feel clear, you are moving from demo-style coding toward more reliable backend engineering.
