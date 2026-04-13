#!/usr/bin/env python3
"""WebSocket System — Real-Time Streaming
Provides WebSocket connections for real-time agent communication, live metrics, and event streaming.
"""

import asyncio
import contextlib
import json
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState


class MessageType(str, Enum):
    # Connection management
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    PING = "ping"
    PONG = "pong"

    # Agent communication
    AGENT_STATUS = "agent_status"
    AGENT_COMMAND = "agent_command"
    AGENT_RESULT = "agent_result"

    # Data streaming
    METRICS = "metrics"
    LOG = "log"
    EVENT = "event"

    # User messages
    MESSAGE = "message"
    BROADCAST = "broadcast"


@dataclass
class WSMessage:
    type: MessageType
    data: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    sender: str = ""
    room: str = ""

    def to_json(self) -> str:
        return json.dumps({
            "type": self.type.value,
            "data": self.data,
            "timestamp": self.timestamp,
            "sender": self.sender,
            "room": self.room,
        })

    @classmethod
    def from_json(cls, raw: str) -> "WSMessage":
        obj = json.loads(raw)
        return cls(
            type=MessageType(obj["type"]),
            data=obj.get("data", {}),
            timestamp=obj.get("timestamp", time.time()),
            sender=obj.get("sender", ""),
            room=obj.get("room", ""),
        )


@dataclass
class WSClient:
    """Represents a connected WebSocket client."""

    websocket: WebSocket
    client_id: str
    rooms: set[str] = field(default_factory=set)
    message_count: int = 0
    connected_at: float = field(default_factory=time.time)
    filters: dict[str, Any] = field(default_factory=dict)

    async def send(self, message: WSMessage) -> bool:
        try:
            if self.websocket.client_state == WebSocketState.CONNECTED:
                await self.websocket.send_text(message.to_json())
                self.message_count += 1
                return True
            return False
        except Exception:
            return False


class ConnectionManager:
    """Manages all WebSocket connections, rooms, and message routing."""

    def __init__(self):
        self._clients: dict[str, WSClient] = {}
        self._rooms: dict[str, set[str]] = {}  # room -> set of client_ids
        self._handlers: dict[MessageType, list[Callable]] = {}
        self._stats = {
            "total_connections": 0,
            "total_disconnections": 0,
            "total_messages": 0,
            "peak_connections": 0,
        }

    # ── Connection Management ──

    async def connect(self, websocket: WebSocket, client_id: str) -> WSClient:
        await websocket.accept()
        client = WSClient(websocket=websocket, client_id=client_id)
        self._clients[client_id] = client
        self._stats["total_connections"] += 1
        self._stats["peak_connections"] = max(
            self._stats["peak_connections"], len(self._clients)
        )
        # Auto-join default room
        await self.join_room(client_id, "default")
        return client

    def disconnect(self, client_id: str) -> None:
        client = self._clients.pop(client_id, None)
        if client:
            for room in list(client.rooms):
                self.leave_room(client_id, room)
            self._stats["total_disconnections"] += 1

    def get_client(self, client_id: str) -> WSClient | None:
        return self._clients.get(client_id)

    def get_connected_count(self) -> int:
        return len(self._clients)

    # ── Room Management ──

    async def join_room(self, client_id: str, room: str) -> bool:
        client = self._clients.get(client_id)
        if not client:
            return False
        client.rooms.add(room)
        if room not in self._rooms:
            self._rooms[room] = set()
        self._rooms[room].add(client_id)
        await self._send_to_room(room, WSMessage(
            type=MessageType.MESSAGE,
            data={"action": "join", "client_id": client_id, "room": room},
            sender="system",
            room=room,
        ), exclude=[client_id])
        return True

    def leave_room(self, client_id: str, room: str) -> bool:
        client = self._clients.get(client_id)
        if not client:
            return False
        client.rooms.discard(room)
        if room in self._rooms:
            self._rooms[room].discard(client_id)
            if not self._rooms[room]:
                del self._rooms[room]
        return True

    def get_rooms(self) -> dict[str, int]:
        return {room: len(clients) for room, clients in self._rooms.items()}

    # ── Message Sending ──

    async def send_to_client(self, client_id: str, message: WSMessage) -> bool:
        client = self._clients.get(client_id)
        if client:
            return await client.send(message)
        return False

    async def send_to_room(self, room: str, message: WSMessage, exclude: list[str] = None) -> int:
        return await self._send_to_room(room, message, exclude or [])

    async def _send_to_room(self, room: str, message: WSMessage, exclude: list[str]) -> int:
        client_ids = self._rooms.get(room, set())
        sent = 0
        for cid in client_ids:
            if cid not in exclude and cid in self._clients:
                if await self._clients[cid].send(message):
                    sent += 1
        return sent

    async def broadcast(self, message: WSMessage, exclude: list[str] = None) -> int:
        exclude = exclude or []
        sent = 0
        for cid, client in list(self._clients.items()):
            if cid not in exclude and await client.send(message):
                sent += 1
        return sent

    # ── Event Handlers ──

    def on(self, message_type: MessageType, handler: Callable):
        if message_type not in self._handlers:
            self._handlers[message_type] = []
        self._handlers[message_type].append(handler)

    async def dispatch(self, client_id: str, message: WSMessage):
        self._stats["total_messages"] += 1
        handlers = self._handlers.get(message.type, [])
        for handler in handlers:
            try:
                result = handler(client_id, message)
                if asyncio.iscoroutine(result):
                    await result
            except Exception as e:
                await self.send_to_client(client_id, WSMessage(
                    type=MessageType.MESSAGE,
                    data={"error": str(e), "type": message.type.value},
                    sender="system",
                ))

    # ── Stats ──

    def get_stats(self) -> dict[str, Any]:
        return {
            **self._stats,
            "active_connections": len(self._clients),
            "active_rooms": len(self._rooms),
            "rooms": self.get_rooms(),
        }

    async def cleanup(self):
        """Disconnect all clients gracefully."""
        for client_id in list(self._clients.keys()):
            client = self._clients.get(client_id)
            if client and client.websocket.client_state == WebSocketState.CONNECTED:
                with contextlib.suppress(Exception):
                    await client.websocket.close()
        self._clients.clear()
        self._rooms.clear()


# Global connection manager
ws_manager = ConnectionManager()

# ── FastAPI Router ──

ws_router = APIRouter(prefix="/ws", tags=["websocket"])


@ws_router.websocket("/connect/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await ws_manager.connect(websocket, client_id)
    try:
        while True:
            raw = await websocket.receive_text()
            message = WSMessage.from_json(raw)
            await ws_manager.dispatch(client_id, message)

            # Default handlers
            if message.type == MessageType.PING:
                await ws_manager.send_to_client(client_id, WSMessage(
                    type=MessageType.PONG,
                    data={"server_time": datetime.now(UTC).isoformat()},
                    sender="server",
                ))
            elif message.type == MessageType.MESSAGE and message.data.get("room"):
                await ws_manager.send_to_room(message.data["room"], message, exclude=[client_id])
            elif message.type == MessageType.BROADCAST:
                await ws_manager.broadcast(message, exclude=[client_id])

    except WebSocketDisconnect:
        ws_manager.disconnect(client_id)
    except Exception:
        ws_manager.disconnect(client_id)


@ws_router.get("/stats")
async def get_ws_stats():
    return ws_manager.get_stats()


# ── Helper Functions ──

async def emit_agent_status(agent_id: str, status: str, details: dict[str, Any] = None):
    await ws_manager.broadcast(WSMessage(
        type=MessageType.AGENT_STATUS,
        data={"agent_id": agent_id, "status": status, **(details or {})},
        sender="system",
    ))


async def emit_metrics(agent_id: str, metrics: dict[str, Any]):
    await ws_manager.broadcast(WSMessage(
        type=MessageType.METRICS,
        data={"agent_id": agent_id, **metrics},
        sender="system",
    ))


async def emit_log(level: str, message: str, data: dict[str, Any] = None):
    await ws_manager.broadcast(WSMessage(
        type=MessageType.LOG,
        data={"level": level, "message": message, **(data or {})},
        sender="system",
    ))
