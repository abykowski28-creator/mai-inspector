from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

from .llm_client import call_llm_json


def load_minimal_session(workspace: Path) -> dict[str, Any]:
    template_path = workspace / "05_Schema_Tests_Config" / "minimal_complete_session.json"
    return json.loads(template_path.read_text(encoding="utf-8"))


def build_draft_session(workspace: Path, case_name: str, project_folder: Path | None = None) -> dict[str, Any]:
    session = load_minimal_session(workspace)
    session["session_id"] = f"mai-{case_name}"
    session["session_date"] = date.today().isoformat()
    session["decision_brief"]["decision"] = (
        f"Analyze project decision reliability for {project_folder.name if project_folder else case_name}."
    )
    session["decision_brief"]["current_status"] = "pre-execution"
    session["decision_brief"]["next_decision_required"] = "diagnose"
    session["thesis_strength"] = "unclear"
    session["critical_breakpoint_proximity"] = "medium"
    return session


def build_missing_questions(case_name: str) -> str:
    return "\n".join([
        f"# Missing Data Questions - {case_name}",
        "",
        "The agent created a draft session, but human confirmation is required before scoring this as a real decision.",
        "",
        "## Required confirmations",
        "",
        "1. What exact decision is being tested?",
        "2. What is the decision type: M&A / Asset Acquisition, Product Launch, Technology / R&D, Regulatory / Policy, Infrastructure / Capital Project, or General?",
        "3. What is the current execution stage?",
        "4. Which claims are confirmed by documents, and which are assumptions?",
        "5. Which decision gates must be closed before funding, signing, launch or execution?",
        "6. What is the correct thesis strength: strong, moderate, weak or unclear?",
        "7. What is the critical breakpoint where the decision becomes unrecoverable?",
        "",
    ])


def build_session_with_llm(
    workspace: Path,
    evidence_pack: str,
    case_name: str,
    learning_notes: str = "",
    provider: str | None = None,
    model: str | None = None,
) -> dict[str, Any]:
    """Convert an evidence pack into a MAI session JSON using the configured LLM.

    Works with any provider supported by call_llm_json (Anthropic or OpenAI).
    """
    prompt_path = workspace / "01_Prompt_System" / "MAI_Prompt_System_v2_1_Latest_Working.md"
    reference_path = workspace / "04_References" / "MAI_Decision_Types_Reference_v2_1.md"
    semantic_path = workspace / "04_References" / "semantic_risk_taxonomy.md"
    minimal_schema_path = workspace / "05_Schema_Tests_Config" / "minimal_complete_session.json"

    sections = [
        "You are MAI Agent v0.1.",
        "",
        "Your task is to convert the evidence pack into a complete MAI session JSON.",
        "Use the MAI Prompt System, Decision Types Reference, Semantic Risk Taxonomy and example session structure below.",
        "Return JSON only. Do not return Markdown. Do not include explanations outside JSON.",
        "",
        f"CASE NAME:\n{case_name}",
        "",
        f"MAI PROMPT SYSTEM:\n{prompt_path.read_text(encoding='utf-8')[:20000]}",
        "",
        f"DECISION TYPES REFERENCE:\n{reference_path.read_text(encoding='utf-8')[:12000]}",
        "",
        f"SEMANTIC RISK TAXONOMY:\n{semantic_path.read_text(encoding='utf-8')[:10000]}",
        "",
        f"EXAMPLE SESSION STRUCTURE:\n{minimal_schema_path.read_text(encoding='utf-8')}",
        "",
        f"EVIDENCE PACK:\n{evidence_pack[:55000]}",
        "",
        f"LOCAL MAI LEARNING NOTES:\n{learning_notes[:12000] if learning_notes else '[Not provided]'}",
        "",
        "Rules:",
        "- If evidence is missing, mark claims and assumptions as unverified or conditional.",
        "- Do not invent contracts, permits, approvals, financial commitments or technical evidence.",
        "- Every claim_register entry must include a 'sources' array; each source is "
        "{file, locator, quote}, where 'quote' is text copied VERBATIM from the evidence pack "
        "and 'file' matches a document name in the evidence pack.",
        "- Never write a quote that is not present verbatim in the evidence pack. If you cannot "
        "quote it, set the claim status to unverified and omit the quote.",
        "- Mark a claim 'confirmed' only when a source quote in the evidence pack states it "
        "directly; otherwise use conditional, assumed, upside or unverified.",
        "- Set thesis_strength independently from score.",
        "- Every deviation must include affected_node and execution_window.",
        "- Every decision gate must include gate, required_evidence, owner, status and criticality.",
        "- Use LOCAL MAI LEARNING NOTES only as pattern guidance; never override project evidence with prior-case assumptions.",
        "- Output must match the MAI session JSON shape.",
    ]
    prompt = "\n".join(sections)
    return call_llm_json(prompt, provider=provider, model=model)


# Backward-compatible alias
build_session_with_openai = build_session_with_llm
