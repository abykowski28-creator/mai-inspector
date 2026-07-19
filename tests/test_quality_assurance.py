from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from agent.quality_assurance import build_quality_report


class QualityAssuranceTests(unittest.TestCase):
    def test_quality_report_rejects_go_with_open_critical_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)
            case_name = "quality_case"
            result = {
                "stability_score": 85,
                "decision_outcome": "GO",
                "critical_breakpoint": "Do not fund before anchor customer evidence is closed.",
                "decision_gates": [
                    {
                        "gate": "Anchor customer proof",
                        "required_evidence": "Signed term sheet.",
                        "owner": "Sponsor",
                        "status": "open",
                        "criticality": "critical",
                    }
                ],
            }
            (output / "result.json").write_text(json.dumps(result), encoding="utf-8")
            (output / "report.md").write_text(
                "# Report\n\nCritical Breakpoint\n\nDecision gates are listed.",
                encoding="utf-8",
            )
            summary = (
                "# Investor Summary\n\n"
                "Methodology and Standards Traceability\n\n"
                "This result is a decision-readiness assessment.\n\n"
                "Required Independent Verification\n"
            )
            (output / "investor_summary.md").write_text(summary, encoding="utf-8")
            (output / f"{case_name}_MAI_Standard_Report.md").write_text(summary, encoding="utf-8")
            (output / f"{case_name}_method_traceability.json").write_text("{}", encoding="utf-8")
            (output / "session_input.json").write_text("{}", encoding="utf-8")

            report = build_quality_report(output, case_name)

            self.assertFalse(report["passed"])
            codes = {issue["code"] for issue in report["issues"]}
            self.assertIn("go_with_open_critical_gate", codes)


if __name__ == "__main__":
    unittest.main()
