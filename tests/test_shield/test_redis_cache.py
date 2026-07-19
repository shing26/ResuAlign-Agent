"""Tests for Redis cache module."""
from __future__ import annotations


class TestRedisCache:
    """Test Redis cache key generation and MD5."""

    def test_md5_consistency(self):
        """Test MD5 generation is consistent."""
        from resume_align.shield.redis_cache import RedisCache

        md5_1 = RedisCache.md5("test content")
        md5_2 = RedisCache.md5("test content")
        assert md5_1 == md5_2

    def test_md5_differs(self):
        """Test different inputs produce different MD5s."""
        from resume_align.shield.redis_cache import RedisCache

        md5_1 = RedisCache.md5("content a")
        md5_2 = RedisCache.md5("content b")
        assert md5_1 != md5_2
