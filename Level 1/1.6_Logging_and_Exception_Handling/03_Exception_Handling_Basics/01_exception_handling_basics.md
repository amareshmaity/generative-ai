# Exception Handling Basics

## What is an exception?

An exception is an error event that interrupts normal program flow.

Examples:

* converting invalid text to an integer
* opening a file that does not exist
* accessing a missing key

## Why exception handling exists

Without exception handling, a failure may crash the current flow immediately.

With exception handling, your code can:

* catch the failure
* respond clearly
* continue safely when appropriate

## Basic structure

```python
try:
    value = int(user_input)
except ValueError:
    print("Invalid number")
```

## Main parts

* `try` contains code that may fail
* `except` handles a specific error
* `finally` runs whether the error happens or not

Example:

```python
try:
    file = open("notes.txt")
except FileNotFoundError:
    print("File not found")
finally:
    print("Finished file operation")
```

## Catch specific exceptions

It is usually better to catch a specific exception rather than a very broad one.

Good:

```python
except ValueError:
```

Risky:

```python
except Exception:
```

Broad exception handling can hide important bugs if used carelessly.

## Do not swallow errors silently

This is a bad pattern:

```python
try:
    risky_operation()
except Exception:
    pass
```

This makes debugging much harder.

## Raise when needed

Sometimes your code should not hide the failure.
It should raise an error so the caller can deal with it.

## Why this matters in APIs

APIs often need to turn internal failures into user-facing responses.

For example:

* invalid input may become `400`
* missing resource may become `404`
* provider failure may become `500` or `503`

## Key takeaway

Exception handling is about controlling failure carefully, not pretending failure does not exist.
