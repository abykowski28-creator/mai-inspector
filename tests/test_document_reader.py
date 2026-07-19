from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from agent.document_reader import build_evidence_pack
from agent.sanitizer import sanitize_text


class DocumentReaderTests(unittest.TestCase):
    def test_build_evidence_pack_reads_text_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = root / "project"
            output = root / "output"
            project.mkdir()
            (project / "brief.txt").write_text("Decision: launch pilot", encoding="utf-8")
            records = build_evidence_pack(project, output)
            self.assertEqual(len(records), 1)
            self.assertTrue((output / "evidence_pack.md").exists())
            self.assertTrue((output / "inventory.json").exists())


if __name__ == "__main__":
    unittest.main()


class SanitizerTests(unittest.TestCase):
    def test_sanitize_text_redacts_basic_sensitive_fields(self):
        email = "sample" + "@" + "example.invalid"
        text = f"Email {email} phone +971 50 123 4567 ACME Energy Marketing"
        sanitized, report = sanitize_text(
            text,
            redaction_map={"ACME Energy Marketing": "COUNTERPARTY_A"},
        )
        self.assertIn("[REDACTED_EMAIL]", sanitized)
        self.assertIn("[REDACTED_PHONE]", sanitized)
        self.assertIn("COUNTERPARTY_A", sanitized)
        self.assertGreaterEqual(report.replacements.get("EMAIL", 0), 1)
