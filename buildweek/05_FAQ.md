# FAQ

## Is MAI Inspector another document summarizer?

No.

Document summarization answers what the documents say. MAI Inspector evaluates whether the available evidence is sufficient to support a specific decision.

## Does MAI Inspector make the decision automatically?

No.

The product supports human judgment. It identifies the responsible level of commitment, blockers, missing evidence, and the next evidence-driven action.

## What is the core insight?

Organizations often have enough information to discuss a decision, but not enough evidence to responsibly act.

MAI Inspector focuses on that difference.

## What does the user provide?

The user provides:

- A proposed decision
- Supporting evidence
- Decision context

The system evaluates evidence relative to that decision.

## What does the user receive?

The user receives a Decision Assessment:

- Decision Status
- Highest Responsible Commitment
- Critical Blockers
- Required Evidence
- Recommended Next Step

## Why does the deterministic engine matter?

High-stakes decision support needs traceability and reproducibility.

OpenAI can help structure evidence. The deterministic MAI engine owns the assessment model, scoring, provenance, and final output structure.

## How is privacy handled?

The prototype is local-only by default.

External LLM use is optional and explicit. The agent includes sanitization, confirmation, and redaction workflows before sending evidence outside the local environment.

## What is working today?

The current prototype includes a local CLI, document extraction, evidence pack generation, draft session creation, optional LLM-assisted session drafting, deterministic scoring, output provenance, investor summaries, quality reports, and 45 passing unit tests.

## What is intentionally out of scope for Build Week?

The Build Week edition does not attempt to be a full enterprise platform.

It focuses on one Decision Object, one workflow, and one executive Decision Assessment so the product concept is easy to understand, demo, and evaluate.

## What should judges remember?

AI already helps people understand information.

MAI Inspector helps people understand whether that information is sufficient to support responsible action.
