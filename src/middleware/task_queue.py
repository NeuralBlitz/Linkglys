#!/usr/bin/env python3
"""
Task Queue — Async Task Processing
Lightweight async task queue with priority, retry, scheduling, and result storage.
No external dependencies needed (no Celery/RabbitMQ required).
"""

import os
import time
import json
import uuid
import asyncio
import hashlib
import traceback
from typing import Dict, Any, Optional, Callable, Awaitable, List
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone
from collections import defaultdict
import heapq


class TaskStatus(str, Enum):
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"


class TaskPriority(int, Enum):
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3
    BACKGROUND = 4


@dataclass(order=True)
class Task:
    """Represents an async task to be executed."""
    priority: int
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()), compare=False)
    name: str = field(default="", compare=False)
    func_name: str = field(default="", compare=False)
    args: tuple = field(default_factory=tuple, compare=False)
    kwargs: Dict[str, Any] = field(default_factory=dict, compare=False)
    status: TaskStatus = field(default=TaskStatus.PENDING, compare=False)
    created_at: float = field(default_factory=time.time, compare=False)
    scheduled_at: float = field(default=0, compare=False)
    started_at: float = field(default=0, compare=False)
    completed_at: float = field(default=0, compare=False)
    result: Any = field(default=None, compare=False)
    error: Optional[str] = field(default=None, compare=False)
    retry_count: int = field(default=0, compare=False)
    max_retries: int = field(default=3, compare=False)
    timeout: float = field(default=300, compare=False)
    tags: List[str] = field(default_factory=list, compare=False)
    group: str = field(default="", compare=False)

    def is_due(self) -> bool:
        if self.scheduled_at == 0:
            return True
        return time.time() >= self.scheduled_at

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "name": self.name,
            "func_name": self.func_name,
            "status": self.status.value,
            "priority": self.priority,
            "created_at": datetime.fromtimestamp(self.created_at, tz=timezone.utc).isoformat(),
            "scheduled_at": datetime.fromtimestamp(self.scheduled_at, tz=timezone.utc).isoformat() if self.scheduled_at else None,
            "started_at": datetime.fromtimestamp(self.started_at, tz=timezone.utc).isoformat() if self.started_at else None,
            "completed_at": datetime.fromtimestamp(self.completed_at, tz=timezone.utc).isoformat() if self.completed_at else None,
            "result": str(self.result) if self.result is not None else None,
            "error": self.error,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "timeout": self.timeout,
            "tags": self.tags,
            "group": self.group,
        }


class TaskQueue:
    """Async task queue with priority, retry, and scheduling."""

    def __init__(self, max_workers: int = 4):
        self._queue: List[Task] = []
        self._tasks: Dict[str, Task] = {}
        self._handlers: Dict[str, Callable] = {}
        self._results: Dict[str, Any] = {}
        self._running = False
        self._max_workers = max_workers
        self._semaphore = asyncio.Semaphore(max_workers)
        self._stats = {
            "total_submitted": 0,
            "total_completed": 0,
            "total_failed": 0,
            "total_retried": 0,
            "total_cancelled": 0,
            "total_timeout": 0,
        }
        self._group_stats: Dict[str, Dict[str, int]] = defaultdict(
            lambda: {"submitted": 0, "completed": 0, "failed": 0}
        )

    def register(self, name: str):
        """Decorator to register a task handler."""
        def decorator(func: Callable):
            self._handlers[name] = func
            return func
        return decorator

    async def submit(
        self,
        name: str,
        *args,
        priority: TaskPriority = TaskPriority.NORMAL,
        delay: float = 0,
        timeout: float = 300,
        max_retries: int = 3,
        tags: List[str] = None,
        group: str = "",
        task_id: str = None,
        **kwargs,
    ) -> str:
        """Submit a task for execution."""
        if name not in self._handlers:
            raise ValueError(f"No handler registered for task '{name}'. Available: {list(self._handlers.keys())}")

        scheduled_at = time.time() + delay if delay > 0 else 0

        task = Task(
            priority=priority.value,
            task_id=task_id or str(uuid.uuid4()),
            name=name,
            func_name=name,
            args=args,
            kwargs=kwargs,
            status=TaskStatus.PENDING,
            scheduled_at=scheduled_at,
            timeout=timeout,
            max_retries=max_retries,
            tags=tags or [],
            group=group,
        )

        self._tasks[task.task_id] = task
        heapq.heappush(self._queue, task)
        self._stats["total_submitted"] += 1

        if group:
            self._group_stats[group]["submitted"] += 1

        return task.task_id

    async def submit_batch(self, tasks: List[Dict[str, Any]]) -> List[str]:
        """Submit multiple tasks at once."""
        ids = []
        for t in tasks:
            task_id = await self.submit(
                name=t["name"],
                *t.get("args", ()),
                priority=TaskPriority(t.get("priority", 2)),
                delay=t.get("delay", 0),
                timeout=t.get("timeout", 300),
                max_retries=t.get("max_retries", 3),
                tags=t.get("tags", []),
                group=t.get("group", ""),
                **t.get("kwargs", {}),
            )
            ids.append(task_id)
        return ids

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        task = self._tasks.get(task_id)
        return task.to_dict() if task else None

    def get_result(self, task_id: str) -> Optional[Any]:
        task = self._tasks.get(task_id)
        if task and task.status == TaskStatus.COMPLETED:
            return task.result
        return None

    def list_tasks(
        self,
        status: TaskStatus = None,
        group: str = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        tasks = list(self._tasks.values())
        if status:
            tasks = [t for t in tasks if t.status == status]
        if group:
            tasks = [t for t in tasks if t.group == group]
        tasks.sort(key=lambda t: t.created_at, reverse=True)
        return [t.to_dict() for t in tasks[:limit]]

    def cancel_task(self, task_id: str) -> bool:
        task = self._tasks.get(task_id)
        if task and task.status in (TaskStatus.PENDING, TaskStatus.QUEUED):
            task.status = TaskStatus.CANCELLED
            self._stats["total_cancelled"] += 1
            return True
        return False

    async def retry_task(self, task_id: str) -> Optional[str]:
        task = self._tasks.get(task_id)
        if task and task.status == TaskStatus.FAILED:
            task.status = TaskStatus.PENDING
            task.retry_count = 0
            task.error = None
            task.result = None
            task.created_at = time.time()
            heapq.heappush(self._queue, task)
            return task.task_id
        return None

    def get_stats(self) -> Dict[str, Any]:
        return {
            **self._stats,
            "queue_size": len([t for t in self._queue if t.status == TaskStatus.PENDING]),
            "running_count": len([t for t in self._tasks.values() if t.status == TaskStatus.RUNNING]),
            "registered_handlers": list(self._handlers.keys()),
            "group_stats": dict(self._group_stats),
        }

    async def _process_queue(self):
        """Background worker that processes the task queue."""
        while self._running:
            # Find next due task
            due_tasks = []
            remaining = []
            for task in self._queue:
                if task.is_due() and task.status == TaskStatus.PENDING:
                    due_tasks.append(task)
                else:
                    remaining.append(task)

            self._queue = remaining
            heapq.heapify(self._queue)

            for task in due_tasks:
                asyncio.create_task(self._execute_task(task))

            await asyncio.sleep(0.1)  # Poll interval

    async def _execute_task(self, task: Task):
        """Execute a single task with timeout and retry."""
        handler = self._handlers.get(task.func_name)
        if not handler:
            task.status = TaskStatus.FAILED
            task.error = f"No handler for '{task.func_name}'"
            self._stats["total_failed"] += 1
            return

        task.status = TaskStatus.RUNNING
        task.started_at = time.time()

        try:
            async with self._semaphore:
                if asyncio.iscoroutinefunction(handler):
                    result = await asyncio.wait_for(
                        handler(*task.args, **task.kwargs),
                        timeout=task.timeout,
                    )
                else:
                    loop = asyncio.get_event_loop()
                    result = await asyncio.wait_for(
                        loop.run_in_executor(None, lambda: handler(*task.args, **task.kwargs)),
                        timeout=task.timeout,
                    )

            task.status = TaskStatus.COMPLETED
            task.result = result
            task.completed_at = time.time()
            self._stats["total_completed"] += 1
            self._results[task.task_id] = result

            if task.group:
                self._group_stats[task.group]["completed"] += 1

        except asyncio.TimeoutError:
            task.status = TaskStatus.FAILED
            task.error = f"Task timed out after {task.timeout}s"
            task.completed_at = time.time()
            self._stats["total_timeout"] += 1
            self._stats["total_failed"] += 1

            if task.group:
                self._group_stats[task.group]["failed"] += 1

        except Exception as e:
            task.error = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
            task.completed_at = time.time()

            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.status = TaskStatus.PENDING
                task.started_at = 0
                task.scheduled_at = time.time() + (2 ** task.retry_count)  # Exponential backoff
                heapq.heappush(self._queue, task)
                self._stats["total_retried"] += 1
            else:
                task.status = TaskStatus.FAILED
                self._stats["total_failed"] += 1

                if task.group:
                    self._group_stats[task.group]["failed"] += 1

    async def start(self):
        """Start the task queue worker."""
        self._running = True
        asyncio.create_task(self._process_queue())

    async def stop(self):
        """Stop the task queue worker."""
        self._running = False
        # Cancel all pending tasks
        for task in self._queue:
            if task.status == TaskStatus.PENDING:
                task.status = TaskStatus.CANCELLED


# Global task queue
task_queue = TaskQueue(max_workers=4)


# ──────────────────────────────────────────────────────────────
# Pre-registered Task Handlers
# ──────────────────────────────────────────────────────────────

@task_queue.register("process_agent")
async def process_agent_task(agent_id: str, action: str, **kwargs):
    """Process an agent action."""
    await asyncio.sleep(0.1)  # Simulate work
    return {
        "agent_id": agent_id,
        "action": action,
        "status": "completed",
        "result": f"Agent {agent_id} executed {action}",
    }


@task_queue.register("analyze_data")
async def analyze_data_task(dataset_id: str, analysis_type: str = "basic"):
    """Analyze a dataset."""
    await asyncio.sleep(0.5)
    return {
        "dataset_id": dataset_id,
        "analysis_type": analysis_type,
        "status": "completed",
        "results": {"rows": 0, "columns": 0, "insights": []},
    }


@task_queue.register("generate_report")
async def generate_report_task(report_type: str, params: Dict[str, Any] = None):
    """Generate a report."""
    await asyncio.sleep(1.0)
    return {
        "report_type": report_type,
        "params": params or {},
        "status": "completed",
        "report_id": f"rpt_{hashlib.md5(f'{report_type}{time.time()}'.encode()).hexdigest()[:8]}",
    }


@task_queue.register("send_notification")
async def send_notification_task(user_id: str, message: str, channel: str = "email"):
    """Send a notification."""
    await asyncio.sleep(0.1)
    return {
        "user_id": user_id,
        "message": message,
        "channel": channel,
        "status": "sent",
    }


@task_queue.register("cleanup")
async def cleanup_task(target: str = "cache"):
    """Run cleanup tasks."""
    await asyncio.sleep(0.2)
    return {
        "target": target,
        "status": "completed",
        "cleaned": 0,
    }
