"""
MAI Decision Lab v2.1 scoring and verdict engine.

This module implements the deterministic part of the MAI Prompt System v2.1:
- stability scoring
- ADI multiplier
- decision architecture diagnosis
- outcome selection
- failure map and gate summary extraction

It is intentionally model-agnostic. An LLM can generate the structured JSON,
then this engine calculates the repeatable decision reliability outputs.

Usage:
    python mai_decision_lab_v2_1.py input.json --out report.json
    python mai_decision_lab_v2_1.py input.json --markdown report.md
"""

from __future__ import annotations

# Vendored into the MAI Inspector public release for reproducibility and auditability.
# Source: internal MAI Decision Lab deterministic engine baseline.
ENGINE_VERSION = "2.1.0"

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


LEVEL_WEIGHT = {
    "none": 0,
    "low": 1,
    "medium": 2,
    "high": 3,
    "critical": 4,
}

IMPACT_WEIGHT = {
    "contained": 1,
    "significant": 2,
    "severe": 3,
    "catastrophic": 4,
}

CLAIM_STATUS_WEIGHT = {
    "confirmed": 0,
    "assumed": 2,
    "conditional": 3,
    "upside": 1,
    "unverified": 4,
}


def norm(value: Any) -> str:
    return str(value or "").strip().lower()


def clamp(value: float, low: int = 0, high: int = 100) -> int:
    return max(low, min(high, int(round(value))))


def severity_points(severity: str, critical_range=(8, 15), high_range=(5, 8)) -> int:
    level = LEVEL_WEIGHT.get(norm(severity), 0)
    if level >= 4:
        return max(critical_range)
    if level == 3:
        return max(high_range)
    if level == 2:
        return 3
    if level == 1:
        return 1
    return 0


def likelihood_factor(likelihood: str) -> float:
    level = LEVEL_WEIGHT.get(norm(likelihood), 2)
    if level >= 4:
        return 1.15
    if level == 3:
        return 1.0
    if level == 2:
        return 0.75
    if level == 1:
        return 0.5
    return 0.75


def visual_bar(score: int, width: int = 10) -> str:
    filled = round(score / 100 * width)
    return "\u2588" * filled + "\u2591" * (width - filled) + f" {score}/100"


@dataclass
class ScoringBreakdown:
    component_risk: float = 0
    domain_instability: float = 0
    stress_scenarios: float = 0
    unresolved_assumptions: float = 0
    semantic_ambiguity: float = 0
    claim_uncertainty: float = 0
    breakpoint_proximity: float = 0
    systemic_overload: float = 0
    raw_deduction: float = 0
    adi_multiplier: float = 1.0
    final_deduction: float = 0
    notes: list[str] = field(default_factory=list)


@dataclass
class MAIResult:
    stability_score: int
    visual_bar: str
    outcome: str
    diagnosis: str
    scoring_breakdown: ScoringBreakdown
    failure_map: list[dict[str, Any]]
    gate_summary: list[dict[str, Any]]
    critical_breakpoint: str
    primary_failure_mechanisms: list[str]
    validation_warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "stability_score": self.stability_score,
            "visual_bar": self.visual_bar,
            "decision_outcome": self.outcome,
            "decision_architecture_diagnosis": self.diagnosis,
            "scoring_breakdown": self.scoring_breakdown.__dict__,
            "failure_map": self.failure_map,
            "decision_gates": self.gate_summary,
            "critical_breakpoint": self.critical_breakpoint,
            "primary_failure_mechanisms": self.primary_failure_mechanisms,
            "validation_warnings": self.validation_warnings,
        }


def validate_session(session: dict[str, Any]) -> list[str]:
    warnings: list[str] = []

    required_paths = [
        ("decision_brief.decision", session.get("decision_brief", {}).get("decision")),
        ("system_map.components", session.get("system_map", {}).get("components")),
        ("system_map.critical_assumptions", session.get("system_map", {}).get("critical_assumptions")),
        ("domain_analysis", session.get("domain_analysis")),
        ("semantic_risks", session.get("semantic_risks")),
        ("claim_register", session.get("claim_register")),
        ("stress_scenarios", session.get("stress_scenarios")),
        ("deviations", session.get("deviations")),
        ("critical_breakpoint", session.get("critical_breakpoint")),
        ("failure_mechanisms", session.get("failure_mechanisms")),
        ("decision_gates", session.get("decision_gates")),
    ]

    for name, value in required_paths:
        if value is None or value == "" or value == [] or value == {}:
            warnings.append(f"Missing or empty field: {name}")

    for idx, assumption in enumerate(session.get("system_map", {}).get("critical_assumptions", []), start=1):
        if isinstance(assumption, str):
            warnings.append(
                "Structured assumption expected at "
                f"system_map.critical_assumptions[{idx}]; got string. "
                "Use {text, status, criticality}."
            )
        elif isinstance(assumption, dict):
            if not (assumption.get("assumption") or assumption.get("text")):
                warnings.append(
                    f"Missing field system_map.critical_assumptions[{idx}].text"
                )
            for field_name in ("status", "criticality"):
                if not assumption.get(field_name):
                    warnings.append(
                        f"Missing field system_map.critical_assumptions[{idx}].{field_name}"
                    )

    for idx, gate in enumerate(session.get("decision_gates", []), start=1):
        for field_name in ("gate", "required_evidence", "owner", "status", "criticality"):
            if not gate.get(field_name):
                warnings.append(f"Missing field decision_gates[{idx}].{field_name}")

    for idx, deviation in enumerate(session.get("deviations", []), start=1):
        for field_name in ("deviation", "severity", "likelihood", "domain", "affected_node"):
            if not deviation.get(field_name):
                warnings.append(f"Missing field deviations[{idx}].{field_name}")

    return warnings


def score_components(session: dict[str, Any], breakdown: ScoringBreakdown) -> None:
    components = session.get("system_map", {}).get("components", [])
    for component in components:
        criticality = norm(component.get("criticality"))
        status = norm(component.get("status"))
        risk = norm(component.get("risk_level") or component.get("risk"))

        points = 0
        if criticality == "critical" and status in {"unconfirmed", "pending", "unknown", "in negotiation"}:
            points += 8
        elif criticality == "important" and status in {"unconfirmed", "pending", "unknown", "in negotiation"}:
            points += 4

        points += severity_points(risk, critical_range=(8, 12), high_range=(5, 7))
        breakdown.component_risk += points


def score_domains(session: dict[str, Any], breakdown: ScoringBreakdown) -> None:
    for domain in session.get("domain_analysis", []):
        level = norm(domain.get("instability_level"))
        if level == "critical":
            breakdown.domain_instability += 10
        elif level == "high":
            breakdown.domain_instability += 5
        elif level == "medium":
            breakdown.domain_instability += 2


def score_stress_scenarios(session: dict[str, Any], breakdown: ScoringBreakdown) -> None:
    for scenario in session.get("stress_scenarios", []):
        impact = norm(scenario.get("system_impact") or scenario.get("impact"))
        if impact == "catastrophic":
            breakdown.stress_scenarios += 10
        elif impact == "severe":
            breakdown.stress_scenarios += 6
        elif impact == "significant":
            breakdown.stress_scenarios += 3
        elif impact == "contained":
            breakdown.stress_scenarios += 1


def score_assumptions(session: dict[str, Any], breakdown: ScoringBreakdown) -> None:
    assumptions = session.get("system_map", {}).get("critical_assumptions", [])
    for assumption in assumptions:
        if isinstance(assumption, str):
            status = "unverified"
            criticality = "high"
        else:
            status = norm(assumption.get("status") or "unverified")
            criticality = norm(assumption.get("criticality") or "high")

        if status in {"unverified", "unconfirmed", "pending"}:
            breakdown.unresolved_assumptions += 8 if criticality == "critical" else 5
        elif status == "conditional":
            breakdown.unresolved_assumptions += 4


def score_semantic_risks(session: dict[str, Any], breakdown: ScoringBreakdown) -> None:
    for risk in session.get("semantic_risks", []):
        severity = norm(risk.get("severity"))
        if severity == "critical":
            breakdown.semantic_ambiguity += 7
        elif severity == "high":
            breakdown.semantic_ambiguity += 5
        elif severity == "medium":
            breakdown.semantic_ambiguity += 3
        elif severity == "low":
            breakdown.semantic_ambiguity += 1


def score_claims(session: dict[str, Any], breakdown: ScoringBreakdown) -> None:
    for claim in session.get("claim_register", []):
        status = norm(claim.get("status"))
        importance = norm(claim.get("importance") or "medium")
        base = CLAIM_STATUS_WEIGHT.get(status, 0)
        if importance == "critical":
            base *= 1.5
        elif importance == "high":
            base *= 1.25
        breakdown.claim_uncertainty += base


def score_breakpoint(session: dict[str, Any], breakdown: ScoringBreakdown) -> None:
    proximity = norm(session.get("critical_breakpoint_proximity") or "medium")
    if proximity == "immediate":
        breakdown.breakpoint_proximity = 20
    elif proximity == "near":
        breakdown.breakpoint_proximity = 15
    elif proximity == "medium":
        breakdown.breakpoint_proximity = 10
    elif proximity == "far":
        breakdown.breakpoint_proximity = 5


def compute_adi_multiplier(session: dict[str, Any], breakdown: ScoringBreakdown) -> float:
    deviations = session.get("deviations", [])
    node_counts: dict[str, int] = {}
    window_counts: dict[str, int] = {}

    for deviation in deviations:
        node = norm(deviation.get("affected_node") or deviation.get("node"))
        window = norm(deviation.get("execution_window") or deviation.get("window"))
        if node:
            node_counts[node] = node_counts.get(node, 0) + 1
        if window:
            window_counts[window] = window_counts.get(window, 0) + 1

    same_node_overload = any(count >= 3 for count in node_counts.values())
    timing_collision = any(count >= 5 for count in window_counts.values())

    if same_node_overload and timing_collision:
        breakdown.notes.append("ADI multiplier 1.30 applied: same-node overload and timing collision detected.")
        return 1.30
    if timing_collision:
        breakdown.notes.append("ADI multiplier 1.25 applied: 5+ deviations collide in the same execution window.")
        return 1.25
    if same_node_overload:
        breakdown.notes.append("ADI multiplier 1.15 applied: 3+ deviations accumulate on the same node.")
        return 1.15
    return 1.0


def apply_category_caps(breakdown: ScoringBreakdown) -> None:
    """Prevent duplicate counting while preserving catastrophic failure reach.

    MAI looks at the same decision through multiple lenses. Category caps keep a
    single unresolved node from being counted repeatedly. If the uncapped signal is
    extreme across several layers, a bounded systemic-overload deduction preserves
    the ability to reach the documented NO-GO outcome.
    """

    caps = {
        "component_risk": 8,
        "domain_instability": 6,
        "stress_scenarios": 6,
        "unresolved_assumptions": 5,
        "semantic_ambiguity": 4,
        "claim_uncertainty": 3,
        "breakpoint_proximity": 7,
    }
    overload_total = 0.0
    severe_overload_layers = 0
    for field_name, cap in caps.items():
        original = getattr(breakdown, field_name)
        if original > cap:
            overload_total += original - cap
            if original >= cap * 4:
                severe_overload_layers += 1
            setattr(breakdown, field_name, cap)
            breakdown.notes.append(
                f"{field_name} capped at {cap} to avoid duplicate risk counting "
                f"(uncapped: {original})."
            )

    if overload_total >= 120 or severe_overload_layers >= 3:
        breakdown.systemic_overload = 18
        breakdown.notes.append(
            "systemic_overload deduction 18 applied: uncapped risk signals "
            "exceed category caps across multiple assessment layers."
        )


def choose_outcome(score: int, gates: list[dict[str, Any]]) -> str:
    critical_open_gates = [
        gate
        for gate in gates
        if norm(gate.get("criticality")) == "critical"
        and norm(gate.get("status")) not in {"closed", "complete", "resolved", "cleared"}
    ]

    if score >= 80 and not critical_open_gates:
        return "GO"
    if score >= 60:
        return "CONDITIONAL GO"
    if score >= 40:
        return "REDESIGN"
    return "NO-GO"


def count_open_critical_gates(gates: list[dict[str, Any]]) -> int:
    return sum(
        1
        for gate in gates
        if norm(gate.get("criticality")) == "critical"
        and norm(gate.get("status")) not in {"closed", "complete", "resolved", "cleared"}
    )


def choose_diagnosis(session: dict[str, Any], gates: list[dict[str, Any]]) -> str:
    thesis_strength = norm(session.get("thesis_strength") or "strong")
    open_critical_gates = count_open_critical_gates(gates)
    architecture = "stable" if open_critical_gates == 0 else "weak"

    if thesis_strength == "strong" and architecture == "stable":
        return "Strong thesis / stable decision architecture"
    if thesis_strength == "strong":
        return "Strong thesis / weak decision architecture"
    if thesis_strength == "moderate" and architecture == "stable":
        return "Moderate thesis / stable decision architecture"
    if thesis_strength == "moderate":
        return "Moderate thesis / weak decision architecture"
    if thesis_strength == "weak" and architecture == "stable":
        return "Weak thesis / stable execution architecture"
    if thesis_strength == "weak":
        return "Weak thesis / weak decision architecture"
    if thesis_strength == "unclear":
        return "Unclear thesis / overconfident execution architecture"
    return "Unclear thesis / overconfident execution architecture"


def build_failure_map(session: dict[str, Any]) -> list[dict[str, Any]]:
    explicit = session.get("failure_map")
    if explicit:
        return explicit

    deviations = sorted(
        session.get("deviations", []),
        key=lambda d: (
            LEVEL_WEIGHT.get(norm(d.get("severity")), 0),
            LEVEL_WEIGHT.get(norm(d.get("likelihood")), 0),
        ),
        reverse=True,
    )
    failure_map = []
    for idx, deviation in enumerate(deviations[:10], start=1):
        failure_map.append(
            {
                "priority": idx,
                "location": deviation.get("affected_node") or deviation.get("domain") or "Unknown",
                "failure_type": deviation.get("deviation") or deviation.get("name") or "Deviation",
                "severity": deviation.get("severity", "Unknown"),
                "fixable": deviation.get("fixable", "Partial"),
            }
        )
    return failure_map


def analyze_session(session: dict[str, Any]) -> MAIResult:
    validation_warnings = validate_session(session)
    breakdown = ScoringBreakdown()
    score_components(session, breakdown)
    score_domains(session, breakdown)
    score_stress_scenarios(session, breakdown)
    score_assumptions(session, breakdown)
    score_semantic_risks(session, breakdown)
    score_claims(session, breakdown)
    score_breakpoint(session, breakdown)
    apply_category_caps(breakdown)

    breakdown.raw_deduction = (
        breakdown.component_risk
        + breakdown.domain_instability
        + breakdown.stress_scenarios
        + breakdown.unresolved_assumptions
        + breakdown.semantic_ambiguity
        + breakdown.claim_uncertainty
        + breakdown.breakpoint_proximity
        + breakdown.systemic_overload
    )
    breakdown.adi_multiplier = compute_adi_multiplier(session, breakdown)
    breakdown.final_deduction = breakdown.raw_deduction * breakdown.adi_multiplier

    score = clamp(100 - breakdown.final_deduction)
    gates = session.get("decision_gates", [])
    outcome = choose_outcome(score, gates)
    diagnosis = choose_diagnosis(session, gates)

    return MAIResult(
        stability_score=score,
        visual_bar=visual_bar(score),
        outcome=outcome,
        diagnosis=diagnosis,
        scoring_breakdown=breakdown,
        failure_map=build_failure_map(session),
        gate_summary=gates,
        critical_breakpoint=session.get("critical_breakpoint", ""),
        primary_failure_mechanisms=session.get("failure_mechanisms", []),
        validation_warnings=validation_warnings,
    )


def render_markdown(session: dict[str, Any], result: MAIResult) -> str:
    decision = session.get("decision_brief", {}).get("decision", "Decision not provided")
    lines = [
        "# MAI Decision Lab v2.1 - Final Report",
        "",
        f"Decision: {decision}",
        "",
        f"MAI Stability Score: **{result.stability_score}/100**",
        "",
        f"`{result.visual_bar}`",
        "",
        f"Decision Architecture Diagnosis: **{result.diagnosis}**",
        "",
        f"Decision Outcome: **{result.outcome}**",
        "",
    ]
    if result.validation_warnings:
        lines.extend(["## Data Completeness Warnings", ""] )
        for warning in result.validation_warnings:
            lines.append(f"- {warning}")
        lines.append("")
    lines.extend([
        "## Critical Breakpoint",
        "",
        result.critical_breakpoint or "Not provided.",
        "",
        "## Primary Failure Mechanisms",
        "",
    ])
    for mechanism in result.primary_failure_mechanisms:
        lines.append(f"- {mechanism}")

    lines.extend(["", "## Failure Map", ""])
    if result.failure_map:
        lines.extend([
            "| Priority | Location | Failure Type | Severity | Fixable? |",
            "|---|---|---|---|---|",
        ])
        for item in result.failure_map:
            lines.append(
                f"| P{item.get('priority')} | {item.get('location', '')} | "
                f"{item.get('failure_type', '')} | {item.get('severity', '')} | "
                f"{item.get('fixable', '')} |"
            )
    else:
        lines.append("No failure map provided.")

    lines.extend(["", "## Decision Gates", ""])
    if result.gate_summary:
        lines.extend([
            "| Gate | Required Evidence | Owner | Status | Criticality |",
            "|---|---|---|---|---|",
        ])
        for gate in result.gate_summary:
            lines.append(
                f"| {gate.get('gate', '')} | {gate.get('required_evidence', '')} | "
                f"{gate.get('owner', '')} | {gate.get('status', 'unknown')} | "
                f"{gate.get('criticality', '')} |"
            )
    else:
        lines.append("No decision gates provided.")

    lines.extend(["", "## Scoring Breakdown", ""])
    lines.extend(["| Field | Value |", "|---|---|"])
    for key, value in result.scoring_breakdown.__dict__.items():
        if key != "notes":
            lines.append(f"| {key} | {value} |")

    if result.scoring_breakdown.notes:
        lines.extend(["", "## Scoring Notes", ""])
        for note in result.scoring_breakdown.notes:
            lines.append(f"- {note}")

    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="MAI Decision Lab v2.1 scoring engine")
    parser.add_argument("input", type=Path, help="Input session JSON file")
    parser.add_argument("--out", type=Path, help="Write full result JSON")
    parser.add_argument("--markdown", type=Path, help="Write human-readable Markdown report")
    parser.add_argument("--validate-only", action="store_true", help="Validate input JSON and exit without scoring")
    args = parser.parse_args()

    session = json.loads(args.input.read_text(encoding="utf-8"))
    validation_warnings = validate_session(session)
    if args.validate_only:
        for warning in validation_warnings:
            print(warning, file=sys.stderr)
        raise SystemExit(1 if validation_warnings else 0)

    result = analyze_session(session)
    for warning in result.validation_warnings:
        print(warning, file=sys.stderr)

    if args.out:
        args.out.write_text(
            json.dumps(result.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    if args.markdown:
        args.markdown.write_text(render_markdown(session, result), encoding="utf-8")
    if not args.out and not args.markdown:
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
