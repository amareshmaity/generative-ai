# Level 14: GenAI Security and Responsible AI

**Goal:** Design GenAI applications that handle untrusted input, sensitive information, and model-generated output safely.

This README is the plan for creating notes one by one. Keep numbered Markdown notes directly in `Level 14`, following the previous levels. The filenames below are planned files, not existing chapter links.

## Prerequisites

- Review application validation, authentication, credentials, tool calling, and logging from Level 6.
- Complete [Level 8: Retrieval-Augmented Generation (RAG)](<../Level 8/README.md>) before the retrieval-specific exercises.
- Review [Level 13: GenAI Evaluation and Optimization](<../Level 13/README.md>) for datasets, rubrics, failure analysis, and regression checks.
- Understand HTTP requests, JSON, backend authorization, and basic dependency management.
- Use a small application you own or are authorized to test, with synthetic users, documents, and secret canaries rather than real sensitive data.
- Media and fine-tuning specializations are optional; their security implications can be studied conceptually.

## Learning outcomes

After completing this level, you should be able to:

- Identify assets, trust boundaries, threat actors, and failure paths in a GenAI application.
- Distinguish prompt-level guidance from application-enforced security controls.
- Validate inputs and outputs without mistaking valid structure for safe content.
- Enforce authentication, authorization, least privilege, and retrieval isolation.
- Reduce sensitive-data exposure through prompts, responses, logs, and stored artifacts.
- Assess moderation, human review, abuse controls, resource budgets, and supply-chain risks.
- Test controlled injection, access, leakage, and poisoning scenarios reproducibly.
- Document limitations, fairness concerns, provenance, and remaining risks.

## Study order and planned note files

| Order | Planned note filename | Focus |
|---|---|---|
| 1 | `01_genai_security_overview.md` | Assets, risks, and security versus responsible-use goals |
| 2 | `02_threat_modeling_and_trust_boundaries.md` | Data flow, threat scenarios, and prioritized controls |
| 3 | `03_direct_and_indirect_prompt_injection.md` | Instruction/data confusion and defensive boundaries |
| 4 | `04_untrusted_documents_and_retrieved_content.md` | Ingestion, retrieved evidence, and source handling |
| 5 | `05_sensitive_data_and_privacy.md` | Data classification, minimization, and exposure paths |
| 6 | `06_leakage_through_prompts_logs_and_responses.md` | Canary tests, safe diagnostics, and output review |
| 7 | `07_input_output_and_schema_validation.md` | Parsing, constraints, and business-rule enforcement |
| 8 | `08_insecure_output_handling.md` | Safe rendering, queries, code, URLs, and downstream use |
| 9 | `09_authentication_authorization_and_least_privilege.md` | Trusted identity and bounded capabilities |
| 10 | `10_retrieval_access_controls_and_tenant_isolation.md` | Permission-aware retrieval, caches, and citations |
| 11 | `11_secrets_management.md` | Credential lifecycle and service boundaries |
| 12 | `12_content_moderation_and_policy_enforcement.md` | Contextual policy checks and failure handling |
| 13 | `13_human_review_and_consequential_decisions.md` | Review gates, evidence, and meaningful oversight |
| 14 | `14_abuse_prevention_and_resource_limits.md` | Request, token, concurrency, retry, and budget controls |
| 15 | `15_model_and_dependency_supply_chain.md` | Provenance, trusted artifacts, and safe loading |
| 16 | `16_training_and_retrieval_data_poisoning.md` | Data integrity, quarantine, and source updates |
| 17 | `17_limitations_bias_fairness_and_transparency.md` | Relevant slices, disclosure, and measurement limits |
| 18 | `18_retention_licensing_and_provenance.md` | Data lifecycle, permitted uses, and source lineage |
| 19 | `19_adversarial_testing_and_security_regressions.md` | Controlled tests, assertions, and repeatable evidence |
| 20 | `20_security_review_project_and_revision.md` | Application review and documented remaining risks |

## Chapter outlines

### 01. Security Risks Specific to GenAI Systems

- Identify prompts, documents, embeddings, model artifacts, outputs, and connected capabilities as assets or entry points.
- Compare confidentiality, integrity, availability, and responsible-use concerns.
- Distinguish model failures from application vulnerabilities.
- Explain why fluent answers and instruction following are not security guarantees.

**Practice:** Inventory assets and external services for a small RAG application.

**Checkpoint:** Separate an incorrect answer from an unauthorized action or data disclosure.

### 02. Threat Modeling and Trust Boundaries

- Diagram users, backend services, model providers, parsers, indexes, storage, and logs.
- Identify trusted instructions, untrusted data, identity sources, and downstream sinks.
- Define realistic threat scenarios and their preconditions.
- Prioritize controls by impact, exposure, and feasibility.
- Record assumptions and controls requiring later operational support.

**Practice:** Build a threat register linking each scenario to a boundary, mitigation, and verification step.

**Checkpoint:** Explain which component enforces each security decision.

### 03. Direct and Indirect Prompt Injection

- Compare malicious user instructions with instructions embedded in documents or other input content.
- Examine attempts to redirect tasks, reveal protected data, or request unauthorized functions.
- Separate instruction channels and clearly mark data, while recognizing incomplete model adherence.
- Keep secrets and privileged decisions outside model context where possible.
- Limit capabilities and enforce authorization independently of model output.

**Practice:** Test synthetic task-redirection and canary-disclosure attempts against an owned application.

**Checkpoint:** Explain why a stronger system prompt or delimiter alone cannot establish a security boundary.

### 04. Untrusted Documents and Retrieved Content

- Treat source text, OCR, metadata, links, and retrieved passages as untrusted.
- Bound parsing work and validate supported files and source locations.
- Preserve provenance and distinguish source claims from application instructions.
- Discuss ingestion review, quarantine, and suspicious-source handling.
- Restrict fetching of model-suggested URLs through application policy.

**Practice:** Ingest a synthetic document containing task-redirection text and verify downstream behavior.

**Checkpoint:** Explain how an apparently relevant source can still contain malicious instructions.

### 05. Sensitive-Data Exposure and Privacy

- Classify personal, confidential, secret, and public information.
- Minimize data sent to models and external processing services.
- Compare redaction, pseudonymization, access restrictions, and their limitations.
- Review provider configuration, retention, and data-use terms when writing implementation notes.
- Distinguish self-hosting from complete privacy protection.

**Practice:** Map sensitive fields through a request lifecycle and identify unnecessary copies.

**Checkpoint:** Explain which exposure risks remain after obvious identifiers are removed.

### 06. Leakage Through Prompts, Logs, and Responses

- Inspect application logs, traces, exceptions, prompt capture, and generated responses.
- Use synthetic canaries to detect unintended exposure.
- Apply allowlisted metadata logging and controlled redaction.
- Restrict access to debugging records and review their retention.
- Explain why hidden instructions must not contain credentials or serve as authorization secrets.

**Practice:** Trigger success and error paths, then inspect logs and responses for synthetic sensitive values.

**Checkpoint:** Verify actual emitted records rather than assuming a redaction setting covers every path.

### 07. Input Validation, Output Validation, and Safe Parsing

- Validate types, lengths, sizes, enums, required fields, and allowed operations.
- Parse JSON with safe libraries and validate schemas with Pydantic.
- Add business rules and semantic checks beyond structural validity.
- Handle refusals, incomplete output, invalid values, and failed validation explicitly.
- Avoid execution-based parsing and unbounded repair/retry behavior.

**Practice:** Test malformed, oversized, valid-but-unauthorized, and semantically invalid inputs/outputs.

**Checkpoint:** Distinguish valid data structure from permission to use its contents.

### 08. Insecure Output Handling

- Treat generated HTML, Markdown, SQL, shell text, file paths, and URLs as untrusted.
- Use context-appropriate escaping, sanitization, parameterized queries, and constrained interfaces.
- Prevent arbitrary execution of generated code or commands.
- Restrict file operations and network destinations through application controls.
- Validate output before rendering, storing, or forwarding it to another system.

**Practice:** Use inert test strings to verify that generated content is displayed as data rather than executed.

**Checkpoint:** Identify the downstream sink and the protection appropriate to that context.

### 09. Authentication, Authorization, and Least Privilege

- Derive identity from validated credentials rather than prompts or model claims.
- Authorize operations and resources on the server for every request.
- Keep tool functions allowlisted with validated arguments and bounded permissions.
- Separate service credentials from application-user credentials.
- Fail closed when identity or authorization context is missing.

**Practice:** Test permitted and forbidden operations for two synthetic roles.

**Checkpoint:** Explain why the model cannot grant itself or a user additional privileges.

### 10. Retrieval Access Controls and Tenant Isolation

- Enforce mandatory permission predicates across dense, lexical, hybrid, and parent-document retrieval.
- Recheck source access when fetching text or serving citation targets.
- Isolate conversation history, caches, namespaces, and stored results as required.
- Handle permission changes and prevent metadata/title leakage.
- Keep unauthorized evidence out of prompts and external rerankers.

**Practice:** Test cross-tenant queries, guessed document IDs, shared-cache behavior, and citation access.

**Checkpoint:** Verify isolation independently of whether a generated answer happens to mention private data.

### 11. Secrets Management

- Load credentials through appropriate environment configuration or secret stores.
- Keep credentials out of repositories, prompts, client-side bundles, and logs.
- Scope service access and separate development and production credentials.
- Introduce rotation, revocation, and response to suspected exposure.
- Use placeholders and synthetic tokens in examples and tests.

**Practice:** Review configuration and error messages for accidental secret exposure.

**Checkpoint:** Trace where a credential is loaded, used, and prevented from reaching untrusted components.

### 12. Content Moderation and Policy Enforcement

- Translate application policy into defined input, action, and output checks.
- Compare classifiers, rules, model-based checks, and review queues.
- Assess false positives, false negatives, language coverage, and contextual ambiguity.
- Define safe behavior when checks fail, time out, or are unavailable.
- Distinguish moderation from authentication, factual verification, and injection defense.

**Practice:** Evaluate a small synthetic policy dataset with explicit expected handling.

**Checkpoint:** Explain what the moderation layer does and what it cannot establish.

### 13. Human Review for Consequential Decisions

- Identify actions requiring qualified review, confirmation, or restricted automation.
- Present supporting evidence, uncertainty, and alternatives to reviewers.
- Avoid approval flows that encourage automatic acceptance of model suggestions.
- Record decisions, escalation paths, and review failures appropriately.
- Bound what may happen before approval and revalidate the approved action before execution.

**Practice:** Design a review gate for a consequential workflow using synthetic cases.

**Checkpoint:** Explain how review can change or stop an action rather than merely acknowledge it.

### 14. Abuse Prevention, Rate Limiting, and Resource Exhaustion

- Bound request size, file size, media duration, output tokens, and expensive operations.
- Apply per-user/tenant limits, concurrency controls, and total deadlines.
- Bound retries, batch work, queue depth, and tool execution.
- Track usage and enforce budgets at application-controlled boundaries.
- Discuss unauthenticated abuse, repeated failures, and graceful capacity rejection.

**Practice:** Use fake clients and small local workloads to verify limits without generating large bills or traffic.

**Checkpoint:** Explain why an output-token cap alone does not bound every cost or resource risk.

### 15. Model and Dependency Supply-Chain Risks

- Inventory libraries, model weights, adapters, tokenizers, parsers, and container sources.
- Verify artifact origin, versions, licenses, and expected integrity records.
- Avoid unsafe deserialization and unreviewed remote-code execution during loading.
- Use minimal privileges and isolation for model loading and document processing.
- Review dependency changes and maintain a patch/update process.

**Practice:** Create an artifact inventory and inspect a model-loading configuration without executing unknown code.

**Checkpoint:** Distinguish a known artifact source from a guarantee that the artifact is safe.

### 16. Training, Fine-Tuning, and Retrieval-Corpus Poisoning

- Compare contamination of training examples, labels, retrieved sources, and metadata.
- Inspect suspicious duplicates, conflicting targets, manipulated provenance, and source changes.
- Restrict ingestion authority and review high-impact corpus updates.
- Quarantine questionable data and preserve rollback/version history.
- Discuss limits of automated detection and removal from already trained artifacts.

**Practice:** Add a clearly labeled synthetic poisoned source or training record and verify review/ingestion controls.

**Checkpoint:** Distinguish integrity checks from proof that every accepted source is truthful.

### 17. Model Limitations, Bias, Fairness, and Transparency

- Document intended uses, excluded uses, uncertainty, and observed failure patterns.
- Define relevant user/task slices and meaningful fairness questions.
- Compare subgroup outcomes with attention to sample size and label quality.
- Discuss accessibility, uneven language performance, and inappropriate inferences.
- Provide useful disclosures without treating disclaimers as substitutes for controls.

**Practice:** Review a small evaluation set by relevant slices and report limitations without overstating conclusions.

**Checkpoint:** Explain which fairness questions are measured and which remain unresolved.

### 18. Data Retention, Licensing, and Provenance

- Map raw uploads, parsed text, embeddings, prompts, logs, outputs, and trained artifacts.
- Define retention and deletion behavior across active storage, caches, replicas, and backups.
- Record permissions and licensing for source data, models, and generated media.
- Preserve lineage for sources, transformations, and outputs without unnecessary sensitive copies.
- Verify applicable organizational requirements and current terms for concrete implementations.

**Practice:** Create a lifecycle table listing owner, purpose, retention, access, and deletion handling for each data class.

**Checkpoint:** Distinguish removal from active retrieval from complete deletion across all retained copies.

### 19. Adversarial Testing and Security Regression Checks

- Define expected secure behavior before running tests.
- Build controlled direct/indirect injection, cross-user access, leakage, and budget-limit cases.
- Assert server-side boundaries separately from probabilistic model behavior.
- Repeat selected model-dependent cases and record model/configuration versions.
- Verify controls after prompt, model, retrieval, dependency, or permission changes.
- Store synthetic payloads and test results without real secrets or unauthorized targets.

**Practice:** Introduce a deliberate permission or logging defect in a local test fixture and verify detection.

**Checkpoint:** Explain what passing tests demonstrate and which threat scenarios remain untested.

### 20. Security Review Project and Revision

- Review an owned GenAI application using its data flow and threat model.
- Test injection, retrieval authorization, logs, output handling, and resource limits.
- Apply targeted fixes and rerun relevant checks.
- Assess model limitations, moderation/review design, and data lifecycle.
- Complete the report below with evidence and remaining risks.

**Checkpoint:** Defend the effectiveness and limits of each important mitigation.

## Level deliverable: GenAI security and responsible-use review

Create `genai_security_review_report.md` in this folder with:

1. Application scope, assets, external services, and a data-flow diagram with trust boundaries.
2. A threat register with scenarios, impact, assumptions, controls, and verification evidence.
3. At least twelve controlled test cases spanning direct/indirect injection, cross-user access, output handling, secret-canary leakage, and resource limits.
4. Two synthetic users/tenants with shared and private documents; evidence that unauthorized text, metadata, and citations remain inaccessible.
5. A review of success/error logs showing whether synthetic secrets or sensitive values leak.
6. Input/schema/business-rule validation checks and constrained downstream output handling.
7. Credential, dependency/model artifact, poisoning, and data-lifecycle reviews.
8. Moderation and human-review decisions with false-positive/negative and failure-mode considerations.
9. Relevant bias/fairness observations and clear limitations of the available evidence.
10. Fixes, before/after results, security regression checks, and prioritized remaining risks with owners or next actions.

A notebook, local API, or small RAG project is sufficient. Use synthetic sensitive data and authorized local targets. Fake clients can test deterministic controls; clearly label fixtures and distinguish those checks from live model injection results. Passing the exercise is evidence about the tested controls, not a guarantee of complete security.

## Suggested format for each note

1. Learning objectives and the asset or trust boundary involved.
2. A concrete threat/failure scenario and its preconditions.
3. Data flow and relevant application/model responsibilities.
4. Minimal mitigation or safe configuration example.
5. A controlled test with expected secure behavior and evidence.
6. Residual risks, false positives/negatives, and operational trade-offs.
7. Exercise and revision questions with answers.
8. References and optional extensions.

Consult authoritative security guidance and current official product documentation when writing detailed notes. Verify dependency behavior, provider data terms, and applicable requirements for the chosen implementation rather than assuming they remain unchanged.

## Completion checklist

- [ ] Identify assets, trust boundaries, and realistic threat scenarios.
- [ ] Explain direct/indirect injection and limits of prompt-only defenses.
- [ ] Handle untrusted documents and generated output as data.
- [ ] Validate inputs, schemas, and business rules safely.
- [ ] Enforce identity, authorization, and least privilege in application code.
- [ ] Verify retrieval, cache, source-view, and tenant isolation.
- [ ] Check prompts, logs, responses, and configuration for synthetic-data leakage.
- [ ] Protect credentials and review model/dependency loading risks.
- [ ] Define moderation, human review, abuse controls, and resource budgets.
- [ ] Assess poisoning, provenance, retention, and deletion behavior.
- [ ] Document limitations, fairness observations, and transparency requirements.
- [ ] Run repeatable adversarial/security regression checks.
- [ ] Complete the review report with mitigations and remaining risks.

## Scope and next step

This level focuses on defensive design and controlled testing of GenAI applications. Full enterprise identity infrastructure, specialist penetration testing, jurisdiction-specific compliance programs, and advanced model-security research are optional extensions. Autonomous agents and agent orchestration remain outside this course.

Next: **Level 15 — Production GenAI Engineering and Portfolio** in the [main course outline](../README.md).
