from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from agent.case_learning import build_learning_library


class CaseLearningTests(unittest.TestCase):
    def test_build_learning_library_from_scored_cases(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            outputs = root / "outputs"
            case = outputs / "trade_case"
            draft = outputs / "draft_case"
            out_dir = root / "learning"
            case.mkdir(parents=True)
            draft.mkdir(parents=True)

            session = {
                "session_id": "mai-trade-case",
                "session_date": "2026-06-22",
                "decision_type": "Trade Finance",
                "scoring_profile": "general",
                "thesis_strength": "moderate",
                "decision_brief": {"decision": "Finance a gasoil trade."},
                "deviations": [
                    {
                        "domain": "Financial / Unit Economics",
                        "affected_node": "net margin",
                    }
                ],
            }
            result = {
                "stability_score": 51,
                "decision_outcome": "REDESIGN",
                "decision_architecture_diagnosis": "Moderate thesis / weak decision architecture",
                "critical_breakpoint": "Do not proceed below USD 50/MT margin.",
                "primary_failure_mechanisms": ["Minimum Margin Threshold Failure"],
                "failure_map": [
                    {
                        "priority": 1,
                        "location": "net margin",
                        "failure_type": "Margin too thin.",
                        "severity": "High",
                        "fixable": "Partial",
                    }
                ],
                "decision_gates": [
                    {
                        "gate": "Minimum margin proof",
                        "gate_code": "G-MARGIN",
                        "required_evidence": "Per-MT model.",
                        "owner": "Finance",
                        "status": "open",
                        "criticality": "critical",
                    }
                ],
            }
            (case / "session_input.json").write_text(json.dumps(session), encoding="utf-8")
            (case / "result.json").write_text(json.dumps(result), encoding="utf-8")
            (draft / "session_draft.json").write_text("{}", encoding="utf-8")

            library = build_learning_library(outputs, out_dir)

            self.assertEqual(library["case_count"], 1)
            self.assertTrue((out_dir / "mai_case_library.json").exists())
            self.assertTrue((out_dir / "mai_learning_notes.md").exists())
            self.assertEqual(library["cases"][0]["case_name"], "trade_case")
            self.assertEqual(library["patterns"]["common_critical_gate_codes"][0]["item"], "G-MARGIN")


if __name__ == "__main__":
    unittest.main()
