# Level 6: LLM APIs and Application Development

Integrate language models into software applications using provider SDKs, validated data contracts, and reliable backend patterns. Build a small FastAPI service with structured output, streaming, controlled tool calling, and measurable quality.

This README is the plan for creating notes one by one. Keep numbered Markdown notes directly in `Level 6`, following the previous levels. The filenames below are planned files, not existing chapter links.

<br/>

## Prerequisites

- Complete [Level 5: Prompt Engineering and Structured Generation](<../Level 5/README.md>).
- Review Level 0 foundations: REST, FastAPI, Pydantic, async/await, authentication, configuration, logging, and testing.
- Understand messages, token budgets, generation settings, schemas, and trust boundaries.
- Have an isolated Python environment. Live exercises need an available model service; prepared responses and fake clients can support offline development and testing.

<br/>

## Learning outcomes

After completing this level, you should be able to:

- Configure a provider client without exposing credentials.
- Construct model requests and inspect responses, completion status, and usage metadata.
- Implement synchronous, asynchronous, streaming, and supported batch interactions.
- Validate structured outputs and execute one bounded, application-controlled function call.
- Handle timeouts, transient failures, rate limits, and cancellation.
- Integrate model calls into authenticated, validated FastAPI endpoints.
- Test application behavior separately from probabilistic model quality.
- Document provider differences, quality, latency, and cost.

<br/>

## Study order and planned note files

| Order | Planned note filename | Focus |
|---|---|---|
| 1 | `01_llm_application_architecture.md` | Request flow and separation of responsibilities |
| 2 | `02_provider_sdks_and_first_request.md` | Direct SDK setup and a minimal model request |
| 3 | `03_api_keys_and_secret_management.md` | Credentials, configuration, and safe handling |
| 4 | `04_model_initialization_and_configuration.md` | Client lifecycle, model choice, and request settings |
| 5 | `05_messages_and_response_objects.md` | Messages, output content, completion status, and metadata |
| 6 | `06_synchronous_and_asynchronous_calls.md` | Blocking I/O, async clients, concurrency, and cancellation |
| 7 | `07_streaming_responses.md` | Events, partial output, disconnects, and stream completion |
| 8 | `08_batch_processing.md` | Supported batch jobs and bounded client-side concurrency |
| 9 | `09_structured_output_apis.md` | Schema integration, validation, and failure handling |
| 10 | `10_basic_tool_calling.md` | Validated, allowlisted, application-controlled function execution |
| 11 | `11_token_usage_and_metadata.md` | Usage accounting, estimates, and measurement |
| 12 | `12_timeouts_retries_and_rate_limits.md` | Reliability, backoff, limits, and safe errors |
| 13 | `13_provider_abstraction_and_portability.md` | Small adapters and explicit capability differences |
| 14 | `14_fastapi_integration.md` | Routes, dependencies, service layers, and client lifecycle |
| 15 | `15_request_and_response_validation.md` | External contracts and business-rule checks |
| 16 | `16_authentication_and_access_control.md` | User identity, authorization, and resource ownership |
| 17 | `17_logging_and_endpoint_testing.md` | Safe diagnostics, fake clients, and integration checks |
| 18 | `18_practice_and_revision.md` | Baseline evaluation and the level project |

<br/>

## Chapter outlines

### 01. LLM Application Architecture

- Trace a user request through API validation, business logic, model integration, and response validation.
- Separate provider-specific code from application contracts.
- Identify trusted configuration, user input, generated output, and permitted actions.
- Introduce request identifiers, error boundaries, and measurement points.
- Design a minimal folder layout for routes, schemas, services, adapters, and tests.

**Practice:** Draw the request flow for a document summarization endpoint.

**Checkpoint:** Explain where validation, authorization, and model calls happen.

<br/>

### 02. Direct Provider SDKs and a First Request

- Select one provider and consult its current official SDK documentation.
- Install and record a compatible SDK version.
- Construct a minimal request and inspect its response.
- Distinguish the SDK, API endpoint, model identifier, and hosted service.
- Introduce supported capabilities and avoid assuming all providers expose identical APIs.

**Practice:** Make one small request using synthetic text, or inspect a documented response fixture offline.

**Checkpoint:** Identify the request parameters and the content returned by the service.

<br/>

### 03. API Keys and Secret Management

- Load credentials through environment variables or a suitable secret store.
- Keep local secret files out of version control and provide placeholder configuration examples.
- Validate missing configuration without printing credential values.
- Keep provider credentials on the backend rather than exposing them to browser clients.
- Introduce credential rotation, least privilege, and separate development/production settings.
- Distinguish provider authentication from authenticating users of your application.

**Practice:** Create safe configuration loading and an example environment file containing no real secrets.

**Checkpoint:** Explain which credentials belong to the service and which identify its users.

<br/>

### 04. Model Initialization and Configuration

- Configure clients, model identifiers, endpoints, and default request settings.
- Distinguish initializing an API client from loading model weights locally.
- Set supported output limits, generation controls, and timeouts explicitly.
- Manage reusable clients and connection cleanup.
- Record model and prompt versions alongside configuration.
- Detect unsupported settings rather than silently assuming they take effect.

**Practice:** Build a typed configuration object with startup validation.

**Checkpoint:** Separate application configuration, client options, and per-request parameters.

<br/>

### 05. Messages and Response Objects

- Map application instructions, user content, and conversation turns to supported message structures.
- Inspect output parts rather than assuming every response is one text string.
- Handle refusals, tool requests, empty content, and incomplete generation where supported.
- Inspect completion status, identifiers, and usage fields.
- Normalize application-relevant fields while preserving useful provider metadata safely.

**Practice:** Parse fixtures representing successful text, incomplete output, refusal, and a tool request.

**Checkpoint:** Distinguish a successful HTTP response from a usable application answer.

<br/>

### 06. Synchronous and Asynchronous Calls

- Compare blocking SDK calls with async client calls.
- Review awaiting I/O and avoiding blocking work inside async request handlers.
- Reuse clients appropriately and bound concurrent requests.
- Handle cancellation and cleanup when a caller disconnects or a deadline expires.
- Distinguish I/O concurrency from parallel model computation.

**Practice:** Compare sequential calls with bounded concurrent calls using a fake client or small live requests.

**Checkpoint:** Explain why unbounded concurrency can worsen rate limiting and resource use.

<br/>

### 07. Streaming Responses

- Distinguish provider stream events from your application's transport format.
- Accumulate text or structured deltas and detect stream completion.
- Introduce server-sent events or another documented streaming response contract.
- Handle disconnects, cancellation, partial failures, and backpressure conceptually.
- Explain why completed structured output should be validated before consequential use.
- Measure time to first content and total completion time.

**Practice:** Implement a stream with a fake event source, including a mid-stream failure and client cancellation.

**Checkpoint:** Distinguish partial content from a completed, validated response.

<br/>

### 08. Batch Processing Where Supported

- Compare provider-managed batch jobs with bounded concurrent client requests.
- Prepare records with stable identifiers and validated inputs.
- Trace submission, status checks, results, and cancellation where available.
- Match results by identifier rather than assuming input order is preserved.
- Handle per-item failures and retry only appropriate items.
- Compare delayed processing with interactive latency requirements.

**Practice:** Design a small classification batch with mixed successes and failures.

**Checkpoint:** Explain which behavior depends on the provider's batch API.

<br/>

### 09. Structured Output APIs

- Translate an application schema into supported provider request options.
- Distinguish JSON syntax constraints from schema-constrained generation.
- Validate returned data with Pydantic and independent business rules.
- Handle unsupported schema features, refusals, truncation, and invalid output.
- Use bounded recovery and explicit failure responses.

**Practice:** Build an extraction operation with valid, malformed, missing-field, and semantically invalid fixtures.

**Checkpoint:** Explain why schema compliance does not establish factual correctness.

<br/>

### 10. Basic Tool Calling

- Define a function name, description, and argument schema.
- Distinguish a model's tool request from actual application execution.
- Allowlist functions and validate arguments before invoking code.
- Apply authorization, execution limits, and output validation independently of the model.
- Return a function result using the provider's supported correlation identifiers and message format.
- Permit one execution stage and a bounded final model response; handle unexpected additional tool requests explicitly.
- Avoid arbitrary code execution and model-controlled function lookup outside the allowlist.

**Practice:** Implement one read-only lookup against a synthetic catalog, including unknown items, malformed arguments, and unauthorized requests.

**Checkpoint:** Explain how application code controls whether the requested function is allowed to run.

**Scope boundary:** This is a single application-controlled tool interaction. Autonomous tool-selection loops, planning, and agent frameworks belong to the separate Agentic AI course.

<br/>

### 11. Token Usage and Usage Metadata

- Inspect reported input, output, cached-input, or reasoning usage where documented.
- Distinguish provider-reported usage from local tokenizer estimates.
- Handle absent metadata, especially during streams or incomplete requests.
- Record latency, model identifiers, completion status, and request identifiers.
- Estimate cost using verified pricing and clearly stated accounting assumptions.
- Avoid treating missing usage as zero consumption.

**Practice:** Create a usage summary from fixtures with complete and missing metadata.

**Checkpoint:** Separate observed usage, estimated usage, and calculated cost.

<br/>

### 12. Timeouts, Retries, Rate Limits, and Errors

- Define connection/read timeouts and a total request deadline where supported.
- Categorize transient failures separately from authentication and invalid-request errors.
- Introduce bounded exponential backoff, jitter, and supported retry hints.
- Inspect SDK retry defaults to avoid multiplying retries across layers.
- Distinguish request limits, token limits, and application concurrency limits.
- Discuss duplicate requests, possible duplicate cost, and documented idempotency support.
- Map failures to safe application errors without leaking provider details or credentials.

**Practice:** Simulate timeout, throttling, and invalid-credential cases; verify bounded retry behavior.

**Checkpoint:** Explain why every failure should not be retried and why partial streams need special handling.

<br/>

### 13. Provider Abstraction and Model Portability

- Define a small interface around capabilities the application actually needs.
- Normalize text results, structured data, errors, and usage carefully.
- Keep provider-specific adapters and explicit capability checks.
- Discuss differences in roles, schemas, tool formats, streaming, and generation controls.
- Validate behavioral changes when switching models or providers.
- Avoid silently downgrading unsupported features.

**Practice:** Implement a fake adapter and one real adapter, with a comparison matrix for a second provider.

**Checkpoint:** Explain why a shared interface does not guarantee identical model behavior.

<br/>

### 14. FastAPI Integration

- Apply Level 0 routing, dependency injection, and service-layer patterns.
- Configure client creation and cleanup through application lifecycle management.
- Build async endpoints with validated request and response models.
- Connect structured-output and streaming operations to clear route contracts.
- Propagate request identifiers, deadlines, and cancellation appropriately.
- Separate endpoint code from prompts and provider-specific response handling.

**Practice:** Build a small API exposing a validated extraction route and a streaming summary route.

**Checkpoint:** Explain how reusable model clients and schemas fit into the application's lifecycle.

<br/>

### 15. Request and Response Validation

- Bound input length, output budgets, and supported task parameters.
- Validate allowed models and options rather than accepting arbitrary backend configuration.
- Apply business rules beyond field types.
- Return consistent success and error contracts.
- Validate generated output before storing it or passing it downstream.
- Distinguish regular JSON responses from streaming event contracts.

**Practice:** Test invalid input, unsupported options, excessive sizes, and invalid model output.

**Checkpoint:** Explain which checks happen before the provider call and which happen after it.

<br/>

### 16. Basic Authentication and Access Control

- Apply a suitable basic authentication mechanism for the teaching application.
- Derive user identity from validated credentials rather than model-generated claims.
- Authorize routes, tool operations, and user-owned resources separately.
- Keep provider keys separate from application-user credentials.
- Introduce per-user limits and isolation between users.
- Test unauthorized and cross-user access attempts.

**Practice:** Protect the API and ensure the catalog lookup obeys application authorization rules.

**Checkpoint:** Explain why prompting the model to respect permissions cannot replace server-side checks.

<br/>

### 17. Logging and Testing Model-Backed Endpoints

- Log request identifiers, status, latency, retries, and usage without exposing secrets or sensitive content.
- Keep raw prompt/response capture optional, controlled, and redacted where needed.
- Use fake clients and fixtures for deterministic validation and error-path tests.
- Test streaming completion, cancellation, tool arguments, authorization, and retry bounds.
- Separate optional live integration checks from routine offline tests.
- Evaluate probabilistic task quality using a fixed dataset rather than exact-string endpoint assertions.

**Practice:** Write meaningful tests for failure paths and access boundaries, then run a small quality evaluation separately.

**Checkpoint:** Distinguish backend correctness tests from model-quality measurements.

<br/>

### 18. Practice and Revision

- Make and inspect a provider request.
- Implement structured output, streaming, and one controlled tool call.
- Add deadlines, bounded retries, authentication, validation, and safe logs.
- Exercise batch processing through supported APIs or documented fixtures.
- Compare provider capabilities and measure application behavior.
- Complete the service project below.

**Checkpoint:** Demonstrate useful output and predictable failure handling using reproducible examples.

<br/>

## Level deliverable: Small model-backed FastAPI service

Build a project with:

1. A reproducible environment and documented setup using placeholder credentials.
2. Typed configuration and reusable provider-client lifecycle management.
3. A structured extraction endpoint with Pydantic and business-rule validation.
4. A streaming summary endpoint with documented event and error behavior.
5. One read-only, allowlisted tool interaction with validated arguments and authorization.
6. Authentication, input limits, request deadlines, bounded retries, and safe errors.
7. Usage and latency reporting where available, with estimates clearly labeled.
8. Offline tests covering valid requests, invalid output, provider failures, cancellation, and unauthorized access.
9. A fixed evaluation set of at least ten cases, including missing information and difficult inputs, with output-validity and task-quality results.
10. An architecture diagram, sample requests, known limitations, and a provider-capability comparison.

Use synthetic or public data. Fake clients support development without paid services; clearly distinguish fixture-based checks from live model results. Containerization, cloud deployment, and comprehensive observability are developed in Level 15.

<br/>

## Suggested format for each note

1. Learning objectives and Level 0/5 concepts being applied.
2. Request-flow diagram or concrete use case.
3. Minimal implementation with explained contracts.
4. Provider-specific capabilities and verified documentation.
5. Success, failure, and cancellation examples where relevant.
6. Validation, trust boundaries, and operational trade-offs.
7. Exercise and revision questions with answers.
8. References and optional extensions.

Verify current SDK versions, API parameters, message formats, capabilities, rate-limit behavior, and pricing when writing code notes. Keep examples small and runnable, and never commit real credentials.

<br/>

## Completion checklist

- [ ] Configure a provider SDK and credentials safely.
- [ ] Construct requests and inspect content, status, and metadata.
- [ ] Use sync and async calls with bounded concurrency.
- [ ] Handle streaming completion, failure, and disconnects.
- [ ] Explain provider batch jobs versus concurrent calls.
- [ ] Validate structured output and handle incomplete or refused responses.
- [ ] Execute one authorized, allowlisted tool call with validated arguments.
- [ ] Distinguish usage measurements from estimates.
- [ ] Apply timeouts, bounded retries, and rate-limit handling.
- [ ] Document capability differences behind a small provider adapter.
- [ ] Integrate authenticated, validated FastAPI routes.
- [ ] Test error paths and evaluate task quality separately.
- [ ] Complete and document the service project.

<br/>

## Scope and next step

This level applies existing backend foundations to LLM integration. It does not require training models, implementing RAG, or building autonomous agents. Systematic evaluation, comprehensive security, and production deployment are expanded in Levels 13–15.

Next: **Level 7 — Embeddings and Semantic Search** in the [main course outline](../README.md).
