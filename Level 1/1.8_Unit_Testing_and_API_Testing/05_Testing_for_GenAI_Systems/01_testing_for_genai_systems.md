# Testing for GenAI Systems

## Why this feels different

Many GenAI systems involve model outputs that can vary.

That can make beginners think:

testing is impossible here

That is not true.

## What can still be tested well

Many GenAI components are deterministic enough for normal testing.

Examples:

* request validation
* prompt template construction
* document chunking
* retrieval filtering
* response schema parsing
* error handling

## What may need a different approach

Some parts may need more than normal unit tests.

Examples:

* answer quality
* hallucination rate
* retrieval usefulness

Those may also involve evaluation workflows, not just standard pass-fail tests.

## Mocking external providers

A good beginner testing habit is to avoid calling real model providers in routine tests.

Why:

* tests become slower
* tests may cost money
* outputs may vary
* network failures may create noise

Instead, many tests should use mocked or fake responses.

## Example mindset

If your backend builds a prompt and calls a provider:

* unit test the prompt-building function
* unit test the parsing logic
* mock the provider call in higher-level tests

## What API tests can still verify

Even for GenAI endpoints, API tests can check:

* status codes
* schema shape
* missing input errors
* missing document errors
* auth failures

## Why this matters in RAG systems

RAG backends have many testable pieces:

* query validation
* chunk selection logic
* top-k boundaries
* empty retrieval results
* provider error handling

## Key takeaway

Even if model output is probabilistic, much of a GenAI backend is still testable with normal engineering practices.
