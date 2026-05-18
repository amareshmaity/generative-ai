# Working with JSON

## What is JSON?

JSON stands for JavaScript Object Notation.

It is a lightweight structured data format used heavily in APIs.

It is common because it is:

* easy to read
* easy to send over the network
* supported by many languages

## JSON looks like structured text

Example:

```json
{
  "question": "Summarize this document",
  "document_id": 12,
  "temperature": 0.2
}
```

## Why JSON matters in backend work

In APIs, JSON is often used for:

* request bodies
* response bodies
* configuration files
* metadata storage

## JSON in Python

Python works with JSON using dictionaries, lists, strings, numbers, and booleans.

Common idea:

* Python dictionary in memory
* JSON string when sending or storing

## Converting Python data to JSON text

```python
import json

payload = {
    "question": "What is RAG?",
    "document_id": 5
}

json_text = json.dumps(payload)
```

## Converting JSON text to Python data

```python
import json

json_text = '{"question": "What is RAG?", "document_id": 5}'
data = json.loads(json_text)
```

## Why structure matters

Good JSON should be:

* clear
* predictable
* easy for clients to parse

Badly structured JSON makes APIs harder to use.

## Why this matters in GenAI

GenAI APIs often send or receive JSON fields such as:

* `question`
* `messages`
* `document_id`
* `model`
* `sources`

This makes JSON one of the most important practical formats for AI application development.

## Key takeaway

JSON is a core format for backend communication, especially in APIs and AI systems.
