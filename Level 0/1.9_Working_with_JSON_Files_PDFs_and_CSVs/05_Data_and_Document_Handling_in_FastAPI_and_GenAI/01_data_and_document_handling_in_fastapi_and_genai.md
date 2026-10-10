# Data and Document Handling in FastAPI and GenAI

## How these pieces connect

A real backend may use several formats together.

Example:

* frontend sends JSON request
* backend accepts a PDF upload
* backend stores metadata in JSON form
* backend loads CSV metadata or evaluation data

That is why this topic is practical, not separate theory.

## JSON in FastAPI

FastAPI commonly uses JSON for:

* request bodies
* response bodies
* structured API contracts

## File handling in FastAPI

FastAPI can also accept uploaded files.

This matters for applications such as:

* PDF question-answering
* resume analysis
* CSV upload dashboards

## Example pattern

```python
from fastapi import FastAPI, UploadFile

app = FastAPI()

@app.post("/upload")
async def upload_file(file: UploadFile):
    content = await file.read()
    return {"filename": file.filename, "size": len(content)}
```

## Why document handling matters in GenAI

A typical GenAI document flow may be:

1. upload PDF or CSV
2. extract or read content
3. clean and chunk the data
4. store embeddings or metadata
5. answer user questions through JSON APIs

## Practical caution

When handling uploaded documents, think about:

* file size
* file type validation
* encoding issues
* missing or corrupted content

## Good backend mindset

Treat documents as data pipelines, not just files.

Ask:

* where does the file come from?
* how is it validated?
* how is text extracted?
* where is metadata stored?

## Key takeaway

In FastAPI and GenAI backends, JSON, files, CSVs, and PDFs often work together inside one document-processing workflow.
