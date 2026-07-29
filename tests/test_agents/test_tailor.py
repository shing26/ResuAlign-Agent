"""Tests for the Tailor agent."""
from __future__ import annotations


class TestTailorAgent:
    """Test TailorAgent structure and guardrails."""

    def test_system_prompt_contains_refusal(self):
        """Test system prompt contains refusal mechanism instructions."""
        from resume_align.services.agents.tailor import TAILOR_SYSTEM_PROMPT

        assert "ZERO FABRICATION" in TAILOR_SYSTEM_PROMPT
        assert "Refusal" in TAILOR_SYSTEM_PROMPT
        assert "Sliding Window" in TAILOR_SYSTEM_PROMPT

    def test_tailor_output_fields(self):
        """Test that TailorOutput has all required fields."""
        from resume_align.services.agents.tailor import TailorOutput

        output = TailorOutput(tailored_content="test")
        assert output.tailored_content == "test"
        assert output.refusal_triggered is False
        assert isinstance(output.missing_skills, list)
        assert isinstance(output.changes_log, list)
