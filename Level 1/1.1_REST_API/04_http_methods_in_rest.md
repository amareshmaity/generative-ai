# 04. HTTP Methods in REST

## Why methods matter

HTTP methods are the verbs of REST.

The route tells you what resource is involved.
The HTTP method tells you what operation you want to perform on it.

Example:

* `GET /users`
* `POST /users`

Same route, different meaning.

## Main methods

### GET

Used to read or fetch data.

Examples:

* `GET /books`
* `GET /books/2`

Meaning:

* give me data
* do not create or modify anything

### POST

Used to create a resource or trigger processing.

Examples:

* `POST /users`
* `POST /orders`

In GenAI, `POST` is also used when the client sends input for generation or processing.

Example:

* `POST /chat`
* `POST /summaries`

### PUT

Used for full update of an existing resource.

Example:

* `PUT /users/5`

Meaning:

replace the resource with the new version

### PATCH

Used for partial update.

Example:

* `PATCH /users/5`

Meaning:

change only some fields, not the full resource

### DELETE

Used to remove a resource.

Example:

* `DELETE /documents/8`

## How to think about methods

### Resource first

Ask:

* what is the resource?

Then ask:

* what do I want to do with it?

Example:

Resource:

* document

Action:

* fetch all documents -> `GET /documents`
* create a document -> `POST /documents`
* update document 4 -> `PUT /documents/4` or `PATCH /documents/4`
* delete document 4 -> `DELETE /documents/4`

## PUT vs PATCH

This is a classic interview question.

### PUT

Use when replacing the full resource.

Example:

If user has:

```json
{
  "name": "Amit",
  "email": "amit@example.com",
  "role": "admin"
}
```

And you send a full new version, that is `PUT`.

### PATCH

Use when changing only part of the resource.

Example:

Only change:

```json
{
  "email": "new@example.com"
}
```

That is `PATCH`.

## POST is not just "create"

In beginner tutorials, `POST` is often taught only as create.
But in real systems, `POST` can also mean:

* submit input for processing
* trigger a workflow
* start a task

That is why many GenAI APIs use `POST`.

Examples:

* `POST /chat`
* `POST /classify`
* `POST /embeddings`

## Safe and idempotent methods

These terms appear in deeper REST discussions.

### Safe

A safe method should not change server state.

Example:

* `GET`

### Idempotent

If the same request is repeated multiple times, the effect should be the same.

Usually:

* `GET` is idempotent
* `PUT` is idempotent
* `DELETE` is usually idempotent
* `POST` is usually not idempotent

## Bad method usage examples

Bad:

* `GET /create-user`
* `GET /delete-document/9`

Why bad:

`GET` should not perform destructive or creation actions.

Better:

* `POST /users`
* `DELETE /documents/9`

## What to remember

REST becomes much cleaner when:

* the route represents the resource
* the method represents the action

That is one of the central ideas of REST.

