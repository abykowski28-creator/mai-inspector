# MAI Deterministic Engine Scope

Status: implemented scope note
Date: 2026-06-27

## What the deterministic engine includes

The deterministic engine is vendored in this public release at:

`agent/engine/mai_decision_lab_v2_1.py`

It includes:

- input completeness warnings;
- component risk scoring;
- domain instability scoring;
- stress scenario scoring;
- unresolved assumption scoring;
- semantic ambiguity scoring;
- claim uncertainty scoring;
- breakpoint proximity scoring;
- category caps to reduce duplicate counting;
- ADI multiplier for same-node overload and timing collision;
- stability score calculation;
- outcome selection;
- decision architecture diagnosis;
- failure map extraction;
- decision gate summary;
- Markdown report rendering.

## What the deterministic engine does not yet include

- external standards text;
- official ISO/COSO/IEC certification logic;
- full JSON Schema validation via `jsonschema`;
- scoring profile loading from `scoring_profiles.json`;
- automatic stage-gate inference with evidence audit;
- legal, technical, environmental, tax or financial model validation;
- automatic verification of whether source documents are true, current or legally binding.

## Why this matters

The engine currently calculates repeatable outputs from a structured session JSON. It does not prove that the session JSON is correct. Therefore, each report must include:

- source document list;
- claim-evidence register;
- human analyst review;
- method traceability;
- stage-gate position;
- independent verification requirements.

## Verification Commands

Run the deterministic engine tests:

```powershell
python -m unittest discover -s tests -v
```

Expected result:

```text
Ran 45 tests
OK
```

## Production Hardening Requirements

Before MAI is used as a formal product, add:

1. JSON Schema validation dependency and mandatory validation step.
2. Stage-gate field in schema.
3. Methodology traceability table in every report.
4. External reference registry with official sources and clause anchors.
5. Calibration log by project type.
6. Evidence attachment map for every claim.
7. Version-controlled standard report template.
