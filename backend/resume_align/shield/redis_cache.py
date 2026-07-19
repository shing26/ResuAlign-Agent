"""Redis Cache layer for MD5-based token cost control."""

from __future__ import annotations

import hashlib
import json
import logging
from typing import Any

import redis.asyncio as aioredis

from resume_align.config import settings

logger = logging.getLogger(__name__)


class RedisCache:
    """MD5-fingerprint cache to avoid redundant LLM calls."""

    def __init__(self) -> None:
        self.client: aioredis.Redis | None = None
        self.ttl = settings.cache_ttl_hours * 3600

    async def connect(self) -> None:
        """Initialize the Redis connection."""
        try:
            self.client = aioredis.from_url(
                settings.redis_url,
                decode_responses=True,
            )
            await self.client.ping()
            logger.info("Connected to Redis at %s", settings.redis_url)
        except Exception as exc:
            logger.warning("Redis unavailable, cache disabled: %s", exc)
            self.client = None

    async def disconnect(self) -> None:
        if self.client:
            await self.client.close()

    @staticmethod
    def md5(text: str) -> str:
        return hashlib.md5(text.encode("utf-8")).hexdigest()

    def _make_key(self, resume_md5: str, jd_md5: str | None = None) -> str:
        if jd_md5:
            return f"cache:resume:{resume_md5}:jd:{jd_md5}"
        return f"cache:resume:{resume_md5}:diagnose"

    async def get(self, resume_md5: str, jd_md5: str | None = None) -> dict[str, Any] | None:
        """Get cached result if available."""
        if not self.client:
            return None
        key = self._make_key(resume_md5, jd_md5)
        data = await self.client.get(key)
        if data:
            logger.info("Cache HIT for key=%s", key)
            return json.loads(data)
        logger.info("Cache MISS for key=%s", key)
        return None

    async def set(
        self, resume_md5: str, data: dict[str, Any], jd_md5: str | None = None
    ) -> None:
        """Store result in cache."""
        if not self.client:
            return
        key = self._make_key(resume_md5, jd_md5)
        await self.client.setex(key, self.ttl, json.dumps(data, default=str))
        logger.info("Cache SET key=%s ttl=%ds", key, self.ttl)
