# Unit Testing Basics

## What is a unit test?

A unit test checks a small piece of code in isolation.

Usually that means testing:

* one function
* one class method
* one small logic block

## Why unit tests are useful

They help you verify logic without running the whole application.

This makes them:

* fast
* focused
* easier to debug

## Simple example

```python
def add(a, b):
    return a + b
```

A simple test:

```python
def test_add():
    assert add(2, 3) == 5
```

## Common test structure

A basic unit test usually follows:

1. prepare input
2. call the function
3. check the result

## What is `pytest`?

`pytest` is one of the most popular Python testing tools.

It is widely used because tests can stay simple and readable.

Example:

```python
def multiply(a, b):
    return a * b

def test_multiply():
    assert multiply(4, 5) == 20
```

## What should unit tests check?

Good candidates include:

* normal expected behavior
* edge cases
* invalid input handling

## Example mindset

If you have a function that cleans prompt input, test:

* normal text
* empty string
* extra spaces
* invalid type if relevant

## Keep unit tests focused

Unit tests should usually avoid unnecessary dependence on:

* real databases
* real APIs
* real provider calls

Those are better handled differently.

## Key takeaway

Unit tests check small logic pieces quickly and help you catch bugs early.
