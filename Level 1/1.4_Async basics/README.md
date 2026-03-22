# 1.4 Async Basics

This section is focused on understanding async programming in Python from a FastAPI point of view.

The goal is not to turn this into a deep Python internals topic.
The goal is to help you understand when async is useful, how `async` and `await` work, and how FastAPI uses them in real backend code.

## Study order

1. `01_What_Is_Async`
2. `02_Sync_vs_Async`
3. `03_Async_in_FastAPI`
4. `04_Await_and_IO_Bound_Work`
5. `05_Practical_FastAPI_Patterns`
6. `06_Interview_and_Revision`

## What you will learn

* what async programming means
* difference between sync and async thinking
* what `async` and `await` do
* when async helps in FastAPI
* how to write simple async endpoints
* how to combine async tasks in a backend workflow

## Practical notebooks

* `02_Sync_vs_Async/sync_vs_async_demo.ipynb`
* `03_Async_in_FastAPI/async_fastapi_demo.ipynb`
* `04_Await_and_IO_Bound_Work/await_and_io_demo.ipynb`
* `05_Practical_FastAPI_Patterns/practical_async_patterns_demo.ipynb`

## Goal

After reading this section, you should be able to:

* explain async in simple words
* tell when to use `def` and when to use `async def`
* understand why `await` is needed
* build simple async FastAPI endpoints
* explain async use cases in GenAI backends
