from __future__ import annotations

"""Evidence traceability checks for MAI sessions.

quality_assurance.py checks that an output is *structurally* complete and
self-consistent. It does NOT check whether the claims are actually traceable to
the source documents. This module closes that gap (audit findings #3 and #8):

- Does each material claim cite a source at all?
- Is the citation structured (file + locator + verbatim quote), not just a
  document type?
- Does the quoted text actually appear in the evidence pack? A quote that cannot
  be found is a potential fabrication and is reported as an error.

Source schema (per claim, and usable on any rated item):

    "sources": [
        {"file": "INVESTMENT MEMORANDUM GP.docx",
         "locator": "p.3 / 'Storage' section",
         "quote": "approximately 130,000 m3 of storage capacity"}
    ]

Backward compatibility: a legacy free-text `evidence` string is accepted but
reported as `unstructured_evidence` so it can be migrated.
"""

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

# Quotes shorter than this are not membership-checked against the evidence pack:
# very short fragments match by accident and would produce false "found" results.
MIN_QUOTE_CHARS = 12

# Importance levels that MUST be backed by a structured, verbatim source.
SOURCE_REQUIRED_IMPORTANCE = {"critical", "high"}

# Claim statuses that assert the claim is documented/true, so they MUST quote.
QUOTE_REQUIRED_STATUS = {"confirmed", "verified"}


@dataclass
class TraceIssue:
    severity: str  # "error" | "warning" | "info"
    code: str
    message: str
    claim: str = ""


def normalize(text: str) -> str:
    """Lowercase, unify whitespace and common unicode punctuation for matching."""
    text = text.replace(" ", " ").replace(" ", " ")
    text = text.replace("–", "-").replace("—", "-")  # en/em dash -> hyphen
    text = text.replace("‘", "'").replace("’", "'")
    text = text.replace("“", '"').replace("”", '"')
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower()


def load_evidence_text(output_dir: Path) -> str:
    """Concatenate the case's evidence pack(s) for quote verification.

    Both the raw and sanitized packs are used: a claim drafted from the sanitized
    pack must still trace to it, and a claim drafted from the raw pack should
    trace to the raw pack.
    """
    parts: list[str] = []
    for name in ("evidence_pack.md", "sanitized_evidence_pack.md"):
        path = output_dir / name
        if path.exists():
            try:
                parts.append(path.read_text(encoding="utf-8"))
            except OSError:
                continue
    return "\n".join(parts)


def _iter_sources(item: dict[str, Any]) -> list[dict[str, Any]]:
    raw = item.get("sources")
    if isinstance(raw, list):
        return [s for s in raw if isinstance(s, dict)]
    return []


def check_claim(
    claim: dict[str, Any],
    evidence_norm: str,
    have_evidence: bool,
) -> list[TraceIssue]:
    issues: list[TraceIssue] = []
    label = str(claim.get("claim") or claim.get("text") or "<unnamed claim>")
    importance = str(claim.get("importance") or "").strip().lower()
    status = str(claim.get("status") or "").strip().lower()
    sources = _iter_sources(claim)

    if not sources:
        # No structured source. How loud we are depends on how load-bearing the claim is.
        if str(claim.get("evidence") or "").strip():
            issues.append(TraceIssue(
                "warning", "unstructured_evidence",
                "Claim cites evidence as free text only (no file/locator/quote).", label,
            ))
        else:
            issues.append(TraceIssue(
                "warning", "claim_without_source",
                "Claim has no evidence citation.", label,
            ))
        if importance in SOURCE_REQUIRED_IMPORTANCE:
            issues.append(TraceIssue(
                "error", "material_claim_without_source",
                f"{importance.capitalize()}-importance claim has no structured source.", label,
            ))
        if status in QUOTE_REQUIRED_STATUS:
            issues.append(TraceIssue(
                "error", "confirmed_without_quote",
                f"Claim marked '{status}' but cites no verbatim quote.", label,
            ))
        return issues

    quoted_any = False
    for src in sources:
        file_ref = str(src.get("file") or "").strip()
        quote = str(src.get("quote") or "").strip()
        if not file_ref:
            issues.append(TraceIssue("warning", "source_without_file",
                                     "Source has no file reference.", label))
        if not quote:
            issues.append(TraceIssue("warning", "source_without_quote",
                                     "Source has no verbatim quote.", label))
            continue
        quoted_any = True
        if len(quote) >= MIN_QUOTE_CHARS and have_evidence:
            if normalize(quote) not in evidence_norm:
                issues.append(TraceIssue(
                    "error", "quote_not_in_evidence",
                    f"Quoted text not found in the evidence pack: {quote!r}", label,
                ))

    if status in QUOTE_REQUIRED_STATUS and not quoted_any:
        issues.append(TraceIssue(
            "error", "confirmed_without_quote",
            f"Claim marked '{status}' but no source provides a verbatim quote.", label,
        ))
    return issues


def check_session_traceability(session: dict[str, Any], evidence_text: str = "") -> list[TraceIssue]:
    issues: list[TraceIssue] = []
    claims = session.get("claim_register")
    if not isinstance(claims, list) or not claims:
        issues.append(TraceIssue("warning", "no_claim_register",
                                 "Session has no claim_register to trace."))
        return issues

    evidence_norm = normalize(evidence_text)
    have_evidence = bool(evidence_norm)
    if not have_evidence:
        issues.append(TraceIssue(
            "info", "no_evidence_pack",
            "No evidence pack available; quotes cannot be verified, only presence of citations.",
        ))
    for claim in claims:
        if isinstance(claim, dict):
            issues.extend(check_claim(claim, evidence_norm, have_evidence))
    return issues


def summarize(issues: list[TraceIssue], case_name: str) -> dict[str, Any]:
    errors = [i for i in issues if i.severity == "error"]
    warnings = [i for i in issues if i.severity == "warning"]
    return {
        "case_name": case_name,
        "traceable": not errors,
        "error_count": len(errors),
        "warning_count": len(warnings),
        "issues": [asdict(i) for i in issues],
    }


def build_traceability_report(output_dir: Path, case_name: str) -> dict[str, Any]:
    """Load a scored case from its output folder and check claim traceability."""
    session_path = output_dir / "session_input.json"
    if not session_path.exists():
        session_path = output_dir / "session_draft.json"
    if not session_path.exists():
        return {
            "case_name": case_name, "traceable": False,
            "error_count": 1, "warning_count": 0,
            "issues": [asdict(TraceIssue("error", "missing_session",
                                         "No session_input.json or session_draft.json found."))],
        }
    try:
        session = json.loads(session_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return {
            "case_name": case_name, "traceable": False,
            "error_count": 1, "warning_count": 0,
            "issues": [asdict(TraceIssue("error", "invalid_session", f"Cannot parse session: {exc}"))],
        }
    evidence_text = load_evidence_text(output_dir)
    issues = check_session_traceability(session, evidence_text)
    return summarize(issues, case_name)


def write_traceability_report(output_dir: Path, case_name: str) -> dict[str, Any]:
    report = build_traceability_report(output_dir, case_name)
    (output_dir / "traceability_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8",
    )
    (output_dir / "traceability_report.md").write_text(
        render_traceability_report(report), encoding="utf-8",
    )
    return report


def render_traceability_report(report: dict[str, Any]) -> str:
    status = "TRACEABLE" if report["traceable"] else "NOT TRACEABLE"
    lines = [
        f"# MAI Traceability Report - {report['case_name']}",
        "",
        f"Status: **{status}**",
        "",
        f"Errors: {report['error_count']}",
        f"Warnings: {report['warning_count']}",
        "",
        "## Issues",
        "",
    ]
    if not report["issues"]:
        lines.append("- No traceability issues detected.")
    for issue in report["issues"]:
        claim = f" — claim: {issue['claim']}" if issue.get("claim") else ""
        lines.append(f"- {issue['severity'].upper()} `{issue['code']}`: {issue['message']}{claim}")
    lines.append("")
    return "\n".join(lines)
