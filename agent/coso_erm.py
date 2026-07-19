from __future__ import annotations

"""COSO ERM-style governance & response table, computed per case ("make it real").

COSO ERM 2017 principles 10-13 cover: identifying risk, assessing severity,
prioritising risks, and implementing risk responses. The methodology table used to
*claim* "decision ownership, severity assessment, prioritization and response
gates" without producing them. This module builds the actual table:

  risk -> owner -> severity/level (P11) -> priority rank (P12) -> response (P13)

The real, per-case finding is a **governance gap**: a risk that requires a response
but has no accountable owner (a principle-13 failure). That is surfaced explicitly.

Reuses the risk matrix (iso31000.risk_level) and gate coverage (fmeca.gate_coverage)
so the three standards stay consistent. Deterministic; does not change the score.
"""

import json
from pathlib import Path
from typing import Any

from .fmeca import gate_coverage
from .iso31000 import risk_level, _source_risks, TREATMENT_REQUIRED_LEVELS

COSO_ERM_VERSION = "1.0.0"

COSO_PRINCIPLES = {
    "10": "Identifies risk (from deviations and stress scenarios).",
    "11": "Assesses severity (severity x likelihood risk level).",
    "12": "Prioritises risks (rank by level then score).",
    "13": "Implements responses (response type + accountable owner via decision gate).",
}

_LEVEL_ORDER = {"Extreme": 4, "High": 3, "Medium": 2, "Low": 1}


def response_type(level: str, covered: bool) -> str:
    """COSO response: Accept / Avoid / Reduce / Share / Pursue."""
    if covered:
        return "Reduce (existing gate control)"
    if level == "Extreme":
        return "Avoid/Reduce — do not proceed until owned and controlled"
    if level == "High":
        return "Reduce — assign owner and define control"
    if level == "Medium":
        return "Reduce / Monitor — assign owner"
    return "Accept (monitor)"


def governance_row(risk: dict[str, Any], gates: list[dict[str, Any]]) -> dict[str, Any]:
    score, level = risk_level(risk.get("severity"), risk.get("likelihood"))
    _coverage, gate = gate_coverage(risk.get("node", ""), gates)
    covered = gate is not None
    owner = gate.get("owner", "") if covered else ""
    control = gate.get("gate", "") if covered else ""
    status = gate.get("status", "") if covered else "no response assigned"
    treatment_required = level in TREATMENT_REQUIRED_LEVELS
    governance_gap = treatment_required and not owner
    return {
        "risk": risk.get("risk", ""),
        "node": risk.get("node", ""),
        "identification_source": risk.get("source", ""),   # principle 10
        "severity": risk.get("severity", ""),
        "risk_level": level,                                # principle 11
        "risk_score": score,
        "response": response_type(level, covered),          # principle 13
        "control": control,
        "owner": owner or "UNASSIGNED",
        "status": status,
        "governance_gap": governance_gap,
    }


def build_coso_erm(session: dict[str, Any]) -> dict[str, Any]:
    gates = session.get("decision_gates", []) or []
    rows = [governance_row(r, gates) for r in _source_risks(session)]
    rows.sort(key=lambda r: (_LEVEL_ORDER.get(r["risk_level"], 0), r["risk_score"]), reverse=True)
    for i, r in enumerate(rows, start=1):
        r["priority"] = i  # principle 12

    response_dist: dict[str, int] = {}
    for r in rows:
        response_dist[r["response"]] = response_dist.get(r["response"], 0) + 1
    gaps = [r for r in rows if r["governance_gap"]]

    return {
        "coso_erm_version": COSO_ERM_VERSION,
        "standard": "COSO ERM 2017 principles 10-13 — structured governance/response table, not a certification.",
        "disclaimer": (
            "Severity/level are judgment-based ordinals tied to the evidence rubric; "
            "owner and control come from the matching decision gate. This is a structured "
            "COSO ERM response table, not a certified assessment, and it does not change "
            "the MAI stability score."
        ),
        "principles": COSO_PRINCIPLES,
        "risk_count": len(rows),
        "governance_gap_count": len(gaps),
        "response_distribution": response_dist,
        "rows": rows,
    }


def render_coso_erm_md(coso: dict[str, Any], case_name: str) -> str:
    lines = [
        f"# COSO ERM Governance & Response - {case_name}",
        "",
        coso["standard"],
        "",
        coso["disclaimer"],
        "",
        f"Risks: {coso['risk_count']} | governance gaps (response required, no owner): "
        f"{coso['governance_gap_count']}",
        "",
        "Principles applied: "
        + "; ".join(f"P{k} — {v}" for k, v in coso["principles"].items()),
        "",
        "| # | Risk | Level | Response (P13) | Control | Owner | Gap |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in coso["rows"]:
        lines.append(
            f"| {r['priority']} | {r['risk']} | {r['risk_level']} | {r['response']} | "
            f"{r['control'] or '—'} | {r['owner']} | {'YES' if r['governance_gap'] else ''} |"
        )
    if coso["governance_gap_count"]:
        lines.extend(["", "## Governance gaps (risk needs a response but has no owner)", ""])
        for r in coso["rows"]:
            if r["governance_gap"]:
                lines.append(f"- {r['risk_level']}: {r['risk']} ({r['node']}) — no accountable owner assigned.")
    lines.append("")
    return "\n".join(lines)


def _load_session(output_dir: Path) -> dict[str, Any]:
    for name in ("session_input.json", "session_draft.json"):
        path = output_dir / name
        if path.exists():
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                return {}
    return {}


def write_coso_erm_report(output_dir: Path, case_name: str) -> dict[str, Any]:
    coso = build_coso_erm(_load_session(output_dir))
    (output_dir / "coso_erm.json").write_text(
        json.dumps(coso, ensure_ascii=False, indent=2), encoding="utf-8",
    )
    (output_dir / "coso_erm.md").write_text(
        render_coso_erm_md(coso, case_name), encoding="utf-8",
    )
    return coso
