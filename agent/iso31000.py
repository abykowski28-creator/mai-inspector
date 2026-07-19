from __future__ import annotations

"""ISO 31000-style risk-process register, computed per case ("make it real").

Like the FMECA module, this performs the procedure instead of only citing the
standard. It walks every risk through the ISO 31000:2018 process and records the
result of each step:

  identification -> analysis (risk level) -> evaluation (against risk criteria)
                 -> treatment (mapped to a decision gate) -> monitoring (owner/status)

The register itself is the "recording & reporting" step. Risks whose level is
High/Extreme but which have no decision gate covering them are surfaced as
**process gaps** — a real, per-case finding, not boilerplate.

Honesty boundary: severity/likelihood are judgment-based ordinals tied to the
evidence rubric; treatment mapping is heuristic (gate tokens vs. risk node). This
is a structured ISO 31000 process, not a certification, and it does not change the
MAI stability score.
"""

import json
from pathlib import Path
from typing import Any

from .fmeca import gate_coverage

ISO31000_VERSION = "1.0.0"

SEVERITY_W = {"critical": 4, "high": 3, "medium": 2, "low": 1}
LIKELIHOOD_W = {"high": 3, "medium": 2, "low": 1}
DEFAULT_SEVERITY_W = 2
DEFAULT_LIKELIHOOD_W = 2

# Risk criteria (clause 6.4.4): how a level maps to an evaluation decision.
RISK_CRITERIA = {
    "Extreme": "Unacceptable — treat and close before proceeding to the blocked milestone.",
    "High": "Treat; do not cross the blocked milestone until the control is in place.",
    "Medium": "Treat as planned (reduce to as low as reasonably practicable).",
    "Low": "Monitor / accept with periodic review.",
}
TREATMENT_REQUIRED_LEVELS = {"Extreme", "High", "Medium"}


def _norm(value: Any) -> str:
    return str(value or "").strip().lower()


def risk_level(severity: str, likelihood: str) -> tuple[int, str]:
    s = SEVERITY_W.get(_norm(severity), DEFAULT_SEVERITY_W)
    l = LIKELIHOOD_W.get(_norm(likelihood), DEFAULT_LIKELIHOOD_W)
    score = s * l
    if score >= 9:
        level = "Extreme"
    elif score >= 6:
        level = "High"
    elif score >= 3:
        level = "Medium"
    else:
        level = "Low"
    return score, level


def _source_risks(session: dict[str, Any]) -> list[dict[str, Any]]:
    risks: list[dict[str, Any]] = []
    for d in session.get("deviations", []) or []:
        if isinstance(d, dict):
            risks.append({
                "risk": d.get("deviation") or d.get("name") or "Risk",
                "node": d.get("affected_node") or d.get("domain") or "",
                "domain": d.get("domain", ""),
                "severity": d.get("severity", ""),
                "likelihood": d.get("likelihood", ""),
                "source": "deviations",
            })
    for sc in session.get("stress_scenarios", []) or []:
        if isinstance(sc, dict):
            impact = _norm(sc.get("system_impact") or sc.get("impact"))
            sev = {"catastrophic": "critical", "severe": "high", "significant": "medium", "contained": "low"}.get(impact, "")
            comps = sc.get("affected_components")
            node = comps[0] if isinstance(comps, list) and comps else ""
            risks.append({
                "risk": sc.get("scenario") or "Stress scenario",
                "node": node,
                "domain": "stress scenario",
                "severity": sev,
                "likelihood": "",
                "source": "stress_scenarios",
            })
    return risks


def register_row(risk: dict[str, Any], gates: list[dict[str, Any]]) -> dict[str, Any]:
    score, level = risk_level(risk.get("severity"), risk.get("likelihood"))
    evaluation = RISK_CRITERIA[level]
    coverage, gate = gate_coverage(risk.get("node", ""), gates)

    if gate is not None:
        treatment = gate.get("required_evidence", "")
        control = gate.get("gate", "")
        owner = gate.get("owner", "")
        status = gate.get("status", "")
        gap = False
    else:
        treatment = "No decision gate addresses this risk."
        control = ""
        owner = ""
        status = "untreated"
        gap = level in TREATMENT_REQUIRED_LEVELS

    return {
        "risk": risk.get("risk", ""),
        "node": risk.get("node", ""),
        "domain": risk.get("domain", ""),
        "identification_source": risk.get("source", ""),
        "severity": risk.get("severity", ""),
        "likelihood": risk.get("likelihood", ""),
        "risk_score": score,
        "risk_level": level,
        "evaluation": evaluation,
        "treatment_required": level in TREATMENT_REQUIRED_LEVELS,
        "control": control,
        "treatment": treatment,
        "owner": owner,
        "status": status,
        "process_gap": gap,
    }


_LEVEL_ORDER = {"Extreme": 4, "High": 3, "Medium": 2, "Low": 1}


def build_iso31000(session: dict[str, Any]) -> dict[str, Any]:
    gates = session.get("decision_gates", []) or []
    rows = [register_row(r, gates) for r in _source_risks(session)]
    rows.sort(key=lambda r: (_LEVEL_ORDER.get(r["risk_level"], 0), r["risk_score"]), reverse=True)
    for i, r in enumerate(rows, start=1):
        r["priority"] = i

    level_counts = {"Extreme": 0, "High": 0, "Medium": 0, "Low": 0}
    for r in rows:
        level_counts[r["risk_level"]] += 1
    gaps = [r for r in rows if r["process_gap"]]
    no_owner = [r for r in rows if r["treatment_required"] and not r["owner"]]

    return {
        "iso31000_version": ISO31000_VERSION,
        "standard": "ISO 31000:2018 risk management process — structured procedure, not a certification.",
        "disclaimer": (
            "Severity and likelihood are judgment-based ordinals tied to the evidence "
            "rubric; treatment mapping is heuristic (gate tokens vs. risk node). This is "
            "a structured ISO 31000 process, not a certified assessment, and it does not "
            "change the MAI stability score."
        ),
        "risk_criteria": RISK_CRITERIA,
        "risk_count": len(rows),
        "risk_level_counts": level_counts,
        "process_gap_count": len(gaps),
        "unowned_treatment_count": len(no_owner),
        "rows": rows,
    }


def render_iso31000_md(reg: dict[str, Any], case_name: str) -> str:
    lines = [
        f"# ISO 31000 Risk Register - {case_name}",
        "",
        reg["standard"],
        "",
        reg["disclaimer"],
        "",
        f"Risks: {reg['risk_count']} | levels — "
        f"Extreme: {reg['risk_level_counts']['Extreme']}, "
        f"High: {reg['risk_level_counts']['High']}, "
        f"Medium: {reg['risk_level_counts']['Medium']}, "
        f"Low: {reg['risk_level_counts']['Low']} | "
        f"process gaps (High/Extreme untreated): {reg['process_gap_count']}",
        "",
        "| # | Risk | Node | Level | Evaluation (criteria) | Treatment (control) | Owner | Status | Gap |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for r in reg["rows"]:
        lines.append(
            f"| {r['priority']} | {r['risk']} | {r['node']} | {r['risk_level']} | "
            f"{r['evaluation']} | {r['control'] or r['treatment']} | {r['owner'] or '—'} | "
            f"{r['status']} | {'YES' if r['process_gap'] else ''} |"
        )
    if reg["process_gap_count"]:
        lines.extend(["", "## Process gaps (High/Extreme risks with no treatment)", ""])
        for r in reg["rows"]:
            if r["process_gap"]:
                lines.append(f"- {r['risk_level']}: {r['risk']} ({r['node']}) — no decision gate addresses this risk.")
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


def write_iso31000_report(output_dir: Path, case_name: str) -> dict[str, Any]:
    reg = build_iso31000(_load_session(output_dir))
    (output_dir / "iso31000.json").write_text(
        json.dumps(reg, ensure_ascii=False, indent=2), encoding="utf-8",
    )
    (output_dir / "iso31000.md").write_text(
        render_iso31000_md(reg, case_name), encoding="utf-8",
    )
    return reg
