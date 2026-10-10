# 02. REST Principles

## Why principles matter

If you only memorize routes like `GET /users`, you may know the syntax but not the design logic.

REST becomes clear when you understand its core principles.

These principles explain why REST APIs look the way they do.

## 1. Client-server separation

In REST, the client and server have separate responsibilities.

### Client

The client is usually:

* browser
* mobile app
* frontend application
* another backend service

The client sends requests and displays or uses the response.

### Server

The server:

* stores or processes data
* applies business logic
* sends responses back

### Why this matters

This separation makes systems easier to build and maintain.

Example:

* frontend team can work on UI
* backend team can work on API

## 2. Statelessness

This is one of the most important REST concepts.

Stateless means each request should contain enough information for the server to process it.

The server should not depend on hidden memory of previous requests.

### Good example

```http
POST /chat
Authorization: Bearer token123
Content-Type: application/json

{
  "question": "Summarize the document",
  "document_id": 20
}
```

This request contains the needed context.

### Why statelessness is useful

* easier scaling
* easier debugging
* simpler architecture
* requests are more independent

### Important note

Stateless does not mean the server can never store data.
It means each request should be understandable on its own.

## 3. Resource-based design

REST is centered around resources.

A resource is the thing your API manages.

Examples:

* users
* products
* orders
* documents
* chats

You design routes around these resources.

Example:

* `/users`
* `/documents`
* `/orders/55`

## 4. Uniform interface

REST encourages consistency.

That means:

* similar rules across endpoints
* standard HTTP methods
* clear naming
* predictable response patterns

This makes APIs easier to learn and use.

## 5. Layered system

The client does not need to know whether it is talking directly to the main server or through other layers.

There may be:

* gateway
* load balancer
* cache
* proxy
* backend service

The client still uses the API in the same way.

## 6. Cacheability

Some REST responses can be cached.

This can improve performance.

Example:

* list of public products
* static metadata

For beginners, just know that REST works well with caching concepts.

## Common misunderstanding

Many people think REST only means using HTTP methods.
That is not enough.

True REST thinking is about:

* resource design
* statelessness
* consistency
* clear separation of concerns

## REST principle summary

Good REST API design usually feels:

* simple
* predictable
* clean
* resource-oriented
* easy to scale

## Quick reflection

If you design:

* weird route names
* inconsistent responses
* action-heavy URLs
* hidden state between requests

then the API is moving away from RESTful design.

## What to remember

The most important REST principles for beginners are:

* client-server separation
* statelessness
* resource-based design
* uniform interface

