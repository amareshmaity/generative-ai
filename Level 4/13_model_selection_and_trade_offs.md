# 13. Model Selection and Trade-offs

## Learning Objectives

By the end of this chapter, you should be able to:

- Define task-specific success criteria before choosing a model.
- Compare quality, instruction following, structured-output support, modalities, and context requirements.
- Measure time to first token, total latency, throughput, and output length where available.
- Compare hosted usage costs with self-managed infrastructure and operating effort.
- Consider decoding controls, versioning, privacy, and deployment constraints.
- Evaluate representative, difficult, and unanswerable requests using a fixed rubric.
- Record uncertainty and avoid treating public benchmark results as sufficient evidence for a specific application.
- Justify a model selection with measured results and explicit requirements.

<br/>

## 1. Start with the Task, Not the Model

Model selection should begin with a clear definition of the task and what counts as success. A model that performs well on a public benchmark may still be unsuitable for a particular application because the real workload has different inputs, constraints, output formats, latency targets, or failure costs.

Before comparing models, define:

- **Task:** What should the model do?
- **Users and operating context:** Who will use the output, and under what conditions?
- **Success criteria:** What makes an answer acceptable?
- **Failure criteria:** Which mistakes are unacceptable or costly?
- **Constraints:** What are the latency, cost, privacy, hardware, and deployment requirements?
- **Evaluation set:** Which representative examples will be used to compare candidates?

Do this before looking at model rankings. Otherwise, it is easy to select a model based on a headline benchmark or an appealing demo that does not match the actual use case.

<br/>

## 2. Define Task-Specific Success Criteria

Success criteria should be observable and measurable wherever possible. They vary by task.

| Task type | Possible success criteria |
|---|---|
| Classification | Accuracy, precision, recall, F1, or task-specific error costs |
| Information extraction | Field-level correctness, schema validity, completeness |
| Summarization | Coverage of key facts, factual consistency, length constraints |
| Question answering | Correctness against known answers, evidence support, appropriate abstention |
| Code generation | Unit-test pass rate, correctness, security checks, maintainability |
| Structured output | Valid JSON/schema compliance, required-field coverage, value correctness |
| Multimodal tasks | Correct interpretation of relevant text, image, audio, or video inputs |
| Conversational assistance | Instruction following, usefulness, consistency, safety, and user-specific criteria |

No single metric covers every dimension. For example, a response can be valid JSON but contain incorrect values. A code sample can pass a few tests while still having security or maintainability problems.

<br/>

### Define hard constraints and soft preferences

- **Hard constraints** are requirements that must be met, such as data residency, valid schema output, or a maximum acceptable latency.
- **Soft preferences** are qualities to optimize when hard constraints are satisfied, such as a lower cost or more natural writing.

A candidate that violates a hard constraint should not win merely because its average score is higher.

<br/>

## 3. Build a Representative Evaluation Set

A useful evaluation set should resemble the real workload. Include at least three categories:

1. **Representative requests:** Common inputs that reflect normal usage.
2. **Difficult requests:** Edge cases, long contexts, ambiguous instructions, multiple constraints, or other challenging inputs.
3. **Unanswerable requests:** Cases where the model lacks sufficient information, the question has no supported answer, or the correct behavior is to ask for clarification or abstain.

Unanswerable examples are important because a model should not be rewarded only for producing an answer. In some applications, recognizing uncertainty is part of correct behavior.

Keep the evaluation set fixed while comparing candidates. If prompts or test examples change between models, differences in results become harder to interpret.

<br/>

### Avoid accidental leakage

Do not tune prompts repeatedly against the final evaluation set and then treat its score as an unbiased estimate of general performance. Use a development set to improve prompts and a separate held-out set for final comparison when practical. For high-impact applications, review the test set periodically and maintain an appropriate governance process.

<br/>

## 4. Compare Capability and Compatibility

A model's selection criteria should include more than general answer quality.

### Quality and instruction following

Evaluate whether the model:

- Answers the actual question.
- Follows constraints and requested formats.
- Handles conflicting or ambiguous instructions appropriately.
- Avoids unsupported claims.
- Admits uncertainty or abstains when appropriate.
- Performs consistently across representative and difficult cases.

<br/>

### Structured-output support

If an application requires JSON, function/tool-call structures, or a schema, check whether the model and endpoint support the needed output mode. Then validate the result. A documented structured-output feature can improve format reliability, but it does not guarantee that the values are correct.

<br/>

### Modalities

Confirm the input and output modalities needed by the application:

- Text only.
- Image input.
- Audio input or output.
- Video or other multimodal input, where supported.

A model should not be considered suitable for a modality merely because another model in the same family supports it. Check the exact model and endpoint.

<br/>

### Context requirements

Estimate the input length, including instructions, conversation history, retrieved documents, and formatting overhead. Check the model's context-window limit and the output budget. A large context window does not guarantee that the model will use every part of a long input equally well.

<br/>

### Controls and deployment constraints

Record whether the endpoint supports the required decoding parameters, stop sequences, output limits, seeds, structured output, and other controls. Also consider versioning, data-handling terms, regional availability, rate limits, and deployment restrictions.

<br/>

## 5. Measure Latency and Throughput

Performance is more than a single “speed” number.

- **Time to first token (TTFT):** Time from request submission until the first output token becomes available. It is particularly relevant for interactive applications.
- **Total latency:** Time until the complete response is returned. It depends on prompt processing, generation length, model behavior, serving load, and network overhead.
- **Throughput:** Amount of work completed per unit of time. It may be reported as tokens per second, requests per second, or another workload-specific measure.
- **Output length:** Number of generated tokens or another documented length measure. Longer outputs can increase total latency and usage cost.
- **Concurrency behavior:** How performance changes when several requests run at once.
- **Variability:** Differences in latency across repeated requests and under different load conditions.

Do not compare TTFT from one setup with total latency from another. Define the measurement precisely and use consistent conditions.

<br/>

### Measurement guidance

1. Use the same prompts and comparable output budgets.
2. Separate cold-start measurements from warmed-up steady-state measurements where relevant.
3. Run multiple trials.
4. Record the model version, provider/endpoint, region if relevant, and date of measurement.
5. Measure under realistic input lengths and concurrency.
6. Report a distribution or percentile values when possible, not only a single average.
7. Include failures, timeouts, and rate-limit behavior in the operational assessment.

Performance measured on a developer's laptop or during a quiet period may not represent production behavior.

<br/>

## 6. Compare Cost Fairly

Hosted and self-managed inference have different cost structures.

### Hosted inference

Potential cost components include:

- Input-token charges.
- Output-token charges.
- Separate charges for cached input, reasoning tokens, tools, or modalities where the provider documents them.
- Minimum usage, subscription, or reserved-capacity costs.
- Rate-limit or throughput constraints that may require a different service tier.

Provider pricing and accounting rules can change. Record the date and exact pricing assumptions used in a comparison.

<br/>

### Self-managed inference

Potential cost components include:

- Hardware purchase or rental.
- GPU/CPU memory and capacity.
- Storage and network costs.
- Electricity and cooling for owned infrastructure.
- Engineering time for deployment, monitoring, security, scaling, and upgrades.
- Reliability work, incident response, and maintenance.
- Idle capacity and utilization.

Do not compare hosted token pricing only with the rental price of a GPU. Include the operating effort and the actual utilization of self-managed capacity. Likewise, do not assume self-hosting is cheaper without estimating workload volume, hardware utilization, and maintenance.

<br/>

### Cost per successful task

A useful application-level metric is:

$$
\text{cost per successful task} =
\frac{\text{total evaluation cost}}{\text{number of successful tasks}}
$$

Define “successful” before calculating the metric. If one model is cheaper per request but fails more often, it may not be cheaper per successful task.

<br/>

## 7. A Fixed Rubric for Comparing Models

Create a rubric before running the test. One possible example is below; adapt the criteria and weights to the application rather than using these values universally.

| Dimension | Example evaluation question | Example measure |
|---|---|---|
| Correctness | Is the final answer correct? | Exact match, expert score, task metric |
| Instruction following | Did it satisfy all explicit requirements? | Pass/fail or rubric score |
| Structured output | Is the output valid and schema-compliant? | Parse and schema-validation rate |
| Uncertainty handling | Does it abstain or clarify when needed? | Appropriate-abstention rate |
| Safety / policy fit | Does it meet application requirements? | Reviewed test outcomes |
| TTFT | How quickly does output begin? | Milliseconds or seconds |
| Total latency | How long until completion? | Seconds and percentiles |
| Throughput | How much work can it handle? | Tokens/s or requests/s |
| Cost | What does it cost for the workload? | Cost per request/task/success |
| Operational fit | Can it be deployed and maintained? | Requirements checklist |

Use the same rubric for every candidate. If some criteria are hard constraints, report them separately rather than hiding them inside a weighted average.

<br/>

## 8. Decision Matrix: Two Candidate Models

The table below is a template for comparing two candidates on the same test set. Fill in measured results; do not invent values to make a decision look precise.

| Criterion | Requirement / importance | Candidate A | Candidate B | Pass / interpretation |
|---|---|---|---|---|
| Correctness on representative cases | Define target | Measure | Measure | Compare against target |
| Difficult-case performance | Define target | Measure | Measure | Inspect failure types |
| Unanswerable-case behavior | Define target | Measure | Measure | Check appropriate abstention |
| Instruction following | Define target | Measure | Measure | Apply same rubric |
| Structured-output validity | Required or optional | Measure | Measure | Validate with parser/schema |
| Required modalities | Must support needed inputs | Verify | Verify | Hard constraint |
| Context capacity | Must fit workload | Verify | Verify | Include input and output budgets |
| TTFT | Maximum or preference | Measure | Measure | Same method |
| Total latency | Maximum or preference | Measure | Measure | Same output budget |
| Throughput | Workload target | Measure | Measure | Same concurrency conditions |
| Cost per successful task | Budget | Estimate | Estimate | Include failures |
| Privacy and terms | Required controls | Verify | Verify | Hard constraint if applicable |
| Versioning and stability | Operational requirement | Verify | Verify | Document limitations |

<br/>

### How to make a decision

1. Eliminate candidates that fail hard requirements.
2. Compare quality on the fixed evaluation set.
3. Examine difficult and unanswerable cases separately.
4. Compare latency and throughput against service requirements.
5. Estimate cost per successful task.
6. Consider privacy, versioning, support, and operational effort.
7. Record the remaining uncertainty and what evidence would change the decision.

A single weighted score can help summarize a decision, but it should not conceal critical failures or uncertain measurements.

<br/>

## 9. Public Benchmarks: Useful but Insufficient

Public benchmarks can help narrow a candidate list, but they are not sufficient evidence that a model will perform well in a specific application.

Reasons include:

- The benchmark may not represent the application's input distribution.
- Evaluation prompts, scoring methods, or model versions may differ.
- A model may be strong on common cases but weak on the application's difficult cases.
- Benchmark scores may not measure latency, cost, privacy, schema compliance, or operational reliability.
- Public test examples may have appeared in training data or otherwise be familiar to the model.
- A score may hide variance and important failure categories.

Use public benchmarks as one source of evidence. Confirm suitability using a fixed, representative evaluation set and operational measurements from the intended deployment path.

<br/>

## 10. Record Uncertainty

A good model-selection decision states what is known, what remains uncertain, and how the uncertainty affects deployment.

Examples of uncertainty to record:

- The evaluation set is small or lacks certain user groups or task types.
- Results vary across repeated runs.
- Provider defaults or exact model revisions are not fully documented.
- Performance was measured at lower concurrency than production expects.
- Cost estimates rely on assumed token lengths or utilization.
- A hosted endpoint may change its underlying model version.
- The test set may not cover rare but high-impact failures.

Use a staged rollout, monitoring, or further testing when uncertainty is material. Do not claim that a candidate is “best” without specifying the task, evidence, and constraints under which it was selected.

<br/>

## 11. Practice: Compare Two Candidates

### Scenario

You are selecting a model for an application that answers questions from a fixed collection of documents and must return a JSON object with three fields. The application has a strict latency target and must avoid inventing answers when the documents do not contain the requested information.

<br/>

### Procedure

1. Define the JSON schema and the criteria for a correct answer.
2. Create a fixed test set with representative, difficult, and unanswerable questions.
3. Use the same input documents and prompts for Candidate A and Candidate B.
4. Record exact model versions, endpoint settings, context limits, output limits, and supported structured-output controls.
5. Measure answer correctness, schema validity, appropriate abstention, TTFT, total latency, output length, and cost.
6. Inspect failures by category rather than looking only at an overall average.
7. Eliminate candidates that violate hard requirements.
8. Record uncertainties and make a recommendation with evidence.

<br/>

### Results table template

| Metric | Candidate A | Candidate B | Requirement |
|---|---|---|---|
| Correct answers | Record | Record | Define target |
| Valid JSON | Record | Record | Define target |
| Appropriate abstention | Record | Record | Define target |
| Difficult-case score | Record | Record | Define target |
| TTFT p50 / p95 | Record | Record | Define limit |
| Total latency p50 / p95 | Record | Record | Define limit |
| Average output tokens | Record | Record | Observe/limit |
| Cost per successful task | Record | Record | Define budget |
| Privacy / versioning requirements | Verify | Verify | Must pass |

Do not fill the table with guessed measurements. The goal is to create a reproducible decision process.

<br/>

## 12. Common Misconceptions

- **“The highest public benchmark score is the best model for my application.”** Benchmark relevance, task-specific testing, cost, latency, and deployment constraints still matter.
- **“One overall score captures every important requirement.”** It can hide failures on hard constraints or unanswerable requests.
- **“The fastest model is automatically the best choice.”** It may fail the quality requirement.
- **“The most accurate model is automatically the best choice.”** It may be too slow, too expensive, unavailable in the required region, or incompatible with privacy constraints.
- **“Hosted cost is just the listed token price.”** Output length, usage categories, failures, service tiers, and operational constraints affect total cost.
- **“Self-hosting is always cheaper or more private.”** Both depend on actual infrastructure, configuration, maintenance, and data handling.
- **“A valid JSON response is a correct answer.”** Syntax and semantic correctness are different checks.
- **“A benchmark proves deployment performance.”** Real workload testing is still necessary.

<br/>

## 13. Answers and Checkpoint Review

### Suggested decision rationale

A defensible model-selection rationale should name the task, hard requirements, evaluation method, measured quality, latency, cost, operational constraints, and remaining uncertainty. For example, a candidate should be selected because it meets the required correctness and schema-validity thresholds on the fixed test set, stays within the latency and cost budgets, and satisfies privacy and deployment constraints—not merely because it ranks higher on a public leaderboard.

<br/>

### Checkpoint

**How do you justify a model selection?** Define explicit requirements first, compare candidates on the same representative, difficult, and unanswerable test cases, and measure task quality, instruction following, structured-output validity, latency, throughput, cost, and operational fit. Eliminate candidates that fail hard constraints, record uncertainty, and explain why the measured trade-offs fit the application.

<br/>

## Summary

Model selection is an application-specific decision. Define success and failure criteria before comparing candidates. Evaluate quality, instruction following, structured output, modalities, context capacity, latency, throughput, output length, cost, privacy, versioning, and deployment constraints on a fixed test set. Include representative, difficult, and unanswerable requests. Public benchmarks are useful evidence but cannot replace task-specific evaluation. A defensible selection is supported by measured results, explicit requirements, and a clear account of uncertainty.
