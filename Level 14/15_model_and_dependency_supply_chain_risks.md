# Chapter 15: Model and Dependency Supply-Chain Risks

## Learning Objectives

By the end of this chapter, you should be able to:

- Inventory libraries, model weights, adapters, tokenizers, parsers, container images, and other artifacts used by a GenAI application.
- Verify artifact origin, version, licensing information, and available integrity records.
- Recognize unsafe deserialization and the risks of enabling unreviewed remote code during artifact loading.
- Apply least privilege and isolation to model loading and document processing.
- Review dependency changes and maintain a repeatable patch and update process.
- Inspect a model-loading configuration without executing unknown code.
- Explain why a known artifact source is not a guarantee that the artifact is safe.

<br/>

## 1. What Is a GenAI Supply Chain?

A GenAI application depends on more than its application source code. It may load model weights, fine-tuning adapters, tokenizers, embedding models, rerankers, document parsers, OCR packages, vector database clients, orchestration libraries, Python packages, base images, and external services.

The **software and model supply chain** is the set of people, systems, repositories, build processes, artifacts, and dependencies involved in producing and running the application.

A compromise or defect anywhere in this chain can affect the deployed system. Examples include:

- A dependency release that introduces malicious code or a vulnerable component.
- A model repository containing unexpected executable loading logic.
- A model file replaced or modified after its expected integrity value was recorded.
- An adapter that is incompatible with, or behaves unexpectedly alongside, its base model.
- A document parser that processes hostile files unsafely.
- A container image containing outdated packages, unnecessary tools, or exposed credentials.
- A license that is incompatible with the intended distribution or commercial use.

Supply-chain security requires traceability, verification, controlled loading, isolation, and ongoing maintenance. No single badge, repository, checksum, scanner, or vendor name proves that an artifact is safe for every use.

<br/>

## 2. Inventory the Artifacts

Start with a complete inventory of what the application obtains and executes, including artifacts downloaded during build, startup, inference, ingestion, or runtime tool use.

### Artifact categories

| Category | Examples | Risks to review |
|---|---|---|
| Application packages | Python, Node.js, orchestration and API libraries | Vulnerabilities, typosquatting, maintainer compromise, transitive dependencies |
| Model weights | LLMs, embedding models, rerankers, vision or audio models | Unexpected origin, tampering, licensing, unsafe loading formats |
| Fine-tuning artifacts | LoRA/PEFT adapters, checkpoints, quantized weights | Provenance, compatibility, integrity, license terms |
| Tokenizers and configs | Vocabulary files, tokenizer configuration, model configuration | Mismatched files, unexpected configuration, incorrect model behavior |
| Model code | Custom architecture or inference code | Arbitrary code execution, hidden side effects, unreviewed dependencies |
| Data-processing libraries | PDF parsers, OCR, image/audio/video decoders | Malformed-file attacks, resource exhaustion, native-code vulnerabilities |
| Container images | Base images, inference images, worker images | Vulnerable packages, untrusted image sources, excessive privileges |
| Build artifacts | Wheels, archives, generated bundles | Tampering, inconsistent builds, unknown origin |
| External services | Model APIs, registries, hosted vector stores | Identity and access controls, availability, data handling, dependency concentration |

Inventory indirect dependencies as well as packages named directly in the project manifest. A top-level package can introduce a large transitive dependency tree.

<br/>

### Suggested inventory fields

- Artifact name and type.
- Version, revision, or immutable identifier.
- Source registry or repository.
- Publisher or maintainer, when known.
- Expected checksum or signature and verification status.
- License and usage constraints.
- Direct and transitive dependency relationships.
- Intended environment and runtime purpose.
- Owner and approval status.
- Known vulnerabilities and patch status.
- Date last reviewed and planned review cadence.

Keep the inventory machine-readable where possible. A software bill of materials (SBOM) can help describe software components and relationships, but a software SBOM may not fully capture model weights, adapters, tokenizer assets, or model-specific provenance. Extend the inventory to cover those artifacts.

<br/>

## 3. Verify Origin, Version, and Integrity

### 3.1 Origin and provenance

Origin answers where an artifact was obtained and, ideally, who published or built it. Prefer approved registries, official project repositories, and controlled internal mirrors. Record the exact repository and immutable revision used rather than relying only on a mutable name such as `latest` or a branch head.

A known source improves traceability, but it does not prove that:

- The publisher's account has not been compromised.
- The repository has no malicious or vulnerable content.
- The artifact was built securely.
- The license permits the intended use.
- The artifact is compatible with your code or deployment.
- The artifact will behave safely on untrusted input.

Treat origin as one verification signal among several.

<br/>

### 3.2 Versions and immutable references

Pin dependency versions and model revisions where reproducibility and controlled updates require it. For source-controlled repositories, use a reviewed commit or immutable revision. For container images, prefer a verified digest over a mutable tag. For model repositories, record the exact revision and the files expected at that revision.

Pinning is not a substitute for patching. A pinned vulnerable dependency can remain vulnerable indefinitely if the update process never revisits it. Combine reproducible pins with a planned review and update cadence.

<br/>

### 3.3 Checksums and signatures

A cryptographic checksum, such as SHA-256, can detect whether bytes match an expected digest. It does not identify the publisher by itself. The expected digest must come from a trusted channel or authenticated release record.

A digital signature can help verify that an artifact was signed by a particular key and has not changed since signing, provided the signature, key identity, and trust policy are themselves verified. Signature verification does not prove that the signed artifact is benign.

Example: calculate a digest for a file already downloaded to a controlled inspection environment.

```python
import hashlib
from pathlib import Path


def sha256_file(path: str) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


print(sha256_file("artifact.bin"))
```

This prints a digest for comparison with an independently obtained, trusted expected value. **Do not treat the printed value alone as proof of authenticity.** Avoid executing or deserializing the file merely to inspect it.

<br/>

### 3.4 Licenses and intended use

Check the license for the exact artifact and version, not only the repository's headline. Model weights, code, datasets, adapters, and tokenizer assets may have different terms. Review restrictions relevant to the intended use, such as redistribution, commercial use, attribution, acceptable-use conditions, or derivative works.

A license check is a compliance review, not a security scan. Conversely, a technically secure artifact may still be unsuitable for the intended use because of its license or provenance.

<br/>

## 4. Model-Loading Risks

Model-loading paths deserve special scrutiny because some formats or loading options may deserialize complex objects or import executable code.

### 4.1 Unsafe deserialization

Some serialization formats can represent more than numerical tensors. Depending on the format and loader, deserialization may invoke code or reconstruct arbitrary objects. Loading an untrusted artifact with an unsafe deserializer can therefore become a code-execution risk.

Safer practices include:

- Prefer data-oriented tensor formats designed to avoid arbitrary object deserialization, where supported by the framework and artifact.
- Use restricted or weights-only loading modes when available and compatible.
- Review the loader's documented security properties and format limitations.
- Keep model artifacts and metadata in a controlled directory with appropriate permissions.
- Inspect file types, sizes, and expected file lists before loading.
- Load untrusted or newly acquired artifacts in an isolated environment with no unnecessary network or credential access.
- Do not assume that a file extension establishes the actual format or safety of a file.

A safer serialization format reduces a class of risks; it does not prove that weights are trustworthy, that configuration is benign, or that inference behavior is appropriate.

<br/>

### 4.2 Remote code execution during loading

Some model repositories provide custom Python code or other executable components needed for loading or inference. A loader option that trusts repository code may execute that code in the current process.

Before enabling custom or remote code:

1. Determine whether it is genuinely required.
2. Identify the exact repository and immutable revision.
3. Inspect the code and its imports.
4. Review network, filesystem, subprocess, and credential access.
5. Check its dependency tree and licensing.
6. Run it in a disposable, isolated environment if dynamic testing is needed.
7. Approve the exact artifact and revision through the application's review process.

Do not enable a “trust remote code” or equivalent option merely to make loading succeed. If custom code is unavoidable, treat it as application code: review it, pin it, test it, and deploy it under a constrained identity.

<br/>

### 4.3 Inspect before loading

A safe first inspection can be largely static:

- Read the model card and repository documentation.
- List files and their sizes.
- Inspect configuration and tokenizer metadata as data.
- Check hashes or signatures against trusted records.
- Inspect Python source files without importing them.
- Review package manifests and declared dependencies.
- Look for unexpected executable files, installation hooks, or unexplained network requirements.
- Compare the artifact file list against the expected release contents.

Static inspection cannot guarantee the absence of malicious behavior. It is an initial triage step that helps determine whether further review or isolated testing is appropriate.

<br/>

## 5. Model Weights, Adapters, and Tokenizers

A model deployment may combine several independently versioned components:

- Base model weights.
- Adapter weights, such as LoRA/PEFT artifacts.
- Model configuration.
- Tokenizer vocabulary and configuration.
- Quantization configuration and supporting libraries.
- Custom model code.
- Runtime and inference engine.

Record the exact combination that was evaluated and deployed. An adapter that is safe to load as data may still be incompatible with a different base model or may cause unexpected output behavior. A tokenizer mismatch can alter tokenization and degrade results. Quantization and inference libraries can introduce separate compatibility or security concerns.

Do not assume that a reputable base model makes every adapter or derivative safe. Review each artifact's origin, integrity, license, and compatibility independently, then evaluate the combined deployment.

<br/>

## 6. Document Parsers and Media Processing

GenAI ingestion pipelines often process untrusted PDFs, office documents, HTML, archives, images, audio, or video. Parsing can invoke complex native libraries and consume substantial CPU, memory, and disk space.

Apply controls such as:

- Run parsers in separate worker processes or containers.
- Use a low-privilege identity with access only to required input and output directories.
- Restrict network access unless explicitly required.
- Set CPU, memory, disk, file-count, and wall-clock limits.
- Bound file size, archive expansion, page count, image dimensions, audio/video duration, and extracted-text size.
- Keep parsers and native dependencies patched.
- Treat extracted text and metadata as untrusted input for later model stages.
- Avoid executing macros, embedded scripts, or active content as part of routine extraction.
- Delete temporary artifacts according to retention policy.

Isolation reduces the blast radius if a parser is exploited; it does not make malformed files harmless. Input validation and resource limits remain necessary.

<br/>

## 7. Least Privilege and Isolation

The component loading a model or parsing a document should have only the permissions needed for that job.

Examples:

- A model-inspection worker should not have production database credentials.
- A document parser should not be able to access unrelated tenant data.
- A build process should not receive broad production credentials unless strictly required.
- A model loader should not have unrestricted outbound network access if artifacts can be staged beforehand.
- An inference service should not run as root merely for convenience.

Useful isolation controls include:

- Dedicated service identities.
- Read-only artifact mounts where practical.
- Restricted filesystem paths.
- Network egress policies.
- Container or process isolation.
- CPU, memory, process-count, and execution-time limits.
- Separation between build, inspection, testing, and production environments.
- Short-lived credentials delivered only when necessary.

Avoid placing credentials in the same workspace as untrusted artifacts. If a malicious loader or parser gains code execution, its available permissions determine much of the potential impact.

<br/>

## 8. Dependency Review and Patch Management

Dependency security is a continuous process. A clean initial scan does not guarantee that the application remains secure as new vulnerabilities, releases, or compromises are discovered.

### A practical update workflow

1. **Inventory:** Identify direct and transitive packages, model assets, containers, and their owners.
2. **Monitor:** Track relevant security advisories and upstream releases.
3. **Prioritize:** Assess exploitability, exposure, severity, and whether the vulnerable component is reachable in your deployment.
4. **Update:** Select a patched version or a documented mitigation.
5. **Review:** Inspect dependency changes, release notes, new maintainers, installation hooks, and license changes.
6. **Test:** Run unit, integration, model-loading, ingestion, and security regression tests.
7. **Stage:** Deploy to a controlled environment and verify compatibility and performance.
8. **Release:** Promote the approved artifact with traceable version and integrity records.
9. **Monitor:** Observe failures, resource use, unexpected network activity, and model-quality regressions.
10. **Rollback or mitigate:** Use a tested rollback or containment process if the update causes unacceptable behavior.

Not every update has the same urgency. Critical, actively exploited vulnerabilities may require an expedited path; routine updates can follow a scheduled review. Define ownership and response targets so that “we will update dependencies” becomes an operational process.

<br/>

### Lockfiles and reproducible builds

Lockfiles can make package resolution more reproducible, but they do not prove that a dependency is safe. Reproducible builds can help establish that the same source and build process produce the expected artifact, but they do not guarantee that the source itself is benign. Combine reproducibility with provenance, review, integrity verification, and vulnerability management.

<br/>

## 9. Artifact Inventory Template

Use this template as a starting point for a project inventory.

| Field | Example or expected content |
|---|---|
| Artifact ID | Stable internal identifier |
| Type | Package, model, adapter, tokenizer, parser, container |
| Name | Exact package or artifact name |
| Version / revision | Pinned package version, commit, or immutable model revision |
| Source | Registry, repository, or controlled internal mirror |
| Integrity record | Expected digest/signature and verification result |
| License | Exact license identifier or review status |
| Dependencies | Direct and relevant transitive dependencies |
| Runtime permissions | Filesystem, network, credentials, and service access |
| Intended environment | Development, inspection, staging, or production |
| Security status | Known vulnerabilities, review findings, mitigations |
| Owner | Team or individual responsible for updates |
| Last review | Date and reviewer/process reference |
| Decision | Approved, restricted, pending review, or rejected |

Do not record actual credentials in the inventory. Refer to the identity or secret-store entry by a non-sensitive identifier.

<br/>

## 10. Practice: Inspect Without Executing Unknown Code

### Scenario

A project needs to evaluate a third-party model repository. It contains weight files, a model configuration, tokenizer files, and a Python file described as a custom loading helper. The documentation recommends enabling a remote-code option.

The goal is to decide whether the artifact can proceed to controlled testing—not to run the code during the initial inspection.

<br/>

### Tasks

1. Record the repository URL, exact revision, publisher, and intended use.
2. List the files and compare them with the documented expected contents.
3. Record file sizes and calculate local checksums without loading the model.
4. Obtain an expected digest or signature through a trusted channel, if available, and document whether it verifies.
5. Inspect the configuration and tokenizer metadata as data.
6. Read the custom Python source as text; do not import it or execute setup scripts.
7. Identify imports and operations involving filesystem access, network access, subprocesses, environment variables, or credentials.
8. Review the license and compatibility requirements for the base model, adapter, tokenizer, and runtime.
9. Decide whether custom code is required or whether a standard safe loader is sufficient.
10. If dynamic testing is justified, define a disposable environment with no production credentials, minimal permissions, restricted network access, and resource limits.
11. Record findings, unresolved questions, and an explicit approval, restriction, or rejection decision.

<br/>

### Inspection commands

These examples list files and inspect text without importing or executing the repository's code. Run them only in a controlled workspace, and adapt paths to the local artifact.

```bash
# List files without executing them
find ./candidate-artifact -type f -printf '%p %s bytes\n'

# Calculate SHA-256 digests
find ./candidate-artifact -type f -print0 \
  | sort -z \
  | xargs -0 sha256sum

# Read configuration as text; do not import model code
sed -n '1,240p' ./candidate-artifact/config.json

# Inspect Python source as text; do not run it
sed -n '1,240p' ./candidate-artifact/modeling_custom.py
```

A digest calculated locally is useful only when compared with an expected digest obtained from an independently trusted source. File listing and source inspection are not complete malware analysis.

<br/>

### Example findings table

| Check | Example finding | Next step |
|---|---|---|
| Origin | Repository identified, publisher history not fully reviewed | Verify publisher and release provenance |
| Revision | Mutable branch reference only | Resolve and record an immutable revision |
| Integrity | Local digest calculated, no trusted expected digest available | Mark integrity as unverified |
| Custom code | Loader imports additional modules and performs network access | Review necessity and behavior; isolate testing |
| License | Terms unclear for intended distribution | Obtain legal/compliance review |
| Permissions | Candidate loader would have access to a developer's home directory | Use a disposable low-privilege environment |
| Decision | Several checks unresolved | Do not load in a privileged or production environment yet |

These are illustrative findings, not claims about a real repository.

<br/>

## 11. Checkpoint

**Checkpoint:** Distinguish a known artifact source from a guarantee that the artifact is safe.

A complete answer should explain:

1. Why provenance and immutable revisions improve traceability.
2. What checksums and signatures establish—and what they do not establish.
3. How licenses differ from security properties.
4. Why unsafe deserialization and unreviewed remote code are dangerous.
5. How model weights, adapters, tokenizers, and custom code should be tracked as separate components.
6. Why document parsers and model loaders should run with minimal privileges and isolation.
7. How dependency review, patching, testing, and rollback form a continuous process.
8. Which findings would block an artifact from production use.

A strong answer states that a trusted source is a useful signal, not proof of benign behavior. A signature can establish that an artifact matches a trusted signing identity and has not changed since signing; it cannot prove that the signed artifact contains no vulnerability or malicious behavior.

<br/>

## 12. Review Questions

1. What belongs in a GenAI artifact inventory beyond ordinary application packages?
2. Why are transitive dependencies important?
3. What does a cryptographic checksum establish?
4. Why does a checksum not establish publisher identity by itself?
5. What is the risk of enabling remote custom code during model loading?
6. Why can a model's file extension not prove the file is safe?
7. Why should adapters, tokenizers, and base weights be tracked separately?
8. How does least privilege reduce the impact of a compromised parser?
9. Why is a pinned dependency not necessarily a secure dependency?
10. What should be done when a license or provenance record is unclear?
11. Why should a new artifact first be inspected without executing unknown code?
12. What does an SBOM provide, and why might a GenAI project need a supplementary model-artifact inventory?

<br/>

### Suggested answers

1. Model weights, adapters, tokenizers, model configuration, custom code, parsers, container images, and build artifacts.
2. They can introduce vulnerabilities, malicious packages, or unexpected behavior even when the top-level package is legitimate.
3. It verifies that bytes match a specific digest, assuming the expected digest is trusted.
4. Anyone who can change the file can calculate a new digest; publisher identity requires a trusted provenance or signature mechanism.
5. The code may execute with the loader process's permissions and access to its files, network, and credentials.
6. Extensions can be misleading, and safety depends on actual format, loader behavior, contents, and execution path.
7. They have separate origins, versions, licenses, integrity records, and compatibility requirements.
8. It limits what the parser can access or damage if exploited.
9. The pinned version may contain known or newly discovered vulnerabilities.
10. Mark the artifact as pending or restricted and obtain the required security or compliance review before use.
11. Static inspection can reveal unexpected files, imports, permissions, and dependencies before code is granted an execution opportunity.
12. An SBOM describes software components and relationships; model-specific assets and provenance may need additional tracking.

<br/>

## Key Takeaways

- Inventory all software and model artifacts, including indirect dependencies and loading code.
- Record immutable versions, origin, license, integrity evidence, owner, and review status.
- Treat checksums, signatures, publisher reputation, and vulnerability scans as complementary signals—not universal safety guarantees.
- Avoid unsafe deserialization and do not execute unreviewed remote code just to load a model.
- Isolate model loading and untrusted document processing with minimal permissions and bounded resources.
- Review and test dependency changes, patch known vulnerabilities, and keep rollback paths available.
- Inspect unknown artifacts as data first; use disposable, constrained environments for justified dynamic testing.

<br/>

## Further Reading

- OWASP Top 10 for LLM Applications — https://genai.owasp.org/
- Python Packaging User Guide — https://packaging.python.org/
- Python `pickle` documentation and its security warning — https://docs.python.org/3/library/pickle.html
- Sigstore documentation — https://docs.sigstore.dev/
- SLSA supply-chain security framework — https://slsa.dev/
- SPDX specifications for software bills of materials and licensing — https://spdx.dev/
- Your model framework's official documentation for safe tensor formats, restricted loading modes, model revisions, and custom-code options.
