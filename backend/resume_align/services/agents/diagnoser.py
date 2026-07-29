"""Diagnoser Agent - Stage 1: Resume diagnostic."""

from __future__ import annotations

import logging
from typing import Any

from pydantic import BaseModel, Field

from resume_align.services.agents.base import BaseAgent
from resume_align.infra.llm import LLMClient

logger = logging.getLogger(__name__)


class ResumeInput(BaseModel):
    raw_text: str
    sections: list[dict[str, Any]] = Field(default_factory=list)


class SkillDepth(BaseModel):
    skill: str = ""
    years: int = 0
    proficiency: str = ""


class DiagnosticReport(BaseModel):
    star_score: float = Field(0.0, ge=0.0, le=1.0)
    quant_score: float = Field(0.0, ge=0.0, le=1.0)
    skill_breadth: list[str] = Field(default_factory=list)
    skill_depth: list[Any] = Field(default_factory=list)
    keyword_density: dict[str, Any] = Field(default_factory=dict)
    issues: list[Any] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    raw_report: str = Field(default="")


SYSTEM_PROMPT = (
    "You are a strict Resume Diagnostic Auditor, not a writer.\n\n"
    "Analyze the resume and return a JSON object with these exact fields:\n"
    "- star_score: number 0.0 to 1.0 (STAR compliance)\n"
    "- quant_score: number 0.0 to 1.0 (quantified metrics)\n"
    "- skill_breadth: list of technical skill strings\n"
    "- skill_depth: list of skills with context (strings or objects)\n"
    "- keyword_density: object mapping keywords to frequency\n"
    "- issues: list of problem descriptions (strings)\n"
    "- suggestions: list of actionable improvement tips\n"
    "- raw_report: full analysis text\n\n"
    "CRITICAL: Do NOT fabricate. Return flat JSON. No markdown, no fences."
)


class DiagnoserAgent(BaseAgent[ResumeInput, DiagnosticReport]):
    def __init__(self, llm: LLMClient) -> None:
        super().__init__(llm, name="Diagnoser")

    def system_prompt(self) -> str:
        return SYSTEM_PROMPT

    def output_model(self) -> type[DiagnosticReport]:
        return DiagnosticReport

    def _format_input(self, input_data: ResumeInput) -> str:
        parts = [f"=== Resume Text ===\n{input_data.raw_text}"]
        if input_data.sections:
            parts.append("=== Sections ===")
            for s in input_data.sections:
                parts.append(f'[{s.get("heading", "?")}]: {s.get("content", "")[:300]}')
        return "\n".join(parts)
