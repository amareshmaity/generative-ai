# Config Management Basics

## Config is more than just secrets

Many people first meet configuration through API keys.

But configuration also includes values such as:

* app name
* debug mode
* host and port
* database URL
* provider model name
* timeout values

## Good separation

Application logic should not be mixed with configuration everywhere.

A cleaner pattern is:

* routes handle requests
* services handle business logic
* config files or settings objects hold runtime values

## Simple structure example

```text
app/
  main.py
  routers/
  services/
  core/
    config.py
```

## Why central config helps

Centralized config makes it easier to:

* update values
* validate required settings
* reuse settings across the app
* avoid repeated `os.getenv()` calls everywhere

## Simple config object idea

Instead of reading environment variables inside many different files, you can create one settings object.

Example idea:

```python
import os

class Settings:
    app_name = os.getenv("APP_NAME", "My App")
    debug = os.getenv("DEBUG", "false")
    openai_api_key = os.getenv("OPENAI_API_KEY")

settings = Settings()
```

Then other files can import `settings`.

## Why validation matters

Some config values must exist.

If a required setting is missing, it is often better to fail at startup than to fail later in a confusing way.

## Why this matters in production

As your app grows, config may include:

* environment-specific values
* service URLs
* security settings
* performance tuning values

If these are unmanaged, the app becomes harder to debug and deploy.

## Key takeaway

Config management is about organizing runtime settings so the app stays clean, predictable, and maintainable.
