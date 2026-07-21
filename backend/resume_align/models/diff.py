"""Structured diff models matching the spec exactly."""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class DiffType(StrEnum):
    MODIFY = "MODIFY"
    ADD = "ADD"
    DELETE = "DELETE"
    REORDER = "REORDER"


class ConfidenceLevel(StrEnum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class DiffItem(BaseModel):
    id: str = Field(default="", description="Unique ID e.g. diff_1")
    section: str = Field(default="", description="Resume section e.g. skills, project_0")
    type: DiffType = Field(default=DiffType.MODIFY)
    original_text: str | None = Field(None, description="Raw text to replace")
    proposed_text: str = Field(default="", description="Target text to insert")
    keywords_aligned: list[str] = Field(default_factory=list)
    reason: str = Field(default="", description="Explanation of change")
    confidence: ConfidenceLevel = Field(default=ConfidenceLevel.HIGH)


class DiffDelta(BaseModel):
    target_job_title: str = ""
    company_name: str | None = None
    match_score_before: int = Field(default=0, ge=0, le=100)
    match_score_after: int = Field(default=0, ge=0, le=100)
    summary: str = ""
    diff_items: list[DiffItem] = Field(default_factory=list)
