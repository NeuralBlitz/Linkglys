"""
raft_consensus.py
Raft-based Distributed Consensus for D-MLMAS

Implements the Raft consensus algorithm with a shared message bus
so nodes actually communicate with each other (not simulated RPCs).
"""

import asyncio
import random
import time
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import deque
import hashlib
import json

logger = logging.getLogger(__name__)


class NodeRole(Enum):
    FOLLOWER = "follower"
    CANDIDATE = "candidate"
    LEADER = "leader"


class LogEntryType(Enum):
    COMMAND = "command"
    CONFIG = "config"
    NO_OP = "no_op"


@dataclass
class LogEntry:
    index: int
    term: int
    entry_type: LogEntryType
    command: Any
    timestamp: float = field(default_factory=time.time)


@dataclass
class RaftState:
    current_term: int = 0
    voted_for: Optional[str] = None
    log: List[LogEntry] = field(default_factory=list)

    def get_last_log_index(self) -> int:
        return len(self.log) - 1 if self.log else -1

    def get_last_log_term(self) -> int:
        return self.log[-1].term if self.log else -1

    def get_entry(self, index: int) -> Optional[LogEntry]:
        if 0 <= index < len(self.log):
            return self.log[index]
        return None


# ─── Shared Message Bus (replaces simulated RPCs) ───

class ClusterMessageBus:
    """Shared message bus for inter-node communication in the same process.
    In production, this would be replaced with actual network RPCs."""

    def __init__(self):
        self._handlers: Dict[str, Dict[str, Callable]] = {}  # node_id -> {method -> handler}

    def register_node(self, node_id: str, handlers: Dict[str, Callable]):
        """Register a node's RPC handlers"""
        self._handlers[node_id] = handlers

    async def send_rpc(self, target_id: str, method: str, params: dict) -> dict:
        """Send RPC to target node via message bus"""
        if target_id not in self._handlers:
            return {"error": f"Node {target_id} not found"}
        handler = self._handlers[target_id].get(method)
        if not handler:
            return {"error": f"Method {method} not found on {target_id}"}
        return await handler(params)


# ─── Raft Node ───

class RaftNode:
    """Raft consensus node with real inter-node communication via ClusterMessageBus."""

    HEARTBEAT_INTERVAL = 0.05
    MIN_ELECTION_TIMEOUT = 0.15
    MAX_ELECTION_TIMEOUT = 0.30

    def __init__(self, node_id: str, peer_ids: List[str], bus: ClusterMessageBus):
        self.node_id = node_id
        self.peer_ids = peer_ids
        self.bus = bus
        self.cluster_size = len(peer_ids) + 1
        self.majority = (self.cluster_size // 2) + 1

        # Raft state
        self.state = RaftState()
        self.role = NodeRole.FOLLOWER
        self.commit_index = -1
        self.last_applied = -1

        # Leader state
        self.next_index: Dict[str, int] = {}
        self.match_index: Dict[str, int] = {}

        # Timing
        self.election_timeout = self._random_timeout()
        self.last_heartbeat = time.time()

        # State machine
        self.state_machine: Dict[str, Any] = {}
        self.pending_commands: Dict[str, asyncio.Future] = {}

        # RPC handlers (registered on bus)
        self._rpc_handlers = {
            "request_vote": self._handle_request_vote,
            "append_entries": self._handle_append_entries,
        }

        self._running = False

    def _random_timeout(self) -> float:
        return random.uniform(self.MIN_ELECTION_TIMEOUT, self.MAX_ELECTION_TIMEOUT)

    async def start(self):
        self._running = True
        self.bus.register_node(self.node_id, self._rpc_handlers)
        logger.info(f"Raft node {self.node_id} starting as {self.role.value}")
        asyncio.create_task(self._main_loop())
        asyncio.create_task(self._election_timer())

    async def stop(self):
        self._running = False
        logger.info(f"Raft node {self.node_id} stopped")

    async def _main_loop(self):
        while self._running:
            if self.role == NodeRole.LEADER:
                current_time = time.time()
                if current_time - self.last_heartbeat > self.HEARTBEAT_INTERVAL:
                    await self._send_heartbeats()
                    self.last_heartbeat = current_time
                await self._advance_commit_index()
            await asyncio.sleep(0.01)

    async def _election_timer(self):
        while self._running:
            await asyncio.sleep(0.01)
            if self.role == NodeRole.LEADER:
                continue
            if time.time() - self.last_heartbeat > self.election_timeout:
                await self._start_election()

    # ─── RPC Handlers (called by peers via message bus) ───

    async def _handle_request_vote(self, params: dict) -> dict:
        """Handle incoming vote request from a candidate peer."""
        term = params["term"]
        candidate_id = params["candidate_id"]
        last_log_index = params["last_log_index"]
        last_log_term = params["last_log_term"]

        # If candidate's term is higher, step down and update term
        if term > self.state.current_term:
            self.state.current_term = term
            self.role = NodeRole.FOLLOWER
            self.state.voted_for = None

        vote_granted = False
        if term >= self.state.current_term:
            last_log_ok = (
                last_log_term > self.state.get_last_log_term()
                or (last_log_term == self.state.get_last_log_term()
                    and last_log_index >= self.state.get_last_log_index())
            )
            if (self.state.voted_for is None or self.state.voted_for == candidate_id) and last_log_ok:
                vote_granted = True
                self.state.voted_for = candidate_id
                self.last_heartbeat = time.time()
                self.election_timeout = self._random_timeout()

        logger.debug(
            f"Node {self.node_id} voted for {candidate_id} in term {term}: {vote_granted}"
        )
        return {"term": self.state.current_term, "vote_granted": vote_granted}

    async def _handle_append_entries(self, params: dict) -> dict:
        """Handle incoming AppendEntries (heartbeat/log replication) from leader."""
        term = params["term"]
        leader_id = params["leader_id"]
        prev_log_index = params["prev_log_index"]
        prev_log_term = params["prev_log_term"]
        entries = params.get("entries", [])
        leader_commit = params.get("leader_commit", -1)

        # Term check
        if term < self.state.current_term:
            return {"term": self.state.current_term, "success": False}

        # Step down if we see a higher term leader
        if term > self.state.current_term:
            self.state.current_term = term
            self.state.voted_for = None
        self.role = NodeRole.FOLLOWER
        self.state.voted_for = None  # Don't vote in this term (leader exists)
        self.last_heartbeat = time.time()
        self.election_timeout = self._random_timeout()

        # Log consistency check
        if prev_log_index >= 0:
            prev_entry = self.state.get_entry(prev_log_index)
            if not prev_entry or prev_entry.term != prev_log_term:
                return {"term": self.state.current_term, "success": False}

        # Delete conflicting entries
        if entries:
            first_new_index = entries[0]["index"]
            while self.state.get_last_log_index() >= first_new_index:
                self.state.log.pop()

            # Append new entries
            for e in entries:
                self.state.log.append(LogEntry(
                    index=e["index"],
                    term=e["term"],
                    entry_type=LogEntryType(e["type"]),
                    command=e["command"],
                    timestamp=e.get("timestamp", time.time()),
                ))

        # Update commit index
        if leader_commit > self.commit_index:
            self.commit_index = min(leader_commit, self.state.get_last_log_index())
            await self._apply_committed_entries()

        return {
            "term": self.state.current_term,
            "success": True,
            "match_index": self.state.get_last_log_index(),
        }

    # ─── Leader Election ───

    async def _start_election(self):
        self.role = NodeRole.CANDIDATE
        self.state.current_term += 1
        self.state.voted_for = self.node_id
        self.election_timeout = self._random_timeout()
        self.last_heartbeat = time.time()

        logger.info(f"Node {self.node_id} starting election for term {self.state.current_term}")

        vote_request = {
            "term": self.state.current_term,
            "candidate_id": self.node_id,
            "last_log_index": self.state.get_last_log_index(),
            "last_log_term": self.state.get_last_log_term(),
        }

        votes_received = 1  # Vote for self
        vote_tasks = [
            self.bus.send_rpc(peer, "request_vote", vote_request)
            for peer in self.peer_ids
        ]

        try:
            responses = await asyncio.wait_for(
                asyncio.gather(*vote_tasks, return_exceptions=True),
                timeout=self.election_timeout,
            )
            for resp in responses:
                if isinstance(resp, Exception):
                    continue
                if isinstance(resp, dict) and resp.get("vote_granted"):
                    votes_received += 1
        except asyncio.TimeoutError:
            pass

        if votes_received >= self.majority:
            await self._become_leader()
        else:
            # Reset for next election
            self.role = NodeRole.FOLLOWER
            logger.debug(f"Node {self.node_id} lost election ({votes_received}/{self.majority} votes)")

    async def _become_leader(self):
        self.role = NodeRole.LEADER
        logger.info(f"Node {self.node_id} became leader for term {self.state.current_term}")

        for peer in self.peer_ids:
            self.next_index[peer] = self.state.get_last_log_index() + 1
            self.match_index[peer] = -1

        await self._send_heartbeats()
        self.last_heartbeat = time.time()

    # ─── Heartbeats & Log Replication ───

    async def _send_heartbeats(self):
        for peer in self.peer_ids:
            asyncio.create_task(self._send_append_entries(peer))

    async def _send_append_entries(self, peer: str, entries: Optional[List[LogEntry]] = None):
        next_idx = self.next_index.get(peer, 0)
        prev_log_index = next_idx - 1
        prev_log_term = self.state.get_entry(prev_log_index).term if prev_log_index >= 0 and self.state.get_entry(prev_log_index) else -1

        serialized_entries = [
            {"index": e.index, "term": e.term, "type": e.entry_type.value, "command": e.command, "timestamp": e.timestamp}
            for e in (entries or [])
        ]

        params = {
            "term": self.state.current_term,
            "leader_id": self.node_id,
            "prev_log_index": prev_log_index,
            "prev_log_term": prev_log_term,
            "entries": serialized_entries,
            "leader_commit": self.commit_index,
        }

        response = await self.bus.send_rpc(peer, "append_entries", params)

        if response.get("error"):
            return

        if response["term"] > self.state.current_term:
            self.state.current_term = response["term"]
            self.role = NodeRole.FOLLOWER
            self.state.voted_for = None
            return

        if response.get("success"):
            if entries:
                self.match_index[peer] = response.get("match_index", -1)
                self.next_index[peer] = self.match_index[peer] + 1
        else:
            self.next_index[peer] = max(0, self.next_index[peer] - 1)

    # ─── Commit & Apply ───

    async def _advance_commit_index(self):
        for n in range(self.commit_index + 1, self.state.get_last_log_index() + 1):
            match_count = 1  # Leader
            for peer in self.peer_ids:
                if self.match_index.get(peer, -1) >= n:
                    match_count += 1
            if match_count >= self.majority:
                entry = self.state.get_entry(n)
                if entry and entry.term == self.state.current_term:
                    self.commit_index = n
                    await self._apply_committed_entries()

    async def _apply_committed_entries(self):
        while self.last_applied < self.commit_index:
            self.last_applied += 1
            entry = self.state.get_entry(self.last_applied)
            if entry:
                await self._apply_entry(entry)

    async def _apply_entry(self, entry: LogEntry):
        if entry.entry_type == LogEntryType.COMMAND:
            command_id = entry.command.get("id")
            result = self._execute_command(entry.command)
            if command_id in self.pending_commands:
                future = self.pending_commands.pop(command_id)
                if not future.done():
                    future.set_result(result)

    def _execute_command(self, command: Any) -> Any:
        op = command.get("op")
        key = command.get("key")
        value = command.get("value")
        if op == "set":
            self.state_machine[key] = value
            return {"status": "ok", "value": value}
        elif op == "get":
            return {"status": "ok", "value": self.state_machine.get(key)}
        elif op == "delete":
            self.state_machine.pop(key, None)
            return {"status": "ok"}
        return {"status": "error", "message": "unknown operation"}

    # ─── Public API ───

    async def propose_command(self, command: Any, timeout: float = 5.0) -> Any:
        if self.role != NodeRole.LEADER:
            return {"status": "error", "message": "not leader"}

        command_id = hashlib.sha256(json.dumps(command, sort_keys=True).encode()).hexdigest()[:16]
        command["id"] = command_id

        entry = LogEntry(
            index=len(self.state.log),
            term=self.state.current_term,
            entry_type=LogEntryType.COMMAND,
            command=command,
        )
        self.state.log.append(entry)

        future = asyncio.Future()
        self.pending_commands[command_id] = future

        for peer in self.peer_ids:
            asyncio.create_task(self._send_append_entries(peer, [entry]))

        try:
            return await asyncio.wait_for(future, timeout=timeout)
        except asyncio.TimeoutError:
            self.pending_commands.pop(command_id, None)
            return {"status": "error", "message": "timeout waiting for commit"}

    def get_status(self) -> dict:
        return {
            "node_id": self.node_id,
            "role": self.role.value,
            "term": self.state.current_term,
            "log_size": len(self.state.log),
            "commit_index": self.commit_index,
            "last_applied": self.last_applied,
            "state_machine_size": len(self.state_machine),
            "leader": self.role == NodeRole.LEADER,
        }


# ─── Cluster Manager ───

class RaftCluster:
    def __init__(self, node_ids: List[str]):
        self.node_ids = node_ids
        self.nodes: Dict[str, RaftNode] = {}
        self.bus = ClusterMessageBus()

    async def start(self):
        for node_id in self.node_ids:
            peer_ids = [n for n in self.node_ids if n != node_id]
            node = RaftNode(node_id, peer_ids, self.bus)
            self.nodes[node_id] = node
            await node.start()
        logger.info(f"Raft cluster started with {len(self.nodes)} nodes")

    async def stop(self):
        for node in self.nodes.values():
            await node.stop()

    def get_leader(self) -> Optional[RaftNode]:
        for node in self.nodes.values():
            if node.role == NodeRole.LEADER:
                return node
        return None

    async def submit_command(self, command: Any) -> Any:
        leader = self.get_leader()
        if leader:
            return await leader.propose_command(command)
        return {"status": "error", "message": "no leader"}


# ─── Demo ───

async def demo_raft_consensus():
    print("\n" + "=" * 80)
    print("⚖️  RAFT CONSENSUS LAYER - DEMO")
    print("=" * 80)

    node_ids = ["node_0", "node_1", "node_2", "node_3", "node_4"]
    cluster = RaftCluster(node_ids)

    print("\n🚀 Starting Raft cluster...")
    await cluster.start()
    await asyncio.sleep(0.5)

    leader = cluster.get_leader()
    if leader:
        print(f"  ✓ Leader elected: {leader.node_id}")
    else:
        print("  ⚠ No leader yet, waiting...")
        await asyncio.sleep(1.0)
        leader = cluster.get_leader()

    print("\n📤 Submitting commands to cluster...")
    commands = [
        {"op": "set", "key": "config", "value": {"nodes": 5}},
        {"op": "set", "key": "task_queue", "value": ["task_1", "task_2"]},
        {"op": "set", "key": "status", "value": "active"},
    ]

    for i, cmd in enumerate(commands):
        result = await cluster.submit_command(cmd)
        status = "✓" if result.get("status") == "ok" else "✗"
        print(f"  {status} Command {i + 1}: {cmd['op']} {cmd['key']}")
        await asyncio.sleep(0.1)

    print("\n📊 Checking state replication...")
    await asyncio.sleep(0.3)

    for node_id, node in cluster.nodes.items():
        s = node.get_status()
        print(f"  {node_id}:")
        print(f"    Role: {s['role']}")
        print(f"    Log size: {s['log_size']}")
        print(f"    Commit index: {s['commit_index']}")
        print(f"    State machine keys: {s['state_machine_size']}")

    print("\n🛑 Stopping cluster...")
    await cluster.stop()
    return cluster


if __name__ == "__main__":
    asyncio.run(demo_raft_consensus())
