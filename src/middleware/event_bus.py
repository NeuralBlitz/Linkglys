#!/usr/bin/env python3
"""Event Bus — Pub/Sub Event System
Async event bus with filtering, persistence, and real-time distribution.
"""

import asyncio
import time
import uuid
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any


class EventPriority(int, Enum):
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3
    DEBUG = 4


class EventStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    DEAD_LETTER = "dead_letter"


@dataclass
class Event:
    """Represents a system event."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: str = ""
    source: str = ""
    data: dict[str, Any] = field(default_factory=dict)
    priority: EventPriority = EventPriority.NORMAL
    status: EventStatus = EventStatus.PENDING
    timestamp: float = field(default_factory=time.time)
    ttl: int = 3600  # Time to live in seconds
    retry_count: int = 0
    max_retries: int = 3
    tags: list[str] = field(default_factory=list)
    correlation_id: str = ""
    error: str | None = None

    def is_expired(self) -> bool:
        return time.time() - self.timestamp > self.ttl

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "source": self.source,
            "data": self.data,
            "priority": self.priority.value,
            "status": self.status.value,
            "timestamp": datetime.fromtimestamp(self.timestamp, tz=UTC).isoformat(),
            "ttl": self.ttl,
            "retry_count": self.retry_count,
            "tags": self.tags,
            "correlation_id": self.correlation_id,
            "error": self.error,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Event":
        d = d.copy()
        d["priority"] = EventPriority(d.get("priority", 2))
        d["status"] = EventStatus(d.get("status", "pending"))
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class Subscription:
    """Represents an event subscription."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_types: list[str] = field(default_factory=list)
    handler: Callable | None = None
    async_handler: Callable | None = None
    filter_fn: Callable[[Event], bool] | None = None
    max_invocations: int = 0  # 0 = unlimited
    invocation_count: int = 0
    created_at: float = field(default_factory=time.time)
    tags: list[str] = field(default_factory=list)

    def can_invoke(self) -> bool:
        return self.max_invocations == 0 or self.invocation_count < self.max_invocations

    async def handle(self, event: Event) -> Any:
        if self.filter_fn and not self.filter_fn(event):
            return None
        if not self.can_invoke():
            return None

        self.invocation_count += 1

        if self.async_handler:
            return await self.async_handler(event)
        elif self.handler:
            result = self.handler(event)
            if asyncio.iscoroutine(result):
                return await result
            return result
        return None


class EventBus:
    """Async pub/sub event bus with priority queue and filtering."""

    def __init__(self, max_queue_size: int = 10000):
        self._subscriptions: dict[str, list[Subscription]] = defaultdict(list)
        self._event_history: list[Event] = []
        self._max_history = 5000
        self._dead_letters: list[Event] = []
        self._max_dead_letters = 1000
        self._running = False
        self._stats = {
            "events_published": 0,
            "events_processed": 0,
            "events_failed": 0,
            "events_dropped": 0,
            "subscriptions_created": 0,
            "total_handler_invocations": 0,
        }

    # ── Publishing ──

    async def publish(self, event: Event) -> str:
        if event.is_expired():
            self._stats["events_dropped"] += 1
            return event.id

        event.status = EventStatus.PENDING
        self._stats["events_published"] += 1

        # Store in history
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history = self._event_history[-self._max_history:]

        # Get matching subscriptions
        subs = self._get_subscriptions(event.type)

        # Process each subscription
        for sub in subs:
            event.status = EventStatus.PROCESSING
            try:
                await sub.handle(event)
                event.status = EventStatus.COMPLETED
            except Exception as e:
                event.status = EventStatus.FAILED
                event.error = str(e)
                event.retry_count += 1

                if event.retry_count >= event.max_retries:
                    event.status = EventStatus.DEAD_LETTER
                    self._dead_letters.append(event)
                    if len(self._dead_letters) > self._max_dead_letters:
                        self._dead_letters.pop(0)

                self._stats["events_failed"] += 1

            self._stats["events_processed"] += 1
            self._stats["total_handler_invocations"] += 1

        return event.id

    def publish_sync(self, event: Event) -> str:
        """Synchronous publish (for non-async contexts)."""
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(self.publish(event))
        finally:
            loop.close()

    async def publish_batch(self, events: list[Event]) -> list[str]:
        return [await self.publish(e) for e in events]

    # ── Subscriptions ──

    def subscribe(
        self,
        event_types: list[str],
        handler: Callable = None,
        async_handler: Callable = None,
        filter_fn: Callable[[Event], bool] = None,
        max_invocations: int = 0,
        tags: list[str] = None,
    ) -> str:
        """Subscribe to events. Returns subscription ID."""
        if not handler and not async_handler:
            raise ValueError("Either handler or async_handler must be provided")

        sub = Subscription(
            event_types=event_types,
            handler=handler,
            async_handler=async_handler,
            filter_fn=filter_fn,
            max_invocations=max_invocations,
            tags=tags or [],
        )

        for et in event_types:
            self._subscriptions[et].append(sub)

        self._stats["subscriptions_created"] += 1
        return sub.id

    def unsubscribe(self, subscription_id: str) -> bool:
        for et, subs in self._subscriptions.items():
            self._subscriptions[et] = [s for s in subs if s.id != subscription_id]
        return True

    def list_subscriptions(self) -> list[dict[str, Any]]:
        all_subs = []
        seen = set()
        for subs in self._subscriptions.values():
            for sub in subs:
                if sub.id not in seen:
                    seen.add(sub.id)
                    all_subs.append({
                        "id": sub.id,
                        "event_types": sub.event_types,
                        "invocation_count": sub.invocation_count,
                        "max_invocations": sub.max_invocations,
                        "tags": sub.tags,
                    })
        return all_subs

    # ── Querying ──

    def get_events(
        self,
        event_type: str | None = None,
        status: EventStatus | None = None,
        limit: int = 100,
        since: float = None,
    ) -> list[dict[str, Any]]:
        events = self._event_history
        if event_type:
            events = [e for e in events if e.type == event_type]
        if status:
            events = [e for e in events if e.status == status]
        if since:
            events = [e for e in events if e.timestamp >= since]
        return [e.to_dict() for e in events[-limit:]]

    def get_dead_letters(self, limit: int = 100) -> list[dict[str, Any]]:
        return [e.to_dict() for e in self._dead_letters[-limit:]]

    async def replay_dead_letter(self, event_id: str) -> str | None:
        for i, event in enumerate(self._dead_letters):
            if event.id == event_id:
                event.status = EventStatus.PENDING
                event.retry_count = 0
                event.error = None
                self._dead_letters.pop(i)
                return await self.publish(event)
        return None

    # ── Internal ──

    def _get_subscriptions(self, event_type: str) -> list[Subscription]:
        """Get subscriptions for an event type, including wildcard subscribers."""
        subs = list(self._subscriptions.get(event_type, []))
        # Wildcard subscriptions
        subs.extend(self._subscriptions.get("*", []))
        # Pattern matching (e.g., "agent.*" matches "agent.status")
        for pattern, pattern_subs in self._subscriptions.items():
            if pattern.endswith("*"):
                prefix = pattern[:-1]
                if event_type.startswith(prefix):
                    subs.extend(pattern_subs)
        return subs

    def get_stats(self) -> dict[str, Any]:
        return {
            **self._stats,
            "active_subscriptions": len(self.list_subscriptions()),
            "event_history_size": len(self._event_history),
            "dead_letter_count": len(self._dead_letters),
        }

    def clear(self) -> None:
        self._subscriptions.clear()
        self._event_history.clear()
        self._dead_letters.clear()
        for key in self._stats:
            if isinstance(self._stats[key], int):
                self._stats[key] = 0


# Global event bus
event_bus = EventBus()


# ── Convenience Decorators ──

def on_event(event_types: list[str], filter_fn=None):
    """Decorator to subscribe a function to events."""
    def decorator(func):
        import asyncio
        if asyncio.iscoroutinefunction(func):
            event_bus.subscribe(
                event_types=event_types,
                async_handler=func,
                filter_fn=filter_fn,
            )
        else:
            event_bus.subscribe(
                event_types=event_types,
                handler=func,
                filter_fn=filter_fn,
            )
        return func
    return decorator


async def emit(event_type: str, data: dict[str, Any], source: str = "", tags: list[str] = None):
    """Quick emit helper."""
    event = Event(type=event_type, source=source, data=data, tags=tags or [])
    return await event_bus.publish(event)
