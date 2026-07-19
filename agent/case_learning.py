from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class CaseCard:
    case_name: str
    session_id: str
    session_date: str
    decision_type: str
    scoring_profile: str
    thesis_strength: str
    decision: str
    stability_score: int | str
    decision_outcome: str
    diagnosis: str
    critical_breakpoint: str
    primary_failure_mechanisms: list[str]
    top_failures: list[dict[str, Any]]
    critical_open_gates: list[dict[str, Any]]
    recurring_domains: list[str]
    learning_signals: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# Smoke/sample runs share this hand-authored sample id; they are synthetic demo data, not
# real evidence, and must not pollute the learning library (audit finding #4).
KNOWN_FIXTURE_SESSION_IDS = {"mai-sample-2026-001"}


def is_fixture_session(session: dict[str, Any]) -> bool:
    if session.get("fixture") is True:
        return True
    return str(session.get("session_id", "")) in KNOWN_FIXTURE_SESSION_IDS


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_learning_library(outputs_dir: Path, out_dir: Path) -> dict[str, Any]:
    outputs_dir = outputs_dir.resolve()
    out_dir = out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    cards = collect_case_cards(outputs_dir)
    library = build_library(cards, outputs_dir)

    (out_dir / "mai_case_library.json").write_text(
        json.dumps(library, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (out_dir / "mai_learning_notes.md").write_text(
        render_learning_notes(library),
        encoding="utf-8",
    )
    return library


def collect_case_cards(outputs_dir: Path) -> list[CaseCard]:
    cards: list[CaseCard] = []
    seen_fingerprints: set[str] = set()
    if not outputs_dir.exists():
        return cards

    for case_dir in sorted(path for path in outputs_dir.iterdir() if path.is_dir()):
        session_path = case_dir / "session_input.json"
        result_path = case_dir / "result.json"
        if not session_path.exists() or not result_path.exists():
            continue

        try:
            session = load_json(session_path)
            result = load_json(result_path)
        except (OSError, json.JSONDecodeError):
            continue

        if is_fixture_session(session):
            continue

        card = case_to_card(case_dir.name, session, result)
        fingerprint = case_fingerprint(card)
        if fingerprint in seen_fingerprints:
            continue
        seen_fingerprints.add(fingerprint)
        cards.append(card)
    return cards


def case_fingerprint(card: CaseCard) -> str:
    return "|".join(
        [
            card.decision.strip().lower(),
            card.critical_breakpoint.strip().lower(),
            card.decision_outcome.strip().lower(),
        ]
    )


def case_to_card(case_name: str, session: dict[str, Any], result: dict[str, Any]) -> CaseCard:
    gates = result.get("decision_gates", [])
    critical_open_gates = [
        compact_gate(gate)
        for gate in gates
        if str(gate.get("criticality", "")).lower() == "critical"
        and str(gate.get("status", "")).lower() not in {"closed", "complete", "resolved", "cleared"}
    ]

    deviations = session.get("deviations", [])
    recurring_domains = sorted(
        {
            str(deviation.get("domain", "")).strip()
            for deviation in deviations
            if str(deviation.get("domain", "")).strip()
        }
    )

    return CaseCard(
        case_name=case_name,
        session_id=str(session.get("session_id", "")),
        session_date=str(session.get("session_date", "")),
        decision_type=str(session.get("decision_type", "")),
        scoring_profile=str(session.get("scoring_profile", "")),
        thesis_strength=str(session.get("thesis_strength", "")),
        decision=str(session.get("decision_brief", {}).get("decision", "")),
        stability_score=result.get("stability_score", "n/a"),
        decision_outcome=str(result.get("decision_outcome", "")),
        diagnosis=str(result.get("decision_architecture_diagnosis", "")),
        critical_breakpoint=str(result.get("critical_breakpoint", "")),
        primary_failure_mechanisms=[
            str(item) for item in result.get("primary_failure_mechanisms", []) if str(item).strip()
        ],
        top_failures=[compact_failure(item) for item in result.get("failure_map", [])[:5]],
        critical_open_gates=critical_open_gates[:10],
        recurring_domains=recurring_domains,
        learning_signals=derive_learning_signals(session, result),
    )


def compact_gate(gate: dict[str, Any]) -> dict[str, Any]:
    return {
        "gate": gate.get("gate", ""),
        "gate_code": gate.get("gate_code", ""),
        "required_evidence": gate.get("required_evidence", ""),
        "owner": gate.get("owner", ""),
        "status": gate.get("status", ""),
        "criticality": gate.get("criticality", ""),
    }


def compact_failure(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "priority": item.get("priority", ""),
        "location": item.get("location", ""),
        "failure_type": item.get("failure_type", ""),
        "severity": item.get("severity", ""),
        "fixable": item.get("fixable", ""),
    }


def derive_learning_signals(session: dict[str, Any], result: dict[str, Any]) -> list[str]:
    signals: list[str] = []
    text = json.dumps({"session": session, "result": result}, ensure_ascii=False).lower()
    decision_type = str(session.get("decision_type", "")).lower()
    is_trade_finance = any(
        marker in decision_type
        for marker in ("trade", "commodity", "finance", "trading")
    ) or any(marker in text for marker in ("usd/mt", "/mt", "gasoil", "cif", "bill of lading", "b/l"))

    if is_trade_finance:
        signals.append("For commodity or trade-finance cases, test fully loaded net margin before treating execution gates as sufficient.")
    if is_trade_finance and ("deferred" in text or "credit period" in text or "receivable" in text):
        signals.append("Model payment timing explicitly; deferred payment can turn an operationally feasible trade into a negative-return decision.")
    if is_trade_finance and ("cif" in text or "bill of lading" in text or "b/l" in text):
        signals.append("Separate payment/document-control mechanics from general commercial attractiveness.")
    if "vendor" in text or "feed" in text or "rom estimate" in text:
        signals.append("For technical projects, distinguish conceptual feasibility from vendor-confirmed FEED or ROM readiness.")
    if "permit" in text or "regulatory" in text or "sanctions" in text or "kyc" in text:
        signals.append("Treat regulatory, KYC, sanctions and permit evidence as gates, not as background risks.")
    if "class 5" in text or "capex" in text or "opex" in text:
        signals.append("Do not let preliminary CAPEX/OPEX estimates be interpreted as bankable investment evidence.")

    if not signals:
        signals.append("Use the case as a reference for gate discipline, failure-map priority and breakpoint wording.")
    return sorted(set(signals))


def build_library(cards: list[CaseCard], outputs_dir: Path) -> dict[str, Any]:
    failure_counter: Counter[str] = Counter()
    gate_counter: Counter[str] = Counter()
    domain_counter: Counter[str] = Counter()
    outcome_counter: Counter[str] = Counter()
    diagnosis_counter: Counter[str] = Counter()
    signal_counter: Counter[str] = Counter()
    scores: list[int] = []

    for card in cards:
        outcome_counter.update([card.decision_outcome])
        diagnosis_counter.update([card.diagnosis])
        scores.extend([card.stability_score] if isinstance(card.stability_score, int) else [])
        failure_counter.update(card.primary_failure_mechanisms)
        gate_counter.update(gate.get("gate_code") or gate.get("gate") for gate in card.critical_open_gates)
        domain_counter.update(card.recurring_domains)
        signal_counter.update(card.learning_signals)

    score_stats = {
        "min": min(scores) if scores else None,
        "max": max(scores) if scores else None,
        "average": round(sum(scores) / len(scores), 1) if scores else None,
    }

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_outputs_dir": str(outputs_dir),
        "case_count": len(cards),
        "scope_note": (
            "Local learning library built from structured MAI outputs only "
            "(session_input.json and result.json). It does not train a model "
            "and does not read raw evidence packs or source documents. "
            "Smoke/sample fixtures are excluded."
        ),
        "cases": [card.to_dict() for card in cards],
        "patterns": {
            "score_stats": score_stats,
            "outcome_distribution": dict(outcome_counter.most_common()),
            "diagnosis_distribution": dict(diagnosis_counter.most_common()),
            "common_failure_mechanisms": counter_rows(failure_counter),
            "common_critical_gate_codes": counter_rows(gate_counter),
            "common_deviation_domains": counter_rows(domain_counter),
            "learning_signals": counter_rows(signal_counter),
        },
    }


def counter_rows(counter: Counter[str]) -> list[dict[str, Any]]:
    return [
        {"item": item, "count": count}
        for item, count in counter.most_common()
        if str(item).strip()
    ]


def render_learning_notes(library: dict[str, Any]) -> str:
    lines = [
        "# MAI Learning Notes",
        "",
        library["scope_note"],
        "",
        f"Cases included: **{library['case_count']}**",
        "",
        "## Pattern Summary",
        "",
    ]
    stats = library["patterns"]["score_stats"]
    lines.extend(
        [
            f"- Score range: {stats['min']} to {stats['max']}",
            f"- Average score: {stats['average']}",
            "",
            "### Reusable Learning Signals",
            "",
        ]
    )
    for row in library["patterns"]["learning_signals"]:
        lines.append(f"- ({row['count']}x) {row['item']}")

    lines.extend(["", "### Common Failure Mechanisms", ""])
    for row in library["patterns"]["common_failure_mechanisms"][:12]:
        lines.append(f"- ({row['count']}x) {row['item']}")

    lines.extend(["", "### Common Critical Gate Codes", ""])
    for row in library["patterns"]["common_critical_gate_codes"][:12]:
        lines.append(f"- ({row['count']}x) {row['item']}")

    lines.extend(["", "## Case Cards", ""])
    for case in library["cases"]:
        lines.extend(
            [
                f"### {case['case_name']}",
                "",
                f"- Decision type: {case['decision_type']}",
                f"- Score / outcome: {case['stability_score']} / {case['decision_outcome']}",
                f"- Diagnosis: {case['diagnosis']}",
                f"- Decision: {case['decision']}",
                "",
                "**Critical breakpoint:**",
                "",
                case["critical_breakpoint"] or "Not provided.",
                "",
                "**Top failures:**",
            ]
        )
        for failure in case["top_failures"][:5]:
            lines.append(
                f"- P{failure['priority']} {failure['location']}: "
                f"{failure['failure_type']} ({failure['severity']})"
            )
        lines.extend(["", "**Learning signals:**"])
        for signal in case["learning_signals"]:
            lines.append(f"- {signal}")
        lines.append("")

    return "\n".join(lines)
