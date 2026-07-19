from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from agent.engine_runner import VENDORED_ENGINE, resolve_engine_path, run_engine
from agent.engine.mai_decision_lab_v2_1 import analyze_session, visual_bar

REPO_ROOT = Path(__file__).resolve().parent.parent
PUBLIC_SAMPLE = REPO_ROOT / "sample_data" / "buildweek_investment_review_session.json"


class EngineRunnerTests(unittest.TestCase):
    def test_vendored_engine_exists(self):
        self.assertTrue(
            VENDORED_ENGINE.exists(),
            "Vendored engine must ship with the repo for reproducible scoring.",
        )

    def test_vendored_engine_is_preferred(self):
        path, source = resolve_engine_path(REPO_ROOT / "does_not_exist")
        self.assertEqual(source, "vendored")
        self.assertEqual(path, VENDORED_ENGINE)

    def test_public_sample_reproduces_and_is_stamped(self):
        self.assertTrue(PUBLIC_SAMPLE.exists(), f"Public sample missing: {PUBLIC_SAMPLE}")

        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "buildweek_sample"
            result = run_engine(
                workspace=REPO_ROOT,
                session_path=PUBLIC_SAMPLE,
                output_dir=out_dir,
            )

            self.assertEqual(result["stability_score"], 61)
            self.assertEqual(result["decision_outcome"], "CONDITIONAL GO")
            self.assertEqual(
                result["decision_architecture_diagnosis"],
                "Moderate thesis / weak decision architecture",
            )

            prov = result.get("provenance")
            self.assertIsNotNone(prov, "result.json must carry a provenance block")
            for key in (
                "generated_at",
                "agent_version",
                "engine_version",
                "engine_sha256",
                "input_session_sha256",
            ):
                self.assertIn(key, prov)
            self.assertEqual(prov["engine_version"], "2.1.0")

            written = json.loads((out_dir / "result.json").read_text(encoding="utf-8"))
            self.assertEqual(written["stability_score"], 61)
            self.assertIn("## Provenance", (out_dir / "report.md").read_text(encoding="utf-8"))


    def test_catastrophic_session_can_reach_no_go(self):
        session = {
            "session_id": "catastrophic-no-go-regression",
            "session_date": "2026-07-19",
            "decision_brief": {"decision": "Approve an irreversible high-stakes commitment?"},
            "thesis_strength": "weak",
            "critical_breakpoint_proximity": "immediate",
            "system_map": {
                "components": [
                    {
                        "component": f"critical component {index}",
                        "criticality": "critical",
                        "status": "pending",
                        "risk_level": "critical",
                    }
                    for index in range(20)
                ],
                "critical_assumptions": [
                    {
                        "assumption": f"critical assumption {index}",
                        "status": "unverified",
                        "criticality": "critical",
                    }
                    for index in range(20)
                ],
            },
            "domain_analysis": [
                {"domain": f"domain {index}", "instability_level": "critical"}
                for index in range(20)
            ],
            "semantic_risks": [
                {"risk": f"semantic risk {index}", "severity": "critical"}
                for index in range(20)
            ],
            "claim_register": [
                {
                    "claim": f"critical claim {index}",
                    "status": "unverified",
                    "importance": "critical",
                    "source": "synthetic",
                }
                for index in range(20)
            ],
            "stress_scenarios": [
                {"scenario": f"stress scenario {index}", "system_impact": "catastrophic"}
                for index in range(20)
            ],
            "deviations": [
                {
                    "deviation": f"critical deviation {index}",
                    "severity": "critical",
                    "likelihood": "critical",
                    "domain": "synthetic",
                    "affected_node": "same_node",
                    "execution_window": "same_window",
                    "fixable": "No",
                }
                for index in range(20)
            ],
            "critical_breakpoint": "Do not proceed under catastrophic evidence failure.",
            "failure_mechanisms": ["Systemic evidence failure"],
            "decision_gates": [
                {
                    "gate": "Stop commitment",
                    "required_evidence": "Independent validation across all critical layers.",
                    "owner": "Decision authority",
                    "status": "open",
                    "criticality": "critical",
                }
            ],
        }

        result = analyze_session(session)

        self.assertLess(result.stability_score, 40)
        self.assertEqual(result.outcome, "NO-GO")
        self.assertGreater(result.scoring_breakdown.systemic_overload, 0)

    def test_visual_bar_uses_readable_block_symbols(self):
        expected = chr(0x2588) * 2 + chr(0x2591) * 2 + ' 50/100'
        self.assertEqual(visual_bar(50, width=4), expected)

    def test_same_input_is_reproducible(self):
        with tempfile.TemporaryDirectory() as tmp:
            a = run_engine(REPO_ROOT, PUBLIC_SAMPLE, Path(tmp) / "a")
            b = run_engine(REPO_ROOT, PUBLIC_SAMPLE, Path(tmp) / "b")
        self.assertEqual(a["stability_score"], b["stability_score"])
        self.assertEqual(a["decision_outcome"], b["decision_outcome"])
        self.assertEqual(
            a["provenance"]["input_session_sha256"],
            b["provenance"]["input_session_sha256"],
        )
        self.assertEqual(
            a["provenance"]["engine_sha256"],
            b["provenance"]["engine_sha256"],
        )


if __name__ == "__main__":
    unittest.main()
