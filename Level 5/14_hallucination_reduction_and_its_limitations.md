# Chapter 14. Hallucination Reduction and Its Limitations

## Learning Objectives

By the end of this chapter, you should be able to:

- Identify common situations in which language models produce unsupported or incorrect claims.
- Improve prompts by supplying complete inputs and defining which evidence may be used.
- Ground answers in relevant source material and require supported attribution.
- Define appropriate behavior for unknown values, abstention, and clarification.
- Independently verify facts, calculations, identifiers, and output constraints where possible.
- Explain why lower temperature, expert personas, and self-review do not guarantee truthfulness.
- Recognize limitations of evidence grounding and document residual risks and human-review requirements.

<br/>

## 14.1. What Is a Hallucination?

In generative AI, a **hallucination** is an output that presents information as true even though the information is false, unsupported by the available evidence, or not justified by the task context. The exact definition varies by application.

Examples include:

- Inventing a citation, identifier, date, or source.
- Adding a fact that is absent from the supplied document.
- Giving a confident answer when the source is ambiguous.
- Misreading a real source and attributing a claim it does not support.
- Producing an incorrect calculation or transforming a value incorrectly.
- Filling a missing field with a plausible-looking guess.

Not every error has the same cause. A wrong answer may result from incomplete input, ambiguous instructions, poor source quality, reasoning failure, stale knowledge, or unsupported generation. The mitigation should target the failure mechanism rather than assume one technique can eliminate all hallucinations.

<br/>

### Truth, support, and task compliance are different

| Dimension | Question | Example failure |
|---|---|---|
| Factual correctness | Is the claim actually true? | The answer gives the wrong release date |
| Evidence support | Does the allowed evidence justify the claim? | The source does not state the date, but the answer invents one |
| Attribution | Does the cited source support the specific claim? | A real citation is attached to a claim it does not establish |
| Task compliance | Did the answer follow the requested constraints? | The answer fills unknown fields instead of returning `null` |
| Calibration | Does the answer express uncertainty appropriately? | The model presents a guess as certain |

An answer may be factually true by coincidence but still unsupported by the permitted source. For evidence-restricted tasks, support matters independently of whether a claim happens to be correct.


<br/>


## 14.2. Improve Input Completeness

A model cannot reliably use information that was never provided or made available to it. If the task depends on a document, time period, definition, identifier, or user-specific detail, make the necessary context explicit.

### Input-completeness checklist

Before writing or revising the prompt, ask:

- Is the relevant source material included or accessible?
- Are the names, dates, units, and identifiers unambiguous?
- Is the requested time period clear?
- Are domain terms and label definitions explained?
- Are all required fields available?
- Are there contradictions between supplied sources?
- Is the model being asked to infer something the evidence cannot establish?

<br/>

### Example: missing input

Weak prompt:

```text
When did the company launch the product?
```

If no company or product source is available, the model may guess or rely on incomplete prior knowledge.

More constrained prompt:

```text
Use only the supplied product announcement to identify the launch date.
If the announcement does not specify a date, return "unknown".
Do not infer a date from indirect clues.

Source:
"""
[Insert the product announcement here]
"""
```

This revision clarifies the allowed evidence and defines the behavior when the answer is missing. It does not guarantee that the model will follow the instruction correctly, so important results still need verification.


<br/>


## 14.3. Define What Evidence May Be Used

Prompts should distinguish between the **task instruction** and the **evidence to be analyzed**. Specify whether the model may use:

- Only supplied text.
- Supplied text plus explicitly identified reference material.
- General model knowledge.
- A stated combination of sources, with a rule for resolving conflicts.

For evidence-restricted extraction or question answering, a useful instruction is:

```text
Answer only from the provided source.
Do not add facts from memory or outside assumptions.
If the source does not support an answer, return "unknown".
For each substantive claim, identify the supporting passage.
```

Use a clear delimiter to mark the source. Delimiters improve readability, but they are not a security boundary: content inside a document may still contain instructions that should be treated as data rather than followed.

<br/>

### Evidence policy should be task-specific

For an open-ended educational explanation, general knowledge may be appropriate. For extracting a contract date or summarizing a particular report, adding outside facts may violate the task. Define the evidence policy based on the consequences of an unsupported claim.


<br/>


## 14.4. Ground Answers in Relevant Material

**Grounding** means tying an answer to evidence available for the task. In a document question-answering workflow, this usually means providing the relevant passages and asking the model to base its answer on them.

A grounded answer should:

1. Use evidence that is relevant to the question.
2. Preserve the source’s qualifications, uncertainty, and scope.
3. Avoid adding unsupported details.
4. Attribute claims to the correct source or passage when attribution is required.
5. State when the evidence is insufficient or conflicting.

<br/>

### Example: evidence and answer

Source:

> “The pilot began in March and included 24 clinics. The report does not provide an outcome measurement.”

Question: “How many clinics took part, and did the pilot improve outcomes?”

Supported answer:

> “The pilot included 24 clinics. The supplied source does not report an outcome measurement, so it does not establish whether outcomes improved.”

Unsupported answer:

> “The pilot included 24 clinics and improved outcomes significantly.”

The second answer invents a result not present in the source.

<br/>

### Require claim-level attribution when useful

For evidence-sensitive tasks, ask for each important claim to be linked to a source passage or document section. Then verify that the passage actually entails the claim. A citation’s presence is not enough; a citation can be real but irrelevant or misinterpreted.

Attribution improves traceability, but it does not guarantee that the model selected the right passage or interpreted it correctly.


<br/>


## 14.5. Handle Unknowns, Abstention, and Clarification

A reliable system needs an explicit way to avoid guessing. Depending on the task, the correct response to insufficient evidence may be to return an unknown value, abstain, or ask a clarifying question.

| Situation | Preferred behavior | Example |
|---|---|---|
| A required fact is absent | Return an agreed unknown value | `"launch_date": null` |
| The request is underspecified | Ask a targeted question | “Which product version do you mean?” |
| Evidence conflicts | Report the conflict or request clarification | “The two documents list different dates.” |
| The task cannot be answered from allowed evidence | Abstain or explain the limitation | “The supplied report does not establish this.” |
| The answer is partially supported | Answer the supported part and identify the gap | “The source gives the count, but not the outcome.” |

<br/>

### Define unknown values precisely

Do not use `null`, an empty string, `"unknown"`, and `"not applicable"` interchangeably unless the schema explicitly defines them that way.

For example:

- `null`: the value is not available or cannot be established.
- `"not_applicable"`: the field does not apply to this case.
- `"ambiguous"`: multiple interpretations remain plausible.
- `"conflicting"`: supplied sources disagree.

The meanings should match the application’s schema and downstream handling.

<br/>

### Avoid excessive abstention

Abstention is not automatically better than answering. If the evidence clearly supports an answer, refusing unnecessarily reduces usefulness. Define the threshold and behavior according to the task’s risk and evidence requirements.


<br/>


## 14.6. Verify Claims Independently Where Possible

Prompt instructions can reduce certain errors, but verification should not depend solely on the same model repeating its own answer.

Use independent checks for properties that can be tested directly.

| Output element | Possible independent check |
|---|---|
| JSON or structured response | Parse it and validate required fields, types, and allowed values |
| Arithmetic | Recalculate with a trusted calculator or deterministic code |
| Dates and identifiers | Compare with the authoritative source or database |
| Extracted quotation | Search for the exact passage in the source |
| Citation | Confirm that the source exists and supports the attached claim |
| Classification | Compare with a predefined label policy or reviewed reference label |
| Summary | Check key facts, qualifications, and omissions against the source |
| Units and ranges | Validate conversions and permitted boundaries programmatically |

<br/>

### Example: calculate rather than trust the generated number

If the model extracts three line items—`120`, `80`, and `45`—and reports a total of `255`, verify the sum independently:

```python
amounts = [120, 80, 45]
verified_total = sum(amounts)

assert verified_total == 245
```

The assertion fails because the reported total is wrong. The code example deliberately illustrates a mismatch; in a real application, parse the extracted values carefully and calculate from the validated inputs.

<br/>

### Independent means meaningfully independent

Asking the same model, “Are you sure?” may catch some mistakes, but it is not a strong independent verification method. The model may repeat its original error. Prefer deterministic checks or authoritative sources for facts that can be checked that way.


<br/>


## 14.7. Why Common Techniques Do Not Guarantee Truthfulness

Several prompt techniques may influence output behavior, but none should be treated as a truth guarantee.

### Lower temperature

Lower temperature generally reduces randomness in token selection, depending on the model and serving implementation. It does not make the model’s underlying knowledge correct or ensure that it interprets evidence accurately.

**Useful for:** reducing some output variation when consistent phrasing or decisions are desired.

**Does not guarantee:** factual accuracy, valid citations, correct arithmetic, or correct interpretation of a source.

<br/>

### Expert personas

Instructions such as “You are an expert analyst” may influence tone, vocabulary, or the style of explanation. They do not supply missing evidence or create expertise that reliably overrides model limitations.

**Useful for:** setting audience, domain framing, and expected level of detail.

**Does not guarantee:** correct specialist judgment or resistance to unsupported claims.

<br/>

### Self-review and critique

Asking a model to review its own answer can surface omissions or inconsistencies. However, the reviewer may share the same assumptions, misunderstand the source, or approve a plausible but false claim.

**Useful for:** an additional pass against an explicit checklist.

**Does not guarantee:** independent verification or detection of every error.

<br/>

### Chain-of-thought-style requests

Asking for detailed reasoning is not a substitute for checking the conclusion against evidence or deterministic calculations. A persuasive explanation can still lead to a wrong answer.

<br/>

### Summary

| Technique | What it may help with | What it cannot establish on its own |
|---|---|---|
| Lower temperature | Output consistency | Truthfulness |
| Expert persona | Tone and domain framing | Actual expertise or evidence |
| Self-review | Some omissions and inconsistencies | Independent correctness |
| “Be accurate” instruction | Makes the desired behavior explicit | Reliable factual accuracy |
| Citations requested in the prompt | Traceability | That citations are valid and supportive |

Choose techniques based on the specific failure being addressed, and add verification where the risk justifies it.


<br/>


## 14.8. Grounding Has Its Own Failure Modes

Grounding reduces reliance on unsupported generation only when the evidence and its use are reliable. It does not make every answer correct.

### Common grounding failures

- **Incorrect source:** The supplied document itself contains an error.
- **Outdated source:** The source was once correct but no longer reflects current facts.
- **Irrelevant retrieval:** The provided passage discusses a similar topic but does not answer the question.
- **Incomplete evidence:** A key qualification or table row is missing.
- **Misinterpretation:** The model misreads a condition, unit, exception, or relationship.
- **Citation mismatch:** A source is cited but does not support the claim.
- **Conflicting sources:** Different documents provide incompatible information.
- **Instruction-like source content:** Untrusted text contains commands that the model may mistakenly follow.

<br/>

### Mitigations matched to failure modes

| Failure mode | Suitable mitigation | Remaining limitation |
|---|---|---|
| Missing source information | Allow unknowns or ask for clarification | The model may still guess |
| Wrong arithmetic | Recalculate programmatically | Incorrect extracted inputs can still produce a wrong result |
| Invalid schema | Parse and validate against a schema | Valid structure can contain false facts |
| Unsupported claim | Require evidence and verify attribution | Evidence may be misread |
| Outdated source | Check source date and authoritative current references | Authoritative sources may themselves lag |
| Conflicting sources | Preserve the conflict and apply a documented resolution policy | The policy may not resolve the underlying truth |
| Ambiguous request | Ask a targeted question or return an ambiguity state | Users may not provide enough information |
| Adversarial text in source | Treat source content as untrusted data and enforce application controls | Prompt wording alone is not a complete security boundary |

The goal is risk reduction, not a claim that hallucinations can be eliminated.


<br/>


## 14.9. Practice: Unconstrained vs Evidence-Restricted Answers

### Source packet

Use the following fictional source:

> “Northstar Health began a scheduling pilot on 12 April 2025 at six clinics. The pilot was planned to run for eight weeks. The document provides no final results and does not identify a percentage change in missed appointments.”

<br/>

### Prompt A — Unconstrained

```text
Explain the Northstar Health scheduling pilot and its results.
```

<br/>

### Prompt B — Evidence-restricted

```text
Use only the source provided below.
Describe the pilot, including its start date, number of clinics, and planned duration.
State whether the source reports final results or a percentage change in missed appointments.
Do not infer outcomes that are not stated.
If a fact is absent, say that the source does not provide it.

Source:
"""
Northstar Health began a scheduling pilot on 12 April 2025 at six clinics.
The pilot was planned to run for eight weeks. The document provides no final
results and does not identify a percentage change in missed appointments.
"""
```

<br/>

### Evaluation procedure

1. Run both prompts using the same model and comparable generation settings.
2. Identify each factual claim in each answer.
3. Check every claim against the source packet.
4. Mark each claim as **supported**, **contradicted**, or **not established**.
5. Check whether the answer invents an outcome or a percentage.
6. Record any missing required facts and any misleading attribution.
7. Compare the answers using evidence support, completeness, uncertainty handling, and clarity.

Do not assume the unconstrained prompt must fail or that the evidence-restricted prompt must pass. Evaluate the actual outputs against the source.

<br/>

### Claim-verification worksheet

| Claim in answer | Source evidence | Status | Notes |
|---|---|---|---|
| Pilot began on 12 April 2025 | Explicitly stated |  |  |
| Six clinics participated | Explicitly stated |  |  |
| Planned duration was eight weeks | Explicitly stated |  |  |
| Missed appointments decreased by a stated percentage | No percentage is provided |  |  |
| Final results were positive | No final results are provided |  |  |


<br/>


## 14.10. Document Residual Risk and Human Review

A mitigation can reduce a known failure mode while leaving other risks unresolved. Document what was tested, what was verified, and what still requires review.

A short residual-risk record can include:

- **Task and scope:** What the model is being used to do.
- **Evidence sources:** Which sources are allowed and how their authority is assessed.
- **Known failure modes:** Errors observed or reasonably expected.
- **Controls:** Prompt constraints, schema validation, deterministic checks, and source verification.
- **Residual risk:** Errors that may still occur despite those controls.
- **Human-review rule:** Which outputs require review and by whom.
- **Escalation behavior:** What happens when evidence conflicts, a check fails, or the model abstains.
- **Limitations:** What the testing did not establish.

<br/>

### Example review policy

For a low-risk internal summary, a team may review a sample of outputs and all outputs that fail validation. For a high-impact decision, the team may require qualified human review before the output is acted upon. The exact policy should be determined by the application’s consequences, applicable rules, and organizational requirements.

Do not describe a system as “hallucination-free” based on prompt design or a small test. State the controls and the remaining uncertainty.


<br/>


## 14.11. Checkpoint: Match Each Mitigation to a Specific Failure

| Proposed mitigation | Failure it targets | What it does not guarantee |
|---|---|---|
| Supply the relevant document | Missing context | Correct interpretation of the document |
| Restrict answers to supplied evidence | Unsupported additions from general knowledge | That the evidence itself is correct |
| Require claim-level attribution | Untraceable or unsupported claims | That citations truly support claims without checking |
| Permit `unknown` or abstention | Guessing when information is absent | That the model always abstains appropriately |
| Ask a clarifying question | Ambiguous or underspecified input | That the user can always resolve the ambiguity |
| Validate JSON with code | Malformed structure and type violations | Semantic truth |
| Recalculate arithmetic independently | Numerical reasoning errors | Correctness of the source numbers |
| Check identifiers against an authoritative source | Invented or mistyped identifiers | Accuracy of the authoritative source |
| Lower temperature | Some generation variability | Factual correctness |
| Use an expert persona | Inappropriate tone or insufficient domain framing | Actual expertise or truthfulness |
| Request self-review | Some omissions and inconsistencies | Independent verification |
| Review high-impact outputs | Residual risks requiring contextual judgment | Elimination of every error |

**Checkpoint answer:** A mitigation should be tied to a defined failure mechanism. Supplying evidence targets missing context; validating JSON targets structural errors; recalculating targets arithmetic errors; and allowing abstention targets unsupported guessing. None guarantees truthfulness, because errors can still arise from bad sources, misinterpretation, incomplete evidence, or failures of the verification process.


<br/>


## 14.12. Key Takeaways

- Hallucination reduction is a layered risk-management problem, not a single prompt trick.
- Make the input complete and state which evidence is permitted.
- Ground important claims in relevant material and verify attribution.
- Define how unknown, ambiguous, and conflicting information should be represented.
- Use independent checks for calculations, identifiers, schema constraints, and other verifiable properties.
- Lower temperature, expert personas, and self-review may help with specific behaviors but do not guarantee truthfulness.
- Grounding can fail if sources are wrong, stale, irrelevant, incomplete, or misinterpreted.
- Document residual risk and apply human review in proportion to the consequences of errors.

**Final checkpoint:** Match each mitigation to the specific failure it is designed to reduce. Describe what the mitigation can help with, what it cannot establish, and which residual risks remain.
