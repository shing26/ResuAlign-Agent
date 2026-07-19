# ResuAlign-Agent 🚀

**反幻觉、精准对齐的简历优化引擎**

ResuAlign-Agent 是一套专为技术人才设计的双阶段智能体简历优化系统。系统首创 **Two-Stage Agentic Pipeline**，在绝对保障数据真实性的前置约束下，实现简历的结构化诊断、岗位画像的向量化比对，以及简历技术栈的动态同义对齐。

## Features

- **Two-Stage Pipeline**: Diagnoser (resume audit) → Tailor (JD-aligned optimization)
- **Anti-Hallucination Guardrails**: Three-layer defense (System Prompt → Assertion Filter → Refusal Mechanism)
- **Sliding Window Alignment**: Section-level processing to solve "Lost in the Middle"
- **Cost-Saving Redis Cache**: MD5-based cache reduces LLM calls by ~80%
- **Multi-LLM Support**: OpenAI + Anthropic factory pattern
- **MCP Server Ready**: Connect to Cursor, Claude Desktop, or any MCP-compatible tool
- **Vector Search**: pgvector for resume-JD semantic matching

## Architecture

```
Client Layer (Vue 3 + SSE)
        |
Gateway Layer (FastAPI + Rate Limiter)
        |
Processing Layer
  ├─ PDF Parser (PyMuPDF -> Text/Sections)
  ├─ JD Structurer (LLM -> Structured JSON, 70% size reduction)
  ├─ Agent 1: Diagnoser (STAR Audit + Quant Check + Keyword Density)
  └─ Agent 2: Tailor (Semantic Bridging + Sliding Window Alignment)
        |
Shield & Storage Layer
  ├─ Assertion Checker (Tech entity cross-validation)
  ├─ PostgreSQL + pgvector (Job embeddings)
  └─ Redis Cache (MD5 fingerprint, 24h TTL)
```

## Quick Start

### Prerequisites
- Python 3.10+
- Docker & Docker Compose
- Node.js 18+ (for frontend)

### 1. Clone & Setup

```bash
git clone https://github.com/your-username/ResuAlign-Agent.git
cd ResuAlign-Agent

# Python dependencies
pip install -r backend/requirements.txt

# Frontend dependencies
cd frontend && npm install && cd ..
```

### 2. Start Infrastructure

```bash
docker compose up -d
```

### 3. Configure

```bash
cp .env.example .env
# Edit .env with your API keys
```

### 4. Run Backend

```bash
cd backend
uvicorn resume_align.main:app --reload
```

### 5. Run Frontend (separate terminal)

```bash
cd frontend
npm run dev
```

Open http://localhost:5173

## Project Structure

```
ResuAlign/
├── backend/
│   ├── resume_align/
│   │   ├── agents/        # Diagnoser + Tailor agents
│   │   ├── api/           # FastAPI routes & schemas
│   │   ├── llm/           # OpenAI/Anthropic client factory
│   │   ├── mcp/           # MCP server integration
│   │   ├── models/        # SQLAlchemy models
│   │   ├── parsers/       # PDF parser + JD structurer
│   │   ├── shield/        # Assertion checker, cache, rate limiter
│   │   ├── config.py      # Central configuration
│   │   ├── main.py        # FastAPI app entry
│   │   └── pipeline.py    # Pipeline orchestrator
│   └── requirements.txt
├── frontend/              # Vue 3 + Vite + TypeScript
├── tests/                 # Pytest suite
├── docker-compose.yml     # PostgreSQL+pgvector + Redis
├── .env.example           # Environment template
└── README.md
```

## Tech Stack

| Component | Choice | Why |
|-----------|--------|-----|
| Backend | FastAPI | Async I/O, SSE streaming, high throughput |
| Agent Framework | PydanticAI | Native `with_structured_output`, JSON Schema enforcement |
| LLM | OpenAI / Anthropic | Dual-provider factory pattern |
| Database | PostgreSQL + pgvector | Unified storage + vector search |
| Cache | Redis | MD5 fingerprint, 24h TTL, rate limiting |
| Frontend | Vue 3 + Vite | Lightweight, reactive, SSE-native |
| PDF | PyMuPDF | Fast text extraction, OCR fallback |
| MCP | FastMCP | Protocol-compatible, stdio transport |

## Anti-Hallucination Design

ResuAlign uses a **three-layer defense** against LLM hallucination:

1. **System Prompt Level**: Agent positioned as "strict auditor", explicit negative constraints
2. **Assertion Checker**: Post-generation cross-validation of tech entities
3. **Refusal Mechanism**: Hard skills without resume basis get flagged, not fabricated

## License

MIT
