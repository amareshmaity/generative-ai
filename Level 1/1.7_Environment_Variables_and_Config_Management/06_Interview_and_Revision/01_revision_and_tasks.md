# Revision and Practice Tasks

## Revision checklist

You should now be able to explain:

* what an environment variable is
* why hardcoding secrets is risky
* what `.env` files are used for
* why config should be separated from business logic
* how FastAPI projects often organize settings
* why GenAI backends need clean config management

## Practice tasks

### Task 1

Write a small Python script that reads:

* `APP_NAME`
* `DEBUG`
* `OPENAI_API_KEY`

Print whether each value exists.

### Task 2

Design a small `Settings` class for a FastAPI app with:

* app name
* debug mode
* default model
* provider API key

### Task 3

Refactor a demo route so that it no longer hardcodes:

* model name
* provider key

Move those values into shared settings.

### Task 4

Design a config list for a RAG project.
Decide which values should be:

* secrets
* normal runtime settings

## Interview questions

* What is an environment variable?
* Why should secrets not be hardcoded in code?
* What is the purpose of a `.env` file?
* Why is centralized config useful?
* Where would config usually live in a FastAPI project?
* What types of settings are common in GenAI systems?

## Final note

If these ideas feel natural, you are building the habits needed for cleaner and more production-ready backend projects.
