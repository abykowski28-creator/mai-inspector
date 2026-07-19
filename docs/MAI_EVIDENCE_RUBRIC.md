# MAI Evidence Rubric & Source Schema

This rubric makes the LLM-assigned inputs **defensible**. Without it, `status`,
`severity` and `likelihood` are free judgments and the deterministic score just
launders a guess (audit finding #2). With it, every rating is tied to a stated
evidence condition that a human can check.

## Source schema

Any claim â€” and optionally any rated item (deviation, assumption, component) â€”
carries structured sources:

```json
"sources": [
  {
    "file": "INVESTMENT MEMORANDUM GP.docx",
    "locator": "p.3, 'Storage capacity' line",
    "quote": "approximately 130,000 m3 of storage capacity across 15 tanks"
  }
]
```

- `file` â€” the source document name as it appears in `inventory.json`.
- `locator` â€” page / section / heading so a human can find it fast.
- `quote` â€” **verbatim** text copied from the evidence pack. This is what makes
  the claim verifiable: the traceability checker confirms this string actually
  appears in `evidence_pack.md` (or `sanitized_evidence_pack.md`).

A legacy free-text `evidence` string is still accepted but flagged
`unstructured_evidence` for migration.

## Claim status rubric (evidence state -> status)

| Status | Required evidence state |
|---|---|
| `confirmed` / `verified` | A primary document is cited **with a verbatim quote** that states the fact directly. Quote must be found in the evidence pack. |
| `conditional` | A source exists but is non-binding, indicative, or depends on an unmet condition (e.g. "subject to DD", a teaser, a draft). |
| `assumed` | Stated by the sponsor/proposal without independent backing; no primary confirmation. |
| `upside` | An optimistic / best-case figure, not a base case. |
| `unverified` | No source, or the source only references the need for the evidence (e.g. a DD question list). |

Rule: a claim may be `confirmed` **only if** at least one source provides a
quote. The checker raises `confirmed_without_quote` otherwise.

## Importance rubric (consequence if wrong)

| Importance | Meaning |
|---|---|
| `critical` | If wrong, the decision outcome flips or capital is lost. Must carry a structured source. |
| `high` | Materially changes economics or timeline. Must carry a structured source. |
| `medium` / `low` | Context; structured source recommended, not required. |

Critical/high claims without a structured source raise
`material_claim_without_source` (error).

## Severity / likelihood rubric (for deviations and risks)

Severity and likelihood stay ordinal, but each level must be justified by a
stated condition, not vibe:

- **severity** = consequence if the deviation materialises (critical = decision
  unrecoverable / capital loss; high = major repricing or delay; medium =
  absorbable; low = cosmetic).
- **likelihood** = evidence that it will occur (high = no mitigating evidence and
  precedent exists; medium = partial mitigation; low = strong evidence it is
  controlled).

When a deviation cites `sources`, the same quote-in-evidence check applies.

## How this is enforced

`agent/evidence_trace.py` runs these checks and writes
`traceability_report.json` / `.md` per case. Wire it into the `--strict-quality`
gate so a case with `quote_not_in_evidence` or `material_claim_without_source`
errors cannot be presented as investor-ready without human sign-off.

This is decision-readiness tracing, not certification: a found quote proves the
text exists in the source, not that the source itself is true.
