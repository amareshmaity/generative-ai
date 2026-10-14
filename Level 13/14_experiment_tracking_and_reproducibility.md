# Chapter 14: Experiment Tracking and Reproducibility

## Learning Objectives

By the end of this chapter, you should be able to:

-   Version the data, labels, prompts, schemas, retrieval settings, and
    model identifiers used in an evaluation.
-   Record code, dependency, environment, seed, hardware, and timestamp
    information.
-   Preserve run manifests, raw outcomes, derived metrics, and reviewer
    decisions.
-   Apply access control, redaction, and retention rules to sensitive
    evaluation artifacts.
-   Explain why reproducing a run with a hosted model may not produce
    identical outputs.
-   Trace every reported score back to the cases, outputs, and
    configuration that produced it.

<br/>

## 1. Why Experiment Tracking Matters

An evaluation score is meaningful only when you can explain how it was
produced. If a team reports that a candidate model improved answer
correctness from 82% to 87%, an auditor or engineer should be able to
determine:

-   Which cases were evaluated?
-   Which reference labels and scoring rubric were used?
-   Which prompt, schema, retrieval configuration, and model identifier
    were active?
-   Which code and dependency versions executed the run?
-   Were failures, timeouts, retries, and missing results counted
    consistently?
-   How were raw outputs transformed into the reported metric?
-   Who reviewed disputed cases, and what decisions were made?

**Experiment tracking** records the configuration and outcomes of each
run. **Reproducibility** is the ability to reconstruct the method and
understand or verify the result. Exact replay is one form of
reproducibility, but it is not always possible with hosted or
nondeterministic systems.

A run that stores only a final score is difficult to audit. A run that
stores versioned inputs, configuration, raw results, derived metrics,
and decision history supports diagnosis, comparison, and regression
testing.

<br/>

## 2. What Must Be Versioned?

Treat the evaluation as a dependency graph: changes in any upstream
artifact can change the result.

| Artifact                | What to record                                                              | Why it matters                              |
| ----------------------- | --------------------------------------------------------------------------- | ------------------------------------------- |
| Evaluation dataset      | Stable dataset ID, version, split, case IDs, inclusion/exclusion rules      | Defines what was tested                     |
| Labels and references   | Label version, reference answers, adjudication status, rubric version       | Changes can alter measured quality          |
| Prompts                 | System/developer/user templates, prompt version, template variables         | Instructions affect model behavior          |
| Output schema           | Schema ID/version, validation rules, business constraints                   | Determines what counts as valid output      |
| Retrieval configuration | Index/corpus version, chunking, filters, top-*k*, reranker and versions     | Changes evidence available to the model     |
| Model                   | Provider, model name, version/snapshot if available, endpoint/region        | Model aliases may change over time          |
| Generation settings     | Temperature, top-*p*, token limits, stop rules, seed if supported           | Affects output and variability              |
| Tools and workflow      | Tool versions, tool schemas, orchestration graph, retry/fallback policies   | Changes execution paths                     |
| Evaluation logic        | Metric implementation, normalization, aggregation, evaluator/judge prompt   | Determines score calculation                |
| Code and dependencies   | Git commit, working-tree state, lockfile, package versions, container image | Helps reconstruct execution                 |
| Runtime environment     | OS, Python/runtime version, hardware, accelerator, relevant drivers         | Can affect execution and numerical behavior |
| Human review            | Reviewer IDs or approved pseudonymous IDs, decisions, adjudication notes    | Makes subjective judgments auditable        |


Version not only the model-facing prompt but also the evaluator prompt
and rubric. A changed evaluator can produce a different score even if
model outputs remain unchanged.

<br/>

### Use stable identifiers

Use immutable identifiers or content hashes where appropriate. For
example:

-   `dataset_version`: `evalset-v3.2`
-   `prompt_version`: `rag-answer-v7`
-   `schema_version`: `answer-schema-v2`
-   `retrieval_config_version`: `hybrid-search-v4`
-   `git_commit`: a full commit hash
-   `run_id`: a unique identifier for one execution

Names such as `latest`, `production`, or `current` are convenient
aliases, but they are not sufficient audit identifiers on their own.
Resolve aliases to the actual version or record the provider response
metadata at run time.

<br/>

## 3. The Run Manifest

A **run manifest** is a machine-readable record of the configuration,
artifacts, environment, and execution policy for one experiment. It
should be created before or at run start and finalized with actual
runtime outcomes.

A useful manifest answers five questions:

1.  **What was evaluated?** Dataset, labels, splits, and task.
2.  **What system was evaluated?** Model, prompts, schemas, retrieval,
    tools, and code.
3.  **How was it run?** Parameters, seed, environment, concurrency,
    timeout, and retry policy.
4.  **How was it scored?** Metric definitions, evaluator version,
    denominator, and aggregation.
5.  **Where are the results?** Raw outputs, logs, derived metrics,
    reviewer decisions, and access policy.

<br/>

### Example manifest in YAML

The following is an illustrative manifest. Replace placeholder values
with actual immutable IDs and verified configuration values in a real
experiment.

``` yaml
experiment:
  experiment_id: rag-answer-quality
  run_id: run-2026-10-14-001
  purpose: compare baseline and candidate answer quality
  started_at_utc: "2026-10-14T08:00:00Z"
  completed_at_utc: null
  owner: evaluation-team

comparison:
  role: candidate
  baseline_run_id: run-2026-10-13-004
  candidate_run_id: run-2026-10-14-001
  comparison_protocol: paired_cases_same_split

data:
  dataset_id: policy-rag-eval
  dataset_version: "3.2"
  split: held_out
  case_id_manifest_uri: "controlled://eval-artifacts/cases-v3.2"
  label_version: "labels-v2.1"
  rubric_version: "groundedness-rubric-v4"
  inclusion_policy_version: "inclusion-v1"
  excluded_case_ids_uri: null

application:
  code_commit: "REPLACE_WITH_FULL_GIT_COMMIT"
  working_tree_clean: true
  container_image_digest: "REPLACE_WITH_IMMUTABLE_IMAGE_DIGEST"
  dependency_lockfile_hash: "REPLACE_WITH_HASH"
  runtime:
    language: Python
    language_version: "REPLACE_WITH_ACTUAL_VERSION"
    operating_system: "REPLACE_WITH_ACTUAL_OS"
    hardware: "REPLACE_WITH_ACTUAL_HARDWARE"

model:
  provider: "REPLACE_WITH_PROVIDER"
  requested_model_id: "REPLACE_WITH_MODEL_ID"
  resolved_model_version: null
  region_or_endpoint: "REPLACE_WITH_ENDPOINT_OR_REGION"
  temperature: 0
  top_p: null
  max_output_tokens: 800
  seed: null
  seed_support: unknown
  provider_request_metadata_uri: "controlled://eval-artifacts/provider-metadata"

prompt:
  prompt_id: rag-answer
  prompt_version: "7"
  prompt_hash: "REPLACE_WITH_HASH_OF_RENDERED_TEMPLATE"
  evaluator_prompt_version: "judge-v3"
  evaluator_prompt_hash: "REPLACE_WITH_HASH"

retrieval:
  corpus_version: "policy-corpus-v12"
  index_version: "policy-index-v12"
  embedding_model_id: "REPLACE_WITH_EMBEDDING_MODEL"
  retrieval_method: hybrid
  top_k: 8
  metadata_filter_version: "permissions-filter-v3"
  reranker_version: "reranker-v2"
  chunking_config_version: "chunking-v5"

output:
  schema_id: answer-schema
  schema_version: "2"
  schema_hash: "REPLACE_WITH_HASH"
  validation_policy_version: "validation-v3"

execution:
  concurrency: 4
  timeout_seconds: 45
  retry_policy_version: "retry-v2"
  fallback_policy_version: "fallback-v1"
  cache_policy: "disabled_for_controlled_comparison"
  failure_accounting_version: "accounting-v2"

evaluation:
  metric_code_version: "metrics-v5"
  primary_metric: grounded_answer_pass_rate
  denominator_policy: "all_assigned_cases; timeouts count as failures"
  aggregation: case_level_rate
  judge_version: "judge-config-v3"
  human_adjudication_policy: "adjudication-v2"

artifacts:
  raw_outputs_uri: "controlled://eval-artifacts/run-2026-10-14-001/raw"
  case_results_uri: "controlled://eval-artifacts/run-2026-10-14-001/cases"
  metrics_uri: "controlled://eval-artifacts/run-2026-10-14-001/metrics"
  logs_uri: "restricted://eval-artifacts/run-2026-10-14-001/logs"
  reviewer_decisions_uri: "restricted://eval-artifacts/run-2026-10-14-001/reviews"

security:
  data_classification: "internal-sensitive"
  redaction_policy_version: "redaction-v2"
  access_policy_id: "eval-artifact-readers"
  retention_policy_id: "evaluation-retention-v1"
```

**Important:** A manifest is not complete merely because every field
exists. Fields must contain actual values or an explicit status such as
`unknown`, `not_supported`, or `not_applicable`. Never silently replace
an unknown seed, model version, or runtime value with a guessed value.

<br/>

## 4. Track the Baseline and Candidate Consistently

A baseline/candidate comparison is easiest to interpret when both runs
use the same evaluation cases, labels, scoring rules, and
failure-accounting policy. Differences should be intentional and
documented.

<br/>

### Recommended comparison controls

-   Use the same held-out case IDs and label version.
-   Keep metric code, normalization, aggregation, and denominator policy
    fixed.
-   Record the baseline and candidate configuration independently.
-   Change only the intended factor when practical; document unavoidable
    differences.
-   Keep timeout, retry, fallback, and cache policies comparable.
-   Capture failures and missing results for both runs.
-   Preserve per-case outputs, not only aggregate scores.
-   Compare quality alongside latency, cost, reliability, and safety
    requirements where relevant.

For paired cases, let $b_i$ be the baseline outcome and $c_i$ the
candidate outcome for case $i$. A case-level difference is:

$$
d_i = c_i - b_i
$$

The average paired difference is:

$$
\bar{d} = \frac{1}{N}\sum_{i=1}^{N} d_i
$$

This calculation is appropriate only when the outcomes and their scale
are meaningfully comparable. For binary pass/fail outcomes, $d_i$
belongs to $\{-1,0,1\}$. Report the number of paired cases and how
missing outputs were handled. A change in denominator can make an
apparent improvement misleading.

<br/>

### Why per-case results matter

Suppose a candidate improves the aggregate pass rate but regresses on a
small set of high-severity policy cases. The aggregate alone may hide
the risk. Per-case records allow you to identify:

-   Cases improved by the candidate.
-   Cases regressed by the candidate.
-   Cases that failed in both systems.
-   Cases with missing outputs or inconsistent execution.
-   Slices where the candidate changed behavior.

<br/>

## 5. Preserve Raw Outcomes and Derived Metrics

Store the **raw outcome** and the **derived evaluation result** as
separate artifacts.

### Raw outcome examples

-   Exact model response.
-   Structured tool-call request and tool result.
-   Retrieved document IDs and ranking scores.
-   Exact assembled context or a protected reference to it.
-   HTTP/provider status, timeout, retry, and error details.
-   Token usage and timing metadata returned by the provider.
-   Schema parser and validator errors.

<br/>

### Derived result examples

-   Correctness or groundedness labels.
-   Parse success and field-level accuracy.
-   Retrieval metrics.
-   Latency percentiles and token/cost summaries.
-   Judge scores and pairwise preferences.
-   Human review decisions and adjudication outcomes.

Derived metrics should be reproducible from raw outcomes and a versioned
metric implementation wherever possible. If a metric is computed
manually or by a hosted evaluator, preserve its input, output, evaluator
configuration, and reviewer decisions.

<br/>

### Case-level result example

``` json
{
  "run_id": "run-2026-10-14-001",
  "case_id": "policy-0042",
  "status": "completed",
  "raw_output_uri": "controlled://eval-artifacts/run-2026-10-14-001/raw/policy-0042",
  "retrieved_document_ids": ["doc-18", "doc-41"],
  "parse_valid": true,
  "groundedness_label": "pass",
  "review_status": "human_reviewed",
  "reviewer_decision_version": "review-batch-07",
  "latency_ms": 1830,
  "input_tokens": 1250,
  "output_tokens": 210
}
```

The example is illustrative. Avoid embedding sensitive prompts, source
text, or outputs directly in broadly accessible metadata. Use controlled
artifact references where the content itself requires stricter
permissions.

<br/>

## 6. Data and Label Lineage

Evaluation datasets change over time. New cases may be added, labels
corrected, duplicates removed, or inclusion rules revised. Track these
changes explicitly.

A robust dataset release should identify:

-   Dataset ID and immutable version.
-   Stable case IDs.
-   Source provenance and permitted use.
-   Dataset split and split-generation method.
-   Label/reference version and rubric version.
-   Changes since the prior release.
-   Excluded cases and reasons for exclusion.
-   Known limitations, coverage gaps, and unresolved disagreements.

<br/>

### Label changes are experiment changes

If a reference answer is corrected after a run, do not silently
overwrite the old label and leave the old score in place. Preserve the
previous label version, create a new version, rerun affected cases, and
mark metrics computed under the earlier version as belonging to the
earlier evaluation definition.

If cases are added or removed, document whether the comparison is still
paired. A baseline score computed on one population should not be
compared casually with a candidate score computed on another.

<br/>

## 7. Human Review and Evaluator Lineage

Human evaluation and LLM-as-a-Judge both require configuration tracking.

For human review, preserve:

-   Rubric and annotation instructions.
-   Reviewer assignment and approved pseudonymous identifier.
-   Individual labels before adjudication.
-   Adjudicated result and reason for changing a label.
-   Review timestamp and relevant case version.
-   Disagreement or uncertainty markers.

For model-based judging, preserve:

-   Judge model identifier and version/snapshot if available.
-   Judge prompt and rubric version.
-   Input fields supplied to the judge.
-   Candidate order and blinding/randomization protocol.
-   Raw judge response and parsed label.
-   Human calibration or adjudication outcomes.

A reviewer decision is an artifact, not an invisible edit to the
dataset. This history makes it possible to understand whether a score
changed because the system improved or because the evaluation labels
changed.

<br/>

## 8. Seeds, Determinism, and Nondeterminism

A random seed can help reproducibility only when the relevant components
support and honor it. Even then, it may not guarantee bit-for-bit
identical output.

Potential sources of variation include:

-   Sampling in model generation.
-   Provider-side model updates behind a stable alias.
-   Nondeterministic kernels or parallel numerical operations.
-   Changes in retrieval index contents or ranking behavior.
-   Tool/API responses that change over time.
-   Dynamic context, external data, or time-sensitive system state.
-   Retries, fallback routing, and concurrency.
-   Judge model variability and reviewer disagreement.

<br/>

### What to record

-   Seed value and whether the provider/component supports it.
-   Sampling and decoding settings.
-   Requested and resolved model version, if available.
-   Timestamp and provider response metadata.
-   Exact prompt and context, or a controlled immutable reference.
-   Retrieval index/corpus version and tool results.
-   Retry, fallback, and cache behavior.
-   Whether the rerun matched exactly, matched at the metric level, or
    differed.

Use precise reproducibility language:

-   **Exact replay:** same inputs and environment produce identical
    outputs.
-   **Procedural reproducibility:** the documented method can be rerun,
    although outputs may vary.
-   **Metric-level reproducibility:** reruns produce sufficiently
    similar aggregate results under a defined tolerance.
-   **Not fully reproducible:** a dependency, version, input, or
    artifact needed to reconstruct the run is unavailable.

Do not claim exact reproducibility for a hosted model merely because the
same model alias and prompt were used.

<br/>

## 9. Hosted Models and External Dependencies

Hosted APIs may not expose all implementation details, and providers can
change behavior without making every internal artifact available to the
user.

For hosted-model experiments, record at least:

-   Provider and endpoint/region.
-   Requested model ID and resolved version if available.
-   Request parameters and relevant response headers/metadata.
-   Request timestamp and provider request ID where available.
-   Prompt, context, and tool results in access-controlled storage.
-   Usage, latency, errors, retries, and fallback route.
-   Provider documentation or terms version when material to the
    experiment.

If the provider does not expose a fixed model snapshot or seed, record
that limitation explicitly. A later rerun may be a new experiment rather
than a true replay. When exact replay is impossible, preserve the
original raw outputs and compare later behavior against them using the
same versioned evaluator.

<br/>

## 10. Sensitive Data, Access Control, and Retention

Evaluation artifacts can contain personal information, confidential
documents, secrets, customer content, or model outputs that reproduce
sensitive input. Reproducibility does not justify unrestricted
retention.

Apply controls proportionate to data sensitivity:

1.  **Minimize:** collect only data necessary to evaluate the system.
2.  **Redact or pseudonymize:** remove unnecessary identifiers and
    secrets before logging.
3.  **Separate metadata from payloads:** store broadly useful run
    metadata separately from restricted prompts, contexts, and outputs.
4.  **Control access:** use least privilege, scoped permissions, and
    audited access.
5.  **Encrypt:** protect data in transit and at rest according to
    organizational policy.
6.  **Define retention:** set retention periods and deletion procedures
    before collection.
7.  **Preserve lineage safely:** use immutable IDs and hashes where
    possible, while recognizing that hashes of low-entropy sensitive
    values may still leak information.
8.  **Respect provider policies:** verify whether inputs or outputs may
    be stored, used for training, or sent to external evaluators.

Do not put API keys, passwords, access tokens, or unnecessary personal
data into manifests, logs, Git repositories, or experiment dashboards.
Use secret managers and controlled artifact storage. A content hash can
verify artifact identity, but it cannot replace access control or prove
that the artifact is safe to share.

<br/>

## 11. Artifact Layout and Audit Trail

A simple directory structure can separate configuration, raw results,
derived metrics, and human review:

``` text
evaluation/
├── manifests/
│   ├── baseline.yaml
│   └── candidate.yaml
├── dataset-releases/
│   ├── dataset-manifest.yaml
│   └── label-changelog.md
├── runs/
│   └── run-2026-10-14-001/
│       ├── run-manifest.yaml
│       ├── case-results.jsonl
│       ├── raw-output-index.jsonl
│       ├── metrics.json
│       ├── errors.jsonl
│       └── reviewer-decisions.jsonl
└── reports/
    └── baseline-vs-candidate.md
```

This is a logical example, not a mandate to store every artifact as a
local file. In production, large or sensitive payloads may live in
controlled object storage, a database, or an experiment-tracking
service. The manifest should point to immutable or versioned artifacts
with appropriate access controls.

<br/>

### Minimum audit trail

For every reported metric, preserve a traceable path:

``` mermaid
flowchart LR
    A[Reported score] --> B[Metric definition and code version]
    B --> C[Per-case scored results]
    C --> D[Raw outputs and errors]
    D --> E[Run manifest]
    E --> F[Dataset, labels, prompts, model and environment]
    C --> G[Reviewer decisions and adjudication]
```

A score is auditable when a reviewer can follow this chain and verify
how the result was computed.

<br/>

## 12. Python: Hash and Record a Manifest

A content hash can help identify a particular manifest or configuration
file. It does not guarantee that referenced external resources remain
available or unchanged.

``` python
import hashlib
import json
from pathlib import Path
from typing import Any


def sha256_file(path: str | Path) -> str:
    """Return the SHA-256 digest of a file's bytes."""
    digest = hashlib.sha256()
    with open(path, "rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json_hash(value: Any) -> str:
    """Hash a JSON-serializable value with stable key ordering."""
    serialized = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(serialized).hexdigest()


manifest_excerpt = {
    "dataset_version": "3.2",
    "prompt_version": "7",
    "schema_version": "2",
    "model_id": "provider/model-snapshot-if-available",
    "temperature": 0,
    "metric_code_version": "metrics-v5",
}

print("Manifest excerpt hash:", canonical_json_hash(manifest_excerpt))
```

**Important limitations:**

-   The example hashes only the manifest excerpt, not the referenced
    dataset, prompt file, model weights, or external service.
-   Hashing requires a canonical representation. Semantically identical
    JSON with different formatting can otherwise have different byte
    hashes.
-   Do not include secrets or raw sensitive values in a manifest just to
    hash them.
-   Record the hash algorithm and what exact bytes or canonical
    representation were hashed.

<br/>

## 13. Practice: Audit a Baseline/Candidate Comparison

### Scenario

A team reports:

-   Baseline grounded-answer pass rate: 81%.
-   Candidate grounded-answer pass rate: 86%.
-   Candidate p95 latency is higher.
-   The candidate used a revised prompt and a new retrieval
    configuration.
-   The team has saved aggregate metrics but has not documented whether
    both runs used identical case IDs.

<br/>

### Tasks

1.  List the minimum manifest fields needed to audit the comparison.
2.  Identify which variables changed intentionally and which controls
    should remain fixed.
3.  Specify the per-case artifacts required to trace each score.
4.  Explain how you would handle timeouts, missing outputs, retries, and
    exclusions.
5.  Describe the evidence needed before concluding that the candidate is
    better.
6.  Explain what you can and cannot reproduce if the hosted model has no
    fixed snapshot or supported seed.

<br/>

## 14. Practice: Example Manifest Checklist

Use this checklist when preparing one baseline/candidate comparison:

-   [ ] Both runs reference an immutable dataset version and explicit
    case IDs.
-   [ ] Label, rubric, and evaluator versions are recorded.
-   [ ] Prompt and schema versions/hashes are recorded.
-   [ ] Model identifiers, provider, endpoint, and available version
    metadata are recorded.
-   [ ] Retrieval corpus/index and settings are recorded.
-   [ ] Code commit, working-tree state, dependency lockfile, and
    runtime are recorded.
-   [ ] Seeds and seed-support status are recorded where relevant.
-   [ ] Timeout, retry, fallback, concurrency, and cache policies are
    recorded.
-   [ ] Metric code, aggregation, normalization, and denominator policy
    are recorded.
-   [ ] Raw outputs, errors, usage, and timing metadata are retained or
    referenced.
-   [ ] Reviewer labels, disagreements, and adjudication decisions are
    preserved.
-   [ ] Sensitive artifacts have appropriate access and retention
    controls.
-   [ ] Aggregate metrics can be recomputed from case-level results.
-   [ ] Differences between baseline and candidate are explicit.
-   [ ] Known reproducibility limitations are documented.

<br/>

## 15. Answer Key and Worked Audit

A strong answer should make the comparison reconstructable, not simply
list model names.

### 1. Minimum manifest fields

At minimum: run IDs and timestamps; dataset version and exact case IDs;
label/rubric version; prompt and schema versions; baseline and candidate
model identifiers; retrieval corpus/index/settings; code commit and
dependency lockfile; generation parameters; runtime and seed support;
retry/timeout/cache policies; metric implementation and denominator
policy; raw artifact locations; reviewer decisions; security/retention
classification.

<br/>

### 2. Changed variables and controls

The prompt and retrieval configuration changed intentionally. To isolate
their effects, compare them separately where feasible---for example,
baseline prompt/baseline retrieval, candidate prompt/baseline retrieval,
baseline prompt/candidate retrieval, and candidate prompt/candidate
retrieval. If only the combined candidate is tested, the team can assess
the combined change but cannot confidently attribute the improvement to
one component.

Keep the dataset cases, labels, evaluator, metric code, and
failure-accounting rules fixed. If any must change, document and justify
it.

<br/>

### 3. Per-case artifacts

Preserve case ID, baseline and candidate raw output references,
retrieval results, assembled context reference where permitted,
parse/validation status, evaluator input/output, human review and
adjudication, latency, token usage, errors, retries, and status. Include
the exact run/configuration identifiers for both outcomes.

<br/>

### 4. Missing outcomes

Define the denominator policy before comparing runs. Report assigned,
completed, failed, timed-out, excluded, and missing counts separately.
Do not silently remove timeouts or failures from one run while counting
them in the other. If the primary task metric treats timeout as failure,
apply that rule consistently and report it. Keep latency summaries
explicit about which requests are included.

<br/>

### 5. Evidence for a candidate improvement

Verify identical paired case IDs and label versions; recompute metrics
from per-case results; inspect improvements and regressions; check
high-severity cases and important slices; quantify uncertainty when
appropriate; and compare latency, cost, reliability, and safety
constraints. An aggregate increase from 81% to 86% alone is insufficient
to establish a robust or acceptable improvement.

<br/>

### 6. Hosted-model reproducibility

If the provider exposes no fixed snapshot or supported seed, exact
output replay may not be possible. You can still preserve the original
request configuration and raw outputs, document provider/version
metadata and timestamps, rerun the documented procedure, and compare
results under a defined tolerance. State clearly that a rerun may use
changed provider-side behavior.

<br/>

## 16. Checkpoint: Trace Every Score

**Checkpoint prompt:** Trace each reported score to its cases, outputs,
and configuration.

For one baseline/candidate comparison, be prepared to demonstrate:

1.  The exact evaluation population and label/rubric versions.
2.  The prompt, schema, retrieval settings, model identifier, and code
    version for each run.
3.  The raw output and execution status for every case.
4.  The versioned scoring implementation and denominator policy.
5.  The derived case-level labels and aggregate metric calculation.
6.  The reviewer decisions and adjudication history for subjective
    labels.
7.  The handling of timeouts, retries, exclusions, and missing results.
8.  The limitations that prevent exact replay, if any.
9.  The access controls and retention policy for sensitive artifacts.

<br/>

### Model checkpoint answer

To audit a reported grounded-answer pass rate, begin with the report's
`run_id` and metric definition. Retrieve the immutable case-ID list and
dataset/label versions. For each case, retrieve its status, raw output
reference, relevant retrieval/context artifacts, and scoring result.
Verify the prompt, model, retrieval configuration, schema, evaluator
version, code commit, and denominator policy from the run manifest.
Recompute the pass rate from case-level outcomes, accounting for
timeouts and missing results exactly as documented. For human- or
judge-based labels, inspect the rubric and applicable
review/adjudication records. Finally, compare the baseline and candidate
on the same cases, review regressions and important slices, and document
any hosted-model nondeterminism that prevents exact replay.

<br/>

## Key Takeaways

-   A reported score should be traceable to the exact cases, outputs,
    evaluator, and configuration that produced it.
-   Version datasets, labels, prompts, schemas, retrieval settings,
    model identifiers, code, dependencies, and runtime.
-   Preserve raw outcomes separately from derived metrics and keep
    reviewer decisions auditable.
-   Use immutable IDs, manifests, and hashes carefully; none alone
    guarantees that all dependencies can be reconstructed.
-   Hosted-model nondeterminism and provider-side changes should be
    documented, not hidden.
-   Reproducibility must coexist with privacy, access control, data
    minimization, and retention requirements.

<br/>

## Further Reading

-   [MLflow Tracking
    Documentation](https://mlflow.org/docs/latest/ml/tracking/) ---
    logging parameters, metrics, artifacts, and runs.
-   [DVC Documentation](https://dvc.org/doc) --- versioning data and
    pipelines.
-   [Git Documentation](https://git-scm.com/doc) --- version control and
    commit history.
-   [OpenTelemetry Documentation](https://opentelemetry.io/docs/) ---
    traces, metrics, and logs.
-   [NIST AI Risk Management
    Framework](https://www.nist.gov/itl/ai-risk-management-framework)
    --- risk management and documentation practices.


<br/>


**Chapter 14 complete.** The next chapter is **Controlled Comparisons
and Uncertainty**.
