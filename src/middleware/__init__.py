"""NeuralBlitz Middleware Package
Provides auth, rate limiting, caching, WebSocket, event bus, and metrics.
"""

from .auth import Role, create_token_pair, decode_access_token, get_current_user, user_store
from .cache import cache, cached, invalidate_cache
from .database import Repository, get_db, init_db
from .event_bus import Event, EventPriority, emit, event_bus, on_event
from .metrics import metrics_endpoint, prometheus_metrics_middleware, registry
from .rate_limiter import RATE_LIMIT_PROFILES, rate_limit_middleware, rate_limiter
from .websocket import emit_agent_status, emit_log, emit_metrics, ws_manager, ws_router

__all__ = [
    "user_store", "create_token_pair", "decode_access_token", "get_current_user", "Role",
    "rate_limiter", "rate_limit_middleware", "RATE_LIMIT_PROFILES",
    "cache", "cached", "invalidate_cache",
    "ws_manager", "ws_router", "emit_agent_status", "emit_metrics", "emit_log",
    "event_bus", "Event", "EventPriority", "emit", "on_event",
    "registry", "prometheus_metrics_middleware", "metrics_endpoint",
    "get_db", "Repository", "init_db",
]
