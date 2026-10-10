# Sync vs Async

## Synchronous thinking

In synchronous code, one step usually waits for the previous step to finish.

Example idea:

1. request comes in
2. server waits for database
3. server waits for external API
4. response is returned

If one step is slow, the flow is blocked.

## Asynchronous thinking

In asynchronous code, waiting points can be handled in a non-blocking way.

That means while one task is waiting, the application can continue handling other work.

## Simple comparison

### Sync

```python
import time

def slow_task():
    time.sleep(2)
    return "done"
```

### Async

```python
import asyncio

async def slow_task():
    await asyncio.sleep(2)
    return "done"
```

The async version expresses that this is a waiting point that can yield control.

## Important note

Not every function should be async.

Use async when:

* the function performs async I O
* it awaits other async operations

Do not use async only because it looks modern.

## In FastAPI

Both of these are valid:

```python
@app.get("/sync")
def sync_route():
    return {"mode": "sync"}
```

```python
@app.get("/async")
async def async_route():
    return {"mode": "async"}
```

The right choice depends on the work being done inside the route.

## Key takeaway

Sync is simple and sequential.
Async is useful when the program spends time waiting and should stay responsive.
