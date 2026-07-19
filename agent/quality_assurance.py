from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .iso31000 import build_iso31000
from .coso_erm import build_coso_erm


ALLOWED_OUTCOMES = {"GO", "CONDITIONAL GO", "REDESIGN", "NO-GO"}
OPEN_GATE_STATUSES = {"open", "pending", "missing", "unverified", "conditional", "incomplete"}
REQUIRED_GATE_FIELDS = ("gate", "required_evidence", "owner", "status", "criticality")


@dataclass
class QualityIssue:
    severity: str
    code: str
    message: str


def build_quality_report(output_dir: Path, case_name: str) -> dict[str, Any]:
    issues: list[QualityIssue] = []

    result = _load_json(output_dir / "result.json", issues, "result.json")
    summary_text = _load_text(output_dir / "investor_summary.md", issues, "investor_summary.md")
    report_text = _load_text(output_dir / "report.md", issues, "report.md")

    _require_file(output_dir / f"{case_name}_MAI_Standard_Report.md", issues)
    _require_file(output_dir / f"{case_name}_method_traceability.json", issues)
    _require_any_file(output_dir, ("session_input.json", "session_draft.json"), issues)

    if (output_dir / "evidence_pack.md").exists():
        _require_file(output_dir / "inventory.json", issues)
    if (output_dir / "sanitized_evidence_pack.md").exists():
        _require_file(output_dir / "redaction_report.json", issues)

    if result:
        _check_result(result, issues)
    if summary_text:
        _check_summary(summary_text, issues)
    if report_text:
        _check_report(report_text, issues)

    session = _load_session(output_dir)
    if session:
        _check_risk_governance(session, issues)

    _check_extraction_coverage(output_dir, issues)

    errors = [issue for issue in issues if issue.severity == "error"]
    warnings = [issue for issue in issues if issue.severity == "warning"]
    return {
        "case_name": case_name,
        "passed": not errors,
        "error_count": len(errors),
        "warning_count": len(warnings),
        "issues": [asdict(issue) for issue in issues],
    }


def write_quality_report(output_dir: Path, case_name: str) -> dict[str, Any]:
    report = build_quality_report(output_dir, case_name)
    (output_dir / "quality_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (output_dir / "quality_report.md").write_text(
        render_quality_report(report),
        encoding="utf-8",
    )
    return report


def render_quality_report(report: dict[str, Any]) -> str:
    status = "PASS" if report["passed"] else "FAIL"
    lines = [
        f"# MAI Quality Report - {report['case_name']}",
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
        lines.append("- No quality issues detected.")
    for issue in report["issues"]:
        lines.append(f"- {issue['severity'].upper()} `{issue['code']}`: {issue['message']}")
    lines.append("")
    return "\n".join(lines)


def _load_json(path: Path, issues: list[QualityIssue], label: str) -> dict[str, Any]:
    if not path.exists():
        issues.append(QualityIssue("error", "missing_file", f"Required file is missing: {label}"))
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        issues.append(QualityIssue("error", "invalid_json", f"{label} cannot be parsed: {exc}"))
        return {}
    if not isinstance(data, dict):
        issues.append(QualityIssue("error", "invalid_json_shape", f"{label} must contain a JSON object."))
        return {}
    return data


def _load_text(path: Path, issues: list[QualityIssue], label: str) -> str:
    if not path.exists():
        issues.append(QualityIssue("error", "missing_file", f"Required file is missing: {label}"))
        return ""
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        issues.append(QualityIssue("error", "unreadable_file", f"{label} cannot be read: {exc}"))
        return ""


def _load_session(output_dir: Path) -> dict[str, Any]:
    for name in ("session_input.json", "session_draft.json"):
        path = output_dir / name
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                return data if isinstance(data, dict) else {}
            except (OSError, ValueError):
                return {}
    return {}


def _require_file(path: Path, issues: list[QualityIssue]) -> None:
    if not path.exists():
        issues.append(QualityIssue("error", "missing_file", f"Required file is missing: {path.name}"))


def _require_any_file(output_dir: Path, names: tuple[str, ...], issues: list[QualityIssue]) -> None:
    if not any((output_dir / name).exists() for name in names):
        joined = ", ".join(names)
        issues.append(QualityIssue("error", "missing_session", f"One of these files is required: {joined}"))


def _check_result(result: dict[str, Any], issues: list[QualityIssue]) -> None:
    score = result.get("stability_score")
    if not isinstance(score, int) or not 0 <= score <= 100:
        issues.append(QualityIssue("error", "invalid_score", "stability_score must be an integer from 0 to 100."))

    outcome = str(result.get("decision_outcome", "")).strip().upper()
    if outcome not in ALLOWED_OUTCOMES:
        issues.append(QualityIssue("error", "invalid_outcome", "decision_outcome must be GO, CONDITIONAL GO, REDESIGN, or NO-GO."))

    breakpoint = str(result.get("critical_breakpoint", "")).strip()
    if not breakpoint or breakpoint.lower() in {"not provided.", "not provided", "none", "n/a"}:
        issues.append(QualityIssue("warning", "missing_breakpoint", "critical_breakpoint is missing or generic."))

    gates = result.get("decision_gates", [])
    if not isinstance(gates, list):
        issues.append(QualityIssue("error", "invalid_gates", "decision_gates must be a list."))
        return
    if not gates:
        issues.append(QualityIssue("warning", "no_decision_gates", "No decision gates were provided."))

    open_critical_gate = False
    for index, gate in enumerate(gates, start=1):
        if not isinstance(gate, dict):
            issues.append(QualityIssue("error", "invalid_gate", f"Decision gate {index} must be an object."))
            continue
        missing = [field for field in REQUIRED_GATE_FIELDS if not str(gate.get(field, "")).strip()]
        if missing:
            issues.append(
                QualityIssue(
                    "error",
                    "incomplete_gate",
                    f"Decision gate {index} is missing required fields: {', '.join(missing)}.",
                )
            )
        criticality = str(gate.get("criticality", "")).strip().lower()
        status = str(gate.get("status", "")).strip().lower()
        if criticality == "critical" and status in OPEN_GATE_STATUSES:
            open_critical_gate = True

    if outcome == "GO" and open_critical_gate:
        issues.append(QualityIssue("error", "go_with_open_critical_gate", "GO outcome is not allowed while critical gates remain open."))


def _check_summary(summary_text: str, issues: list[QualityIssue]) -> None:
    lowered = summary_text.lower()
    if "decision-readiness assessment" not in lowered:
        issues.append(QualityIssue("error", "missing_limitation", "Investor summary must state the MAI decision-readiness boundary."))
    if "required independent verification" not in lowered:
        issues.append(QualityIssue("warning", "missing_independent_verification", "Investor summary should include required independent verification."))
    if "methodological references" not in lowered:
        issues.append(QualityIssue("warning", "missing_method_references", "Investor summary should include the methodological references section."))
    if "not a statement of compliance" not in lowered:
        issues.append(QualityIssue("error", "overstated_standards_compliance", "Investor summary must state that the standards informed the MAI method but are not applied or certified per case."))


def _check_report(report_text: str, issues: list[QualityIssue]) -> None:
    lowered = report_text.lower()
    if "critical breakpoint" not in lowered:
        issues.append(QualityIssue("warning", "report_missing_breakpoint", "Full report should include a critical breakpoint section."))
    if "decision gate" not in lowered and "gates" not in lowered:
        issues.append(QualityIssue("warning", "report_missing_gates", "Full report should include decision gate information."))


def _check_risk_governance(session: dict[str, Any], issues: list[QualityIssue]) -> None:
    """Surface the per-case analysis modules' gap findings as warnings.

    Computed from the session (independent of file write order). Warnings, not
    errors: they inform human review without auto-failing the gate.
    """
    try:
        iso = build_iso31000(session)
        coso = build_coso_erm(session)
    except Exception:  # never let an analysis module break the QA gate
        return

    process_gaps = [r for r in iso.get("rows", []) if r.get("process_gap")]
    for r in process_gaps[:10]:
        issues.append(QualityIssue(
            "warning", "uncovered_high_risk",
            f"{r['risk_level']} risk has no decision gate (see iso31000.md): "
            f"{r['risk']} ({r['node']}).",
        ))

    gov_gaps = coso.get("governance_gap_count", 0)
    if gov_gaps:
        issues.append(QualityIssue(
            "warning", "unassigned_risk_owner",
            f"{gov_gaps} risk(s) require a response but have no accountable owner "
            f"(see coso_erm.md).",
        ))


def _check_extraction_coverage(output_dir: Path, issues: list[QualityIssue]) -> None:
    """Warn when the document reader dropped or truncated source content.

    Closes the remaining half of audit finding #3: a claim could rest on a file
    that was skipped (over the 40-file cap) or on text past the per-file char
    limit. These are warnings so a human knows the evidence pack is incomplete.
    """
    path = output_dir / "extraction_coverage.json"
    if not path.exists():
        return
    try:
        cov = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return
    skipped = cov.get("files_skipped_over_cap", []) or []
    truncated = cov.get("files_truncated", []) or []
    if skipped:
        issues.append(QualityIssue(
            "warning", "evidence_files_skipped",
            f"{len(skipped)} source file(s) exceeded the {cov.get('max_files')}-file cap and "
            f"were NOT read; claims may rest on content absent from the evidence pack.",
        ))
    if truncated:
        issues.append(QualityIssue(
            "warning", "evidence_files_truncated",
            f"{len(truncated)} source file(s) were truncated to "
            f"{cov.get('max_chars_per_file')} chars; later passages are not in the evidence pack.",
        ))
