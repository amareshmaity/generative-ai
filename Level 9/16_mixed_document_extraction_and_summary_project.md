# Chapter 16: Mixed-Document Extraction and Summary Project

## Learning Objectives

By the end of this project, you should be able to:

- Process a document that contains both text and visual information.
- Compare text-extraction-only input with page-image input and combined input.
- Produce schema-validated fields and an evidence-supported summary.
- Preserve page locators and verify numerical and table-related claims independently.
- Document omissions, unsupported claims, and differences between approaches.
- Explain which facts required visual inspection and which were available from text alone.

<br/>

## 1. Project Overview

Many real documents combine selectable text with information encoded visually. Examples include:

- Reports containing paragraphs, charts, and tables.
- Product manuals with instructions and labeled diagrams.
- Invoices with text, line items, stamps, and handwritten annotations.
- Research papers containing prose, equations, plots, and figures.
- Scanned forms where the page image is the primary source.

A text extraction pipeline may capture the paragraphs but lose layout, chart relationships, visual labels, or content embedded in images. A vision-capable model may inspect the page image, but it can also misread small text or numerical values. A combined pipeline can use both sources and preserve links to the original pages.

**Project goal:** extract a defined set of fields and produce a concise summary, with each important claim linked to inspectable source evidence.

<br/>

### Deliverables

1. A sample mixed-content document.
2. A text-extraction pipeline.
3. A page-image or combined-input pipeline.
4. A schema for extracted fields.
5. A source-evidence record with page locators.
6. A comparison report covering quality, omissions, hallucinations, latency, and usage where available.

<br/>

## 2. Define the Task Before Processing

Choose a document type and a limited set of fields. Avoid trying to extract every possible detail in the first iteration.

Example task for a technical report:

- Document title
- Reporting period
- Main objective
- Key findings
- Important numerical values
- Table or chart conclusions
- Diagram components and relationships
- Limitations stated by the source
- Summary supported by source evidence

Define which fields are required, which may be null, and what counts as sufficient evidence.

<br/>

### Example project contract

```text
Input:
  One PDF containing text and visual elements.

Outputs:
  1. Structured fields validated against a schema.
  2. A concise evidence-supported summary.
  3. Page-level evidence references for extracted claims.
  4. A comparison of text-only, page-image, and combined approaches.

Rules:
  - Do not invent missing values.
  - Mark unreadable or absent information explicitly.
  - Preserve the page number for each source claim.
  - Verify important numerical and table claims independently.
```

<br/>

## 3. Inspect the Document and Preserve Page Identity

Before extraction, record basic document metadata:

- A stable document ID.
- File type and file size.
- Page count.
- Source version or collection date where applicable.
- Whether each page appears to contain selectable text, scanned content, tables, charts, or diagrams.

Do not assume that a PDF is text-only because some pages have selectable text. Different pages may require different processing methods.

<br/>

### Page-level representation

Use a record that links extracted text and visual evidence to the same page:

```json
{
  "document_id": "report-001",
  "page_number": 4,
  "text_artifact_id": "report-001-p004-text",
  "page_image_id": "report-001-p004-image",
  "elements": [
    {
      "element_id": "chart-02",
      "element_type": "chart",
      "page_number": 4,
      "description": "Quarterly trend chart",
      "bounding_box": [72, 160, 520, 460]
    }
  ]
}
```

This is an illustrative data structure. Use consistent page numbering and coordinate conventions, and document whether page numbers are one-based or zero-based.

<br/>

## 4. Build the Text-Extraction Baseline

Extract selectable text first. For a small PDF prototype, PyMuPDF can retrieve text by page.

### Install dependencies

```bash
pip install pymupdf pydantic
```

<br/>

### Extract page text

```python
from pathlib import Path
import fitz  # PyMuPDF

def extract_pdf_text(pdf_path: str) -> list[dict]:
    path = Path(pdf_path)
    if not path.is_file():
        raise FileNotFoundError(f"PDF not found: {path}")

    pages = []
    with fitz.open(path) as document:
        for page_index, page in enumerate(document):
            pages.append({
                "page_number": page_index + 1,
                "text": page.get_text("text").strip(),
            })

    return pages
```

Inspect the output instead of assuming extraction succeeded. A page may return little or no text even though the page visibly contains important content.

<br/>

### Text-only baseline

Construct a text-only input from the extracted pages, preserving page boundaries:

```python
def build_text_only_input(pages: list[dict]) -> str:
    sections = []
    for page in pages:
        sections.append(
            f"[Source page {page['page_number']}]\n{page['text']}"
        )
    return "\n\n".join(sections)
```

Page labels help preserve provenance, but they do not guarantee accurate citations. The application must retain the underlying page records and validate every reference.

<br/>

### Known limitations of text extraction

- Scanned pages may have no selectable text.
- Reading order may be wrong in multi-column layouts.
- Tables may be flattened into ambiguous text.
- Chart axes, legends, arrows, and spatial relationships may be lost.
- Text embedded in diagrams may not appear in the extracted output.

Treat extracted text as one representation of the document, not as a complete substitute for it.

<br/>

## 5. Create Page Images for Visual Inspection

A page-image path can help recover layout and visual information that text extraction misses.

PyMuPDF can render PDF pages as images:

```python
from pathlib import Path
import fitz

def render_pdf_pages(
    pdf_path: str,
    output_dir: str,
    dpi: int = 150,
) -> list[dict]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    scale = dpi / 72
    matrix = fitz.Matrix(scale, scale)
    rendered = []

    with fitz.open(pdf_path) as document:
        for page_index, page in enumerate(document):
            pixmap = page.get_pixmap(matrix=matrix, alpha=False)
            image_path = output_path / f"page_{page_index + 1:03}.png"
            pixmap.save(image_path)

            rendered.append({
                "page_number": page_index + 1,
                "image_path": str(image_path),
                "width": pixmap.width,
                "height": pixmap.height,
            })

    return rendered
```

The chosen DPI is a preprocessing setting, not a universal recommendation. Larger renders may preserve more detail but also increase file size, transfer time, and model processing cost. Test the resolution needed for the document type.

For a first experiment, render only a small set of pages that contain both text and visual elements. Keep page images linked to the source PDF and page numbers.

<br/>

## 6. Compare Three Input Strategies

Use the same document, task, field schema, and evaluation rubric for all strategies.

### Strategy A: Text extraction only

Send the extracted text and page labels to the model.

**Likely strengths**
- Efficient for paragraphs and clearly extracted textual facts.
- Easier to inspect as plain text.
- May reduce image-processing requirements.

**Likely weaknesses**
- May miss chart structure, diagram relationships, or image-only labels.
- Can misinterpret flattened tables.
- Cannot inspect visual evidence that was never extracted.

<br/>

### Strategy B: Page-image input

Send relevant rendered pages to a model that documents support for image input.

**Likely strengths**
- Preserves page layout and visual relationships.
- Can expose labels, diagrams, charts, and scanned text that text extraction misses.

**Likely weaknesses**
- Small text may remain unreadable.
- Numerical values and chart relationships can still be misread.
- Image processing may increase latency, usage, or cost.

<br/>

### Strategy C: Combined text and page-image input

Supply extracted text with its page identifiers and the relevant page images.

**Likely strengths**
- Provides searchable text plus visual context.
- Supports cross-checking extracted text against page appearance.
- Can improve traceability when text and image references are aligned.

**Likely weaknesses**
- More input does not automatically mean better output.
- Text and images may be duplicated or contradictory.
- Context limits and cost can increase.
- Incorrect page associations can create false evidence.

<br/>

### Comparison table

| Dimension | Text only | Page image | Combined |
|---|---|---|---|
| Paragraph extraction | Often effective when selectable text is clean | Model must read text from the image | Text extraction plus visual verification |
| Scanned text | Limited without OCR | Can inspect the rendered page, subject to legibility | Image plus any OCR output |
| Tables | May lose row/column structure | Preserves layout but values may be misread | Allows comparison of text and visual structure |
| Charts and diagrams | Often incomplete | Direct visual evidence is available | Text labels and visual relationships can be combined |
| Page-level provenance | Must be retained by application | Must be associated with each image | Must align text and image page IDs |
| Operational cost | Often lower, but depends on model and text length | Depends on image processing and resolution | Can be highest due to combined inputs |
| Main risk | Missing visual information | Visual misinterpretation | Misalignment, duplication, or conflicting evidence |

Do not assume one strategy is universally best. Compare them on representative documents and questions.

<br/>

## 7. Define a Validated Output Schema

Use a schema to enforce output structure. Keep the schema separate from the evidence-verification process: schema-valid output can still contain incorrect facts.

The following example uses Pydantic v2. It allows uncertain or unavailable fields to be represented explicitly and associates claims with page-level evidence.

```python
from pydantic import BaseModel, Field
from typing import Literal

class EvidenceReference(BaseModel):
    page_number: int = Field(ge=1)
    element_id: str | None = None
    evidence_note: str = Field(
        description="Short description of the source region supporting the claim"
    )

class ExtractedFact(BaseModel):
    field_name: str
    value: str | float | int | None
    status: Literal[
        "supported",
        "partially_supported",
        "not_found",
        "unreadable",
    ]
    evidence: list[EvidenceReference] = Field(default_factory=list)

class DocumentResult(BaseModel):
    document_id: str
    title: str | None = None
    facts: list[ExtractedFact]
    summary: str
    summary_evidence: list[EvidenceReference] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
```

Example local validation:

```python
example = {
    "document_id": "report-001",
    "title": "Quarterly Operations Review",
    "facts": [
        {
            "field_name": "reporting_period",
            "value": "Q2 2026",
            "status": "supported",
            "evidence": [
                {
                    "page_number": 1,
                    "element_id": None,
                    "evidence_note": "Period appears in the report heading",
                }
            ],
        }
    ],
    "summary": "The report reviews quarterly operations.",
    "summary_evidence": [
        {
            "page_number": 1,
            "element_id": None,
            "evidence_note": "Title and introductory paragraph",
        }
    ],
    "limitations": [],
}

validated = DocumentResult.model_validate(example)
print(validated.model_dump_json(indent=2))
```

This example validates structure and types only. It does not establish that the claim is supported by the referenced page. Implement independent checks for page existence, evidence coverage, and numerical accuracy.

<br/>

## 8. Produce an Evidence-Supported Summary

A summary should be concise, faithful to the source, and traceable to supporting pages or visual elements.

### Suggested process

1. Identify the user’s requested output and required fields.
2. Retrieve relevant text and pages rather than sending an entire large document by default.
3. Ask the model to extract facts separately from its narrative summary.
4. Require page or element references for key claims.
5. Validate the structured response against the schema.
6. Verify each reference points to a real source location.
7. Inspect numerical, table, chart, and diagram claims independently.
8. Mark claims that are unsupported, ambiguous, or absent.
9. Generate the final summary only from the checked evidence.

<br/>

### Evidence record

For each claim, preserve:

- Claim or field identifier.
- Extracted value or summary sentence.
- Source document and version.
- Page number and, where available, element ID or bounding box.
- Evidence type: extracted text, table, chart, diagram, or page image.
- Verification result and reviewer notes.

An evidence note should identify where to inspect the claim; it should not replace the underlying source.

<br/>

## 9. Verify Numerical and Table Claims Independently

Numerical claims are easy to misread and can be consequential. Do not rely only on a model’s fluent explanation.

### Verification procedure

- Locate the relevant source page and table or chart.
- Check column headers, row labels, units, signs, and decimal separators.
- Confirm whether values are counts, percentages, currency, rates, or normalized quantities.
- Recalculate totals, differences, or percentages from source values when possible.
- Compare extracted values with the original visual representation.
- Record discrepancies and the method used to resolve them.
- If the source is ambiguous, preserve the ambiguity rather than silently choosing a value.

For charts, verify axis scale, legend, series identity, and time period. For tables, verify that each value is associated with the correct row and column. A correct number attached to the wrong label is still an incorrect extraction.

<br/>

## 10. Run a Controlled Comparison

Create a small evaluation set with manually checked answers. Include cases that require text, cases that require visual information, and cases where evidence is absent or ambiguous.

### Example evaluation record

| Case ID | Question or field | Required evidence | Text-only result | Image result | Combined result |
|---|---|---|---|---|---|
| DOC-01 | Report title | Page 1 heading | Fill in | Fill in | Fill in |
| DOC-02 | Table total | Table cells on page 3 | Fill in | Fill in | Fill in |
| DOC-03 | Direction of an arrow | Diagram on page 4 | Fill in | Fill in | Fill in |
| DOC-04 | Label inside a scanned figure | Figure on page 5 | Fill in | Fill in | Fill in |
| DOC-05 | Value not present in source | No supporting evidence | Fill in | Fill in | Fill in |

For each approach, assess:

- Field-level correctness.
- Evidence support and citation accuracy.
- Missing facts or omissions.
- Unsupported claims or hallucinations.
- Numerical and table accuracy.
- Appropriate uncertainty or abstention.
- Latency and usage, when available.
- Preprocessing effort and failure rate.

Use the same test cases and output schema across approaches. Otherwise, differences may come from changes in the task rather than the input strategy.

<br/>

### Results table

| Metric | Text only | Page image | Combined |
|---|---:|---:|---:|
| Required fields correct | Fill in | Fill in | Fill in |
| Claims with valid supporting evidence | Fill in | Fill in | Fill in |
| Unsupported claims | Fill in | Fill in | Fill in |
| Numerical/table errors | Fill in | Fill in | Fill in |
| Appropriate uncertainty cases | Fill in | Fill in | Fill in |
| Median latency | Fill in | Fill in | Fill in |
| Reported usage / estimated cost | Fill in | Fill in | Fill in |

Do not fabricate benchmark results. Fill the table with measured results from your own test set and clearly label estimates.

<br/>

## 11. Practice: Demonstrate Extraction and Summarization

### Choose a suitable document

Use a public or synthetic report, manual, invoice, or research-style document that you are authorized to process. It should contain:

- At least one text-heavy page.
- At least one table, chart, or diagram.
- At least one fact whose interpretation depends on visual layout.
- A page where an answer is absent or uncertain, if possible.

<br/>

### Demonstration steps

1. Record the document ID, page count, and relevant source pages.
2. Extract text while preserving page numbers.
3. Render the relevant pages as images.
4. Define a small output schema with nullable fields and evidence references.
5. Run text-only extraction.
6. Run page-image extraction on the same questions.
7. Run combined input, preserving page-to-image associations.
8. Validate every structured result.
9. Independently inspect numerical and table claims.
10. Compare omissions, unsupported claims, uncertainty behavior, latency, and usage.
11. Write a short evidence-supported summary and document the remaining weaknesses.

<br/>

### Practice report template

- **Document type and source:**
- **Document ID/version:**
- **Pages evaluated:**
- **Fields and schema:**
- **Text extraction method:**
- **Page rendering settings:**
- **Model and input configuration:**
- **Text-only findings:**
- **Page-image findings:**
- **Combined-input findings:**
- **Claims checked independently:**
- **Omissions and hallucinations:**
- **Latency and usage observations:**
- **Facts that required visual information:**
- **Facts available from text alone:**
- **Largest remaining weakness:**

<br/>

## 12. Revision Questions and Answers

**1. Why compare text-only, page-image, and combined inputs?**  
They expose different information. Comparing them reveals which facts are available in extracted text, which depend on visual layout, and whether combining sources improves evidence coverage.

**2. Why preserve page numbers during extraction?**  
Page identifiers maintain traceability from a claim to the source document and make independent review possible.

**3. Does schema validation prove an extracted fact is correct?**  
No. It checks structure and types. Evidence verification must establish whether the value is supported by the source.

**4. Why inspect numerical and table claims independently?**  
Models and extraction pipelines can misread digits, units, row/column associations, signs, and chart scales. Independent checks catch errors that a fluent summary may conceal.

**5. What should happen when a value cannot be read?**  
Represent it as unreadable or uncertain, preserve the source locator, and avoid inventing a replacement value.

**6. Why can combined input perform worse than text-only input?**  
It may introduce duplicated or conflicting content, incorrect page associations, additional distractions, or context and processing costs.

**7. What is the difference between a citation and evidence support?**  
A citation points to a source location. Evidence support means the referenced source actually justifies the associated claim.

<br/>

## 13. Completion Checklist

- [ ] Choose an authorized document containing both text and visual information.
- [ ] Preserve page IDs through text extraction and image rendering.
- [ ] Run text-only, page-image, and combined approaches on comparable tasks.
- [ ] Define and validate a structured output schema.
- [ ] Link extracted facts and summary claims to inspectable source evidence.
- [ ] Independently check numerical and table claims.
- [ ] Record omissions, unsupported claims, and uncertainty failures.
- [ ] Compare quality, latency, preprocessing effort, and usage.
- [ ] Identify facts that required visual information and facts available from text alone.
- [ ] Document the largest remaining weakness.

<br/>

## Checkpoint

**Explain which facts required visual information and which were available from text alone.**

For each evaluated fact, identify the evidence source. Textual facts may be available directly from selectable text, while chart relationships, arrow direction, spatial layout, or image-only labels may require visual inspection. Some facts require both: extracted text may supply a number, while the page image confirms its row, column, unit, or context.

Your conclusion should be based on inspected source evidence and measured comparison results—not on the assumption that one input strategy is always superior.

<br/>

## Further Reading

Check the current documentation for the exact libraries and model API used in your implementation.

- [PyMuPDF documentation](https://pymupdf.readthedocs.io/)
- [Pydantic documentation](https://docs.pydantic.dev/)
- [OpenAI image and vision guide](https://platform.openai.com/docs/guides/images-vision)
- [OpenAI Responses API reference](https://platform.openai.com/docs/api-reference/responses)
- [OpenAI API pricing](https://openai.com/api/pricing/)
