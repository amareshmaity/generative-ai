# 08. RAG Retrieval Metrics

## Learning Objectives

By the end of this chapter, you should be able to:

-   Define relevance judgments, ranked results, cutoffs, and duplicate
    handling.
-   Calculate Precision@k and Recall@k with explicit denominators.
-   Explain reciprocal rank and Mean Reciprocal Rank (MRR) for finding
    the first relevant result.
-   Calculate Discounted Cumulative Gain (DCG) and normalized DCG (nDCG)
    using a stated graded-relevance convention and ideal ranking.
-   Discuss incomplete judgments, queries with no relevant documents,
    and document-versus-passage granularity.
-   Distinguish retrieval relevance metrics from
    approximate-nearest-neighbor (ANN) agreement with exact neighbors.

<br/>

## 1. What Retrieval Metrics Measure

In retrieval-augmented generation (RAG), retrieval selects documents or
passages that may help answer a query. Retrieval metrics evaluate the
retrieved and ranked items against relevance judgments. They do **not**
directly establish whether the final generated answer is correct,
faithful, or useful; those are separate evaluation dimensions.

A typical retrieval pipeline is:

``` mermaid
flowchart TD
    A[User query] --> B[Retriever]
    B --> C[Ranked documents or passages]
    C --> D[Compare with relevance judgments]
    D --> E[Compute retrieval metrics]
    C --> F[Context selection]
    F --> G[Answer generation]
    G --> H[Evaluate answer separately]
```

The retrieval evaluation must specify what counts as a relevant item,
which items were eligible to be retrieved, how ranking cutoffs are
chosen, and how duplicates are handled.

<br/>

## 2. Relevance Judgments and Ranked Results

### 2.1 Relevance judgments

A relevance judgment is a label assigned to a document or passage for a
particular query. Judgments may be binary or graded.

-   **Binary relevance:** relevant (`1`) or not relevant (`0`).
-   **Graded relevance:** a score such as `0`, `1`, `2`, or `3`, where
    larger values mean greater usefulness.

Relevance is query-dependent. A document about database indexes may be
relevant to "How do B-tree indexes speed up queries?" but irrelevant to
"How do I configure an API timeout?"

Judgments should follow a written rubric. For example:

| Grade | Example interpretation                   |
| ----- | ---------------------------------------- |
| 0     | Not relevant to the query                |
| 1     | Tangentially related; little direct help |
| 2     | Relevant and useful, but incomplete      |
| 3     | Highly relevant and directly useful      |


This is only one possible rubric. Define the convention before computing
metrics, and use it consistently.

<br/>

### 2.2 Ranked results

A retriever returns a ranked list:

$$
R_q = [d_1, d_2, \ldots, d_n]
$$

where (d_1) is the highest-ranked result for query (q). A cutoff (k)
means the metric considers only the first (k) results, or all available
results if fewer than (k) are returned.

Choose (k) based on the application. If the answer generator receives
only five passages, metrics at 5 may be more actionable than metrics at
20. It can still be useful to report several cutoffs, such as `@1`,
`@3`, `@5`, and `@10`.

<br/>

### 2.3 Duplicate handling

Duplicates can distort metrics if repeated copies of the same content
occupy multiple ranks.

Before evaluation, define whether an item is a document, passage, chunk,
or canonical source. Possible policies:

-   **Deduplicate by canonical document ID:** multiple passages from one
    document count as one document.
-   **Evaluate passages independently:** distinct chunks are separate
    items, even when they come from the same document.
-   **Collapse exact duplicates:** repeated copies of the same chunk
    count once.
-   **Keep overlapping chunks:** when overlap is part of the deployed
    system, evaluate them as returned but also measure redundancy if it
    matters.

The policy must match the application's retrieval unit. Do not
deduplicate after seeing results unless the policy was predeclared.

<br/>

## 3. Precision@k

Precision@k measures the fraction of the top-(k) retrieved items that
are relevant.

$$
\mathrm{Precision@k} = \frac{\text{Relevant items among the first } k}{\text{Number of items actually evaluated in the top-}k}
$$

If the retriever returns at least (k) items, the denominator is usually
(k). If it returns fewer than (k), state whether the denominator is the
number actually returned or whether missing slots are treated as
non-relevant. For most practical reporting, use the number actually
returned and record the short result list; for fixed-depth retrieval
contracts, missing slots may instead count as failures.

**Example:** The top five results contain three relevant items.

$$
\mathrm{Precision@5} = \frac{3}{5} = 0.60
$$

Interpretation: 60% of the five retrieved results are relevant.
Precision@k is useful when irrelevant context consumes a limited prompt
budget or distracts the generator.

<br/>

## 4. Recall@k

Recall@k measures the fraction of all known relevant items that appear
in the top (k).

$$
\mathrm{Recall@k} = \frac{\text{Relevant items among the first } k}{\text{Total relevant items for the query in the evaluation corpus}}
$$

The denominator is not the number retrieved. It is the total number of
relevant items judged to exist in the defined corpus for that query.

**Example:** There are eight known relevant passages in the corpus, and
three appear in the top five.

$$
\mathrm{Recall@5} = \frac{3}{8} = 0.375
$$

Interpretation: the retriever found 37.5% of the known relevant passages
in the first five results.

Recall is only as reliable as the relevance judgments and the corpus
boundary. If the set of relevant items is incomplete, the denominator
may be too small and recall may be overstated.

<br/>

## 5. Reciprocal Rank and Mean Reciprocal Rank

Reciprocal Rank (RR) evaluates the rank of the **first relevant
result**.

$$
\mathrm{RR}(q) =
\begin{cases}
\frac{1}{r_q}, & \text{if the first relevant result is at rank } r_q \\
0, & \text{if no relevant result is found within the evaluated ranking}
\end{cases}
$$

Examples:

-   First relevant result at rank 1: RR = 1.
-   First relevant result at rank 2: RR = 0.5.
-   First relevant result at rank 4: RR = 0.25.
-   No relevant result in the evaluated list: RR = 0.

Mean Reciprocal Rank averages RR across a set of queries:

$$
\mathrm{MRR} = \frac{1}{|Q|} \sum_{q \in Q} \mathrm{RR}(q)
$$

MRR is useful when quickly surfacing at least one useful result is the
primary goal, such as finding the correct support article. It ignores
additional relevant results after the first one, so it is not a
substitute for recall or graded-ranking metrics.

For queries with no relevant documents in the corpus, define the policy
explicitly. Commonly, such a query receives RR = 0 if the evaluation
asks whether retrieval found a relevant item, but it may be excluded
from some analyses if the task definition says it is unanswerable.
Report the number of such queries and the chosen policy.

<br/>

## 6. DCG and nDCG for Graded Relevance

Precision and recall treat relevance as binary. When relevance has
degrees, Discounted Cumulative Gain (DCG) rewards highly relevant items
near the top of the ranking.

One common convention is:

$$
\mathrm{DCG@k} = \sum_{i=1}^{k} \frac{2^{\mathrm{rel}_i}-1}{\log_2(i+1)}
$$

where (rel_i) is the graded relevance of the item at rank (i). The
logarithmic discount reduces the contribution of items lower in the
ranking.

Another convention uses (rel_i / `\log`{=tex}\_2(i+1)). Both conventions
appear in practice; never compare DCG values across systems unless the
same gain and discount convention is used.

<br/>

### Worked DCG example

Use grades `0–3` and the gain (2\^{rel}-1). Suppose the ranked grades
are:

$$
[3, 2, 0]
$$

Then:

$$
\mathrm{DCG@3} = \frac{2^3-1}{\log_2(2)} + \frac{2^2-1}{\log_2(3)} + \frac{2^0-1}{\log_2(4)}
$$

$$
= 7 + \frac{3}{1.585} + 0 \approx 8.893
$$

<br/>

### Ideal DCG and nDCG

Ideal DCG (IDCG@k) is the DCG of the best possible ranking of the same
judged items, sorted by decreasing relevance. Normalized DCG is:

$$
\mathrm{nDCG@k} = \frac{\mathrm{DCG@k}}{\mathrm{IDCG@k}}
$$

When IDCG@k is zero because no judged item has positive relevance, nDCG
is mathematically undefined. Decide whether to report it as `N/A`,
exclude that query from the nDCG average while reporting the excluded
count, or apply another documented policy. Do not silently convert an
undefined value to 1.

**Example:** If DCG@3 = 8.893 and IDCG@3 = 9.631:

$$
\mathrm{nDCG@3} \approx 0.923
$$

This indicates that the ranking achieved about 92.3% of the ideal DCG
under the selected relevance grades and gain convention.

<br/>

## 7. Tiny Ranked-List Example: Compute by Hand

Suppose a query has four known relevant passages in the evaluation
corpus. The retriever returns these results:

| Rank | Passage | Relevance grade | Binary relevant? |
| ---- | ------- | --------------- | ---------------- |
| 1    | P-A     | 3               | Yes              |
| 2    | P-B     | 0               | No               |
| 3    | P-C     | 2               | Yes              |
| 4    | P-D     | 1               | Yes              |

Assume the relevant set contains four passages total, including P-A,
P-C, P-D, and one passage not retrieved.

At (k=3):

-   Relevant items in top 3: 2.
-   Precision@3: (2/3 `\approx 0.667`{=tex}).
-   Recall@3: (2/4 = 0.5).
-   First relevant result is rank 1, so RR = 1.

At (k=4):

-   Relevant items in top 4: 3.
-   Precision@4: (3/4 = 0.75).
-   Recall@4: (3/4 = 0.75).

For $\mathrm{DCG@3}$ with grades $[3, 0, 2]$ and the gain $(2^{\mathrm{rel}} - 1)$:

$$
\mathrm{DCG@3} = 7 + \frac{0}{\log_2(3)} + \frac{3}{\log_2(4)} = 7 + 1.5 = 8.5
$$

The ideal top-three grades are $[3, 2, 1]$:

$$
\mathrm{IDCG@3} = 7 + \frac{3}{\log_2(3)} + \frac{1}{\log_2(4)} \approx 9.393
$$

$$
\mathrm{nDCG@3} \approx \frac{8.5}{9.393} \approx 0.905
$$

These calculations use binary relevance for Precision/Recall/RR and
graded relevance for DCG/nDCG. State this distinction in reports.

<br/>

## 8. Mean Metrics Across Queries

Compute a metric per query first, then aggregate according to the chosen
policy.

For query-level Precision@k:

$$
\mathrm{Mean\ Precision@k} = \frac{1}{|Q|} \sum_{q \in Q} \mathrm{Precision@k}(q)
$$

This is a macro average across queries. It gives each query equal
weight. Other aggregation choices may weight by number of relevant items
or by business importance, but the policy must be explicit.

Report more than a single mean when useful:

-   Number of queries evaluated.
-   Mean and median.
-   Distribution or confidence interval.
-   Results by query category, difficulty, or source.
-   Count of queries with no known relevant items.
-   Count of queries with incomplete relevance judgments.

Do not average raw DCG values across queries as if they were normalized;
nDCG is often more comparable across queries with different relevance
distributions, provided the same conventions and policies are used.

<br/>

## 9. Incomplete Judgments and Queries with No Relevant Documents

### Incomplete relevance judgments

In many test collections, only a subset of corpus items has been judged.
A result labeled "not relevant" may actually be **unjudged**, not truly
irrelevant.

Possible policies:

-   **Pool and judge:** collect top results from multiple retrievers,
    then label the union.
-   **Treat unjudged as non-relevant:** simple, but can penalize systems
    retrieving novel useful items.
-   **Report judged-only metrics:** use only judged results, while
    carefully documenting the changed denominator.
-   **Human-review a sample of unjudged results:** estimate how often
    unjudged items are actually relevant.

Do not conflate "not relevant" with "not judged." Store separate states
when the dataset supports them.

<br/>

### Queries with no relevant items

If a query has no relevant items in the defined corpus:

-   Recall@k has a zero denominator and is undefined.
-   nDCG@k is undefined if IDCG@k = 0.
-   Precision@k can still be calculated, with zero relevant items in the
    retrieved list yielding 0 if results are returned.
-   RR is commonly 0 if no relevant item is found, but the policy
    depends on whether the query is expected to be answerable.

Report the number of such queries and the handling policy. For a RAG
assistant, an unanswerable query may require abstention rather than
retrieval of superficially related material.

<br/>

## 10. Document Versus Passage Granularity

Retrieval may return whole documents or chunks/passages. Metrics depend
on the evaluation unit.

-   **Document-level relevance:** a document counts as relevant if it
    contains information that answers the query under the rubric.
-   **Passage-level relevance:** an individual chunk must contain
    sufficient relevant evidence.
-   **Parent-document aggregation:** several relevant passages from one
    document may count as one relevant source, if the application
    consumes or displays documents.
-   **Chunk-level retrieval:** relevant overlapping chunks may be
    distinct retrieval units, but duplicates and overlap can inflate
    counts.

Choose the unit that matches the application interface and downstream
context assembly. If the generator consumes passages, passage-level
metrics are often diagnostic. If the application displays sources as
documents, document-level metrics may better reflect user experience.
When both matter, report both.

<br/>

## 11. Relevance Metrics Versus ANN Neighbor Agreement

Approximate nearest neighbor (ANN) indexes speed up vector search by
returning approximate neighbors rather than exhaustively scoring every
vector. ANN evaluation asks whether the approximate index retrieves the
same neighbors as an exact vector search.

This is not the same as semantic relevance evaluation.

| Evaluation                       | Comparison                                           | What it measures                      |
| -------------------------------- | ---------------------------------------------------- | ------------------------------------- |
| Retrieval relevance              | Retrieved items vs human/task relevance judgments    | Whether results help answer the query |
| ANN recall\@k / neighbor overlap | Approximate top-k neighbors vs exact top-k neighbors | Agreement with exact vector search    |
| End-to-end RAG quality           | Generated answer vs task/evidence criteria           | Whether the full system answers well  |


An ANN index can perfectly reproduce exact vector neighbors while
retrieving semantically irrelevant content because the embedding model
or query representation is poor. Conversely, an ANN index may miss some
exact neighbors but still return relevant passages that support the
answer. Keep index approximation quality and task relevance separate.

<br/>

## 12. Python Example: Compute Retrieval Metrics

The following example calculates binary Precision@k, Recall@k,
Reciprocal Rank, DCG@k, and nDCG@k for a single ranked list. It assumes
a complete relevance set and unique passage IDs. It is a small reference
implementation, not a production evaluation framework.

``` python
from math import log2

def precision_at_k(ranked_ids, relevant_ids, k):
    top_k = ranked_ids[:k]
    if not top_k:
        return 0.0
    return sum(item in relevant_ids for item in top_k) / len(top_k)

def recall_at_k(ranked_ids, relevant_ids, k):
    if not relevant_ids:
        return None  # undefined: zero relevant items in the corpus
    top_k = ranked_ids[:k]
    return sum(item in relevant_ids for item in top_k) / len(relevant_ids)

def reciprocal_rank(ranked_ids, relevant_ids, k=None):
    results = ranked_ids if k is None else ranked_ids[:k]
    for rank, item in enumerate(results, start=1):
        if item in relevant_ids:
            return 1.0 / rank
    return 0.0

def dcg_at_k(ranked_ids, relevance_grades, k):
    grades = [relevance_grades.get(item, 0) for item in ranked_ids[:k]]
    return sum((2**grade - 1) / log2(rank + 1)
               for rank, grade in enumerate(grades, start=1))

def ndcg_at_k(ranked_ids, relevance_grades, k):
    actual = dcg_at_k(ranked_ids, relevance_grades, k)
    ideal_ids = sorted(
        relevance_grades,
        key=lambda item: relevance_grades[item],
        reverse=True
    )[:k]
    ideal = dcg_at_k(ideal_ids, relevance_grades, k)
    if ideal == 0:
        return None  # undefined; report this case explicitly
    return actual / ideal

ranked = ["P-A", "P-B", "P-C", "P-D"]
relevant = {"P-A", "P-C", "P-D", "P-E"}
grades = {"P-A": 3, "P-B": 0, "P-C": 2, "P-D": 1, "P-E": 2}

k = 3
print("Precision@3:", precision_at_k(ranked, relevant, k))
print("Recall@3:", recall_at_k(ranked, relevant, k))
print("RR@3:", reciprocal_rank(ranked, relevant, k))
print("DCG@3:", round(dcg_at_k(ranked, grades, k), 3))
print("nDCG@3:", round(ndcg_at_k(ranked, grades, k), 3))
```

Implementation notes:

-   The example treats an item as binary relevant if its ID is in
    `relevant`; graded relevance is supplied separately for DCG/nDCG.
-   The denominator for Recall@k is the number of known relevant IDs,
    not the number retrieved.
-   This simple code does not deduplicate IDs. If duplicates can occur,
    define a policy and canonicalize or deduplicate before metric
    computation.
-   For multiple queries, compute per-query metrics first and then
    aggregate.
-   The example assumes the judgments are complete; production
    evaluations should represent unjudged items separately.

<br/>

## 13. Practice: Compute Metrics by Hand and with Code

Use the ranked list and relevance judgments from Section 7.

-   Ranked results: `P-A, P-B, P-C, P-D`
-   Binary relevant set: `P-A, P-C, P-D, P-E`
-   Graded relevance: `P-A: 3`, `P-B: 0`, `P-C: 2`, `P-D: 1`, `P-E: 2`

Tasks:

1.  Calculate Precision@3 and Recall@3.
2.  Calculate RR@3 and explain why it does not reward the second
    relevant result.
3. Calculate $\mathrm{DCG@3}$ using gain $(2^{\mathrm{rel}} - 1)$ and discount $(\log_2(i+1))$.
4.  Sort the judged items by grade to calculate IDCG@3, then calculate
    nDCG@3.
5.  Explain how the result would change if `P-C` and `P-D` were
    duplicate chunks that should count as one canonical document.
6.  Explain why ANN neighbor agreement with exact search does not prove
    that retrieved items are relevant.

<br/>

### Practice answer key

1. Top three are `P-A`, `P-B`, `P-C`. Two are relevant, so $\mathrm{Precision@3} = 2/3 \approx 0.667$. Four items are known relevant (`P-A`, `P-C`, `P-D`, `P-E`), so $\mathrm{Recall@3} = 2/4 = 0.5$.
2. The first relevant result is rank 1, so $\mathrm{RR@3} = 1$. RR only considers the first relevant item; it ignores later relevant results.
3. Grades are `[3, 0, 2]`. $\mathrm{DCG@3} = 7 + 0 + 3/\log_2(4) = 8.5$.
4. Ideal top-three grades are `[3, 2, 2]`, so $\mathrm{IDCG@3} = 7 + 3/\log_2(3) + 3/\log_2(4) \approx 10.393$. Thus $\mathrm{nDCG@3} \approx 8.5 / 10.393 \approx 0.818$. The ideal ranking uses the highest three grades among all judged items, including `P-E`.

5.  If duplicates are collapsed at document level, map chunks to
    canonical document IDs and recompute the ranking and relevance set
    at that same granularity. The numerator and denominator may both
    change; do not merely remove one result while leaving the relevance
    denominator unchanged.
6.  Exact-neighbor agreement measures approximation fidelity to the
    embedding search, not task-level relevance. A poor embedding
    representation can return irrelevant exact neighbors.

<br/>

## 14. Checkpoint

**Prompt:** Choose retrieval metrics that reflect the application's
actual retrieval needs.

**Model answer:**

Choose metrics based on how retrieval is used downstream. Use
Precision@k when the context budget is tight and irrelevant results are
costly; Recall@k when missing any required evidence is costly; MRR when
finding the first useful result quickly is the primary objective; and
nDCG@k when graded relevance and ranking position both matter. Specify
relevance labels, the evaluation unit, cutoff, duplicate policy,
unjudged-item handling, and queries with no relevant documents before
computing results. Evaluate ANN neighbor agreement separately from
semantic relevance, and evaluate the generated answer separately from
retrieval.

<br/>

## 15. Further Reading

-   [Stanford Information Retrieval Book: Evaluation in Information
    Retrieval](https://nlp.stanford.edu/IR-book/html/htmledition/evaluation-in-information-retrieval-1.html)
    --- core retrieval evaluation concepts.
-   [scikit-learn ranking
    metrics](https://scikit-learn.org/stable/modules/model_evaluation.html)
    --- reference documentation for evaluation metrics.
-   [BEIR benchmark](https://github.com/beir-cellar/beir) ---
    heterogeneous information retrieval benchmark and evaluation
    tooling.
-   [RAGAS documentation](https://docs.ragas.io/) --- RAG evaluation
    concepts and metrics.
-   [FAISS documentation](https://github.com/facebookresearch/faiss) ---
    vector similarity search and index evaluation context.


<br/>


## Chapter Summary

Retrieval metrics quantify different ranking needs. Precision@k measures
the usefulness of returned items, Recall@k measures coverage of known
relevant items, MRR rewards finding the first relevant result early, and
nDCG evaluates ranked results using graded relevance. Reliable
measurement requires explicit relevance judgments, denominators,
cutoffs, duplicate and granularity policies, and treatment of unjudged
or unanswerable queries. ANN agreement with exact neighbors is an
index-quality measure, not proof of semantic relevance or good final
answers.
