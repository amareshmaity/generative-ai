# Revision and Practice Tasks

## Revision checklist

You should now be able to explain:

* what async means
* why async helps with I O bound work
* difference between sync and async code
* what `await` does
* when to use `async def` in FastAPI
* why async is useful in GenAI backends

## Practice tasks

### Task 1

Create a FastAPI app with:

* one sync endpoint
* one async endpoint

### Task 2

Create an async helper function using:

```python
await asyncio.sleep(1)
```

and call it from a route.

### Task 3

Build a route that uses `asyncio.gather()` to combine:

* document fetch
* user preference fetch

### Task 4

Create a small GenAI-style endpoint:

* request includes `question` and `document_id`
* route fetches context asynchronously
* response returns `answer`

## Interview questions

* What is async programming?
* What is the difference between sync and async code?
* What does `await` do?
* When should you use `async def` in FastAPI?
* Does async help CPU-heavy work?
* Why is async useful in GenAI APIs?

## Example interview answer

Question:

Why is async useful in FastAPI?

Good answer:

"Async is useful in FastAPI when the server spends time waiting on I O operations like database calls, external APIs, or model providers. Using `async def` and `await` helps the application handle waiting more efficiently and stay responsive. It is especially helpful in GenAI backends where many steps depend on network-based services."

## Final note

Do not use async only because it looks advanced.
Use it when the problem actually involves waiting on I O work.
