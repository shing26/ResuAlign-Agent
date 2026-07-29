"""Pipeline orchestrator: ties Diagnoser + Tailor + Shield into one async flow."""

from __future__ import annotations

import hashlib
import logging
import time

from resume_align.infra.llm import create_llm_client
from resume_align.services.parsers.pdf_parser import PDFParser, ResumeParseResult
from resume_align.services.parsers.jd_parser import JDStructurer, StructuredJD
from resume_align.services.agents.diagnoser import DiagnoserAgent, DiagnosticReport, ResumeInput
from resume_align.services.agents.tailor import TailorAgent, TailorOutput, TailorInput
from resume_align.shield.assertion_checker import AssertionChecker
from resume_align.domain.diff import ConfidenceLevel
from resume_align.infra.redis_cache import RedisCache

logger = logging.getLogger(__name__)
MAX_TAILOR_RETRIES = 2
MAX_TAILOR_RETRIES = 2


class PipelineResult:
    def __init__(self, diagnostic, tailoring=None, cached=False, processing_time_ms=0, missing_skills=None, had_fabrication=False):
        self.diagnostic = diagnostic
        self.tailoring = tailoring
        self.cached = cached
        self.processing_time_ms = processing_time_ms
        self.missing_skills = missing_skills or []
        self.had_fabrication = had_fabrication


class ResumePipeline:
    def __init__(self):
        llm = create_llm_client()
        self.pdf_parser = PDFParser()
        self.jd_structurer = JDStructurer(llm)
        self.diagnoser = DiagnoserAgent(llm)
        self.tailor = TailorAgent(llm)
        self.checker = AssertionChecker()
        self._section_memory: list[str] = []
        self.cache = RedisCache()

    async def initialize(self):
        await self.cache.connect()

    async def run(self, resume_content, jd_text=None, filename="resume.pdf", llm_configs=None, event_callback=None):
        start_time = time.monotonic()
        if isinstance(resume_content, bytes):
            parse_result = self.pdf_parser.parse_bytes(resume_content, filename)
        else:
            md5 = hashlib.md5(resume_content.encode("utf-8")).hexdigest()
            sections = self.pdf_parser._split_sections(resume_content)
            parse_result = ResumeParseResult(raw_text=resume_content, sections=sections, md5_fingerprint=md5, page_count=0)
        logger.info("Parsed: %d chars, %d sections, md5=%s", len(parse_result.raw_text), len(parse_result.sections), parse_result.md5_fingerprint[:8])
        if event_callback:
            await event_callback({"event": "stage", "data": {"stage": "parsing", "progress": 15, "message": f"Parsed {len(parse_result.sections)} sections"}})

        jd_md5 = self.jd_structurer.md5(jd_text) if jd_text else None
        cached_result = await self.cache.get(parse_result.md5_fingerprint, jd_md5)
        if cached_result:
            elapsed = int((time.monotonic() - start_time) * 1000)
            return PipelineResult(diagnostic=DiagnosticReport(**cached_result["diagnostic"]), cached=True, processing_time_ms=elapsed)

        if event_callback:
            await event_callback({"event": "stage", "data": {"stage": "diagnosing", "progress": 30, "message": "Running resume diagnosis..."}})
        resume_input = ResumeInput(raw_text=parse_result.raw_text, sections=parse_result.sections)
        diagnostic_report = await self.diagnoser.run(resume_input)
        logger.info("Diagnosis: STAR=%.2f, Quant=%.2f", diagnostic_report.star_score, diagnostic_report.quant_score)
        if event_callback:
            await event_callback({"event": "result", "data": {"type": "diagnostic", "content": diagnostic_report.model_dump()}})
            await event_callback({"event": "stage", "data": {"stage": "jd_structuring", "progress": 45, "message": "Analyzing job requirements..."}})

        tailored_results = None
        missing_skills = []
        had_fabrication = False

        if jd_text:
            jd_llm = self._make_stage_client("jd_structurer", llm_configs)
            diag_llm = self._make_stage_client("diagnoser", llm_configs)
            tailor_llm = self._make_stage_client("tailor", llm_configs)

            if jd_llm:
                self.jd_structurer = JDStructurer(jd_llm)
            if diag_llm:
                self.diagnoser = DiagnoserAgent(diag_llm)
            if tailor_llm:
                self.tailor = TailorAgent(tailor_llm)

            structured_jd = await self.jd_structurer.structure(jd_text)
            jd_ctx = self.jd_structurer.to_context_dict(structured_jd)
            logger.info("JD structured: %d required skills", len(structured_jd.required_skills))
            original_skills = set(diagnostic_report.skill_breadth)
            tailored_results = []
            if event_callback:
                await event_callback({"event": "stage", "data": {"stage": "tailoring", "progress": 60, "message": f"Optimizing {len(parse_result.sections)} sections..."}})

            for section in parse_result.sections:
                sr = await self._tailor_section_with_retry(section, jd_ctx, original_skills, set(structured_jd.required_skills), diagnostic_report.suggestions)
                tailored_results.append(sr["output"])
            if event_callback:
                dd = sr["output"].diff_delta
                await event_callback({"event": "progress", "data": {"section": len(tailored_results), "total": len(parse_result.sections), "content": sr["output"].tailored_content, "missing_skills": sr["missing_skills"], "diff_delta": dd.model_dump() if dd else None}})
                missing_skills.extend(sr["missing_skills"])
                if sr["had_fabrication"]:
                    had_fabrication = True
            missing_skills = list(set(missing_skills))

        cache_data = {"diagnostic": diagnostic_report.model_dump(), "tailoring": [r.model_dump() for r in tailored_results] if tailored_results else None, "missing_skills": missing_skills}
        await self.cache.set(parse_result.md5_fingerprint, cache_data, jd_md5)
        elapsed = int((time.monotonic() - start_time) * 1000)
        tailoring_data = None
        if event_callback:
            tailoring_data = [r.model_dump() for r in tailored_results] if tailored_results else None
        all_diffs = []
        if tailoring_data:
            for t in tailoring_data:
                if t.get("diff_delta") and t["diff_delta"].get("diffs"):
                    all_diffs.extend(t["diff_delta"]["diffs"])
        if event_callback:
            await event_callback({"event": "complete", "data": {"diagnostic": diagnostic_report.model_dump(), "tailoring": tailoring_data, "diff_delta": {"diffs": all_diffs, "missing_skills": missing_skills, "summary": ""}, "missing_skills": missing_skills, "processing_time_ms": elapsed}})
        return PipelineResult(diagnostic=diagnostic_report, tailoring=tailored_results, processing_time_ms=elapsed, missing_skills=missing_skills, had_fabrication=had_fabrication)

    async def _tailor_section_with_retry(self, section, jd_ctx, original_skills, jd_skills, diagnostic_suggestions):
        retry_hints = list(diagnostic_suggestions)
        if self._section_memory:
            retry_hints.append("Previous sections: " + " | ".join(self._section_memory[-3:]))
        for attempt in range(MAX_TAILOR_RETRIES + 1):
            tailor_input = TailorInput(resume_section=section, section_heading=section.get("heading", ""), jd_requirements=jd_ctx, diagnostic_hints=retry_hints, original_skills=list(original_skills))
            result = await self.tailor.run(tailor_input)
            assertion = self.checker.check(tailored_text=result.tailored_content, original_skills=original_skills, jd_skills=jd_skills)
            if assertion["passed"]:
                # Update diff item confidence based on assertion
                if result.diff_delta:
                    for diff_item in result.diff_delta.diff_items:
                        diff_item = self.checker.check_diff(diff_item, original_skills, jd_skills)
                    # Auto-fix: if ALL diffs are LOW (fabrication risk), retry anyway
                    all_low = all(d.confidence == ConfidenceLevel.LOW for d in result.diff_delta.diff_items)
                    if all_low and result.diff_delta.diff_items:
                        logger.warning("All diffs LOW confidence, triggering retry")
                        fabricated = [d.alert for d in result.diff_delta.diff_items if d.alert]
                        assertion["passed"] = False
                        assertion["fabricated_skills"] = fabricated

                memory_entry = f"[{section.get('heading', 'section')}] {result.tailored_content[:150]}"
                self._section_memory.append(memory_entry)
                return {"output": result, "missing_skills": result.missing_skills, "had_fabrication": attempt > 0}
            fabricated = assertion["fabricated_skills"]
            logger.warning("Attempt %d/%d for %s: fabricated=%s", attempt + 1, MAX_TAILOR_RETRIES + 1, section.get("heading", "?"), fabricated)
            if attempt < MAX_TAILOR_RETRIES:
                retry_hints.append(f"PREVIOUS ATTEMPT fabricated: {fabricated}. CRITICAL: Do NOT add these skills. Use ONLY skills from the original resume.")
            else:
                logger.warning("Max retries for %s, keeping original", section.get("heading", "?"))
                fallback = TailorOutput(tailored_content=section.get("content", ""), changes_log=[{"type": "degradation", "reason": f"Fabrication risk, original kept after {MAX_TAILOR_RETRIES + 1} attempts"}], missing_skills=list(jd_skills - original_skills), refusal_triggered=True)
                return {"output": fallback, "missing_skills": fallback.missing_skills, "had_fabrication": True}
        raise RuntimeError("unreachable")

    def _make_stage_client(self, config_key, llm_configs):
        if llm_configs:
            cfg = llm_configs.get(config_key) or llm_configs.get("default")
            if cfg and isinstance(cfg, dict):
                return create_llm_client(**cfg)
        return None
AlignmentPipeline = ResumePipeline
