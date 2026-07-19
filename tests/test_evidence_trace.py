from __future__ import annotations

import unittest

from agent.evidence_trace import (
    check_session_traceability,
    normalize,
)


def codes(issues):
    return {i.code for i in issues}


EVIDENCE = (
    "# MAI Evidence Pack\n"
    "The asset includes approximately 130,000 m3 of storage capacity across 15 tanks.\n"
    "Investor return: 12% p.a. fixed on a USD 60M secured loan.\n"
)


class EvidenceTraceTests(unittest.TestCase):
    def test_quote_found_in_evidence_is_clean(self):
        session = {"claim_register": [{
            "claim": "130,000 m3 across 15 tanks.",
            "status": "confirmed",
            "importance": "critical",
            "sources": [{
                "file": "memo.docx",
                "locator": "p.1",
                "quote": "approximately 130,000 m3 of storage capacity across 15 tanks",
            }],
        }]}
        issues = check_session_traceability(session, EVIDENCE)
        self.assertEqual(codes(issues), set(), f"unexpected issues: {codes(issues)}")

    def test_quote_not_in_evidence_is_error(self):
        session = {"claim_register": [{
            "claim": "100 MW long-term portfolio ambition.",
            "status": "confirmed",
            "importance": "high",
            "sources": [{"file": "x.docx", "locator": "p.9",
                         "quote": "guaranteed 100 MW baseload portfolio secured"}],
        }]}
        issues = check_session_traceability(session, EVIDENCE)
        self.assertIn("quote_not_in_evidence", codes(issues))

    def test_confirmed_without_quote_is_error(self):
        session = {"claim_register": [{
            "claim": "Lease is assignable.",
            "status": "confirmed",
            "importance": "critical",
            "sources": [{"file": "lease.docx", "locator": "p.2", "quote": ""}],
        }]}
        issues = check_session_traceability(session, EVIDENCE)
        self.assertIn("confirmed_without_quote", codes(issues))

    def test_material_claim_without_source_is_error(self):
        session = {"claim_register": [{
            "claim": "Steady-state revenue USD 29-53m.",
            "status": "upside",
            "importance": "high",
            "evidence": "Technical proposal describes revenue envelope.",
        }]}
        issues = check_session_traceability(session, EVIDENCE)
        self.assertIn("material_claim_without_source", codes(issues))
        self.assertIn("unstructured_evidence", codes(issues))

    def test_normalize_handles_unicode_dashes_and_spaces(self):
        self.assertEqual(normalize("USD 29–53m"), "usd 29-53m")

    def test_no_claim_register_warns(self):
        issues = check_session_traceability({}, EVIDENCE)
        self.assertIn("no_claim_register", codes(issues))


if __name__ == "__main__":
    unittest.main()
