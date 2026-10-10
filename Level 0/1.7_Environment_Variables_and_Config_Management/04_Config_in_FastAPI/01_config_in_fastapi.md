# Config in FastAPI

## Where config fits in a FastAPI project

FastAPI apps often keep settings in a shared place such as:

* `core/config.py`
* `settings.py`

This keeps route files cleaner.

## Common pattern

A route should not hardcode values like:

* API provider key
* model name
* debug flag

Instead, it should use values loaded from shared settings.

## Example structure

```text
app/
  main.py
  core/
    config.py
  routers/
    chat.py
  services/
    llm_service.py
```

## Example settings idea

```python
import os

class Settings:
    app_name = os.getenv("APP_NAME", "GenAI Backend")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    default_model = os.getenv("DEFAULT_MODEL", "gpt-4o-mini")

settings = Settings()
```

Then a service can use:

```python
from app.core.config import settings
```

## Why this is better

This approach helps:

* reduce duplication
* keep secrets out of route code
* make configuration easier to change

## Config and dependencies

Sometimes settings are also used inside FastAPI dependencies.

Examples:

* checking debug mode
* using a configured API key
* choosing a service endpoint

## Beginner habit to build now

Even in small FastAPI projects, start separating:

* routes
* services
* schemas
* config

That habit makes later growth much easier.

## Key takeaway

In FastAPI, configuration should usually live in a shared settings layer instead of being spread through route files.
