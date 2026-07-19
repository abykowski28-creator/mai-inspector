# Security

**Product:** MAI Inspector
**Version:** v1.0.0
**Edition:** OpenAI Build Week Edition
**Status:** Final

## Purpose and Scope

This document records the security-relevant boundaries and implemented guardrails in the MAI Inspector public release package.

It describes only behavior implemented in the public repository.

It does not claim formal security certification, compliance certification, enterprise access control, hosted production security controls, encryption at rest, secrets vault integration, or audit infrastructure.

MAI Inspector v1.0.0 defines explicit operational, credential, privacy, and network boundaries. These controls support responsible prototype use but do not constitute security certification, regulatory compliance, or production infrastructure assurance.

## Security Boundary

MAI Inspector v1.0.0 is a local CLI-based prototype.

The default deterministic evaluation path runs locally against a structured session JSON and does not require external network access or model access.

Optional LLM-assisted session drafting is a separate path. When used, evidence content may be sent to an external API provider selected by the operator.

The operator remains responsible for deciding whether evidence may be sent to an external API under applicable organizational policies, agreements, laws, and data-handling requirements.

## API Key Handling

API keys are read from runtime environment variables by `agent/llm_client.py`.

Implemented environment variable names include:

- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `MAI_LLM_PROVIDER`
- `MAI_OPENAI_MODEL`
- `MAI_ANTHROPIC_MODEL`

The repository includes `.env.example` as a template only.

Real API keys must not be committed to Git.

## Credential Exclusion

The `.gitignore` file excludes:

- `.env`
- `.env.*`
- virtual environments;
- local output folders;
- local release-check artifacts;
- large media files;
- common private document formats such as `.docx`, `.xlsx`, and `.pdf`.

The exception `!.env.example` allows the empty public template to remain in the repository.

No real API keys are required for the deterministic public sample.

## Local Processing Boundary

The public sample workflow uses:

```powershell
python -m agent.mai_agent analyze --workspace . --session sample_data/buildweek_investment_review_session.json --case-name buildweek_sample --output-dir .release_check/buildweek_sample
```

This path loads the structured session JSON, runs the vendored deterministic engine, and writes local outputs.

It does not call OpenAI or Anthropic.

## Input Handling

MAI Inspector can accept:

- an existing structured session JSON through `--session`;
- a project folder through `--project-folder`.

Project-folder intake can read supported public file types and create an evidence pack and inventory.

Input parsing and document extraction are convenience functions for local processing. They are not a malware scanning system, document security gateway, or certified content-inspection layer.

Operators should not process confidential, regulated, personal, privileged, or commercially sensitive files unless they are authorized to do so in their own environment.

## Output and Artifact Boundaries

Local analysis outputs may include:

- copied `session_input.json`;
- draft session files;
- evidence packs;
- sanitized evidence packs;
- redaction reports;
- deterministic result files;
- quality and traceability reports;
- method helper reports;
- `machine_result.json`.

These files are written to the chosen output directory.

When `--session` is used, the structured session is copied into the output directory as `session_input.json`.

When `--project-folder` is used, `evidence_pack.md` may contain extracted text excerpts from source documents, and `inventory.json` records file metadata and excerpts. Reports may also include claims, gates, required evidence, source references, and other structured content derived from the session or evidence pack.

CLI status messages are limited to paths, completion messages, explicit guardrail failures, and external-send confirmation prompts. External API error handling can surface provider error details when optional LLM calls fail.

The `.gitignore` excludes common local output folders, but operators remain responsible for reviewing generated artifacts before sharing, committing, uploading, or publishing them.

The official demo video is not stored in the Git repository. It is distributed as a GitHub Release asset.

## Privacy Guardrails

Implemented privacy-relevant guardrails include:

- external LLM mode is off unless requested with `--use-llm` or the deprecated `--use-openai`;
- raw evidence is blocked from LLM mode unless `--sanitize` is used or `--allow-raw-llm` is explicitly supplied;
- external LLM submission requires `--confirm-send` or `--yes-send`;
- interactive confirmation requires typing `SEND`;
- sanitization can write `sanitized_evidence_pack.md`;
- sanitization writes `redaction_report.json`;
- explicit redaction maps can be supplied through `--redaction-map`;
- currency amount redaction can be requested through `--redact-amounts`.

The sanitizer implements pattern-based and map-based redaction. It does not guarantee removal of every possible sensitive, personal, confidential, regulated, or proprietary item.

## Provenance and Integrity Controls

Provenance is implemented by `agent/engine_runner.py`.

`result.json` records metadata including:

- generation timestamp;
- agent version;
- engine version;
- engine source;
- engine file name;
- engine SHA-256;
- git commit;
- input session SHA-256.

These controls support reproducibility and integrity review of deterministic outputs.

They are not a substitute for access control, tamper-proof audit logging, cryptographic signing, or enterprise security monitoring.

## Dependency and Network Boundary

The deterministic sample path does not require external model calls.

Network calls are implemented in `agent/llm_client.py` for optional LLM-assisted drafting:

- OpenAI Responses API;
- Anthropic Messages API.

The CLI path that can initiate those calls is project-folder session drafting with `--use-llm` or the deprecated `--use-openai`, after the send guardrails described above are satisfied.

The deterministic `--session` evaluation path does not call `agent/llm_client.py` and does not make an external model request.

Those calls use `urllib.request` and runtime API keys.

The repository does not implement a network sandbox, proxy policy, outbound firewall, secrets vault, or centralized credential manager.

Dependencies are listed in `requirements.txt` and package metadata. This document does not claim third-party dependency security certification.

## Public Sample Data

The public Build Week sample is:

```text
sample_data/buildweek_investment_review_session.json
```

It is a controlled public sample for demonstration and reproducibility.

It does not contain real client files or real confidential evidence.

## Operational Responsibilities

Operators are responsible for:

- deciding whether files are appropriate to process locally;
- deciding whether evidence may be sent to an external API;
- reviewing evidence packs before external submission;
- keeping real API keys outside Git;
- reviewing generated outputs before sharing or committing them;
- complying with their applicable data-handling, confidentiality, legal, and regulatory obligations.

MAI Inspector is decision-support software. It does not transfer responsibility for security, privacy, confidentiality, or final decision-making away from the operator or organization.

## Threats Not Addressed

The public release does not address:

- hostile multi-user access;
- hosted service hardening;
- authentication and authorization;
- role-based access control;
- secrets vault integration;
- endpoint or filesystem sandboxing;
- adversarial document malware analysis;
- full prompt-injection defense for external LLM workflows;
- encrypted storage;
- tamper-proof audit trails;
- enterprise logging and monitoring;
- compliance certification.

## Known Limitations

Known limitations include:

- local filesystem security depends on the operator's environment;
- `.gitignore` reduces accidental commits but does not prevent intentional disclosure;
- sanitizer coverage is pattern-based and incomplete by design;
- optional external API processing can transmit evidence outside the local environment;
- provenance hashes support reproducibility but do not prove source evidence is truthful;
- public tests do not certify the system for production security use.

## Release Verification

Verified release state:

```text
v1.0.0^{} = 82b78faf4ea0b584dd185c660c4616e4daf21c52
main      = 805e1de9eccf23f5c66329fd64d306ef9fa5bb5b or later post-release documentation updates
```

Security-relevant implementation anchors:

- [../.gitignore](../.gitignore)
- [../.env.example](../.env.example)
- [../agent/mai_agent.py](../agent/mai_agent.py)
- [../agent/llm_client.py](../agent/llm_client.py)
- [../agent/sanitizer.py](../agent/sanitizer.py)
- [../agent/engine_runner.py](../agent/engine_runner.py)
- [../sample_data/buildweek_investment_review_session.json](../sample_data/buildweek_investment_review_session.json)

Verified boundary checks:

- environment handling verified;
- repository secret scan verified;
- `.gitignore` boundaries verified;
- network behavior verified;
- input and output privacy boundaries verified;
- unsupported security claims removed.
