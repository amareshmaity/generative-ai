# 10. Basic Tool Calling

## Learning objectives

By the end of this chapter, you should be able to:

-   Define a function name, description, and argument schema.
-   Distinguish a model's tool request from actual application
    execution.
-   Allowlist functions and validate arguments before invoking code.
-   Apply authorization, execution limits, and output validation
    independently of the model.
-   Return a function result using the provider's supported correlation
    identifiers and message format.
-   Permit one execution stage and a bounded final model response;
    handle unexpected additional tool requests explicitly.
-   Avoid arbitrary code execution and model-controlled function lookup
    outside the allowlist.

> **Scope boundary:** This chapter covers one application-controlled
> tool interaction. It does not cover autonomous tool-selection loops,
> planning, or agent frameworks; those belong in the separate Agentic AI
> course.

> **Provider note:** Examples use the OpenAI Responses API and Python
> SDK. Tool schemas, response item fields, and follow-up input formats
> are provider-specific. Verify current documentation and the SDK
> version pinned by your project.

<br/>

## 1. What tool calling is

Tool calling lets a model request that an application invoke a named
function with structured arguments. The model does **not** execute that
function itself. The application receives the request, checks it,
decides whether it is permitted, executes the function if allowed, and
returns the result using the provider's documented protocol.

A tool call is therefore a request---not an authorization decision.

``` mermaid
sequenceDiagram
    participant App as Application
    participant Model as Model API
    participant Tool as Allowlisted Function
    App->>Model: User request + tool definitions
    Model-->>App: Structured tool request
    App->>App: Check allowlist, schema, authorization, limits
    alt Allowed
        App->>Tool: Execute validated arguments
        Tool-->>App: Tool result
        App->>Model: Correlated tool result
        Model-->>App: Bounded final response
    else Rejected
        App-->>App: Reject without executing function
    end
```

For this course, keep the workflow deliberately bounded:

1.  Send the request and the available tool definition.
2.  Inspect the model response for a tool request.
3.  Validate and authorize the request.
4.  Execute at most one tool stage.
5.  Return the result using the provider's required correlation ID and
    format.
6.  Request one final model response.
7.  If the model requests another tool or does not produce an acceptable
    final answer, stop and return a controlled outcome.

This is an application-controlled interaction, not an autonomous agent
loop.


<br/>


## 2. Define a function and its argument schema

A useful tool definition has:

-   **Name:** a stable identifier for the operation.
-   **Description:** a concise explanation of what it does and when it
    should be used.
-   **Argument schema:** the fields and types the model may supply.
-   **Application implementation:** trusted code that performs the
    operation.
-   **Policy:** explicit rules for authentication, authorization,
    limits, and error handling.

Example: look up a product in a synthetic, read-only catalog. The model
can request a lookup, but it cannot access arbitrary files, run SQL, or
call arbitrary Python functions.

``` python
TOOL_DEFINITION = {
    "type": "function",
    "name": "lookup_catalog_item",
    "description": (
        "Look up one item in the synthetic product catalog by its exact item ID. "
        "Use only for catalog items the current user is authorized to view."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "item_id": {
                "type": "string",
                "description": "Exact catalog item identifier, such as ITEM-100",
            }
        },
        "required": ["item_id"],
        "additionalProperties": False,
    },
    "strict": True,
}
```

This illustrates the function-tool format used by supported Responses
API versions. Exact schema requirements and strict-mode support can
vary. Confirm them in the provider's current documentation.

A strict provider schema can help constrain generated arguments, but
application code must still validate them. Never treat a model-generated
argument as trusted input.


<br/>


## 3. Separate the model's request from execution

A model response may contain a structured function-call item. The
application should inspect the item type and extract only the fields
defined by the provider protocol.

In the Responses API, a function call is represented as an output item
with fields such as `name`, `arguments`, and `call_id`. The exact SDK
types depend on the installed version.

``` python
def get_single_tool_request(response) -> dict | None:
    calls = [
        item for item in response.output
        if item.type == "function_call"
    ]

    if not calls:
        return None

    # This bounded chapter intentionally permits one call only.
    if len(calls) != 1:
        raise ValueError("Expected at most one tool request.")

    call = calls[0]
    return {
        "name": call.name,
        "arguments": call.arguments,
        "call_id": call.call_id,
    }
```

The application must not execute a function merely because the model
named it. First check that the name is in a fixed allowlist, parse the
arguments, validate their structure, and apply authorization rules.

**Unsafe pattern:**

``` python
# Never do this with model-controlled input:
function = globals()[model_requested_name]
result = function(**model_arguments)
```

This gives model output control over application function lookup and may
expose unintended operations.

**Safer pattern:** use a fixed mapping from permitted tool names to
trusted functions, and validate every argument before dispatch.


<br/>


## 4. Build a read-only synthetic catalog

The practice implementation uses an in-memory catalog and does not
access real customer or production data.

``` python
CATALOG = {
    "ITEM-100": {"name": "USB-C Cable", "stock": 24},
    "ITEM-200": {"name": "Wireless Mouse", "stock": 8},
    "ITEM-300": {"name": "Laptop Stand", "stock": 0},
}

def lookup_catalog_item(item_id: str) -> dict:
    item = CATALOG.get(item_id)
    if item is None:
        return {
            "ok": False,
            "error": "item_not_found",
        }

    return {
        "ok": True,
        "item": {
            "item_id": item_id,
            "name": item["name"],
            "stock": item["stock"],
        },
    }
```

The function is read-only. It returns only the fields the caller needs
and uses a controlled error code for unknown items. Avoid returning
internal records or sensitive fields just because they exist in the
underlying data source.


<br/>


## 5. Validate arguments, authorization, and execution limits

Treat the model's arguments as untrusted input even when the provider
constrained their schema.

``` python
import json
from pydantic import BaseModel, ConfigDict, Field, ValidationError

class CatalogLookupArgs(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    item_id: str = Field(min_length=1, max_length=32, pattern=r"^ITEM-[0-9]{3}$")

def parse_tool_arguments(raw_arguments: str) -> CatalogLookupArgs:
    try:
        payload = json.loads(raw_arguments)
    except json.JSONDecodeError as exc:
        raise ValueError("Tool arguments are not valid JSON.") from exc

    try:
        return CatalogLookupArgs.model_validate(payload)
    except ValidationError as exc:
        raise ValueError("Tool arguments failed validation.") from exc
```

Validation checks shape and format. Authorization is separate:

``` python
def is_authorized_for_catalog(user_context: dict, item_id: str) -> bool:
    # Synthetic policy for the exercise.
    # In production, derive identity and permissions from trusted auth context,
    # never from model-supplied arguments.
    return user_context.get("can_read_catalog", False)
```

A safe dispatch function combines these checks and an allowlist:

``` python
ALLOWED_TOOLS = {
    "lookup_catalog_item": lookup_catalog_item,
}

def execute_tool_request(
    *,
    tool_name: str,
    raw_arguments: str,
    user_context: dict,
) -> dict:
    if tool_name not in ALLOWED_TOOLS:
        return {"ok": False, "error": "tool_not_allowed"}

    if tool_name != "lookup_catalog_item":
        return {"ok": False, "error": "tool_not_implemented"}

    try:
        args = parse_tool_arguments(raw_arguments)
    except ValueError:
        return {"ok": False, "error": "invalid_arguments"}

    if not is_authorized_for_catalog(user_context, args.item_id):
        return {"ok": False, "error": "not_authorized"}

    # Execution budget for this bounded example: exactly one read-only call.
    return ALLOWED_TOOLS[tool_name](args.item_id)
```

Production controls may additionally include per-user quotas, request
deadlines, audit events, concurrency limits, data-access scopes, and
output-size limits. These checks belong to the application, not to the
model.


<br/>


## 6. Return the tool result with correlation identifiers

A provider needs to associate a tool result with the request that
produced it. In the Responses API, a function-call output uses the
`call_id` from the model's function-call item.

The follow-up request format is provider-specific. The example below
illustrates the OpenAI Responses API pattern:

``` python
from openai import OpenAI
import json

client = OpenAI()

response = client.responses.create(
    model="YOUR_SUPPORTED_MODEL",
    input="Look up ITEM-100 in the catalog.",
    tools=[TOOL_DEFINITION],
    tool_choice="auto",
)

tool_request = get_single_tool_request(response)

if tool_request is None:
    # Handle a normal text response according to the application contract.
    print(response.output_text)
else:
    result = execute_tool_request(
        tool_name=tool_request["name"],
        raw_arguments=tool_request["arguments"],
        user_context={"can_read_catalog": True},  # Synthetic example only
    )

    tool_output = {
        "type": "function_call_output",
        "call_id": tool_request["call_id"],
        "output": json.dumps(result),
    }

    follow_up = client.responses.create(
        model="YOUR_SUPPORTED_MODEL",
        previous_response_id=response.id,
        input=[tool_output],
        tools=[TOOL_DEFINITION],
        tool_choice="none",
    )

    print(follow_up.output_text)
```

Implementation notes:

-   The model name is a placeholder; use a currently supported model
    with tool-calling capability.
-   Check current SDK documentation for the exact response item fields
    and follow-up request shape.
-   `previous_response_id` is one supported way to continue a Responses
    API interaction; another provider or endpoint may require a
    different message history format.
-   The second request uses `tool_choice="none"` to prevent another tool
    request in this bounded example where supported.
-   Still inspect the follow-up response status and output. Do not
    assume the model returned a usable final answer.
-   If the initial response requests an unknown tool or multiple calls,
    reject the request without executing any function.
-   If the provider or model cannot guarantee the desired bounded
    behavior, enforce the limit in application code and stop after the
    allowed stage.


<br/>


## 7. Handle unexpected additional tool requests

A bounded design must define what happens when the model requests more
than one tool, requests an unknown tool, or asks for another tool after
the single permitted execution stage.

Recommended behavior:

1.  **Unknown tool name:** reject it; do not look up arbitrary functions
    dynamically.
2.  **Multiple tool requests:** reject or return a controlled
    unsupported-operation outcome; do not execute some of them
    accidentally.
3.  **Malformed arguments:** return a controlled tool error or stop,
    depending on the application contract.
4.  **Unauthorized request:** do not execute the function; record a safe
    audit event if appropriate.
5.  **Additional tool request after execution:** stop the workflow and
    return an explicit bounded-workflow error or safe fallback.
6.  **Provider/API failure:** handle as a provider error, not as a tool
    result.
7.  **No usable final response:** return a controlled failure instead of
    claiming success.

For this chapter, do not implement a `while` loop that repeatedly sends
tool results to the model until it stops requesting tools. That is an
autonomous tool-execution loop and is outside this course's scope.


<br/>


## 8. Validate tool output before returning it to the model

Tool output is application data, but it may still be malformed,
unexpectedly large, or contain sensitive fields. Validate and minimize
it before sending it back to the model.

For example:

``` python
from pydantic import BaseModel, ConfigDict, Field

class CatalogItemResult(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    item_id: str
    name: str = Field(min_length=1, max_length=100)
    stock: int = Field(ge=0)

def validate_catalog_item_result(payload: dict) -> CatalogItemResult:
    return CatalogItemResult.model_validate(payload)
```

In a production implementation, distinguish the `item_not_found` error
result from the successful item schema rather than forcing both into the
same model. Apply the schema that matches each outcome.

Also consider that tool results can contain text originating from
external or user-controlled sources. Treat such text as data, not as new
instructions that override application policy.


<br/>


## 9. Practice: synthetic catalog lookup with mixed cases

Use the catalog and helper functions above. Test these four cases
without calling a real provider:

``` python
test_cases = [
    {
        "name": "known_item",
        "tool_name": "lookup_catalog_item",
        "arguments": '{"item_id":"ITEM-100"}',
        "user_context": {"can_read_catalog": True},
    },
    {
        "name": "unknown_item",
        "tool_name": "lookup_catalog_item",
        "arguments": '{"item_id":"ITEM-999"}',
        "user_context": {"can_read_catalog": True},
    },
    {
        "name": "malformed_arguments",
        "tool_name": "lookup_catalog_item",
        "arguments": '{"item_id":',
        "user_context": {"can_read_catalog": True},
    },
    {
        "name": "unauthorized",
        "tool_name": "lookup_catalog_item",
        "arguments": '{"item_id":"ITEM-100"}',
        "user_context": {"can_read_catalog": False},
    },
    {
        "name": "unknown_tool",
        "tool_name": "delete_catalog",
        "arguments": '{"item_id":"ITEM-100"}',
        "user_context": {"can_read_catalog": True},
    },
]

for case in test_cases:
    result = execute_tool_request(
        tool_name=case["tool_name"],
        raw_arguments=case["arguments"],
        user_context=case["user_context"],
    )
    print(case["name"], "->", result)
```

Expected behavior:

| Case                     | Expected Outcome      | Was Catalog Function Executed? |
| ------------------------ | --------------------- | ------------------------------ |
| Known item, authorized   | Item details returned | Yes                            |
| Unknown item, authorized | `item_not_found`      | Yes, read-only lookup          |
| Malformed arguments      | `invalid_arguments`   | No                             |
| Unauthorized user        | `not_authorized`      | No                             |
| Unknown tool name        | `tool_not_allowed`    | No                             |


### Practice extensions

-   Add an item ID with the wrong pattern and confirm validation rejects
    it.
-   Add a user context with read permission only for a subset of item
    IDs.
-   Add an output schema and validate successful results.
-   Simulate a model request containing two function calls and confirm
    the application executes neither.
-   Simulate a second tool request in the final response and confirm the
    application stops rather than looping.
-   Record an audit event without logging sensitive arguments or user
    data.


<br/>


## 10. Checkpoint: how does application code control whether a tool runs?

The model only proposes a function name and arguments. Application code
decides whether the proposal is permitted.

Before execution, the application checks that the function name belongs
to a fixed allowlist, parses and validates the arguments, verifies the
current user's authorization using trusted context, and enforces
execution limits. Only then does it call the trusted function. It
validates and minimizes the result before returning it to the model or
the caller.

A schema-constrained tool request does not replace these controls. The
model must never be the authority for permissions, and model-generated
names must never drive arbitrary function lookup or code execution.

<br/>

## 11. Scope boundary: one controlled tool interaction

This chapter deliberately limits the workflow to one tool-execution
stage and one bounded final model response. It does not implement
autonomous planning, repeated tool selection, long-running task
orchestration, or agent frameworks. Those topics belong in the separate
Agentic AI course.

<br/>

## 12. Key takeaways

-   A tool request is not execution; the application is the decision
    point.
-   Define tool names, descriptions, and argument schemas explicitly.
-   Use a fixed allowlist and never perform arbitrary model-controlled
    function lookup.
-   Validate arguments, authorization, execution limits, and outputs
    independently.
-   Correlate tool results with the provider's documented call
    identifier and format.
-   Bound the workflow and explicitly reject unexpected additional tool
    requests.
-   Keep this integration single-stage; autonomous agent loops are out
    of scope.

<br/>

## References

-   OpenAI API documentation --- Function calling:
    https://platform.openai.com/docs/guides/function-calling
-   OpenAI API reference --- Responses:
    https://platform.openai.com/docs/api-reference/responses
-   OpenAI Python SDK: https://github.com/openai/openai-python
-   Pydantic documentation --- Models:
    https://docs.pydantic.dev/latest/concepts/models/

Check the current provider documentation and pinned SDK version before
relying on exact tool schemas, call identifiers, or follow-up request
parameters.
