from __future__ import annotations

import argparse
import json
import tempfile
import unittest
from pathlib import Path

from agent.mai_agent import analyze


class MaiAgentWorkflowTests(unittest.TestCase):
    def test_project_folder_draft_is_not_scored_without_explicit_override(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workspace = root / "workspace"
            project = root / "project"
            output = root / "output"
            (workspace / "05_Schema_Tests_Config").mkdir(parents=True)
            project.mkdir()
            minimal_session = {
                "session_id": "mai-template",
                "session_date": "2026-06-27",
                "decision_brief": {
                    "decision": "Template decision.",
                    "current_status": "",
                    "next_decision_required": "",
                },
                "thesis_strength": "unclear",
                "critical_breakpoint_proximity": "medium",
            }
            (workspace / "05_Schema_Tests_Config" / "minimal_complete_session.json").write_text(
                json.dumps(minimal_session),
                encoding="utf-8",
            )
            (project / "brief.txt").write_text("Decision: launch pilot.", encoding="utf-8")
            args = argparse.Namespace(
                workspace=workspace,
                case_name="draft_case",
                session=None,
                project_folder=project,
                output_dir=output,
                draft_only=False,
                allow_draft_scoring=False,
                strict_quality=False,
                use_llm=False,
                use_openai=False,
                provider=None,
                model=None,
                sanitize=False,
                redaction_map=None,
                redact_amounts=False,
                confirm_send=False,
                yes_send=False,
                allow_raw_llm=False,
                use_learning=False,
                learning_notes=root / "missing_learning.md",
            )

            with self.assertRaises(SystemExit) as raised:
                analyze(args)

            self.assertIn("Refusing to score", str(raised.exception))
            self.assertTrue((output / "session_draft.json").exists())
            self.assertTrue((output / "missing_data_questions.md").exists())
            self.assertFalse((output / "result.json").exists())


if __name__ == "__main__":
    unittest.main()
