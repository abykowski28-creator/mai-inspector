# Deterministic Assessment

The deterministic assessment layer is implemented in the vendored engine:

```text
agent/engine/mai_decision_lab_v2_1.py
```

The runner prefers the vendored engine by default:

```text
agent/engine_runner.py
```

Confirmed behavior:

- The engine version is included in result provenance.
- The engine SHA-256 is included in result provenance.
- The input session SHA-256 is included in result provenance.
- Re-running the same public sample with the same vendored engine produces the same score and outcome.
- A catastrophic structured session can reach the documented `NO-GO` outcome.

The public sample currently reproduces:

```text
stability_score: 61
decision_outcome: CONDITIONAL GO
decision_architecture_diagnosis: Moderate thesis / weak decision architecture
```

The Build Week demo expresses the product result as executive decision-assessment fields. The CLI writes these fields in `machine_result.json` under `executive_outputs`.
