# MAI Inspector - Technical Overview

**Product:** MAI Inspector
**Version:** v1.0.0
**Edition:** OpenAI Build Week Edition
**Status:** Release Candidate, implementation verified

## 1. Purpose

This document describes the implemented public architecture of MAI Inspector v1.0.0.

MAI Inspector is a CLI-based decision intelligence prototype that evaluates whether available evidence responsibly supports a Proposed Decision.

The implementation separates:

1. optional semantic preparation using OpenAI or another supported LLM provider;
2. deterministic evaluation of structured assessment inputs;
3. generation of standardized executive outputs;
4. provenance and reproducibility controls.

This document describes the current public release only.

It does not define future product architecture or introduce additional methodological concepts.

## 2. System Boundary

MAI Inspector v1.0.0 accepts a Structured Assessment Session representing the decision and evidence context required by the deterministic engine.

The public sample session contains fields such as:

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

The system then performs Deterministic MAI Evaluation and produces a Decision Assessment.

The principal system boundary is:

```text
Structured Assessment Session
            |
            v
Deterministic MAI Evaluation
            |
            v
Decision Assessment
```

An optional OpenAI-assisted workflow may be used to draft the Structured Assessment Session from unstructured information.

## 3. High-Level Architecture

```text
Decision Context and Evidence
            |
            v
Optional OpenAI-Assisted Session Drafting
            |
            v
Structured Assessment Session
            |
            v
JSON Parsing, Engine Validation Warnings, and Quality Checks
            |
            v
Deterministic MAI Evaluation
            |
            v
Responsible Commitment Boundary
            |
            v
Five Executive Outputs
            |
            v
Output Files and Provenance Records
```

The architecture deliberately separates semantic interpretation from deterministic assessment.

## 4. Core Components

### 4.1 CLI

The command-line interface provides the public execution workflow.

Implementation anchor: `agent/mai_agent.py`

Depending on the selected mode, the CLI can:

- accept a prepared session with `--session`;
- read a project folder with `--project-folder`;
- create an evidence pack and inventory;
- optionally sanitize evidence before LLM use;
- optionally invoke LLM-assisted session drafting with `--use-llm` and `--provider openai`;
- block raw LLM submission unless explicitly allowed;
- require confirmation before external LLM submission;
- invoke the deterministic assessment engine;
- write reports, QA artifacts, method outputs, traceability output, and machine-readable output;
- expose execution errors and quality-gate failures.

The authoritative user-facing commands are documented in the repository README.

### 4.2 OpenAI-Assisted Session Drafting

OpenAI integration is optional in MAI Inspector v1.0.0.

Implementation anchors: `agent/session_builder.py`, `agent/llm_client.py`

Its purpose is to assist with preparing a Structured Assessment Session from decision context and available information.

The OpenAI-assisted workflow may support:

- interpretation of the Proposed Decision;
- identification of candidate material claims;
- organization of supporting evidence;
- identification of possible gaps or contradictions;
- drafting structured inputs for subsequent evaluation.

The generated draft is not treated as an authoritative decision.

It remains subject to:

- JSON parsing and implementation checks;
- human review;
- deterministic processing;
- provenance controls.

The deterministic engine can also process an approved Structured Assessment Session without making a new model call.

### 4.3 Structured Assessment Session

The Structured Assessment Session is the interface between semantic preparation and deterministic assessment.

It contains the structured information required by the MAI engine.

At a practical level, the public sample shows the current v1.0.0 structure:

- [../sample_data/buildweek_investment_review_session.json](../sample_data/buildweek_investment_review_session.json)

The Structured Assessment Session provides:

- a stable input boundary;
- separation between model output and deterministic logic;
- inspectable assessment inputs;
- repeatable execution;
- support for public sample reproduction.

### 4.4 Input Checks and Quality Gates

The current release does not claim full JSON Schema validation through `jsonschema`.

Implemented checks include:

- JSON parsing of session input;
- engine-level validation warnings from the vendored deterministic engine;
- quality checks over generated result and report artifacts;
- required file checks for output artifacts;
- decision gate checks, including rejection of a `GO` outcome while critical gates remain open;
- optional `--strict-quality` and traceability gate behavior.

Implementation anchors: `agent/engine/mai_decision_lab_v2_1.py`, `agent/quality_assurance.py`, `agent/evidence_trace.py`

Invalid JSON, missing execution inputs, failed quality gates, or unreviewed draft-scoring paths are surfaced explicitly rather than silently treated as authoritative assessments.

### 4.5 Deterministic MAI Evaluation

Deterministic MAI Evaluation is the authoritative assessment stage of the current prototype.

Implementation anchors: `agent/engine_runner.py`, `agent/engine/mai_decision_lab_v2_1.py`

It receives the Structured Assessment Session and applies defined evaluation logic.

Depending on the provided session data, the engine evaluates:

- evidence sufficiency indicators;
- consistency and ambiguity indicators;
- unresolved assumptions;
- failure mechanisms;
- Critical Blockers and decision gates;
- support for the Proposed Decision;
- the Responsible Commitment Boundary.

The engine does not rely on unrestricted natural-language generation to establish the final commitment boundary.

For identical structured inputs and the same implementation version, the deterministic layer is designed to produce the same assessment result.

### 4.6 Responsible Commitment Boundary

The Responsible Commitment Boundary separates commitment levels supported by the available evidence from commitment levels that are not yet supported.

The primary product result derived from this boundary is the Highest Responsible Commitment.

Example:

```text
Proposed Commitment
Investment Approval

Highest Responsible Commitment
Structured Due Diligence
```

In this case, investment approval is not currently supported, but Structured Due Diligence is supported as the responsible next commitment level.

### 4.7 Decision Assessment Outputs

Every completed evaluation writes machine-readable executive outputs.

Implementation anchor: `agent/machine_output.py`

The five outputs are:

1. Decision Status
2. Highest Responsible Commitment
3. Critical Blockers
4. Required Evidence
5. Recommended Next Step

These five outputs form the standardized Decision Assessment interface.

## 5. Processing Pipeline

### Step 1 - Define or Load the Decision Context

The workflow begins with the Proposed Decision and relevant Decision Context.

### Step 2 - Prepare the Structured Assessment Session

The session may be:

- prepared manually;
- loaded from a public sample;
- produced by an approved upstream workflow;
- drafted with optional OpenAI assistance.

### Step 3 - Parse and Check the Session

The system parses JSON and applies implemented validation warnings, QA checks, and guardrails.

### Step 4 - Run Deterministic MAI Evaluation

The structured session is passed to the deterministic engine.

### Step 5 - Establish the Responsible Commitment Boundary

The engine identifies whether the Proposed Decision is supported and what lower commitment level, if any, is responsibly justified.

### Step 6 - Generate Five Executive Outputs

The system produces the standardized Decision Assessment.

### Step 7 - Write Outputs and Provenance Data

Assessment outputs and available provenance information are written according to the public CLI workflow.

## 6. Execution Modes

MAI Inspector v1.0.0 supports two main execution paths.

### Deterministic Sample or Session Evaluation

```text
Approved Structured Assessment Session
                |
                v
Deterministic MAI Evaluation
                |
                v
Decision Assessment
```

This mode supports:

- public sample reproduction;
- automated testing;
- regression checks;
- deterministic comparison;
- operation without a new OpenAI request.

README command:

```bash
python -m agent.mai_agent analyze --workspace . --session sample_data/buildweek_investment_review_session.json --case-name buildweek_sample --output-dir .release_check/buildweek_sample
```

### OpenAI-Assisted Session Drafting

```text
Decision Context and Available Information
                |
                v
OpenAI-Assisted Session Drafting
                |
                v
Structured Assessment Session
                |
                v
Human Review and Implemented Checks
                |
                v
Deterministic MAI Evaluation
                |
                v
Decision Assessment
```

This mode reduces the manual effort required to structure complex information.

OpenAI assistance does not replace deterministic evaluation.

External LLM use is explicit and guarded by CLI flags such as `--use-llm`, `--provider openai`, `--sanitize`, `--confirm-send`, and `--yes-send`.

## 7. Provenance

MAI Inspector includes provenance controls implemented in the public release.

Implementation anchor: `agent/engine_runner.py`

The provenance block written to `result.json` includes:

- generation timestamp;
- agent version;
- engine version;
- engine file;
- engine source;
- engine SHA-256;
- git commit where available;
- input session SHA-256.

The Markdown report also includes a provenance section.

Provenance does not prove that source evidence is factually correct.

It supports traceability between inputs, execution, and outputs.

## 8. Reproducibility

The deterministic execution path is designed to support reproducible assessment.

Reproduction requires:

- the same Structured Assessment Session;
- the same MAI Inspector version;
- the same relevant configuration;
- the same deterministic assessment logic.

The public investment assessment example provides an approved input and expected result.

Its expected primary outputs are:

```text
Decision Status
Not Yet

Highest Responsible Commitment
Structured Due Diligence
```

Detailed reproduction steps are documented in:

- [../engineering/REPRODUCIBILITY.md](../engineering/REPRODUCIBILITY.md)

## 9. Privacy and Security Boundaries

The public prototype implements limited, explicit privacy and configuration controls.

These include:

- API credentials supplied through runtime configuration;
- no committed API credentials;
- defined input and output locations;
- privacy guardrails for external LLM mode;
- sanitizer support for common sensitive fields and explicit redaction maps;
- separation of public sample data from private evidence;
- local deterministic processing after session preparation.

Users remain responsible for determining whether evidence may be submitted to an external model.

Confidential, personal, regulated, or commercially sensitive material should not be processed through OpenAI-Assisted Session Drafting unless the applicable policies, permissions, and agreements allow it.

MAI Inspector v1.0.0 does not claim enterprise security certification.

See:

- [../engineering/SECURITY.md](../engineering/SECURITY.md)

## 10. Public Sample

The repository includes a public investment assessment example.

The example is intended to demonstrate:

- the format of a Structured Assessment Session;
- deterministic evaluation;
- production of the five executive outputs;
- correspondence between the public sample and official demo;
- reproducible output using approved public inputs.

The public sample contains synthetic evidence only and excludes confidential evidence.

See:

- [../sample_data/buildweek_investment_review_session.json](../sample_data/buildweek_investment_review_session.json)

## 11. Testing

The public release includes an automated test suite covering implemented behavior.

Test categories include:

- document reading;
- sanitization;
- deterministic engine runner;
- reproducibility and provenance;
- evidence trace validation;
- extraction coverage warnings;
- fixture quarantine;
- ISO 31000, IEC 31010, COSO ERM, and FMECA helper logic;
- machine output;
- draft scoring guardrails;
- quality assurance;
- risk governance QA;
- public sample reproduction.

The authoritative test command is:

```bash
python -m unittest discover -s tests -v
```

Verified baseline:

```text
Ran 45 tests
OK
```

Detailed testing notes are documented in:

- [../engineering/TESTING.md](../engineering/TESTING.md)

Claims about test coverage should be interpreted only within the functions explicitly tested by the public suite.

Passing tests do not establish the factual correctness of external evidence or suitability for a specific real-world decision.

## 12. Repository Components

The public release is organized around the following components:

```text
agent/          Public MAI Inspector implementation
tests/          Automated tests
docs/           Product and conceptual documentation
demo/           Demo documentation and assets
buildweek/      OpenAI Build Week submission package
engineering/    Engineering evidence
examples/       Public execution examples
sample_data/    Public structured assessment inputs
```

The actual repository structure is authoritative if it differs from this simplified representation.

## 13. Known Limitations

MAI Inspector v1.0.0 is a public prototype.

Current limitations include:

- CLI-based interaction;
- one Decision Object per assessment;
- dependence on structured session inputs for deterministic execution;
- optional OpenAI drafting may require human review;
- model-generated drafts may contain errors or omissions;
- no guarantee of source-document factual correctness;
- no autonomous decision authority;
- no replacement for professional due diligence;
- limited public benchmark coverage;
- no claim of production-grade enterprise deployment readiness;
- no claim of universal document-format ingestion;
- no full JSON Schema validation claim in the current public release;
- no security or regulatory certification.

These limitations define the current product boundary.

## 14. Human Responsibility

MAI Inspector supports human decision-makers.

It does not:

- authorize investments;
- approve acquisitions;
- provide legal or financial advice;
- replace qualified technical review;
- make regulatory determinations;
- remove executive accountability.

The system makes the relationship between evidence and commitment more explicit.

Final decisions remain the responsibility of authorized human decision-makers.

## 15. Technical Design Principle

```text
OpenAI-Assisted Session Drafting
                |
                v
Structured Assessment Session
                |
                v
Deterministic MAI Evaluation
                |
                v
Responsible Commitment Boundary
                |
                v
Five Executive Outputs
```

The semantic layer helps prepare decision evidence.

The deterministic layer establishes the assessment result.

## 16. Release Verification

This document has been checked against:

- the tagged v1.0.0 source;
- the public CLI;
- the public sample;
- the automated test suite;
- the release gate report;
- the engineering documentation.

If the implementation and this document differ, the tagged implementation is authoritative and the documentation must be corrected.

## 17. Conclusion

MAI Inspector v1.0.0 demonstrates a controlled evidence-to-commitment workflow.

OpenAI may assist with transforming unstructured information into a Structured Assessment Session.

Deterministic MAI Evaluation then establishes the Responsible Commitment Boundary and produces five standardized executive outputs.

This architecture combines semantic flexibility with reproducible decision assessment.

**From Document Intelligence to Decision Intelligence.**
