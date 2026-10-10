# API Testing Basics

## What is API testing?

API testing checks whether an API behaves correctly from the outside.

Instead of testing one small function only, you test how an endpoint responds to requests.

## What API tests usually check

API tests often verify:

* status code
* JSON response shape
* error behavior
* validation behavior

## Example idea

If you call:

* `GET /health`

you may expect:

* status code `200`
* JSON body with `{"status": "ok"}`

## Why API tests matter

They help confirm that:

* routes are wired correctly
* validation behaves as expected
* clients receive predictable responses

## API testing vs unit testing

Unit testing focuses on small logic pieces.

API testing focuses on the behavior of an endpoint from the client point of view.

Both are useful.

## Common things to test

For an API route, check:

* successful request
* invalid request body
* missing resource
* unauthorized access if auth exists

## Why this matters in FastAPI

FastAPI apps often depend on:

* request validation
* status codes
* structured JSON responses

API tests help confirm these contracts stay stable.

## Key takeaway

API testing checks whether the interface exposed to clients behaves correctly, not just whether internal functions work.
