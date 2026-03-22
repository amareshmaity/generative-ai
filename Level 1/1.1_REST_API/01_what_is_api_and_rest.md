# 01. What Is API and What Is REST

## Start with the basic question

Before learning REST API deeply, we need to separate three ideas:

* software
* communication
* rules for communication

One software system often needs data or functionality from another system.
That communication needs a standard way to happen.
That standard way is where APIs come in.

## What is an API?

API means Application Programming Interface.

In simple language, an API is a contract that allows one application to talk to another.

It tells:

* what can be requested
* how to request it
* what response will come back

### Real-life analogy

Think about a restaurant.

* You are the client
* The kitchen is the server
* The menu is the API

The menu tells you:

* what is available
* what you can ask for
* what format the request follows

You do not go inside the kitchen and cook directly.
You use the interface provided to you.

That is how APIs work.

## What is a web API?

A web API is an API exposed over the web, usually using HTTP.

Example:

* a frontend app asks a backend for user data
* a mobile app sends a login request
* a GenAI app sends a prompt to a backend service

## What is REST?

REST stands for Representational State Transfer.

REST is not a language and not a tool.
It is an architectural style for designing web APIs.

That means REST gives a way of thinking about API design.

It encourages us to build APIs around:

* resources
* standard HTTP methods
* predictable URLs
* stateless communication
* standard responses

## What is a REST API?

A REST API is an API designed according to REST principles.

Examples:

* `GET /users`
* `GET /users/10`
* `POST /orders`
* `DELETE /documents/4`

These routes work with resources using standard HTTP methods.

## API vs REST API

This is a very common confusion.

### API

API is the broad concept.
Any interface that allows communication between systems can be an API.

Examples:

* library API
* operating system API
* web API
* REST API
* GraphQL API

### REST API

REST API is one specific style of web API design.

So:

* every REST API is an API
* not every API is a REST API

## Why REST became popular

REST became popular because it is:

* simple
* readable
* easy to understand
* compatible with HTTP
* easy for frontend and backend teams to collaborate on

## Simple example

Imagine we are building an online bookstore.

Possible REST API:

* `GET /books` -> get all books
* `GET /books/5` -> get one book
* `POST /books` -> create a book
* `PUT /books/5` -> update a book
* `DELETE /books/5` -> delete a book

This style is easy to read because the resource is clear: `books`.

## REST is about nouns more than verbs

In REST, URLs usually represent resources, not actions.

Better:

* `/books`
* `/users`
* `/documents`

Less RESTful:

* `/getBooks`
* `/createUser`
* `/deleteDocument`

The action should usually come from the HTTP method, not from the route name.

## Where REST appears in GenAI

In GenAI systems, REST APIs are commonly used for:

* chat requests
* document upload
* retrieval services
* model inference
* conversation history
* evaluation jobs

Even if the AI part is powerful, the system still usually needs a clean API to interact with users and other services.

## What you should remember from this file

* API is a communication contract
* REST is an architectural style for web APIs
* REST APIs use resources, URLs, HTTP methods, and standard responses
* REST is one of the most common foundations of production software, including GenAI systems

