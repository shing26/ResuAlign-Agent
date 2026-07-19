"""Tests for PDF parser module."""
from __future__ import annotations


class TestPDFParser:
    """Test PDF parsing and section splitting."""

    def test_section_split(self, sample_resume_text: str):
        """Test that resume text is split into correct sections."""
        from resume_align.parsers.pdf_parser import PDFParser

        parser = PDFParser()
        sections = parser._split_sections(sample_resume_text)

        assert len(sections) >= 3
        headings = [s["heading"] for s in sections]
        assert any("Skills" in h or "Technical Skills" in h for h in headings)
        assert any("Experience" in h or "Work Experience" in h for h in headings)

    def test_empty_text_returns_header_only(self):
        """Test that empty text returns a single section."""
        from resume_align.parsers.pdf_parser import PDFParser

        parser = PDFParser()
        sections = parser._split_sections("")
        assert len(sections) == 1
        assert sections[0]["heading"] == "header"
