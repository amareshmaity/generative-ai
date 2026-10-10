# Revision and Practice Tasks

## Revision checklist

You should now be able to explain:

* what authentication means
* authentication vs authorization
* API key vs bearer token
* JWT at a basic level
* how FastAPI can protect routes
* why GenAI backends should keep provider secrets private

## Practice tasks

### Task 1

Build a small FastAPI app with:

* `GET /health`
* `GET /protected`

Protect the second route with a simple API key.

### Task 2

Change the protected route to check a bearer token in the `Authorization` header.

### Task 3

Add a fake `current_user` object after token validation and return it in the response.

### Task 4

Design a GenAI route such as `POST /chat` where:

* the user must be authenticated
* the backend keeps the model provider key private
* the response returns only safe user-facing data

## Interview questions

* What is the difference between authentication and authorization?
* What is an API key?
* What is a bearer token?
* Why should secrets not be hardcoded in code?
* How can FastAPI reuse authentication logic?
* Why should a GenAI frontend not expose the provider API key?

## Final note

If these ideas are comfortable, you are ready to add basic route protection to beginner-level backend and GenAI projects.
