# 04. Vector Dimensions and Normalization

## Learning Objectives

By the end of this chapter, you should be able to:

- Track the shapes of corpus embeddings and query embeddings.
- Define vector norms and explain unit-length normalization.
- Detect and handle zero vectors and invalid numerical values.
- Estimate how vector dimensions affect storage, memory, and computation.
- Distinguish model-supported dimension reduction from arbitrary vector truncation.
- Record the embedding model, dimensions, normalization, and index configuration together.

<br/>

## 1. What Is a Vector Dimension?

A text embedding is a numerical vector. Its **dimension** is the number of numerical components it contains.

For example:

$$ \mathbf{x} = [0.2,\; -0.4,\; 0.7] $$

This vector has three dimensions. If an embedding model returns 768 values for each input, each embedding has dimension $d=768$.

For a corpus of $N$ passages, the embedding matrix commonly has shape:

$$ X \in \mathbb{R}^{N \times d} $$

where:

* $N$ is the number of passages.
* $d$ is the number of dimensions per embedding.
* Each row represents one passage vector.

A single query embedding commonly has shape:

$$ \mathbf{q} \in \mathbb{R}^{d} $$

If multiple queries are encoded together, their embeddings may form a matrix of shape $Q \times d$, where $Q$ is the number of queries.

Actual library outputs may include extra batch dimensions or wrapper objects. Inspect the documented output format rather than assuming a shape.


<br/>

## 2. Track Corpus and Query Shapes

Shape compatibility is one of the first checks to perform before calculating similarity.

Suppose a corpus contains 1,000 passages and the selected model returns 384-dimensional vectors. The corpus matrix should have shape `(1000, 384)`. One query vector should have shape `(384,)`.

```python
import numpy as np

# Illustrative vectors, not model-generated embeddings.
corpus_vectors = np.array([
    [0.1, 0.2, 0.3],
    [0.4, 0.5, 0.6],
    [0.7, 0.8, 0.9],
], dtype=np.float32)

query_vector = np.array([0.2, 0.3, 0.4], dtype=np.float32)

print("Corpus shape:", corpus_vectors.shape)  # (3, 3)
print("Query shape:", query_vector.shape)     # (3,)
print("Corpus dimension:", corpus_vectors.shape[1])
print("Query dimension:", query_vector.shape[0])

if corpus_vectors.ndim != 2:
    raise ValueError("Corpus vectors must be a 2D matrix")

if query_vector.ndim != 1:
    raise ValueError("Query vector must be one-dimensional")

if corpus_vectors.shape[1] != query_vector.shape[0]:
    raise ValueError("Corpus and query dimensions do not match")
```

The corpus and query must use compatible embedding conventions, not just matching shapes. Shape checks detect structural errors; they cannot establish that two vectors came from compatible models.

<br/>

### Common shape errors

- A single vector is accidentally represented as `(1, d)` when the function expects `(d,)`.
- A corpus is represented as a one-dimensional array because only one vector was provided.
- The query dimension differs from the index dimension.
- The model returns an unexpected output shape due to batching or an API wrapper.
- The corpus vector order no longer matches the document ID order.

Validate both shapes and the mapping between vectors and source records.

<br/>

## 3. Vector Norms

A **norm** measures the magnitude or length of a vector. The Euclidean, or L2, norm is commonly used in embedding workflows.

For a vector

$$
\mathbf{x} = [x_1, x_2, \ldots, x_d]
$$

its L2 norm is:

$$
\|\mathbf{x}\|_2 = \sqrt{\sum_{i=1}^{d} x_i^2}
$$

For example, if:

$$
\mathbf{x} = [3,4]
$$

then:

$$
\|\mathbf{x}\|_2 = \sqrt{3^2 + 4^2} = 5
$$

The norm describes vector magnitude. It does not directly measure the quality or correctness of the represented text.

<br/>

## 4. Unit-Length Normalization

**L2 normalization** scales a non-zero vector so that its L2 norm becomes 1.

For a non-zero vector $\mathbf{x}$, its normalized form is:

$$ \hat{\mathbf{x}} = \frac{\mathbf{x}}{\|\mathbf{x}\|_2} $$

For $\mathbf{x}=[3,4]$, the norm is 5, so:

$$ \hat{\mathbf{x}} = [0.6,0.8] $$

Its norm is:

$$ \sqrt{0.6^2+0.8^2}=1 $$


Normalization changes magnitude but preserves direction for a non-zero vector. Whether normalization should be applied depends on the model and retrieval configuration. Some models return normalized vectors; others do not. Do not normalize automatically without checking the intended scoring method and model documentation.

<br/>

### Why normalization matters

For unit-normalized vectors, cosine similarity and dot product have the same ranking relationship because:

$$
\cos(\mathbf{x},\mathbf{y}) =
\frac{\mathbf{x}\cdot\mathbf{y}}
{\|\mathbf{x}\|_2\|\mathbf{y}\|_2}
$$

If both vectors have norm 1:

$$
\cos(\mathbf{x},\mathbf{y}) = \mathbf{x}\cdot\mathbf{y}
$$

This relationship is useful, but it does not mean all vector databases or models require normalized vectors. Follow the model's recommended metric and index configuration.

<br/>

## 5. Zero Vectors and Invalid Numerical Values

Some operations are undefined or unsafe for invalid vectors. Validate vector data before adding it to an index or using it for scoring.

### 5.1 Zero vectors

A zero vector contains only zeros:

$$
\mathbf{0} = [0,0,\ldots,0]
$$

Its L2 norm is zero. L2 normalization would require division by zero, so a zero vector cannot be normalized to unit length using the standard formula. Cosine similarity is also undefined when either vector has zero norm.

A zero vector may indicate a failed embedding operation, invalid input handling, or an application bug. Do not silently treat it as a normal embedding.

<br/>

### 5.2 NaN and infinity

Numerical arrays may contain:

- `NaN` — not a number
- `+inf` — positive infinity
- `-inf` — negative infinity

These values can corrupt scoring, sorting, normalization, or index behavior. Reject or quarantine invalid vectors and investigate their origin.

<br/>

### 5.3 Safe normalization example

```python
import numpy as np

def l2_normalize(vector: np.ndarray) -> np.ndarray:
    vector = np.asarray(vector, dtype=np.float32)

    if vector.ndim != 1:
        raise ValueError("Expected a one-dimensional vector")

    if vector.size == 0:
        raise ValueError("Vector must not be empty")

    if not np.isfinite(vector).all():
        raise ValueError("Vector contains NaN or infinity")

    norm = np.linalg.norm(vector)

    if norm == 0:
        raise ValueError("Cannot L2-normalize a zero vector")

    return vector / norm


example = np.array([3.0, 4.0], dtype=np.float32)
normalized = l2_normalize(example)

print("Original:", example)
print("Original norm:", np.linalg.norm(example))
print("Normalized:", normalized)
print("Normalized norm:", np.linalg.norm(normalized))
```

Expected conceptual output:

```text
Original: [3. 4.]
Original norm: 5.0
Normalized: [0.6 0.8]
Normalized norm: 1.0
```

Floating-point output may contain small rounding differences. Use a tolerance when testing norms rather than requiring exact equality to `1.0`.

For matrices, normalize each row independently if each row represents a separate embedding. Avoid normalizing the entire matrix as though it were one vector.

<br/>

## 6. Storage, Memory, and Computation

Vector dimension affects the resources needed to store and search an embedding collection.

### 6.1 Raw vector storage estimate

If there are $N$ vectors, each with $d$ dimensions, and each component uses $b$ bytes, the raw vector payload is approximately:

$$ \text{Bytes} = N \times d \times b $$

For 100,000 vectors with 768 dimensions stored as 32-bit floats (4 bytes per component):

$$ 100{,}000 \times 768 \times 4 = 307{,}200{,}000 \text{ bytes} $$


That is approximately 307.2 MB in decimal units, or about 293 MiB. This estimate excludes metadata, document text, IDs, index structures, allocator overhead, replicas, and backups.

<br/>

### 6.2 Dimension and search cost

For a simple exhaustive search, scoring a query against $N$ vectors with $d$ dimensions generally requires work proportional to $N \times d$.


This means that, all else equal:

- More vectors increase the number of candidates to score.
- Higher dimensions increase the arithmetic per vector.
- Lower dimensions can reduce storage and computation.
- Lower dimensions may also reduce retrieval quality if useful information is lost.

Approximate nearest-neighbor indexes change the search trade-offs and add their own memory and construction costs; those index families are discussed in later chapters.

<br/>

### 6.3 Estimate storage with Python

```python
def estimate_vector_storage(
    num_vectors: int,
    dimensions: int,
    bytes_per_component: int = 4,
) -> dict[str, float]:
    if num_vectors < 0 or dimensions <= 0 or bytes_per_component <= 0:
        raise ValueError("Invalid storage estimate inputs")

    total_bytes = num_vectors * dimensions * bytes_per_component

    return {
        "bytes": float(total_bytes),
        "decimal_MB": total_bytes / 1_000_000,
        "binary_MiB": total_bytes / (1024 ** 2),
    }


estimate = estimate_vector_storage(100_000, 768)
print(estimate)
```

This is a raw-vector estimate, not a prediction of total database memory or cloud-service cost.

<br/>

## 7. Dimension Reduction vs. Arbitrary Truncation

Reducing embedding dimensions can lower storage and computation costs, but the method matters.

### 7.1 Supported dimension reduction

Some embedding models explicitly support producing embeddings at configurable dimensions or provide a documented dimension-reduction method. Such options may be trained or designed to preserve useful information at supported output sizes.

When using a supported option:

- Verify the model documentation and allowed dimensions.
- Use the same supported configuration for corpus and query embeddings.
- Evaluate retrieval quality at each candidate dimension.
- Record the chosen dimension with the model and index configuration.

<br/>

### 7.2 Arbitrary truncation

Arbitrary truncation means taking only the first $k$ components of an embedding without a model-supported reason:

```python
short_vector = original_vector[:128]
```

This is not automatically a valid dimension-reduction method. The discarded components may contain useful information, and the remaining components may not form a meaningful representation under the model's training or scoring assumptions.

Do not assume that a shorter vector created by slicing is equivalent to a model-generated embedding of that dimension.

<br/>

### 7.3 Projection methods

Dimensionality reduction can also be performed using a separately fitted projection method, such as PCA, when suitable data and validation procedures are available. This creates an additional transformation that must be applied consistently to query and document vectors. Its impact on retrieval quality must be measured.

For this course's core workflow, prefer model-supported dimensions unless there is a clear reason to implement and evaluate another reduction method.

<br/>

## 8. Keep Model and Index Configuration Together

The index configuration should document the embedding configuration that produced its vectors. A useful record includes:

| Setting | Example of what to record |
|---|---|
| Model ID | Exact provider/model identifier |
| Model version | Revision or dated version where available |
| Embedding dimension | Actual output dimension |
| Query/document encoding | Prefixes, instructions, or modes |
| Normalization | None, model-provided, or application-applied L2 normalization |
| Similarity metric | Cosine, dot product, or a supported distance metric |
| Vector data type | For example, 32-bit float |
| Index type and parameters | Exact configuration for the selected index |
| Corpus version | Source revision, snapshot, or ingestion version |
| Configuration date | Date checked and tested |

Why record these together? The vector values and their interpretation depend on the model, encoding method, normalization, metric, and index settings. A change to one setting can make old index contents incompatible with new queries or change the ranking behavior.

<br/>

### Example configuration

```python
index_config = {
    "model_id": "record-the-selected-model-id",
    "model_version": "record-version-if-available",
    "dimensions": 768,
    "query_encoding": "document-the-required-query-mode",
    "document_encoding": "document-the-required-passage-mode",
    "normalization": "l2",
    "metric": "cosine",
    "vector_dtype": "float32",
    "index_type": "record-the-selected-index",
}
```

The values are placeholders for documentation practice, not a recommendation to use a particular model or index. Replace them with verified values from the chosen implementation.

<br/>

## 9. Practice: Normalize Toy Vectors and Verify Shapes

### Task A: Inspect shapes

Use this toy corpus:

```python
import numpy as np

corpus = np.array([
    [3.0, 4.0],
    [1.0, 0.0],
    [0.0, 2.0],
], dtype=np.float32)

query = np.array([3.0, 4.0], dtype=np.float32)

print("Corpus shape:", corpus.shape)
print("Query shape:", query.shape)
```

Questions:

1. What is the corpus matrix shape?
2. What is the query vector shape?
3. What is the embedding dimension?
4. Would a query vector of shape `(3,)` be compatible with this corpus?

<br/>

### Task B: Normalize each row

```python
norms = np.linalg.norm(corpus, axis=1, keepdims=True)

if not np.isfinite(corpus).all():
    raise ValueError("Corpus contains invalid values")

if np.any(norms == 0):
    raise ValueError("Corpus contains a zero vector")

normalized_corpus = corpus / norms

print("Normalized corpus:\n", normalized_corpus)
print("Row norms:", np.linalg.norm(normalized_corpus, axis=1))
```

`axis=1` computes one norm per row. `keepdims=True` keeps the result shaped as a column so NumPy can broadcast it across each row.

<br/>

### Task C: Verify unit norms

Use a tolerance to account for floating-point rounding:

```python
row_norms = np.linalg.norm(normalized_corpus, axis=1)

assert np.allclose(row_norms, 1.0, atol=1e-6)
print("All corpus vectors have unit norm.")
```

<br/>

### Task D: Handle invalid inputs

Test the normalization helper with:

- A zero vector such as `[0.0, 0.0]`
- A vector containing `np.nan`
- A vector containing `np.inf`
- An empty vector

The implementation should reject invalid cases explicitly rather than silently producing invalid normalized values.

<br/>

## 10. Common Mistakes

- **Checking only the vector dimension:** Matching dimensions do not guarantee model compatibility.
- **Normalizing without checking for zero norms:** This can cause division by zero and invalid values.
- **Ignoring NaN or infinity:** Invalid values can corrupt scoring and indexing.
- **Normalizing the whole matrix at once:** If each row is a separate embedding, normalize each row independently.
- **Assuming every model returns unnormalized vectors:** Some models already normalize outputs; follow the documented behavior.
- **Reducing dimensions by slicing without evaluation:** Arbitrary truncation can damage the representation.
- **Estimating total index size from vector bytes alone:** Index structures, metadata, IDs, and storage overhead are additional.
- **Changing dimensions or normalization without updating the index:** Old vectors and new queries may no longer follow the same configuration.
- **Using exact equality for floating-point norms:** Use numerical tolerances when testing unit length.

<br/>

## 11. Revision Questions and Answers

**1. What does the dimension of an embedding represent?**  
The number of numerical components in the vector.

**2. What is the usual shape of a corpus embedding matrix?**  
`(number_of_documents, embedding_dimension)`.

**3. What is the L2 norm of `[3, 4]`?**  
$\sqrt{3^2+4^2}=5$.

**4. What does L2 normalization do?**  
It divides a non-zero vector by its L2 norm so that the resulting vector has unit length.

**5. Why must zero vectors be handled explicitly?**  
Their norm is zero, so standard L2 normalization divides by zero, and cosine similarity is undefined for a zero-norm input.

**6. Why validate numerical finiteness?**  
NaN and infinite values can make scoring, normalization, sorting, and indexing unreliable.

**7. How does dimension affect raw storage?**  
For a fixed number of vectors and bytes per component, storage grows linearly with dimension.

**8. Why is arbitrary vector truncation risky?**  
The removed components may contain useful information, and the remaining vector may not preserve the model's intended representation.

**9. What should be recorded alongside the index?**  
The model and version, dimensions, encoding conventions, normalization, metric, data type, index type and parameters, and corpus version.

**10. Why might changing normalization require rebuilding an index?**  
The stored vectors may no longer match the scoring assumptions or configuration used for query vectors and index search. Depending on the backend, vectors may need to be transformed and the index rebuilt.

<br/>

## 12. Chapter Checkpoint

You should now be able to:

- Inspect corpus and query shapes.
- Calculate L2 norms and normalize non-zero vectors.
- Reject zero vectors and non-finite values.
- Estimate raw vector storage and understand dimension-related computation.
- Distinguish supported dimension reduction from arbitrary truncation.
- Keep the embedding and index configuration reproducible.

**Checkpoint answer:** Changing dimensions may require re-embedding the corpus because the index expects vectors with a particular shape and representation. Changing normalization can alter vector magnitudes and similarity or distance scores. If stored document vectors and incoming query vectors use inconsistent dimensions or normalization conventions, retrieval may fail or rankings may change. Record the configuration together and rebuild or migrate the index whenever the change makes existing vectors or index assumptions incompatible.

<br/>

## References and Further Reading

- Level 7 course outline: `README.md`, Chapter 04 — “Vector Dimensions and Normalization.”
- Documentation for the selected embedding model: verify output dimensions, supported reduced dimensions, and whether vectors are normalized.
- Documentation for the selected vector index: verify supported dimensions, vector data types, metrics, and any normalization assumptions.

**Scope note:** This chapter covers vector shapes, norms, normalization, and dimension-related trade-offs. Similarity and distance metrics are developed in Chapter 05; vector-index families and their trade-offs are developed in Chapters 08–09.
