# Level 12: Fine-Tuning and Model Customization

**Goal:** Determine when a model should be customized and understand practical fine-tuning workflows.

This README is the plan for creating notes one by one. Keep numbered Markdown notes directly in `Level 12`, following the previous levels. The filenames below are planned files, not existing chapter links.

**Scope note:** Training foundation models from scratch is outside the core course. The main exercises focus on instruction tuning of a small language model or a supported hosted model.

## Prerequisites

- Review [Level 4: LLM Fundamentals and Inference](<../Level 4/README.md>), especially training stages, SFT, and quantization.
- Apply prompting, validation, and model API fundamentals from Levels 5–6. Review Level 8 when comparing customization with RAG.
- Complete the evaluation fundamentals in **Level 13 before running fine-tuning experiments**: task rubrics, held-out datasets, baseline comparisons, and failure analysis. See the [main course outline](../README.md).
- For local training, learn basic PyTorch tensors, devices, autograd, datasets, and training loops first. Hosted fine-tuning does not require implementing a local training loop.
- Use an isolated environment, a small permitted dataset, and a compatible base model. Set explicit compute, runtime, and cost limits before training.
- Levels 10–11 are media specializations and are not prerequisites for this language-model customization track.

## Learning outcomes

After completing this level, you should be able to:

- Choose among prompting, RAG, and fine-tuning using a measured problem statement.
- Curate instruction examples and create leakage-resistant train/validation/test splits.
- Explain SFT, PEFT, LoRA, and high-level QLoRA concepts.
- Configure and run a bounded training experiment through a suitable local or hosted route.
- Detect overfitting and compare base and customized models on a fixed test set.
- Version datasets, configurations, checkpoints, and adapters reproducibly.
- Assess deployment compatibility, regressions, resource needs, and remaining limitations.

## Study order and planned note files

| Order | Planned note filename | Focus |
|---|---|---|
| 1 | `01_customization_decision_framework.md` | Prompting versus RAG versus fine-tuning |
| 2 | `02_fine_tuning_suitability_and_baselines.md` | Failure diagnosis, success criteria, and stopping rules |
| 3 | `03_dataset_curation_and_quality_checks.md` | Permissions, coverage, consistency, and duplicates |
| 4 | `04_train_validation_and_test_splits.md` | Leakage prevention and held-out evaluation |
| 5 | `05_instruction_examples_and_data_formats.md` | Conversations, templates, labels, and loss masking |
| 6 | `06_supervised_fine_tuning.md` | Training objective and the SFT lifecycle |
| 7 | `07_parameter_efficient_fine_tuning.md` | Frozen parameters and trainable components |
| 8 | `08_lora_and_adapters.md` | Low-rank updates, configuration, and compatibility |
| 9 | `09_quantization_and_qlora.md` | Quantized base weights and trainable adapters |
| 10 | `10_training_configuration_and_hyperparameters.md` | Learning rate, batches, steps, precision, and limits |
| 11 | `11_overfitting_and_generalization.md` | Validation signals and regression risks |
| 12 | `12_hosted_and_local_fine_tuning.md` | Execution routes, constraints, and data handling |
| 13 | `13_checkpoints_versioning_and_reproducibility.md` | Artifacts, lineage, recovery, and experiment manifests |
| 14 | `14_before_and_after_evaluation.md` | Fair comparisons, improvements, and regressions |
| 15 | `15_deploying_customized_models.md` | Loading adapters, serving contracts, and rollback |
| 16 | `16_guided_fine_tuning_project.md` | A small end-to-end customization experiment |
| 17 | `17_practice_and_revision.md` | Consolidation and the level report |

## Chapter outlines

### 01. Prompt Engineering versus RAG versus Fine-Tuning

- Compare inference-time instructions, retrieved evidence, and weight updates.
- Distinguish changing behavior or format from supplying current knowledge.
- Explain that these approaches may be combined.
- Consider maintenance, data availability, privacy, cost, and deployment requirements.
- Recognize that fine-tuning does not guarantee reliable factual storage or eliminate hallucinations.

**Practice:** Recommend an approach for style consistency, changing policy documents, and structured extraction.

**Checkpoint:** Explain what each approach changes and why that addresses the chosen problem.

### 02. When Fine-Tuning Is and Is Not Appropriate

- Diagnose a recurring failure using representative examples.
- Establish a prompt-only or RAG baseline before training.
- Define target improvements, acceptable regressions, and resource limits.
- Check base-model support, licensing, task suitability, and available training examples.
- Identify situations where a conventional classifier, validation rule, better retrieval, or stronger model is sufficient.

**Practice:** Write an experiment proposal with a measurable go/no-go criterion.

**Checkpoint:** Justify training through evidence rather than treating it as a mandatory upgrade.

### 03. Dataset Curation and Quality Checks

- Collect permitted, representative instruction-response examples.
- Review correctness, consistency, diversity, and task coverage.
- Remove or handle duplicates, contradictory targets, sensitive data, and irrelevant examples.
- Audit label distributions and missing edge cases.
- Record source provenance, annotation guidance, and review decisions.
- Discuss synthetic-data limitations and independent review of generated examples.

**Practice:** Audit a small dataset and produce an accepted/rejected-example report.

**Checkpoint:** Explain why increasing example count cannot compensate for systematically incorrect targets.

### 04. Training, Validation, and Test Splits

- Assign training data to learning, validation data to selection, and test data to final assessment.
- Split by document, user, entity, time, or source when needed to avoid related examples crossing boundaries.
- Detect exact and near-duplicate leakage.
- Keep few-shot demonstrations and synthetic generation seeds/sources from contaminating held-out cases.
- Reserve the test set before prompt and hyperparameter iteration.

**Practice:** Design split rules for multiple examples derived from the same source documents.

**Checkpoint:** Explain why a random row split may overstate generalization.

### 05. Instruction-Tuning Examples and Data Formats

- Compare instruction/input/output records with conversation formats.
- Use the selected model's supported chat template and special tokens.
- Define which tokens contribute to the training loss where configurable.
- Handle truncation, padding, sequence length, and packing boundaries carefully.
- Validate schemas, message ordering, and target outputs before training.

**Practice:** Convert reviewed examples into a supported format and inspect the tokenized training targets.

**Checkpoint:** Verify that the intended responses are actually included in the learning objective.

### 06. Supervised Fine-Tuning

- Trace tokenized examples, forward computation, loss, gradients, updates, and evaluation.
- Distinguish SFT from pretraining, preference optimization, and inference.
- Compare full-parameter updates with restricted updates.
- Introduce training/evaluation modes and checkpoint selection.
- Explain that the exact loss and masking depend on the task and implementation.

**Practice:** Annotate a small training lifecycle or inspect a framework-managed SFT run configuration.

**Checkpoint:** Explain which parameters change and how target responses supervise them.

### 07. Parameter-Efficient Fine-Tuning (PEFT)

- Define frozen parameters and trainable task-specific components.
- Introduce adapters, low-rank adaptation, and prompt/prefix tuning conceptually.
- Compare trainable parameter count with total runtime memory.
- Discuss storage, portability, serving support, and quality trade-offs.
- Distinguish learned soft prompts from ordinary text prompting.

**Practice:** Inspect trainable versus total parameter counts for a toy configuration.

**Checkpoint:** Explain why fewer trainable parameters do not eliminate base-model loading costs.

### 08. LoRA and Adapter Concepts

- Explain low-rank updates to selected weight matrices conceptually.
- Introduce rank, scaling, dropout, and target modules.
- Record the exact base model and revision required by an adapter.
- Compare separate adapter loading with merging where supported.
- Discuss compatibility, multiple adapters, and risks from mismatched components.

**Practice:** Identify target modules and record a minimal LoRA configuration for the chosen model.

**Checkpoint:** Distinguish a LoRA adapter artifact from a complete standalone model.

### 09. Quantization and QLoRA at a High Level

- Review reduced-precision representations and quantization error.
- Explain QLoRA as training low-rank adapters while keeping a quantized base model frozen.
- Introduce computation precision, quantized storage, and optimizer-state memory separately.
- Discuss activation memory, sequence length, and hardware/library compatibility.
- Explain that quantization is not itself instruction tuning.

**Practice:** Draw the frozen-base/trainable-adapter path and list all major memory contributors.

**Checkpoint:** Explain why quantized base weights do not imply every training computation uses the same low-bit format.

### 10. Training Configuration and Hyperparameters

- Configure learning rate, schedule, epochs/steps, batch size, and gradient accumulation.
- Record maximum sequence length, precision, optimizer, and checkpoint/evaluation intervals.
- Introduce gradient clipping and memory-saving options where supported.
- Perform a small smoke run to catch invalid batches, non-finite loss, and memory problems.
- Bound runtime, storage, checkpoints, and hosted-job cost.
- Change configurations systematically rather than searching blindly.

**Practice:** Prepare a small-run configuration and estimate its workload with stated assumptions.

**Checkpoint:** Distinguish microbatch size, accumulated effective batch size, and total training steps.

### 11. Overfitting and Generalization

- Compare training and validation loss with task-specific evaluation.
- Inspect memorization, template dependence, and narrow-domain regressions.
- Discuss early stopping, checkpoint selection, and data improvements.
- Evaluate unfamiliar inputs and retain important base-model capabilities.
- Explain why lower training loss alone does not prove a better application.

**Practice:** Analyze sample learning curves and validation outputs to choose a checkpoint or stop the experiment.

**Checkpoint:** Identify both underperforming training and overfitting without consulting the final test set repeatedly.

### 12. Hosted Fine-Tuning versus Local Fine-Tuning

- Compare supported models, methods, formats, controls, and artifact access.
- Trace hosted upload, job submission, status checks, cancellation, and resulting model identifiers.
- Trace local environment setup, model loading, training, and artifact saving.
- Compare hardware, cost, privacy, retention, licensing, and operational effort.
- Verify current service and framework capabilities rather than assuming feature parity.

**Practice:** Choose one execution route and document a feasible alternative.

**Checkpoint:** Explain which parts of the training and deployment lifecycle remain under application control.

### 13. Model Checkpoints, Versioning, and Reproducibility

- Version datasets, split manifests, prompts/templates, configurations, and dependencies.
- Record base-model revisions, tokenizer versions, adapters, seeds, and hardware.
- Distinguish resumable training checkpoints from inference-ready artifacts.
- Preserve optimizer/scheduler state when needed for resumption.
- Store evaluation results alongside artifact identifiers and protect sensitive data.
- Document nondeterminism and avoid claiming exact reproducibility across all environments.

**Practice:** Create an experiment manifest linking source data to a selected checkpoint and its results.

**Checkpoint:** Identify everything required to load the artifact and everything additionally required to resume training.

### 14. Evaluation Before and After Fine-Tuning

- Compare the base and customized models on the same held-out cases and rubric.
- Keep prompts, decoding, and token budgets matched where appropriate; document required template differences.
- Measure correctness, format compliance, task quality, and critical regressions.
- Check unrelated/generalization cases and unsupported requests.
- Record latency, resource usage, and cost separately from output quality.
- Discuss small-test-set uncertainty and avoid overstating results.

**Practice:** Produce a side-by-side results table with reviewed successes and failures.

**Checkpoint:** Decide whether measured improvement justifies the training and serving costs.

### 15. Deployment Considerations for Customized Models

- Load the intended base revision, tokenizer, and adapter or full checkpoint.
- Verify serving-library support, precision, context settings, and chat formatting.
- Validate outputs through the same application contracts used for the baseline.
- Run a small inference and compatibility check before promotion.
- Plan artifact access control, rollback, model versioning, and monitoring.
- Discuss retention, deletion, and privacy implications of training data encoded into artifacts.

**Practice:** Prepare an inference script and deployment checklist for the selected artifact.

**Checkpoint:** Explain how a training result becomes a reviewable serving candidate rather than an automatically approved production model.

### 16. Guided Fine-Tuning Project

- Select one narrow task and establish a baseline.
- Curate a small instruction dataset with isolated validation and test sets.
- Choose a suitable small local model or supported hosted service.
- Run a bounded SFT experiment, using LoRA/QLoRA only where appropriate and supported.
- Evaluate the selected artifact and record improvements, regressions, and compute needs.
- Save reproducible artifacts and an inference demonstration.

**Practice:** Complete one end-to-end customization experiment within the defined resource budget.

**Checkpoint:** Trace the final recommendation to the original problem, dataset, configuration, and held-out evidence.

### 17. Practice and Revision

- Compare prompting, RAG, SFT, PEFT, LoRA, and QLoRA.
- Review data quality, leakage prevention, training controls, and overfitting.
- Inspect artifact lineage and deployment compatibility.
- Summarize base-versus-customized results and decide whether to retain the customization.
- Complete the report below.

**Checkpoint:** Explain both why customization helped or failed and what experiment should follow.

## Level deliverable: Fine-tuning experiment report

Create `fine_tuning_experiment_report.md` in this folder with:

1. Problem statement, baseline failures, alternatives, and measurable success criteria.
2. Dataset provenance, permissions, quality checks, format, and split rules.
3. A small instruction-tuning dataset with versioned train/validation/test manifests.
4. Base-model identifier/revision, tokenizer/template, method, configuration, environment, and resource budget.
5. A guided training run, checkpoint-selection rationale, and relevant training/validation observations.
6. Base-versus-customized evaluation on a fixed held-out test set of at least twenty cases where feasible, including edge cases and regression checks.
7. Reviewed improvements and failures, with task metrics and uncertainty/coverage limitations.
8. Runtime, hardware, memory, artifact size, and cost where available; estimates explicitly labeled.
9. Saved artifact identifiers, lineage, an inference demonstration, and deployment/rollback considerations.
10. A recommendation to adopt, revise, or reject the customization, with reasons and remaining risks.

A notebook, command-line project, or documented hosted workflow is sufficient. A small model and short training run are appropriate; paid services and large-model training are not required. If access or hardware prevents execution, complete preparation and mark the training/evaluation portions pending. Fixtures and hypothetical results do not count as a completed fine-tuning experiment.

## Suggested format for each note

1. Learning objectives and prerequisite concepts.
2. Intuition and a concrete customization example.
3. Data flow, parameter-update diagram, or worked calculation.
4. Minimal configuration or implementation.
5. Validation, evaluation, and resource measurements.
6. Failure cases, leakage risks, compatibility, and trade-offs.
7. Exercise and revision questions with answers.
8. References and optional extensions.

Verify current framework APIs, hosted fine-tuning capabilities, supported models, licensing, and pricing when writing implementation notes. Keep examples small and clearly distinguish observed results from estimates.

## Completion checklist

- [ ] Choose among prompting, RAG, and fine-tuning using evidence.
- [ ] Complete evaluation foundations before running training experiments.
- [ ] Curate permitted, consistent instruction examples.
- [ ] Create train/validation/test splits without source or duplicate leakage.
- [ ] Validate data formats, tokenization, templates, and training targets.
- [ ] Explain SFT, PEFT, LoRA, and QLoRA distinctly.
- [ ] Configure a bounded training run and inspect validation behavior.
- [ ] Detect overfitting and evaluate generalization/regressions.
- [ ] Complete one guided local or hosted fine-tuning exercise.
- [ ] Version datasets, configurations, checkpoints, and adapters.
- [ ] Compare base and customized models fairly on held-out cases.
- [ ] Demonstrate artifact loading and document deployment limitations.
- [ ] Complete and review the fine-tuning experiment report.

## Scope and next step

Training foundation models from scratch is outside the core course. Detailed preference-optimization training, distributed training, and advanced adapter research are optional extensions. Media-specific customization can build on Levels 10–11 after the core workflow is understood.

Use **Level 13 — GenAI Evaluation and Optimization** as a prerequisite and continuing reference. After this specialization, deepen evaluation and proceed to security and production engineering in Levels 14–15. See the [main course outline](../README.md).
