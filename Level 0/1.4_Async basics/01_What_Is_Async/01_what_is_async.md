# What Is Async?

## Start with the main problem

Programs often spend time waiting.

They may wait for:

* database queries
* API calls
* file reads
* network responses

During that waiting time, the CPU may not be doing useful work.

Async programming helps us handle waiting more efficiently.

## What does async mean?

Async means a program can start a task, pause while it is waiting, and let other work continue.

It is especially useful when the work is I O bound.

I O bound means the task spends a lot of time waiting on external systems such as:

* network
* disk
* database

## Simple intuition

Think of a restaurant server.

A server takes your order and gives it to the kitchen.
While the food is being prepared, the server does not stand still doing nothing.
The server can help other tables.

That is the basic idea behind async.

## Async is not magic speed

Async does not automatically make all code faster.

It mainly helps when:

* many requests are waiting on I O
* the server can do other work during that waiting

It does not help much for heavy CPU calculations.

Examples of CPU-heavy work:

* model training
* large image processing
* heavy numerical computation

## Why async matters in FastAPI

FastAPI is often used for APIs that interact with:

* databases
* external APIs
* model providers
* vector stores

Those are common waiting points.

That is why async becomes useful in backend and GenAI systems.

## Key takeaway

Async is about handling waiting better, not about replacing all normal Python code.
