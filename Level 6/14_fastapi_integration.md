# Chapter 14: FastAPI Integration

## Learning objectives

By the end of this chapter, you should be able to:

-   Apply routing, dependency injection, and service-layer patterns in a
    FastAPI application.
-   Create and close reusable model clients through application lifespan
    management.
-   Build asynchronous endpoints with validated request and response
    models.
-   Expose structured extraction and streaming operations through clear
    route contracts.
-   Propagate request IDs, deadlines, and cancellation where supported.
-   Keep endpoint code separate from prompts and provider-specific
    response handling.

<br/>

## 1 Where FastAPI fits in an LLM application

FastAPI provides the HTTP layer around your application. It validates
incoming data, resolves dependencies, invokes application services, and
serializes responses. It should not become the place where prompts,
provider SDK details, retries, and business rules are all mixed
together.

A practical separation is:

``` mermaid
flowchart TD
    A[HTTP client] --> B[FastAPI router]
    B --> C[Request and response schemas]
    B --> D[Dependency injection]
    D --> E[Application service]
    E --> F[Provider adapter or model client]
    F --> G[LLM provider]
    E --> H[Normalized application result]
    H --> B
    B --> I[Validated HTTP response]
```

Typical responsibilities:

-   **Router/endpoint:** HTTP method, path, status code,
    request/response schema, and HTTP-specific error mapping.
-   **Schema:** validates input and defines the public response
    contract.
-   **Dependency provider:** supplies reusable services and clients to
    endpoints.
-   **Service layer:** owns use-case orchestration and application-level
    validation.
-   **Prompt module:** contains versioned prompt templates and
    instructions.
-   **Provider adapter:** calls the SDK and normalizes provider-specific
    results.
-   **Application lifespan:** initializes shared resources and closes
    them during shutdown.

This structure makes endpoints easier to test and reduces coupling to a
particular provider.

<br/>

## 2 Suggested project structure

For a small API, keep the structure compact but establish clear
boundaries.

``` text
app/
├── main.py
├── api/
│   └── routes/
│       └── llm.py
├── schemas/
│   └── extraction.py
├── services/
│   └── llm_service.py
├── prompts/
│   └── extraction.py
├── providers/
│   └── openai_adapter.py
└── core/
    └── config.py
tests/
├── test_extraction_route.py
└── test_stream_route.py
```

Do not create a separate module for every tiny function prematurely.
Split modules when doing so makes responsibilities, testing, or
ownership clearer.

<br/>

## 3 Define validated request and response models

Use Pydantic models to define the API contract. Validate user input
before calling the model, and validate the model's extracted result
before returning it.

``` python
from pydantic import BaseModel, Field


class ExtractionRequest(BaseModel):
    text: str = Field(min_length=1, max_length=20_000)


class TicketExtraction(BaseModel):
    category: str
    priority: str
    summary: str = Field(min_length=1, max_length=500)


class ExtractionResponse(BaseModel):
    request_id: str
    result: TicketExtraction
```

The request model limits input size at the HTTP boundary. Production
applications should also define domain-specific constraints,
authorization rules, and an overall request deadline. Do not rely on
prompt instructions alone to enforce the output schema.

For fields with a fixed set of valid values, prefer `Literal` or enums
over unrestricted strings. For example, a ticket priority might be
constrained to `"low"`, `"medium"`, or `"high"`.

<br/>

## 4 Create reusable clients through application lifespan

A client often owns an HTTP connection pool and configuration. Creating
a new provider client for every request can waste resources. Prefer one
reusable client per application process or worker when the SDK supports
safe reuse.

FastAPI's lifespan context manager is a suitable place to initialize
shared resources and close them on shutdown.

``` python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from openai import AsyncOpenAI


@asynccontextmanager
async def lifespan(app: FastAPI):
    client = AsyncOpenAI(timeout=20.0, max_retries=2)
    app.state.llm_client = client

    try:
        yield
    finally:
        await client.close()


app = FastAPI(lifespan=lifespan)
```

Important considerations:

-   Use the async client in async request handlers when the SDK provides
    one.
-   Close the client using the SDK's documented cleanup method.
-   Keep API keys in environment-based configuration or a secrets
    manager, not in source code.
-   Do not create a second client in every endpoint if a shared client
    is already available.
-   Confirm thread-safety and lifecycle guidance for the specific SDK
    and deployment model.
-   Lifespan runs per application process; multiple worker processes
    generally each own their own client.

The example demonstrates the lifecycle pattern. Add startup validation
and application-specific configuration as needed.

<br/>

## 5 Dependency injection for services

Expose a dependency that retrieves the application-owned service. This
keeps endpoint functions independent of provider-client construction.

``` python
from fastapi import Request, Depends


def get_llm_service(request: Request):
    return request.app.state.llm_service
```

Initialize the service in lifespan alongside the client:

``` python
@asynccontextmanager
async def lifespan(app: FastAPI):
    client = AsyncOpenAI(timeout=20.0, max_retries=2)
    app.state.llm_service = LLMService(client=client)

    try:
        yield
    finally:
        await client.close()
```

The `LLMService` class is application code that you define. It should
own the use cases---such as extraction and summarization---while the
provider adapter owns SDK-specific calls and response parsing.

An endpoint can then request the service:

``` python
from typing import Annotated
from fastapi import Depends

LLMServiceDependency = Annotated[LLMService, Depends(get_llm_service)]
```

Use dependency overrides in tests to inject a fake service. This avoids
network calls and makes endpoint tests deterministic.

<br/>

## 6 Keep prompts and provider logic out of endpoints

A route should express the HTTP contract and delegate the work.

Avoid embedding large prompts and provider-specific parsing in the
endpoint. Instead:

-   Keep prompt templates in a prompt module or a clearly defined
    service method.
-   Keep provider request construction and response parsing in the
    provider adapter.
-   Keep domain validation in the service layer or domain model.
-   Keep status codes and HTTP response shaping in the route.

A simplified service might look like:

``` python
class LLMService:
    def __init__(self, client):
        self.client = client

    async def extract_ticket(self, text: str) -> TicketExtraction:
        prompt = build_ticket_extraction_prompt(text)
        # The provider adapter should perform the call and validate
        # the structured result before this service returns it.
        return await self.client.extract_ticket(prompt)
```

`build_ticket_extraction_prompt` and `client.extract_ticket` are
application-specific interfaces to implement. The example intentionally
leaves provider-specific details out of the service contract.

<br/>

## 7 Build a structured extraction route

A route should validate the request, call the service, and return a
declared response model.

``` python
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import ValidationError

router = APIRouter(prefix="/llm", tags=["llm"])


@router.post(
    "/extract",
    response_model=ExtractionResponse,
)
async def extract_ticket(
    payload: ExtractionRequest,
    request: Request,
    service: LLMServiceDependency,
):
    request_id = getattr(request.state, "request_id", str(uuid4()))

    try:
        result = await service.extract_ticket(payload.text)
    except TimeoutError:
        raise HTTPException(
            status_code=504,
            detail={"code": "llm_timeout", "request_id": request_id},
        )
    except ValueError:
        raise HTTPException(
            status_code=502,
            detail={"code": "llm_invalid_output", "request_id": request_id},
        )

    return ExtractionResponse(request_id=request_id, result=result)
```

This is a pattern example; adjust exception types to match your
service's explicit error contract. Avoid catching every exception and
returning a generic success-shaped result. Unexpected failures should be
logged with a correlation ID and handled by a centralized exception
handler.

The service must validate the provider's output before constructing
`TicketExtraction`. Pydantic validation at the HTTP boundary cannot
repair invalid model output automatically.

<br/>

### Clear route contract

-   `POST /llm/extract`
-   Request: `ExtractionRequest`
-   Success: `ExtractionResponse`
-   Invalid input: FastAPI's request validation response (typically HTTP
    422)
-   Upstream timeout: mapped to a documented timeout response (example:
    HTTP 504)
-   Invalid provider output: mapped to a safe upstream error (example:
    HTTP 502)

Document response status codes and error schemas in the API's OpenAPI
documentation.

<br/>

## 8 Build a streaming summary route

Streaming endpoints have a different contract from ordinary JSON routes.
For example, Server-Sent Events (SSE) can deliver a sequence of text
deltas and a terminal event.

The provider adapter should convert provider-specific events into
application-level events. The route should not need to understand every
provider event type.

``` python
from fastapi.responses import StreamingResponse
import json


async def summary_event_stream(service, text: str, request_id: str):
    try:
        async for delta in service.stream_summary(text):
            event = {"type": "delta", "request_id": request_id, "text": delta}
            yield f"data: {json.dumps(event)}\n\n"

        event = {"type": "completed", "request_id": request_id}
        yield f"data: {json.dumps(event)}\n\n"
    except Exception:
        # Log the exception internally with request_id.
        # Do not expose raw provider errors or credentials to the client.
        event = {"type": "error", "request_id": request_id, "code": "stream_failed"}
        yield f"data: {json.dumps(event)}\n\n"


@router.post("/summarize/stream")
async def stream_summary(
    payload: ExtractionRequest,
    request: Request,
    service: LLMServiceDependency,
):
    request_id = getattr(request.state, "request_id", str(uuid4()))

    return StreamingResponse(
        summary_event_stream(service, payload.text, request_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Request-ID": request_id,
        },
    )
```

This example uses JSON data frames with SSE's `data:` framing. A
production stream should define its event contract, heartbeat behavior
if needed, proxy buffering settings, and terminal-event semantics.
Ensure the service emits only application-level text deltas and handles
provider-specific completion events.

**Streaming caution:** once response headers and body chunks have been
sent, the server cannot reliably replace the response with a normal HTTP
error status. Represent in-stream failures with a documented terminal
error event, and mark the generation as incomplete in logs. Do not
append a restarted generation to already delivered partial text without
an explicit recovery policy.

<br/>

## 9 Request identifiers, deadlines, and cancellation

A request identifier connects endpoint logs, service logs, provider
calls, and client-reported errors. Generate one if the caller has not
supplied an accepted correlation ID, and validate or sanitize externally
supplied IDs before using them in logs.

A minimal middleware example:

``` python
from uuid import uuid4
from fastapi import Request


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid4())
    request.state.request_id = request_id

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response
```

In production, validate header length and character set, and consider
generating a server-owned ID while separately recording a validated
client correlation ID.

<br/>

### Deadlines

A total application deadline should include provider work and any
retry/backoff time. If the SDK supports per-call timeouts, pass the
remaining time budget rather than allowing each retry to consume the
full original budget.

<br/>

### Cancellation

Clients may disconnect or cancel requests while generation is still
running. Propagate cancellation through the service and provider stream
where supported, and close streaming resources in `finally` blocks or
async context managers. Do not convert cancellation into a normal
successful completion.

Cancellation behavior depends on the framework, ASGI server, SDK, and
provider transport. Test it with the actual deployment stack.

<br/>

## 10 Test the API without calling a real provider

Use FastAPI dependency overrides to inject a fake service. This verifies
request validation and response contracts independently of network
access.

``` python
from fastapi.testclient import TestClient


class FakeLLMService:
    async def extract_ticket(self, text):
        return TicketExtraction(
            category="billing",
            priority="medium",
            summary="Customer has a billing question.",
        )

    async def stream_summary(self, text):
        yield "First part. "
        yield "Second part."


def override_llm_service():
    return FakeLLMService()


app.dependency_overrides[get_llm_service] = override_llm_service

with TestClient(app) as client:
    response = client.post(
        "/llm/extract",
        json={"text": "I have a billing question."},
    )
    assert response.status_code == 200
    assert response.json()["result"]["category"] == "billing"

    invalid = client.post("/llm/extract", json={"text": ""})
    assert invalid.status_code == 422

app.dependency_overrides.clear()
```

The test assumes the router has been included in `app` and that the
service dependency matches the route's dependency declaration. For async
tests, `httpx.AsyncClient` with the appropriate ASGI transport can be
useful. Test streaming behavior separately because buffering in test
clients may differ from production clients and proxies.

Recommended test cases:

-   Valid extraction request returns the declared schema.
-   Missing or empty input is rejected before calling the model.
-   Invalid model output maps to a safe upstream error.
-   Provider timeout maps to the documented timeout response.
-   Streaming emits deltas and a terminal completion event.
-   Stream failure emits a terminal error event and is recorded as
    incomplete.
-   Request ID appears in the response and logs.
-   Client cancellation stops upstream work where supported.
-   Lifespan cleanup closes the shared client.

<br/>

## 11 Operational and security considerations

-   Authenticate callers and apply authorization before allowing costly
    model operations.
-   Enforce input length, output limits, concurrency, and rate limits.
-   Keep credentials in secret configuration, not code or responses.
-   Avoid logging raw prompts and generated content unless justified,
    access-controlled, and privacy-reviewed.
-   Set timeouts and a total request budget.
-   Record model identifier, status, latency, usage source, and
    correlation ID.
-   Return stable application errors rather than raw provider
    exceptions.
-   Configure reverse proxies to avoid buffering SSE responses when
    real-time delivery is required.
-   Define how interrupted streams are represented to clients.
-   Treat request IDs as correlation data, not authentication
    credentials.

<br/>

## 12 Practice and revision

Build a small FastAPI application with two endpoints:

1.  `POST /llm/extract`: accepts validated text, invokes a structured
    extraction service, validates the result, and returns a typed
    response.
2.  `POST /llm/summarize/stream`: accepts text and emits SSE events for
    deltas and completion.

Then verify the following:

-   Reusable async client is initialized and closed through lifespan.
-   Endpoints obtain the service through dependency injection.
-   Prompts and provider-specific parsing live outside route functions.
-   Request and response schemas are explicit and documented.
-   Provider errors are mapped to safe application errors.
-   Request IDs are propagated through logs and responses.
-   Deadlines and cancellation are handled where supported.
-   Fake-service tests cover success, validation failure, timeout, and
    stream interruption.

<br/>

### Checkpoint answer

Reusable model clients should normally be created during application
startup and closed during shutdown so their connection pools and other
resources can be reused across requests. In a multi-worker deployment,
each worker typically owns its own client instance.

Pydantic schemas define stable request and response contracts, and can
also validate extracted structured data before it reaches the API
response. Dependency injection supplies the service to each endpoint,
while the service and provider adapter keep prompts, orchestration, and
SDK-specific response handling out of route code. This separation
improves testability, lifecycle management, and provider portability.

<br/>

## References

-   [FastAPI: Lifespan
    events](https://fastapi.tiangolo.com/advanced/events/)
-   [FastAPI:
    Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/)
-   [FastAPI: Response
    models](https://fastapi.tiangolo.com/tutorial/response-model/)
-   [FastAPI: Streaming
    responses](https://fastapi.tiangolo.com/advanced/custom-response/)
-   [FastAPI: Testing](https://fastapi.tiangolo.com/tutorial/testing/)
-   [OpenAI Python SDK](https://github.com/openai/openai-python)
-   [Pydantic documentation](https://docs.pydantic.dev/)

Check the current FastAPI, Pydantic, SDK, and ASGI server documentation
for exact lifecycle, cancellation, streaming, and timeout behavior
before deploying.
