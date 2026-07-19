# MAI Standard Report Specification

Status: working standard report format
Date: 2026-06-27

## Purpose

Every MAI project report must use the same logic and disclose the same minimum evidence. The report is a decision-readiness memo, not an investment recommendation, legal opinion, FEED report, valuation report or regulatory approval.

## Mandatory Sections

1. Executive Decision Snapshot
2. Decision Under Review
3. Current Stage-Gate Position
4. Methodology and Standards Traceability
5. Evidence Basis and Source Documents
6. Claim-Evidence Register
7. System Map
8. Risk and Domain Analysis
9. FMEA-Style Failure Map
10. Stress Scenarios
11. Critical Breakpoint
12. Decision Gates / Conditions Precedent
13. Scoring Breakdown
14. MAI Outcome and Investor Position
15. Limitations and Required Independent Verification

## Current Stage-Gate Position

Every report must state:

- current stage;
- next gate;
- blocked milestone;
- gate owner;
- minimum evidence to pass the gate;
- whether movement is allowed: proceed / proceed conditionally / redesign / stop.

Example:

```text
Current stage: Stage 2 - Business Case / Pre-FEED
Next gate: FEED authorization and anchor customer term sheet
Blocked milestone: equipment order and investor capital commitment
Gate owner: sponsor / EPC / customer / investor committee
Movement allowed: CONDITIONAL GO only
```

## Methodology and Standards Traceability

Every report must include a table:

| Report component | Method reference | Exact anchor | How applied |
|---|---|---|---|
| Risk process | ISO 31000:2018 | Clauses 4-6 | Risk identification, assessment, treatment and monitoring. |
| Risk techniques | IEC 31010:2019 | risk assessment techniques | Scenario, checklist, sensitivity or FMEA-like analysis. |
| Governance | COSO ERM 2017 | five components / principles 10-13 | Decision owner, risk severity, prioritization, response. |
| Failure map | IEC 60812:2018 | FMEA/FMECA method | Failure mode, effect, criticality and treatment gate. |
| Project set-up maturity | IPA Project Set Up Toolkit | Outcome Profile / Opportunity Framing / Project Routemap | Early-stage why, what and how checks before stage-gate movement. |
| Project delivery gates | GovS 002: Project delivery | Sections 2, 4.2.3, 4.3, 6.3, 7.6, 7.8, 8.6, Annex B, Annex C | Current stage, next gate, blocked milestone, assurance before significant decisions, traceability and verification/validation. |
| Stage gate | Phase-gate / Stage-Gate logic | stage/gate model | Secondary private-sector terminology for current stage, next gate and blocked milestone. |

## Claim-Evidence Register

Claims must be labeled:

| Status | Meaning |
|---|---|
| confirmed | evidence is attached and accepted |
| documented | appears in project documents but requires validation for decision use |
| conditional | depends on another gate or third party |
| assumed | analyst/project assumption |
| unverified | material claim with no evidence |
| upside | potential benefit, not base-case evidence |

## Decision Gates

Each gate must include:

- gate name;
- gate code;
- required evidence;
- owner;
- status;
- criticality;
- blocked milestone;
- standards reference.

## Outcome Rules

| Score / gate condition | Outcome |
|---|---|
| Score >= 80 and no open critical gates | GO |
| Score >= 60 with open gates | CONDITIONAL GO |
| Score 40-59 | REDESIGN |
| Score < 40 | NO-GO |

Open critical gates block unconditional GO even if score is high.

## Standard Limitation Text

Use this limitation text in every investor-facing report:

```text
This MAI report is a decision-readiness assessment. It does not replace legal due diligence, technical due diligence, FEED, HAZOP, environmental assessment, financial model audit, tax review, sanctions/KYC review or regulatory approval. MAI evaluates whether the current decision architecture is reliable enough to proceed to the next stage-gate.
```

## Standard Project Stage Labels

| Stage | Label | Typical examples |
|---|---|---|
| 0 | Concept / Intake | first review, source document package, project idea |
| 1 | Scoping / Pre-DD | preliminary risk map, first investor review |
| 2 | Business Case / Pre-FEED | technical concept, commercial model, early CAPEX/OPEX |
| 3 | FEED / DD / Structuring | engineering, legal, financing, permits, CP drafting |
| 4 | Pilot / Validation | pilot build, performance test, customer acceptance |
| 5 | Execution / Closing / Launch | closing, procurement, launch, first delivery |

## Standard Report File Names

```text
<case_name>_MAI_Standard_Report.md
<case_name>_MAI_Standard_Report.docx
<case_name>_method_traceability.json
quality_report.json
quality_report.md
```

## Standard Quality Gate

Every scored run should write:

- `quality_report.json`;
- `quality_report.md`.

The quality gate must check at minimum:

- required output files exist;
- `stability_score` is an integer from 0 to 100;
- `decision_outcome` is one of GO, CONDITIONAL GO, REDESIGN, NO-GO;
- critical decision gates include gate, required evidence, owner, status and criticality;
- unconditional GO is blocked when a critical gate remains open;
- investor summary includes the MAI decision-readiness limitation;
- traceability and independent verification sections are present.
