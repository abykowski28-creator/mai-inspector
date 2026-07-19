# Architecture

**Product:** MAI Inspector
**Version:** v1.0.0
**Edition:** OpenAI Build Week Edition
**Status:** Release Candidate, implementation verified

## Purpose and Scope

This document describes the implemented public architecture of MAI Inspector v1.0.0.

MAI Inspector is a local CLI-based decision intelligence prototype. It evaluates whether a Structured Assessment Session supports a Proposed Decision and writes deterministic assessment outputs.

The document covers only the public v1.0.0 release.

It does not describe a web application, hosted backend, database, multi-user service, production deployment platform, or future enterprise architecture.

## System Boundary

The current system accepts one of two input paths:

1. an existing Structured Assessment Session JSON supplied with `--session`;
2. a project folder supplied with `--project-folder`, from which the CLI can build an evidence pack and draft a session.

The deterministic public sample uses the first path.

The main boundary is:

```text
Structured Assessment Session
        |
        v
Deterministic MAI Evaluation
        |
        v
Decision Assessment Outputs
```

OpenAI-assisted session drafting is optional and happens before deterministic evaluation.

## Architecture Overview

Canonical v1.0.0 architecture:

```text
Proposed Decision + Evidence Package
                 |
                 v
Optional OpenAI-Assisted Session Drafting
                 |
                 v
Structured Assessment Session
                 |
                 v
Validation Boundary
                 |
                 v
Deterministic MAI Evaluation
                 |
                 v
Responsible Commitment Boundary
                 |
                 v
Five Executive Decision Outputs
```

Implemented repository flow:

```text
Session JSON or project folder
        |
        v
agent.mai_agent CLI
        |
        v
document_reader / session_builder / sanitizer / llm_client
        |
        v
engine_runner
        |
        v
vendored deterministic engine
        |
        v
reports, quality checks, traceability, machine output, provenance
```

## Core Components

### CLI Entry Point

Implementation: [agent/mai_agent.py](../agent/mai_agent.py)

The CLI exposes two subcommands:

- `analyze`
- `learn`

The Build Week public workflow uses `analyze`.

The `analyze` command can:

- load an existing session JSON with `--session`;
- read a project folder with `--project-folder`;
- write outputs under a case-specific output directory;
- create an evidence pack and inventory;
- optionally sanitize evidence before external LLM use;
- optionally draft a session with `--use-llm` and `--provider openai`;
- block raw LLM submission unless `--allow-raw-llm` is explicitly used;
- require `--confirm-send` or `--yes-send` before external LLM submission;
- refuse scoring of non-LLM draft sessions unless `--allow-draft-scoring` is explicitly used;
- run the deterministic engine;
- write reports, QA outputs, method outputs, traceability output, and `machine_result.json`.

### Document Reader

Implementation: [agent/document_reader.py](../agent/document_reader.py)

The document reader supports project-folder intake by producing:

- `evidence_pack.md`
- `inventory.json`
- `extraction_coverage.json`

This component supports evidence preparation. It is not the deterministic assessment engine.

### Sanitizer

Implementation: [agent/sanitizer.py](../agent/sanitizer.py)

The sanitizer can produce:

- `sanitized_evidence_pack.md`
- `redaction_report.json`

It supports basic redaction patterns and explicit redaction maps before external LLM use.

### Session Builder and LLM Client

Implementations:

- [agent/session_builder.py](../agent/session_builder.py)
- [agent/llm_client.py](../agent/llm_client.py)

These modules support draft session creation.

The LLM client supports provider selection for `anthropic` or `openai`; the OpenAI path uses runtime API credentials supplied outside the repository.

### Engine Runner

Implementation: [agent/engine_runner.py](../agent/engine_runner.py)

The engine runner loads the deterministic MAI engine, runs the session, writes `result.json` and `report.md`, and records provenance metadata.

It prefers the vendored engine included in this repository.

### Vendored Deterministic Engine

Implementation: [agent/engine/mai_decision_lab_v2_1.py](../agent/engine/mai_decision_lab_v2_1.py)

This is the deterministic assessment layer used by the public release. It evaluates the structured session and returns scoring, diagnosis, decision gates, validation warnings, and related assessment data.

### Output and QA Modules

Implemented output and evidence modules include:

- [agent/report_generator.py](../agent/report_generator.py)
- [agent/quality_assurance.py](../agent/quality_assurance.py)
- [agent/evidence_trace.py](../agent/evidence_trace.py)
- [agent/machine_output.py](../agent/machine_output.py)
- [agent/fmeca.py](../agent/fmeca.py)
- [agent/iso31000.py](../agent/iso31000.py)
- [agent/iec31010.py](../agent/iec31010.py)
- [agent/coso_erm.py](../agent/coso_erm.py)

The standardized five executive outputs are written by `agent/machine_output.py` under `executive_outputs` in `machine_result.json`.

## Execution Modes

### Deterministic Session Evaluation

This is the public sample and regression path.

```text
Existing session JSON
        |
        v
agent.mai_agent analyze --session ...
        |
        v
engine_runner
        |
        v
vendored deterministic engine
        |
        v
machine_result.json and reports
```

Verified command:

```bash
python -m agent.mai_agent analyze --workspace . --session sample_data/buildweek_investment_review_session.json --case-name buildweek_sample --output-dir .release_check/buildweek_sample
```

This mode does not require an OpenAI API call.

### Project Folder Drafting

A project folder can be processed into an evidence pack and draft session.

```text
Project folder
        |
        v
document_reader
        |
        v
evidence_pack.md + inventory.json
        |
        v
session_builder
        |
        v
session_draft.json
```

By default, the CLI refuses to score an automatically generated non-LLM draft session unless `--allow-draft-scoring` is explicitly used for controlled testing.

### OpenAI-Assisted Session Drafting

OpenAI-assisted drafting is optional.

```text
Project folder evidence
        |
        v
optional sanitizer
        |
        v
--use-llm --provider openai
        |
        v
session_input.json
        |
        v
deterministic MAI evaluation
```

Raw LLM mode is blocked by default. External send requires explicit confirmation through `--confirm-send` or `--yes-send`.

### Learning Library Generation

The `learn` subcommand builds a local learning library from completed output folders.

Implementation: [agent/case_learning.py](../agent/case_learning.py)

This is not part of the Build Week demo path.

## Data Flow

For the deterministic public sample:

```text
sample_data/buildweek_investment_review_session.json
        |
        v
output_dir/session_input.json
        |
        v
agent/engine_runner.py
        |
        v
agent/engine/mai_decision_lab_v2_1.py
        |
        v
output_dir/result.json
output_dir/report.md
output_dir/investor_summary.md
output_dir/quality_report.json
output_dir/quality_report.md
output_dir/traceability_report.json
output_dir/traceability_report.md
output_dir/machine_result.json
```

Additional method output files may also be written, including FMECA, ISO 31000, IEC 31010, COSO ERM, standard report, and method traceability artifacts.

## Structured Assessment Session

The public sample is the authoritative example of the current Structured Assessment Session format:

- [../sample_data/buildweek_investment_review_session.json](../sample_data/buildweek_investment_review_session.json)

The public sample includes these top-level fields:

- `session_id`
- `session_date`
- `decision_brief`
- `thesis_strength`
- `critical_breakpoint_proximity`
- `system_map`
- `domain_analysis`
- `semantic_risks`
- `claim_register`
- `stress_scenarios`
- `deviations`
- `critical_breakpoint`
- `failure_mechanisms`
- `decision_gates`

The code and sample files are authoritative if documentation and implementation diverge.

## Validation Boundary

The current public release does not claim full JSON Schema validation through `jsonschema`.

Implemented validation and guardrail behavior includes:

- JSON parsing of session input;
- engine-level `validate_session` warnings in the vendored engine;
- quality checks in `agent/quality_assurance.py`;
- traceability checks in `agent/evidence_trace.py`;
- extraction coverage warnings for project-folder evidence packs;
- guardrails against scoring unreviewed non-LLM draft sessions;
- optional strict quality failure behavior through `--strict-quality`.

Invalid JSON, missing execution inputs, or failed strict gates are surfaced as explicit failures.

Validation does not prove that source evidence is factually correct.

## OpenAI-Assisted Session Drafting

OpenAI-assisted drafting supports semantic preparation of structured assessment inputs.

It can help transform unstructured evidence into a draft session for human review and deterministic processing.

It does not establish the final Responsible Commitment Boundary.

The deterministic engine can process an approved session without making a new model call.

OpenAI credentials are not committed to the repository. They must be supplied through runtime configuration.

## Deterministic MAI Evaluation

Deterministic MAI Evaluation is performed by the vendored engine through `agent/engine_runner.py`.

For identical structured inputs and the same implementation version, this layer is designed to produce the same score, outcome, decision gates, and related assessment outputs.

The deterministic layer is responsible for the assessment result. It does not rely on unrestricted model generation for the final commitment boundary.

## Decision Assessment Outputs

The machine-readable output is written to `machine_result.json`.

Its `schema_version` is:

```text
mai-machine-result-v1
```

The standardized executive output object is:

```text
executive_outputs
```

It contains:

- `decision_status`
- `highest_responsible_commitment`
- `critical_blockers`
- `required_evidence`
- `recommended_next_step`

For the public sample, the primary expected outputs are:

```text
Decision Status: Not Yet
Highest Responsible Commitment: Structured Due Diligence
```

## Provenance and Reproducibility

Provenance is implemented in [agent/engine_runner.py](../agent/engine_runner.py).

The `result.json` provenance block includes:

- `generated_at`
- `agent_version`
- `engine_version`
- `engine_file`
- `engine_source`
- `engine_sha256`
- `git_commit`
- `input_session_sha256`

The Markdown report also receives a provenance section.

Reproducibility depends on the same session input, same engine implementation, same versioned code, and same relevant configuration.

See also:

- [REPRODUCIBILITY.md](REPRODUCIBILITY.md)
- [DETERMINISTIC_ASSESSMENT.md](DETERMINISTIC_ASSESSMENT.md)

## Trust and Authority Boundaries

MAI Inspector is decision-support software.

The system does not:

- approve investments;
- authorize acquisitions;
- provide legal, financial, regulatory, or engineering advice;
- certify evidence as true;
- replace professional due diligence;
- remove executive responsibility.

OpenAI-assisted drafting helps structure meaning.

Deterministic MAI Evaluation establishes the implemented assessment output.

Human decision-makers remain responsible for final action.

## Failure Behaviour

The current CLI is designed to fail explicitly in several important cases:

- no `--session` or `--project-folder` is provided;
- raw LLM mode is requested without `--sanitize` or `--allow-raw-llm`;
- LLM mode is requested without `--confirm-send` or `--yes-send`;
- interactive confirmation does not receive `SEND`;
- a learning notes file requested with `--use-learning` is missing;
- an automatically generated non-LLM draft is scored without `--allow-draft-scoring`;
- `--strict-quality` is used and quality or traceability gates fail.

Quality warnings may still be written for human review without stopping execution unless strict gate flags are used.

## Current Deployment Model

The current deployment model is local execution from a Git repository.

The public release includes:

- Python source files;
- public sample data;
- tests;
- documentation;
- demo metadata and thumbnail.

The repository does not include:

- hosted backend services;
- a web UI;
- persistent database services;
- production authentication;
- enterprise deployment automation;
- the final 94 MB demo video file.

## Known Limitations

MAI Inspector v1.0.0 is a public prototype.

Known limitations include:

- CLI-only interaction;
- one primary Decision Object per assessment;
- deterministic execution depends on structured session input;
- OpenAI-assisted drafts require human review;
- no guarantee of source-document factual correctness;
- no universal document-format ingestion claim;
- no full JSON Schema validation claim;
- limited public benchmark coverage;
- no production-grade enterprise security certification;
- no autonomous decision authority.

## Implementation References

Core implementation:

- [../agent/mai_agent.py](../agent/mai_agent.py)
- [../agent/document_reader.py](../agent/document_reader.py)
- [../agent/sanitizer.py](../agent/sanitizer.py)
- [../agent/session_builder.py](../agent/session_builder.py)
- [../agent/llm_client.py](../agent/llm_client.py)
- [../agent/engine_runner.py](../agent/engine_runner.py)
- [../agent/engine/mai_decision_lab_v2_1.py](../agent/engine/mai_decision_lab_v2_1.py)
- [../agent/machine_output.py](../agent/machine_output.py)
- [../agent/quality_assurance.py](../agent/quality_assurance.py)
- [../agent/evidence_trace.py](../agent/evidence_trace.py)

Verification references:

- [TESTING.md](TESTING.md)
- [SECURITY.md](SECURITY.md)
- [REPRODUCIBILITY.md](REPRODUCIBILITY.md)
- [DETERMINISTIC_ASSESSMENT.md](DETERMINISTIC_ASSESSMENT.md)
- [../tests/](../tests/)
- [../sample_data/buildweek_investment_review_session.json](../sample_data/buildweek_investment_review_session.json)
