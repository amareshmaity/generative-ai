# Chapter 05 — Similarity and Distance Metrics

## Learning Objectives

By the end of this chapter, you should be able to:

- Calculate cosine similarity, dot product, and Euclidean distance.
- Distinguish similarity scores (larger is generally better) from distances (smaller is generally better).
- Explain why cosine similarity, dot product, and Euclidean distance produce equivalent rankings for unit-normalized vectors.
- Explain how vector magnitude affects an unnormalized dot product.
- Select a metric that is compatible with the embedding model and vector index.
- Explain why a similarity score is not a calibrated probability or a universal relevance threshold.

<br/>

## 1. Why Metrics Matter

An embedding model maps text to vectors. A retrieval system needs a rule for comparing a query vector with document vectors and ranking the candidates.

For example, suppose the query is:

> How can I reset my account password?

A corpus might contain:

- Document A: “Steps to change a forgotten password”
- Document B: “How to update a billing address”
- Document C: “Password-reset troubleshooting”

The metric assigns a numerical comparison between the query vector and each document vector. The retrieval system then ranks the documents using those values.

The metric does **not** decide relevance independently of the embedding model. Rankings depend on the model, the vectors it produces, preprocessing, and the metric used.

<br/>

## 2. Three Common Metrics

Let the query embedding be $q$ and a document embedding be $d$, each with $n$ components.

### 2.1 Dot product

The dot product multiplies corresponding components and sums the results:

$$ q \cdot d = \sum_{i=1}^{n} q_i d_i $$

Example:

$$ q=[1,2], \qquad d=[3,4] $$

$$ q \cdot d = (1)(3)+(2)(4)=11 $$


**Interpretation:** For unnormalized vectors, the score depends on both vector direction and magnitude. A vector with a larger magnitude can receive a larger dot-product score even if its direction is not the closest.

Dot product is often appropriate when the embedding model and its retrieval guidance are designed for dot-product scoring. Do not assume that it is interchangeable with cosine similarity for arbitrary, unnormalized embeddings.

<br/>

### 2.2 Cosine similarity

Cosine similarity compares the angle between two nonzero vectors:

$$ \operatorname{cosine}(q,d)= \frac{q\cdot d}{\lVert q\rVert_2\lVert d\rVert_2} $$

where the L2 norm is:

$$ \lVert q\rVert_2=\sqrt{\sum_{i=1}^{n}q_i^2} $$

Using the previous vectors:

$$ q=, \qquad d= $$

Their dot product is $11$, and their norms are:

$$ \lVert q\rVert_2=\sqrt{5}, \qquad \lVert d\rVert_2=5 $$

Therefore:

$$ \operatorname{cosine}(q,d)=\frac{11}{5\sqrt{5}}\approx 0.984 $$

Cosine similarity is commonly between $-1$ and $1$ for real-valued, nonzero vectors:

* Near $1$: vectors point in similar directions.
* Near $0$: vectors are orthogonal.
* Near $-1$: vectors point in opposite directions.


These are geometric interpretations, not guaranteed labels for semantic relevance. The score distribution depends on the embedding model and data.

**Important:** Cosine similarity is undefined when either vector has zero norm. Validate embeddings before calculating it.

<br/>

### 2.3 Euclidean distance (L2 distance)

Euclidean distance measures the straight-line distance between two vectors:

$$ d_2(q,d)=\lVert q-d\rVert_2 =\sqrt{\sum_{i=1}^{n}(q_i-d_i)^2} $$

For:

$$ q=, \qquad d= $$

$$ d_2(q,d)=\sqrt{(1-3)^2+(2-4)^2} =\sqrt{8}\approx 2.828 $$


**Interpretation:** A smaller distance means the vectors are closer in the embedding space. Euclidean distance is nonnegative and equals zero when the vectors are identical.

<br/>

## 3. Similarity Scores vs. Distances

| Metric | What it returns | Better ranking direction | Magnitude-sensitive? |
|---|---|---|---|
| Dot product | Similarity score | Larger is better | Yes, unless vector norms are fixed |
| Cosine similarity | Directional similarity | Larger is better | No; vector magnitudes are divided out |
| Euclidean distance | Distance | Smaller is better | Yes |

Do not reverse the sorting direction accidentally. A retrieval implementation that sorts Euclidean distances in descending order returns the farthest candidates first.

Some vector databases expose a “distance” field even when the configured index uses a transformed score. Check the backend's documented semantics rather than assuming all returned numbers are directly comparable.

<br/>

## 4. Why Unit Normalization Changes the Relationship
L2 normalization converts a nonzero vector $x$ into a unit vector:

$$ \hat{x}=\frac{x}{\lVert x\rVert_2} $$

A unit vector has norm $1$.

For unit-normalized query and document vectors:

$$ \hat{q}\cdot\hat{d} =\operatorname{cosine}(\hat{q},\hat{d}) $$

So **dot product and cosine similarity return the same score** for unit-normalized vectors.

Euclidean distance is related to the same score:

$$ \lVert\hat{q}-\hat{d}\rVert_2^2 = \lVert\hat{q}\rVert_2^2+\lVert\hat{d}\rVert_2^2 -2(\hat{q}\cdot\hat{d}) $$

Because both norms equal $1$:

$$ \lVert\hat{q}-\hat{d}\rVert_2^2 =2-2\operatorname{cosine}(\hat{q},\hat{d}) $$

Equivalently:

$$ d_2(\hat{q},\hat{d})=\sqrt{2-2\operatorname{cosine}(\hat{q},\hat{d})} $$

This is a monotonic relationship: as cosine similarity increases, Euclidean distance decreases. Therefore, for the same set of unit-normalized vectors, all three metrics produce the same ranking, assuming exact calculations and consistent tie handling.

They do **not** produce the same numerical values or units.

<br/>

## 5. When Rankings Differ

### 5.1 Unnormalized vectors

Consider query vector $q=[1,0]$ and two documents:

- $A=[2,0]$
- $B=[1,1]$

| Candidate | Dot product | Cosine similarity | Euclidean distance |
|---|---:|---:|---:|
| A | 2 | 1.000 | 1.000 |
| B | 1 | 0.707 | 1.000 |

The dot product prefers A. Cosine similarity also prefers A. Euclidean distance ties them in this example.

Now consider $A=[10,1]$ and $B=[1,0.5]$, with the same query $q=[1,0]$:

| Candidate | Dot product | Cosine similarity | Euclidean distance |
|---|---:|---:|---:|
| A | 10 | $10/\sqrt{101}\approx0.995$ | $\sqrt{82}\approx9.055$ |
| B | 1 | $1/\sqrt{1.25}\approx0.894$ | $\sqrt{0.25}=0.5$ |


Here, dot product and cosine prefer A, while Euclidean distance prefers B. The vectors are not normalized, so the metrics respond differently to magnitude and absolute coordinate differences.

<br/>

### 5.2 What this means in practice

Rankings can differ when:

- Document vectors have different norms.
- Query and document vectors are normalized inconsistently.
- The model expects a particular similarity function but another is configured.
- The vector index implements a transformed distance or approximation.
- Numerical precision or approximate-neighbor search changes close results.

Use the embedding model's documented retrieval instructions and the vector store's metric configuration. Keep the query and document embedding pipelines compatible.

<br/>

## 6. Runnable Python Example

This example uses NumPy to compare the metrics for a small, illustrative corpus. The vectors are hand-authored toy values, not real embeddings from a trained model.

```python
import numpy as np

query = np.array([1.0, 0.0])

documents = {
    "doc_A": np.array([10.0, 1.0]),
    "doc_B": np.array([1.0, 0.5]),
    "doc_C": np.array([0.0, 2.0]),
}


def cosine_similarity(a, b):
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)

    if norm_a == 0 or norm_b == 0:
        raise ValueError("Cosine similarity is undefined for zero vectors.")

    return float(np.dot(a, b) / (norm_a * norm_b))


def dot_product(a, b):
    return float(np.dot(a, b))


def euclidean_distance(a, b):
    return float(np.linalg.norm(a - b))


def l2_normalize(vector):
    norm = np.linalg.norm(vector)
    if norm == 0:
        raise ValueError("Cannot L2-normalize a zero vector.")
    return vector / norm


def rank_scores(score_fn, *, higher_is_better):
    scores = {
        doc_id: score_fn(query, vector)
        for doc_id, vector in documents.items()
    }
    return sorted(
        scores.items(),
        key=lambda item: item[1],
        reverse=higher_is_better,
    )


print("Unnormalized dot product:")
print(rank_scores(dot_product, higher_is_better=True))

print("Unnormalized cosine similarity:")
print(rank_scores(cosine_similarity, higher_is_better=True))

print("Unnormalized Euclidean distance:")
print(rank_scores(euclidean_distance, higher_is_better=False))

normalized_query = l2_normalize(query)
normalized_documents = {
    doc_id: l2_normalize(vector)
    for doc_id, vector in documents.items()
}

print("\\nNormalized rankings:")
for name, score_fn, higher_is_better in [
    ("dot product", dot_product, True),
    ("cosine similarity", cosine_similarity, True),
    ("Euclidean distance", euclidean_distance, False),
]:
    scores = {
        doc_id: score_fn(normalized_query, vector)
        for doc_id, vector in normalized_documents.items()
    }
    ranking = sorted(
        scores.items(),
        key=lambda item: item[1],
        reverse=higher_is_better,
    )
    print(name, ranking)
```

Expected observations:

- The unnormalized rankings may differ.
- After L2 normalization, the rankings should agree apart from ties and floating-point effects.
- Euclidean distance is sorted ascending; dot product and cosine similarity are sorted descending.

<br/>

## 7. Scores Are Not Probabilities

A cosine similarity of `0.82` does **not** mean an 82% probability that a document is relevant. Likewise, a dot product of `14.0` is not a probability.

A metric is a geometric comparison, not automatically a calibrated estimate of relevance. Scores depend on factors such as:

- The embedding model and its training objective.
- The domain and language of the corpus.
- Query phrasing and document content.
- Vector normalization and the selected metric.
- The distribution of candidates in the index.

There is no universal cutoff such as “cosine similarity above 0.75 is relevant” that works for every model and dataset. A threshold should be selected using representative queries, relevance judgments, and the cost of false positives versus false negatives.

For a small retrieval prototype, inspect ranked results and calculate retrieval metrics such as Recall@K or MRR using labeled examples. Threshold calibration, reranking, and broader retrieval evaluation are covered in more depth elsewhere in the course.

<br/>

## 8. Metric and Index Configuration Checklist

Before indexing or querying:

1. **Check model guidance.** Determine whether the embedding model recommends cosine similarity, dot product, or another metric.
2. **Check normalization.** Know whether the model returns normalized vectors and whether your pipeline normalizes them.
3. **Keep configuration consistent.** Use compatible query/document encoding, vector dimensions, normalization, and index metric.
4. **Verify backend semantics.** Confirm whether the backend sorts by similarity or distance and whether it transforms returned values.
5. **Test rankings.** Compare results on a small, labeled query set rather than choosing a metric from intuition alone.
6. **Record the setup.** Save model name/version, dimensions, normalization policy, metric, index configuration, and evaluation results.

Changing the metric or normalization policy can change rankings. Treat such changes as retrieval configuration changes and evaluate them before adopting them.

<br/>

## 9. Practice

### Exercise A — Calculate the metrics

Let:

$$
q=[1,2], \quad d_1=[2,1], \quad d_2=[1,3]
$$

Calculate dot product, cosine similarity, and Euclidean distance for each document. Rank the documents under each metric.

<br/>

### Exercise B — Normalize and compare

L2-normalize the query and both documents from Exercise A. Recalculate all metrics.

- Which score values changed?
- Which rankings stayed the same?
- Why do the metrics agree on the normalized vectors?

<br/>

### Exercise C — Magnitude effect

Compare:

$$
q=[1,0], \quad d_1=[2,0], \quad d_2=[1,1]
$$

Explain why dot product, cosine similarity, and Euclidean distance do not all express the same preference.

<br/>

### Exercise D — Retrieval configuration

A model's documentation recommends dot-product retrieval, and its embeddings are already L2-normalized. A teammate proposes switching to Euclidean distance because “distance is more intuitive.”

List the checks and experiments you would run before changing the index configuration.

<br/>

## 10. Exercise Answers

### Exercise A
For $q=$:

For $d_1=[2,1]$:

$$ q\cdot d_1 = 1(2)+2(1)=4 $$

$$ \operatorname{cosine}(q,d_1)=\frac{4}{\sqrt{5}\sqrt{5}}=0.8 $$

$$ d_2(q,d_1)=\sqrt{(1-2)^2+(2-1)^2}=\sqrt{2}\approx1.414 $$

For $d_2=[1,3]$:

$$ q\cdot d_2 = 1(1)+2(3)=7 $$

$$ \operatorname{cosine}(q,d_2)=\frac{7}{\sqrt{5}\sqrt{10}}\approx0.990 $$

$$ d_2(q,d_2)=\sqrt{(1-1)^2+(2-3)^2}=1 $$

All three metrics rank $d_2$ ahead of $d_1$: it has the larger dot product and cosine similarity, and the smaller Euclidean distance.

<br/>

### Exercise B

L2 normalization preserves vector directions but changes vector magnitudes. For nonzero vectors, cosine similarity is unchanged by positive scaling. Dot products and Euclidean distances change numerically after normalization. Because all three vectors are now unit vectors, their rankings agree.

<br/>

### Exercise C

- Dot product: $q\cdot d_1=2$, $q\cdot d_2=1$, so it prefers $d_1$.
- Cosine: $1$ for $d_1$, approximately $0.707$ for $d_2$, so it prefers $d_1$.
- Euclidean distance: $1$ for both, so it ties them.


This example shows that a ranking can differ or tie when the vectors are not normalized.

<br/>

### Exercise D

Check the model's documented scoring recommendation, confirm that query and document vectors are normalized consistently, verify the vector index's metric semantics, and run both configurations on the same labeled query set. Compare Recall@K/MRR, latency, index behavior, and score distributions. Since unit-normalized vectors have equivalent rankings under these three exact metrics, Euclidean distance should not improve ranking quality by itself; the change may still affect score interpretation or backend implementation details.

<br/>

## 11. References and Optional Extensions

- Review the embedding model's official documentation for its recommended similarity function and normalization behavior.
- Review the selected vector database or index documentation for metric names, score semantics, and ranking direction.
- Optional extension: implement a metric comparison notebook that records top-K rankings, score values, and retrieval metrics for a fixed query set.

<br/>

## Checkpoint

You should be able to explain:

- Why similarity scores are sorted descending while distances are sorted ascending.
- Why dot product and cosine similarity are equal for unit-normalized vectors.
- Why Euclidean distance produces the same ranking for unit-normalized vectors.
- How vector magnitude can change unnormalized dot-product rankings.
- Why similarity scores are not calibrated probabilities or universal relevance thresholds.
- How to choose and validate a metric using model guidance, index configuration, and representative retrieval tests.
