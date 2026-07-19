from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

from .case_learning import build_learning_library
from .document_reader import build_evidence_pack
from .engine_runner import run_engine
from .evidence_trace import write_traceability_report
from .fmeca import write_fmeca_report
from .iso31000 import write_iso31000_report
from .iec31010 import write_iec31010_report
from .coso_erm import write_coso_erm_report
from .machine_output import write_machine_result
from .quality_assurance import write_quality_report
from .report_generator import write_investor_summary
from .sanitizer import sanitize_file
from .session_builder import (
    build_draft_session,
    build_missing_questions,
    build_session_with_llm,
)

# Backward-compatible alias
build_session_with_openai = build_session_with_llm

_LLM_PROVIDERS = ("anthropic", "openai")


def analyze(args: argparse.Namespace) -> None:
    workspace = args.workspace.resolve()
    output_dir = (args.output_dir or Path("outputs") / args.case_name).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    provider: str | None = getattr(args, "provider", None) or None
    if getattr(args, "use_openai", False) and provider is None:
        provider = "openai"
    model: str | None = getattr(args, "model", None) or None

    session_path: Path
    if args.session:
        session_path = args.session.resolve()
        copied_session_path = output_dir / "session_input.json"
        if session_path != copied_session_path.resolve():
            shutil.copy2(session_path, copied_session_path)
            session_path = copied_session_path
    elif args.project_folder:
        project_folder = args.project_folder.resolve()
        build_evidence_pack(project_folder, output_dir)
        evidence_pack_path = output_dir / "evidence_pack.md"

        if args.sanitize:
            sanitize_file(
                evidence_pack_path,
                output_dir / "sanitized_evidence_pack.md",
                output_dir / "redaction_report.json",
                redaction_map_path=args.redaction_map.resolve() if args.redaction_map else None,
                redact_amounts=args.redact_amounts,
            )
            evidence_pack_path = output_dir / "sanitized_evidence_pack.md"

        use_llm = getattr(args, "use_llm", False) or getattr(args, "use_openai", False)

        if use_llm:
            if not args.sanitize and not args.allow_raw_llm:
                raise SystemExit(
                    "LLM mode is blocked by default for raw evidence. "
                    "Use --sanitize or explicitly add --allow-raw-llm."
                )
            if not args.confirm_send and not args.yes_send:
                raise SystemExit(
                    "LLM mode requires explicit send confirmation. "
                    "Review the evidence pack, then add --confirm-send or --yes-send."
                )
            if args.confirm_send:
                confirm_external_send(evidence_pack_path)

            evidence_pack = evidence_pack_path.read_text(encoding="utf-8")
            learning_notes = ""
            if args.use_learning:
                learning_notes_path = args.learning_notes.resolve()
                if not learning_notes_path.exists():
                    raise SystemExit(f"Learning notes file not found: {learning_notes_path}")
                learning_notes = learning_notes_path.read_text(encoding="utf-8")

            session = build_session_with_llm(
                workspace,
                evidence_pack,
                args.case_name,
                learning_notes=learning_notes,
                provider=provider,
                model=model,
            )
            session_path = output_dir / "session_draft.json"
            session_path.write_text(json.dumps(session, ensure_ascii=False, indent=2), encoding="utf-8")
            (output_dir / "session_input.json").write_text(
                json.dumps(session, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            session_path = output_dir / "session_input.json"
        else:
            session = build_draft_session(workspace, args.case_name, project_folder)
            session_path = output_dir / "session_draft.json"
            session_path.write_text(json.dumps(session, ensure_ascii=False, indent=2), encoding="utf-8")
            (output_dir / "missing_data_questions.md").write_text(
                build_missing_questions(args.case_name),
                encoding="utf-8",
            )
            if args.draft_only:
                print(f"Draft session and evidence pack written to {output_dir}")
                return
            if not getattr(args, "allow_draft_scoring", False):
                raise SystemExit(
                    "Refusing to score an automatically generated draft session. "
                    "Use --draft-only, use --use-llm with reviewed evidence, provide --session, "
                    "or explicitly add --allow-draft-scoring for controlled testing."
                )
            (output_dir / "session_input.json").write_text(
                json.dumps(session, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            session_path = output_dir / "session_input.json"
    else:
        raise SystemExit("Provide either --session or --project-folder")

    result = run_engine(workspace, session_path, output_dir)
    write_investor_summary(output_dir, args.case_name, result)
    quality_report = write_quality_report(output_dir, args.case_name)
    traceability_report = write_traceability_report(output_dir, args.case_name)
    write_fmeca_report(output_dir, args.case_name)
    write_iso31000_report(output_dir, args.case_name)
    write_iec31010_report(output_dir, args.case_name)
    write_coso_erm_report(output_dir, args.case_name)
    machine_result = write_machine_result(
        output_dir,
        args.case_name,
        result,
        quality_report=quality_report,
        traceability_report=traceability_report,
    )
    if getattr(args, "strict_quality", False) and not quality_report["passed"]:
        raise SystemExit(f"MAI quality gate failed: {output_dir / 'quality_report.md'}")
    if getattr(args, "strict_quality", False) and not traceability_report["traceable"]:
        raise SystemExit(
            f"MAI traceability gate failed: {output_dir / 'traceability_report.md'}"
        )
    if getattr(args, "machine_json", False):
        print(json.dumps(machine_result, ensure_ascii=False))
    else:
        print(f"MAI analysis complete: {output_dir}")


def confirm_external_send(evidence_pack_path: Path) -> None:
    print("External API send requested.", file=sys.stderr)
    print(f"Evidence file to send: {evidence_pack_path}", file=sys.stderr)
    print("Type SEND to confirm that this file has been reviewed and may be sent.", file=sys.stderr)
    response = input("> ").strip()
    if response != "SEND":
        raise SystemExit("External send cancelled.")


def learn(args: argparse.Namespace) -> None:
    library = build_learning_library(args.outputs, args.out_dir)
    count = library["case_count"]
    print(f"MAI learning library written to {args.out_dir.resolve()} ({count} scored cases)")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="MAI Agent v0.1")
    subparsers = parser.add_subparsers(dest="command", required=True)

    ap = subparsers.add_parser("analyze", help="Analyze a project folder or MAI session JSON")
    ap.add_argument("--workspace", type=Path, required=True, help="Path to the workspace containing session data and project documents")
    ap.add_argument("--case-name", required=True, help="Case name for output folder")
    ap.add_argument("--session", type=Path, help="Existing MAI session JSON")
    ap.add_argument("--project-folder", type=Path, help="Folder with project documents")
    ap.add_argument("--output-dir", type=Path, help="Custom output folder")
    ap.add_argument("--draft-only", action="store_true", help="Stop after evidence pack and draft session")
    ap.add_argument("--allow-draft-scoring", action="store_true",
                    help="Allow scoring of an automatically generated non-LLM draft session (controlled testing only)")
    ap.add_argument("--strict-quality", action="store_true",
                    help="Exit with an error when the generated MAI quality report has errors")
    ap.add_argument("--machine-json", action="store_true",
                    help="Print the n8n-friendly machine_result.json payload to stdout")

    ap.add_argument("--use-llm", action="store_true",
                    help="Use an LLM to draft the session JSON (auto-detects Anthropic or OpenAI)")
    ap.add_argument("--provider", choices=_LLM_PROVIDERS, default=None,
                    help="LLM provider: anthropic (Claude) or openai. Overrides MAI_LLM_PROVIDER env var.")
    ap.add_argument("--model", default=None,
                    help="Model name, e.g. claude-sonnet-4-6 or gpt-5.5. Overrides env var defaults.")
    ap.add_argument("--use-openai", action="store_true",
                    help="[Deprecated] Use --use-llm --provider openai instead.")

    ap.add_argument("--sanitize", action="store_true",
                    help="Sanitize evidence pack before any external API call")
    ap.add_argument("--redaction-map", type=Path,
                    help="JSON map of sensitive names/entities to aliases")
    ap.add_argument("--redact-amounts", action="store_true",
                    help="Redact currency amounts from sanitized evidence")
    ap.add_argument("--confirm-send", action="store_true",
                    help="Require interactive SEND confirmation before LLM API call")
    ap.add_argument("--yes-send", action="store_true",
                    help="Non-interactive confirmation for LLM API call")
    ap.add_argument("--allow-raw-llm", action="store_true",
                    help="Allow sending raw (unsanitized) evidence to external LLM API")
    ap.add_argument("--allow-raw-openai", action="store_true", dest="allow_raw_llm",
                    help=argparse.SUPPRESS)

    ap.add_argument("--use-learning", action="store_true",
                    help="Include local MAI learning notes in session drafting")
    ap.add_argument("--learning-notes", type=Path,
                    default=Path("learning") / "mai_learning_notes.md",
                    help="Learning notes file path (used with --use-learning)")
    ap.set_defaults(func=analyze)

    lp = subparsers.add_parser("learn", help="Build a learning library from completed MAI output folders")
    lp.add_argument("--outputs", type=Path, default=Path("outputs"),
                    help="Folder containing MAI case output folders")
    lp.add_argument("--out-dir", type=Path, default=Path("learning"),
                    help="Folder where the learning library will be written")
    lp.set_defaults(func=learn)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
