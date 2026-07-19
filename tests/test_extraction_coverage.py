from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from agent.document_reader import build_evidence_pack
from agent.quality_assurance import _check_extraction_coverage, QualityIssue


class ExtractionCoverageTests(unittest.TestCase):
    def test_skipped_and_truncated_are_recorded_and_visible(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "proj"
            proj.mkdir()
            # three files; one is long enough to be truncated
            (proj / "a.txt").write_text("alpha content", encoding="utf-8")
            (proj / "b.txt").write_text("beta content", encoding="utf-8")
            (proj / "c.txt").write_text("x" * 50, encoding="utf-8")
            out = Path(tmp) / "out"

            build_evidence_pack(proj, out, max_files=2, max_chars_per_file=10)

            cov = json.loads((out / "extraction_coverage.json").read_text(encoding="utf-8"))
            self.assertEqual(cov["supported_files_found"], 3)
            self.assertEqual(cov["files_included"], 2)
            self.assertEqual(len(cov["files_skipped_over_cap"]), 1)        # c.txt dropped
            self.assertIn("c.txt", cov["files_skipped_over_cap"][0])
            self.assertTrue(cov["files_truncated"])                        # a or b truncated at 10 chars

            pack = (out / "evidence_pack.md").read_text(encoding="utf-8")
            self.assertIn("## Extraction Coverage", pack)
            self.assertIn("WARNING: some source content is not in this pack", pack)

    def test_qa_warns_on_skipped_and_truncated(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            (out / "extraction_coverage.json").write_text(json.dumps({
                "supported_files_found": 45, "files_included": 40,
                "files_truncated": ["big.docx"],
                "files_skipped_over_cap": ["x41.pdf", "x42.pdf", "x43.pdf", "x44.pdf", "x45.pdf"],
                "max_files": 40, "max_chars_per_file": 12000,
            }), encoding="utf-8")
            issues: list[QualityIssue] = []
            _check_extraction_coverage(out, issues)
            codes = {i.code for i in issues}
            self.assertIn("evidence_files_skipped", codes)
            self.assertIn("evidence_files_truncated", codes)
            self.assertTrue(all(i.severity == "warning" for i in issues))

    def test_qa_silent_when_no_coverage_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            issues: list[QualityIssue] = []
            _check_extraction_coverage(Path(tmp), issues)
            self.assertEqual(issues, [])


if __name__ == "__main__":
    unittest.main()
