# Why OpenAI

**Product:** MAI Inspector
**Version:** v1.0.0
**Edition:** OpenAI Build Week Edition
**Status:** Final

## Purpose

MAI Inspector addresses a problem that begins with unstructured information but ends with a decision boundary.

Real evidence packages contain presentations, technical reports, financial information, inspection records, contracts, and supporting documents. Before this information can be assessed consistently, it must be translated into a structured representation of:

- the Proposed Decision;
- material claims;
- supporting evidence;
- contradictions;
- missing information;
- decision context.

OpenAI provides the semantic capability needed to assist with this translation.

MAI then applies deterministic assessment logic to the resulting structured session.

The architectural principle is:

> **OpenAI helps understand and structure the evidence.**

> **MAI assesses what level of commitment that evidence responsibly supports.**

## Two Different Problems

MAI Inspector separates the workflow into two fundamentally different problems.

### Semantic Interpretation

The first problem is understanding heterogeneous, unstructured information.

This may require:

- identifying material claims;
- recognizing evidence associated with those claims;
- distinguishing evidence from assertion;
- identifying possible contradictions;
- interpreting information relative to the Proposed Decision;
- drafting structured assessment inputs.

This is where OpenAI contributes.

### Deterministic Assessment

The second problem is evaluating the structured session consistently.

This requires:

- applying defined assessment rules;
- calculating evidence sufficiency;
- evaluating blockers;
- establishing the commitment boundary;
- producing standardized outputs;
- preserving provenance;
- supporting reproducibility.

This is the responsibility of the MAI deterministic assessment layer.

## OpenAI's Role in the Current Prototype

MAI Inspector v1.0.0 includes an optional OpenAI-assisted workflow for drafting structured assessment sessions from decision context and available evidence.

OpenAI may assist with:

- interpreting the Proposed Decision;
- identifying candidate material claims;
- structuring available evidence;
- identifying potential gaps or contradictions;
- drafting a session representation for deterministic evaluation.

The resulting structured session is not treated as an unquestionable final answer.

It becomes an input to the MAI assessment workflow and remains subject to:

- schema validation where implemented;
- deterministic processing;
- provenance controls;
- human review;
- explicit decision boundaries.

OpenAI assists with semantic preparation.

It does not independently approve, reject, or authorize a high-stakes decision.

## MAI's Role

The deterministic MAI layer receives structured assessment inputs and applies defined decision-assessment logic.

Its responsibilities include:

- evaluating evidence sufficiency;
- processing consistency and gap indicators;
- identifying Critical Blockers;
- establishing the Highest Responsible Commitment;
- producing the five executive outputs;
- preserving reproducible assessment behavior;
- recording provenance and hashes where implemented.

The five outputs are:

1. Decision Status
2. Highest Responsible Commitment
3. Critical Blockers
4. Required Evidence
5. Recommended Next Step

The final commitment boundary is established by MAI assessment logic rather than generated directly as an unrestricted model opinion.

## Why the Separation Matters

High-stakes AI systems need both interpretive capability and controlled behavior.

A model-only workflow may provide strong semantic interpretation, but its conclusions can vary with prompts, context, and generation.

A rules-only workflow may be reproducible, but it cannot easily interpret complex and heterogeneous natural-language evidence.

MAI Inspector combines the strengths of both approaches:

| OpenAI Layer | MAI Layer |
| --- | --- |
| Interprets unstructured information | Evaluates structured inputs |
| Identifies candidate claims | Applies deterministic logic |
| Structures evidence | Assesses evidence sufficiency |
| Identifies possible contradictions | Establishes the commitment boundary |
| Drafts assessment sessions | Produces standardized outputs |
| Supports semantic reasoning | Supports reproducibility and traceability |

This division is central to the product architecture.

## Optional by Design

The OpenAI-assisted drafting workflow is optional in MAI Inspector v1.0.0.

The deterministic engine can process an already structured assessment session without requiring a new model call.

This supports:

- repeatable testing;
- offline evaluation of public samples;
- deterministic regression checks;
- inspection of known structured inputs;
- separation of semantic drafting from assessment execution.

The public sample case can therefore be reproduced consistently using its approved structured inputs.

This is not a limitation of the architecture.

It is a deliberate separation of concerns.

## Why OpenAI Is Valuable

OpenAI enables MAI Inspector to work toward the conditions found in real decision environments.

Evidence is rarely delivered as a clean scoring table.

It arrives as language, documents, claims, explanations, assumptions, and incomplete records.

OpenAI provides the semantic flexibility required to convert this material into structured decision evidence.

This reduces the gap between:

```text
What the documents contain
        |
        v
What claims are being made
        |
        v
What evidence supports those claims
        |
        v
What information remains missing
```

MAI then evaluates what that structured evidence responsibly permits.

Without the semantic layer, users must perform more of this structuring manually.

Without the deterministic layer, the system loses its controlled and reproducible evidence-to-commitment boundary.

## Human Responsibility

MAI Inspector does not delegate executive responsibility to either the OpenAI model or the deterministic engine.

The system supports human decision-makers by making explicit:

- what evidence is available;
- what remains unsupported;
- what prevents a higher commitment;
- what level of commitment is currently justified;
- what evidence should be obtained next.

Final decisions remain the responsibility of authorized human decision-makers.

## Privacy and Control

The current prototype is designed around explicit input and output boundaries.

Implemented controls are documented in:

- [Security and Privacy](../engineering/SECURITY.md)
- [Architecture](../engineering/ARCHITECTURE.md)
- [Reproducibility](../engineering/REPRODUCIBILITY.md)

API credentials are not embedded in the repository and must be supplied through approved runtime configuration.

Users should not submit confidential, personal, regulated, or commercially sensitive information to an external model unless their organizational policies and applicable agreements permit it.

## Current Boundary

MAI Inspector v1.0.0 demonstrates:

- optional OpenAI-assisted session drafting;
- deterministic processing of structured sessions;
- standardized executive outputs;
- public sample reproduction;
- provenance and testing controls.

The current release does not claim:

- autonomous decision authority;
- fully automated due diligence;
- universal document ingestion;
- guaranteed factual correctness of model-generated drafts;
- replacement of professional review;
- production-grade enterprise security certification.

## Core Formula

```text
Unstructured Evidence
        |
        v
OpenAI-Assisted Session Drafting
        |
        v
Structured Assessment Session
        |
        v
Deterministic MAI Evaluation
        |
        v
Responsible Commitment Boundary
```

OpenAI helps transform information into structured decision evidence.

MAI transforms structured decision evidence into a reproducible assessment of responsible commitment.

## Conclusion

OpenAI is valuable to MAI Inspector because high-stakes evidence begins as meaning, not as a score.

The MAI deterministic layer is necessary because responsible commitment should not depend on an unrestricted model opinion.

Together, they enable a system that combines semantic understanding with controlled decision assessment.

**From Document Intelligence to Decision Intelligence.**
