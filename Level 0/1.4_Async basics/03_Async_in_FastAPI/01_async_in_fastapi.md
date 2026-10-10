# Async in FastAPI

## FastAPI supports both sync and async routes

You can write route handlers using:

* `def`
* `async def`

Example:

```python
@app.get("/health")
def health():
    return {"status": "ok"}
```

```python
@app.get("/async-health")
async def async_health():
    return {"status": "ok"}
```

## When should you use `async def`?

Use `async def` when your route performs asynchronous operations such as:

* async database calls
* async HTTP requests
* async file or network operations

If your route is purely simple and synchronous, normal `def` is fine.

## What does `await` do?

Inside an async function, `await` marks a point where the function can pause while waiting for an async operation to complete.

Example:

```python
import asyncio

@app.get("/demo")
async def demo():
    await asyncio.sleep(1)
    return {"message": "done"}
```

## Common beginner mistake

This is wrong:

```python
@app.get("/bad")
async def bad():
    result = slow_sync_function()
    return {"result": result}
```

Why it can be a problem:

If `slow_sync_function()` blocks heavily, the benefits of async are reduced.

## Key takeaway

In FastAPI, async routes are most useful when the route is waiting on async I O work.
