from __future__ import annotations

import unittest

from agent.iso31000 import build_iso31000, risk_level

GATES = [
    {"gate": "Lease bankability and assignment comfort", "gate_code": "G-LEASE",
     "required_evidence": "Ministry confirmation of lease assignment.",
     "owner": "Counsel", "status": "open", "criticality": "critical"},
]


class Iso31000Tests(unittest.TestCase):
    def test_risk_level_matrix(self):
        self.assertEqual(risk_level("Critical", "High")[1], "Extreme")   # 4*3=12
        self.assertEqual(risk_level("High", "Medium")[1], "High")        # 3*2=6
        self.assertEqual(risk_level("High", "Low")[1], "Medium")         # 3*1=3 -> Medium
        self.assertEqual(risk_level("Low", "Low")[1], "Low")             # 1*1=1

    def test_medium_band_boundary(self):
        # 2*2 = 4 -> Medium ; 2*1 = 2 -> Low
        self.assertEqual(risk_level("Medium", "Medium")[1], "Medium")
        self.assertEqual(risk_level("Medium", "Low")[1], "Low")

    def test_covered_risk_has_treatment_and_owner_no_gap(self):
        session = {"decision_gates": GATES, "deviations": [
            {"deviation": "Lease not assignable.", "severity": "Critical",
             "likelihood": "High", "affected_node": "land lease"},
        ]}
        reg = build_iso31000(session)
        row = reg["rows"][0]
        self.assertEqual(row["risk_level"], "Extreme")
        self.assertEqual(row["owner"], "Counsel")
        self.assertFalse(row["process_gap"])
        self.assertEqual(reg["process_gap_count"], 0)

    def test_uncovered_high_risk_is_process_gap(self):
        session = {"decision_gates": GATES, "deviations": [
            {"deviation": "Revenue model unproven.", "severity": "High",
             "likelihood": "High", "affected_node": "revenue architecture"},
        ]}
        reg = build_iso31000(session)
        row = reg["rows"][0]
        self.assertTrue(row["process_gap"])           # High + no covering gate
        self.assertEqual(row["status"], "untreated")
        self.assertEqual(reg["process_gap_count"], 1)

    def test_low_risk_uncovered_is_not_a_gap(self):
        session = {"decision_gates": GATES, "deviations": [
            {"deviation": "Cosmetic signage.", "severity": "Low",
             "likelihood": "Low", "affected_node": "signage"},
        ]}
        reg = build_iso31000(session)
        self.assertFalse(reg["rows"][0]["process_gap"])
        self.assertEqual(reg["process_gap_count"], 0)


if __name__ == "__main__":
    unittest.main()
