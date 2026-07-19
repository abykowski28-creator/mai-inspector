from __future__ import annotations

import unittest

from agent.iec31010 import build_iec31010


def _status(log, technique_substr):
    for r in log["rows"]:
        if technique_substr.lower() in r["technique"].lower():
            return r["status"]
    return None


class Iec31010Tests(unittest.TestCase):
    def test_applied_when_data_present(self):
        session = {
            "stress_scenarios": [{"scenario": "Shock", "system_impact": "Severe",
                                  "propagation_path": "a -> b"}],
            "decision_gates": [{"gate": "G", "criticality": "critical", "status": "open"}],
            "deviations": [{"deviation": "d", "severity": "High", "likelihood": "High"}],
            "claim_register": [{"claim": "c"}],
            "semantic_risks": [{"risk": "r"}],
        }
        log = build_iec31010(session)
        self.assertEqual(_status(log, "Scenario analysis"), "applied")
        self.assertEqual(_status(log, "Failure mode"), "applied")
        self.assertEqual(_status(log, "Checklist"), "applied")
        self.assertEqual(_status(log, "Consequence/likelihood"), "applied")
        self.assertEqual(_status(log, "propagation"), "applied")
        self.assertGreaterEqual(log["applied_count"], 5)

    def test_not_applicable_when_data_absent(self):
        log = build_iec31010({})
        self.assertEqual(_status(log, "Scenario analysis"), "not_applicable")
        self.assertEqual(_status(log, "Checklist"), "not_applicable")
        # Root cause is always not_applicable until the schema carries causes.
        self.assertEqual(_status(log, "Root cause"), "not_applicable")
        self.assertEqual(_status(log, "HAZOP"), "not_applicable")

    def test_root_cause_applied_when_cause_present(self):
        log = build_iec31010({"deviations": [{"deviation": "d", "cause": "weld defect"}]})
        self.assertEqual(_status(log, "Root cause"), "applied")

    def test_matrix_requires_both_severity_and_likelihood(self):
        log = build_iec31010({"deviations": [{"deviation": "d", "severity": "High"}]})
        self.assertEqual(_status(log, "Consequence/likelihood"), "not_applicable")


if __name__ == "__main__":
    unittest.main()
