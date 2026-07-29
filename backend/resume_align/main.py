"""FastAPI application entry point."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from resume_align.core.config import settings
from resume_align.api.v1.routes import router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle."""
    logger.info("ResuAlign-Agent starting up...")
    yield
    logger.info("ResuAlign-Agent shutting down...")


app = FastAPI(
    title="ResuAlign-Agent",
    description="Anti-hallucination resume optimization pipeline",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}


if __name__ == "__main__":
    uvicorn.run(
        "resume_align.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.env == "development",
    )
