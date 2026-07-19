from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from types import ModuleType
from typing import Any

from .version import AGENT_VERSION

# Canonical, version-controlled copy of the scoring engine that ships with this
# repo. Using the vendored copy by default is what makes outputs reproducible:
# the exact scoring logic is pinned here and hashed into every result.json.
VENDORED_ENGINE = Path(__file__).resolve().parent / "engine" / "mai_decision_lab_v2_1.py"


def load_engine(engine_path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location("mai_engine_runtime", engine_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load MAI engine from {engine_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def resolve_engine_path(workspace: Path) -> tuple[Path, str]:
    """Prefer the vendored engine; fall back to the workspace engine.

    Returns (path, source) where source is 'vendored' or 'workspace'.
    """
    if VENDORED_ENGINE.exists():
        return VENDORED_ENGINE, "vendored"
    candidate = workspace / "03_Engine" / "mai_decision_lab_v2_1.py"
    if candidate.exists():
        return candidate, "workspace"
    raise RuntimeError(
        "No scoring engine found. Expected vendored copy at "
        f"{VENDORED_ENGINE} or workspace copy at {candidate}."
    )


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _git_commit(repo_dir: Path) -> str | None:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if out.returncode == 0:
            return out.stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        pass
    return None


def build_provenance(
    engine_path: Path,
    engine_source: str,
    engine_module: ModuleType,
    session_path: Path,
) -> dict[str, Any]:
    repo_dir = Path(__file__).resolve().parent.parent
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "agent_version": AGENT_VERSION,
        "engine_version": getattr(engine_module, "ENGINE_VERSION", "unknown"),
        "engine_file": engine_path.name,
        "engine_source": engine_source,
        "engine_sha256": _sha256(engine_path),
        "git_commit": _git_commit(repo_dir),
        "input_session_sha256": _sha256(session_path),
    }


def _provenance_footer(provenance: dict[str, Any]) -> str:
    lines = [
        "",
        "---",
        "",
        "## Provenance",
        "",
        "This report is reproducible: re-running the stamped engine version on the "
        "stamped input session hash yields the same score and outcome.",
        "",
        f"- Generated at: {provenance['generated_at']}",
        f"- Agent version: {provenance['agent_version']}",
        f"- Engine version: {provenance['engine_version']} ({provenance['engine_source']})",
        f"- Engine file: {provenance['engine_file']}",
        f"- Engine SHA-256: {provenance['engine_sha256']}",
        f"- Git commit: {provenance['git_commit'] or 'n/a (repo not under git)'}",
        f"- Input session SHA-256: {provenance['input_session_sha256']}",
        "",
    ]
    return "\n".join(lines)


def run_engine(
    workspace: Path,
    session_path: Path,
    output_dir: Path,
    engine_path: Path | None = None,
) -> dict[str, Any]:
    if engine_path is None:
        engine_path, engine_source = resolve_engine_path(workspace)
    else:
        engine_path = Path(engine_path)
        engine_source = "explicit"

    engine = load_engine(engine_path)
    session = json.loads(session_path.read_text(encoding="utf-8"))
    result = engine.analyze_session(session)
    result_data = result.to_dict()

    provenance = build_provenance(engine_path, engine_source, engine, session_path)
    # Provenance is metadata only. It never changes the score or outcome; the
    # engine remains the single source of truth for those.
    result_data["provenance"] = provenance

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "result.json").write_text(
        json.dumps(result_data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (output_dir / "report.md").write_text(
        engine.render_markdown(session, result) + _provenance_footer(provenance),
        encoding="utf-8",
    )
    return result_data
