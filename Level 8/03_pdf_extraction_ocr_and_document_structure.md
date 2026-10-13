# 03. PDF Extraction, OCR, Tables, and Document Structure

**Level 8: Retrieval-Augmented Generation (RAG) · Generative AI Engineering**

## 1. Learning Objectives

After completing this chapter, you should be able to:

- Distinguish digitally encoded PDF text from scanned pages that require Optical Character Recognition (OCR).
- Inspect reading order, columns, headings, headers, footers, and page breaks.
- Preserve table structure and relationships instead of flattening tables indiscriminately.
- Record physical PDF page indexes separately from printed page labels.
- Review OCR quality, missing text, and uncertain extraction.
- Decide when layout-aware or multimodal document parsing is appropriate.
- Diagnose when poor RAG answers originate from extraction problems rather than retrieval or generation.

<br/>

## 2. Why PDF Parsing Is Difficult

PDF is a page-description format, not necessarily a structured document format. A PDF may visually display paragraphs, headings, columns, tables, footnotes, and page numbers, but the file may not store these elements as a clean, ordered sequence of text.

A parser might extract text in the wrong order, omit text embedded in images, merge table columns, or include repeated headers and footers in every page's content.

These issues matter in RAG because later stages can only retrieve and generate from the information made available to them. If the parser loses a number or separates a qualification from its statement, a powerful retrieval system may still return misleading evidence.

<br/>

## 3. Digital PDFs Versus Scanned PDFs

### 3.1 Digitally encoded text

A digital PDF usually contains text that can be selected, searched, or extracted directly.

Examples include PDFs exported from Word, Google Docs, LaTeX, or many reporting systems.

**Typical workflow:**

```text
PDF page → text extraction → structure inspection → normalized records
```

OCR may be unnecessary when the text layer is complete and accurate. However, digital PDFs can still have broken reading order, unusual font encoding, or image-only sections.

<br/>

### 3.2 Scanned PDFs

A scanned PDF often contains page images rather than usable text. It may have been created by scanning paper documents or by inserting images of pages into a PDF.

A text extractor may return an empty string or only a small amount of metadata.

OCR detects text within the page images and converts it into machine-readable characters.

**Typical workflow:**

```text
Scanned page image → preprocessing → OCR → text and confidence review
```

OCR can introduce errors, especially with low-resolution images, skewed pages, handwriting, unusual fonts, poor contrast, and dense tables.

<br/>

### 3.3 Mixed PDFs

A PDF can contain both selectable text and scanned pages. Some pages may have a usable text layer while others require OCR. A scanned page may also contain an existing but inaccurate OCR layer.

Therefore, choose the extraction method based on observed page content and quality rather than assuming that every page in a PDF is alike.

<br/>

### Quick comparison

| Property | Digital-text PDF | Scanned PDF |
|---|---|---|
| Primary content representation | Encoded text and page layout | Page images, sometimes with an OCR layer |
| First extraction approach | Native text extraction | OCR if usable text is absent or inadequate |
| Common failure | Reading order or font-encoding errors | Recognition errors or missing text |
| Table extraction | May require layout-aware processing | OCR plus layout/table recognition may be needed |
| Quality checks | Completeness, order, symbols, columns | Completeness, OCR confidence, visual comparison |

<br/>

## 4. Inspect Reading Order and Page Layout

A PDF's visual order does not guarantee that its extracted text appears in the same order.

Consider a two-column page:

```text
Visual layout

┌──────────────────────┬──────────────────────┐
│ LEFT COLUMN           │ RIGHT COLUMN         │
│ Introduction          │ Experimental Results │
│ Method                │ Discussion           │
│ Data Collection       │ Limitations          │
└──────────────────────┴──────────────────────┘
```

A naive extractor might output the first line from each column, then the next line from each column, interleaving unrelated content. Another extractor might read the entire left column first, which may be correct for this layout. The appropriate order depends on the document's actual reading flow.

Inspect extracted text for:

- Interleaved columns or paragraphs
- Headings detached from their sections
- Repeated headers and footers
- Hyphenated words split across line breaks
- Footnotes inserted into the middle of paragraphs
- Missing bullets, mathematical symbols, or special characters
- Text boxes that appear in an unexpected sequence

<br/>

### Example of a reading-order failure

Expected text:

```text
Eligibility
Employees with at least one year of service qualify.

Application
Submit the form to Human Resources.
```

Potentially incorrect extraction:

```text
Eligibility Application
Employees with at least one year of service qualify.
Submit the form to Human Resources.
```

The text remains present, but section relationships are less clear. This can cause a retriever to return the wrong statement for a question about eligibility or applications.

<br/>

### Headers and footers

Repeated page headers and footers can add noise to every chunk. Examples include document titles, confidentiality labels, page numbers, and copyright notices.

Do not remove repeated text blindly: a header may contain a version number or a confidentiality label that matters. Inspect patterns across pages and preserve information needed for provenance, version identification, or access handling.

<br/>

## 5. Preserve Tables and Their Relationships

Tables often contain relationships that disappear when cells are concatenated into plain text.

Consider this table:

| Leave type | Annual allowance | Eligibility |
|---|---:|---|
| Annual leave | 18 days | All permanent employees |
| Sick leave | 10 days | Subject to policy conditions |

Flattening the table into an unstructured string can make it unclear which allowance belongs to which leave type.

A more useful representation retains headers and row relationships:

```python
table_record = {
    "source_id": "employee_leave_policy",
    "page_index": 3,
    "table_id": "table_01",
    "headers": ["Leave type", "Annual allowance", "Eligibility"],
    "rows": [
        ["Annual leave", "18 days", "All permanent employees"],
        ["Sick leave", "10 days", "Subject to policy conditions"],
    ],
}
```

This representation allows downstream processing to interpret each row in the context of the column headers.

<br/>

### Table extraction strategies

- Preserve tables as structured rows and columns when the parser supports it.
- Associate each table with its source, page, caption, and surrounding section.
- Repeat essential headers when converting rows into independent text chunks.
- Preserve units, footnotes, merged-cell meaning, and multi-level headers where possible.
- Validate extracted cell values against the rendered PDF for important tables.

For example, if a table contains a value such as `1,500.00`, OCR might produce `1,50O.OO` or omit punctuation. Such errors can materially change a retrieved answer.

For complex tables, a layout-aware parser or a specialized table extraction tool may be more reliable than plain text extraction.

<br/>

## 6. Page Indexes Versus Printed Page Labels

A PDF page has a physical position in the file, while the page may display a printed label such as `i`, `1`, or `A-3`.

These are not always the same.

For example, a PDF may contain:

| Physical PDF page index (zero-based) | Physical page number (one-based) | Printed page label |
|---:|---:|---|
| 0 | 1 | Cover |
| 1 | 2 | i |
| 2 | 3 | ii |
| 3 | 4 | 1 |
| 4 | 5 | 2 |

A citation system should define its convention explicitly and preserve the values it can reliably determine.

A useful locator might be:

```python
locator = {
    "pdf_page_index": 3,       # Zero-based index used by code
    "pdf_page_number": 4,      # One-based physical page number
    "printed_page_label": "1", # Label printed on the page
}
```

Do not assume that a printed page label can always be inferred from the physical index. If it cannot be detected reliably, store it as unknown rather than inventing one.

Consistent page locators are essential for citations, debugging, and tracing a generated answer back to the original source.

<br/>

## 7. Extracting Text from a PDF with Python

One widely used Python library for extracting text from PDFs is PyMuPDF.

Install it:

```bash
pip install pymupdf
```

### 7.1 Extract text page by page

```python
from pathlib import Path
import pymupdf


def extract_pdf_text(pdf_path: str) -> list[dict]:
    results = []

    with pymupdf.open(pdf_path) as pdf:
        for page_index, page in enumerate(pdf):
            text = page.get_text("text").strip()

            results.append({
                "pdf_page_index": page_index,
                "pdf_page_number": page_index + 1,
                "text": text,
                "character_count": len(text),
                "extraction_status": (
                    "success" if text else "empty_text"
                ),
            })

    return results


pages = extract_pdf_text("documents/policy.pdf")

for page in pages:
    print(
        page["pdf_page_number"],
        page["extraction_status"],
        page["character_count"],
    )
```

This example records each page separately, which makes it easier to detect pages with no extracted text. A non-empty result is not proof that the extraction is correct: the text might be garbled or in the wrong order.

<br/>

### 7.2 Inspect suspicious pages

```python
for page in pages:
    if page["character_count"] < 30:
        print(f"Review PDF page {page['pdf_page_number']}")
        print(repr(page["text"]))
```

The threshold is illustrative. Short pages may legitimately contain only a heading, image, or diagram. Use this as a review signal, not an automatic verdict.

<br/>

### 7.3 Inspect text blocks and layout

PyMuPDF can also return structured page data:

```python
import pymupdf

with pymupdf.open("documents/policy.pdf") as pdf:
    page = pdf[0]
    page_data = page.get_text("dict")

    for block in page_data["blocks"]:
        if "lines" not in block:
            continue

        block_text = []
        for line in block["lines"]:
            for span in line["spans"]:
                block_text.append(span["text"])

        print("Block:", "".join(block_text))
        print("Bounding box:", block["bbox"])
```

Bounding boxes provide coordinates for text blocks, which can help inspect columns and layout. The order returned by a parser may still require correction or layout-aware processing. Coordinates alone do not guarantee correct semantic reading order.

<br/>

## 8. OCR: Recognizing Text in Scanned Pages

OCR is useful when the page contains images of text and native text extraction is absent or unreliable.

Common OCR stages include:

1. Render the PDF page as an image.
2. Preprocess the image if necessary, for example by correcting rotation or improving contrast.
3. Detect text regions and recognize characters.
4. Reconstruct lines, blocks, and reading order.
5. Review recognition quality and preserve page provenance.

<br/>

### Example with Tesseract OCR

Tesseract is an open-source OCR engine. A Python wrapper can call it, but the Tesseract executable must also be installed separately.

Install the Python packages:

```bash
pip install pymupdf pytesseract pillow
```

Install the Tesseract OCR engine using the appropriate instructions for your operating system. Then run:

```python
import pymupdf
import pytesseract
from PIL import Image
from io import BytesIO


def ocr_pdf_page(pdf_path: str, page_index: int) -> dict:
    with pymupdf.open(pdf_path) as pdf:
        if not 0 <= page_index < len(pdf):
            raise IndexError("PDF page index is out of range")

        page = pdf[page_index]

        # Render the page at a higher resolution for OCR.
        pixmap = page.get_pixmap(
            matrix=pymupdf.Matrix(2, 2),
            alpha=False,
        )

        image = Image.open(BytesIO(pixmap.tobytes("png")))
        text = pytesseract.image_to_string(image).strip()

        return {
            "pdf_page_index": page_index,
            "pdf_page_number": page_index + 1,
            "text": text,
            "character_count": len(text),
            "extraction_status": (
                "success" if text else "empty_ocr"
            ),
        }


result = ocr_pdf_page("documents/scanned_policy.pdf", 0)
print(result)
```

The rendering scale of `2` is an example, not a universal optimum. Higher resolution can improve recognition but increases processing time and memory use.

<br/>

### OCR quality checks

OCR output should be reviewed for:

- Missing lines or paragraphs
- Confused characters, such as `0` and `O`, or `1` and `l`
- Incorrect dates, amounts, percentages, and identifiers
- Lost table columns and row associations
- Broken reading order
- Unexpectedly low text volume
- Recognition confidence, when the OCR engine exposes it

An OCR engine's confidence score is a useful signal but not a guarantee of correctness. Critical values may need direct comparison with the original page or human review.

<br/>

## 9. When to Use Layout-Aware or Multimodal Parsing

Plain text extraction is often sufficient for simple, digitally generated documents. More complex documents may require methods that use layout, images, or visual context.

### Plain text extraction may be sufficient when:

- The PDF contains selectable text in a straightforward reading order.
- Paragraphs and headings are extracted reliably.
- Tables are simple or not important to the application.
- Page-level source references can be preserved.

<br/>

### Layout-aware parsing may be needed when:

- The page has multiple columns or complex reading order.
- Tables contain merged cells, multi-level headers, or footnotes.
- Headings, captions, and text blocks must remain associated.
- The document uses forms, sidebars, or complex visual grouping.

<br/>

### OCR or multimodal parsing may be needed when:

- Pages are scanned or contain image-only text.
- Diagrams, charts, or images carry essential information.
- Understanding depends on the spatial relationship between text and visuals.
- Tables or forms cannot be reliably reconstructed by a conventional parser.

A multimodal model may interpret page images and their visual relationships, but it can still misread text, numbers, or layout. Validate critical information and preserve links to the original pages.

Tool selection should be driven by observed extraction failures, accuracy requirements, privacy constraints, processing cost, and latency—not by choosing the most complex parser by default.

<br/>

## 10. Diagnosing Parsing Errors Versus Retrieval or Generation Errors

A poor answer can originate at different stages of the RAG pipeline. Inspect each stage's output before changing the system.

| Observation | Likely area to investigate |
|---|---|
| The source visibly says `18 days`, but extracted text says `8 days` | Parsing or OCR |
| A paragraph is missing from extracted output | Parsing or extraction coverage |
| The correct passage exists in normalized records but is absent from top-k results | Retrieval, chunking, embeddings, or indexing |
| The correct passage is retrieved but omitted from the final context | Context selection or compression |
| The correct evidence reaches the model but the answer contradicts it | Generation or prompt design |
| The answer is correct but cites the wrong page | Provenance or citation mapping |

<br/>

### A practical debugging procedure

1. Open the original PDF page and confirm the expected fact.
2. Inspect the extracted page text and table structure.
3. Inspect the normalized record and its source locator.
4. Inspect the chunks generated from that record.
5. Run retrieval and review the returned text and metadata.
6. Inspect the exact context supplied to the model.
7. Compare the answer and citations against that context and the original page.

**Engineering rule:** Do not tune retrieval or the generation prompt to compensate for content that was incorrectly extracted or never ingested.

<br/>

## 11. Practice: Compare Three PDF Types

### Task

Prepare three test files:

1. **Text PDF:** A digitally generated page containing a heading and paragraph.
2. **Scanned PDF:** An image of a printed or synthetic page.
3. **Table PDF:** A page containing a table with headers, numeric values, and at least two rows.

Use public or synthetic material that you are permitted to process.

<br/>

### Procedure

1. Record each file's name, source ID, and content hash.
2. Extract text page by page with PyMuPDF.
3. Record physical page indexes and page numbers.
4. Identify pages with empty or suspiciously short extraction.
5. Run OCR on scanned pages or pages with unusable text layers.
6. Inspect table rows and columns against the original page.
7. Review headings, reading order, headers, footers, and page breaks.
8. Record each page's extraction status and any warnings.
9. Compare the extracted output with the original visual content.

<br/>

### Suggested experiment manifest

| File type | Native text result | OCR needed? | Structure check | Final status |
|---|---|---|---|---|
| Text PDF | Record observed result | If required | Heading and reading order | Fill in |
| Scanned PDF | Record observed result | Usually, if no usable text layer | OCR completeness | Fill in |
| Table PDF | Record observed result | Depends on text layer | Header/row/column relationships | Fill in |

Do not assume the result before inspecting the files. A scanned PDF may contain a usable OCR layer, and a text PDF may still have serious extraction defects.

<br/>

### Optional extension

Create a JSON manifest containing:

- `source_id`
- `content_hash`
- `pdf_page_index`
- `pdf_page_number`
- `printed_page_label`, if known
- `extraction_method` (`native_text`, `ocr`, or another documented method)
- `extraction_status`
- `character_count`
- `warnings`

Use the manifest to identify which pages need manual review or a different extraction method.

<br/>

## 12. Chapter Checkpoint

**Question:** How can you recognize when a poor answer originates from parsing errors rather than retrieval or generation?

**Answer:** Compare the original source with the extracted text and structured records first. If the fact is missing, corrupted, misordered, or associated with the wrong table cell during extraction, the problem originates in parsing or OCR. If the extracted content is correct but the relevant passage is not returned, investigate chunking, indexing, or retrieval. If the correct evidence is retrieved and supplied to the model but the answer is wrong, investigate generation and validation. Tracing each stage prevents changes to later components from masking an upstream data-quality problem.

<br/>

## 13. Key Takeaways

- Digitally encoded text and scanned page images require different extraction approaches.
- PDFs can contain mixed content, and extraction quality must be checked page by page.
- Reading order, columns, headings, headers, footers, and page breaks can affect meaning.
- Tables should retain their headers, row relationships, units, and footnotes wherever possible.
- Store zero-based PDF page indexes separately from one-based physical page numbers and printed page labels.
- OCR can recover image-based text but can introduce recognition errors; confidence scores do not guarantee correctness.
- Layout-aware or multimodal parsing is useful when ordinary extraction loses important structure.
- Preserve provenance and extraction status so answers can be traced to the original source.
- Diagnose parsing, retrieval, context assembly, and generation separately.

<br/>

## 14. References

- [PyMuPDF documentation](https://pymupdf.readthedocs.io/)
- [PyMuPDF text extraction recipes](https://pymupdf.readthedocs.io/en/latest/recipes-text.html)
- [Tesseract OCR documentation](https://tesseract-ocr.github.io/)
- [pytesseract documentation](https://github.com/madmaze/pytesseract)
- [Pillow documentation](https://pillow.readthedocs.io/)


<br/>


**Next chapter:** `04_chunking_strategies_and_overlap.md` — Fixed-size, recursive, sentence-based, and structure-aware chunking; token-aware sizing; overlap; and source mapping.
