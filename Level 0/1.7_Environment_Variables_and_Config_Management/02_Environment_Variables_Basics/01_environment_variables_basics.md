# Environment Variables Basics

## What is an environment variable?

An environment variable is a name-value setting provided outside your code.

Examples:

* `APP_NAME=GenAI Notes App`
* `DEBUG=true`
* `OPENAI_API_KEY=...`

Your application can read these values while it runs.

## Why environment variables are useful

They let you change behavior without editing source code.

For example:

* one machine can use one database URL
* another machine can use a different one
* production can disable debug mode

## Reading environment variables in Python

Basic example:

```python
import os

api_key = os.getenv("OPENAI_API_KEY")
debug_mode = os.getenv("DEBUG", "false")
```

`os.getenv()` returns the value if it exists.
It can also return a default value.

## What is a `.env` file?

A `.env` file is a convenient way to store environment-style values during development.

Example:

```text
APP_NAME=GenAI Notes App
DEBUG=true
OPENAI_API_KEY=demo-key
```

This is very common in local projects.

## Important caution

A `.env` file may contain secrets.

That means it should usually:

* stay out of public Git commits
* be included in `.gitignore`

## Required vs optional values

Some environment variables are critical.

Examples:

* database URL
* secret key
* provider API key

If these are missing, the app may need to fail early instead of running incorrectly.

## Why this matters in GenAI

GenAI apps often depend on:

* provider API keys
* model selection
* chunk size settings
* vector store connection values

Environment variables are a common way to supply these values safely outside the code.

## Key takeaway

Environment variables let you move important settings out of source code and into the runtime environment.
