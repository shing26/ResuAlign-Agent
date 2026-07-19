"""Application configuration via environment variables."""

from __future__ import annotations

import os
from enum import StrEnum
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent.parent.parent / ".env")


class LLMProvider(StrEnum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
    DEEPSEEK = "deepseek"
    GEMINI = "gemini"
    GLM = "glm"
    MOONSHOT = "moonshot"
    OPENROUTER = "openrouter"
    MOCK = "mock"


PROVIDER_CONFIGS: dict[str, dict] = {
    "openai": {"base_url": "https://api.openai.com/v1", "default_model": "gpt-4o"},
    "deepseek": {"base_url": "https://api.deepseek.com", "default_model": "deepseek-chat"},
    "glm": {"base_url": "https://open.bigmodel.cn/api/paas/v4", "default_model": "glm-4"},
    "moonshot": {"base_url": "https://api.moonshot.cn/v1", "default_model": "moonshot-v1-8k"},
    "openrouter": {"base_url": "https://openrouter.ai/api/v1", "default_model": "openai/gpt-4o"},
}


class Settings:
    def __init__(self) -> None:
        raw_provider = os.getenv("LLM_PROVIDER", "deepseek")
        try:
            self.llm_provider = LLMProvider(raw_provider)
        except ValueError:
            self.llm_provider = LLMProvider.DEEPSEEK

        prov = self.llm_provider.value
        cfg = PROVIDER_CONFIGS.get(prov, {})
        env_prefix = prov.upper()
        self.api_key: str = os.getenv(f"{env_prefix}_API_KEY", "")
        self.base_url: str = os.getenv(f"{env_prefix}_BASE_URL", cfg.get("base_url", ""))
        self.model: str = os.getenv(f"{env_prefix}_MODEL", cfg.get("default_model", ""))

        self.gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
        self.gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
        self.anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
        self.anthropic_model: str = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")
        self.ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.ollama_model: str = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
        self.ollama_api_url: str = f"{self.ollama_base_url.rstrip('/')}/v1"
        self.mock_delay_ms: int = int(os.getenv("MOCK_DELAY_MS", "500"))
        self.database_url: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://resualign:resualign@localhost:5432/resualign")
        self.redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.host: str = os.getenv("HOST", "0.0.0.0")
        self.port: int = int(os.getenv("PORT", "8000"))
        self.env: str = os.getenv("ENV", "development")
        self.rate_limit_per_minute: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "30"))
        self.cache_ttl_hours: int = int(os.getenv("CACHE_TTL_HOURS", "24"))
        self.ocr_fallback_enabled: bool = os.getenv("OCR_FALLBACK_ENABLED", "false").lower() == "true"
        self.ocr_language: str = os.getenv("OCR_LANGUAGE", "chi_sim+eng")


settings = Settings()
