from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class RedactionReport:
    replacements: dict[str, int] = field(default_factory=dict)
    redaction_map_used: bool = False

    def add(self, label: str, count: int) -> None:
        if count:
            self.replacements[label] = self.replacements.get(label, 0) + count

    def to_dict(self) -> dict:
        return {
            "redaction_map_used": self.redaction_map_used,
            "replacements": self.replacements,
        }


PATTERNS: list[tuple[str, re.Pattern[str], str]] = [
    (
        "EMAIL",
        re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE),
        "[REDACTED_EMAIL]",
    ),
    (
        "PHONE",
        re.compile(r"(?<!\w)(?:\+?\d[\d\s().-]{7,}\d)(?!\w)"),
        "[REDACTED_PHONE]",
    ),
    (
        "IBAN",
        re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9]{11,30}\b", re.IGNORECASE),
        "[REDACTED_IBAN]",
    ),
    (
        "SWIFT",
        re.compile(r"\b(?:swift|bic)\s*[:#-]?\s*[A-Z]{6}[A-Z0-9]{2}(?:[A-Z0-9]{3})?\b", re.IGNORECASE),
        "[REDACTED_SWIFT]",
    ),
    (
        "LABELED_ID",
        re.compile(
            r"\b(?:passport|civil id|national id|id no\.?|passport no\.?|license no\.?|"
            r"registration no\.?|bank account|account number|routing number)\s*[:#-]?\s*[A-Z0-9-]{4,}\b",
            re.IGNORECASE,
        ),
        "[REDACTED_ID_OR_ACCOUNT]",
    ),
    (
        "SIGNATURE_BLOCK",
        re.compile(r"(?im)^\s*(?:signed by|signature|authorized signatory)\s*[:#-]?.*$"),
        "[REDACTED_SIGNATURE_BLOCK]",
    ),
]


AMOUNT_PATTERN = re.compile(
    r"(?<!\w)(?:USD|US\$|OMR|AED|EUR|GBP|\$|€|£)\s?\d[\d,]*(?:\.\d+)?(?:\s?(?:m|mn|million|bn|billion))?",
    re.IGNORECASE,
)


def load_redaction_map(path: Path | None) -> dict[str, str]:
    if not path:
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Redaction map must be a JSON object")
    return {str(key): str(value) for key, value in data.items()}


def apply_explicit_map(text: str, redaction_map: dict[str, str], report: RedactionReport) -> str:
    for source, replacement in sorted(redaction_map.items(), key=lambda item: len(item[0]), reverse=True):
        if not source:
            continue
        pattern = re.compile(re.escape(source), re.IGNORECASE)
        text, count = pattern.subn(replacement, text)
        report.add(f"MAP:{replacement}", count)
    if redaction_map:
        report.redaction_map_used = True
    return text


def sanitize_text(
    text: str,
    redaction_map: dict[str, str] | None = None,
    redact_amounts: bool = False,
) -> tuple[str, RedactionReport]:
    report = RedactionReport()
    sanitized = apply_explicit_map(text, redaction_map or {}, report)

    for label, pattern, replacement in PATTERNS:
        sanitized, count = pattern.subn(replacement, sanitized)
        report.add(label, count)

    if redact_amounts:
        sanitized, count = AMOUNT_PATTERN.subn("[REDACTED_AMOUNT]", sanitized)
        report.add("AMOUNT", count)

    return sanitized, report


def sanitize_file(
    input_path: Path,
    output_path: Path,
    report_path: Path,
    redaction_map_path: Path | None = None,
    redact_amounts: bool = False,
) -> RedactionReport:
    redaction_map = load_redaction_map(redaction_map_path)
    text = input_path.read_text(encoding="utf-8")
    sanitized, report = sanitize_text(
        text,
        redaction_map=redaction_map,
        redact_amounts=redact_amounts,
    )
    output_path.write_text(sanitized, encoding="utf-8")
    report_path.write_text(json.dumps(report.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    return report
