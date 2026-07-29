"""PDF Parser: extract text from resume PDFs using PyMuPDF, with OCR fallback."""

from __future__ import annotations

import hashlib
import logging
import re
from typing import Any

import fitz  # PyMuPDF

from resume_align.core.config import settings

logger = logging.getLogger(__name__)


class ResumeParseResult:
    """Result of parsing a resume PDF."""

    def __init__(
        self,
        raw_text: str,
        sections: list[dict[str, Any]],
        md5_fingerprint: str,
        page_count: int,
        ocr_fallback_used: bool = False,
    ) -> None:
        self.raw_text = raw_text
        self.sections = sections
        self.md5_fingerprint = md5_fingerprint
        self.page_count = page_count
        self.ocr_fallback_used = ocr_fallback_used


# Markdown headings used in resumes
SECTION_HEADINGS = re.compile(
    r"^(#{1,3}\s+)?((工作经验|教育背景|专业技能|项目经验|工作经历|"
    r"实习经历|个人项目|开源贡献|证书|语言|自我介绍|个人总结|"
    r"关于我|Work Experience|Education|Skills|Projects|"
    r"Experience|Internship|Open Source|Certifications|Languages|"
    r"Summary|Professional Experience|Technical Skills|"
    r"Employment History|Project Experience))",
    re.IGNORECASE | re.MULTILINE,
)


class PDFParser:
    """Extract and structure resume text from PDF files."""

    def parse(self, file_path: str) -> ResumeParseResult:
        """Parse a PDF file and return structured result."""
        doc = fitz.open(file_path)
        page_count = len(doc)
        raw_text = ""

        for page in doc:
            page_text = page.get_text()
            raw_text += page_text + "\n\n"

        doc.close()

        # If text extraction yields too little content, try OCR fallback
        if len(raw_text.strip()) < 100 and settings.ocr_fallback_enabled:
            logger.info("Low text yield (%d chars), attempting OCR fallback", len(raw_text.strip()))
            raw_text = self._ocr_extract(file_path)

        sections = self._split_sections(raw_text)
        md5_fingerprint = hashlib.md5(raw_text.encode("utf-8")).hexdigest()

        return ResumeParseResult(
            raw_text=raw_text,
            sections=sections,
            md5_fingerprint=md5_fingerprint,
            page_count=page_count,
            ocr_fallback_used=len(raw_text.strip()) < 100 and settings.ocr_fallback_enabled,
        )

    def parse_bytes(self, content: bytes, filename: str = "resume.pdf") -> ResumeParseResult:
        """Parse a PDF from raw bytes (e.g., upload)."""
        import tempfile

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        try:
            return self.parse(tmp_path)
        finally:
            import os
            os.unlink(tmp_path)

    def _split_sections(self, text: str) -> list[dict[str, Any]]:
        """Split resume text into sections based on Markdown-style headings."""
        lines = text.split("\n")
        sections: list[dict[str, Any]] = []
        current_heading = "header"
        current_content: list[str] = []

        section_order = 0
        for line in lines:
            match = SECTION_HEADINGS.match(line.strip())
            if match:
                if current_content:
                    sections.append({
                        "heading": current_heading,
                        "content": "\n".join(current_content).strip(),
                        "order": section_order,
                    })
                    section_order += 1
                # Extract clean heading (drop markdown markers)
                raw_heading = match.group(0).strip()
                current_heading = re.sub(r"^#{1,3}\s+", "", raw_heading)
                current_content = []
            else:
                current_content.append(line)

        # Last section
        if current_content:
            sections.append({
                "heading": current_heading,
                "content": "\n".join(current_content).strip(),
                "order": section_order,
            })

        return sections

    def _ocr_extract(self, file_path: str) -> str:
        """OCR fallback using Tesseract (if available)."""
        try:
            import subprocess
            result = subprocess.run(
                ["tesseract", file_path, "stdout", "-l", settings.ocr_language],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode == 0:
                logger.info("OCR extraction successful")
                return result.stdout
            else:
                logger.warning("OCR failed: %s", result.stderr)
                return ""
        except FileNotFoundError:
            logger.warning("Tesseract not installed; OCR fallback unavailable")
            return ""
        except Exception as exc:
            logger.error("OCR error: %s", exc)
            return ""


def parse_pdf_resume(file_content: bytes, filename: str = "resume.pdf") -> str:
    """Standalone convenience function: parse PDF bytes to raw text."""
    parser = PDFParser()
    result = parser.parse_bytes(file_content, filename)
    return result.raw_text

