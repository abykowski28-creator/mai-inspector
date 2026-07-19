# Testing

The public release candidate uses Python `unittest`.

Command:

```powershell
python -m unittest discover -s tests -v
```

Expected baseline:

```text
45 tests
0 failures
0 skipped
```

Confirmed coverage areas include:

- document reading
- sanitization
- deterministic engine runner
- `NO-GO` reachability regression
- reproducibility and provenance
- evidence trace validation
- extraction coverage warnings
- fixture quarantine
- ISO 31000, IEC 31010, COSO ERM and FMECA helper logic
- machine output
- draft scoring guardrails
- quality assurance
- risk governance QA

The public golden engine test uses `sample_data/buildweek_investment_review_session.json`; it does not depend on private output folders.
