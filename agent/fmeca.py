from __future__ import annotations

"""IEC 60812-style FMECA, computed per case (audit finding #1, "make it real").

The methodology table used to *claim* an IEC 60812 FMECA without performing one.
This module actually performs the procedure: for every failure mode in the
session it computes Severity (S), Occurrence (O) and Detection (D), then the Risk
Priority Number (RPN = S x O x D) and the FMECA criticality (S x O), and ranks
the modes. Output is written per case as `fmeca.json` / `fmeca.md`.

Inputs and honesty boundary
---------------------------
- S and O come from the session's `deviations` severity/likelihood. These are
  judgment-based ordinals; with the evidence rubric (docs/MAI_EVIDENCE_RUBRIC.md)
  each level is tied to a stated evidence condition, so they are defensible, but
  this is still a structured assessment, NOT a certified FMECA.
- D (detection) is what IEC 60812 needs and the session does not directly carry.
  It is resolved in this order, and the basis is recorded per row:
    1. explicit `deviation['detectability']` (high/medium/low), if provided;
    2. otherwise derived from whether a decision gate covers the failure's node
       (a control that could catch it before the critical breakpoint);
    3. otherwise a neutral default.
- This does not change the MAI stability score. The scoring engine remains the
  single source of truth for the score/outcome; FMECA is a separate analysis.
"""

import json
import re
from pathlib import Path
from typing import Any

FMECA_VERSION = "1.0.0"

# Ordinal -> 1..10 scales (documented in docs/MAI_EVIDENCE_RUBRIC.md).
SEVERITY_SCALE = {"critical": 10, "high": 8, "medium": 5, "low": 2}
OCCURRENCE_SCALE = {"high": 8, "medium": 5, "low": 2}
# Higher D = harder to detect before it bites = worse.
DETECTABILITY_SCALE = {"high": 2, "medium": 5, "low": 9}
# D derived from decision-gate coverage of the affected node.
COVERAGE_DETECTION = {"critical": 3, "standard": 5, "none": 9}

DEFAULT_S = 5
DEFAULT_O = 5
DEFAULT_D = 6

_OPEN_GATE_STATUSES = {"open", "pending", "missing", "unverified", "conditional", "incomplete", ""}
_STOPWORDS = {"the", "and", "of", "a", "to", "for", "in", "on", "or", "is", "are", "by"}


def _norm(value: Any) -> str:
    return str(value or "").strip().lower()


def _tokens(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9]+", _norm(text)) if len(t) > 2 and t not in _STOPWORDS}


def severity_value(deviation: dict[str, Any]) -> int:
    return SEVERITY_SCALE.get(_norm(deviation.get("severity")), DEFAULT_S)


def occurrence_value(deviation: dict[str, Any]) -> int:
    return OCCURRENCE_SCALE.get(_norm(deviation.get("likelihood")), DEFAULT_O)


def gate_coverage(node: str, gates: list[dict[str, Any]]) -> tuple[str, dict[str, Any] | None]:
    """Return ('critical'|'standard'|'none', covering_gate or None).

    A node is 'covered' when an open gate's name/required_evidence shares
    meaningful tokens with the affected node — i.e. a control exists that would
    surface this failure before the breakpoint.
    """
    node_tokens = _tokens(node)
    if not node_tokens:
        return "none", None
    best: tuple[str, dict[str, Any] | None] = ("none", None)
    for gate in gates:
        if _norm(gate.get("status")) not in _OPEN_GATE_STATUSES:
            continue
        gate_tokens = _tokens(gate.get("gate")) | _tokens(gate.get("required_evidence")) | _tokens(gate.get("gate_code"))
        if node_tokens & gate_tokens:
            if _norm(gate.get("criticality")) == "critical":
                return "critical", gate
            best = ("standard", gate)
    return best


def detection_value(deviation: dict[str, Any], gates: list[dict[str, Any]]) -> tuple[int, str, dict[str, Any] | None]:
    explicit = _norm(deviation.get("detectability") or deviation.get("detection"))
    if explicit in DETECTABILITY_SCALE:
        return DETECTABILITY_SCALE[explicit], f"explicit detectability: {explicit}", None

    node = deviation.get("affected_node") or deviation.get("node") or deviation.get("domain") or ""
    coverage, gate = gate_coverage(node, gates)
    if coverage == "critical":
        return COVERAGE_DETECTION["critical"], f"covered by critical gate: {gate.get('gate', '')}", gate
    if coverage == "standard":
        return COVERAGE_DETECTION["standard"], f"covered by gate: {gate.get('gate', '')}", gate
    return COVERAGE_DETECTION["none"], "no decision gate covers this node", None


def rpn_band(rpn: int) -> str:
    if rpn >= 200:
        return "high"
    if rpn >= 90:
        return "medium"
    return "low"


def criticality_band(crit: int) -> str:
    if crit >= 56:
        return "high"
    if crit >= 30:
        return "medium"
    return "low"


def fmeca_row(deviation: dict[str, Any], gates: list[dict[str, Any]]) -> dict[str, Any]:
    s = severity_value(deviation)
    o = occurrence_value(deviation)
    d, d_basis, gate = detection_value(deviation, gates)
    rpn = s * o * d
    crit = s * o
    if gate is not None:
        action = f"Close gate '{gate.get('gate', '')}': {gate.get('required_evidence', '')}".strip()
    else:
        action = "Define a decision gate to detect and close this before the critical breakpoint."
    return {
        "location": deviation.get("affected_node") or deviation.get("domain") or "Unknown",
        "failure_mode": deviation.get("deviation") or deviation.get("name") or "Deviation",
        "domain": deviation.get("domain", ""),
        "severity": s,
        "occurrence": o,
        "detection": d,
        "detection_basis": d_basis,
        "rpn": rpn,
        "rpn_band": rpn_band(rpn),
        "criticality": crit,
        "criticality_band": criticality_band(crit),
        "fixability": deviation.get("fixable", ""),
        "recommended_action": action,
    }


def _source_modes(session: dict[str, Any]) -> list[dict[str, Any]]:
    deviations = session.get("deviations")
    if isinstance(deviations, list) and deviations:
        return [d for d in deviations if isinstance(d, dict)]
    # Fallback: derive minimal modes from an explicit failure_map (no likelihood).
    rows: list[dict[str, Any]] = []
    for item in session.get("failure_map", []) or []:
        if isinstance(item, dict):
            rows.append({
                "affected_node": item.get("location"),
                "deviation": item.get("failure_type"),
                "severity": item.get("severity"),
                "fixable": item.get("fixable"),
            })
    return rows


def build_fmeca(session: dict[str, Any]) -> dict[str, Any]:
    gates = session.get("decision_gates", []) or []
    modes = _source_modes(session)
    rows = [fmeca_row(m, gates) for m in modes]
    rows.sort(key=lambda r: (r["rpn"], r["criticality"]), reverse=True)
    for i, r in enumerate(rows, start=1):
        r["priority"] = i

    band_counts = {"high": 0, "medium": 0, "low": 0}
    for r in rows:
        band_counts[r["rpn_band"]] += 1

    return {
        "fmeca_version": FMECA_VERSION,
        "standard": "IEC 60812:2018 (FMEA/FMECA) — structured procedure, not a certification.",
        "disclaimer": (
            "Severity and Occurrence are judgment-based ordinals tied to the evidence "
            "rubric; Detection is derived from decision-gate coverage unless explicitly "
            "provided. This is a structured FMECA computation, not a certified analysis, "
            "and it does not change the MAI stability score."
        ),
        "scales": {
            "severity": SEVERITY_SCALE,
            "occurrence": OCCURRENCE_SCALE,
            "detection_from_detectability": DETECTABILITY_SCALE,
            "detection_from_gate_coverage": COVERAGE_DETECTION,
        },
        "mode_count": len(rows),
        "rpn_band_counts": band_counts,
        "highest_rpn": rows[0]["rpn"] if rows else 0,
        "rows": rows,
    }


def render_fmeca_md(fmeca: dict[str, Any], case_name: str) -> str:
    lines = [
        f"# FMECA (IEC 60812-style) - {case_name}",
        "",
        fmeca["standard"],
        "",
        fmeca["disclaimer"],
        "",
        f"Failure modes: {fmeca['mode_count']} | RPN bands — "
        f"high: {fmeca['rpn_band_counts']['high']}, "
        f"medium: {fmeca['rpn_band_counts']['medium']}, "
        f"low: {fmeca['rpn_band_counts']['low']}",
        "",
        "| # | Location | Failure mode | S | O | D | RPN | Band | Crit | Detection basis |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in fmeca["rows"]:
        lines.append(
            f"| {r['priority']} | {r['location']} | {r['failure_mode']} | "
            f"{r['severity']} | {r['occurrence']} | {r['detection']} | {r['rpn']} | "
            f"{r['rpn_band']} | {r['criticality']} | {r['detection_basis']} |"
        )
    lines.extend(["", "## Recommended actions (by priority)", ""])
    for r in fmeca["rows"]:
        lines.append(f"- P{r['priority']} ({r['rpn_band']} RPN {r['rpn']}) {r['location']}: {r['recommended_action']}")
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


def write_fmeca_report(output_dir: Path, case_name: str) -> dict[str, Any]:
    session = _load_session(output_dir)
    fmeca = build_fmeca(session)
    (output_dir / "fmeca.json").write_text(
        json.dumps(fmeca, ensure_ascii=False, indent=2), encoding="utf-8",
    )
    (output_dir / "fmeca.md").write_text(
        render_fmeca_md(fmeca, case_name), encoding="utf-8",
    )
    return fmeca
