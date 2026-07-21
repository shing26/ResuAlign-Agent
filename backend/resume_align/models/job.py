"""Job description & embedding models + JobContext."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel
from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, Float, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class JobDescription(Base):
    __tablename__ = "job_descriptions"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    raw_text: Mapped[str] = mapped_column(Text)
    structured: Mapped[dict] = mapped_column(JSONB, default=dict)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    company: Mapped[str | None] = mapped_column(String(255), nullable=True)
    required_skills: Mapped[dict] = mapped_column(JSONB, default=list)
    nice_to_have: Mapped[dict] = mapped_column(JSONB, default=list)
    responsibilities: Mapped[dict] = mapped_column(JSONB, default=list)
    md5_fingerprint: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class JobEmbedding(Base):
    __tablename__ = "job_embeddings"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    embedding: Mapped[list[float]] = mapped_column(Vector(1536))
    similarity: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class JobContext(BaseModel):
    """Pydantic model for runtime context (not DB)."""
    raw_text: str = ""
    title: str = ""
    company: str = ""
