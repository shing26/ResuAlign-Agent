"""MCP Server: expose ResuAlign-Agent tools via Model Context Protocol."""

from __future__ import annotations

import json
import logging
from typing import Any

from mcp.server.fastmcp import FastMCP

from resume_align.core.config import settings
from resume_align.infra.llm import create_llm_client
from resume_align.services.agents.diagnoser import DiagnoserAgent, ResumeInput
from resume_align.services.agents.tailor import TailorAgent, TailorInput
from resume_align.shield.assertion_checker import AssertionChecker

logger = logging.getLogger(__name__)


def create_mcp_server() -> FastMCP:
    """Create and configure the MCP server with ResuAlign tools."""
    mcp = FastMCP("ResuAlign-Agent", log_level="INFO")

    llm = create_llm_client()
    diagnoser = DiagnoserAgent(llm)
    tailor = TailorAgent(llm)
    checker = AssertionChecker()

    @mcp.tool()
    async def diagnose_resume(
        resume_text: str,
        sections: list[dict[str, Any]] | None = None,
    ) -> str:
        """Analyze a resume for STAR compliance, quant metrics, and skill breadth/depth.

        Args:
            resume_text: Full raw text of the resume
            sections: Optional list of structured resume sections
        """
        input_data = ResumeInput(
            raw_text=resume_text,
            sections=sections or [],
        )
        report = await diagnoser.run(input_data)
        return json.dumps(report.model_dump(), indent=2, ensure_ascii=False)

    @mcp.tool()
    async def tailor_resume_section(
        resume_section: dict[str, Any],
        section_heading: str,
        jd_requirements: dict[str, Any],
        original_skills: list[str],
        diagnostic_hints: list[str] | None = None,
    ) -> str:
        """Tailor a single resume section to match target JD requirements.

        Uses Sliding Window Alignment: processes one section at a time.
        Anti-hallucination guard: refuses to fabricate skills not in the original resume.

        Args:
            resume_section: Dict with 'heading' and 'content' keys
            section_heading: Name of the section (e.g., "Project Experience")
            jd_requirements: Dict with JD structured requirements
            original_skills: List of skills present in the original resume
            diagnostic_hints: Optional hints from the diagnoser stage
        """
        input_data = TailorInput(
            resume_section=resume_section,
            section_heading=section_heading,
            jd_requirements=jd_requirements,
            diagnostic_hints=diagnostic_hints or [],
            original_skills=original_skills,
        )
        result = await tailor.run(input_data)

        # Run assertion check
        all_original = set(original_skills)
        all_jd = set(jd_requirements.get("required_skills", []))
        check_result = checker.check(
            tailored_text=result.tailored_content,
            original_skills=all_original,
            jd_skills=all_jd,
        )

        output = result.model_dump()
        output["assertion_check"] = check_result
        return json.dumps(output, indent=2, ensure_ascii=False)

    return mcp


def run_mcp_server() -> None:
    """Entry point to run the MCP server (stdio transport for Claude Desktop / Cursor)."""
    mcp = create_mcp_server()
    logger.info("Starting ResuAlign MCP server (stdio transport)...")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    run_mcp_server()
