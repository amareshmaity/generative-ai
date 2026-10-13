# Chapter 07 — BM25 as a Lexical Baseline

## Learning Objectives

By the end of this chapter, you should be able to:

- Prepare consistent text tokenization for documents and queries.
- Explain term frequency, inverse document frequency, and document-length normalization.
- Describe the BM25 parameters $k_1$ and $b$ conceptually.
- Recognize how stopwords, punctuation, language, and identifiers affect lexical retrieval.
- Retrieve top-$k$ results while preserving document IDs for comparison with dense retrieval.
- Explain vocabulary mismatch and the limitations of lexical matching.

<br/>

## 1. Why Use BM25?

BM25 is a widely used classical lexical ranking function. It scores documents based on how query terms occur in a document and how informative those terms are across the corpus. It is a strong baseline because it is comparatively straightforward to implement, inspect, and evaluate.

In an embedding-based search system, BM25 provides a useful point of comparison. A dense retriever may identify paraphrases, while BM25 may be especially effective when the query contains exact terms, product names, error codes, or technical identifiers.

The purpose of a baseline is not to prove that one approach is universally better. It is to establish a reproducible reference so that retrieval alternatives can be compared on the same corpus, queries, and relevance labels.

<br/>

## 2. How BM25 Works Conceptually

BM25 combines three important ideas:

1. **Term frequency (TF):** a query term appearing in a document can be evidence of relevance, although repeated occurrences have diminishing returns.
2. **Inverse document frequency (IDF):** a term that appears in fewer documents is generally more informative than a term that appears almost everywhere.
3. **Document-length normalization:** long documents have more opportunities to contain query terms, so BM25 adjusts for document length.

A commonly used form of the BM25 score is:

$$ \operatorname{BM25}(D,Q)= \sum_{t\in Q} \operatorname{IDF}(t) \cdot \frac{f(t,D)(k_1+1)} {f(t,D)+k_1\left(1-b+b\frac{|D|}{\operatorname{avgdl}}\right)} $$

Where:

* $D$: a document.
* $Q$: the query's terms.
* $t$: a query term.
* $f(t,D)$: the frequency of term $t$ in document $D$.
* $|D|$: the document length measured in tokens.
* $\operatorname{avgdl}$: average document length in the corpus.
* $k_1$: controls how quickly the contribution from repeated term occurrences saturates.
* $b$: controls the strength of document-length normalization.
* $\operatorname{IDF}(t)$: a weight reflecting how rare or informative term $t$ is in the corpus.


Implementations use slightly different IDF formulas and conventions. The equation above explains the core mechanism; use the selected library's documentation for its exact behavior.

<br/>

## 3. Term Frequency: More Matches, Diminishing Returns

Term frequency counts how often a term appears in a document. If the query contains `password`, a document that mentions `password` may be more relevant than one that never mentions it.

However, repeating a term 20 times should not necessarily make a document 20 times as relevant as one containing it once. BM25 uses a saturation function: additional occurrences can increase the score, but their contribution diminishes.

Example:

- Document A: “Reset your password.”
- Document B: “Password reset guide. Password recovery steps. Password support.”
- Document C: “Update your billing address.”

For a query containing `password`, A and B have lexical matches while C does not. BM25 considers more than the raw count: it also considers term rarity and document length.

<br/>

## 4. Inverse Document Frequency: How Informative Is a Term?

A term appearing in nearly every document usually provides little discrimination. A rare term may help distinguish a small set of documents.

For example, in a technical-support corpus:

- `the` may occur in many documents.
- `password` may occur in a smaller subset.
- `ERR_PAY_204` may occur in only a few documents.

IDF gives greater weight to terms that are rarer across the corpus, according to the implementation's formula. This can make exact error codes and specialized terms powerful retrieval signals.

Rarity does not guarantee relevance. A rare token can be noise, a typo, or an irrelevant identifier. BM25 ranks candidates; the application still needs evaluation and, where appropriate, validation.

<br/>

## 5. Document-Length Normalization

Long documents naturally contain more words and have more chances to match a query. BM25 adjusts term contributions based on the document length relative to the corpus average.

The $b$ parameter controls the strength of this adjustment:

- $b=0$: no document-length normalization in the standard formulation.
- $b=1$: full length normalization according to the standard formula.
- Values between 0 and 1: intermediate normalization.

The $k_1$ parameter controls term-frequency saturation. Higher values generally allow term frequency to continue influencing the score over a wider range before saturation. These parameters are often left at library defaults initially and tuned only when a representative evaluation set justifies it.

Do not assume that a particular parameter setting is optimal for every corpus. Document lengths, query types, tokenization, and relevance criteria all matter.

<br/>

## 6. Tokenization Is Part of the Retrieval Model

BM25 works on tokens, so preprocessing can change what matches. Apply a consistent, deliberate policy to both indexed documents and incoming queries.

### 6.1 Basic tokenization

A simple tokenizer might lowercase text and extract word-like sequences:

```python
import re

def tokenize(text: str) -> list[str]:
    return re.findall(r"\b\w+\b", text.lower())
```

This is a teaching example, not a universal production tokenizer. It can split or transform punctuation-bearing identifiers in ways that are undesirable. For example, `ERR-PAY-204`, `v1.2`, `C++`, and `foo.bar()` may need domain-specific handling.

<br/>

### 6.2 Stopwords

Stopwords are frequent terms such as “the,” “is,” or “and.” Some lexical pipelines remove them; others retain them and rely on term weighting to reduce their influence.

Do not remove stopwords automatically without considering the task. Words such as “not” can reverse meaning:

- “Allow access”
- “Do not allow access”

Removing `not` may harm retrieval quality.

<br/>

### 6.3 Punctuation and identifiers

Punctuation may be meaningful in technical text:

- `C++`
- `node.js`
- `v1.2.0`
- `ERR-PAY-204`
- `user_id`

A generic tokenizer can split these into different token sequences. Decide whether to preserve identifiers as single tokens, normalize them in a controlled way, or index both the original identifier and useful subparts. Apply the same policy to queries and documents.

For exact identifiers, consider retaining a normalized exact-match field in addition to full-text indexing. This is a design option to evaluate, not a requirement for every search system.

<br/>

### 6.4 Language-specific processing

Languages differ in word boundaries, morphology, script, and tokenization requirements. Whitespace splitting may work as a baseline for some text, but it is not suitable for every language.

Depending on the corpus, you may need language-aware tokenization, stemming, lemmatization, character n-grams, or other analysis. These transformations can improve matching, but they can also erase distinctions that matter. Evaluate them on queries from the actual target language and domain.

<br/>

## 7. Build a BM25 Baseline with `rank-bm25`

The following example uses the third-party `rank-bm25` package. Install it in your environment first:

```bash
pip install rank-bm25
```

This implementation uses a basic lowercase tokenizer. It is suitable for a small demonstration corpus; adapt the tokenizer before using technical identifiers or multilingual content in a real application.

```python
import re
from rank_bm25 import BM25Okapi

documents = [
    {
        "id": "doc_001",
        "text": "Reset a forgotten password using the account recovery page.",
    },
    {
        "id": "doc_002",
        "text": "Troubleshoot duplicate billing transactions and repeated charges.",
    },
    {
        "id": "doc_003",
        "text": "ERR_PAY_204 indicates that a payment retry failed.",
    },
    {
        "id": "doc_004",
        "text": "Change your subscription plan from account settings.",
    },
]

def tokenize(text: str) -> list[str]:
    return re.findall(r"\b\w+\b", text.lower())

tokenized_documents = [
    tokenize(document["text"])
    for document in documents
]

bm25 = BM25Okapi(tokenized_documents)

def search_bm25(query: str, top_k: int = 3):
    query_tokens = tokenize(query)
    scores = bm25.get_scores(query_tokens)

    ranked_indices = sorted(
        range(len(documents)),
        key=lambda i: scores[i],
        reverse=True,
    )[:top_k]

    return [
        {
            "id": documents[i]["id"],
            "text": documents[i]["text"],
            "bm25_score": float(scores[i]),
        }
        for i in ranked_indices
    ]

for result in search_bm25("duplicate charge billing", top_k=3):
    print(result)
```

<br/>

### Important implementation details

- Document IDs are stored separately from tokenized text.
- The BM25 index is built once for this fixed corpus.
- Queries use the same tokenizer as documents.
- Results include stable IDs so they can be compared with dense-search results.
- Scores are sorted in descending order because larger BM25 scores indicate stronger lexical matches within this scoring setup.

The example does not include production concerns such as persistence, concurrent updates, access-control filtering, language-specific analyzers, or large-corpus performance.

<br/>

## 8. Preserve IDs for Dense-vs-BM25 Comparisons

A fair comparison requires both retrievers to search the same logical corpus. Keep stable document IDs and metadata separate from the representation used by each index.

```python
corpus = [
    {
        "id": "doc_001",
        "text": "Reset a forgotten password using account recovery.",
        "metadata": {"category": "account"},
    },
    {
        "id": "doc_002",
        "text": "Resolve duplicate billing transactions.",
        "metadata": {"category": "billing"},
    },
]
```

Use the same IDs for:

- The BM25 document collection.
- The dense embedding records.
- Relevance judgments for each query.
- Evaluation output and failure analysis.

If a dense retriever returns `doc_002` and BM25 returns `doc_001`, the IDs let you compare their rankings directly. Do not compare raw BM25 scores with cosine similarity or dot-product scores: they have different scales and meanings.

<br/>

## 9. Vocabulary Mismatch and Other Limitations

BM25 is a lexical method. It can rank documents well when important query terms appear in the documents, but it does not inherently understand that two different expressions have the same meaning.

Example:

- Query: “How can I get my money back?”
- Relevant document: “Refund eligibility and reimbursement procedure.”

The document may be relevant despite limited exact term overlap. Depending on the tokenizer and query, BM25 may rank it below a less relevant document that repeats “money” or “back.”

Other limitations include:

- **Synonyms:** `car` and `automobile` may not match without expansion or additional indexing.
- **Morphology:** related word forms may be treated differently unless processing handles them.
- **Tokenization errors:** important identifiers can be split inconsistently.
- **Ambiguous terms:** a lexical match can occur in an irrelevant context.
- **Rare-token noise:** an unusual term may be highly weighted but not useful.
- **Language differences:** one tokenizer configuration may not work well across all languages.

These limitations make BM25 a valuable baseline rather than a universal solution. Dense retrieval, learned sparse retrieval, query expansion, or hybrid retrieval may help with some failure modes, but improvements must be measured.

<br/>

## 10. Practice

### Exercise A — Build the baseline

Use the same corpus and stable document IDs as your dense-search experiment.

1. Tokenize each document consistently.
2. Build a BM25 index.
3. Run at least 10 representative queries.
4. Retrieve top-5 results for each query.
5. Save the query, ranked document IDs, and BM25 scores.

<br/>

### Exercise B — Compare query types

Include at least:

- A paraphrase query.
- A query containing an exact error code.
- A product or API identifier.
- A query with a negation such as “do not allow access.”
- A query with a synonym not used in the relevant document.

Before running each query, predict whether BM25 will perform well and explain why. Then compare the prediction with the results.

<br/>

### Exercise C — Compare with dense retrieval

For each query:

1. Run dense retrieval and BM25 over the same corpus.
2. Compare the top-$k$ document IDs and their relevance labels.
3. Record which relevant documents each method missed.
4. Calculate a metric such as Recall@5.
5. Inspect examples where the methods disagree.

Compare relevance and ranking quality—not the numerical magnitude of a BM25 score against an embedding similarity score.

<br/>

### Exercise D — Test tokenization

Create a small test set containing `ERR-PAY-204`, `v1.2.0`, `C++`, and `node.js`. Inspect the output of your tokenizer. Decide whether each identifier should remain intact, be normalized, or be represented through both exact and component tokens.

<br/>

## 11. Common Mistakes

- **Using different preprocessing for documents and queries:** this can prevent terms from matching.
- **Assuming lowercase tokenization is enough:** technical identifiers and multilingual text may require custom handling.
- **Removing all stopwords blindly:** negation and other task-critical terms may be lost.
- **Comparing raw BM25 scores with dense scores:** these scores are not on a common scale.
- **Changing the corpus between experiments:** this makes comparisons unreliable.
- **Ignoring stable IDs:** without shared IDs, relevance judgments and ranking comparisons become error-prone.
- **Assuming BM25 understands meaning:** lexical overlap is not semantic understanding.

<br/>

## 12. References and Optional Extensions

- Read the documentation for the BM25 implementation you select; implementations can differ in tokenization assumptions, IDF formulation, defaults, and API.
- Review the documentation for your dense-search library to ensure that both retrievers use the same document IDs and corpus version.
- Optional extension: compare the default BM25 parameters with one alternative configuration on a fixed relevance-labeled query set.

<br/>

## Checkpoint

You should be able to explain:

- How term frequency, inverse document frequency, and document-length normalization contribute to BM25.
- What $k_1$ and $b$ control conceptually.
- Why consistent tokenization is required for documents and queries.
- Why punctuation, stopwords, language, and identifiers need deliberate preprocessing decisions.
- How to retrieve top-$k$ results while preserving stable document IDs.
- Why BM25 can struggle with vocabulary mismatch.
- Why dense and BM25 retrieval should be compared using the same queries, corpus, IDs, and relevance labels—not by directly comparing raw scores.
