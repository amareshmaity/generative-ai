# Chapter 14: Consent, Impersonation Risks, Provenance, and Responsible Use

## Learning Objectives

By the end of this chapter, you should be able to:

- Check the relevant licenses and permitted uses for models, voices, recordings, images, music, and generated outputs.
- Identify when explicit consent or additional authorization is needed for a custom voice or likeness reference.
- Recognize risks from deceptive impersonation, misleading edits, and undisclosed synthetic media.
- Create a provenance manifest that records model versions, prompts, references, settings, and output history.
- Protect private recordings, transcripts, faces, and voice data through access control, minimization, and retention policies.
- Explain why provenance metadata and synthetic-media detectors provide evidence but not certainty.
- Build a practical consent/licensing checklist for a media-generation project.

<br/>

## 1. Responsible Use Is a Workflow Requirement

Responsible use should be considered before data is uploaded or generation begins—not added only after an output has been created.

Audio and video projects can involve several distinct assets and rights:

- The model or service used to generate or transform media.
- Voice recordings, voice references, speech transcripts, or speaker embeddings.
- Images, photographs, video footage, faces, and likeness references.
- Music, sound effects, scripts, and other source material.
- The generated or edited output.
- Personal data in prompts, logs, metadata, and intermediate files.

Permission for one asset does not automatically grant permission for every other asset or use. For example, permission to use a photograph does not necessarily grant permission to clone the pictured person's voice. A model license also does not automatically clear rights in a user-supplied recording or generated output.

This chapter provides a practical workflow, not legal advice. Applicable law, contract terms, privacy rules, and platform policies depend on the jurisdiction, asset, use case, and parties involved. Escalate uncertain or high-impact cases for qualified legal or privacy review.

<br/>

## 2. Check Licenses and Permitted Uses

### 2.1 Review each layer separately

Before using an asset, record its source and review the applicable terms.

| Asset or component | What to verify |
|---|---|
| Model or API | License/terms, commercial-use permission, restrictions, attribution, prohibited uses, retention and training policies |
| Custom voice or voice reference | Speaker authorization, permitted purpose, scope, duration, revocation process, provider requirements |
| Voice recording | Recording permission, ownership/licensing, privacy expectations, allowed processing and sharing |
| Image/video/likeness | Rights to use, consent where required, model releases or other authorization, restrictions on editing or distribution |
| Music/sound effects | Composition and recording rights, synchronization/adaptation permissions, distribution scope, attribution |
| Script/transcript | Copyright or ownership, confidentiality, personal data, permission to reproduce or transform |
| Generated output | Provider terms, applicable law, third-party rights, disclosure requirements, restrictions on redistribution |

Do not assume that “publicly available” means “free to use.” Likewise, a license that permits model use may not authorize every downstream activity or every type of generated content.

<br/>

### 2.2 A repeatable license-review process

1. Identify the exact model, version, API, dataset, and asset.
2. Locate the current official license, terms of service, or rights documentation.
3. Record the date reviewed and a stable URL or saved copy where permitted.
4. Check commercial use, redistribution, attribution, derivative works, and prohibited-use clauses.
5. Check data handling: retention, training use, subprocessors, region, deletion, and access.
6. Confirm that each asset's permission covers the intended output and audience.
7. Record restrictions and required notices in the project manifest.
8. If terms conflict or are ambiguous, pause the affected use until clarified.

Licenses and service terms can change. Recheck them before a major release or when changing providers, models, assets, or intended use.

<br/>

## 3. Consent for Custom Voices and Likenesses

A custom voice or likeness reference can be used to generate media that appears to come from a real person. The risk is not limited to exact replication: even a plausible imitation can mislead an audience.

### 3.1 Consent should be specific and informed

Where consent or authorization is required, document its scope. Useful fields include:

- Identity of the person or authorized representative.
- The specific recording, image, or likeness being used.
- The purpose of generation (for example, an accessibility narration, a private demo, or a public advertisement).
- Permitted platforms, audience, and distribution territory where relevant.
- Whether commercial use, editing, translation, or reuse is allowed.
- Duration of permission and any expiry or revocation process.
- Whether the person may review outputs before release.
- How reference files and derived assets will be stored, accessed, and deleted.
- Contact point for questions, correction, or withdrawal requests.

A generic release may not cover every future use. Keep the scope understandable and avoid treating consent for one project as unlimited authorization.

<br/>

### 3.2 Practical safeguards

- Use a person's voice or likeness only within documented authorization and applicable provider rules.
- Do not create a custom voice from leaked, private, or otherwise unauthorized recordings.
- Do not use voice similarity as proof of identity or as an authentication mechanism.
- Restrict who can access reference recordings and any derived voice assets.
- Keep a way to disable or remove a custom voice from future workflows when required.
- Reassess permission when the use changes materially, especially for commercial, political, sensitive, or public-facing uses.

For deceased persons, minors, public figures, employees, or other sensitive contexts, additional legal, ethical, contractual, or representative authorization may be relevant. Do not assume that a person's public visibility removes consent or disclosure concerns.

<br/>

## 4. Impersonation, Misleading Edits, and Disclosure

### 4.1 Deceptive impersonation

Synthetic speech or video can falsely imply that a person said or did something. High-risk patterns include:

- Impersonating a real person to obtain money, credentials, access, or confidential information.
- Fabricating a person's endorsement, confession, threat, or statement.
- Creating deceptive evidence or presenting synthetic footage as authentic documentation.
- Removing context or editing a recording to materially misrepresent what happened.
- Using a familiar voice or face to exploit trust, even when the generated content is not an exact copy.

The same media can be low-risk in a clearly labelled fictional demonstration and high-risk when presented as a real person's statement. Evaluate the full context: generation, editing, publication, audience, and likely interpretation.

<br/>

### 4.2 Disclosure

A disclosure should be understandable, visible or audible at the point where it matters, and consistent with the distribution channel. Depending on the use, this could include:

- A clear on-screen label or caption.
- A spoken disclosure in the media.
- A description or accompanying note when the content is shared.
- A platform-provided synthetic-media label or metadata.
- A production note for internal review.

A hidden note in a filename or an inaccessible metadata field is unlikely to inform an ordinary viewer. Disclosure needs depend on the context and applicable requirements; no single label is universally sufficient.

<br/>

### 4.3 Misleading edits

Editing can mislead even if every individual frame or audio segment was originally real. Preserve relevant context and document transformations such as:
- Splicing or rearranging statements.
- Removing pauses or surrounding speech.
- Replacing audio or changing visible lip movements.
- Combining footage from different times or locations.
- Generating transitions or background events that alter the perceived meaning.

Keep source material and edited outputs distinguishable. Where authenticity matters, retain an edit history and make material changes clear to reviewers or audiences as appropriate.

<br/>

## 5. Provenance and Output History

**Provenance** is a record of where an asset came from and how it was transformed. A provenance manifest supports traceability, debugging, review, and incident response. It does not by itself prove that the content is true or authorized.

### 5.1 What to record

A useful manifest may include:

- Project and asset identifiers.
- Source file name or internal identifier; avoid putting sensitive personal data in the name.
- Source owner/provider and acquisition method.
- License/permission reference and review date.
- Consent record identifier and permitted purpose, where applicable.
- Model/provider, exact model version if available, and API endpoint/version.
- Prompt and negative prompt, if used.
- Reference image/audio/video identifiers and preprocessing steps.
- Explicit settings such as duration, resolution, seed, voice, or supported controls.
- Job/request ID, generation timestamp, and output identifier.
- Output hash, media metadata, and parent/source asset references.
- Transformations after generation (trimming, resampling, editing, muxing, subtitles).
- Disclosure decision and release status.
- Reviewer, approval status, and known limitations.

Record only what is needed for traceability. Prompts and logs may contain private information, so provenance itself must be access-controlled.

<br/>

### 5.2 Example provenance manifest

The following JSON is an illustrative schema, not a universal standard or a valid manifest for a particular provider.

```json
{
  "project_id": "demo-project-001",
  "asset_id": "video-output-003",
  "asset_type": "generated_video",
  "created_at_utc": "2026-10-14T10:00:00Z",
  "source_assets": [
    {
      "asset_id": "reference-image-001",
      "source_type": "user_supplied_image",
      "permission_record_id": "permission-014",
      "license_reviewed_at": "2026-10-10"
    }
  ],
  "generation": {
    "provider": "record actual provider",
    "model": "record actual model/version",
    "endpoint_version": "record if available",
    "prompt_record_id": "prompt-003",
    "settings_record_id": "settings-003",
    "job_id": "record actual job identifier"
  },
  "post_processing": [
    "trimmed beginning",
    "added captions"
  ],
  "output": {
    "file_name": "final-video.mp4",
    "sha256": "record actual SHA-256 hash",
    "disclosure_status": "review required",
    "review_status": "pending"
  },
  "retention": {
    "classification": "internal",
    "delete_after": "set according to policy"
  }
}
```

Use actual values in a real manifest. Do not leave placeholder text in a production record, and do not place secrets, access tokens, or raw sensitive data in fields intended for broad access.

<br/>

### 5.3 Hashes and versioning

A cryptographic hash such as SHA-256 can help detect whether a file has changed relative to a recorded digest. It does not establish who created the file, whether the source was authorized, or whether the content is authentic. Keep the hash with a trustworthy, access-controlled record of the asset and its history.

<br/>

## 6. Privacy, Storage, Logs, and Retention

Audio and video may reveal identity, location, relationships, sensitive conversations, or biometric characteristics. Transcripts can expose the same information even when the original recording is deleted.

### 6.1 Data-minimization principles

- Collect and upload only the media needed for the task.
- Crop, redact, or remove unrelated people and private details when feasible.
- Avoid placing raw transcripts, faces, voice references, or private content in general-purpose logs.
- Use pseudonymous asset IDs instead of names where possible.
- Limit access by role and purpose.
- Encrypt data in transit and at rest where supported.
- Separate reference assets, generated outputs, consent records, and operational logs when different access rules apply.
- Check provider retention and training terms before uploading sensitive material.
- Define deletion for source media, intermediate files, caches, derived voice assets, transcripts, and backups.
- Keep an audit trail for access and deletion where appropriate.

<br/>

### 6.2 Retention plan

For each data category, specify:
- Why it is retained.
- Who may access it.
- Where it is stored.
- How long it is retained.
- How deletion is triggered and verified.
- Whether provider-side copies or backups may persist after local deletion.

Do not promise complete deletion unless the relevant systems and providers support it and the deletion has been verified to the extent possible. Some systems have backup, legal-hold, or processing limitations that need to be disclosed.

<br/>

### 6.3 Logging safely

Prefer recording operational metadata such as request ID, model version, elapsed time, status, and error category rather than full media content. If content-level debugging is necessary, use a restricted, time-limited process with a clear purpose. Avoid logging credentials, signed download URLs, or private media inline.

<br/>

## 7. Provenance Metadata and Synthetic-Media Detection: Limits

### Provenance metadata

Metadata or cryptographic signing can carry information about origin and edits. Its strength depends on how it was created, protected, preserved, and verified.

Limitations:
- Metadata can be stripped during export, upload, transcoding, or screenshotting.
- Unsigned or untrusted metadata can be forged.
- A valid signature establishes a relationship to a signing key and recorded claims, not the truth of every depicted event.
- Missing provenance does not prove that media is synthetic.
- Provenance can describe an authorized workflow without proving that all permissions or claims were valid.

<br/>

### Synthetic-media detectors

Detectors estimate whether media exhibits patterns associated with synthetic generation or manipulation. They can be useful as one signal, but:
- False positives can flag authentic media.
- False negatives can miss synthetic or edited content.
- Performance can degrade on new generators, compression, cropping, filters, or unfamiliar content.
- Scores depend on the model, data, threshold, and context.
- Detection does not determine consent, legality, intent, or whether the content is misleading.

<br/>

### Responsible verification

Use layered evidence where authenticity matters:
1. Check provenance/signatures where available.
2. Verify source and chain of custody.
3. Compare with trusted original recordings or independent evidence.
4. Review context and editing history.
5. Use detectors as supporting signals, not final adjudicators.
6. Document uncertainty and avoid definitive claims unsupported by evidence.

Neither metadata nor a detector score should be treated as a universal “authentic/fake” verdict.

<br/>

## 8. Practice: Consent/Licensing Checklist and Provenance Manifest

Choose a small audio/video project—for example, a generated narration over a licensed image—or create a hypothetical project clearly marked as a plan.

### A. Consent and licensing checklist

- [ ] Model/service terms and version reviewed.
- [ ] Commercial, redistribution, attribution, and output-use terms checked.
- [ ] Source image/video/audio and script origin recorded.
- [ ] Rights or licenses cover the intended transformation and distribution.
- [ ] Consent/authorization for any identifiable voice or likeness documented where required.
- [ ] Scope, purpose, duration, platforms, and revocation process recorded.
- [ ] Sensitive data and unnecessary bystanders removed or minimized where feasible.
- [ ] Disclosure decision documented for the intended audience and channel.
- [ ] Retention and deletion requirements defined for source and derived assets.
- [ ] Access permissions and safe logging approach defined.
- [ ] Provenance manifest created and linked to the output.
- [ ] Reviewer/approval status recorded before publication.

Mark each item as **Pass**, **Fail**, **Not applicable**, or **Needs review**. Do not treat “not checked” as “pass.”

<br/>

### B. Asset register

| Asset ID | Type/source | Permission/license reference | Consent needed/status | Storage/retention |
|---|---|---|---|---|
| | Model/API | | | |
| | Voice recording/reference | | | |
| | Image/video/likeness | | | |
| | Music/sound effect | | | |
| | Script/transcript | | | |
| | Generated output | | | |

<br/>

### C. Provenance report

Record:
- Input asset IDs and their permission references.
- Model/provider/version and request/job ID.
- Prompt and explicit settings, stored with appropriate access control.
- Output hash and media metadata.
- Post-processing steps and parent-child asset links.
- Disclosure choice and rationale.
- Retention/deletion date or trigger.
- Reviewer and unresolved risks.

If the project is hypothetical, label all values as planned rather than claiming an actual review or generation occurred.

<br/>

## 9. Checkpoint: Permission, Disclosure, and Retention

These controls address different risks and should not be substituted for one another.

- **Permission/consent** addresses whether the assets and likeness/voice may be used for the intended purpose.
- **Disclosure** addresses whether the audience is given an appropriate understanding that content is synthetic or materially edited.
- **Retention and access controls** address how private data is stored, used, exposed, and eventually deleted.
- **Provenance** helps trace assets and transformations.
- **Detection** can provide a clue about manipulation but cannot establish permission or truth.

<br/>

### Checkpoint answer

> Asset permission determines whether the source material, voice, likeness, model, and intended use are authorized. Disclosure helps prevent audiences from mistaking synthetic or materially edited content for authentic recordings. Retention and access policies limit exposure of private recordings, transcripts, faces, and voice references. A provenance manifest records the model, inputs, settings, and edit history for traceability, while hashes, metadata, and detectors have limitations and do not independently prove authenticity, consent, or truth.

Apply the answer to the actual project and identify any unresolved permission, disclosure, or retention question before release.

<br/>

## 10. Review Questions and Answers

**1. Does a model license automatically authorize a supplied voice recording?**  
No. Model terms and source-asset rights/consent are separate checks.

**2. What makes consent for custom voice or likeness use meaningful?**  
It should be informed and scoped to the asset, purpose, distribution, duration, reuse, storage, and relevant withdrawal or review process.

**3. Why can a clearly labelled fictional demo be different from deceptive impersonation?**  
Audience expectations and context affect whether people are likely to believe a real person said or did something. Labels do not excuse every misuse, but clear context can reduce deception risk.

**4. What is provenance?**  
A traceable record of asset origin and transformations, including inputs, model/settings, outputs, and post-processing.

**5. Does a SHA-256 hash prove a video is authentic?**  
No. It can help detect changes relative to a trusted recorded digest, but it does not prove origin, authorization, or truth.

**6. Does missing provenance prove that media is synthetic?**  
No. Metadata can be removed or lost during ordinary processing.

**7. Why are synthetic-media detectors not definitive?**  
They can produce false positives and false negatives, and their performance depends on content, processing, model, and threshold.

**8. Why include retention rules in the project manifest?**  
They define how long sensitive source and derived assets remain accessible and how deletion is handled, including intermediates and provider-side copies where applicable.

<br/>

## 11. Further Reading

- [Creative Commons licenses](https://creativecommons.org/share-your-work/cclicenses/) — license types and reuse permissions.
- [C2PA specifications](https://c2pa.org/specifications/specifications/) — standards for content provenance and authenticity-related claims.
- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework) — governance and risk management concepts.
- [NIST Privacy Framework](https://www.nist.gov/privacy-framework) — privacy risk management.
- [OWASP Top 10 for LLM Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/) — security risks in AI-enabled applications.
- [OpenAI policies and terms](https://openai.com/policies/) — check the current applicable policies and terms for the service being used.

These resources are starting points, not substitutes for reviewing the exact license, provider terms, and legal requirements that apply to a project.


<br/>


## Chapter Summary

- Review model/service terms and source-asset permissions separately.
- Obtain and record appropriate consent for custom voice and likeness references.
- Evaluate impersonation and misleading-edit risks in the context of how media will be used and perceived.
- Disclose synthetic or materially edited media where appropriate or required.
- Maintain a provenance manifest for source assets, model/version, prompts, settings, outputs, and edits.
- Minimize and protect private recordings, transcripts, faces, and voice data; define retention and deletion.
- Metadata, hashes, and synthetic-media detectors provide limited evidence and do not independently prove authenticity, consent, or truth.
