# Chapter 17: Model Limitations, Bias, Fairness, and Transparency

## Learning Objectives

By the end of this chapter, you should be able to:

- Document intended uses, excluded uses, uncertainty, and observed failure patterns for a GenAI application.
- Define relevant user and task slices for evaluation and formulate meaningful fairness questions.
- Compare subgroup outcomes while accounting for sample size, label quality, and uncertainty.
- Assess accessibility, uneven language performance, and risks from inappropriate inferences.
- Write useful transparency disclosures without treating disclaimers as substitutes for technical and operational controls.
- Review a small synthetic evaluation set by relevant slices and report limitations without overstating conclusions.

<br/>

## 1. Why Limitations and Fairness Need Explicit Treatment

A GenAI system may produce useful outputs for many requests while still failing systematically for particular tasks, languages, input formats, or user groups. Aggregate performance can hide these failures. A high overall score does not establish that the system performs adequately for every relevant population or use case.

**Model limitations** are known constraints on a system's reliability, capability, context, or appropriate use. **Bias** can arise from data, labels, system design, interaction patterns, or deployment context and may lead to systematic errors or unequal treatment. **Fairness** is not a single universal metric: it requires defining which outcomes matter, who may be affected, and which differences are relevant under the application's purpose and obligations. **Transparency** means communicating material information about the system's role, evidence, uncertainty, limitations, and appropriate use.

These topics should be addressed throughout the lifecycle: requirements, data preparation, evaluation, release decisions, user experience, monitoring, and incident response.

<br/>

### Core principle

A responsible limitation statement identifies what has and has not been evaluated, describes material uncertainty, and connects the finding to a practical control or usage boundary.

<br/>

## 2. Document Intended and Excluded Uses

A model card, system card, or application-level limitations document should explain the context in which the system was evaluated. The documentation should describe the application as deployed—not merely repeat a generic description of the underlying model.

<br/>

### Recommended sections

- **System overview:** What the application does and which model or components it uses.
- **Intended uses:** Tasks, user populations, input types, and operating conditions that were evaluated.
- **Excluded or restricted uses:** Tasks or decisions that are unsupported, prohibited, or require additional safeguards.
- **Human role:** Whether the system assists, recommends, drafts, or makes decisions.
- **Evaluation scope:** Datasets, languages, tasks, metrics, baselines, and test conditions.
- **Observed limitations:** Known failure patterns, edge cases, and weak performance areas.
- **Uncertainty:** Where evidence is limited, contradictory, or too small to support a firm conclusion.
- **Operational assumptions:** Required access controls, review steps, input constraints, and fallback behavior.
- **Update history:** Model, prompt, policy, dataset, and evaluation changes that affect the claims.

Avoid saying “works for all users” or “safe for any use” when testing covers only a narrow set of tasks. A limitation document should be specific enough to inform a release decision and a user's behavior.

<br/>

### Intended-use example

A workplace knowledge assistant may be evaluated for summarizing approved internal documents in two supported languages. Its documentation might state that it is intended to help employees locate and summarize information, that answers require source verification for consequential decisions, and that it has not been evaluated for legal advice, personnel decisions, or unsupported languages.

This is an example of scoped documentation, not a universal template for every workplace assistant.

<br/>

## 3. Distinguish Types of Limitations

Different limitations require different responses. A single generic disclaimer does not adequately describe them.

| Limitation type | Example | Possible response |
|---|---|---|
| Capability | The system struggles with complex multi-step calculations | Use a verified calculation tool or restrict the task |
| Knowledge or freshness | The model may not know recent changes | Retrieve current authoritative sources or disclose the cutoff |
| Grounding | The model may generate claims unsupported by retrieved documents | Add evidence checks, citations, or abstention behavior |
| Language coverage | Performance is weaker in some languages or dialects | Evaluate those slices and limit unsupported use |
| Input modality | OCR or audio transcription fails on certain formats | Validate inputs and offer an accessible alternative |
| Context limits | Long conversations may omit earlier details | Use bounded, validated state and show relevant context |
| Fairness | Error rates differ across relevant groups | Investigate data, labels, task design, and downstream impact |
| Security | Untrusted content may influence tool use | Use security boundaries, tool controls, and adversarial testing |
| Human factors | Users may over-trust confident language | Present evidence and uncertainty and support review |
| Deployment | Latency or service availability varies under load | Apply capacity controls and safe fallbacks |

State whether a limitation was directly observed, inferred from a known design constraint, or remains untested. These are different levels of evidence.

<br/>

## 4. Define Fairness Questions Before Measuring

Fairness evaluation should start with a concrete question about the application and its consequences, not with a metric selected merely because it is available.

Examples of questions include:

- Does the system make more consequential errors for one relevant group than another?
- Does it misunderstand dialects, code-switching, or particular input formats more often?
- Are recommendations or refusals distributed differently across comparable cases?
- Are users with assistive technologies able to access and correct the output?
- Are errors more costly for one group because the workflow offers fewer opportunities to appeal?
- Does the system rely on sensitive or proxy attributes in a way that is inappropriate for the task?
- Are the labels used for evaluation themselves reliable and appropriate across groups?

The correct questions depend on the application. A translation assistant, a customer-support classifier, and a system that informs access to essential services have different failure consequences and fairness requirements.

<br/>

### Define the unit of analysis

Be explicit about what is being compared:

- Individual examples, user sessions, decisions, or completed workflows.
- The model output alone or the final human-plus-system outcome.
- One language, task, product feature, or deployment condition.
- A single model version or performance across updates.

A model may have similar output-level scores across groups but still lead to unequal outcomes if the downstream workflow treats its outputs differently. Conversely, a group-level difference may be explained by task mix, data quality, or sampling. Investigation is needed before drawing causal conclusions.

<br/>

## 5. Choose Relevant Evaluation Slices

A **slice** is a subset of evaluation cases defined by a characteristic relevant to performance or impact. Slices can be defined by task, language, input type, context length, workflow stage, or—where lawful, appropriate, and justified—user-group attributes.

Potential slices include:

- Language and dialect.
- Task type or domain.
- Short versus long input.
- Text-only versus image, audio, or document input.
- Supported assistive-technology or accessibility pathway.
- High-impact versus low-impact workflow.
- Source quality or retrieval coverage.
- Relevant demographic groups, when collection and analysis are justified and permitted.
- Intersectional groups, when there is enough reliable data to analyze them responsibly.

Do not collect or infer sensitive attributes merely because subgroup analysis is possible. Define why an attribute is relevant, how it will be obtained lawfully and respectfully, how it will be protected, and who can access the results. If group membership is unknown or cannot responsibly be collected, do not invent it from names, writing style, images, or other unreliable proxies.

<br/>

### Slice design checklist

For every slice, record:

1. The question being investigated.
2. The reason the slice is relevant to the task or potential harm.
3. The inclusion criteria and source of the attribute.
4. The number of cases and how they were sampled.
5. The quality and limitations of the reference labels.
6. The metric and decision threshold, if applicable.
7. Whether the sample is representative of deployment.
8. What action would follow a concerning result.

Avoid slicing data repeatedly until an apparently large difference appears. Predefine primary slices where possible, label exploratory analyses as exploratory, and validate surprising findings on new data.

<br/>

## 6. Compare Outcomes Carefully

Use metrics that match the task. Examples include:

- Classification: precision, recall, false-positive rate, false-negative rate, calibration, and confusion matrices.
- Retrieval: recall at K, relevant-source coverage, and permission-related retrieval errors.
- Generation: groundedness, task completion, factual error rate, rubric scores, and human preference.
- Workflow outcomes: escalation rates, correction rates, time to resolution, or harmful-action rates.
- Accessibility: task completion, error recovery, navigation and comprehension barriers, and compatibility with assistive technology.

A single aggregate score may conceal important differences. However, no single subgroup metric is sufficient to establish fairness across every application. Metrics can conflict, and selecting a metric is a normative decision about which errors matter.

<br/>

### Sample size and uncertainty

Subgroup results can be unstable when a slice contains few cases. Report the denominator with each metric. Use confidence intervals or another appropriate uncertainty estimate where feasible. A small observed difference may be noise; a large observed difference from a tiny or biased sample may also be unreliable.

Do not interpret “no statistically significant difference” as proof of equal performance. The study may have too little power to detect a meaningful gap. Conversely, statistical significance alone does not establish practical importance.

<br/>

### Label quality

A reference label is not automatically ground truth. Labels can be incomplete, inconsistent, biased, outdated, or based on criteria that are inappropriate for the task. Before comparing groups, assess whether the same rubric is applied consistently and whether labels capture the intended outcome.

When label quality differs by slice, the metric may reflect annotation differences as well as model behavior. Document that limitation rather than presenting the result as a pure model effect.

<br/>

## 7. Metrics Are Evidence, Not a Complete Definition of Fairness

Some fairness metrics cannot generally be satisfied simultaneously when underlying base rates differ and predictions are imperfect. For example, parity in selection rates, equal false-positive rates, and equal calibration can impose different requirements. The correct choice depends on the application, relevant legal and ethical obligations, and the consequences of each error.

Before choosing a fairness criterion, document:

- Which outcome is being protected or improved.
- Which error types are most harmful.
- Whether the system makes or merely informs a decision.
- Whether labels and base rates are trustworthy.
- Which differences are acceptable, unacceptable, or require investigation.
- Which constraints arise from law, policy, or professional standards.
- How affected people can challenge or correct an outcome.

Avoid declaring a system “fair” solely because one metric is similar across groups. State the exact metric, dataset, version, uncertainty, and scope of the conclusion.

<br/>

## 8. Accessibility and Uneven Language Performance

Accessibility is part of system quality, not an optional visual layer. GenAI interfaces can create barriers through dense prose, ambiguous controls, inaccessible charts, non-semantic status messages, poor keyboard support, or failure to accommodate screen readers and other assistive technologies.

Consider whether users can:

- Navigate the workflow using keyboard or assistive technology.
- Understand error messages and next steps.
- Correct a model misunderstanding without repeating the entire task.
- Request a shorter, clearer, or alternative-format response.
- Inspect citations and supporting evidence accessibly.
- Understand when the system is uncertain or unavailable.
- Reach human support or appeal where needed.

Language performance may vary across languages, dialects, code-switching, transliteration, slang, and domain-specific terminology. Evaluate the languages the application claims to support. If reliable evaluation data is unavailable for a language, document that gap and avoid implying parity.

Do not equate fluent text with correct interpretation. A model may produce grammatically natural language while misunderstanding a user's intent or the cultural and domain context.

<br/>

## 9. Avoid Inappropriate Inferences

A model may infer personal traits, intentions, competence, risk, or other attributes from incomplete or irrelevant signals. Such inferences can be inaccurate, difficult to contest, and harmful when used in consequential workflows.

Controls should include:

- Define which attributes are necessary for the task.
- Prohibit unsupported inferences where they are not appropriate.
- Avoid using names, dialect, appearance, or other weak proxies to infer sensitive characteristics.
- Separate observed evidence from model interpretation.
- Require stronger evidence and qualified review for consequential conclusions.
- Provide correction and appeal paths where a person is affected.
- Test whether irrelevant attribute changes alter outputs in ways that are not justified by the task.

Counterfactual tests—changing one attribute while holding other relevant facts constant—can help identify sensitivity to that attribute. They do not, by themselves, prove the system is fair: the change may alter meaning, the test may miss indirect effects, and real-world context may be more complex.

<br/>

## 10. Transparency and Useful Disclosures

Transparency should help users and operators understand the system's role, limitations, and appropriate use. A useful disclosure is specific, understandable, and placed where it affects the decision.

Depending on the application, disclose:

- That AI is being used and what role it plays.
- Whether the output is a draft, recommendation, classification, or automated action.
- The kinds of sources or evidence used, where appropriate.
- Material uncertainty, missing evidence, or unsupported input types.
- Important known limitations and excluded uses.
- Whether human review is required and how to request it.
- How to correct an error, appeal an outcome, or reach a responsible contact.
- Relevant data handling and retention information, consistent with the actual system.

Avoid vague statements such as “AI may make mistakes” as the only disclosure. Explain which errors are known to occur and what users should do when the result matters.

<br/>

### Disclaimers do not replace controls

A disclaimer cannot compensate for an application that exposes private data, permits unauthorized actions, or uses an unvalidated model for a high-impact decision. Use engineering controls, policy enforcement, qualified review, access controls, and monitoring. Disclosures support informed use; they do not transfer every responsibility to the user.

<br/>

## 11. Example: Slice-Based Evaluation Report

The following values are **synthetic and illustrative only**. They demonstrate how to report subgroup metrics, not the performance of a real model.

Suppose an assistant is evaluated on a binary classification task. A “positive” prediction is treated as the policy-relevant event, and the table reports recall on examples whose reference label is positive.

| Slice | Positive cases evaluated | True positives | Recall | Limitation |
|---|---:|---:|---:|---|
| Slice A | 100 | 90 | 90% | Synthetic example; label quality assumed adequate |
| Slice B | 20 | 15 | 75% | Small denominator; estimate is less stable |
| Slice C | 12 | 10 | 83.3% | Very small denominator; avoid strong conclusions |

Tasks:

1. State the observed recall for each slice.
2. Explain why Slice B's lower point estimate does not automatically establish a systematic disparity.
3. Explain why Slice C's higher point estimate does not establish that it performs better in general.
4. Identify the label-quality and sampling questions you would investigate.
5. Recommend whether to release, restrict, or collect more evidence, based on the use's risk and the limits of this small sample.
6. List the additional metrics needed to understand false positives and the downstream consequences.

<br/>

### Example interpretation

The observed recall differs across the three synthetic slices. The denominators are unequal, and Slice B and Slice C have small positive-case counts. These figures alone do not establish the cause, statistical reliability, or practical importance of the differences. A responsible report would examine confidence intervals, sampling, label quality, task mix, false-positive behavior, and the consequences of errors before making a release decision.

Do not infer demographic identity or other sensitive attributes from the slice labels. In a real evaluation, document how each slice was defined and whether that definition is appropriate and permitted.

<br/>

## 12. Practice: Review a Synthetic Evaluation Set

Use this small, synthetic dataset. It contains no real personal information.

| Case | Slice | Expected label | Model prediction | Note |
|---|---|---|---|---|
| E1 | Language A | Positive | Positive | |
| E2 | Language A | Positive | Positive | |
| E3 | Language A | Positive | Negative | Missed positive |
| E4 | Language A | Negative | Negative | |
| E5 | Language A | Negative | Positive | False alarm |
| E6 | Language B | Positive | Positive | |
| E7 | Language B | Positive | Negative | Missed positive |
| E8 | Language B | Negative | Negative | |
| E9 | Language B | Negative | Positive | False alarm |
| E10 | Language B | Negative | Negative | |

For this exercise, positive means “the policy-defined condition is present.” The dataset is too small to support broad claims about either language.

<br/>

### Tasks

1. Calculate TP, FN, FP, and TN for each language slice.
2. Calculate recall and false-positive rate for each slice.
3. State the denominator for every metric.
4. Explain why the values should not be generalized to all users of either language.
5. List at least three possible sources of uncertainty, including sampling and label quality.
6. Propose a follow-up evaluation plan with more representative cases.
7. Draft a limitations statement that reports the observation without claiming a proven cause.

<details>
<summary>Answer key</summary>

**Language A**
- TP = 2, FN = 1, FP = 1, TN = 1.
- Recall = 2 / (2 + 1) = 66.7%.
- False-positive rate = 1 / (1 + 1) = 50%.

**Language B**
- TP = 1, FN = 1, FP = 1, TN = 2.
- Recall = 1 / (1 + 1) = 50%.
- False-positive rate = 1 / (1 + 2) = 33.3%.

Each slice contains only five cases, and each metric uses a very small denominator. The observed differences are descriptive of this synthetic set only. They do not establish a stable language disparity, its cause, or production performance. More representative sampling, reviewed labels, confidence intervals, task and input diversity, and downstream impact analysis are needed.

</details>

<br/>

### Suggested limitations statement

> In a small synthetic evaluation set, recall was 66.7% for Language A (3 positive cases) and 50% for Language B (2 positive cases). False-positive rates were 50% (2 negative cases) and 33.3% (3 negative cases), respectively. These estimates are highly uncertain because each slice contains only five examples. The results do not establish a general language-performance gap or its cause. Further evaluation with representative samples, validated labels, and broader task coverage is required before drawing deployment conclusions.

<br/>

## 13. Checkpoint

**Checkpoint:** Explain which fairness questions are measured and which remain unresolved.

A complete submission should:

1. State the intended and excluded uses of the evaluated system.
2. Define the relevant user or task slices and explain why they matter.
3. Report metrics with denominators and suitable uncertainty estimates.
4. Discuss label quality, sampling, and whether the evaluation represents deployment.
5. Distinguish measured differences from causal explanations.
6. Address accessibility, language coverage, and inappropriate inferences.
7. Identify fairness questions that were not measured and explain why.
8. Describe practical mitigations, release limits, or additional evaluation needed.
9. Provide disclosures that explain the system's role and limitations without replacing safeguards.

A strong answer does not claim that a model is “unbiased” or “fair” in general. It states the specific outcomes measured, the evidence supporting each conclusion, the uncertainty that remains, and the actions planned to reduce risk.

<br/>

## 14. Review Questions

1. What is the difference between an intended use and an excluded use?
2. Why can an aggregate score conceal important performance failures?
3. How should an evaluation slice be selected?
4. Why must sample size and label quality be reported alongside subgroup metrics?
5. Why does a non-significant difference not prove parity?
6. Why can fairness metrics conflict?
7. What are examples of accessibility barriers in a GenAI interface?
8. Why should sensitive attributes not be inferred casually from proxies?
9. What makes a transparency disclosure useful?
10. Why are disclaimers insufficient as the only safety measure?
11. What is the difference between an observed performance difference and a causal explanation?
12. How should a report describe fairness questions that were not evaluated?

<br/>

### Suggested answers

1. Intended uses describe tasks and conditions the system is designed and evaluated to support; excluded uses are unsupported, prohibited, or require additional safeguards.
2. Aggregate performance can hide uneven error rates across languages, tasks, input formats, or relevant groups.
3. Select it based on a concrete task or harm question and a justified, permitted characteristic.
4. Small samples produce unstable estimates, and flawed labels can make metrics misleading.
5. The evaluation may lack statistical power to detect a meaningful gap.
6. Different metrics encode different definitions of acceptable error distribution, and not all can always be satisfied simultaneously.
7. Inaccessible controls, poor keyboard navigation, unreadable charts, unclear errors, or no accessible route to evidence and appeal.
8. Proxy inferences can be inaccurate, sensitive, irrelevant, and difficult for affected people to contest.
9. It accurately explains the AI role, evidence, uncertainty, limitations, appropriate use, and available correction or appeal paths.
10. A disclaimer does not prevent unauthorized actions, data leakage, or systematic errors; operational and technical controls are required.
11. A difference is an observed result; a causal explanation requires further evidence and a design capable of supporting that inference.
12. State that the question was not measured, why it was omitted, the risk created by the gap, and what evidence is needed next.

<br/>

## Key Takeaways

- Document intended uses, excluded uses, evaluation scope, observed failures, and uncertainty.
- Define fairness questions before selecting metrics or slices.
- Report denominators, label quality, sampling limits, and uncertainty alongside subgroup outcomes.
- Do not equate one metric with complete fairness or infer causation from a descriptive difference.
- Evaluate accessibility and language coverage for the actual users and tasks the application claims to support.
- Avoid unsupported personal inferences and provide correction or appeal paths for consequential outcomes.
- Make transparency disclosures specific and actionable.
- Use disclosures alongside—not instead of—technical controls, review, and monitoring.

<br/>

## Further Reading

- NIST AI Risk Management Framework — https://www.nist.gov/itl/ai-risk-management-framework
- NIST AI Risk Management Framework: Generative AI Profile — https://www.nist.gov/itl/ai-risk-management-framework
- OECD AI Principles — https://oecd.ai/en/ai-principles
- W3C Web Accessibility Initiative (WAI) — https://www.w3.org/WAI/
- Google Model Cards and reporting resources — https://modelcards.withgoogle.com/
- Datasheets for Datasets — https://arxiv.org/abs/1803.09010
