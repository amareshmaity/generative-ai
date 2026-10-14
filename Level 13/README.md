# Level 13: GenAI Evaluation and Optimization

**Goal:** Measure application quality systematically and improve it without relying on subjective impressions alone.

This README is the plan for creating notes one by one. Keep numbered Markdown notes directly in `Level 13`, following the previous levels. The filenames below are planned files, not existing chapter links.

## Prerequisites

- Review prompting, structured outputs, validation, and model-backed applications from Levels 5–6.
- Complete [Level 8: Retrieval-Augmented Generation (RAG)](<../Level 8/README.md>) before the RAG-specific chapters.
- Review basic statistics: averages, percentiles, variation, sampling, and proportions.
- Have one application, fixed model-output fixtures, or a reproducible inference workflow to evaluate.
- Fine-tuning and media specializations are not prerequisites. This level supplies the evaluation foundations required before Level 12 training experiments.

## Learning outcomes

After completing this level, you should be able to:

- Define measurable task-specific quality criteria and build representative evaluation datasets.
- Combine deterministic checks, human review, and calibrated model-based judgments appropriately.
- Distinguish correctness, relevance, faithfulness, citation support, and answerability.
- Evaluate retrieval separately from answer generation.
- Compare prompts, models, and configurations with uncertainty and regression analysis.
- Measure latency, throughput, usage, and cost alongside quality.
- Track reproducible experiments, define release gates, and incorporate production feedback.
- Choose optimizations from diagnosed failures and measured trade-offs.

## Study order and planned note files

| Order | Planned note filename | Focus |
|---|---|---|
| 1 | `01_genai_evaluation_vs_software_testing.md` | Probabilistic quality versus deterministic correctness checks |
| 2 | `02_task_specific_quality_criteria.md` | Success criteria, rubrics, and acceptable failures |
| 3 | `03_golden_datasets_and_test_cases.md` | Coverage, labeling, splits, and leakage prevention |
| 4 | `04_human_evaluation.md` | Annotation guidance, disagreement, and review quality |
| 5 | `05_exact_match_and_task_specific_metrics.md` | Objective checks and metric suitability |
| 6 | `06_correctness_relevance_and_faithfulness.md` | Distinct quality dimensions and evidence requirements |
| 7 | `07_structured_output_evaluation.md` | Parsing, schemas, fields, and semantic validation |
| 8 | `08_rag_retrieval_metrics.md` | Precision@k, Recall@k, MRR, and nDCG |
| 9 | `09_rag_answer_quality_and_groundedness.md` | Evidence use, citations, and abstention |
| 10 | `10_llm_as_a_judge.md` | Judge design, calibration, biases, and limitations |
| 11 | `11_pairwise_and_preference_evaluation.md` | Blinded comparisons, ties, and preference criteria |
| 12 | `12_latency_throughput_usage_and_cost.md` | Performance measurements and accounting |
| 13 | `13_error_categorization_and_failure_analysis.md` | Stage-level diagnosis and actionable patterns |
| 14 | `14_experiment_tracking_and_reproducibility.md` | Versioned runs, artifacts, and environment records |
| 15 | `15_controlled_comparisons_and_uncertainty.md` | Paired comparisons, variation, and coverage limits |
| 16 | `16_prompt_and_model_regression_testing.md` | Repeatable comparisons and critical regressions |
| 17 | `17_optimization_and_trade_offs.md` | Quality, latency, and cost improvements with safeguards |
| 18 | `18_evaluation_gates_in_ci_cd.md` | Release criteria and layered automated checks |
| 19 | `19_online_feedback_and_production_evaluation.md` | Observed outcomes, drift, and controlled rollout |
| 20 | `20_evaluation_project_and_revision.md` | Reproducible suite and optimization report |

## Foundation path before fine-tuning

Before running Level 12 experiments, study Chapters **01–07, 12–16**, then complete a small baseline evaluation using the Chapter 20 report structure. You should have a versioned held-out dataset, explicit rubric, reusable comparison procedure, failure categories, and baseline quality/resource results. Study Chapters 08–09 when retrieval is part of the baseline. If using model judges or preference judgments, also complete Chapters 10–11 before relying on their scores.

## Chapter outlines

### 01. Why GenAI Evaluation Differs from Conventional Testing

- Compare deterministic application contracts with variable model behavior.
- Distinguish unit/integration tests, task-quality evaluation, and operational monitoring.
- Explain multiple acceptable answers and repeated-run variability.
- Identify where exact expected values remain appropriate.

**Practice:** Separate endpoint tests from quality checks for a summarization service.

**Checkpoint:** Explain why passing schema validation does not establish useful output.

### 02. Task-Specific Quality Criteria

- Define users, tasks, expected outcomes, and consequential failure types.
- Translate requirements into observable criteria and anchored scoring rubrics.
- Separate hard requirements from preferences and operational budgets.
- Define abstention behavior and acceptable uncertainty.

**Practice:** Write a rubric with examples of acceptable, borderline, and failing output.

**Checkpoint:** Explain what a passing score means for the application.

### 03. Golden Datasets and Representative Cases

- Collect typical, difficult, ambiguous, unsupported, and adversarial cases.
- Record inputs, references/evidence, expected labels or facts, and provenance.
- Separate development/selection data from final held-out assessment.
- Prevent duplicate, source, user, and temporal leakage where relevant.
- Version labels and document incomplete or uncertain reference answers.

**Practice:** Build a small dataset with coverage categories and explicit split rules.

**Checkpoint:** Explain which user populations and failure modes the dataset does not cover.

### 04. Human Evaluation

- Create annotation instructions and concrete scoring anchors.
- Blind reviewers to candidate identities where feasible.
- Review overlapping samples and record disagreement.
- Adjudicate uncertain cases without hiding genuine ambiguity.
- Consider reviewer expertise, fatigue, privacy, and annotation effort.

**Practice:** Review sample outputs independently where possible and reconcile disagreements.

**Checkpoint:** Distinguish reviewer preference from evidence-supported task correctness.

### 05. Exact-Match and Task-Specific Metrics

- Use exact match for tasks with genuinely fixed acceptable outputs.
- Define normalization without erasing meaningful errors.
- Compare classification accuracy, precision/recall/F1, and extraction field accuracy as appropriate.
- Introduce overlap-based text metrics and their limitations for open-ended answers.
- Define aggregation, denominators, invalid outputs, and missing-result treatment.

**Practice:** Score the same examples with a suitable metric and a misleading metric, then explain the difference.

**Checkpoint:** Connect each metric to the task behavior it actually measures.

### 06. Hallucination, Correctness, Relevance, and Faithfulness

- Distinguish factual correctness from support in supplied evidence.
- Define relevance, completeness, unsupported claims, and contradictions.
- Separate an answer's fluency from its truth or source fidelity.
- Use evidence-backed claim checks and mark unverifiable cases explicitly.

**Practice:** Label answers that are correct but unsupported, faithful to an incorrect source, irrelevant, or fabricated.

**Checkpoint:** Explain why these dimensions must not be collapsed into one vague quality label.

### 07. Evaluating Structured Outputs

- Separate parse success, schema validity, field accuracy, and business-rule compliance.
- Evaluate missing values, extra fields, enums, nested records, and source evidence.
- Track refusals, truncation, invalid responses, and unsupported requests explicitly.
- Report both field-level and complete-record performance where useful.

**Practice:** Score prepared outputs that are valid JSON but contain wrong values.

**Checkpoint:** Explain how invalid outputs contribute to the reported result rather than silently excluding them.

### 08. RAG Retrieval Metrics

- Define relevance judgments, ranked results, cutoffs, and duplicate handling.
- Calculate Precision@k and Recall@k with explicit denominators.
- Explain reciprocal rank and MRR for finding the first relevant result.
- Calculate DCG/nDCG using a stated graded-relevance convention and ideal ranking.
- Discuss incomplete judgments, queries with no relevant documents, and document-versus-passage granularity.
- Distinguish relevance metrics from ANN agreement with exact neighbors.

**Practice:** Compute metrics for a tiny ranked result set by hand and with code.

**Checkpoint:** Choose metrics that reflect the application's actual retrieval needs.

### 09. RAG Answer Quality and Groundedness

- Evaluate retrieval and generation independently before inspecting the full pipeline.
- Assess answer correctness, evidence coverage, faithful use, and citation support.
- Verify citation identifiers and whether cited passages support their claims.
- Include unanswerable, conflicting-source, stale-source, and permission-restricted cases.
- Keep authorization tests distinct from relevance scores.

**Practice:** Compare answer quality with retrieved versus known-sufficient evidence to diagnose stage failures.

**Checkpoint:** Explain whether a failure comes from absent evidence or misuse of available evidence.

### 10. LLM-as-a-Judge

- Define judge inputs, rubrics, output contracts, and evidence boundaries.
- Calibrate against a human-reviewed set and inspect systematic disagreements.
- Discuss position, verbosity, style, self-preference, and model-family biases.
- Treat evaluated content as untrusted and test judge susceptibility to injected instructions.
- Version judge models/prompts and sample repeat judgments for stability.
- Avoid using uncalibrated scores as factual ground truth or sole release authority.

**Practice:** Compare judge labels with reviewed labels and categorize disagreements.

**Checkpoint:** State where the judge is useful and where independent verification is required.

### 11. Pairwise Comparisons and Preference Evaluation

- Compare candidates using explicit task criteria and allow ties or abstentions.
- Randomize or swap candidate order to inspect position effects.
- Distinguish preference from absolute acceptability.
- Define win-rate denominators and treatment of ties, missing results, and failures.

**Practice:** Run a small blinded comparison with reasons tied to rubric criteria.

**Checkpoint:** Explain why winning against a weak baseline does not establish production readiness.

### 12. Latency, Throughput, Token Usage, and Cost

- Measure end-to-end and stage latency; distinguish time to first token from completion time.
- Report percentiles with workload, sample count, and concurrency.
- Track input/output usage, retries, cache behavior, and missing usage fields.
- Separate provider-reported values from local estimates.
- Calculate cost using verified rates and explicit accounting assumptions.
- Compare quality and reliability under the same workload, not speed alone.

**Practice:** Produce a measurement table for two configurations, including failures and unavailable measurements.

**Checkpoint:** Explain the conditions under which performance comparisons are valid.

### 13. Error Categorization and Failure Analysis

- Categorize input, parsing, retrieval, context, generation, validation, and infrastructure failures.
- Distinguish symptoms from supported root-cause hypotheses.
- Group results by task, language, source type, and other relevant slices.
- Prioritize fixes by severity, frequency, user impact, and feasibility.

**Practice:** Review failed cases and propose one targeted change for each recurring category.

**Checkpoint:** Identify what evidence would confirm the suspected cause.

### 14. Experiment Tracking and Reproducibility

- Version datasets, labels, prompts, schemas, retrieval settings, and model identifiers.
- Record code/dependency versions, seeds where supported, hardware, dates, and raw outcomes.
- Preserve run manifests, derived metrics, and reviewer decisions.
- Protect sensitive inputs and outputs through controlled storage and retention.
- Document nondeterminism and limits of rerunning hosted models.

**Practice:** Create a manifest sufficient to audit one baseline/candidate comparison.

**Checkpoint:** Trace each reported score to its cases, outputs, and configuration.

### 15. Controlled Comparisons and Uncertainty

- Compare candidates on matched cases with controlled settings and workload.
- Repeat selected cases to inspect stochastic variation.
- Introduce confidence intervals or bootstrap estimates with stated assumptions.
- Discuss small samples, rare failures, subgroup uncertainty, and repeated experiment selection.
- Reserve a final assessment set and avoid tuning to it repeatedly.

**Practice:** Report a quality difference with coverage limits and uncertainty rather than only a point estimate.

**Checkpoint:** Explain why a small observed gain may not support a confident improvement claim.

### 16. Prompt and Model Regression Testing

- Maintain stable cases for important successful behavior and past failures.
- Compare task metrics and critical-case outcomes against a versioned baseline.
- Test prompt, model, tokenizer/template, retrieval, and dependency changes where applicable.
- Define acceptable variation and review unexpected differences.
- Keep deterministic software checks separate from potentially flaky live evaluations.

**Practice:** Introduce a deliberate regression and verify the comparison report exposes it.

**Checkpoint:** Explain how aggregate improvements can conceal a critical subgroup regression.

### 17. Optimization from Measured Trade-offs

- Select one diagnosed quality, latency, or cost issue and state a hypothesis.
- Compare prompt simplification, model choice, context selection, retrieval tuning, and output budgets.
- Consider batching, concurrency, and caching with correctness and isolation checks.
- Inspect quality/resource trade-offs instead of minimizing one metric blindly.
- Re-evaluate after each meaningful change and record unsuccessful experiments.

**Practice:** Make one targeted optimization and compare it with the unchanged baseline.

**Checkpoint:** Justify the change using measured benefit and acceptable regressions.

### 18. Evaluation Gates in CI/CD

- Layer fast offline checks, fixed regression evaluations, and optional live comparisons.
- Define thresholds, critical failures, sample requirements, and reviewer escalation.
- Version baselines and prevent missing/failed evaluations from silently passing.
- Keep secrets and private evaluation data out of public logs.
- Attach reports to changes and support rollback when release criteria fail.

**Practice:** Write a small gate that catches a critical failure and reports inconclusive evaluation explicitly.

**Checkpoint:** Explain which checks block a release and why.

### 19. Online Feedback and Production Evaluation

- Distinguish explicit ratings, observed task outcomes, and noisy behavioral signals.
- Collect permitted, minimal feedback with provenance and retention controls.
- Review sampled failures, distribution shifts, and delayed outcomes.
- Introduce shadow evaluation, canary rollout, and controlled experiments conceptually.
- Convert verified production failures into reviewed regression cases without leaking private data.
- Avoid treating user satisfaction alone as correctness or safety evidence.

**Practice:** Design a feedback-to-dataset workflow with review and rollback triggers.

**Checkpoint:** Explain how online evidence complements rather than replaces offline assessment.

### 20. Evaluation Project and Revision

- Create a reproducible evaluation suite for one GenAI application.
- Compare two prompts, models, or configurations on the same cases.
- Evaluate retrieval separately where the application uses RAG.
- Implement regression checks and one justified quality/resource optimization.
- Document failures, uncertainty, release criteria, and remaining limitations.

**Practice:** Complete the report below and demonstrate that an introduced regression is detected.

**Checkpoint:** Defend whether the candidate should be adopted, revised, rejected, or assessed with more data.

## Level deliverable: Evaluation and optimization report

Create `evaluation_and_optimization_report.md` in this folder with:

1. Application scope, task rubric, critical failures, and resource requirements.
2. A versioned dataset with at least twenty representative held-out cases where feasible, provenance, split rules, and coverage limitations.
3. A baseline and candidate evaluated on the same cases, with model/prompt/configuration identifiers.
4. Deterministic validation results, task-quality metrics, and reviewed example outputs.
5. Separate retrieval and answer-quality results for a RAG application; mark these not applicable otherwise.
6. Human review procedures and judge calibration results if a model judge is used.
7. Repeated-run observations and uncertainty/coverage qualifications.
8. Latency, throughput, usage, and cost under a documented workload where measurable.
9. Failure categories, critical subgroup regressions, and one controlled optimization experiment.
10. Reproducible run manifests, regression checks, proposed CI/CD gates, and an online-feedback plan.
11. A recommendation with evidence, known limitations, and next actions.

A notebook or command-line runner is sufficient. Prepared outputs support metric and validation exercises but must be labeled as fixtures. Do not present fixture results as live model quality or hypothetical estimates as measured performance. A small dataset is a learning baseline, not proof of production reliability.

## Suggested format for each note

1. Learning objectives and the evaluation question being answered.
2. Definitions, assumptions, and a concrete example.
3. Rubric, metric formula, or evaluation-flow diagram.
4. A small worked calculation or runnable check.
5. Interpretation, uncertainty, and failure examples.
6. Reproducibility, privacy, and implementation constraints.
7. Exercise and revision questions with answers.
8. References and optional extensions.

Define relevance conventions, scoring scales, aggregation, and missing-result treatment explicitly. Verify current evaluation-tool APIs, model versions, and pricing when writing implementation notes.

## Completion checklist

- [ ] Distinguish software correctness tests from model-quality evaluation.
- [ ] Define task criteria and anchored rubrics.
- [ ] Create representative datasets with isolated assessment cases.
- [ ] Conduct human review and record disagreement.
- [ ] Use appropriate task metrics and evaluate structured outputs beyond syntax.
- [ ] Distinguish correctness, relevance, faithfulness, and citation support.
- [ ] Calculate and interpret retrieval metrics when applicable.
- [ ] Calibrate any model judge and document its limitations.
- [ ] Compare candidates with controlled settings, ties, and uncertainty handled explicitly.
- [ ] Measure latency, throughput, usage, and cost with stated assumptions.
- [ ] Track runs and diagnose failures by stage and slice.
- [ ] Detect regressions and evaluate one targeted optimization.
- [ ] Define release gates and a production-feedback review process.
- [ ] Complete and review the evaluation and optimization report.

## Scope and next step

This level develops practical evaluation and evidence-based optimization. Advanced statistical experimentation and large-scale evaluation platforms are optional extensions. Comprehensive threat modeling and security controls belong to Level 14; deployment and operational infrastructure to Level 15.

Next: **Level 14 — GenAI Security and Responsible AI**. If studying this level as a prerequisite for fine-tuning, return to [Level 12: Fine-Tuning and Model Customization](<../Level 12/README.md>) after completing the foundation path. See the [main course outline](../README.md).
