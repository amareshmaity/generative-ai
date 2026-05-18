# What Is Authentication?

## Start with the main question

When a user or system sends a request, the server may ask:

Who are you?

Authentication is the process of verifying identity.

## Authentication vs authorization

These two ideas are related but different.

Authentication means:

* prove who you are

Authorization means:

* decide what you are allowed to do

Simple example:

* logging in with email and password is authentication
* being allowed to delete a file is authorization

## Why authentication matters

Without authentication, many APIs would be unsafe.

A server needs a way to decide whether a request comes from:

* a real user
* a trusted application
* an internal service

## Common things used for authentication

Identity may be verified with:

* username and password
* API key
* bearer token
* session cookie
* OAuth-based login

## Authentication in backend APIs

In APIs, authentication often happens before the main business logic runs.

The server may:

1. read a header, cookie, or token
2. check whether it is valid
3. allow or reject the request

If the credentials are invalid, the API usually returns an error such as:

* `401 Unauthorized`

## Why this matters in GenAI

GenAI applications often work with:

* private documents
* paid model APIs
* team knowledge bases
* user-specific chat history

That means the backend must know which user or system is making the request.

## Key takeaway

Authentication answers the question:
Who is making this request?
