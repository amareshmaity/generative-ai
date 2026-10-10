# 02. Request Design Basics

## What is a request design?

Request design means deciding how the client should send data to the server.

A request may include:

* method
* URL
* headers
* path parameters
* query parameters
* body

Good request design makes each part do the right job.

## Use the right place for the right data

### Path parameters

Use path parameters when identifying a specific resource.

Example:

```http
GET /documents/12
```

Here `12` identifies one document.

### Query parameters

Use query parameters for optional controls such as:

* filtering
* sorting
* searching
* pagination

Example:

```http
GET /documents?topic=finance&page=2
```

### Request body

Use the body when sending structured input data.

Example:

```json
{
  "question": "Summarize the report",
  "document_id": 12,
  "temperature": 0.2
}
```

## Good request field naming

Good field names are usually:

* explicit
* readable
* consistent
* domain-focused

Good:

* `question`
* `document_id`
* `user_id`
* `max_tokens`

Avoid:

* `q`
* `x1`
* `data_value`
* `temp_value_for_model`

## Required vs optional fields

Decide carefully:

* what must always be sent
* what may use defaults

Example:

```json
{
  "question": "Explain the summary",
  "document_id": 12,
  "temperature": 0.2
}
```

Possible design:

* `question` required
* `document_id` required
* `temperature` optional with default

## Keep requests small and purposeful

Do not send unnecessary fields.

Bad:

```json
{
  "question": "Summarize the report",
  "document_id": 12,
  "unused_flag": true,
  "random_note": "test",
  "screen_color": "blue"
}
```

Only request what the server actually needs.

## Validation mindset

Good request design should make validation easy.

Ask:

* is the field name clear?
* is the type obvious?
* is the field required or optional?
* is the field placed in the right part of the request?

## Key takeaway

A clean request is clear, minimal, and easy to validate.
