# Await and I O Bound Work

## Why `await` exists

In async Python, `await` is used to pause an async function until another async operation finishes.

During that pause, control can return to the event loop so other work can continue.

## Example

```python
import asyncio

async def fetch_data():
    await asyncio.sleep(1)
    return "done"
```

Here `await asyncio.sleep(1)` represents a waiting point.

## I O bound vs CPU bound

### I O bound

Tasks that spend time waiting for external systems.

Examples:

* API calls
* DB queries
* file operations
* retrieval from remote services

### CPU bound

Tasks that spend time actively using the CPU.

Examples:

* model training
* large matrix calculations
* heavy data processing

Async is especially useful for I O bound work.

## Combining async work

Sometimes multiple independent async tasks can be started together.

Example:

```python
results = await asyncio.gather(
    fetch_document(),
    fetch_user_context()
)
```

This is useful when two tasks do not depend on each other.

## Why this matters in FastAPI

A FastAPI route may need to:

* fetch a document
* fetch user settings
* call a model provider

Some of these steps can be async, and some can even run together.

## Key takeaway

`await` helps async code pause at the right places so waiting does not block everything else.
