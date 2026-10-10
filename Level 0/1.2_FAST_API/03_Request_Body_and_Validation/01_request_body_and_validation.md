# Request Body and Validation

## Why this matters

FastAPI becomes powerful when you stop taking raw input manually and start defining clear data models.

This gives:

* validation
* predictable input
* better docs
* fewer runtime bugs

## Request body with Pydantic

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class ChatRequest(BaseModel):
    question: str
    document_id: int
    temperature: float = 0.2


@app.post("/chat")
def chat(payload: ChatRequest):
    return {
        "question": payload.question,
        "document_id": payload.document_id,
        "temperature": payload.temperature
    }
```

## What Pydantic does

Pydantic:

* validates types
* parses input data
* gives defaults
* improves generated docs

## Validation examples

FastAPI can reject:

* missing fields
* wrong data types
* invalid values when rules are defined

Example:

* `document_id` should be `int`
* `question` should be `str`

## Why this is useful in GenAI

GenAI endpoints often accept:

* prompts
* document ids
* temperature
* max tokens
* top_k

If these are not validated, your backend becomes fragile quickly.

## Good modeling mindset

Ask:

* what fields are required?
* what types are allowed?
* what defaults are reasonable?
* what invalid inputs should be blocked early?

## Key takeaway

Pydantic models are one of the biggest reasons FastAPI feels clean, safe, and production-friendly.

