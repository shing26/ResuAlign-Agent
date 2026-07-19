"""Tailor Agent - Stage 2: JD-aligned resume tailoring with anti-hallucination guardrails."""

from __future__ import annotations

import logging
from typing import Any

from typing import Any
from pydantic import BaseModel, Field

from resume_align.agents.base import BaseAgent
from resume_align.llm import LLMClient

logger = logging.getLogger(__name__)


class TailorInput(BaseModel):
    """Input for the Tailor agent."""
    resume_section: dict[str, Any] = Field(..., description="One resume section block")
    section_heading: str = ""
    jd_requirements: dict[str, Any] = Field(default_factory=dict)
    diagnostic_hints: list[str] = Field(default_factory=list)
    original_skills: list[str] = Field(default_factory=list, description="Skills from original resume")


class TailorOutput(BaseModel):
    """Structured output from the Tailor Agent."""
    tailored_content: str = Field(..., description="Optimized section text")
    changes_log: list[Any] = Field(
        default_factory=list,
        description="List of changes: {type: 'rewrite'|'rephrase', reason: ..., before: ..., after: ...}",
    )
    missing_skills: list[str] = Field(
        default_factory=list,
        description="JD-required skills absent from original resume",
    )
    refusal_triggered: bool = Field(
        default=False,
        description="True if agent refused to fabricate a missing skill",
    )


TAILOR_SYSTEM_PROMPT = """\
You are a **Strict Resume Tailoring Engineer**, not a creative writer.

Your job is to align a resume section to a target job description (JD) while following **ABSOLUTE GROUND RULES**:

## CORE RULES (Violation = System Failure)

1. **ZERO FABRICATION**: Never add skills, technologies, or metrics that do not exist in the original resume. If the JD requires "Go" or "K8s" and the resume does not mention them, you MUST NOT add them.
2. **Semantic Bridging ONLY**: You may rephrase existing content to use terminology that better resonates with the target JD, but the factual ground truth must remain identical.
3. **Refusal Mechanism**: If a hard requirement from the JD has zero factual basis in the resume, add it to `missing_skills` and set `refusal_triggered=True`.
4. **Sliding Window Focus**: Work only with the single section provided. Do not import context from other sections.
5. **Preserve Quantified Metrics**: Keep all numbers, percentages, and metrics exactly as written.

## PRIORITY
- Factual fidelity > Terminology alignment > Creative phrasing
- When in doubt, keep the original text unchanged.

Return valid JSON matching the TailorOutput schema.
"""


class TailorAgent(BaseAgent[TailorInput, TailorOutput]):
    """Stage 2 agent: tailors a single resume section to match JD requirements."""

    def __init__(self, llm: LLMClient) -> None:
        super().__init__(llm, name="Tailor")

    def system_prompt(self) -> str:
        return TAILOR_SYSTEM_PROMPT

    def output_model(self) -> type[TailorOutput]:
        return TailorOutput

    def _format_input(self, input_data: TailorInput) -> str:
        parts = [
            f"=== Section: {input_data.section_heading} ===",
            input_data.resume_section.get("content", str(input_data.resume_section)),
        ]
        if input_data.jd_requirements:
            parts.append(f"\n=== JD Requirements ===")
            parts.append(input_data.jd_requirements.get("raw", str(input_data.jd_requirements)))
        if input_data.diagnostic_hints:
            parts.append(f"\n=== Diagnostic Hints ===")
            parts.append("\n".join(f"- {h}" for h in input_data.diagnostic_hints))
        if input_data.original_skills:
            parts.append(f"\n=== Original Resume Skills ===")
            parts.append(", ".join(input_data.original_skills))
        return "\n".join(parts)
