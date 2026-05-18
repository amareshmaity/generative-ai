# Authentication in FastAPI

## Where authentication fits

In FastAPI, authentication is often handled before the main route logic runs.

That means:

* read the credential
* validate it
* allow or reject the request

FastAPI dependencies are very useful for this.

## A simple mental model

Think of authentication as a gate before the route body.

If the user is valid, the request continues.
If not, the route stops and returns an error.

## Common FastAPI pattern

You may define a helper that checks a header or token.

Then routes can reuse that helper.

Example:

```python
from fastapi import Depends, Header, HTTPException

def verify_api_key(x_api_key: str = Header(default="")):
    if x_api_key != "expected-key":
        raise HTTPException(status_code=401, detail="Invalid API key")
    return {"client": "trusted"}

@app.get("/protected")
def protected_route(client = Depends(verify_api_key)):
    return {"status": "ok", "client": client}
```

## Why dependencies help

They keep authentication logic:

* reusable
* separated from business logic
* easier to maintain

## Common pieces you will see

In real FastAPI projects, auth may involve:

* `Header`
* `Cookie`
* `Depends`
* `HTTPException`
* security helpers from FastAPI

## Important beginner habit

Do not hardcode real secrets in route files.

Prefer:

* environment variables
* config settings
* secret managers in production systems

## Authentication and current user idea

Many backends do more than just check a token.

They also load the current user information such as:

* user id
* email
* role

Then the route can use that information safely.

## Why this matters in GenAI backends

A protected GenAI endpoint may need to check:

* whether the user can access a document
* whether the user belongs to a paid plan
* whether the request should use a limited model tier

Authentication is often the first step before those checks.

## Key takeaway

FastAPI usually handles authentication through reusable validation logic that runs before protected route code.
