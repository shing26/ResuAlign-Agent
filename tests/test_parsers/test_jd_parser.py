"""Tests for JD structurer module."""
from __future__ import annotations

import pytest


class TestJDStructurer:
    """Test JD parsing and structuring."""

    def test_md5_consistency(self):
        """Test that same text produces same MD5."""
        from resume_align.services.parsers.jd_parser import JDStructurer

        structurer = JDStructurer.__new__(JDStructurer)
        md5_1 = structurer.md5("same text")
        md5_2 = structurer.md5("same text")
        assert md5_1 == md5_2

    def test_md5_different(self):
        """Test that different texts produce different MD5."""
        from resume_align.services.parsers.jd_parser import JDStructurer

        structurer = JDStructurer.__new__(JDStructurer)
        md5_1 = structurer.md5("text a")
        md5_2 = structurer.md5("text b")
        assert md5_1 != md5_2
