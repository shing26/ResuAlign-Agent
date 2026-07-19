"""JD Structurer: compress raw JD text into structured Pydantic JSON (70% size reduction)."""

from __future__ import annotations

import hashlib
import logging
from typing import Any

from pydantic import BaseModel, Field

from resume_align.llm import LLMClient, create_llm_client

logger = logging.getLogger(__name__)


class StructuredJD(BaseModel):
    """Compressed structured representation of a Job Description."""
    title: str = Field(default="", description="Job title")
    company: str = Field(default="", description="Company name")
    required_skills: list[str] = Field(
        default_factory=list,
        description="Must-have technical skills extracted from JD",
    )
    nice_to_have: list[str] = Field(
        default_factory=list,
        description="Bonus/preferred skills",
    )
    responsibilities: list[str] = Field(
        default_factory=list,
        description="Key responsibilities and duties",
    )
    seniority: str = Field(default="", description="Seniority level if mentioned")


JD_STRUCTURER_PROMPT = """\
You are a Job Description Structurer. Compress the following raw JD text into a structured JSON object.

Rules:
1. Extract ONLY what is explicitly stated - do not infer or add requirements.
2. Distinguish between "must-have" (required) and "nice-to-have" (preferred/plus).
3. Group similar skills together under a single canonical name.
4. Keep responsibilities concise but preserve technical details.
5. Output must be valid JSON matching the schema.

The goal is to reduce token volume by ~70% while preserving all factual requirements.
"""


class JDStructurer:
    """Parses raw JD text into a structured Pydantic model using LLM."""

    def __init__(self, llm: LLMClient | None = None) -> None:
        self.llm = llm or create_llm_client()

    async def structure(self, raw_jd: str) -> StructuredJD:
        """Compress raw JD into structured form."""
        logger.info("Structuring JD (%d chars)...", len(raw_jd))

        prompt_lines = [
            "=== Raw Job Description ===",
            raw_jd,
            "\nExtract and structure the JD requirements into the target JSON schema.",
        ]
        user_prompt = "\n".join(prompt_lines)

        result = await self.llm.generate_structured(
            system_prompt=JD_STRUCTURER_PROMPT,
            user_prompt=user_prompt,
            response_model=StructuredJD,
        )
        logger.info("JD structured: title=%s, skills=%d", result.title, len(result.required_skills))
        return result

    def md5(self, raw_jd: str) -> str:
        return hashlib.md5(raw_jd.encode("utf-8")).hexdigest()

    def to_context_dict(self, structured: StructuredJD) -> dict[str, Any]:
        """Convert structured JD to a dict for injection into agent prompts."""
        return {
            "title": structured.title,
            "company": structured.company,
            "seniority": structured.seniority,
            "required_skills": structured.required_skills,
            "nice_to_have": structured.nice_to_have,
            "responsibilities": structured.responsibilities,
        }
