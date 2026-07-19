# MAI Agent Data Protection

## Default rule

MAI Agent is local-only by default.

No project content is sent to an external LLM/API unless the user explicitly adds:

```powershell
--use-llm
```

## External API safety gate

When `--use-llm` or backward-compatible `--use-openai` is used with a project folder, MAI Agent blocks raw evidence by default.

Allowed patterns:

```powershell
--sanitize --confirm-send --use-llm --provider anthropic
```

or, for non-interactive automation:

```powershell
--sanitize --yes-send --use-llm --provider openai
```

Unsafe override:

```powershell
--allow-raw-llm --yes-send --use-llm
```

The override exists for controlled testing only. It should not be used for real due diligence materials.

## Sanitization outputs

When `--sanitize` is enabled, the agent writes:

- `sanitized_evidence_pack.md`
- `redaction_report.json`

The report lists how many replacements were made by category.

## Built-in redactions

The sanitizer masks:

- emails;
- phone-like numbers;
- IBANs;
- SWIFT-like codes;
- labeled passport, ID, registration and account numbers;
- signature blocks.

Currency amounts are preserved by default because they are often analytically important.

Use:

```powershell
--redact-amounts
```

when financial figures should not leave the local machine.

## Project-specific redaction map

Use `--redaction-map` for sensitive counterparties, people, project names or assets.

Example:

```json
{
  "ACME Energy Marketing": "COUNTERPARTY_A",
  "COUNTERPARTY_B": "COUNTERPARTY_B",
  "Atlas Sponsor": "SPONSOR_A"
}
```

## Recommended workflow

1. Run local extraction and sanitization:

```powershell
python -m agent.mai_agent analyze --workspace . --project-folder examples/public_case --case-name case_001 --sanitize --draft-only
```

2. Review `sanitized_evidence_pack.md`.
3. Review `redaction_report.json`.
4. Only then run LLM mode with `--confirm-send`.

## Responsibility boundary

Sanitization is a protection layer, not a legal guarantee.

For highly sensitive projects, use local-only mode or manually prepare an approved evidence pack before any external API call.
