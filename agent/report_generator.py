from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .methodology_references import (
    METHOD_DISCLAIMER,
    METHOD_REFERENCES,
    normalize_stage_gate,
)


def write_investor_summary(output_dir: Path, case_name: str, result: dict[str, Any]) -> None:
    session = _load_session(output_dir)
    score = result.get("stability_score", "n/a")
    outcome = result.get("decision_outcome", "n/a")
    diagnosis = result.get("decision_architecture_diagnosis", "n/a")
    breakpoint = result.get("critical_breakpoint") or "Not provided."
    gates = result.get("decision_gates", [])
    stage_gate = normalize_stage_gate(session, str(outcome))

    lines = [
        f"# Investor Summary - {case_name}",
        "",
        f"MAI Stability Score: **{score}/100**",
        "",
        f"Decision Outcome: **{outcome}**",
        "",
        f"Decision Architecture Diagnosis: **{diagnosis}**",
        "",
        "## Current Stage-Gate Position",
        "",
        f"- Current stage: {stage_gate['current_stage']}",
        f"- Next gate: {stage_gate['next_gate']}",
        f"- Blocked milestone: {stage_gate['blocked_milestone']}",
        f"- Gate owner: {stage_gate['gate_owner']}",
        f"- Movement allowed: {stage_gate['movement_allowed']}",
        "",
        "## Methodological References",
        "",
        METHOD_DISCLAIMER,
        "",
        "| Standard / framework | Anchor | What it covers | How it informed the MAI method | Reference |",
        "|---|---|---|---|---|",
    ]
    for item in METHOD_REFERENCES:
        lines.append(
            "| "
            f"{item['reference']} | "
            f"{item.get('anchors', 'method-level reference')} | "
            f"{item['scope']} | "
            f"{item['influence']} | "
            f"{item['source']} |"
        )

    lines.extend(
        [
            "",
            "Method boundary: MAI is a decision-readiness assessment. It is not a certification under ISO, COSO, IEC, FMEA/FMECA or Stage-Gate, and it does not replace legal, technical, financial, tax, sanctions/KYC, environmental, HSE, FEED or regulatory due diligence.",
            "",
            "Computed per case for this assessment (structured procedures, not certifications): IEC 60812 FMECA (see `fmeca.md`), the ISO 31000 risk-process register (see `iso31000.md`), the IEC 31010 technique-application log (see `iec31010.md`), and the COSO ERM governance/response table (see `coso_erm.md`).",
            "",
            "## Interpretation",
            "",
            "This result should be read as a decision-readiness assessment, not as a valuation opinion or technical approval.",
            "",
            "MAI identifies whether the decision architecture is reliable enough for execution, funding or further due diligence.",
            "",
            "## Critical Breakpoint",
            "",
            breakpoint,
            "",
            "## Gates Before Investor Commitment",
            "",
        ]
    )
    if gates:
        for gate in gates:
            if str(gate.get("criticality", "")).lower() == "critical":
                lines.append(
                    f"- {gate.get('gate', 'Unnamed gate')}: {gate.get('required_evidence', 'Evidence not specified')} "
                    f"(status: {gate.get('status', 'unknown')})"
                )
    else:
        lines.append("- No gates provided.")

    lines.extend(
        [
            "",
            "## Recommended Investor Position",
            "",
            investor_position(outcome),
            "",
            "## Required Independent Verification",
            "",
            "- Legal due diligence and contract enforceability.",
            "- Technical due diligence, FEED/HAZOP/OEM guarantees where relevant.",
            "- Financial model audit, tax, sanctions/KYC and payment security.",
            "- Regulatory, permit, environmental, HSE and insurance checks.",
            "",
        ]
    )
    report_text = "\n".join(lines)
    (output_dir / "investor_summary.md").write_text(report_text, encoding="utf-8")
    (output_dir / f"{case_name}_MAI_Standard_Report.md").write_text(report_text, encoding="utf-8")
    (output_dir / f"{case_name}_method_traceability.json").write_text(
        json.dumps(
            {
                "case_name": case_name,
                "stage_gate": stage_gate,
                "method_boundary": "MAI is a decision-readiness assessment, not a certification or substitute for independent due diligence.",
                "standards_applied_per_case": False,
                "computed_analyses": [
                    "IEC 60812 FMECA (fmeca.md)",
                    "ISO 31000 register (iso31000.md)",
                    "IEC 31010 technique log (iec31010.md)",
                    "COSO ERM governance/response (coso_erm.md)",
                ],
                "method_disclaimer": METHOD_DISCLAIMER,
                "method_references": METHOD_REFERENCES,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def investor_position(outcome: str) -> str:
    outcome = str(outcome).strip().upper()
    if outcome == "GO":
        return "Proceed to investment review, provided all external technical, legal and financial due diligence remains satisfactory."
    if outcome == "CONDITIONAL GO":
        return "Maintain investor interest, but condition commitment on specific gate closures and evidence delivery."
    if outcome == "REDESIGN":
        return "Do not proceed to binding commitment in the current form. Redesign the decision architecture and clear critical gates first."
    if outcome == "NO-GO":
        return "Do not proceed unless the project thesis or execution structure is materially changed."
    return "Investor position cannot be determined from the current output."


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
