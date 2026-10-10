# API Keys and Tokens

## Why this topic matters

In backend and GenAI systems, you will constantly see:

* API keys
* access tokens
* secret keys

If you do not understand what they are, many production workflows will feel confusing.

## What is an API key?

An API key is usually a secret string assigned to a client or application.

It helps the server answer:

* which client is calling me?

API keys are common in:

* internal APIs
* developer platforms
* early-stage products

## Where API keys are sent

They are often sent in:

* a custom header such as `x-api-key`
* the `Authorization` header

Headers are preferred over query parameters for sensitive credentials.

## What is a token?

A token is a value that represents authenticated access.

It may represent:

* a logged-in user
* an approved client
* a temporary access grant

Tokens are often short-lived.
That makes them safer than long-term secrets in many cases.

## Bearer token idea

Bearer means:

whoever carries the token can use it

That is why bearer tokens must be:

* stored carefully
* sent over HTTPS
* rotated or expired when possible

## JWT intuition

A JWT is one common token format.

At a basic level, it often includes:

* identity information
* token expiry
* a signature

The signature helps the server detect tampering.

## Safe handling habits

Do not:

* hardcode secrets in source code
* commit keys to GitHub
* print tokens freely in logs

Do:

* store secrets in environment variables
* rotate compromised keys
* keep token lifetime limited when possible

## Why this matters in GenAI

In GenAI projects, you may need:

* a user token for your app
* a provider API key for OpenAI or another model service
* internal service keys for vector stores or storage systems

These should not be mixed casually.

## Key takeaway

API keys and tokens are both credentials, but they are used in different ways and should be handled carefully.
