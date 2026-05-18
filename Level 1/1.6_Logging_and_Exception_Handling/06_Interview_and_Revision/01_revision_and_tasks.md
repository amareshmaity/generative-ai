# Revision and Practice Tasks

## Revision checklist

You should now be able to explain:

* why logging matters
* common log levels
* why logging is better than only using `print()`
* what exceptions are
* how `try` and `except` work
* how FastAPI returns clear API errors
* why GenAI systems need careful logging

## Practice tasks

### Task 1

Write a small Python function that:

* logs the start of an operation
* raises an error for invalid input
* logs the failure clearly

### Task 2

Build a FastAPI route such as `GET /documents/{id}` that:

* logs the incoming request
* returns `404` when the document does not exist

### Task 3

Create a simple GenAI route such as `POST /summarize` that:

* logs the selected document id
* returns a clean error when input is empty
* avoids logging private document content directly

### Task 4

Design a small error strategy for a RAG API.
Decide what status code you would return for:

* invalid input
* missing document
* provider timeout
* unexpected internal bug

## Interview questions

* What is the purpose of logging in backend systems?
* What are common log levels?
* Why is `print()` not enough for real applications?
* What is an exception in Python?
* Why should you avoid `except Exception: pass`?
* How does FastAPI handle API errors?
* What should be logged carefully in a GenAI system?

## Final note

If these ideas feel comfortable, you are developing the mindset needed to build debuggable and production-friendly AI backends.
