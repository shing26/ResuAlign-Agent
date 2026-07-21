"""Pydantic request/response schemas for the REST API."""

from __future__ import annotations

import uuid
from datetime import datetime

from typing import Any
from pydantic import BaseModel, Field



class StageConfig(BaseModel):
    provider: str | None = None
    api_key: str | None = None
    model: str | None = None
    base_url: str | None = None


class JobAnalysisRequest(BaseModel):
    """Request payload: upload a resume and optionally a JD for analysis."""

    resume_text: str = Field(..., description="Raw text extracted from the resume PDF")
    jd_text: str | None = Field(None, description="Job description text, optional")
    resume_md5: str | None = Field(None, description="MD5 fingerprint for cache lookup")
    jd_md5: str | None = Field(None, description="MD5 fingerprint for cache lookup")
    # Simple mode: one model for all stages
    provider: str | None = Field(None, description="LLM provider override")
    api_key: str | None = Field(None, description="API key override")
    model: str | None = Field(None, description="Model name override")
    base_url: str | None = Field(None, description="Base URL override")
    # Advanced mode: per-stage model routing
    jd_provider: StageConfig | None = Field(None, description="JD structuring stage config")
    diagnoser_provider: StageConfig | None = Field(None, description="Diagnosis stage config")
    tailor_provider: StageConfig | None = Field(None, description="Tailoring stage config")


class DiagnosticResultResponse(BaseModel):
    """Result of Stage 1: resume diagnostic."""

    report_id: str
    star_score: float = Field(..., ge=0.0, le=1.0)
    quant_score: float = Field(..., ge=0.0, le=1.0)
    skill_breadth: list[str]
    skill_depth: dict[str, int]
    issues: list[Any]
    suggestions: list[str]
    raw_report: str


class TailoringResultResponse(BaseModel):
    """Result of Stage 2: JD-aligned tailoring."""

    result_id: str
    original_sections: list[dict]
    tailored_sections: list[dict]
    missing_skills: list[str]
    changes_log: list[Any]
    full_output: str


class JobAnalysisResponse(BaseModel):
    """Complete pipeline response (both stages)."""

    diagnostic: DiagnosticResultResponse
    tailoring: TailoringResultResponse | None = None
    cached: bool = False
    processing_time_ms: int = 0


class SessionConfigRequest(BaseModel):
    provider: str
    api_key: str
    model: str | None = None
    base_url: str | None = None


class SessionConfigResponse(BaseModel):
    session_id: str
    provider: str
    model: str
    masked_key: str


class TailorRequest(BaseModel):
    resume_text: str
    job_text: str
    company_name: str = ""
    job_title: str = ""


class SessionTestRequest(BaseModel):
    session_id: str


class ErrorResponse(BaseModel):
    """Standard error response."""

    detail: str
    error_code: str | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
