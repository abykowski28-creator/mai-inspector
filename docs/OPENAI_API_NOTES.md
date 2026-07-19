# LLM API Notes

Date checked: 2026-06-19

MAI Agent v0.1 supports provider-agnostic LLM session drafting through `agent/llm_client.py`.

Supported providers:

- Anthropic Messages API through `ANTHROPIC_API_KEY`;
- OpenAI Responses API through `OPENAI_API_KEY`.

OpenAI API notes checked:

- Responses API supports `text.format` for text or structured JSON output.
- `{"type": "json_object"}` remains supported as JSON mode, while `json_schema` is preferred for stricter structured outputs when supported.
- `temperature` is supported and should be kept low for deterministic diagnostic output.
- Current model guidance lists `gpt-5.5` as the flagship model and `gpt-5.4-mini` as a lower-latency, lower-cost option.

Current default in `.env.example`:

```text
MAI_OPENAI_MODEL=gpt-5.4-mini
MAI_ANTHROPIC_MODEL=claude-sonnet-4-6
```

For higher-quality reasoning on large project folders, set:

```text
MAI_OPENAI_MODEL=gpt-5.5
```

Future improvement:

- Replace JSON mode with strict `json_schema` output using `mai_session_schema_v2_1.json`.
- Add provider-specific schema enforcement where supported.
