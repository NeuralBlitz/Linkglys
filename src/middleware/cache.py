#!/usr/bin/env python3
"""Redis Caching Layer — Distributed Cache with Fallback
Provides Redis caching with in-memory fallback, cache invalidation, and TTL management.
"""

import functools
import hashlib
import json
import os
import time
from collections.abc import Callable
from typing import Any

# ──────────────────────────────────────────────────────────────
# In-Memory Fallback Cache (used when Redis unavailable)
# ──────────────────────────────────────────────────────────────

class MemoryCache:
    """LRU in-memory cache with TTL support — fallback for Redis."""

    def __init__(self, max_size: int = 10000):
        self._store: dict[str, dict[str, Any]] = {}
        self._max_size = max_size
        self._access_order: dict[str, float] = {}
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Any | None:
        entry = self._store.get(key)
        if entry is None:
            self._misses += 1
            return None
        if time.time() > entry["expires_at"]:
            self._store.pop(key, None)
            self._access_order.pop(key, None)
            self._misses += 1
            return None
        self._access_order[key] = time.time()
        self._hits += 1
        return entry["value"]

    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        # Evict oldest if at capacity
        if len(self._store) >= self._max_size:
            oldest_key = min(self._access_order, key=self._access_order.get)
            self._store.pop(oldest_key, None)
            self._access_order.pop(oldest_key, None)

        self._store[key] = {
            "value": value,
            "expires_at": time.time() + ttl,
            "created_at": time.time(),
        }
        self._access_order[key] = time.time()
        return True

    def delete(self, key: str) -> bool:
        self._store.pop(key, None)
        self._access_order.pop(key, None)
        return True

    def clear(self) -> None:
        self._store.clear()
        self._access_order.clear()

    def get_stats(self) -> dict[str, Any]:
        total = self._hits + self._misses
        return {
            "type": "memory",
            "size": len(self._store),
            "max_size": self._max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": round(self._hits / total, 4) if total > 0 else 0.0,
        }

    def cleanup_expired(self) -> int:
        now = time.time()
        expired = [k for k, v in self._store.items() if now > v["expires_at"]]
        for key in expired:
            self._store.pop(key, None)
            self._access_order.pop(key, None)
        return len(expired)


# ──────────────────────────────────────────────────────────────
# Cache Manager (Redis with Memory Fallback)
# ──────────────────────────────────────────────────────────────

class CacheManager:
    """Unified cache manager with Redis primary and memory fallback."""

    def __init__(self, redis_url: str | None = None):
        self._redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self._redis = None
        self._memory = MemoryCache()
        self._use_redis = False
        self._prefix = "nb:"
        self._stats = {"gets": 0, "sets": 0, "deletes": 0, "errors": 0}

        # Try to connect to Redis
        try:
            import redis
            self._redis = redis.from_url(
                self._redis_url,
                decode_responses=True,
                socket_timeout=2,
                socket_connect_timeout=2,
            )
            self._redis.ping()
            self._use_redis = True
        except Exception:
            self._use_redis = False  # Fall back to memory cache

    def _make_key(self, key: str) -> str:
        return f"{self._prefix}{key}"

    def get(self, key: str) -> Any | None:
        self._stats["gets"] += 1
        if self._use_redis:
            try:
                data = self._redis.get(self._make_key(key))
                if data:
                    return json.loads(data)
                return None
            except Exception:
                self._stats["errors"] += 1
                self._use_redis = False
                return self._memory.get(key)
        return self._memory.get(key)

    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        self._stats["sets"] += 1
        if self._use_redis:
            try:
                serialized = json.dumps(value, default=str)
                self._redis.setex(self._make_key(key), ttl, serialized)
                return True
            except Exception:
                self._stats["errors"] += 1
                self._use_redis = False
                return self._memory.set(key, value, ttl)
        return self._memory.set(key, value, ttl)

    def delete(self, key: str) -> bool:
        self._stats["deletes"] += 1
        if self._use_redis:
            try:
                return bool(self._redis.delete(self._make_key(key)))
            except Exception:
                self._stats["errors"] += 1
                self._use_redis = False
                return self._memory.delete(key)
        return self._memory.delete(key)

    def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching a pattern (Redis only)."""
        if self._use_redis:
            try:
                keys = self._redis.keys(self._make_key(pattern))
                if keys:
                    return self._redis.delete(*keys)
                return 0
            except Exception:
                self._stats["errors"] += 1
        return 0

    def clear(self) -> None:
        if self._use_redis:
            try:
                keys = self._redis.keys(f"{self._prefix}*")
                if keys:
                    self._redis.delete(*keys)
            except Exception:
                self._stats["errors"] += 1
        self._memory.clear()

    def get_stats(self) -> dict[str, Any]:
        mem_stats = self._memory.get_stats()
        return {
            "backend": "redis" if self._use_redis else "memory",
            "redis_url": self._redis_url if self._use_redis else None,
            "operations": dict(self._stats),
            "memory_cache": mem_stats,
        }

    def health_check(self) -> dict[str, Any]:
        if self._use_redis:
            try:
                ping = self._redis.ping()
                return {"status": "healthy", "backend": "redis", "ping": ping}
            except Exception as e:
                self._use_redis = False
                return {"status": "degraded", "backend": "memory (redis failed)", "error": str(e)}
        return {"status": "healthy", "backend": "memory"}


# Global cache manager
cache = CacheManager()


# ──────────────────────────────────────────────────────────────
# Cache Decorator
# ──────────────────────────────────────────────────────────────

def cached(ttl: int = 300, key_prefix: str = ""):
    """Decorator to cache function results."""
    def decorator(func: Callable):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            cache_key = _make_cache_key(func, args, kwargs, key_prefix)
            result = cache.get(cache_key)
            if result is not None:
                return result
            result = await func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            cache_key = _make_cache_key(func, args, kwargs, key_prefix)
            result = cache.get(cache_key)
            if result is not None:
                return result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result

        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    return decorator


def _make_cache_key(func: Callable, args: tuple, kwargs: dict, prefix: str) -> str:
    key_parts = [prefix, func.__module__, func.__qualname__]
    key_parts.extend(str(a) for a in args)
    key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
    raw = ":".join(key_parts)
    return hashlib.md5(raw.encode()).hexdigest()[:16]


def invalidate_cache(pattern: str) -> int:
    """Invalidate cache entries matching a pattern."""
    return cache.delete_pattern(pattern)
