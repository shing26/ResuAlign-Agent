"""Rate limiter using Redis Token Bucket."""

from __future__ import annotations

import logging
import time

import redis.asyncio as aioredis

from resume_align.core.config import settings

logger = logging.getLogger(__name__)


class RateLimiter:
    """Token bucket rate limiter backed by Redis."""

    def __init__(self) -> None:
        self.client: aioredis.Redis | None = None
        self.max_requests = settings.rate_limit_per_minute
        self.window = 60  # seconds

    async def connect(self) -> None:
        try:
            self.client = aioredis.from_url(
                settings.redis_url,
                decode_responses=True,
            )
            await self.client.ping()
        except Exception as exc:
            logger.warning("Rate limiter Redis unavailable: %s", exc)
            self.client = None

    async def check(self, client_ip: str) -> tuple[bool, dict[str, int]]:
        """Check if request is allowed. Returns (allowed, headers)."""
        if not self.client:
            return True, {"X-RateLimit-Limit": str(self.max_requests)}

        key = f"ratelimit:{client_ip}"
        now = int(time.time())
        window_start = now - self.window

        pipe = self.client.pipeline()
        pipe.zremrangebyscore(key, 0, window_start)
        pipe.zcard(key)
        pipe.zadd(key, {str(now): now})
        pipe.expire(key, self.window + 1)
        _, count, _, _ = await pipe.execute()

        allowed = count <= self.max_requests
        return allowed, {
            "X-RateLimit-Limit": str(self.max_requests),
            "X-RateLimit-Remaining": str(max(0, self.max_requests - count)),
        }
