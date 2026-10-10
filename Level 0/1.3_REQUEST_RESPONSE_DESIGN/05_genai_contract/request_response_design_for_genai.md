# 05. Request and Response Design for GenAI

## Why this topic matters in GenAI

GenAI systems often receive:

* prompts
* chat messages
* document ids
* uploaded file metadata
* generation settings

That means request and response design becomes very important.

If the contract is unclear, the AI system may still work, but the product experience becomes fragile.

## Common request fields in GenAI APIs

Examples:

* `question`
* `messages`
* `document_id`
* `temperature`
* `max_tokens`
* `top_k`
* `conversation_id`

Example request:

```json
{
  "question": "Summarize the annual report",
  "document_id": 12,
  "temperature": 0.2,
  "max_tokens": 300
}
```

## Common response fields in GenAI APIs

Examples:

* `answer`
* `summary`
* `sources`
* `model`
* `usage`
* `conversation_id`

Example response:

```json
{
  "status": "success",
  "answer": "The annual report shows revenue growth and lower debt.",
  "document_id": 12,
  "model": "gpt-4.1-nano"
}
```

## Useful GenAI response ideas

Sometimes a GenAI response should include metadata such as:

* retrieved source ids
* token usage
* latency
* model name
* confidence or warning messages

Example:

```json
{
  "status": "success",
  "answer": "The report shows stable growth.",
  "sources": [
    {"document_id": 12, "chunk_id": 3}
  ],
  "model": "gpt-4.1-nano"
}
```

## Validate request inputs carefully

GenAI APIs should often validate:

* empty prompts
* invalid document ids
* unsupported model names
* unreasonable parameter values

Without validation, downstream model calls become harder to debug.

## Design for clarity, not only flexibility

Do not make every endpoint accept too many optional fields unless they are actually needed.

A beginner mistake is designing one huge payload for many unrelated behaviors.

Better:

* keep each endpoint focused
* define clear request models
* return structured output

## Key takeaway

Good request and response design turns an AI demo into a usable backend product.
