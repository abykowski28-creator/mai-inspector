# MAI Agent v0.1 Technical Specification

## Objective

Create a local working AI agent that converts project documents into MAI Decision Lab analysis outputs.

## MVP boundary

The first version is a command-line agent, not a web app.

It supports two workflows:

1. Existing session workflow: run a prepared MAI session JSON through the deterministic engine.
2. Project folder workflow: extract documents, build an evidence pack, create a draft session, and optionally use an external LLM to draft the structured session JSON.

## Non-goals in v0.1

- No autonomous investment decision.
- No automatic claim of factual certainty.
- No replacement of legal, financial, engineering or regulatory due diligence.
- No database or multi-user platform.

## Human-in-the-loop rule

Before investor-facing use, a human analyst must review:

- thesis_strength;
- critical decision gates;
- unverified assumptions;
- semantic risk classification;
- critical breakpoint;
- final investor framing.

## Data protection rule

The default execution mode is local-only.

External API calls require explicit `--use-llm` or the backward-compatible `--use-openai`. Raw evidence is blocked from LLM mode unless the user also provides `--allow-raw-llm` or the backward-compatible `--allow-raw-openai`.

Recommended external API path:

```text
raw documents -> evidence pack -> sanitization -> human review -> LLM session draft -> local MAI engine -> quality report
```

## Core components

| Component | File | Role |
|---|---|---|
| CLI | `agent/mai_agent.py` | Entry point. |
| Document Reader | `agent/document_reader.py` | Extracts text and builds evidence packs. |
| Session Builder | `agent/session_builder.py` | Creates draft or LLM-generated MAI session JSON. |
| Engine Runner | `agent/engine_runner.py` | Runs deterministic MAI/ADI engine. |
| Report Generator | `agent/report_generator.py` | Creates investor summary. |
| LLM Client | `agent/llm_client.py` | Optional Anthropic/OpenAI JSON generation. |
| Sanitizer | `agent/sanitizer.py` | Redacts sensitive evidence before external API use. |
| Quality Assurance | `agent/quality_assurance.py` | Checks scored outputs for required files, gate completeness and standard-report boundaries. |

## Output files

Each case writes:

- `evidence_pack.md`
- `inventory.json`
- `session_draft.json` or `session_input.json`
- `result.json`
- `report.md`
- `investor_summary.md`
- `<case_name>_MAI_Standard_Report.md`
- `<case_name>_method_traceability.json`
- `quality_report.json`
- `quality_report.md`
- `missing_data_questions.md` when applicable
- `sanitized_evidence_pack.md` when `--sanitize` is used
- `redaction_report.json` when `--sanitize` is used

## Reliability principle

The LLM is allowed to structure evidence.

The deterministic engine owns scoring, ADI multiplier, diagnosis and outcome.

Automatically generated non-LLM draft sessions are not scored by default. They must remain draft-only unless the operator explicitly uses `--allow-draft-scoring` for controlled testing.
