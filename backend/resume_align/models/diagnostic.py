"""Diagnostic report & tailoring result models."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Float, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class DiagnosticReport(Base):
    __tablename__ = "diagnostic_reports"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    star_score: Mapped[float] = mapped_column(Float, default=0.0)
    quant_score: Mapped[float] = mapped_column(Float, default=0.0)
    keyword_density: Mapped[dict] = mapped_column(JSONB, default=dict)
    skill_breadth: Mapped[dict] = mapped_column(JSONB, default=list)
    skill_depth: Mapped[dict] = mapped_column(JSONB, default=dict)
    issues: Mapped[dict] = mapped_column(JSONB, default=list)
    suggestions: Mapped[dict] = mapped_column(JSONB, default=list)
    raw_report: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class TailoringResult(Base):
    __tablename__ = "tailoring_results"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    job_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    original_sections: Mapped[dict] = mapped_column(JSONB, default=dict)
    tailored_sections: Mapped[dict] = mapped_column(JSONB, default=dict)
    missing_skills: Mapped[dict] = mapped_column(JSONB, default=list)
    changes_log: Mapped[dict] = mapped_column(JSONB, default=list)
    full_output: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
