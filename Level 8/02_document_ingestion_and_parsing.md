# 02. Document Ingestion and Parsing

**Level 8: Retrieval-Augmented Generation (RAG) · Generative AI Engineering**

## 1. Learning Objectives

After completing this chapter, you should be able to:

- Inventory document sources, formats, ownership, and update frequency.
- Assign stable source identifiers and record content hashes and versions.
- Parse supported formats into a consistent document representation.
- Preserve headings, section boundaries, source locations, and extraction status.
- Handle duplicate documents, empty extraction results, malformed files, and partial failures explicitly.
- Treat source documents as untrusted input and use bounded, safe parsing.
- Produce an ingestion manifest that records successful and failed processing attempts.
- Trace each parsed record back to its original source and version.

<br/>

## 2. What Is Document Ingestion?

**Document ingestion** is the process of collecting source content, validating it, extracting its useful information, and preparing it for downstream processing in a RAG system.

**Parsing** is one stage of ingestion. It converts a source format—such as PDF, Markdown, HTML, or plain text—into a representation that an application can inspect and process.

For example, a company-policy PDF might be transformed into structured records containing:

- Extracted text
- Document title and section headings
- Source identifier and version
- Page or section location
- Content hash
- Extraction status and any warnings

The ingestion stage should not silently discard documents that fail. It should record what happened so the system can be debugged and the source can be reprocessed when necessary.

<br/>

### Where ingestion fits in RAG

```mermaid
flowchart LR
    A["Source files"] --> B["Inventory and validate"]
    B --> C["Parse and extract"]
    C --> D["Normalize document records"]
    D --> E["Chunking"]
    E --> F["Embedding"]
    F --> G["Indexing"]
```

This chapter focuses on the stages through parsing and normalization. Chunking, embedding, and indexing are covered in later chapters.

<br/>

## 3. Inventory the Knowledge Sources

Before writing a parser, create a source inventory. It defines what the application is allowed and expected to ingest.

A source inventory can record:

| Field | Purpose | Example |
|---|---|---|
| `source_id` | Stable identifier for a logical source | `employee_leave_policy` |
| `uri` or path | Where the source is obtained | `documents/leave_policy.pdf` |
| `format` | Expected content format | `pdf` |
| `owner` | Responsible team or person | `Human Resources` |
| `update_frequency` | Expected refresh schedule | `monthly` |
| `access_scope` | Who may use the source | `employees` |
| `version` | Source revision identifier | `v3` |
| `last_ingested_at` | Last ingestion time | ISO 8601 timestamp |
| `status` | Processing status | `success`, `warning`, or `failed` |

Do not treat the filename as a reliable identifier. Files can be renamed, and different files can have the same filename. Use an application-controlled identifier and store the actual path or URI separately.

<br/>

### Example source inventory

```python
sources = [
    {
        "source_id": "employee_leave_policy",
        "path": "documents/leave_policy.md",
        "format": "markdown",
        "owner": "Human Resources",
        "update_frequency": "monthly",
        "access_scope": "employees",
    },
    {
        "source_id": "it_security_guide",
        "path": "documents/security_guide.txt",
        "format": "text",
        "owner": "IT Security",
        "update_frequency": "quarterly",
        "access_scope": "employees",
    },
]
```

This is a small illustrative inventory. A production inventory should be stored in a controlled configuration file or database and validated before ingestion.

<br/>

### Why ownership and update frequency matter

Ownership tells the team who is responsible for source correctness and access decisions. Update frequency helps schedule refreshes and identify content that may be stale.

The schedule is a policy, not proof that a document has changed. Use content hashes or source version metadata to detect actual changes where possible.

<br/>

## 4. Stable Source IDs, Versions, and Content Hashes

A RAG system needs to distinguish three related concepts:

- **Source ID:** Identifies the logical document or source over time.
- **Version:** Identifies a particular revision of that source.
- **Content hash:** Helps detect whether the source bytes or normalized content have changed.

For example:

| Source ID | Version | Content hash | Meaning |
|---|---|---|---|
| `employee_leave_policy` | `v1` | `a1...` | Original policy content |
| `employee_leave_policy` | `v2` | `b7...` | Updated policy content |
| `it_security_guide` | `v1` | `c4...` | Separate logical source |

The hash values above are illustrative, not real SHA-256 values.

A stable source ID should normally survive ordinary edits to the same logical document. A version or content hash distinguishes revisions.

<br/>

### 4.1 Calculating a content hash

Python's `hashlib` module can calculate a SHA-256 hash:

```python
from hashlib import sha256
from pathlib import Path

def sha256_file(path: str) -> str:
    digest = sha256()

    with Path(path).open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(block)

    return digest.hexdigest()
```

Usage:

```python
content_hash = sha256_file("documents/leave_policy.md")
print(content_hash)
```

Reading in blocks avoids loading a very large file into memory all at once.

**Important:** A content hash is useful for change detection and integrity checks, but it is not an identity or authorization mechanism. Identical content can legitimately exist under different source IDs or access scopes.

<br/>

### 4.2 Versioning strategies

Versions can come from:

- A document-management system's revision ID
- A database record's version number
- A repository commit or release
- An application-managed version assigned when content changes

If the source does not provide a trustworthy version, record the content hash and ingestion timestamp. Avoid inventing a business version that implies approval or authority when none exists.

<br/>

## 5. Parse Sources into a Consistent Representation

Different file formats expose content differently. A RAG ingestion system should convert supported formats into a common document representation while preserving format-specific information that matters.

For example, a normalized record might look like this:

```python
{
    "source_id": "employee_leave_policy",
    "source_version": "v2",
    "content_hash": "example-hash",
    "text": "## Annual Leave\nEmployees receive 18 days...",
    "title": "Employee Leave Policy",
    "sections": ["Annual Leave"],
    "locators": [
        {"type": "heading", "value": "Annual Leave"}
    ],
    "status": "success",
    "warnings": []
}
```

The `content_hash` above is a placeholder. Real records should contain the actual calculated hash.

A consistent representation makes later stages easier because chunking and indexing can work with a common schema instead of needing separate logic for every file type.

<br/>

### 5.1 Format-specific considerations

| Format | Typical parsing considerations |
|---|---|
| Plain text (`.txt`) | Character encoding, line breaks, empty files |
| Markdown (`.md`) | Headings, lists, code blocks, tables |
| HTML (`.html`) | Main content extraction, navigation, scripts, hidden content |
| PDF (`.pdf`) | Page boundaries, reading order, tables, scanned pages |
| CSV (`.csv`) | Headers, delimiters, row structure, encoding |
| DOCX (`.docx`) | Paragraphs, headings, tables, document order |

Do not assume every file with a given extension is valid or safe. A file may be corrupted, mislabeled, encrypted, or intentionally crafted to consume excessive resources.

PDF-specific extraction and OCR are covered in Chapter 03.

<br/>

## 6. A Minimal Working Parser for Text and Markdown

The following example implements a deliberately small parser for `.txt` and `.md` files. It includes:

- Source inventory metadata
- SHA-256 hashing
- File-size limits
- UTF-8 decoding
- Empty-content checks
- A normalized document record
- An explicit success/failure manifest

It does **not** implement PDF, HTML, DOCX, or CSV parsing. Those formats require format-specific parsers and additional validation.

```python
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any


MAX_FILE_BYTES = 2 * 1024 * 1024  # 2 MiB


@dataclass
class IngestionResult:
    source_id: str
    path: str
    status: str
    content_hash: str | None = None
    character_count: int = 0
    document: dict[str, Any] | None = None
    error: str | None = None
    warnings: list[str] | None = None
    ingested_at: str | None = None


def parse_text_source(source: dict[str, str]) -> IngestionResult:
    path = Path(source["path"])
    timestamp = datetime.now(timezone.utc).isoformat()

    try:
        # Prevent paths outside the configured corpus directory.
        # This example expects source paths to be relative to "corpus".
        root = Path("corpus").resolve()
        resolved_path = (root / path).resolve()

        if not resolved_path.is_relative_to(root):
            raise ValueError("Source path is outside the corpus directory")

        if resolved_path.suffix.lower() not in {".txt", ".md"}:
            raise ValueError("Unsupported file format")

        if not resolved_path.is_file():
            raise FileNotFoundError("Source file does not exist")

        size = resolved_path.stat().st_size
        if size > MAX_FILE_BYTES:
            raise ValueError("Source exceeds the configured size limit")

        raw_bytes = resolved_path.read_bytes()
        content_hash = sha256(raw_bytes).hexdigest()

        # Strict decoding: malformed UTF-8 becomes a recorded failure.
        text = raw_bytes.decode("utf-8").strip()

        if not text:
            raise ValueError("Extracted content is empty")

        document = {
            "source_id": source["source_id"],
            "source_version": source.get("version", "unversioned"),
            "content_hash": content_hash,
            "format": resolved_path.suffix.lower().lstrip("."),
            "title": source.get("title", resolved_path.stem),
            "text": text,
            "locators": [],
            "status": "success",
        }

        return IngestionResult(
            source_id=source["source_id"],
            path=str(resolved_path),
            status="success",
            content_hash=content_hash,
            character_count=len(text),
            document=document,
            warnings=[],
            ingested_at=timestamp,
        )

    except (OSError, UnicodeError, ValueError, KeyError) as exc:
        return IngestionResult(
            source_id=source.get("source_id", "unknown"),
            path=str(path),
            status="failed",
            error=f"{type(exc).__name__}: {exc}",
            warnings=[],
            ingested_at=timestamp,
        )
```

<br/>

### 6.1 Run the parser against several sources

Create this folder structure:

```text
project/
├── corpus/
│   ├── leave_policy.md
│   ├── security_guide.txt
│   └── empty_document.txt
└── ingest.py
```

Example `corpus/leave_policy.md`:

```text
# Employee Leave Policy

## Annual Leave

Employees receive 18 days of annual leave per calendar year.
```

Example `corpus/security_guide.txt`:

```text
Security Guide

Employees must protect their account credentials.
```

Leave `empty_document.txt` empty to test failure handling.

Then define the inventory and run the parser:

```python
import json
from dataclasses import asdict
from pathlib import Path

sources = [
    {
        "source_id": "employee_leave_policy",
        "path": "leave_policy.md",
        "version": "v1",
        "title": "Employee Leave Policy",
    },
    {
        "source_id": "it_security_guide",
        "path": "security_guide.txt",
        "version": "v1",
        "title": "Security Guide",
    },
    {
        "source_id": "empty_test_document",
        "path": "empty_document.txt",
        "version": "v1",
        "title": "Empty Test Document",
    },
    {
        "source_id": "missing_test_document",
        "path": "missing.txt",
        "version": "v1",
        "title": "Missing Test Document",
    },
]

results = [parse_text_source(source) for source in sources]

manifest = {
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "total": len(results),
    "succeeded": sum(r.status == "success" for r in results),
    "failed": sum(r.status == "failed" for r in results),
    "results": [asdict(result) for result in results],
}

Path("ingestion_manifest.json").write_text(
    json.dumps(manifest, indent=2, ensure_ascii=False),
    encoding="utf-8",
)

print(f"Processed: {manifest['total']}")
print(f"Succeeded: {manifest['succeeded']}")
print(f"Failed: {manifest['failed']}")
print("Manifest written to ingestion_manifest.json")
```

With the sample files above, two sources should succeed and two should fail: one is empty and one is missing. If your results differ, inspect the paths and file contents.

The manifest contains a record for every attempted source, rather than stopping at the first failure.

<br/>

### 6.2 Example manifest record

A successful record will resemble:

```json
{
  "source_id": "employee_leave_policy",
  "path": "/project/corpus/leave_policy.md",
  "status": "success",
  "content_hash": "<actual SHA-256 hash>",
  "character_count": 100,
  "document": {
    "source_id": "employee_leave_policy",
    "source_version": "v1",
    "content_hash": "<actual SHA-256 hash>",
    "format": "md",
    "title": "Employee Leave Policy",
    "text": "# Employee Leave Policy\n\n## Annual Leave\n\nEmployees receive 18 days of annual leave per calendar year.",
    "locators": [],
    "status": "success"
  },
  "error": null,
  "warnings": [],
  "ingested_at": "<UTC timestamp>"
}
```

The character count and timestamps depend on the exact input files and execution environment. The hash shown here is a placeholder, not a computed value.

A failed record should include the source ID, failure status, error category/message, and timestamp. Avoid placing secrets or sensitive document content in error logs.

<br/>

## 7. Preserve Provenance and Document Structure

**Provenance** is the information needed to establish where extracted content came from and which source revision it represents.

At minimum, preserve:

- Stable source ID
- Source version or content hash
- Original path or URI in an access-controlled record
- Title and section headings where available
- Page, paragraph, row, or other source locator where applicable
- Extraction status and warnings

This information is essential when later RAG stages create chunks, return citations, update a document, or delete stale content.

<br/>

### Example: heading-aware representation

Instead of storing only unstructured text:

```text
Employees receive 18 days of annual leave per calendar year.
```

Preserve the section context:

```python
record = {
    "source_id": "employee_leave_policy",
    "source_version": "v1",
    "section_path": ["Employee Leave Policy", "Annual Leave"],
    "text": "Employees receive 18 days of annual leave per calendar year.",
    "locator": {
        "type": "heading",
        "value": "Annual Leave",
    },
}
```

A later chunking stage can carry these fields into chunk metadata. For PDFs, the locator may include a physical page index and, if available, a printed page label. For CSV files, it might include a sheet or row identifier.

**Do not fabricate locators.** If a parser cannot reliably determine a page or section, record the limitation rather than inventing a precise source location.

<br/>

## 8. Duplicates, Empty Output, and Partial Failures

A reliable ingestion pipeline treats failures as explicit outcomes.

### 8.1 Duplicate documents

Two files may have different names but identical bytes. Conversely, a single logical document may have multiple legitimate versions.

Use hashes to identify byte-identical content, but do not automatically merge records with different owners or permissions. Identical content does not mean identical access rights.

A duplicate policy should decide whether to:

- Skip duplicate processing while preserving source references
- Link multiple source IDs to one stored content object
- Reprocess the source if its metadata or access scope changes

<br/>

### 8.2 Empty extraction

A parser may return no useful text because a file is empty, contains only images, or is damaged.

Record an explicit status such as `failed` or `needs_ocr`, depending on the workflow. Do not silently index an empty string as if ingestion succeeded.

<br/>

### 8.3 Malformed or unsupported files

Handle unsupported extensions, invalid encodings, corrupted files, and parser exceptions explicitly. The application should continue processing independent sources where appropriate, while recording each failure.

<br/>

### 8.4 Partial failures

A batch can contain both successful and failed documents. A useful manifest records each source's status and provides summary counts.

Do not mark the entire batch as fully successful merely because the processing job completed.

<br/>

## 9. Safe and Bounded Parsing

Documents are **untrusted input**, even when they come from an internal repository. Files can be malformed, unexpectedly large, or deliberately constructed to exploit a parser.

Practical safeguards include:

- Allowlisting supported formats rather than accepting arbitrary file types.
- Limiting file size, page count, processing time, and extracted-text size.
- Restricting file access to configured directories or approved storage locations.
- Avoiding execution of macros, scripts, or embedded active content.
- Running risky parsers in an appropriately isolated environment.
- Handling parser exceptions without exposing internal paths, secrets, or sensitive text to users.
- Treating extracted text as untrusted content in downstream prompts.
- Recording warnings and failures for review.

The code example uses a size limit, extension allowlist, strict UTF-8 decoding, and a corpus-directory check. It is a teaching example, not a complete security boundary. Production systems should account for symlinks, concurrent file changes, archive expansion, parser-specific vulnerabilities, and resource limits enforced outside the parser process.

<br/>

## 10. Practice: Build a Source Inventory and Ingestion Manifest

### Task

Create a small corpus with at least four entries:

1. A valid Markdown document.
2. A valid plain-text document.
3. An empty file.
4. A missing or malformed file.

Then:

1. Assign each source a stable source ID.
2. Record its format, owner, update frequency, and access scope.
3. Calculate a content hash for every file that can be read.
4. Parse supported files into the common document representation.
5. Record success or failure for every source.
6. Save the manifest to `ingestion_manifest.json`.
7. Confirm that each successful record can be traced back to its source and version.

<br/>

### Expected behavior

| Test case | Expected result |
|---|---|
| Valid Markdown | `success`, with text and metadata |
| Valid text | `success`, with text and metadata |
| Empty file | `failed` or a documented non-success status |
| Missing file | `failed`, with a recorded error |
| Unsupported format | `failed`, with an explicit reason |

<br/>

### Extension exercise

Add a duplicate document with identical bytes but a different filename. Compare its SHA-256 hash with the original, and design a policy that preserves both source identities and their permissions.

<br/>

## 11. Chapter Checkpoint

**Question:** How can you trace each parsed record back to its source and version?

**Answer:** Assign a stable source ID to the logical document and preserve the source version or content hash in every parsed record. Retain the original path or URI in a controlled metadata store, along with available section or page locators and ingestion status. When records are later chunked and indexed, propagate the source identity, version, and locators into chunk metadata. This allows retrieved evidence to be traced to the correct source revision.

<br/>

## 12. Key Takeaways

- Ingestion prepares source content for downstream RAG processing; parsing is one stage of that workflow.
- A source inventory should capture identity, format, ownership, update frequency, and access scope.
- Stable source IDs, versions, and content hashes serve different purposes.
- A normalized document representation makes downstream chunking and indexing easier.
- Provenance and source locators should be preserved throughout the pipeline.
- Empty, malformed, unsupported, and partially processed files require explicit outcomes.
- Hashes help detect content changes but do not establish authorization.
- Treat files and extracted content as untrusted input, and apply resource limits and safe parsing practices.
- An ingestion manifest makes batch results reproducible and failures diagnosable.

<br/>

## 13. References

- [Python `hashlib` documentation](https://docs.python.org/3/library/hashlib.html)
- [Python `pathlib` documentation](https://docs.python.org/3/library/pathlib.html)
- [Python `json` documentation](https://docs.python.org/3/library/json.html)
- [OWASP File Upload Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html)
- [OWASP Top 10 for Large Language Model Applications](https://genai.owasp.org/)


<br/>


**Next chapter:** `03_pdf_extraction_ocr_and_document_structure.md` — Digital PDFs, scanned pages, OCR, tables, reading order, page locators, and extraction-quality checks.
