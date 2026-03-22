# 05. REST Request and Response

## REST is communication

A REST API is useful only when the request and response are clear.

So we need to understand what a client sends and what a server returns.

## Parts of a request

A request can contain:

* HTTP method
* URL
* headers
* path parameters
* query parameters
* body

## 1. Method

Tells the action.

Example:

* `GET`
* `POST`
* `PUT`
* `PATCH`
* `DELETE`

## 2. URL

Tells which resource is being targeted.

Example:

```text
/documents/10
```

## 3. Headers

Headers carry metadata about the request.

Examples:

* content type
* authorization
* accepted response format

Common examples:

```http
Content-Type: application/json
Authorization: Bearer token123
```

## 4. Path parameters

Used when the value identifies a specific resource.

Example:

```http
GET /users/8
```

Here `8` is part of the path.

## 5. Query parameters

Used for optional filtering, sorting, searching, or pagination.

Example:

```http
GET /documents?topic=finance&page=2
```

## 6. Body

Used when sending structured data.

Usually used with:

* `POST`
* `PUT`
* `PATCH`

Example:

```json
{
  "question": "Explain this report",
  "document_id": 7
}
```

## Parts of a response

A response usually contains:

* status code
* headers
* body

## Status code

Tells whether the request succeeded or failed.

Examples:

* `200 OK`
* `201 Created`
* `404 Not Found`
* `500 Internal Server Error`

## Response body

In REST APIs, the response body is commonly JSON.

Example:

```json
{
  "id": 7,
  "title": "Annual Report",
  "status": "available"
}
```

## Good request design

A good request should be:

* clear
* structured
* predictable
* easy to validate

Bad:

```json
{
  "x": "hello",
  "y": 9
}
```

Better:

```json
{
  "question": "hello",
  "document_id": 9
}
```

## Good response design

A good response should be:

* consistent
* readable
* useful

Example:

```json
{
  "answer": "The report shows strong growth.",
  "document_id": 9,
  "status": "success"
}
```

## Error response design

A clean API should also have clean error responses.

Bad:

```json
{
  "error": "failed"
}
```

Better:

```json
{
  "error": {
    "code": "DOCUMENT_NOT_FOUND",
    "message": "Document 9 does not exist"
  }
}
```

## Why this matters in real systems

Frontend developers, mobile apps, other services, and AI pipelines all depend on stable request and response formats.

If the format is confusing, the whole system becomes harder to use.

## What to remember

A REST API is not only route design.
It is also about sending and returning data in a way that is clean, consistent, and predictable.

