# Level 7: Embeddings and Semantic Search

Represent text as vectors and retrieve relevant content using dense and lexical search. Understand similarity metrics, vector indexes, metadata, permissions, and index maintenance, then build a measured semantic-search prototype.

This README is the plan for creating notes one by one. Keep numbered Markdown notes directly in `Level 7`, following the previous levels. The filenames below are planned files, not existing chapter links.

<br/>

## Prerequisites

- Complete [Level 6: LLM APIs and Application Development](<../Level 6/README.md>).
- Review vectors, dot products, norms, basic NumPy, and data handling from Level 0.
- Understand API configuration, bounded batch processing, validation, authentication, and safe logging.
- Use a small public or synthetic corpus and an isolated Python environment. Paid embedding services are optional.

<br/>

## Learning outcomes

After completing this level, you should be able to:

- Explain what text embeddings represent and where they can fail.
- Generate compatible document and query embeddings.
- Compare cosine similarity, dot product, and distance metrics.
- Build dense search and a BM25 lexical baseline.
- Distinguish exact search from approximate nearest-neighbor search and compare index trade-offs.
- Apply metadata filters and server-enforced retrieval permissions.
- Distinguish indexing libraries from vector stores and databases.
- Evaluate model choices, index updates, and deletion behavior using representative queries.

<br/>

## Study order and planned note files

| Order | Planned note filename | Focus |
|---|---|---|
| 1 | `01_embeddings_and_semantic_search_overview.md` | Representations and retrieval data flow |
| 2 | `02_text_embedding_models_and_limitations.md` | Model behavior, input limits, and failure cases |
| 3 | `03_document_and_query_embeddings.md` | Compatible encoding and asymmetric retrieval |
| 4 | `04_vector_dimensions_and_normalization.md` | Shapes, norms, and model compatibility |
| 5 | `05_similarity_and_distance_metrics.md` | Cosine similarity, dot product, and Euclidean distance |
| 6 | `06_dense_lexical_and_sparse_retrieval.md` | Dense versus sparse representations and keyword matching |
| 7 | `07_bm25_lexical_baseline.md` | Tokenization, term statistics, and baseline retrieval |
| 8 | `08_exact_and_approximate_nearest_neighbor_search.md` | Exact reference results and ANN trade-offs |
| 9 | `09_vector_indexes_and_trade_offs.md` | Flat, graph-based, partitioned, and compressed indexes |
| 10 | `10_metadata_design_and_filtering.md` | Record fields, filters, and candidate selection |
| 11 | `11_access_control_aware_retrieval.md` | Authorization, ownership, and tenant isolation |
| 12 | `12_indexing_libraries_and_vector_databases.md` | FAISS versus managed or persistent vector systems |
| 13 | `13_embedding_model_selection.md` | Quality, language, domain, latency, and cost |
| 14 | `14_index_updates_and_deletion.md` | Stable IDs, versioning, refreshes, and removal |
| 15 | `15_semantic_search_testing_and_evaluation.md` | Relevance labels, retrieval metrics, and failure analysis |
| 16 | `16_practice_and_revision.md` | Search experiments and the level deliverable |

<br/>

## Chapter outlines

### 01. Embeddings and Semantic Search Overview

- Define an embedding as a learned numerical representation.
- Distinguish token-level representations from text embeddings used for retrieval.
- Trace corpus preparation, document encoding, indexing, query encoding, scoring, and ranked results.
- Compare semantic relatedness with literal keyword overlap.
- Separate retrieval from answer generation.

**Practice:** Draw a search pipeline and identify stored data versus query-time operations.

**Checkpoint:** Explain why a retrieved result is a candidate source rather than a verified answer.

<br/>

### 02. Text Embedding Models and Their Limitations

- Introduce retrieval-trained encoders and pooled text representations conceptually.
- Discuss token limits, truncation, input length, and domain/language coverage.
- Examine negation, identifiers, numbers, rare terms, and ambiguous queries.
- Explain that embedding proximity does not establish truth or factual agreement.
- Distinguish embedding services from text-generation services.
- Record model versions, licenses, and supported input formats.

**Practice:** Compare related, unrelated, and subtly contradictory sentences using one model or prepared vectors.

**Checkpoint:** Identify examples where semantic proximity can be misleading.

<br/>

### 03. Document and Query Embeddings

- Compare symmetric similarity with asymmetric query-to-document retrieval.
- Use required query/document modes, prefixes, or instructions where documented by the model.
- Keep query and corpus representations in a compatible embedding space.
- Prepare stable document or passage IDs and source text.
- Introduce simple passage splitting when documents exceed input limits.
- Batch document encoding with validation and bounded resource usage.

**Practice:** Encode a small collection and retrieve documents for several queries.

**Checkpoint:** Explain why equal vector dimensions alone do not make two embedding models compatible.

**Depth boundary:** Advanced parsing, chunking, overlap, and document ingestion are developed in Level 8. Use a simple documented splitting strategy here.

<br/>

### 04. Vector Dimensions and Normalization

- Track corpus and query array shapes.
- Define vector norms and unit-length normalization.
- Handle zero vectors and invalid numerical values explicitly.
- Discuss storage, memory, and dimension-related computation.
- Distinguish supported dimension reduction from arbitrary truncation of vectors.
- Record model, dimension, normalization, and index configuration together.

**Practice:** Normalize toy vectors and verify their norms and shapes.

**Checkpoint:** Explain why changing dimensions or normalization may require rebuilding an index.

<br/>

### 05. Similarity and Distance Metrics

- Calculate cosine similarity, dot product, and Euclidean distance.
- Distinguish similarity scores, where larger is better, from distances, where smaller is better.
- Explain ranking relationships for unit-normalized vectors.
- Discuss the effect of vector magnitude on unnormalized dot products.
- Match the metric to model recommendations and index configuration.
- Explain why a similarity score is not a calibrated probability or a universal relevance threshold.

**Practice:** Rank a toy corpus with multiple metrics and compare normalized versus unnormalized results.

**Checkpoint:** Explain when metrics yield equivalent rankings and when they do not.

<br/>

### 06. Dense, Lexical, and Sparse Retrieval

- Compare dense numerical representations with sparse term-based representations.
- Explain exact-match strengths for names, codes, technical terms, and identifiers.
- Discuss semantic search strengths for paraphrases and vocabulary mismatch.
- Introduce classical lexical retrieval and learned sparse retrieval as distinct approaches.
- Recognize that sparse retrieval is broader than BM25.
- Preview hybrid retrieval without assuming dense and lexical scores are directly comparable.

**Practice:** Predict which retrieval approach will suit paraphrase queries versus exact-identifier queries.

**Checkpoint:** Explain why dense retrieval should be compared with a lexical baseline.

<br/>

### 07. BM25 as a Lexical Baseline

- Prepare consistent text tokenization for documents and queries.
- Explain term frequency, inverse document frequency, and document-length normalization.
- Introduce BM25 parameters conceptually without requiring a full derivation.
- Discuss stopwords, punctuation, language-specific processing, and identifier preservation.
- Retrieve top-k results and keep their IDs comparable with dense-search results.
- Explain vocabulary mismatch and the limitations of lexical matching.

**Practice:** Build a BM25 baseline on the same corpus used for dense search.

**Checkpoint:** Compare result relevance rather than directly comparing raw BM25 and embedding scores.

<br/>

### 08. Exact and Approximate Nearest-Neighbor Search

- Establish exhaustive scoring as an exact reference on a small dataset.
- Explain why large collections motivate approximate search.
- Compare ANN retrieval recall, search latency, index construction, and memory.
- Introduce candidate exploration and tunable search effort.
- Distinguish ANN agreement with exact neighbors from relevance to human judgments.

**Practice:** Compare approximate results with exact top-k neighbors and separately assess query relevance.

**Checkpoint:** Explain why accurate nearest-neighbor retrieval can still return irrelevant documents.

<br/>

### 09. Vector Indexes and Index Trade-offs

- Compare flat indexes, graph-based approaches such as HNSW, partitioned approaches such as IVF, and compression such as product quantization.
- Discuss construction, training requirements where applicable, and query-time parameters.
- Compare memory, latency, recall, insertion, and deletion constraints.
- Inspect supported combinations of metrics, dimensions, and persistence.
- Explain why suitable configurations depend on collection size and workload.

**Practice:** Create an index comparison table and run one approximate configuration against an exact baseline if supported.

**Checkpoint:** Document chosen parameters and avoid universal claims about the best index.

<br/>

### 10. Metadata Design and Filtering

- Define source IDs, passage IDs, ownership, language, timestamps, and document versions.
- Validate metadata types and missing-field behavior.
- Apply filters to restrict candidates based on application requirements.
- Compare prefiltering and postfiltering and their effects on result count and relevance.
- Discuss selective filters and implementation-dependent index behavior.
- Return enough source metadata to inspect retrieved results.

**Practice:** Search a synthetic corpus using language, date, and category filters.

**Checkpoint:** Explain why filtering after top-k selection may return too few relevant results.

<br/>

### 11. Access-Control-Aware Retrieval

- Derive user identity and permissions from authenticated application state.
- Enforce tenant, owner, and document access restrictions server-side.
- Do not allow user-supplied filters to weaken mandatory authorization predicates.
- Ensure unauthorized text and metadata are not returned, logged, or passed downstream.
- Recheck access at document fetch where required and handle permission changes.
- Fail closed when authorization data is missing or invalid.
- Distinguish relevance filtering from security enforcement.

**Practice:** Test two synthetic users with shared and private documents, including cross-user access attempts.

**Checkpoint:** Explain why prompting a model to ignore unauthorized documents cannot enforce retrieval permissions.

<br/>

### 12. Vector Indexing Libraries and Vector Stores/Databases

- Distinguish nearest-neighbor indexing from a complete persistence and data-management service.
- Use FAISS as an indexing-library example; discuss external metadata and lifecycle handling.
- Compare stores/databases such as Chroma, Pinecone, and Weaviate by documented capabilities.
- Consider persistence, metadata filters, updates, deletion, deployment, authentication, and operational effort.
- Choose one implementation for the core exercise rather than requiring every product.
- Verify current APIs, licensing, and service behavior when writing implementation notes.

**Practice:** Create a capability matrix and implement a small retrieval interface with one backend.

**Checkpoint:** Explain which responsibilities belong to the index and which remain in your application.

<br/>

### 13. Embedding Model Selection

- Define domain, language, document length, query style, and relevance requirements.
- Compare retrieval quality on the same labeled query set.
- Consider dimensions, throughput, latency, hardware, privacy, licensing, and cost.
- Check required query/document encoding conventions.
- Evaluate truncation and difficult inputs rather than relying only on public benchmarks.
- Plan full re-embedding or a compatible migration strategy when changing models.

**Practice:** Compare two embedding configurations or models using fixed queries and relevance judgments.

**Checkpoint:** Support model selection with application results and document assumptions.

<br/>

### 14. Index Updates and Deletion

- Use stable IDs, source versions, and content hashes where helpful.
- Distinguish insertion, replacement, upsert, soft deletion, and physical removal.
- Update all affected passages when a source changes.
- Remove stale vectors and metadata when documents are deleted.
- Track model/configuration versions to prevent mixing incompatible spaces.
- Discuss index rebuilds, update consistency, and backend-specific deletion support.
- Account for caches, replicas, snapshots, and retention separately from active search removal.

**Practice:** Insert, edit, and delete synthetic documents; verify that search returns current permitted content.

**Checkpoint:** Distinguish removal from active retrieval from complete deletion across all storage and backups.

<br/>

### 15. Semantic Search Testing and Evaluation

- Build representative queries with explicit document relevance judgments.
- Compare dense search with BM25 using the same corpus and query set.
- Introduce Precision@k, Recall@k, and ranking measures such as MRR where appropriate.
- Record latency, encoding runtime, index size, and failures.
- Evaluate authorization and lifecycle correctness separately from relevance.
- Change one factor at a time: model, passage size, metric, filter, or index configuration.
- Record incomplete relevance judgments and dataset limitations.

**Practice:** Analyze both paraphrase and exact-match failures and summarize measured trade-offs.

**Checkpoint:** Distinguish retrieval-quality metrics from generation quality and ANN neighbor recall.

**Depth boundary:** Larger datasets, nDCG, experiment tracking, and production evaluation are expanded in Level 13. A small evaluation baseline is required here.

<br/>

### 16. Practice and Revision

- Generate compatible document and query embeddings.
- Compare metrics, dense search, and BM25.
- Compare exact search and an approximate index where feasible.
- Apply metadata restrictions and server-enforced permissions.
- Test source updates and deletions.
- Complete the semantic-search prototype below.

**Checkpoint:** Explain why each result was eligible for retrieval and assess whether it is relevant.

<br/>

## Level deliverable: Evaluated semantic-search prototype

Build a small project and create `semantic_search_report.md` in this folder with:

1. A reproducible corpus of public or synthetic documents with stable IDs and metadata.
2. A documented embedding model, encoding conventions, dimensions, normalization, and similarity metric.
3. An exact dense-search baseline and a BM25 baseline on the same corpus.
4. One approximate index comparison if supported; explain any omission due to dataset size or environment limits.
5. At least ten representative queries with explicit relevant document IDs, including paraphrases, identifiers, and queries lacking relevant results.
6. Top-k relevance measurements and runtime/index-size measurements where available.
7. Metadata filters and two synthetic users with different retrieval permissions.
8. Tests for unauthorized retrieval, invalid vectors, document replacement, and deletion.
9. An experiment varying at least one model or retrieval configuration, with observed improvements and regressions.
10. A pipeline diagram, sample results, known limitations, and a recommendation for the preferred configuration.

A notebook or command-line tool is sufficient; a FastAPI search endpoint is optional. Local embedding models and open-source tools can support the core exercise without paid services. Label prepared vectors and estimates clearly rather than presenting them as observed model results.

<br/>

## Suggested format for each note

1. Learning objectives and prerequisite concepts.
2. Intuition and a concrete retrieval example.
3. Definitions, formulas, or data shapes where useful.
4. A small worked calculation or runnable implementation.
5. Configuration choices and backend-specific limitations.
6. Failure examples, trust boundaries, and trade-offs.
7. Exercise and revision questions with answers.
8. References and optional extensions.

Verify current embedding-model requirements and library/database APIs when writing implementation notes. Keep corpus preparation and evaluation reproducible.

<br/>

## Completion checklist

- [ ] Explain embeddings and their limitations.
- [ ] Generate compatible document and query vectors.
- [ ] Track dimensions and apply normalization correctly.
- [ ] Calculate and interpret similarity and distance metrics.
- [ ] Compare dense, lexical, and sparse retrieval.
- [ ] Build a BM25 baseline.
- [ ] Distinguish exact search, ANN neighbor recall, and relevance quality.
- [ ] Explain vector-index trade-offs and record configuration.
- [ ] Apply metadata filters and mandatory authorization checks.
- [ ] Distinguish FAISS-style indexing from vector-store/database responsibilities.
- [ ] Select an embedding model using representative query results.
- [ ] Verify updates, replacement, and deletion behavior.
- [ ] Complete and review the semantic-search prototype and report.

<br/>

## Scope and next step

This level focuses on retrieving relevant sources. Full document ingestion, advanced chunking, hybrid fusion, reranking, context selection, citations, and grounded answer generation are developed in Level 8. Comprehensive security and production operations are expanded in Levels 14–15.

Next: **Level 8 — Retrieval-Augmented Generation (RAG)** in the [main course outline](../README.md).
