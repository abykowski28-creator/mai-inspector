# Reproducibility

Reproducibility is supported by the following implemented mechanisms:

- The scoring engine is vendored in the repository.
- `agent/engine_runner.py` prefers the vendored engine.
- Each run writes `result.json`.
- Each run writes a Markdown report with a provenance section.
- Provenance includes engine version, engine SHA-256, and input session SHA-256.
- Tests verify that repeated runs on the public sample preserve score, outcome, engine hash, and input hash.

Public reproducibility check:

```powershell
python -m agent.mai_agent analyze `
  --workspace . `
  --session sample_data\buildweek_investment_review_session.json `
  --case-name buildweek_sample `
  --output-dir .release_check\buildweek_sample
```

Then inspect:

```text
.release_check/buildweek_sample/result.json
.release_check/buildweek_sample/report.md
.release_check/buildweek_sample/machine_result.json
```
