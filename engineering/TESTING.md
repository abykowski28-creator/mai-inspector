# Testing

**Product:** MAI Inspector
**Version:** v1.0.0
**Edition:** OpenAI Build Week Edition
**Status:** Final

## Purpose

This document records the implemented test coverage and verified test result for the MAI Inspector public release package.

The purpose is to describe what the current automated tests verify, how they were run, and what the result means for release evaluation.

It does not claim production certification, exhaustive scenario coverage, security certification, external API certification, or enterprise readiness.

## Verified Test Environment

Verified local release environment:

```text
Python 3.12.13
Test framework: unittest
Repository: abykowski28-creator/mai-inspector
```

The test suite was run from the repository root.

Timing is environment-dependent and is not treated as a release requirement.

## Exact Test Command

The verified command is:

```powershell
python -m unittest discover -s tests -v
```

In the local release verification environment, this was also executed with a clean virtual-environment Python interpreter.

## Verified Result

The verified result was:

```text
Ran 45 tests
OK
```

No failures, errors, or skipped tests were reported in the verified run.

The elapsed runtime is intentionally not recorded as a normative requirement because it varies by machine, filesystem, and environment.

## Test Suite Structure

The public test suite contains 14 test files:

- `test_case_learning.py`
- `test_coso_erm.py`
- `test_document_reader.py`
- `test_engine_runner.py`
- `test_evidence_trace.py`
- `test_extraction_coverage.py`
- `test_fixture_quarantine.py`
- `test_fmeca.py`
- `test_iec31010.py`
- `test_iso31000.py`
- `test_machine_output.py`
- `test_mai_agent_workflow.py`
- `test_quality_assurance.py`
- `test_risk_governance_qa.py`

The suite contains 45 test methods discovered by `unittest`.

## Functional Areas Covered

The tests cover implemented behavior in these areas:

- deterministic engine loading and execution;
- public sample reproducibility;
- deterministic output provenance;
- `NO-GO` reachability regression;
- readable deterministic report visual output;
- machine-readable executive outputs;
- document reading for public text-based evidence intake;
- sanitization of basic sensitive fields;
- evidence trace validation;
- extraction coverage warnings;
- quality-assurance gate behavior;
- risk-governance QA checks;
- FMECA helper logic;
- ISO 31000 helper logic;
- IEC 31010 helper logic;
- COSO ERM helper logic;
- fixture isolation and quarantine;
- case learning library behavior;
- CLI workflow guardrail for unreviewed draft scoring.

## Deterministic Engine Tests

The deterministic engine tests are implemented primarily in `tests/test_engine_runner.py`.

They verify that:

- the vendored deterministic engine exists;
- the vendored deterministic engine is preferred;
- the public Build Week sample reproduces expected deterministic outputs;
- repeated execution of the same structured input is reproducible;
- the documented `NO-GO` outcome is reachable for a catastrophic structured session;
- the visual score bar uses readable block characters.

The public deterministic sample is:

```text
sample_data/buildweek_investment_review_session.json
```

The public sample does not require an OpenAI API call.

## CLI and Workflow Tests

CLI and workflow behavior is covered by `tests/test_mai_agent_workflow.py` and related output tests.

The implemented guardrail verifies that a project-folder draft is not scored as a real decision unless explicit override behavior is used for controlled testing.

The tests do not claim full interactive CLI coverage for every flag combination.

## Evidence and Provenance Tests

Evidence and provenance-related behavior is covered by:

- `tests/test_document_reader.py`
- `tests/test_evidence_trace.py`
- `tests/test_extraction_coverage.py`
- `tests/test_engine_runner.py`

These tests verify structural evidence handling, traceability checks, extraction coverage warnings, and deterministic result stamping.

They do not prove that external source documents are factually true.

## Quality and Risk-Governance Tests

Quality and risk-governance behavior is covered by:

- `tests/test_quality_assurance.py`
- `tests/test_risk_governance_qa.py`
- `tests/test_coso_erm.py`
- `tests/test_iso31000.py`
- `tests/test_iec31010.py`
- `tests/test_fmeca.py`

These tests verify implemented helper logic and quality-gate behavior for the public release.

They do not certify compliance with any external standard or regulatory framework.

## Fixture Isolation and Quarantine

Fixture behavior is covered by `tests/test_fixture_quarantine.py`.

The tests verify that known fixture cases are detected and excluded from learning-library construction.

This protects public demonstration fixtures from being treated as ordinary learned cases.

## What Is Not Covered

The public automated test suite does not claim coverage of:

- live OpenAI API calls;
- live Anthropic API calls;
- network integration testing;
- browser, web UI, or hosted backend behavior;
- authentication and authorization systems;
- production deployment infrastructure;
- large-scale benchmark validation;
- adversarial security testing;
- legal, financial, regulatory, or engineering certification;
- factual verification of source evidence;
- exhaustive document-format ingestion for all possible files;
- exhaustive testing of every CLI flag combination.

Optional OpenAI-assisted session drafting is separated from deterministic evaluation.

The deterministic public sample and the 45-test suite can run without external model access.

## Interpretation of Test Results

The verified `45 tests OK` result means that the implemented public behaviors covered by the suite passed in the verified environment.

It supports the release claim that MAI Inspector v1.0.0 includes a reproducible deterministic assessment workflow for the public sample.

It does not mean the product is production-certified, complete for all use cases, or validated for all high-stakes decision domains.

Human review remains required for evidence interpretation, source validation, and final decisions.

## Release References

Release state:

```text
v1.0.0^{} = 82b78faf4ea0b584dd185c660c4616e4daf21c52
main      = 54536619cca81828415d8ecd9a37028b70da2237 or later post-release documentation updates
```

The `v1.0.0` tag points to the initial public release commit.

The `main` branch may include post-release documentation updates, including public demo links and engineering note finalization.

Related engineering documents:

- [ARCHITECTURE.md](ARCHITECTURE.md)
- [DETERMINISTIC_ASSESSMENT.md](DETERMINISTIC_ASSESSMENT.md)
- [REPRODUCIBILITY.md](REPRODUCIBILITY.md)
- [SECURITY.md](SECURITY.md)
