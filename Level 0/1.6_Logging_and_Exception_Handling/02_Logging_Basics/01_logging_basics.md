# Logging Basics

## What is a log?

A log is a recorded message about what your application is doing.

Logs are useful for:

* debugging
* monitoring
* tracing failures
* understanding runtime behavior

## Why not just use print?

`print()` is fine for tiny experiments.

But logging is better for real applications because it gives you:

* log levels
* timestamps
* consistent formatting
* better control over output

## Common log levels

Typical levels are:

* `DEBUG`
* `INFO`
* `WARNING`
* `ERROR`
* `CRITICAL`

Simple intuition:

* `DEBUG` for detailed development information
* `INFO` for normal useful events
* `WARNING` for something unusual but not fatal
* `ERROR` for failures that affect an operation
* `CRITICAL` for severe failures

## Basic Python example

```python
import logging

logging.basicConfig(level=logging.INFO)

logging.info("Application started")
logging.warning("Using fallback configuration")
logging.error("Document processing failed")
```

## What makes a good log?

A useful log message is:

* short
* specific
* meaningful

Bad log:

```text
Error happened
```

Better log:

```text
Document retrieval failed for document_id=42
```

## What not to log carelessly

Avoid logging sensitive data such as:

* passwords
* API keys
* bearer tokens
* private document contents

## Why this matters in GenAI

GenAI backends may need logs for:

* model name
* request id
* latency
* retrieval step status
* provider failure type

But logs should still protect sensitive content.

## Key takeaway

Logging helps you understand application behavior, and good log messages make debugging much easier.
