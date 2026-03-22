# 04. Error Response Design

## Why error design matters

An API is not well designed if it only handles success cases clearly.

Error responses should help the client understand:

* what failed
* why it failed
* what can be fixed

## Weak vs strong error responses

Weak:

```json
{
  "error": "failed"
}
```

Problem:

* too vague
* not actionable
* difficult for frontend or logs

Better:

```json
{
  "error": {
    "code": "DOCUMENT_NOT_FOUND",
    "message": "Document 12 does not exist"
  }
}
```

This is more useful.

## What a good error response often includes

Useful parts:

* machine-readable error code
* human-readable message
* optional details for debugging

Example:

```json
{
  "error": {
    "code": "INVALID_INPUT",
    "message": "question must not be empty",
    "details": {
      "field": "question"
    }
  }
}
```

## Match errors with correct status codes

Examples:

* `400 Bad Request` for malformed input
* `401 Unauthorized` for missing auth
* `403 Forbidden` for denied access
* `404 Not Found` for missing resource
* `422 Unprocessable Entity` for validation errors
* `500 Internal Server Error` for unexpected server failures

## Error consistency matters

If different endpoints return completely different error formats, the client side becomes messy.

Try to keep one standard pattern for error responses.

## Good design question

Ask:

If a frontend developer sees this error, will they know what happened and how to handle it?

If not, improve the error response.

## Key takeaway

Clean error responses are part of good API design, not an extra feature.
