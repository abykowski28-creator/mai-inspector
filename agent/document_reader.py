from __future__ import annotations

import csv
import json
import re
import zipfile
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable
from xml.etree import ElementTree as ET


SUPPORTED_EXTENSIONS = {
    ".txt",
    ".md",
    ".json",
    ".csv",
    ".docx",
    ".xlsx",
    ".pdf",
}


@dataclass
class DocumentRecord:
    path: str
    name: str
    extension: str
    size_bytes: int
    status: str
    text_chars: int
    excerpt: str
    error: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


def read_text_file(path: Path) -> str:
    data = path.read_bytes()
    for encoding in ("utf-8-sig", "utf-8", "utf-16", "cp1251"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def read_docx(path: Path) -> str:
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    chunks: list[str] = []
    with zipfile.ZipFile(path) as docx:
        xml = docx.read("word/document.xml")
    root = ET.fromstring(xml)
    for paragraph in root.findall(".//w:p", ns):
        text = "".join(t.text or "" for t in paragraph.findall(".//w:t", ns)).strip()
        if text:
            chunks.append(text)
    return "\n".join(chunks)


def read_xlsx(path: Path) -> str:
    try:
        import openpyxl  # type: ignore
    except Exception as exc:  # pragma: no cover - optional dependency
        raise RuntimeError("openpyxl is not available for xlsx extraction") from exc

    workbook = openpyxl.load_workbook(path, data_only=True, read_only=True)
    chunks: list[str] = []
    for sheet in workbook.worksheets:
        chunks.append(f"# Sheet: {sheet.title}")
        for row in sheet.iter_rows(max_row=80, values_only=True):
            values = [str(value) for value in row if value is not None]
            if values:
                chunks.append(" | ".join(values))
    return "\n".join(chunks)


def read_pdf(path: Path) -> str:
    try:
        from pypdf import PdfReader  # type: ignore
    except Exception as exc:  # pragma: no cover - optional dependency
        raise RuntimeError("pypdf is not available for pdf extraction") from exc

    reader = PdfReader(str(path))
    chunks: list[str] = []
    for page in reader.pages[:30]:
        chunks.append(page.extract_text() or "")
    return "\n".join(chunks)


def normalize_text(text: str) -> str:
    text = text.replace("\x00", "")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def iter_project_files(project_folder: Path) -> Iterable[Path]:
    for path in sorted(project_folder.rglob("*")):
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
            if any(part.startswith(".") for part in path.parts):
                continue
            yield path


def extract_document(path: Path, max_chars: int = 12000) -> tuple[str, str]:
    suffix = path.suffix.lower()
    if suffix in {".txt", ".md", ".json"}:
        text = read_text_file(path)
    elif suffix == ".csv":
        rows: list[str] = []
        with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as handle:
            reader = csv.reader(handle)
            for row in list(reader)[:200]:
                rows.append(" | ".join(row))
        text = "\n".join(rows)
    elif suffix == ".docx":
        text = read_docx(path)
    elif suffix == ".xlsx":
        text = read_xlsx(path)
    elif suffix == ".pdf":
        text = read_pdf(path)
    else:
        raise RuntimeError(f"Unsupported extension: {suffix}")

    text = normalize_text(text)
    if len(text) > max_chars:
        return text[:max_chars], f"truncated to {max_chars} chars"
    return text, "ok"


def _coverage_note(coverage: dict) -> list[str]:
    """A human/LLM-visible header that makes dropped/truncated content explicit."""
    lines = [
        "## Extraction Coverage",
        "",
        f"- Supported files found in project: {coverage['supported_files_found']}",
        f"- Files included in this pack: {coverage['files_included']}",
        f"- Files truncated to {coverage['max_chars_per_file']} chars: {len(coverage['files_truncated'])}",
        f"- Files SKIPPED (beyond the {coverage['max_files']}-file cap, NOT read): {len(coverage['files_skipped_over_cap'])}",
    ]
    if coverage["files_truncated"]:
        lines.append("  - truncated: " + "; ".join(coverage["files_truncated"][:20]))
    if coverage["files_skipped_over_cap"]:
        lines.append("  - skipped: " + "; ".join(coverage["files_skipped_over_cap"][:20]))
    if coverage["files_truncated"] or coverage["files_skipped_over_cap"]:
        lines.append("")
        lines.append(
            "> WARNING: some source content is not in this pack. A claim that relies on "
            "skipped or truncated text cannot be verified here — mark such claims unverified."
        )
    lines.append("")
    return lines


def build_evidence_pack(
    project_folder: Path,
    output_dir: Path,
    max_files: int = 40,
    max_chars_per_file: int = 12000,
) -> list[DocumentRecord]:
    output_dir.mkdir(parents=True, exist_ok=True)
    records: list[DocumentRecord] = []

    all_files = list(iter_project_files(project_folder))
    selected = all_files[:max_files]
    skipped = all_files[max_files:]
    truncated_names: list[str] = []

    body_lines: list[str] = []
    for index, path in enumerate(selected, start=1):
        try:
            text, status = extract_document(path, max_chars=max_chars_per_file)
            error = ""
        except Exception as exc:
            text = ""
            status = "error"
            error = str(exc)

        rel = str(path.relative_to(project_folder))
        if "truncated" in status:
            truncated_names.append(rel)
        excerpt = text[:max_chars_per_file]
        records.append(
            DocumentRecord(
                path=rel,
                name=path.name,
                extension=path.suffix.lower(),
                size_bytes=path.stat().st_size,
                status=status,
                text_chars=len(text),
                excerpt=excerpt,
                error=error,
            )
        )
        body_lines.extend(
            [
                f"## Document {index}: {rel}",
                "",
                f"- Status: {status}",
                f"- Size: {path.stat().st_size} bytes",
                "",
                "```text",
                excerpt if excerpt else f"[No text extracted: {error}]",
                "```",
                "",
            ]
        )

    coverage = {
        "supported_files_found": len(all_files),
        "files_included": len(selected),
        "files_truncated": truncated_names,
        "files_skipped_over_cap": [str(p.relative_to(project_folder)) for p in skipped],
        "max_files": max_files,
        "max_chars_per_file": max_chars_per_file,
    }

    evidence_lines = [
        "# MAI Evidence Pack",
        "",
        f"Project folder: `{project_folder}`",
        "",
    ]
    evidence_lines.extend(_coverage_note(coverage))
    evidence_lines.extend(body_lines)

    (output_dir / "inventory.json").write_text(
        json.dumps([record.to_dict() for record in records], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (output_dir / "extraction_coverage.json").write_text(
        json.dumps(coverage, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (output_dir / "evidence_pack.md").write_text("\n".join(evidence_lines), encoding="utf-8")
    return records
