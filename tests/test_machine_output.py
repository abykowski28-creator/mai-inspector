from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from agent.machine_output import write_machine_result


class MachineOutputTests(unittest.TestCase):
    def test_write_machine_result_includes_stage_gate_and_open_critical_gates(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)
            session = {
                "stage_gate": {
                    "current_stage": "Stage 2 - Business Case / Pre-FEED",
                    "next_gate": "Gas treatment FEED",
                    "blocked_milestone": "equipment order",
                    "gate_owner": "Investor committee",
                }
            }
            result = {
                "stability_score": 61,
                "decision_outcome": "CONDITIONAL GO",
                "decision_architecture_diagnosis": "Strong thesis / unstable execution architecture",
                "critical_breakpoint": "Do not order equipment before FEED.",
                "decision_gates": [
                    {
                        "gate": "Gas treatment FEED",
                        "gate_code": "G-FEED",
                        "owner": "EPC",
                        "status": "open",
                        "criticality": "critical",
                        "required_evidence": "FEED package.",
                    },
                    {
                        "gate": "Scope ring-fence",
                        "gate_code": "G-SCOPE",
                        "owner": "Sponsor",
                        "status": "open",
                        "criticality": "high",
                        "required_evidence": "Approved scope.",
                    },
                ],
            }
            (output_dir / "session_input.json").write_text(
                json.dumps(session),
                encoding="utf-8",
            )

            payload = write_machine_result(
                output_dir,
                "gas_case",
                result,
                quality_report={"passed": True},
                traceability_report={"traceable": True},
            )

            self.assertEqual(payload["schema_version"], "mai-machine-result-v1")
            self.assertEqual(payload["critical_gates_open_count"], 1)
            self.assertEqual(payload["critical_gates_open"][0]["gate_code"], "G-FEED")
            self.assertEqual(payload["stage_gate"]["current_stage"], "Stage 2 - Business Case / Pre-FEED")
            self.assertEqual(payload["executive_outputs"]["decision_status"], "Not Yet")
            self.assertEqual(
                payload["executive_outputs"]["highest_responsible_commitment"],
                "Gas treatment FEED",
            )
            self.assertIn("critical_blockers", payload["executive_outputs"])
            self.assertIn("required_evidence", payload["executive_outputs"])
            self.assertIn("recommended_next_step", payload["executive_outputs"])
            self.assertTrue((output_dir / "machine_result.json").exists())


if __name__ == "__main__":
    unittest.main()
