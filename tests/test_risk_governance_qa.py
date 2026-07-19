from __future__ import annotations

import unittest

from agent.quality_assurance import _check_risk_governance, QualityIssue

COVERING_GATE = {
    "gate": "Lease bankability and assignment comfort", "gate_code": "G-LEASE",
    "required_evidence": "Ministry confirmation.", "owner": "Counsel",
    "status": "open", "criticality": "critical",
}


class RiskGovernanceQaTests(unittest.TestCase):
    def test_uncovered_high_risk_warns(self):
        session = {
            "decision_gates": [COVERING_GATE],
            "deviations": [
                {"deviation": "Lease not assignable.", "severity": "Critical",
                 "likelihood": "High", "affected_node": "land lease"},        # covered
                {"deviation": "Revenue unproven.", "severity": "High",
                 "likelihood": "High", "affected_node": "revenue architecture"},  # uncovered
            ],
        }
        issues: list[QualityIssue] = []
        _check_risk_governance(session, issues)
        codes = {i.code for i in issues}
        self.assertIn("uncovered_high_risk", codes)
        self.assertIn("unassigned_risk_owner", codes)
        # All gap findings are warnings (they inform, they do not fail the gate).
        self.assertTrue(all(i.severity == "warning" for i in issues))

    def test_fully_covered_session_has_no_gap_warnings(self):
        session = {
            "decision_gates": [COVERING_GATE],
            "deviations": [
                {"deviation": "Lease not assignable.", "severity": "Critical",
                 "likelihood": "High", "affected_node": "land lease"},
            ],
        }
        issues: list[QualityIssue] = []
        _check_risk_governance(session, issues)
        codes = {i.code for i in issues}
        self.assertNotIn("uncovered_high_risk", codes)
        self.assertNotIn("unassigned_risk_owner", codes)

    def test_empty_session_is_safe(self):
        issues: list[QualityIssue] = []
        _check_risk_governance({}, issues)
        self.assertEqual(issues, [])


if __name__ == "__main__":
    unittest.main()
