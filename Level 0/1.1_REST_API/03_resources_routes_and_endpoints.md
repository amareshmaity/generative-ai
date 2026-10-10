# 03. Resources, Routes, and Endpoints

## Why this file matters

A lot of REST confusion disappears once you clearly understand:

* resource
* route
* endpoint
* URL

These terms are related, but they are not exactly the same.

## What is a resource?

A resource is the main thing your API manages.

Examples:

* user
* order
* book
* document
* chat session

In REST, resources are usually written as nouns.

Good examples:

* `/users`
* `/orders`
* `/documents`

## What is a route?

A route is the path pattern in your API.

Examples:

* `/users`
* `/users/{id}`
* `/documents/{document_id}`

It tells the server what path to respond to.

## What is an endpoint?

An endpoint is usually the combination of:

* route
* HTTP method
* behavior

Example:

* `GET /users`
* `POST /users`

These use the same route but are different endpoints because the method and behavior are different.

## What is a URL?

A URL is the full address.

Example:

```text
https://api.example.com/users/10
```

In that full URL:

* domain: `api.example.com`
* route/path: `/users/10`

## Collection resource vs single resource

### Collection resource

Represents a group of items.

Example:

* `/users`
* `/documents`

### Single resource

Represents one item from that collection.

Example:

* `/users/10`
* `/documents/9`

This is a very important REST pattern.

## Nested resources

Sometimes one resource belongs to another.

Example:

* `/users/10/orders`
* `/documents/7/chunks`

Use nested resources when the relationship is clear and meaningful.

But do not over-nest.

Too deep:

* `/companies/1/departments/2/teams/3/employees/4/tasks/8`

That becomes hard to manage.

## Naming conventions

Good REST route naming is usually:

* plural nouns
* lowercase
* simple
* consistent

Good:

* `/users`
* `/blog-posts`
* `/chat-sessions`

Avoid:

* `/getUsers`
* `/create-user-now`
* `/UserData`

## Action in route vs method in route

REST prefers the action to come from the HTTP method.

Example:

* `GET /documents`
* `POST /documents`
* `DELETE /documents/8`

Instead of:

* `/getDocuments`
* `/addDocument`
* `/removeDocument`

## GenAI examples

If you are building a GenAI product, possible resources are:

* `/documents`
* `/conversations`
* `/messages`
* `/evaluations`
* `/prompts`

Possible endpoints:

* `GET /documents`
* `POST /documents`
* `GET /documents/11`
* `DELETE /documents/11`
* `GET /conversations/5/messages`

## Common beginner mistakes

### Mistake 1: treating routes as random names

Routes should reflect resources clearly.

### Mistake 2: mixing actions into URLs

If the method already says what is happening, do not repeat it in the route.

### Mistake 3: inconsistent naming

Bad consistency:

* `/users`
* `/document-data`
* `/getOrders`

Good consistency:

* `/users`
* `/documents`
* `/orders`

## What to remember

* resource = the thing being managed
* route = the path
* endpoint = method plus route plus behavior
* URL = full address

When you understand this clearly, REST design becomes much easier.

