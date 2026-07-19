# MAI Inspector

## Decision Intelligence for High-Stakes Decisions

**AI understands information.**

**But organizations still need to know whether their evidence is sufficient to act.**

**MAI Inspector fills that gap.**

MAI Inspector is an AI-assisted decision intelligence system that evaluates whether the available evidence responsibly supports a proposed high-stakes decision.

Instead of asking only:

> What do these documents say?

MAI Inspector asks:

> What level of commitment does the available evidence responsibly support?

This represents a shift:

**From Document Intelligence to Decision Intelligence.**

## The Problem

Organizations make investment, acquisition, technology, infrastructure, partnership, and deployment decisions using complex evidence packages that may include:

- presentations;
- technical reports;
- financial information;
- inspection records;
- scientific publications;
- contracts;
- regulatory documents;
- due diligence materials.

Modern AI systems can summarize, compare, and explain these documents.

But document understanding does not answer the central decision question:

> Do we have enough evidence to responsibly make this decision?

An evidence package may be persuasive without being sufficient.

Its claims may exceed the available validation. Important information may be missing, contradictory, outdated, or unsupported.

MAI Inspector evaluates the relationship between the proposed decision, the available evidence, and the level of commitment that evidence can responsibly support.

## Watch the Official Demo

The official Build Week demo is intentionally not stored in this Git repository because the approved export is approximately 94 MB.

Demo package:

- [Watch official demo video](https://github.com/abykowski28-creator/mai-inspector/releases/download/v1.0.0/MAI_Inspector_Official_Build_Week_Demo_v2.0_1080p.mp4)
- [GitHub Release v1.0.0](https://github.com/abykowski28-creator/mai-inspector/releases/tag/v1.0.0)
- [Demo README and video release notes](demo/README.md)
- [Official production script](demo/Demo_Script.md)
- [Demo thumbnail](demo/thumbnail.jpg)

**Duration:** 2:09
**Format:** 1920 x 1080, H.264
**Version:** MAI Inspector v1.0.0 - OpenAI Build Week Edition

The demo presents an investment assessment based on an available evidence package.

The proposed investment commitment is assessed as:

**Decision Status**

> Not Yet

**Highest Responsible Commitment**

> Structured Due Diligence

The system does not reject the opportunity.

It identifies the highest level of commitment that the current evidence can responsibly support.

## How It Works

Every assessment begins with a **Decision Object**:

```text
Proposed Decision
        +
Supporting Evidence
        +
Decision Context
        |
        v
Optional OpenAI Semantic Layer
        |
        v
Structured Claims and Evidence
        |
        v
MAI Deterministic Assessment Engine
        |
        v
Executive Decision Assessment
```

### 1. Define the Proposed Decision

The user states the decision to be evaluated.

Example:

```text
Should we proceed with an investment commitment based on the current evidence package?
```

### 2. Provide Supporting Evidence

The system receives the available evidence relevant to that decision.

The public release supports a reviewed structured session JSON as the deterministic sample input. The CLI also includes document extraction, evidence inventory, sanitization, and optional LLM-assisted session drafting.

### 3. Structure the Evidence with OpenAI

The optional OpenAI semantic layer can support:

- material claim identification;
- evidence structuring;
- contradiction identification;
- decision-context interpretation;
- conversion of unstructured information into structured assessment inputs.

External LLM use is explicit. Local deterministic execution works without an OpenAI API key when a reviewed session JSON is provided.

### 4. Apply Deterministic MAI Assessment

The structured evidence is evaluated by the MAI deterministic assessment layer.

This layer applies reproducible logic to assess:

- evidence sufficiency;
- internal consistency;
- missing information;
- critical blockers;
- responsible commitment boundaries.

### 5. Produce the Executive Assessment

The result is presented through five standard executive outputs.

## Five Executive Outputs

### Decision Status

Whether the proposed decision is currently supported by the available evidence.

Build Week Edition uses two executive statuses:

- `Supported`
- `Not Yet`

`Not Yet` means that the current evidence is insufficient for the proposed commitment. It does not mean that the opportunity has been rejected.

### Highest Responsible Commitment

The maximum level of commitment that the available evidence can responsibly support.

This is the defining capability of MAI Inspector.

### Critical Blockers

The conditions preventing support for a higher level of commitment.

Examples include:

- missing independent validation;
- inconsistent performance claims;
- incomplete financial verification;
- unsupported commercial assumptions;
- unresolved technical uncertainty.

### Required Evidence

The additional evidence needed to reduce the gap between the proposed decision and the currently supported commitment.

### Recommended Next Step

The immediate evidence-driven action that allows the assessment to progress responsibly.

## Example Result

```text
Decision Status
Not Yet

Highest Responsible Commitment
Structured Due Diligence

Critical Blockers
- Structured Due Diligence remains open.

Required Evidence
- Independent technical validation; verified financial information; commercial and operational evidence.

Recommended Next Step
Proceed with Structured Due Diligence before considering a higher commitment.
```

## Why It Is Different

MAI Inspector is not another document summarizer.

| Traditional Document AI | MAI Inspector |
| --- | --- |
| Summarizes documents | Evaluates a Decision Object |
| Retrieves information | Maps claims to evidence |
| Explains what documents say | Assesses what the evidence supports |
| Generates recommendations | Establishes a responsible commitment boundary |
| Primarily model-driven | Combines optional OpenAI structuring with deterministic assessment |
| May produce variable conclusions | Supports reproducible and traceable assessment |

The system separates two functions:

**OpenAI can help understand and structure the evidence.**

**MAI assesses what level of commitment that evidence responsibly supports.**

## What Is Already Implemented

MAI Inspector v1.0.0 includes:

- a working CLI prototype;
- optional OpenAI-assisted structured session drafting;
- structured claim and evidence processing;
- deterministic decision assessment;
- five executive decision outputs;
- provenance and hashing controls;
- privacy guardrails;
- a reproducible public sample case;
- automated tests;
- public product and technical documentation;
- an official OpenAI Build Week demo package.

The current release focuses on one complete evidence-to-commitment workflow.

## Run the Public Example

The public example reproduces the investment assessment presented in the official demo.

### 1. Clone the Repository

After the public GitHub repository is created, clone it with:

```bash
git clone https://github.com/AlexanderBykovski/mai-inspector.git
cd mai-inspector
```


### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it:

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
python -m pip install -r requirements.txt
python -m pip install -e .
```

### 4. Run the Tests

Verified test command:

```bash
python -m unittest discover -s tests -v
```

Expected result:

```text
Ran 45 tests
OK
```

### 5. Run the Sample Assessment

Verified sample command:

```bash
python -m agent.mai_agent analyze --workspace . --session sample_data/buildweek_investment_review_session.json --case-name buildweek_sample --output-dir .release_check/buildweek_sample
```

The expected executive assessment is:

```text
Decision Status: Not Yet
Highest Responsible Commitment: Structured Due Diligence
```

Machine-readable output is written to:

```text
.release_check/buildweek_sample/machine_result.json
```

Public sample input:

- [sample_data/buildweek_investment_review_session.json](sample_data/buildweek_investment_review_session.json)

## Architecture

```text
Evidence Package or Reviewed Session JSON
        |
        v
Input and Privacy Controls
        |
        v
Optional OpenAI Semantic Evidence Structuring
        |
        v
Structured Evidence Representation
        |
        v
Deterministic MAI Assessment Engine
        |
        v
Provenance and Reproducibility Controls
        |
        v
Decision Assessment
```

Technical documentation:

- [Architecture](engineering/ARCHITECTURE.md)
- [Deterministic Assessment](engineering/DETERMINISTIC_ASSESSMENT.md)
- [Testing](engineering/TESTING.md)
- [Security and Privacy](engineering/SECURITY.md)
- [Reproducibility](engineering/REPRODUCIBILITY.md)

## OpenAI Build Week 2026

MAI Inspector v1.0.0 is the first public release of the product and was prepared as the OpenAI Build Week Edition.

Submission materials:

- [One-Page Pitch](buildweek/01_One_Page_Pitch.md)
- [Why OpenAI](buildweek/02_WHY_OPENAI.md)
- [Technical Overview](buildweek/03_TECHNICAL_OVERVIEW.md)
- [Submission Text](buildweek/04_SUBMISSION_TEXT.md)
- [Frequently Asked Questions](buildweek/05_FAQ.md)
- [Submission Readiness](buildweek/06_Submission_Readiness.md)

## Current Scope

The Build Week Edition supports:

- one Decision Object per assessment;
- one structured evidence-to-commitment workflow;
- deterministic assessment over structured evidence;
- five standardized executive outputs;
- a CLI-based public prototype;
- a reproducible public sample case.

The current version is a prototype and decision-support tool.

It does not replace:

- executive responsibility;
- legal advice;
- financial advice;
- regulatory approval;
- professional technical judgment;
- independent due diligence.

## Guiding Principle

No organization should commit beyond what its available evidence can responsibly support.

## Repository Structure

```text
mai-inspector/
|-- README.md
|-- LICENSE
|-- CHANGELOG.md
|-- pyproject.toml
|-- requirements.txt
|-- agent/
|-- tests/
|-- docs/
|-- demo/
|-- buildweek/
|-- engineering/
|-- examples/
`-- sample_data/
```

## Team

**Prof. Dr. Alexander Bykovski**
Founder and President, EnergeticaX Institute Limited

Product concept, decision reliability methodology, architecture, domain expertise, and product leadership.

Development support was provided through AI-assisted software engineering, testing, documentation, and release preparation using OpenAI and Codex workflows.

## License

Copyright © 2026 EnergeticaX Institute Limited.

All rights reserved.

This repository is publicly available for evaluation and demonstration. Public availability does not grant permission to copy, modify, distribute, sublicense, or commercially use the software, methodology, documentation, or related materials except where expressly authorized in writing.

See [LICENSE](LICENSE) for the complete terms.

## Release

MAI Inspector v1.0.0 - OpenAI Build Week Edition

**From Document Intelligence to Decision Intelligence.**
