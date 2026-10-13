# Level 8: Retrieval-Augmented Generation (RAG)

**Goal:** Build applications that use retrieved information to ground model responses in a defined knowledge source.

This README is the plan for creating notes one by one. Keep numbered Markdown notes directly in `Level 8`, following the previous levels. The filenames below are planned files, not existing chapter links.

## Prerequisites

- Complete [Level 7: Embeddings and Semantic Search](<../Level 7/README.md>).
- Understand dense retrieval, BM25, metadata filters, permissions, and index lifecycle management.
- Review prompt design, structured generation, model APIs, and validation from Levels 5–6.
- Use a reproducible Python environment and public or synthetic documents, including a small PDF collection.

## Learning outcomes

After completing this level, you should be able to:

- Trace ingestion and query-time RAG pipelines separately.
- Parse documents while preserving useful structure and provenance.
- Compare chunking, retrieval, rewriting, and reranking configurations.
- Select evidence within a context budget and generate source-grounded answers.
- Return verifiable citations and handle insufficient or conflicting evidence.
- Enforce retrieval permissions and maintain current indexes after updates and deletion.
- Evaluate retrieval separately from answer quality and diagnose pipeline failures.
- Build a PDF Q&A application and a knowledge-base assistant with source citations.

## Study order and planned note files

| Order | Planned note filename | Focus |
|---|---|---|
| 1 | `01_rag_architecture_and_data_flow.md` | Ingestion and query-time pipelines |
| 2 | `02_document_ingestion_and_parsing.md` | Source inventory, parsing, and ingestion records |
| 3 | `03_pdf_extraction_ocr_and_document_structure.md` | Digital PDFs, scans, tables, and reading order |
| 4 | `04_chunking_strategies_and_overlap.md` | Boundaries, sizes, overlap, and source mapping |
| 5 | `05_metadata_design_and_filtering.md` | Provenance, versions, and retrieval constraints |
| 6 | `06_indexing_and_baseline_retrieval.md` | Building the first searchable knowledge source |
| 7 | `07_dense_sparse_and_hybrid_retrieval.md` | Complementary signals and rank fusion |
| 8 | `08_query_rewriting_and_expansion.md` | Retrieval-oriented query transformations |
| 9 | `09_reranking.md` | Candidate scoring and relevance refinement |
| 10 | `10_parent_child_and_multi_stage_retrieval.md` | Small retrieval units and broader evidence |
| 11 | `11_context_selection_and_compression.md` | Evidence assembly within a token budget |
| 12 | `12_grounded_answer_generation.md` | Evidence-restricted prompts and answer contracts |
| 13 | `13_citations_and_source_attribution.md` | Source identifiers, locators, and claim support |
| 14 | `14_missing_evidence_and_unanswerable_questions.md` | Abstention, clarification, and conflicting sources |
| 15 | `15_ingestion_updates_reindexing_and_deletion.md` | Refreshing sources and removing stale content |
| 16 | `16_retrieval_permissions_and_data_isolation.md` | Authorization throughout the pipeline |
| 17 | `17_basic_and_advanced_rag_patterns.md` | Choosing improvements from measured failures |
| 18 | `18_rag_failure_modes_and_evaluation.md` | Retrieval metrics, answer quality, and diagnostics |
| 19 | `19_pdf_question_answering_project.md` | A reproducible PDF Q&A baseline |
| 20 | `20_knowledge_base_assistant_project.md` | Citations, permissions, updates, and comparisons |
| 21 | `21_practice_and_revision.md` | Consolidation and the level report |

## Chapter outlines

### 01. RAG Architecture and Data Flow

- Define retrieval-augmented generation and distinguish it from fine-tuning.
- Trace ingestion: source collection, parsing, chunking, encoding, and indexing.
- Trace query handling: authorization, retrieval, context assembly, generation, and validation.
- Separate stored model knowledge from supplied evidence.
- Identify measurement and failure points in both pipelines.

**Practice:** Draw a two-pipeline RAG diagram with data and trust boundaries.

**Checkpoint:** Explain why retrieval supplies evidence without updating model weights.

### 02. Document Ingestion and Parsing

- Inventory sources, formats, ownership, and update frequency.
- Assign stable source identifiers and record content hashes and versions.
- Parse supported formats into a consistent document representation.
- Preserve headings, section boundaries, source locations, and extraction status.
- Handle duplicates, empty output, malformed files, and partial failures explicitly.
- Treat documents as untrusted data and use bounded, safe parsing.

**Practice:** Ingest several public or synthetic documents and produce a success/failure manifest.

**Checkpoint:** Trace each parsed record back to its source and version.

### 03. PDF Extraction, OCR, Tables, and Document Structure

- Distinguish digitally encoded text from scanned pages requiring OCR.
- Inspect reading order, columns, headings, headers, footers, and page breaks.
- Preserve table structure and relationships rather than flattening indiscriminately.
- Record page numbers and distinguish PDF page indexes from printed page labels.
- Review OCR quality, missing text, and uncertain extraction.
- Discuss when layout-aware or multimodal parsing may be needed.

**Practice:** Compare extraction from a text PDF, a scanned page, and a table-containing page.

**Checkpoint:** Recognize when poor answers originate from parsing errors rather than retrieval or generation.

### 04. Chunking Strategies and Overlap

- Compare fixed-size, recursive, sentence-based, and structure-aware splitting.
- Choose token-aware sizes compatible with embedding and generation limits.
- Preserve headings, table context, and source locators.
- Discuss overlap, duplicates, indexing cost, and retrieval noise.
- Keep passage IDs and source mappings stable enough for updates and citations.
- Compare configurations using representative questions rather than assuming one best size.

**Practice:** Chunk the same document in two ways and inspect boundary-dependent retrieval results.

**Checkpoint:** Explain why larger chunks can preserve context while diluting retrieval specificity.

### 05. Metadata Design and Filtering

- Define source ID, chunk ID, page/section locator, version, language, and timestamps.
- Include trustworthy ownership and permission metadata.
- Validate required metadata and missing-field behavior.
- Apply source, date, category, and language filters.
- Distinguish relevance filters from mandatory authorization predicates.

**Practice:** Design a chunk schema and retrieve from selected source subsets.

**Checkpoint:** Explain which metadata supports relevance, provenance, and access enforcement.

### 06. Indexing and Baseline Retrieval

- Reuse Level 7 embedding conventions and index configuration.
- Store compatible vectors, source records, and metadata.
- Build an exact or simple dense-retrieval baseline before adding advanced stages.
- Inspect top-k candidates with scores and source text.
- Verify query/document encoding, normalization, and metric compatibility.

**Practice:** Retrieve evidence for a small labeled question set without generating answers yet.

**Checkpoint:** Separate retrieval correctness from whether a model can phrase an answer well.

### 07. Dense, Sparse, and Hybrid Retrieval

- Compare dense embeddings, BM25, and other sparse approaches conceptually.
- Analyze paraphrase queries versus exact names, codes, and identifiers.
- Combine candidates using rank fusion such as reciprocal rank fusion.
- Discuss score normalization if score-based combination is used.
- Deduplicate candidates and apply mandatory permissions to every retrieval branch.
- Compare hybrid results against both component baselines.

**Practice:** Evaluate dense, BM25, and one hybrid configuration on the same queries.

**Checkpoint:** Explain why raw scores from different retrieval systems should not be added without justification.

### 08. Query Rewriting and Expansion

- Introduce query cleanup, contextual reformulation, and alternative query generation.
- Resolve conversation references using bounded history where appropriate.
- Preserve names, identifiers, dates, intent, and authorization scope.
- Discuss drift, invented assumptions, added latency, and expanded retrieval noise.
- Bound generated queries and keep the original query available as a baseline.

**Practice:** Compare original and rewritten queries, including cases where rewriting hurts retrieval.

**Checkpoint:** Verify that retrieval improvements do not come from changing the user's question.

### 09. Reranking

- Distinguish broad candidate retrieval from more expensive relevance scoring.
- Introduce cross-encoder rerankers and model-based ranking conceptually.
- Compare candidate count, quality, latency, and input limits.
- Preserve source IDs and metadata through ranking.
- Avoid sending unauthorized candidates to external reranking services.

**Practice:** Rerank a fixed candidate set and compare its ordering against relevance judgments.

**Checkpoint:** Explain why reranking cannot recover evidence absent from its candidate set.

### 10. Parent-Child and Multi-Stage Retrieval

- Retrieve small passages and fetch their permitted parent sections or documents.
- Compare retrieval units with context units.
- Trace candidate generation, deduplication, reranking, and evidence expansion.
- Preserve source/version relationships during parent lookup.
- Bound expansion and recheck permissions when fetching broader content.

**Practice:** Compare passage-only context with permitted parent-section expansion.

**Checkpoint:** Explain when expansion improves evidence and when it adds irrelevant or unauthorized material.

### 11. Context Selection and Compression

- Reserve context capacity for instructions, the question, and output.
- Select relevant, diverse evidence and remove duplicate overlap.
- Compare extractive selection with generated summaries of evidence.
- Preserve source references, qualifiers, numbers, and conflicting claims.
- Discuss information loss, ordering, and long-context limitations.
- Keep original passages available to verify compressed material.

**Practice:** Assemble a bounded evidence packet and check that key facts survive selection or compression.

**Checkpoint:** Explain why compressed text must not be treated as more authoritative than its sources.

### 12. Grounded Answer Generation

- Construct prompts that distinguish trusted instructions from retrieved content.
- Define evidence-use rules, answer format, and missing-information behavior.
- Separate source statements from inference and unsupported model knowledge.
- Include source identifiers in the evidence packet.
- Validate response structure and factual support independently.
- Recognize indirect prompt injection in retrieved documents.

**Practice:** Generate answers from fixed evidence packets and inspect unsupported additions.

**Checkpoint:** Explain why an evidence-restricted prompt reduces risk without guaranteeing faithfulness.

### 13. Citations and Source Attribution

- Assign application-controlled source identifiers and resolvable page/section locators.
- Require citations for supported claims rather than decorative source lists.
- Verify returned identifiers against the supplied evidence.
- Check whether cited passages actually support associated statements.
- Preserve links to authorized source views and the relevant source version.
- Avoid exposing private titles, snippets, or URLs through citation metadata.

**Practice:** Identify fabricated citations, valid identifiers with unsupported claims, and correctly supported citations.

**Checkpoint:** Distinguish citation validity from citation support.

### 14. Missing Evidence and Unanswerable Questions

- Distinguish no relevant evidence, incomplete evidence, ambiguity, and conflicting evidence.
- Define abstention and clarification behavior.
- Avoid treating similarity scores as calibrated answerability probabilities.
- Prefer explicit uncertainty when available sources disagree or are outdated.
- Handle permission-restricted evidence without revealing inaccessible content.

**Practice:** Test answerable, partially answerable, unanswerable, and permission-filtered questions.

**Checkpoint:** Explain why an empty result set does not establish that the underlying fact is false.

### 15. Ingestion Updates, Re-indexing, and Deletion

- Detect changed sources and replace their affected chunks.
- Handle model/configuration changes that require re-embedding.
- Publish coherent index versions and avoid stale or duplicate passages.
- Remove deleted source content from active retrieval and associated metadata.
- Invalidate relevant caches and document backend-specific consistency behavior.
- Distinguish active-search removal from backup and retention policies.

**Practice:** Update a source fact, delete a document, and verify retrieval and citations reflect current permitted versions.

**Checkpoint:** Trace source lifecycle changes through both indexing and query-time behavior.

### 16. Retrieval Permissions and Data Isolation

- Derive identity and access scope from authenticated application state.
- Enforce access across dense, lexical, expanded, and parent-document retrieval.
- Isolate tenant data, indexes or namespaces, caches, and conversation state as required.
- Recheck access when fetching source text and citation targets.
- Fail closed on missing or invalid authorization metadata.
- Keep unauthorized content out of prompts, external services, logs, and responses.

**Practice:** Test two synthetic users and attempt cross-user retrieval, parent expansion, and citation access.

**Checkpoint:** Explain how server-side controls enforce access independently of model instructions.

### 17. Basic versus Advanced RAG Patterns

- Establish a simple retrieve-select-generate baseline.
- Compare hybrid retrieval, rewriting, reranking, parent expansion, and compression as optional improvements.
- Select stages based on diagnosed failures and measured benefit.
- Discuss complexity, added calls, latency, cost, and maintenance.
- Use controlled comparisons to avoid attributing gains to several simultaneous changes.
- Keep query-processing workflows fixed and bounded within this course.

**Practice:** Choose one improvement for a baseline failure and justify why it is the next experiment.

**Checkpoint:** Explain why adding more stages can introduce regressions.

**Scope boundary:** Autonomous retrieval planning, agent loops, and agent orchestration belong to the separate Agentic AI course.

### 18. Common RAG Failure Modes and Evaluation

- Diagnose ingestion loss, broken chunk boundaries, weak retrieval, poor ranking, and context omission.
- Identify unsupported answers, false abstention, fabricated citations, and stale sources.
- Label relevant evidence and expected answer criteria in a fixed dataset.
- Measure retrieval with suitable Precision@k, Recall@k, MRR, or nDCG metrics.
- Assess answer correctness, faithfulness, completeness, citation support, and abstention separately.
- Record per-stage latency, token usage, cost, and permission/lifecycle correctness.
- Review limitations of human judgments and model-based evaluation.

**Practice:** Compare retrieval configurations while holding the model and generation prompt fixed, then analyze answer failures separately.

**Checkpoint:** Locate the failing stage before changing the prompt or retrieval configuration.

**Depth boundary:** Larger evaluation programs, judge calibration, experiment tracking, and regression gates are expanded in Level 13.

### 19. PDF Question-Answering Project

- Build a small ingestion-to-answer pipeline over public or synthetic PDFs.
- Inspect extraction quality and preserve page locators.
- Implement baseline chunking, retrieval, context budgeting, and cited answers.
- Include table-containing and scanned samples where tools are available; document unsupported cases.
- Test questions with and without supporting evidence.

**Practice:** Demonstrate PDF Q&A with inspectable retrieved passages and page citations.

**Checkpoint:** Reproduce an answer and trace its supporting evidence back to the original page.

### 20. Knowledge-Base Assistant Project

- Extend the baseline to multiple sources with versions and metadata.
- Implement two synthetic access scopes and authorized source views.
- Compare baseline retrieval with one or more measured improvements.
- Add source refresh and deletion workflows.
- Keep conversational history bounded and avoid treating earlier answers as authoritative evidence.
- Return answer, citations, and explicit insufficient-evidence status where appropriate.

**Practice:** Demonstrate source updates, permission-filtered retrieval, and unanswerable-question handling.

**Checkpoint:** Explain both the assistant's useful behavior and remaining limitations.

### 21. Practice and Revision

- Review the full ingestion and query-time flows.
- Compare chunking and retrieval strategies on fixed cases.
- Verify citation support, abstention, permissions, and deletion.
- Diagnose failures by stage rather than relying on answer fluency.
- Complete the report below and document both project demonstrations.

**Checkpoint:** Defend a pipeline configuration with evidence and identify its largest remaining weakness.

## Level deliverable: Evaluated RAG applications

Build the PDF Q&A application and knowledge-base assistant. They may share one codebase, with separate demonstrations. Create `rag_evaluation_report.md` in this folder containing:

1. Corpus inventory, source permissions, versions, and reproducible setup.
2. Ingestion and query-time architecture diagrams with trust boundaries.
3. Parsing, chunking, embedding, index, retrieval, and generation configurations.
4. At least twenty fixed questions with relevant source locations and expected answer criteria, covering answerable, ambiguous, conflicting, unanswerable, and permission-restricted cases.
5. A baseline and at least one retrieval improvement compared on the same dataset.
6. Retrieval metrics and separate answer-quality, citation-support, and abstention results.
7. Tests for unauthorized access, malformed documents, source updates, and deletion.
8. Examples tracing answers and citations to original source passages.
9. Latency, token usage, cost, and environment measurements where available.
10. Failure analysis, trade-offs, remaining risks, and recommended next improvements.

Use public or synthetic data. A notebook, command-line interface, or small FastAPI application is sufficient. Local models and open-source tools can support the projects without paid services; clearly label estimates and fixture-based checks. Full cloud deployment and operational monitoring belong to Level 15.

## Suggested format for each note

1. Learning objectives and concepts reused from previous levels.
2. Intuition and a concrete document/question example.
3. Pipeline diagram, schemas, or source-mapping details.
4. A minimal implementation or worked comparison.
5. Configuration choices and measured trade-offs.
6. Failure cases, permissions, and trust boundaries.
7. Exercise and revision questions with answers.
8. References and optional extensions.

Verify current parser, OCR, model, and database capabilities when writing implementation notes. Keep corpus versions, configurations, prompts, and evaluation inputs reproducible.

## Completion checklist

- [ ] Explain ingestion and query-time RAG flows separately.
- [ ] Inspect PDF extraction, OCR, tables, and document structure.
- [ ] Compare chunking strategies with preserved provenance.
- [ ] Build indexed retrieval with metadata filters.
- [ ] Compare dense, sparse, and hybrid configurations.
- [ ] Explain rewriting, reranking, and parent-child retrieval trade-offs.
- [ ] Assemble a bounded, source-traceable context packet.
- [ ] Generate grounded answers and verify citation support.
- [ ] Handle missing, conflicting, and inaccessible evidence appropriately.
- [ ] Verify source updates, re-indexing, and deletion.
- [ ] Enforce permissions throughout retrieval and source access.
- [ ] Evaluate retrieval separately from answer generation.
- [ ] Demonstrate both PDF Q&A and a knowledge-base assistant.
- [ ] Complete and review the RAG evaluation report.

## Scope and next step

This level develops source-grounded applications using fixed, application-controlled workflows. Advanced multimodal retrieval is introduced in Level 9; systematic evaluation, comprehensive security, and production operations are expanded in Levels 13–15. Agentic retrieval and autonomous orchestration remain outside this course.

Recommended engineering path: study **Level 13 — GenAI Evaluation and Optimization**, then **Level 14 — GenAI Security and Responsible AI**, before production deployment. For the numbered topic sequence, continue to **Level 9 — Multimodal Generative AI**. See the [main course outline](../README.md).
