from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from agent.case_learning import build_learning_library, is_fixture_session


def _write_case(folder: Path, session: dict, score: int, outcome: str) -> None:
    folder.mkdir(parents=True)
    (folder / "session_input.json").write_text(json.dumps(session), encoding="utf-8")
    (folder / "result.json").write_text(
        json.dumps({"stability_score": score, "decision_outcome": outcome}),
        encoding="utf-8",
    )


class FixtureQuarantineTests(unittest.TestCase):
    def test_is_fixture_detects_flag_and_known_id(self):
        self.assertTrue(is_fixture_session({"fixture": True, "session_id": "x"}))
        self.assertTrue(is_fixture_session({"session_id": "mai-sample-2026-001"}))
        self.assertFalse(is_fixture_session({"session_id": "mai-real-case-2026-001"}))

    def test_learn_excludes_fixtures(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            outputs = root / "outputs"
            _write_case(
                outputs / "real_case",
                {"session_id": "mai-real-2026-001",
                 "decision_brief": {"decision": "Real decision."}},
                61, "CONDITIONAL GO",
            )
            _write_case(
                outputs / "flagged_fixture",
                {"session_id": "mai-real-2026-002", "fixture": True,
                 "decision_brief": {"decision": "Demo decision."}},
                51, "REDESIGN",
            )
            _write_case(
                outputs / "known_sample",
                {"session_id": "mai-sample-2026-001",
                 "decision_brief": {"decision": "Sample decision."}},
                51, "REDESIGN",
            )

            library = build_learning_library(outputs, root / "learning")

            self.assertEqual(library["case_count"], 1)
            self.assertEqual(library["cases"][0]["case_name"], "real_case")
            ids = {c["session_id"] for c in library["cases"]}
            self.assertNotIn("mai-sample-2026-001", ids)


if __name__ == "__main__":
    unittest.main()
