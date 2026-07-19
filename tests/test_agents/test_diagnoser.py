"""Tests for the Diagnoser agent."""
from __future__ import annotations


class TestDiagnoserAgent:
    """Test DiagnoserAgent structure and prompts."""

    def test_system_prompt_contains_constraints(self):
        """Test system prompt contains anti-hallucination constraints."""
        from resume_align.agents.diagnoser import SYSTEM_PROMPT

        assert "STAR" in SYSTEM_PROMPT
        assert "quant" in SYSTEM_PROMPT.lower()
        assert "Do NOT fabricate" in SYSTEM_PROMPT

    def test_output_model_has_required_fields(self):
        """Test that DiagnosticReport has all required fields."""
        from resume_align.agents.diagnoser import DiagnosticReport

        model = DiagnosticReport(star_score=0.5, quant_score=0.5)
        assert 0.0 <= model.star_score <= 1.0
        assert 0.0 <= model.quant_score <= 1.0
        assert hasattr(model, "skill_breadth")
        assert hasattr(model, "issues")
        assert hasattr(model, "suggestions")
