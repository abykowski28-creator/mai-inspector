# Deterministic Assessment

**Product:** MAI Inspector
**Version:** v1.0.0
**Edition:** OpenAI Build Week Edition
**Status:** Final

## Purpose and Scope

This document defines the implemented deterministic assessment boundary in MAI Inspector v1.0.0.

Canonical release statement:

```text
Given the same validated Structured Assessment Session, the same MAI engine version, and the same applicable configuration, the deterministic evaluation produces the same substantive assessment result without requiring a model call.
```

The key boundary is substantive assessment result.

This document does not claim that every generated file is byte-for-byte identical across runs. Some artifacts include timestamps, output paths, provenance metadata, or serialization details that may vary between executions.

## Determinism Levels

MAI Inspector v1.0.0 distinguishes three levels:

```text
Same validated assessment input
        |
        v
Same substantive evaluation result
        |
        v
Potentially variable artifact metadata
```

Substantive determinism covers scores, outcomes, gate-derived commitment boundary values, and the five executive decision outputs.

Artifact-level variability may occur in timestamps, generated paths, provenance metadata, report footers, and any field that intentionally records where or when execution occurred.

## Input Determinism

The deterministic input is a Structured Assessment Session.

In the public sample, the canonical file is:

```text
sample_data/buildweek_investment_review_session.json
```

The vendored engine accepts a Python `dict` through:

```text
agent.engine.mai_decision_lab_v2_1.analyze_session(session)
```

The public CLI path accepts JSON through:

```powershell
python -m agent.mai_agent analyze --workspace . --session sample_data/buildweek_investment_review_session.json --case-name buildweek_sample --output-dir .release_check/buildweek_sample
```

The CLI copies the supplied session into the output directory as `session_input.json`, then `agent/engine_runner.py` loads that JSON and calls the vendored engine.

## Structured Input Contract

The public sample is the authoritative example for the implemented input shape.

The engine validation function checks for these top-level or nested fields:

- `decision_brief.decision`
- `system_map.components`
- `system_map.critical_assumptions`
- `domain_analysis`
- `semantic_risks`
- `claim_register`
- `stress_scenarios`
- `deviations`
- `critical_breakpoint`
- `failure_mechanisms`
- `decision_gates`

It also checks selected fields inside assumptions, decision gates, and deviations.

The code and public sample files are authoritative if documentation diverges.

## Validation Boundary

Validation is implemented in:

```text
agent/engine/mai_decision_lab_v2_1.py
```

The `analyze_session(session)` function calls `validate_session(session)` and records returned warnings in `validation_warnings`.

Validation warnings do not stop the lower-level engine evaluation. This is important: the public engine function accepts a Python object directly, and callers that invoke it programmatically are responsible for satisfying the input contract.

The public CLI path performs JSON parsing before engine execution. Invalid JSON, missing input source, missing project-folder learning notes, blocked raw LLM submission, draft-scoring guardrails, and strict quality gate failures can stop CLI execution explicitly.

The public CLI path is therefore a guarded release workflow. The lower-level `analyze_session()` function is an implementation function and should not be treated as a complete input governance layer by itself.

## Evaluation Pipeline

The implemented deterministic evaluation path is:

```text
Structured Assessment Session JSON
        |
        v
JSON parsing and session copy in CLI path
        |
        v
engine_runner loads vendored engine
        |
        v
engine validation warnings
        |
        v
normalization helpers
        |
        v
scoring dimensions and category caps
        |
        v
ADI multiplier
        |
        v
score, outcome, diagnosis, gates, failure map
        |
        v
machine_result.json executive outputs
        |
        v
provenance and output serialization
```

This path does not require a model call.

## Normalization

The engine normalizes many string comparisons through `norm(value)`, which converts missing values to an empty string, strips surrounding whitespace, and lowercases the result.

This affects comparisons such as:

- severity and likelihood levels;
- gate criticality and status;
- claim status and importance;
- assumption status and criticality;
- deviation node and execution-window grouping;
- thesis strength;
- critical breakpoint proximity.

The engine uses internal weight maps such as `LEVEL_WEIGHT`, `IMPACT_WEIGHT`, and `CLAIM_STATUS_WEIGHT`.

## Scoring Dimensions

The implemented scoring dimensions are:

- `component_risk`
- `domain_instability`
- `stress_scenarios`
- `unresolved_assumptions`
- `semantic_ambiguity`
- `claim_uncertainty`
- `breakpoint_proximity`
- `systemic_overload`

These are accumulated in `ScoringBreakdown`.

The engine then applies category caps to reduce duplicate counting:

```text
component_risk <= 8
domain_instability <= 6
stress_scenarios <= 6
unresolved_assumptions <= 5
semantic_ambiguity <= 4
claim_uncertainty <= 3
breakpoint_proximity <= 7
```

If uncapped signals are extreme across multiple layers, the implemented `systemic_overload` deduction can be applied.

## ADI Multiplier

The implemented ADI multiplier is based on deviations sharing affected nodes and execution windows.

Implemented multiplier values:

- `1.30` when same-node overload and timing collision are both detected;
- `1.25` when five or more deviations collide in the same execution window;
- `1.15` when three or more deviations accumulate on the same node;
- `1.0` otherwise.

The final deduction is:

```text
raw_deduction * adi_multiplier
```

The score is:

```text
clamp(100 - final_deduction)
```

## Outcome Thresholds and Blocking Conditions

The implemented outcome thresholds are:

```text
GO              score >= 80 and no open critical gates
CONDITIONAL GO  score >= 60
REDESIGN        score >= 40
NO-GO           score < 40
```

An open critical gate blocks `GO` even when the score is high enough.

In the implemented `choose_outcome()` function, open critical gates do not block `CONDITIONAL GO`, `REDESIGN`, or `NO-GO`; those outcomes are score-threshold driven.

This means blocking rules have priority over aggregate score only for the transition to `GO`.

The machine-readable executive outputs apply an additional gate-sensitive interpretation: `decision_status` is `Supported` only when the outcome is `GO` and there are no open critical gates. Otherwise it is `Not Yet`.

## Responsible Commitment Boundary

The highest responsible commitment is constructed in `agent/machine_output.py`.

The implemented rule is:

```text
first open critical gate name
else normalized stage-gate next_gate
else "Further Review"
```

For the public Build Week sample, the open critical gate is:

```text
Structured Due Diligence
```

Therefore the highest responsible commitment is:

```text
Structured Due Diligence
```

The decision status is computed separately from this label. In the public sample it is:

```text
Not Yet
```

## Five Executive Outputs

The five executive outputs are written under `executive_outputs` in:

```text
machine_result.json
```

The JSON keys are:

- `decision_status`
- `highest_responsible_commitment`
- `critical_blockers`
- `required_evidence`
- `recommended_next_step`

The display labels used in the demo and documentation are:

- Decision Status
- Highest Responsible Commitment
- Critical Blockers
- Required Evidence
- Recommended Next Step

The implemented output order in the JSON object follows the listed key order.

For the public sample, the verified substantive executive outputs are:

```text
Decision Status: Not Yet
Highest Responsible Commitment: Structured Due Diligence
Critical Blockers: Structured Due Diligence remains open.
Required Evidence: Independent technical validation; verified financial information; commercial and operational evidence.
Recommended Next Step: Proceed with Structured Due Diligence before considering a higher commitment.
```

`critical_blockers` and `required_evidence` can be populated from open critical gates. If no required evidence is found from gates, `required_evidence` can fall back to the critical breakpoint.

## Provenance

Provenance is implemented in:

```text
agent/engine_runner.py
```

`result.json` includes:

- `generated_at`
- `agent_version`
- `engine_version`
- `engine_file`
- `engine_source`
- `engine_sha256`
- `git_commit`
- `input_session_sha256`

The Markdown report also receives a provenance footer.

These fields support review of engine identity, input identity, and execution context. They are not part of the substantive assessment result and may vary across runs.

## Separation from OpenAI-Assisted Drafting

The deterministic `--session` evaluation path:

- does not call `agent/llm_client.py`;
- does not require `OPENAI_API_KEY`;
- does not require `ANTHROPIC_API_KEY`;
- does not require network access for model calls;
- accepts an already prepared Structured Assessment Session;
- can be reproduced locally.

Optional project-folder drafting with `--use-llm` or the deprecated `--use-openai` is a separate workflow that can call an external model provider after explicit guardrails are satisfied.

The deterministic assessment claim applies to the structured-session evaluation path, not to generation quality of an optional LLM-created draft.

## Repeated-Run Verification

Repeated-run verification was performed with two separate output directories:

```text
.release_check/determinism/run_a
.release_check/determinism/run_b
```

Both runs used the same public sample session and the same local code state.

Substantive comparison result:

```text
substantive_equal: true
score: 61
outcome: CONDITIONAL GO
decision_status: Not Yet
highest_responsible_commitment: Structured Due Diligence
```

Artifact-level comparison result:

```text
result.json: not byte-identical
machine_result.json: not byte-identical
report.md: not byte-identical
investor_summary.md: byte-identical
quality_report.json: byte-identical
traceability_report.json: byte-identical
```

The non-identical artifacts differ because they include runtime metadata such as `generated_at`, output paths, or provenance/report footer values.

This confirms substantive deterministic assessment behavior while preserving an honest boundary around artifact metadata variability.

## Test Confirmation

The automated test suite confirms this behavior through:

- public sample reproducibility;
- same-input reproducibility;
- vendored-engine preference;
- `NO-GO` reachability regression;
- readable visual bar output;
- machine output construction.

Verified command:

```powershell
python -m unittest discover -s tests -v
```

Verified result:

```text
Ran 45 tests
OK
```

## Human Authority Boundary

MAI Inspector produces structured decision support.

It does not approve, reject, authorize, or execute an investment decision.

Human decision-makers remain responsible for evidence validation, professional due diligence, and final action.

## What Determinism Does Not Guarantee

The deterministic assessment boundary does not guarantee:

- correctness of supplied evidence;
- completeness of the evidence package;
- correctness of an optional OpenAI-generated or Anthropic-generated draft;
- professional due diligence;
- absence of bias in encoded rules;
- universal validity across all decision domains;
- byte-identical artifacts when metadata varies;
- production certification.

## Release Verification

Verified release state at the time of this document:

```text
v1.0.0^{} = 82b78faf4ea0b584dd185c660c4616e4daf21c52
main      = 539866cceed39a4376ac7667c5f8faea0be78d62 or later post-release documentation updates
```

Implementation anchors:

- [../agent/engine/mai_decision_lab_v2_1.py](../agent/engine/mai_decision_lab_v2_1.py)
- [../agent/engine_runner.py](../agent/engine_runner.py)
- [../agent/machine_output.py](../agent/machine_output.py)
- [../agent/methodology_references.py](../agent/methodology_references.py)
- [../tests/test_engine_runner.py](../tests/test_engine_runner.py)
- [../tests/test_machine_output.py](../tests/test_machine_output.py)
- [../sample_data/buildweek_investment_review_session.json](../sample_data/buildweek_investment_review_session.json)

Verified finalization criteria:

- validated input contract reviewed;
- no model call on deterministic path verified;
- scoring and blocking rules verified;
- commitment-boundary logic verified;
- five-output construction verified;
- provenance behavior verified;
- repeated-run comparison completed.
