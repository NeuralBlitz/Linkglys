#!/usr/bin/env python3
"""Rate Limiter — Token Bucket Algorithm
Provides per-user and per-IP rate limiting with configurable buckets.
"""

import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse

# ──────────────────────────────────────────────────────────────
# Token Bucket Implementation
# ──────────────────────────────────────────────────────────────

@dataclass
class TokenBucket:
    """Token bucket rate limiter."""

    capacity: int       # Maximum tokens
    refill_rate: float  # Tokens per second
    tokens: float = 0.0
    last_refill: float = field(default_factory=time.monotonic)

    def __post_init__(self):
        if self.tokens == 0.0:
            self.tokens = float(self.capacity)

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self.last_refill
        new_tokens = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + new_tokens)
        self.last_refill = now

    def consume(self, tokens: int = 1) -> tuple[bool, float]:
        """Try to consume tokens. Returns (success, wait_time)."""
        self._refill()
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True, 0.0
        wait_time = (tokens - self.tokens) / self.refill_rate
        return False, wait_time

    @property
    def remaining(self) -> int:
        self._refill()
        return int(self.tokens)

    @property
    def reset_in(self) -> float:
        if self.tokens >= self.capacity:
            return 0.0
        return (self.capacity - self.tokens) / self.refill_rate


# ──────────────────────────────────────────────────────────────
# Rate Limit Configuration Profiles
# ──────────────────────────────────────────────────────────────

RATE_LIMIT_PROFILES = {
    "default": {"capacity": 60, "refill_rate": 1.0},       # 60 requests, 1/sec refill
    "strict": {"capacity": 10, "refill_rate": 0.2},        # 10 requests, 1 per 5 sec
    "moderate": {"capacity": 30, "refill_rate": 0.5},      # 30 requests, 1 per 2 sec
    "relaxed": {"capacity": 120, "refill_rate": 2.0},      # 120 requests, 2/sec refill
    "api": {"capacity": 100, "refill_rate": 5.0},          # 100 requests, 5/sec refill
    "webhook": {"capacity": 1000, "refill_rate": 50.0},    # 1000 requests, 50/sec refill
}


# ──────────────────────────────────────────────────────────────
# Rate Limiter Manager
# ──────────────────────────────────────────────────────────────

class RateLimiter:
    """Manages per-key token buckets with configurable profiles."""

    def __init__(self, default_profile: str = "default"):
        self.default_profile = default_profile
        self._buckets: dict[str, TokenBucket] = {}
        self._profile_overrides: dict[str, str] = {}
        self._stats: dict[str, dict[str, int]] = defaultdict(lambda: {"allowed": 0, "denied": 0})

    @property
    def available_profiles(self) -> list[str]:
        """Return available rate limit profile names."""
        return list(RATE_LIMIT_PROFILES.keys())

    def set_profile(self, key: str, profile: str) -> None:
        """Override the rate limit profile for a specific key."""
        if profile not in RATE_LIMIT_PROFILES:
            raise ValueError(f"Unknown profile: {profile}. Available: {list(RATE_LIMIT_PROFILES.keys())}")
        self._profile_overrides[key] = profile

    def set_custom_limit(self, key: str, capacity: int, refill_rate: float) -> None:
        """Set a custom limit for a specific key."""
        self._buckets[key] = TokenBucket(capacity=capacity, refill_rate=refill_rate)

    def _get_bucket(self, key: str) -> TokenBucket:
        if key not in self._buckets:
            profile_name = self._profile_overrides.get(key, self.default_profile)
            config = RATE_LIMIT_PROFILES.get(profile_name, RATE_LIMIT_PROFILES["default"])
            self._buckets[key] = TokenBucket(**config)
        return self._buckets[key]

    def check(self, key: str, tokens: int = 1) -> tuple[bool, dict[str, Any]]:
        """Check rate limit for a key. Returns (allowed, info_dict)."""
        bucket = self._get_bucket(key)
        allowed, wait_time = bucket.consume(tokens)

        self._stats[key]["allowed" if allowed else "denied"] += 1

        return allowed, {
            "remaining": bucket.remaining,
            "limit": bucket.capacity,
            "reset_in": round(bucket.reset_in, 2),
            "retry_after": round(wait_time, 2) if not allowed else None,
        }

    def get_stats(self) -> dict[str, Any]:
        return {
            "active_buckets": len(self._buckets),
            "profile_overrides": dict(self._profile_overrides),
            "request_stats": {k: dict(v) for k, v in self._stats.items()},
        }

    def reset(self, key: str | None = None) -> None:
        if key:
            self._buckets.pop(key, None)
            self._stats.pop(key, None)
            self._profile_overrides.pop(key, None)
        else:
            self._buckets.clear()
            self._stats.clear()
            self._profile_overrides.clear()


# Global rate limiter
rate_limiter = RateLimiter()


# ──────────────────────────────────────────────────────────────
# FastAPI Middleware
# ──────────────────────────────────────────────────────────────

async def rate_limit_middleware(request: Request, call_next):
    """FastAPI middleware for rate limiting."""
    # Skip rate limiting for health checks and docs
    skip_paths = {"/health", "/docs", "/redoc", "/openapi.json", "/favicon.ico"}
    if request.url.path in skip_paths:
        return await call_next(request)

    # Identify client
    client_ip = request.client.host if request.client else "unknown"
    request.headers.get("X-API-Key", "")
    user_id = request.headers.get("X-User-ID", "")

    key = f"user:{user_id}" if user_id else f"ip:{client_ip}"

    allowed, info = rate_limiter.check(key)

    if not allowed:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "error": "rate_limit_exceeded",
                "message": f"Rate limit exceeded. Retry after {info['retry_after']}s",
                "retry_after": info["retry_after"],
            },
            headers={
                "Retry-After": str(int(info["retry_after"]) + 1),
                "X-RateLimit-Limit": str(info["limit"]),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(int(time.time()) + int(info["reset_in"])),
            },
        )

    # Call the actual endpoint
    response = await call_next(request)

    # Add rate limit headers to response
    response.headers["X-RateLimit-Limit"] = str(info["limit"])
    response.headers["X-RateLimit-Remaining"] = str(info["remaining"])
    response.headers["X-RateLimit-Reset"] = str(int(time.time()) + int(info["reset_in"]))

    return response


# ──────────────────────────────────────────────────────────────
# Dependency for endpoint-level rate limiting
# ──────────────────────────────────────────────────────────────

def rate_limit(profile: str = "default"):
    """Dependency factory for endpoint-specific rate limiting."""
    async def limiter(request: Request):
        key = f"endpoint:{request.url.path}:{request.client.host if request.client else 'unknown'}"
        rate_limiter.set_profile(key, profile)
        allowed, info = rate_limiter.check(key)
        if not allowed:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Retry after {info['retry_after']}s",
                headers={"Retry-After": str(int(info["retry_after"]) + 1)},
            )
        return info
    return limiter
