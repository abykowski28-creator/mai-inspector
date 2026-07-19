# Security

Implemented security-relevant behavior in this release:

- Local execution is the default path.
- External LLM mode requires explicit CLI flags.
- Raw evidence is blocked from external LLM mode unless explicitly allowed.
- Sanitization can redact sensitive text before an external LLM call.
- Interactive or non-interactive send confirmation is required before LLM session drafting.
- `.env` and `.env.*` files are ignored by Git.
- Public sample data is synthetic.

Implementation anchors:

- LLM send guardrails: `agent/mai_agent.py`
- Sanitization: `agent/sanitizer.py`
- Ignore rules: `.gitignore`
- Public sample: `sample_data/buildweek_investment_review_session.json`

This repository does not claim formal security certification, compliance certification, access control, encryption at rest, or hosted production security controls.
