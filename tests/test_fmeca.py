from __future__ import annotations

import unittest

from agent.fmeca import build_fmeca, detection_value, gate_coverage

GATES = [
    {"gate": "Lease bankability and assignment comfort", "gate_code": "G-LEASE",
     "required_evidence": "Ministry confirmation of lease assignment.",
     "owner": "Counsel", "status": "open", "criticality": "critical"},
]


class FmecaTests(unittest.TestCase):
    def test_gate_coverage_matches_node_tokens(self):
        level, gate = gate_coverage("land lease", GATES)
        self.assertEqual(level, "critical")
        self.assertIsNotNone(gate)
        level2, _ = gate_coverage("unrelated widget", GATES)
        self.assertEqual(level2, "none")

    def test_detection_prefers_explicit_detectability(self):
        d, basis, _ = detection_value({"detectability": "low", "affected_node": "land lease"}, GATES)
        self.assertEqual(d, 9)
        self.assertIn("explicit", basis)

    def test_detection_from_gate_coverage(self):
        d, basis, gate = detection_value({"affected_node": "land lease"}, GATES)
        self.assertEqual(d, 3)  # covered by critical gate
        self.assertIsNotNone(gate)
        d2, basis2, _ = detection_value({"affected_node": "marketing plan"}, GATES)
        self.assertEqual(d2, 9)  # no gate covers it
        self.assertIn("no decision gate", basis2)

    def test_rpn_and_ranking(self):
        session = {
            "decision_gates": GATES,
            "deviations": [
                {"deviation": "Lease not assignable.", "severity": "Critical",
                 "likelihood": "High", "affected_node": "land lease", "fixable": "Partial"},
                {"deviation": "Minor cosmetic issue.", "severity": "Low",
                 "likelihood": "Low", "affected_node": "signage", "fixable": "Yes"},
            ],
        }
        fmeca = build_fmeca(session)
        rows = fmeca["rows"]
        self.assertEqual(rows[0]["priority"], 1)
        # Critical+High covered by critical gate: S10 * O8 * D3 = 240
        self.assertEqual(rows[0]["rpn"], 240)
        self.assertEqual(rows[0]["rpn_band"], "high")
        # Low+Low, no gate: S2 * O2 * D9 = 36
        self.assertEqual(rows[1]["rpn"], 36)
        self.assertEqual(rows[1]["rpn_band"], "low")
        # Highest-RPN mode ranks first.
        self.assertGreater(rows[0]["rpn"], rows[1]["rpn"])

    def test_does_not_crash_without_deviations(self):
        fmeca = build_fmeca({"failure_map": [
            {"location": "tanks", "failure_type": "Corrosion", "severity": "High", "fixable": "Yes"},
        ]})
        self.assertEqual(fmeca["mode_count"], 1)
        self.assertEqual(fmeca["rows"][0]["severity"], 8)


if __name__ == "__main__":
    unittest.main()
