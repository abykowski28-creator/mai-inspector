# MAI Inspector Project Context

This document is a compact memory file for future work on `mai-inspector`.

## What This Project Is

`mai-inspector` is a public CLI MVP around the MAI Decision Lab / MAI-ADI deterministic engine.

Its job is to:

- read project folders or prepared MAI session JSON files;
- extract source-document text into an evidence pack;
- create a draft or LLM-assisted MAI session JSON;
- run the vendored deterministic MAI/ADI engine;
- write structured outputs and investor-facing summaries;
- protect sensitive data before optional external LLM use.

## Agent Instructions

Public operating guidance lives in `README.md`, `docs/`, `engineering/`, and `buildweek/`.

## Current Product Boundary

The project is a CLI MVP, not a web app or multi-user system.

The LLM can help structure evidence into MAI session JSON, but scoring, ADI multiplier, diagnosis, gates, and final decision outcome belong to the deterministic MAI/ADI engine.

## Core Files

- `agent/mai_agent.py` - CLI entry point and workflow orchestration.
- `agent/document_reader.py` - document extraction, inventory, and evidence-pack creation.
- `agent/session_builder.py` - draft session and LLM prompt construction.
- `agent/llm_client.py` - Anthropic/OpenAI JSON calls.
- `agent/sanitizer.py` - redaction and redaction-report generation.
- `agent/engine_runner.py` - deterministic engine loading and execution.
- `agent/report_generator.py` - investor summary output.
- `agent/case_learning.py` - local learning-library generation from scored outputs.
- `agent/methodology_references.py` - method traceability and stage-gate normalization.
- `agent/quality_assurance.py` - standard quality report and scored-output gate checks.

## Operating Principles

- Local-only by default.
- External LLM calls require explicit flags and confirmation.
- Raw evidence should not be sent externally unless explicitly allowed.
- Sanitized evidence and redaction reports should be reviewed before external processing.
- If evidence is incomplete, stop at missing-data questions or mark assumptions as unverified.
- Automatically generated non-LLM draft sessions are not scored unless `--allow-draft-scoring` is explicitly used for controlled testing.
- Every scored run should produce `quality_report.json` and `quality_report.md`.
- Do not treat the output as legal, technical, financial, tax, sanctions/KYC, environmental, HSE, FEED, or regulatory due diligence.

## Current Known Notes

- `__pycache__/` folders are generated Python runtime artifacts and can reappear after tests.
