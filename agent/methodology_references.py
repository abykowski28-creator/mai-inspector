from __future__ import annotations

from typing import Any


# IMPORTANT — honesty boundary (audit finding #1).
# These standards informed the DESIGN of the MAI method. The engine does NOT
# execute an ISO 31000 risk process, an IEC 31010 technique selection, a COSO
# control mapping or an IEC 60812 FMECA on any specific case. This list is the
# same for every assessment, so it must be presented as background references,
# never as case-specific compliance or clause-level traceability.
METHOD_DISCLAIMER = (
    "These standards informed the design of the MAI method. MAI does not execute "
    "their procedures on this specific case, and this section is not a statement of "
    "compliance, certification, or per-case traceability to any clause. The same "
    "references apply to every MAI assessment."
)

METHOD_REFERENCES = [
    {
        "reference": "ISO 31000:2018",
        "scope": "Risk management process: identification, analysis, evaluation, treatment, reporting.",
        "influence": "Shapes how an MAI session structures risks, domains and gates.",
        "source": "https://www.iso.org/standard/65694.html",
    },
    {
        "reference": "IEC 31010:2019",
        "scope": "Risk assessment techniques (scenario analysis, checklists, FMEA-style mapping).",
        "influence": "Inspires the stress-scenario and failure-map structure of a session.",
        "source": "https://www.iso.org/standard/72140.html",
    },
    {
        "reference": "COSO ERM 2017",
        "scope": "Enterprise risk governance and response (severity, prioritization, ownership).",
        "influence": "Inspires gate ownership, criticality and response framing.",
        "source": "https://www.coso.org/guidance-erm",
    },
    {
        "reference": "IEC 60812:2018",
        "scope": "FMEA / FMECA failure-mode and criticality analysis.",
        "influence": "Inspires the failure map's mode / severity / fixability structure.",
        "source": "https://webstore.iec.ch/en/publication/26359",
    },
    {
        "reference": "UK Government Functional Standard GovS 002: Project delivery",
        "scope": "Project delivery governance: assurance, decision making, life cycles, gates, traceability, risk and verification/validation.",
        "influence": "Provides the primary MAI stage-gate and assurance-before-commitment reference.",
        "source": "docs/MAI_GOVS002_PROJECT_DELIVERY_REFERENCE_RU.md",
        "anchors": "Sections 2, 4.2.3, 4.3, 6.3, 7.6, 7.8, 8.6, Annex B, Annex C.",
    },
    {
        "reference": "IPA Project Set Up Toolkit",
        "scope": "Early project set-up maturity: Project / Programme Outcome Profile, Opportunity Framing and Project Routemap.",
        "influence": "Frames MAI's early-stage why / what / how checks before a project moves through stage-gates.",
        "source": "docs/MAI_PROJECT_SET_UP_TOOLKIT_REFERENCE_RU.md",
        "anchors": "Outcome Profile = why; Opportunity Framing = what; Project Routemap = how.",
    },
    {
        "reference": "Generic phase-gate / Stage-Gate decision logic",
        "scope": "Stages separated by gate reviews.",
        "influence": "Secondary generic framing for private-sector stage-gate terminology where GovS 002 is not directly applicable.",
        "source": "docs/MAI_METHOD_REFERENCE_REGISTRY_RU.md",
    },
]

# Backward-compatible alias (older code imported STANDARD_TRACEABILITY).
STANDARD_TRACEABILITY = METHOD_REFERENCES


DEFAULT_STAGE_GATE = {
    "current_stage": "Stage 1 - Scoping / Pre-DD",
    "next_gate": "Evidence package and decision gate definition",
    "blocked_milestone": "binding commitment or investor funding",
    "gate_owner": "Sponsor / investor committee",
    "movement_allowed": "Proceed only to controlled due diligence.",
}


def normalize_stage_gate(session: dict[str, Any], outcome: str | None = None) -> dict[str, str]:
    raw = session.get("stage_gate") or session.get("current_stage_gate") or {}
    if isinstance(raw, str):
        stage = {"current_stage": raw}
    elif isinstance(raw, dict):
        stage = {str(k): "" if v is None else str(v) for k, v in raw.items()}
    else:
        stage = {}

    normalized = dict(DEFAULT_STAGE_GATE)
    normalized.update({k: v for k, v in stage.items() if v})

    if "current_stage" not in stage and "decision_brief" in session:
        inferred = infer_stage_from_session(session)
        normalized.update({k: v for k, v in inferred.items() if v})

    if outcome:
        normalized["movement_allowed"] = movement_from_outcome(outcome)

    return normalized


def infer_stage_from_session(session: dict[str, Any]) -> dict[str, str]:
    text = " ".join(
        str(value)
        for value in [
            session.get("decision_type", ""),
            session.get("scoring_profile", ""),
            session.get("decision_brief", {}).get("current_status", "")
            if isinstance(session.get("decision_brief"), dict)
            else "",
            session.get("decision_brief", {}).get("next_decision_required", "")
            if isinstance(session.get("decision_brief"), dict)
            else "",
        ]
    ).lower()

    if "feed" in text or "business plan" in text or "pilot" in text:
        return {
            "current_stage": "Stage 2 - Business Case / Pre-FEED",
            "next_gate": "Validated technical, commercial and permitting basis for pilot/FEED authorization",
            "blocked_milestone": "equipment order, customer commitment and investor capital commitment",
        }
    if "acquisition" in text or "due diligence" in text or "dd" in text:
        return {
            "current_stage": "Stage 1-2 - Scoping / Due Diligence Structuring",
            "next_gate": "Validated legal, technical, commercial and financial due diligence package",
            "blocked_milestone": "SPA signing, closing or investor funding",
        }
    if "trade" in text or "supply" in text or "offtake" in text:
        return {
            "current_stage": "Stage 2 - Commercial Structuring / Pre-Funding",
            "next_gate": "Priced and secured trade structure with payment, title and margin protection",
            "blocked_milestone": "first lift authorization or deferred payment exposure",
        }
    return {}


def movement_from_outcome(outcome: str) -> str:
    normalized = str(outcome).strip().upper()
    if normalized == "GO":
        return "Proceed to the next gate if independent due diligence remains satisfactory."
    if normalized == "CONDITIONAL GO":
        return "Proceed conditionally; do not cross blocked milestone until critical gates are closed."
    if normalized == "REDESIGN":
        return "Redesign decision architecture before any binding commitment."
    if normalized == "NO-GO":
        return "Stop current decision path unless the project thesis or structure materially changes."
    return DEFAULT_STAGE_GATE["movement_allowed"]
