# 06. Synchronous and Asynchronous Calls

## Learning objectives

By the end of this chapter, you should be able to:

-   Compare blocking SDK calls with asynchronous client calls.
-   Await I/O correctly and avoid blocking work inside asynchronous
    request handlers.
-   Reuse clients appropriately and bound concurrent requests.
-   Understand cancellation and cleanup when a caller disconnects or a
    deadline expires.
-   Distinguish I/O concurrency from parallel model computation.

> **Scope:** Examples use Python and the OpenAI SDK to illustrate common
> patterns. Exact APIs and cancellation behavior depend on the provider,
> SDK, HTTP transport, and web framework versions. Verify them against
> the versions pinned by your project.

<br/>

## 1. Synchronous versus asynchronous I/O

A synchronous call blocks the current thread until the operation
returns. An asynchronous call allows the current task to yield while
waiting for I/O, so the event loop can run other tasks.

LLM API calls are often I/O-bound from the application's perspective:
the application sends a request and waits for a remote service. Async
I/O can improve throughput when a service handles many concurrent
requests, but it does not automatically make an individual model
inference faster.


| Concern             | Synchronous Call                       | Asynchronous Call                                                 |
| ------------------- | -------------------------------------- | ----------------------------------------------------------------- |
| Typical invocation  | `client.responses.create(...)`         | `await async_client.responses.create(...)`                        |
| Waiting behavior    | Current thread waits                   | Current task yields while waiting                                 |
| Fits naturally with | Simple scripts, synchronous frameworks | Async frameworks and high-concurrency I/O                         |
| Concurrency model   | Often threads or sequential calls      | Event-loop tasks, with async-compatible I/O                       |
| Main risk           | Blocking a thread during slow I/O      | Blocking the event loop with sync work or creating too many tasks |


<br/>

### Synchronous example

``` python
from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="YOUR_SUPPORTED_MODEL",
    input="Explain I/O-bound work in one sentence.",
)

print(response.output_text)
```

This is straightforward for scripts, command-line jobs, or synchronous
request handlers.

<br/>

### Asynchronous example

``` python
import asyncio
from openai import AsyncOpenAI

async def main() -> None:
    async with AsyncOpenAI() as client:
        response = await client.responses.create(
            model="YOUR_SUPPORTED_MODEL",
            input="Explain I/O-bound work in one sentence.",
        )
        print(response.output_text)

asyncio.run(main())
```

Important details:

-   `AsyncOpenAI` is the asynchronous client in the OpenAI Python SDK.
-   `await` suspends the current coroutine while the request waits for
    I/O.
-   `asyncio.run()` is appropriate at a top-level script entry point. In
    an already-running event loop, such as many async web handlers, call
    an async function with `await` instead of starting a nested event
    loop.
-   Use the sync client in synchronous code and the async client in
    async code. Avoid mixing them casually.


<br/>


## 2. What `await` does---and does not do

`await` lets a coroutine pause until an awaitable operation completes,
giving the event loop a chance to run other ready tasks. It does not
make arbitrary blocking code asynchronous.

For example, this is a problem in an async endpoint:

``` python
async def endpoint():
    # Bad pattern: a synchronous network call can block the event loop.
    response = sync_client.responses.create(
        model="YOUR_SUPPORTED_MODEL",
        input="Hello",
    )
    return {"text": response.output_text}
```

Use the async client instead:

``` python
async def endpoint():
    response = await async_client.responses.create(
        model="YOUR_SUPPORTED_MODEL",
        input="Hello",
    )
    return {"text": response.output_text}
```

Other operations can block an event loop too, including CPU-heavy Python
code, synchronous database calls, large file operations, or calls to
libraries that do not support async I/O.

Practical rules:

-   Use async-compatible libraries in async request handlers.
-   Move unavoidable blocking I/O to a suitable worker thread or
    background worker.
-   Use a process pool or specialized compute infrastructure for
    substantial CPU-bound work when appropriate.
-   Do not add `async` to a function and assume its internal synchronous
    operations become non-blocking.


<br/>


## 3. Sequential calls versus concurrent calls

Suppose an application needs results from several independent prompts.
Sequential execution waits for each call to finish before starting the
next. Concurrent execution starts multiple I/O operations and awaits
their completion.

``` mermaid
flowchart TD
    A[Three independent requests] --> B[Sequential execution]
    A --> C[Concurrent execution]
    B --> D[Request 1 completes]
    D --> E[Request 2 completes]
    E --> F[Request 3 completes]
    C --> G[Request 1 starts]
    C --> H[Request 2 starts]
    C --> I[Request 3 starts]
    G --> J[Await all results]
    H --> J
    I --> J
```

<br/>

### Sequential baseline

``` python
import asyncio
from openai import AsyncOpenAI

PROMPTS = [
    "Define an embedding.",
    "Define a token.",
    "Define a context window.",
]

async def sequential(client: AsyncOpenAI) -> list[str]:
    results = []
    for prompt in PROMPTS:
        response = await client.responses.create(
            model="YOUR_SUPPORTED_MODEL",
            input=prompt,
        )
        results.append(response.output_text)
    return results
```

This is simple and naturally limits the number of simultaneous requests
to one.

<br/>

### Concurrent calls with a fixed small batch

``` python
async def concurrent_small_batch(client: AsyncOpenAI) -> list[str]:
    tasks = [
        client.responses.create(
            model="YOUR_SUPPORTED_MODEL",
            input=prompt,
        )
        for prompt in PROMPTS
    ]

    responses = await asyncio.gather(*tasks)
    return [response.output_text for response in responses]
```

This can reduce total wall-clock time when calls are independent and the
provider allows the requests to run concurrently. However, `gather()`
over a large unbounded collection can overwhelm the application or
provider. Use a concurrency limit for real workloads.


<br/>


## 4. Bound concurrency

Concurrency should be an explicit resource budget. A semaphore is a
simple way to limit the number of in-flight requests.

``` python
import asyncio
from openai import AsyncOpenAI

MAX_IN_FLIGHT = 5

async def run_one(
    client: AsyncOpenAI,
    semaphore: asyncio.Semaphore,
    prompt: str,
) -> str:
    async with semaphore:
        response = await client.responses.create(
            model="YOUR_SUPPORTED_MODEL",
            input=prompt,
        )
        return response.output_text

async def run_bounded(
    client: AsyncOpenAI,
    prompts: list[str],
) -> list[str]:
    semaphore = asyncio.Semaphore(MAX_IN_FLIGHT)

    tasks = [
        run_one(client, semaphore, prompt)
        for prompt in prompts
    ]
    return await asyncio.gather(*tasks)
```

This example creates one task per prompt but permits only five calls to
enter the protected section at once. For very large input collections,
task creation itself can consume memory; use a bounded queue or worker
pool so that both in-flight requests and queued work are controlled.

Choose a limit based on:

-   Provider request-per-minute and token-per-minute limits.
-   Expected prompt and output sizes.
-   Account or project quota.
-   HTTP connection pool capacity.
-   Application memory and CPU.
-   End-to-end latency objectives.
-   Retry behavior and the number of simultaneous users.

A concurrency limit is not a rate limiter. Five concurrent requests can
still exceed a requests-per-minute limit if they complete quickly.
Production systems may need both concurrency control and rate limiting.


<br/>


## 5. Reuse clients and manage their lifecycle

Clients usually manage reusable HTTP connections, transport
configuration, timeouts, and other shared resources. Creating a fresh
client for every request can add overhead and make connection management
less efficient.

For a short async script, a context manager provides clear cleanup:

``` python
import asyncio
from openai import AsyncOpenAI

async def main() -> None:
    async with AsyncOpenAI() as client:
        response = await client.responses.create(
            model="YOUR_SUPPORTED_MODEL",
            input="What is an API client?",
        )
        print(response.output_text)

asyncio.run(main())
```

In a long-running web service, create a client during application
startup and close it during shutdown, rather than constructing one for
every incoming HTTP request. The exact lifecycle hooks depend on your
framework.

Conceptual FastAPI lifespan example:

``` python
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from openai import AsyncOpenAI

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with AsyncOpenAI() as client:
        app.state.llm_client = client
        yield

app = FastAPI(lifespan=lifespan)

@app.get("/explain")
async def explain(request: Request):
    response = await request.app.state.llm_client.responses.create(
        model="YOUR_SUPPORTED_MODEL",
        input="Explain asynchronous I/O briefly.",
    )
    return {"text": response.output_text}
```

Treat this as a lifecycle pattern to adapt and test against your pinned
FastAPI and SDK versions. Do not share mutable per-request state through
a global client. Shared clients should be configured for reuse;
request-specific data belongs in each call.


<br/>


## 6. Cancellation, timeouts, and caller disconnects

An asynchronous task can be cancelled---for example, when a caller
disconnects, a parent task is cancelled, or an application deadline
expires. Cancellation is a control-flow event, not automatically proof
that the remote provider stopped processing the request.

Use `try`/`finally` for cleanup and avoid swallowing cancellation:

``` python
import asyncio

async def call_with_deadline(client, prompt: str) -> str:
    try:
        async with asyncio.timeout(20):
            response = await client.responses.create(
                model="YOUR_SUPPORTED_MODEL",
                input=prompt,
            )
            return response.output_text
    except TimeoutError:
        # Record a timeout and return/raise an application-level error.
        raise
```

`asyncio.timeout()` requires Python 3.11 or newer. For earlier versions,
use an appropriate alternative such as `asyncio.wait_for()`.

Guidelines:

-   Configure provider/HTTP-client timeouts as well as application-level
    deadlines.
-   Propagate cancellation after performing necessary cleanup.
-   Do not catch `BaseException` broadly or suppress
    `asyncio.CancelledError` without a specific reason.
-   Release semaphores and other resources using context managers or
    `finally`.
-   If a web framework cancels a handler on disconnect, test that
    behavior in your deployed framework and server configuration.
-   A timed-out request may still have incurred provider compute or
    billing. Do not assume cancellation reverses remote work.
-   Be cautious when retrying a timed-out operation: the first attempt
    may have completed remotely even though the client never received
    the result.


<br/>


## 7. I/O concurrency is not parallel model computation

Async I/O allows one application process to manage multiple waiting
requests efficiently. It does not mean that Python is computing multiple
model inferences locally in parallel.

-   **I/O concurrency:** multiple network operations are in flight while
    the application awaits responses.
-   **Parallel computation:** CPU or accelerator work executes
    simultaneously across cores, processes, devices, or provider
    infrastructure.
-   **Provider-side scheduling:** the model service decides how requests
    are queued, batched, and executed. Client-side `asyncio` does not
    control that scheduling directly.

For hosted LLM APIs, asynchronous calls mainly help the client use
waiting time efficiently. They may improve throughput and reduce
queueing inside your application, but latency still depends on provider
capacity, model generation time, network conditions, rate limits, and
request sizes.


<br/>


## 8. Practice: compare sequential and bounded concurrency

This exercise uses a fake async client, so it requires no API key and
incurs no API cost. The simulated delay represents waiting for remote
I/O.

``` python
import asyncio
import time

class FakeResponse:
    def __init__(self, text: str):
        self.output_text = text

class FakeAsyncClient:
    async def generate(self, prompt: str) -> FakeResponse:
        await asyncio.sleep(0.2)  # Simulated network/model wait
        return FakeResponse(f"Answer: {prompt}")

PROMPTS = [f"prompt-{i}" for i in range(10)]

async def run_sequential(client, prompts):
    results = []
    for prompt in prompts:
        response = await client.generate(prompt)
        results.append(response.output_text)
    return results

async def run_bounded(client, prompts, limit=3):
    semaphore = asyncio.Semaphore(limit)

    async def one(prompt):
        async with semaphore:
            response = await client.generate(prompt)
            return response.output_text

    return await asyncio.gather(*(one(p) for p in prompts))

async def main():
    client = FakeAsyncClient()

    start = time.perf_counter()
    sequential_results = await run_sequential(client, PROMPTS)
    sequential_seconds = time.perf_counter() - start

    start = time.perf_counter()
    concurrent_results = await run_bounded(client, PROMPTS, limit=3)
    concurrent_seconds = time.perf_counter() - start

    assert sequential_results == concurrent_results
    print(f"Sequential: {sequential_seconds:.2f}s")
    print(f"Bounded concurrency: {concurrent_seconds:.2f}s")

asyncio.run(main())
```

With ten simulated requests, each waiting 0.2 seconds, sequential
execution should take roughly two seconds. With a concurrency limit of
three, bounded execution should take roughly four waves of waiting, or
about 0.8 seconds, plus overhead. Actual timings vary.

### Practice extensions

1.  Change the limit to `1`, `2`, `5`, and `10`; record elapsed time.
2.  Make one request raise an exception and observe how
    `asyncio.gather()` behaves.
3.  Add a timeout around each fake request.
4.  Add a maximum queue size for a large prompt list.
5.  Replace the fake client with a small number of real provider
    requests only after configuring credentials, cost controls, and a
    conservative concurrency limit.

<br/>


## 9. Checkpoint: why unbounded concurrency can make things worse

Unbounded concurrency can create more simultaneous requests than the
provider, HTTP connection pool, or application can handle. This can
cause:

-   More `429` rate-limit responses and retry traffic.
-   Increased queueing and tail latency.
-   Exhausted sockets, connection pools, memory, or task capacity.
-   A retry storm that amplifies load.
-   Higher costs from requests that complete remotely even if the caller
    times out.
-   Poor fairness between users or tenants.

**Checkpoint answer:** Concurrency is a resource to budget, not a
setting to maximize. Bound in-flight requests, add rate limiting where
required, use sensible timeouts, and implement backoff for retryable
errors. Tune limits from observed throughput, latency, quota, and
resource metrics.

<br/>

## 10. Key takeaways

-   Use synchronous clients in synchronous code and asynchronous clients
    in async code.
-   `await` helps only when the awaited operation is genuinely
    asynchronous.
-   Async I/O improves how waiting time is used; it does not
    automatically speed up model inference.
-   Reuse clients and close them at application shutdown.
-   Bound concurrency and, where needed, also enforce request/token rate
    limits.
-   Handle cancellation and deadlines without assuming remote work was
    cancelled.
-   Benchmark with a fake client before running controlled live tests.

<br/>

## References

-   OpenAI Python SDK: https://github.com/openai/openai-python
-   OpenAI Python SDK --- async client and lifecycle patterns:
    https://github.com/openai/openai-python#async-usage
-   Python `asyncio` tasks and cancellation:
    https://docs.python.org/3/library/asyncio-task.html
-   Python `asyncio` synchronization primitives:
    https://docs.python.org/3/library/asyncio-sync.html
-   FastAPI lifespan events:
    https://fastapi.tiangolo.com/advanced/events/

Check current provider documentation and the SDK/framework versions
pinned by your project before relying on exact APIs or lifecycle
behavior.
