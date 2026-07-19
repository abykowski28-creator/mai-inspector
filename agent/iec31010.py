from __future__ import annotations

"""IEC 31010-style technique-application log, computed per case ("make it real").

IEC 31010:2019 is a catalogue of risk-assessment techniques and guidance on
selecting/applying them. The methodology table used to *claim* "scenario analysis,
checklist logic, FMEA-style mapping" without recording what was actually done.

This module produces an honest application log: for each technique it records
whether it was APPLIED to this case, to WHICH session data, and WHAT it produced
— and, just as importantly, which techniques are NOT APPLICABLE and why (e.g. the
schema carries no explicit cause fields, so root-cause analysis is not performed).
That honesty is the point: it shows the boundary instead of rubber-stamping every
technique.

Deterministic; does not change the MAI stability score.
"""

import json
from pathlib import Path
from typing import Any

IEC31010_VERSION = "1.0.0"

APPLIED = "applied"
PARTIAL = "partial"
NOT_APPLICABLE = "not_applicable"


def _norm(value: Any) -> str:
    return str(value or "").strip().lower()


def _list(session: dict[str, Any], key: str) -> list[Any]:
    v = session.get(key)
    return v if isinstance(v, list) else []


def _impact_distribution(scenarios: list[dict[str, Any]]) -> dict[str, int]:
    dist: dict[str, int] = {}
    for sc in scenarios:
        if isinstance(sc, dict):
            imp = _norm(sc.get("system_impact") or sc.get("impact")) or "unspecified"
            dist[imp] = dist.get(imp, 0) + 1
    return dist


def build_iec31010(session: dict[str, Any]) -> dict[str, Any]:
    scenarios = _list(session, "stress_scenarios")
    gates = _list(session, "decision_gates")
    deviations = _list(session, "deviations")
    failure_map = _list(session, "failure_map")
    claims = _list(session, "claim_register")
    semantic = _list(session, "semantic_risks")
    domains = _list(session, "domain_analysis")

    modes = deviations or failure_map
    rated = [d for d in deviations if isinstance(d, dict) and d.get("severity") and d.get("likelihood")]
    open_critical = sum(
        1 for g in gates if isinstance(g, dict)
        and _norm(g.get("criticality")) == "critical"
        and _norm(g.get("status")) not in {"closed", "complete", "resolved", "cleared"}
    )
    with_propagation = [s for s in scenarios if isinstance(s, dict) and s.get("propagation_path")]

    rows: list[dict[str, Any]] = []

    def add(technique: str, reference: str, status: str, applied_to: str, output: str, note: str = "") -> None:
        rows.append({
            "technique": technique,
            "iec_reference": reference,
            "status": status,
            "applied_to": applied_to,
            "output": output,
            "note": note,
        })

    # 1. Scenario analysis
    if scenarios:
        add("Scenario analysis", "IEC 31010 B.5", APPLIED, "stress_scenarios",
            f"{len(scenarios)} scenarios analysed; impact distribution {_impact_distribution(scenarios)}.")
    else:
        add("Scenario analysis", "IEC 31010 B.5", NOT_APPLICABLE, "stress_scenarios",
            "No stress scenarios in the session.")

    # 2. FMEA / FMECA
    if modes:
        add("Failure mode and effects analysis (FMEA/FMECA)", "IEC 31010 B.19 / IEC 60812",
            APPLIED, "deviations", f"{len(modes)} failure modes scored (S/O/D, RPN). See fmeca.md.")
    else:
        add("Failure mode and effects analysis (FMEA/FMECA)", "IEC 31010 B.19 / IEC 60812",
            NOT_APPLICABLE, "deviations", "No deviations or failure_map to analyse.")

    # 3. Checklists
    if gates:
        add("Checklist analysis", "IEC 31010 B.1", APPLIED, "decision_gates",
            f"{len(gates)} decision gates used as a required-evidence checklist; {open_critical} critical gates open.")
    else:
        add("Checklist analysis", "IEC 31010 B.1", NOT_APPLICABLE, "decision_gates",
            "No decision gates defined.")

    # 4. Consequence/likelihood (risk) matrix
    if rated:
        add("Consequence/likelihood matrix", "IEC 31010 B.29", APPLIED, "deviations.severity x likelihood",
            f"{len(rated)} risks rated on a severity x likelihood matrix. See iso31000.md.")
    else:
        add("Consequence/likelihood matrix", "IEC 31010 B.29", NOT_APPLICABLE, "deviations",
            "No deviation carries both severity and likelihood.")

    # 5. Cause-consequence / propagation analysis
    if with_propagation:
        add("Cause-consequence / propagation analysis", "IEC 31010 B.17", APPLIED, "stress_scenarios.propagation_path",
            f"{len(with_propagation)} propagation paths traced from trigger to system impact.")
    else:
        add("Cause-consequence / propagation analysis", "IEC 31010 B.17", NOT_APPLICABLE,
            "stress_scenarios.propagation_path", "No propagation paths recorded.")

    # 6. Structured assumption/semantic analysis (MAI extension; not a named IEC technique)
    if semantic or claims:
        add("Structured assumption / semantic analysis (MAI extension)", "IEC 31010 (selection principles)",
            APPLIED, "semantic_risks + claim_register",
            f"{len(semantic)} semantic risks and {len(claims)} claims examined for interpretation/uncertainty risk.")
    else:
        add("Structured assumption / semantic analysis (MAI extension)", "IEC 31010 (selection principles)",
            NOT_APPLICABLE, "semantic_risks + claim_register", "No semantic risks or claims recorded.")

    # 7. Root cause analysis — honest NOT APPLICABLE (schema gap)
    has_causes = any(isinstance(d, dict) and (d.get("cause") or d.get("root_cause")) for d in deviations)
    if has_causes:
        add("Root cause analysis", "IEC 31010 B.12", APPLIED, "deviations.cause",
            "Explicit causes present and used.")
    else:
        add("Root cause analysis", "IEC 31010 B.12", NOT_APPLICABLE, "deviations.cause",
            "Schema carries no explicit cause/root_cause fields; RCA not performed (candidate schema extension).")

    # 8. Out-of-scope techniques — declared, not faked
    for tech, ref in (
        ("Bow-tie analysis", "IEC 31010 B.20"),
        ("HAZOP", "IEC 31010 B.18"),
        ("Fault tree analysis", "IEC 31010 B.23"),
    ):
        add(tech, ref, NOT_APPLICABLE, "—", "Out of MAI scope for decision-readiness assessment.")

    applied = [r for r in rows if r["status"] == APPLIED]
    not_applicable = [r for r in rows if r["status"] == NOT_APPLICABLE]

    return {
        "iec31010_version": IEC31010_VERSION,
        "standard": "IEC 31010:2019 technique selection/application — structured log, not a certification.",
        "disclaimer": (
            "This log records which IEC 31010 techniques the MAI method actually applied "
            "to this case and what each produced, plus techniques that are not applicable "
            "and why. It is deterministic and does not change the MAI stability score."
        ),
        "technique_count": len(rows),
        "applied_count": len(applied),
        "not_applicable_count": len(not_applicable),
        "rows": rows,
    }


def render_iec31010_md(log: dict[str, Any], case_name: str) -> str:
    lines = [
        f"# IEC 31010 Technique Application Log - {case_name}",
        "",
        log["standard"],
        "",
        log["disclaimer"],
        "",
        f"Techniques: {log['technique_count']} | applied: {log['applied_count']} | "
        f"not applicable: {log['not_applicable_count']}",
        "",
        "| Technique | IEC ref | Status | Applied to | Output / reason |",
        "|---|---|---|---|---|",
    ]
    for r in log["rows"]:
        detail = r["output"] if r["status"] == APPLIED else r["note"]
        lines.append(
            f"| {r['technique']} | {r['iec_reference']} | {r['status']} | {r['applied_to']} | {detail} |"
        )
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


def write_iec31010_report(output_dir: Path, case_name: str) -> dict[str, Any]:
    log = build_iec31010(_load_session(output_dir))
    (output_dir / "iec31010.json").write_text(
        json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8",
    )
    (output_dir / "iec31010.md").write_text(
        render_iec31010_md(log, case_name), encoding="utf-8",
    )
    return log
