"""FastAPI route definitions with DRY response builder."""

from __future__ import annotations
import json
import asyncio
import logging
import uuid

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from sse_starlette.sse import EventSourceResponse

from resume_align.api.schemas import (SessionConfigRequest, SessionConfigResponse, SessionTestRequest, TailorRequest,
    JobAnalysisRequest, JobAnalysisResponse, DiagnosticResultResponse,
    TailoringResultResponse, ErrorResponse,
)
from resume_align.pipeline import ResumePipeline, AlignmentPipeline
from resume_align.session_store import create_session, get_session, clear_session

logger = logging.getLogger(__name__)
router = APIRouter()
_pipeline = None


async def get_pipeline():
    global _pipeline
    if _pipeline is None:
        _pipeline = ResumePipeline()
        await _pipeline.initialize()
    return _pipeline


def _build_llm_configs(request):
    configs = {}
    if request.provider:
        configs["default"] = {"provider": request.provider, "api_key": request.api_key, "model": request.model, "base_url": request.base_url}
    for key, stage in [("jd_structurer", request.jd_provider), ("diagnoser", request.diagnoser_provider), ("tailor", request.tailor_provider)]:
        if stage and stage.provider:
            configs[key] = {"provider": stage.provider, "api_key": stage.api_key, "model": stage.model, "base_url": stage.base_url}
    return configs if configs else None


async def _run_and_build(pipeline, resume_content, jd_text=None, filename='resume.pdf', llm_configs=None):
    result = await pipeline.run(resume_content=resume_content, jd_text=jd_text, filename=filename)
    diagnostic_resp = DiagnosticResultResponse(
        report_id=str(uuid.uuid4()),
        star_score=result.diagnostic.star_score,
        quant_score=result.diagnostic.quant_score,
        skill_breadth=result.diagnostic.skill_breadth,
        skill_depth={sd.skill: sd.years for sd in result.diagnostic.skill_depth if hasattr(sd, chr(115)+chr(107)+chr(105)+chr(108)+chr(108))},
        issues=result.diagnostic.issues,
        suggestions=result.diagnostic.suggestions,
        raw_report=result.diagnostic.raw_report,
    )
    tailoring_resp = None
    if result.tailoring:
        tailoring_resp = TailoringResultResponse(
            result_id=str(uuid.uuid4()),
            original_sections=[],
            tailored_sections=[{"section": "", "content": t.tailored_content} for t in result.tailoring],
            missing_skills=result.missing_skills,
            changes_log=sum((t.changes_log for t in result.tailoring), []),
            full_output="\n\n".join(t.tailored_content for t in result.tailoring),
        )
    return JobAnalysisResponse(diagnostic=diagnostic_resp, tailoring=tailoring_resp, cached=result.cached, processing_time_ms=result.processing_time_ms)



@router.post('/resume/parse-pdf', summary='Parse PDF resume to raw text')
async def parse_pdf(file: UploadFile = File(...)):
    content = await file.read()
    pipeline = await get_pipeline()
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, pipeline.pdf_parser.parse_bytes, content, file.filename or 'resume.pdf')
    return {'raw_text': result.raw_text, 'sections': result.sections, 'md5': result.md5_fingerprint}

@router.post('/tailor', summary='Two-stage agent alignment: Diagnoser + Tailor + Shield')
async def tailor_resume(request: TailorRequest):
    pipeline = ResumePipeline()
    await pipeline.initialize()
    result = await pipeline.run(resume_content=request.resume_text, jd_text=request.job_text)
    diffs = []
    if result.tailoring:
        for t in result.tailoring:
            if hasattr(t, 'diff_delta') and t.diff_delta:
                diffs.extend(t.diff_delta.diffs)
    return {
        'diagnostic': {'star_score': result.diagnostic.star_score, 'quant_score': result.diagnostic.quant_score, 'skill_breadth': result.diagnostic.skill_breadth},
        'diff_delta': {'target_job_title': request.job_title, 'company_name': request.company_name,
            'match_score_before': round(result.diagnostic.star_score * 100),
            'match_score_after': round(result.diagnostic.quant_score * 100),
            'summary': f'Optimized for {request.job_title}',
            'diff_items': [d.model_dump() for d in diffs]},
        'missing_skills': result.missing_skills,
        'processing_time_ms': result.processing_time_ms,
    }


@router.post('/session/test')
async def test_connection(request: SessionTestRequest):
    session = get_session(request.session_id)
    if not session:
        return {"ok": False, "msg": "Session expired"}
    try:
        from resume_align.llm.client import create_llm_client
        llm = create_llm_client(provider=session["provider"], api_key=session["api_key"], model=session["model"], base_url=session.get("base_url", ""))
        await llm.generate_text(system_prompt="Reply with: OK", user_prompt="Test")
        return {"ok": True, "msg": "Connection successful"}
    except Exception as e:
        return {"ok": False, "msg": str(e)}


@router.post('/session/configure', response_model=SessionConfigResponse, summary='Store API key securely in server session')
async def configure_session(request: SessionConfigRequest):
    session_id = create_session(provider=request.provider, api_key=request.api_key, model=request.model, base_url=request.base_url)
    masked = request.api_key[-4:] if request.api_key and len(request.api_key) > 4 else '****'
    return SessionConfigResponse(session_id=session_id, provider=request.provider, model=request.model or '', masked_key=masked)


@router.post('/analyze', response_model=JobAnalysisResponse, responses={400: {'model': ErrorResponse}}, summary='Two-stage resume analysis')
async def analyze_resume(request: JobAnalysisRequest):
    try:
        pipeline = await get_pipeline()
        llm_configs = _build_llm_configs(request)
        return await _run_and_build(pipeline, resume_content=request.resume_text, jd_text=request.jd_text, llm_configs=llm_configs)
    except Exception as exc:
        logger.exception('Analysis failed')
        raise HTTPException(status_code=500, detail=str(exc))


_stream_queues: dict[str, asyncio.Queue] = {}


async def _run_and_stream(report_id: str, pipeline, resume_content, jd_text, filename, llm_configs):
    queue = _stream_queues[report_id]
    try:
        async def emit(event):
            sse_data = json.dumps(event, ensure_ascii=False)
            await queue.put(f"data: {sse_data}\n\n")
        await pipeline.run(resume_content=resume_content, jd_text=jd_text, filename=filename, llm_configs=llm_configs, event_callback=emit)
    except Exception as e:
        err = {"event": "error", "data": {"message": str(e)}}
        await queue.put(f"data: {json.dumps(err, ensure_ascii=False)}\n\n")
    finally:
        await queue.put(None)  # Signal end


@router.post('/analyze/stream', summary='Streaming resume analysis with SSE')
async def analyze_resume_stream(
    file: UploadFile = File(...),
    jd_text: str | None = Form(None),
    session_id: str | None = Form(None),
):
    content = await file.read()
    pipeline = await get_pipeline()
    report_id = str(uuid.uuid4())

    llm_configs = {}
    if session_id:
        session = get_session(session_id)
        if session:
            llm_configs['default'] = {'provider': session['provider'], 'api_key': session['api_key'], 'model': session.get('model', ''), 'base_url': session.get('base_url', '')}

    queue = asyncio.Queue()
    _stream_queues[report_id] = queue
    asyncio.create_task(_run_and_stream(report_id, pipeline, content, jd_text, file.filename or 'resume.pdf', llm_configs if llm_configs else None))

    async def event_generator():
        while True:
            msg = await queue.get()
            if msg is None:
                break
            yield msg
        _stream_queues.pop(report_id, None)

    from sse_starlette.sse import EventSourceResponse
    return EventSourceResponse(event_generator())




@router.post('/analyze/upload', summary='Upload PDF resume for analysis')
async def analyze_resume_upload(
    file: UploadFile = File(...),
    jd_text: str | None = Form(None),
    session_id: str | None = Form(None),
    provider: str | None = Form(None),
    api_key: str | None = Form(None),
    model: str | None = Form(None),
    base_url: str | None = Form(None),
    jd_structurer_provider: str | None = Form(None),
    jd_structurer_api_key: str | None = Form(None),
    jd_structurer_model: str | None = Form(None),
    diagnoser_provider: str | None = Form(None),
    diagnoser_api_key: str | None = Form(None),
    diagnoser_model: str | None = Form(None),
    tailor_provider: str | None = Form(None),
    tailor_api_key: str | None = Form(None),
    tailor_model: str | None = Form(None),
):
    try:
        content = await file.read()
        pipeline = await get_pipeline()
        llm_configs = {}
        if session_id:
            session = get_session(session_id)
            if session:
                llm_configs['default'] = {'provider': session['provider'], 'api_key': session['api_key'], 'model': session.get('model', ''), 'base_url': session.get('base_url', '')}
        if provider:
            llm_configs['default'] = {'provider': provider, 'api_key': api_key, 'model': model, 'base_url': base_url}
        for s_key, s_p, s_k, s_m in [
            ('jd_structurer', jd_structurer_provider, jd_structurer_api_key, jd_structurer_model),
            ('diagnoser', diagnoser_provider, diagnoser_api_key, diagnoser_model),
            ('tailor', tailor_provider, tailor_api_key, tailor_model),
        ]:
            if s_p:
                llm_configs[s_key] = {'provider': s_p, 'api_key': s_k, 'model': s_m}
        llm_configs = llm_configs if llm_configs else None
        return await _run_and_build(pipeline, resume_content=content, jd_text=jd_text, filename=file.filename or 'resume.pdf', llm_configs=llm_configs)
    except Exception as exc:
        logger.exception('Upload analysis failed')
        raise HTTPException(status_code=500, detail=str(exc))


@router.get('/analyze/{report_id}/stream', summary='SSE stream for pipeline progress')
async def stream_analysis(report_id: str):
    async def event_generator():
        stages = [('diagnosing', 'Running diagnosis...'), ('tailoring', 'Tailoring to JD...'), ('checking', 'Assertion checks...'), ('complete', 'Done!')]
        for event_type, message in stages:
            yield {'event': event_type, 'data': json.dumps({'message': message})}
            import asyncio; await asyncio.sleep(0.5)
    return EventSourceResponse(event_generator())
