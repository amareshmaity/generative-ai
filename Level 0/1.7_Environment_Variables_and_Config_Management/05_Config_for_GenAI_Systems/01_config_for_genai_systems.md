# Config for GenAI Systems

## GenAI systems usually have many settings

A GenAI backend may need configuration for:

* provider API keys
* model names
* embedding model names
* vector store URLs
* chunk size and overlap
* timeout settings
* rate limits
* feature flags

That is why config management becomes very important very quickly.

## Sensitive vs non-sensitive config

Some values are secrets.

Examples:

* provider API keys
* database passwords
* service tokens

Some values are not secrets, but still need good management.

Examples:

* model name
* temperature default
* chunk size
* retrieval top-k

Both categories belong in organized configuration, but secrets need extra care.

## Common beginner mistake

A very common mistake is writing provider credentials directly inside notebooks, route files, or frontend code.

This is risky because:

* secrets can leak
* costs can be abused
* changing providers becomes harder

## Better pattern

Use the backend as the control layer:

* backend reads provider secrets from environment or secure config
* routes call services
* services read shared settings

## Config examples in GenAI apps

Real settings might include:

* `OPENAI_API_KEY`
* `DEFAULT_MODEL`
* `EMBEDDING_MODEL`
* `VECTOR_DB_URL`
* `MAX_CHUNK_SIZE`
* `TOP_K`

## Why config helps experimentation

GenAI development often involves changing settings to compare behavior.

If these values are well organized, it becomes easier to:

* test different models
* adjust retrieval behavior
* tune latency and cost trade-offs

without rewriting large parts of the code.

## Logging and config

It is often useful to log non-sensitive settings such as:

* selected model
* chunk size
* top-k

But sensitive secrets should never be logged directly.

## Key takeaway

GenAI systems depend on many settings, so good config management supports security, flexibility, and experimentation.
