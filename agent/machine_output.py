from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .methodology_references import normalize_stage_gate


_CLOSED_STATUSES = {"closed", "complete", "completed", "passed", "resolved", "done"}


def build_executive_outputs(session: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    outcome = str(result.get("decision_outcome", "UNKNOWN")).strip().upper()
    gates = result.get("decision_gates", [])
    critical_open_gates = _critical_open_gates(gates)
    stage_gate = normalize_stage_gate(session, outcome)
    next_gate = _first_gate_name(critical_open_gates) or stage_gate.get("next_gate") or "Further Review"

    decision_status = "Supported" if outcome == "GO" and not critical_open_gates else "Not Yet"
    critical_blockers = [
        _format_gate_blocker(gate) for gate in critical_open_gates
    ] or list(result.get("primary_failure_mechanisms", []))
    required_evidence = [
        gate.get("required_evidence")
        for gate in critical_open_gates
        if gate.get("required_evidence")
    ]
    if not required_evidence and result.get("critical_breakpoint"):
        required_evidence = [str(result["critical_breakpoint"])]

    return {
        "decision_status": decision_status,
        "highest_responsible_commitment": next_gate,
        "critical_blockers": critical_blockers,
        "required_evidence": required_evidence,
        "recommended_next_step": _recommended_next_step(decision_status, next_gate),
    }


def build_machine_result(
    output_dir: Path,
    case_name: str,
    result: dict[str, Any],
    quality_report: dict[str, Any] | None = None,
    traceability_report: dict[str, Any] | None = None,
) -> dict[str, Any]:
    session = _load_session(output_dir)
    outcome = str(result.get("decision_outcome", "UNKNOWN"))
    gates = result.get("decision_gates", [])
    critical_open_gates = _critical_open_gates(gates)
    stage_gate = normalize_stage_gate(session, outcome)

    return {
        "schema_version": "mai-machine-result-v1",
        "case_name": case_name,
        "status": "completed",
        "score": result.get("stability_score"),
        "outcome": outcome,
        "diagnosis": result.get("decision_architecture_diagnosis"),
        "executive_outputs": build_executive_outputs(session, result),
        "stage_gate": stage_gate,
        "critical_breakpoint": result.get("critical_breakpoint"),
        "critical_gates_open_count": len(critical_open_gates),
        "critical_gates_open": [
            {
                "gate": gate.get("gate"),
                "gate_code": gate.get("gate_code"),
                "owner": gate.get("owner"),
                "status": gate.get("status"),
                "required_evidence": gate.get("required_evidence"),
            }
            for gate in critical_open_gates
        ],
        "quality": {
            "passed": None if quality_report is None else quality_report.get("passed"),
            "traceable": None if traceability_report is None else traceability_report.get("traceable"),
        },
        "paths": {
            "output_dir": str(output_dir),
            "result_json": str(output_dir / "result.json"),
            "session_input_json": str(output_dir / "session_input.json"),
            "investor_summary_md": str(output_dir / "investor_summary.md"),
            "standard_report_md": str(output_dir / f"{case_name}_MAI_Standard_Report.md"),
            "method_traceability_json": str(output_dir / f"{case_name}_method_traceability.json"),
            "quality_report_md": str(output_dir / "quality_report.md"),
            "traceability_report_md": str(output_dir / "traceability_report.md"),
            "fmeca_md": str(output_dir / "fmeca.md"),
            "iso31000_md": str(output_dir / "iso31000.md"),
            "iec31010_md": str(output_dir / "iec31010.md"),
            "coso_erm_md": str(output_dir / "coso_erm.md"),
            "machine_result_json": str(output_dir / "machine_result.json"),
        },
    }


def write_machine_result(
    output_dir: Path,
    case_name: str,
    result: dict[str, Any],
    quality_report: dict[str, Any] | None = None,
    traceability_report: dict[str, Any] | None = None,
) -> dict[str, Any]:
    machine_result = build_machine_result(
        output_dir,
        case_name,
        result,
        quality_report=quality_report,
        traceability_report=traceability_report,
    )
    (output_dir / "machine_result.json").write_text(
        json.dumps(machine_result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return machine_result


def _critical_open_gates(gates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        gate
        for gate in gates
        if str(gate.get("criticality", "")).strip().lower() == "critical"
        and str(gate.get("status", "")).strip().lower() not in _CLOSED_STATUSES
    ]


def _first_gate_name(gates: list[dict[str, Any]]) -> str | None:
    for gate in gates:
        if gate.get("gate"):
            return str(gate["gate"])
    return None


def _format_gate_blocker(gate: dict[str, Any]) -> str:
    gate_name = gate.get("gate") or "Critical gate"
    status = gate.get("status") or "open"
    return f"{gate_name} remains {status}."


def _recommended_next_step(decision_status: str, next_gate: str) -> str:
    if decision_status == "Supported":
        return "Proceed, subject to human review and required external due diligence."
    return f"Proceed with {next_gate} before considering a higher commitment."


def _load_session(output_dir: Path) -> dict[str, Any]:
    session_path = output_dir / "session_input.json"
    if not session_path.exists():
        session_path = output_dir / "session_draft.json"
    if not session_path.exists():
        return {}
    try:
        return json.loads(session_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
