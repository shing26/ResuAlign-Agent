"""Tests for the assertion checker (anti-hallucination guard)."""
from __future__ import annotations


class TestAssertionChecker:
    """Test anti-hallucination assertion logic."""

    def test_no_fabrication_passes(self):
        """Test that text with only original+JD skills passes."""
        from resume_align.shield.assertion_checker import AssertionChecker

        checker = AssertionChecker()
        result = checker.check(
            tailored_text="Built microservices with Python and Redis",
            original_skills={"Python", "Redis"},
            jd_skills={"microservices", "Kubernetes"},
        )
        assert result["passed"] is True
        assert len(result["fabricated_skills"]) == 0

    def test_fabrication_detected(self):
        """Test that fabricated skills are flagged."""
        from resume_align.shield.assertion_checker import AssertionChecker

        checker = AssertionChecker()
        result = checker.check(
            tailored_text="Built systems with Python, Go, and K8s",
            original_skills={"Python", "Java"},
            jd_skills={"Java"},
        )
        assert result["passed"] is False
        # Go and K8s are not in original or JD
        assert len(result["fabricated_skills"]) > 0

    def test_extract_entities(self):
        """Test that tech entities are correctly extracted from text."""
        from resume_align.shield.assertion_checker import AssertionChecker

        checker = AssertionChecker()
        entities = checker.extract_tech_entities(
            "I used Python, Django, and PostgreSQL daily"
        )
        assert "python" in entities
        assert "postgresql" in entities
