# Reproducibility

**Product:** MAI Inspector
**Version:** v1.0.0
**Edition:** OpenAI Build Week Edition
**Status:** Final

## Purpose and Scope

This document explains how an independent reviewer can reproduce the checkable behavior of the public MAI Inspector v1.0.0 release.

It is a release verification document. It is not a user guide, methodology description, production deployment guide, or security certification.

The reproducibility target is the implemented public release behavior: automated tests, public sample execution, five executive outputs, deterministic assessment result, and provenance inspection.

## Verified References

MAI Inspector uses two public references:

```text
v1.0.0
Initial Public Release
82b78faf4ea0b584dd185c660c4616e4daf21c52
```

```text
main
Post-release documentation updates
```

The release tag `v1.0.0` is the reference for reproducing the published product behavior.

The `main` branch contains documentation updates after the release tag, including public demo links and finalized engineering notes.

Post-release behavior boundary was checked with:

```powershell
git diff --name-status v1.0.0..main
git diff --stat v1.0.0..main
git diff --name-status v1.0.0..main -- agent tests sample_data examples
```

The implementation-path diff for `agent`, `tests`, `sample_data`, and `examples` was empty.

The post-release `.env.example` change is configuration-template cleanup and does not change deterministic assessment behavior.

## Reproduction Flow

The recommended reviewer flow is:

```text
Clone repository
        |
        v
Checkout verified reference
        |
        v
Create virtual environment
        |
        v
Install dependencies
        |
        v
Run automated tests
        |
        v
Run public sample
        |
        v
Verify five executive outputs
        |
        v
Inspect provenance
```

## Clean-Clone Verification

Clean-clone verification was performed against:

```text
Repository: https://github.com/abykowski28-creator/mai-inspector.git
Reference: v1.0.0
Commit: 82b78faf4ea0b584dd185c660c4616e4daf21c52
Python: 3.12.13
Dependency file: requirements.txt
```

The clean clone was created in a temporary directory outside the working repository.

## Clone and Checkout

Use the public repository URL:

```powershell
git clone --branch v1.0.0 --depth 1 https://github.com/abykowski28-creator/mai-inspector.git mai-inspector-v1.0.0
cd mai-inspector-v1.0.0
```

Because `v1.0.0` is an annotated tag, Git may report that the tag object itself is not a commit and then switch to the peeled commit. The expected peeled commit is:

```text
82b78faf4ea0b584dd185c660c4616e4daf21c52
```

## Create Environment

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

## Install Dependencies

Install dependencies from the release dependency file:

```powershell
python -m pip install -r requirements.txt
```

The README also supports editable local installation:

```powershell
python -m pip install -e .
```

The verified clean-clone run used `requirements.txt` before running tests and the public sample.

## Run Automated Tests

Verified command:

```powershell
python -m unittest discover -s tests -v
```

Verified result:

```text
Ran 45 tests
OK
```

This confirms the implemented behavior covered by the public test suite. It does not claim complete coverage of all scenarios, production readiness, security certification, or external API integration.

## Run Public Sample

Verified public sample command:

```powershell
python -m agent.mai_agent analyze --workspace . --session sample_data\buildweek_investment_review_session.json --case-name buildweek_sample --output-dir .release_check\buildweek_sample
```

Expected CLI completion message:

```text
MAI analysis complete: <output path>
```

The primary machine-readable output is:

```text
.release_check\buildweek_sample\machine_result.json
```

The deterministic path uses an already prepared Structured Assessment Session. It does not require an API key, does not require a model call, and does not require network access for model execution.

## Verify Five Executive Outputs

Inspect:

```text
.release_check\buildweek_sample\machine_result.json
```

The expected executive outputs are:

```text
Decision Status: Not Yet
Highest Responsible Commitment: Structured Due Diligence
Critical Blockers: Structured Due Diligence remains open.
Required Evidence: Independent technical validation; verified financial information; commercial and operational evidence.
Recommended Next Step: Proceed with Structured Due Diligence before considering a higher commitment.
```

The JSON keys are:

- `decision_status`
- `highest_responsible_commitment`
- `critical_blockers`
- `required_evidence`
- `recommended_next_step`

Display labels in the video and documentation may use title case, while machine-readable output uses normalized JSON keys.

## Inspect Provenance

Inspect:

```text
.release_check\buildweek_sample\result.json
```

The implemented provenance fields are:

- `generated_at`
- `agent_version`
- `engine_version`
- `engine_file`
- `engine_source`
- `engine_sha256`
- `git_commit`
- `input_session_sha256`

These fields support inspection of engine identity, input identity, and execution context.

They are not all expected to be byte-identical across runs because some fields record runtime context.

## Repeated-Run Comparison

Repeated-run verification was performed with two output directories:

```text
.release_check\repro_run_a
.release_check\repro_run_b
```

Both runs used:

```text
sample_data\buildweek_investment_review_session.json
```

Substantive comparison result:

```text
substantive_equal: true
score: 61
outcome: CONDITIONAL GO
decision_status: Not Yet
highest_responsible_commitment: Structured Due Diligence
```

Artifact comparison result:

```text
result.json: not byte-identical
machine_result.json: not byte-identical
report.md: not byte-identical
investor_summary.md: byte-identical
quality_report.json: byte-identical
traceability_report.json: byte-identical
```

Repeated executions of the same validated Structured Assessment Session are expected to produce the same substantive assessment result.

Certain implementation-specific artifacts, such as timestamps, output paths, serialization details, or provenance metadata, may legitimately differ between executions.

## Optional Model-Assisted Path

Optional model-assisted session drafting is not part of the required reproduction scenario.

The optional path can be triggered with:

```text
--use-llm
```

or the deprecated:

```text
--use-openai
```

That path may require environment variables such as `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` and may send evidence to an external provider after the CLI send guardrails are satisfied.

The deterministic public sample does not use that path.

## Troubleshooting

Common reproduction issues:

- Wrong checkout reference: use `v1.0.0` to reproduce the published release behavior.
- Incorrect Python version: verified with Python 3.12.13.
- Missing dependencies: rerun `python -m pip install -r requirements.txt`.
- Invalid Structured Assessment Session: verify the sample path and JSON content.
- Optional model-assisted path missing environment variables: set `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` only if intentionally testing optional external drafting.

## Reproduction Checklist

Use this checklist for release verification:

- Repository cloned.
- Verified reference checked out.
- Virtual environment created.
- Dependencies installed from `requirements.txt`.
- Automated tests passed.
- Public sample executed.
- Five executive outputs verified.
- Provenance inspected.
- Deterministic behavior confirmed at the substantive-result level.
- Expected artifact variability understood.

## Known Limitations

Reproducibility in this release means substantive reproducibility of the deterministic assessment behavior for the same validated input and implementation version.

It does not mean:

- byte-for-byte identity for every generated artifact;
- correctness or completeness of supplied evidence;
- correctness of optional model-assisted drafts;
- production certification;
- security certification;
- universal validity across all decision domains;
- coverage of every possible input file or CLI flag combination.

The public sample is demonstrational and controlled.

## Release Verification

Verified release state at the time of this document:

```text
v1.0.0^{} = 82b78faf4ea0b584dd185c660c4616e4daf21c52
main      = 3ef7a606c8339dc14d09ea940756c1151e779588 or later post-release documentation updates
```

Related documents:

- [ARCHITECTURE.md](ARCHITECTURE.md)
- [TESTING.md](TESTING.md)
- [SECURITY.md](SECURITY.md)
- [DETERMINISTIC_ASSESSMENT.md](DETERMINISTIC_ASSESSMENT.md)

Finalization evidence:

- clean-clone execution completed;
- command sequence checked against README and Technical Overview;
- automated test result matches `engineering/TESTING.md`;
- five executive outputs match the public sample, official demo, and Build Week documentation;
- reproducibility boundary matches `engineering/DETERMINISTIC_ASSESSMENT.md`;
- no unsupported byte-identical artifact guarantee is made.
