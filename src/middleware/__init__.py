"""
NeuralBlitz Middleware Package
Provides auth, rate limiting, caching, WebSocket, event bus, and metrics.
"""

from .auth import user_store, create_token_pair, decode_access_token, get_current_user, Role
from .rate_limiter import rate_limiter, rate_limit_middleware, RATE_LIMIT_PROFILES
from .cache import cache, cached, invalidate_cache
from .websocket import ws_manager, ws_router, emit_agent_status, emit_metrics, emit_log
from .event_bus import event_bus, Event, EventPriority, emit, on_event
from .metrics import registry, prometheus_metrics_middleware, metrics_endpoint
from .database import get_db, Repository, init_db

__all__ = [
    "user_store", "create_token_pair", "decode_access_token", "get_current_user", "Role",
    "rate_limiter", "rate_limit_middleware", "RATE_LIMIT_PROFILES",
    "cache", "cached", "invalidate_cache",
    "ws_manager", "ws_router", "emit_agent_status", "emit_metrics", "emit_log",
    "event_bus", "Event", "EventPriority", "emit", "on_event",
    "registry", "prometheus_metrics_middleware", "metrics_endpoint",
    "get_db", "Repository", "init_db",
]
