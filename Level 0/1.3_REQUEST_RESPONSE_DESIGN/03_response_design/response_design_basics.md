# 03. Response Design Basics

## What is response design?

Response design means deciding how the server returns data after handling a request.

A response should help the client understand:

* what happened
* whether the request succeeded
* what data is being returned
* what to do next if needed

## Good responses are predictable

A good response is usually:

* structured
* readable
* consistent
* useful

Clients should not have to guess what fields will appear.

## Example of a clear response

```json
{
  "status": "success",
  "document_id": 12,
  "summary": "The report shows stable quarterly growth."
}
```

This tells the client:

* the request succeeded
* which resource it relates to
* what the result is

## Include meaningful fields

Response fields should serve a purpose.

Common useful fields:

* `id`
* `status`
* `message`
* `data`
* `answer`
* `created_at`

Avoid vague responses like:

```json
{
  "data": "ok"
}
```

That tells very little.

## Consistency matters

If one endpoint returns:

```json
{
  "status": "success",
  "answer": "..."
}
```

and another returns:

```json
{
  "result_ok": true,
  "output_text": "..."
}
```

the API becomes harder to consume.

Try to keep naming and structure consistent across endpoints.

## Response shape depends on the use case

### Single resource

```json
{
  "id": 5,
  "name": "Report A"
}
```

### Collection

```json
{
  "items": [
    {"id": 1, "name": "Report A"},
    {"id": 2, "name": "Report B"}
  ],
  "page": 1,
  "total": 2
}
```

### Action or processing result

```json
{
  "status": "success",
  "answer": "The report highlights low churn."
}
```

## Key takeaway

Good responses reduce confusion and make client integration much smoother.
