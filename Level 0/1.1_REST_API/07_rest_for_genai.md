# 07. REST API in GenAI Systems

## Why this file exists

You are learning REST for a GenAI path, so it is important to connect REST concepts to GenAI applications directly.

REST is not separate from GenAI engineering.
It is one of the main ways GenAI systems are exposed and consumed.

## Where REST appears in GenAI

Common GenAI use cases that expose REST APIs:

* chat systems
* summarization services
* document question-answering
* embedding generation
* evaluation jobs
* prompt management systems
* agent workflow triggers

## Example resources in GenAI

Possible resources:

* `/documents`
* `/conversations`
* `/messages`
* `/summaries`
* `/embeddings`
* `/evaluations`

Notice these are nouns, not random action names.

## Example design

For a document assistant app:

* `POST /documents`
* `GET /documents`
* `GET /documents/15`
* `DELETE /documents/15`
* `POST /conversations`
* `POST /messages`

## Why many GenAI APIs use POST

This is important.

Many GenAI operations involve sending text input for processing.

Examples:

* ask a question
* summarize text
* classify text
* generate embeddings

These often use `POST` because the client sends input in the request body.

## REST and model calls

Even if your backend later calls:

* OpenAI
* Azure OpenAI
* Hugging Face
* a vector database

your own application may still expose a clean REST API to clients.

So a GenAI engineer often works at two levels:

* consuming external APIs
* building internal or public APIs

## Why REST knowledge helps you in GenAI jobs

Because companies need engineers who can:

* receive user requests
* validate inputs
* connect to LLMs
* structure outputs
* return reliable responses

That full flow usually depends on API design.

## Example thinking

A user asks:

"Summarize the uploaded report."

Possible flow:

1. client sends a REST request
2. backend receives text or document id
3. backend retrieves context
4. backend calls the model
5. backend returns the answer in JSON

Without REST knowledge, you may understand the AI part but still struggle to build the product.

## What to remember

REST is one of the bridges between AI models and real users.

That is why backend and API skills are highly valuable in GenAI roles.

