# Common Authentication Methods

## No single method fits everything

Different systems use different authentication approaches.

The right choice depends on:

* who is calling the API
* whether a browser is involved
* how much security and control are needed

## Username and password

This is the most familiar login style.

The user sends credentials, and the server verifies them.

Important note:

Passwords should never be stored in plain text.
They should be hashed securely.

## Session-based authentication

This is common in traditional web apps.

Typical flow:

1. user logs in
2. server creates a session
3. browser stores a session cookie
4. later requests include that cookie

This works well for many browser-based applications.

## API key authentication

An API key is a secret string used to identify a client application.

It is often used for:

* internal tools
* service-to-service APIs
* simple developer platforms

## Bearer token authentication

A bearer token is usually sent in the `Authorization` header.

Example:

```text
Authorization: Bearer <token>
```

If a client has the token, it can use it.
That is why the token must be protected carefully.

## JWT at a basic level

JWT stands for JSON Web Token.

At a high level, it is a token that carries some structured information such as:

* user id
* role
* expiration time

JWT is often used with bearer token authentication.

You do not need to go deep into JWT internals yet.

## OAuth and social login

OAuth is commonly used when users log in through services like:

* Google
* GitHub
* Microsoft

This is very common in real products, but it is a bigger topic.
For now, it is enough to know that OAuth helps delegate login to a trusted identity provider.

## Quick intuition

Use this mental map:

* session cookie for many browser apps
* API key for simple app or service access
* bearer token for modern API clients
* OAuth when external identity providers are involved

## Key takeaway

Authentication methods differ in how identity is proved, stored, and sent with each request.
