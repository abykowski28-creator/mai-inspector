# MAI Inspector - Official Build Week Demo

**Product Version:** v1.0.0
**Demo Version:** v2.1
**Edition:** OpenAI Build Week Edition
**Status:** Final

## Watch the Demo

The official Build Week submission demo is hosted on YouTube. The GitHub Release keeps the source-code release and archived release assets attached to `v1.0.0`.

- [Watch official demo video on YouTube](https://youtu.be/P0FDph_TqGA)
- [GitHub Release v1.0.0](https://github.com/abykowski28-creator/mai-inspector/releases/tag/v1.0.0)

It is not stored directly in this Git repository because video files are distributed outside source control.

**Duration:** 2:32
**Resolution:** 1920 x 1080
**Video Codec:** H.264
**Frame Rate:** 25 fps
**Audio:** AAC

## Included Demo Materials

- [Demo_Script.md](Demo_Script.md) - official production script v2.0
- [thumbnail.jpg](thumbnail.jpg) - lightweight approved demo thumbnail

## What the Demo Shows

The demo presents an investment assessment based on a Proposed Decision and an available evidence package.

The central question is:

> **Should we proceed with an investment commitment based on the current evidence package?**

MAI Inspector evaluates whether the available evidence responsibly supports that commitment.

The demo illustrates the product's evidence-to-commitment workflow:

```text
Proposed Decision
        |
        v
Evidence Package
        |
        v
Optional OpenAI-Assisted Session Drafting
        |
        v
Structured Assessment Session
        |
        v
Deterministic MAI Evaluation
        |
        v
Responsible Commitment Boundary
        |
        v
Five Executive Outputs
```

## Demonstrated Result

The official video presents the executive assessment in viewer-facing language:

```text
Decision Status
Not Yet

Highest Responsible Commitment
Structured Due Diligence

Critical Blockers
- Independent technical validation is missing
- Financial verification is incomplete
- Commercial assumptions are insufficiently supported

Required Evidence
- Independent technical validation
- Verified financial information
- Commercial and operational evidence

Recommended Next Step
Proceed with Structured Due Diligence before considering an investment commitment
```

The opportunity is not rejected.

The current evidence supports progression to Structured Due Diligence, but not yet to investment approval.

## The Aha Moment

The defining moment of the demo is the transition:

```text
Decision Status
Not Yet
```

followed by:

```text
Highest Responsible Commitment
Structured Due Diligence
```

This demonstrates the difference between a binary approve/reject system and MAI Inspector.

MAI Inspector does not simply stop a decision.

It identifies the next level of commitment that the available evidence responsibly supports.

## Sound-Off Test

The official demo is designed to remain understandable without audio.

The video visually presents:

- Decision Status;
- Highest Responsible Commitment;
- Critical Blockers;
- Required Evidence;
- Recommended Next Step.

The primary assessment screens remain visible long enough to be read independently of the narration.

The final positioning is:

```text
MAI Inspector
Decision Intelligence for High-Stakes Decisions
From Document Intelligence to Decision Intelligence
```

## Relationship to the Public Sample

The demo and the public investment assessment example represent the same decision outcome and responsible commitment boundary.

Expected public sample result:

```text
Decision Status
Not Yet

Highest Responsible Commitment
Structured Due Diligence
```

The public sample also writes the machine-readable fields `critical_blockers`, `required_evidence`, and `recommended_next_step` in `machine_result.json`.

Those fields use implementation-normalized wording, while the video uses compact executive wording for readability.

Run the public sample from the repository root:

```bash
python -m agent.mai_agent analyze --workspace . --session sample_data/buildweek_investment_review_session.json --case-name buildweek_sample --output-dir .release_check/buildweek_sample
```

Public sample input:

- [../sample_data/buildweek_investment_review_session.json](../sample_data/buildweek_investment_review_session.json)

## Related Materials

- [Official Demo Script](Demo_Script.md)
- [Demo Thumbnail](thumbnail.jpg)
- [Build Week Submission Package](../buildweek/04_SUBMISSION_TEXT.md)
- [Technical Overview](../buildweek/03_TECHNICAL_OVERVIEW.md)

## Technical Verification

The final demo export was verified for:

- 1920 x 1080 resolution;
- H.264 video;
- 25 fps;
- AAC audio;
- readable Decision Assessment screens;
- separate presentation of `Not Yet`;
- separate presentation of `Structured Due Diligence`;
- visibility of the remaining three executive outputs;
- correct final product positioning;
- sound-off comprehension.

## Product Boundary

The demo presents a controlled product scenario.

It does not claim:

- autonomous investment authority;
- completed professional due diligence;
- universal document ingestion;
- guaranteed correctness of model-generated drafts;
- production-grade enterprise deployment;
- replacement of human executive responsibility.

The demonstrated result is decision support, not an automated investment decision.

## Guiding Principle

No organization should commit beyond what its available evidence can responsibly support.

**MAI Inspector**

**From Document Intelligence to Decision Intelligence.**
