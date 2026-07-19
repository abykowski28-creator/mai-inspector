from __future__ import annotations

import unittest

from agent.coso_erm import build_coso_erm, response_type

GATES = [
    {"gate": "Lease bankability and assignment comfort", "gate_code": "G-LEASE",
     "required_evidence": "Ministry confirmation.", "owner": "Counsel",
     "status": "open", "criticality": "critical"},
]


class CosoErmTests(unittest.TestCase):
    def test_response_type(self):
        self.assertIn("Reduce (existing gate control)", response_type("High", True))
        self.assertIn("Avoid", response_type("Extreme", False))
        self.assertIn("Accept", response_type("Low", False))

    def test_covered_risk_has_owner_no_gap(self):
        session = {"decision_gates": GATES, "deviations": [
            {"deviation": "Lease not assignable.", "severity": "Critical",
             "likelihood": "High", "affected_node": "land lease"}]}
        coso = build_coso_erm(session)
        row = coso["rows"][0]
        self.assertEqual(row["owner"], "Counsel")
        self.assertFalse(row["governance_gap"])
        self.assertEqual(coso["governance_gap_count"], 0)

    def test_uncovered_high_risk_is_governance_gap(self):
        session = {"decision_gates": GATES, "deviations": [
            {"deviation": "Revenue unproven.", "severity": "High",
             "likelihood": "High", "affected_node": "revenue architecture"}]}
        coso = build_coso_erm(session)
        row = coso["rows"][0]
        self.assertEqual(row["owner"], "UNASSIGNED")
        self.assertTrue(row["governance_gap"])
        self.assertEqual(coso["governance_gap_count"], 1)

    def test_low_uncovered_is_not_a_gap(self):
        session = {"decision_gates": GATES, "deviations": [
            {"deviation": "Signage.", "severity": "Low",
             "likelihood": "Low", "affected_node": "signage"}]}
        coso = build_coso_erm(session)
        self.assertFalse(coso["rows"][0]["governance_gap"])
        self.assertEqual(coso["governance_gap_count"], 0)

    def test_priority_ranking(self):
        session = {"decision_gates": GATES, "deviations": [
            {"deviation": "Low risk.", "severity": "Low", "likelihood": "Low", "affected_node": "x"},
            {"deviation": "Extreme risk.", "severity": "Critical", "likelihood": "High", "affected_node": "y"}]}
        coso = build_coso_erm(session)
        self.assertEqual(coso["rows"][0]["risk_level"], "Extreme")
        self.assertEqual(coso["rows"][0]["priority"], 1)


if __name__ == "__main__":
    unittest.main()
