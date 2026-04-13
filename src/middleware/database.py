#!/usr/bin/env python3
"""SQLAlchemy ORM — Typed Database Models
Replaces raw SQL with typed, validated database models for all entities.
"""

import json
import os
import uuid
from datetime import UTC, datetime
from enum import Enum as PyEnum
from typing import Any

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship, sessionmaker
from sqlalchemy.pool import StaticPool

# ──────────────────────────────────────────────────────────────
# Database Configuration
# ──────────────────────────────────────────────────────────────

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./neuralblitz.db"
)

# Detect SQLite and use appropriate connect args
_is_sqlite = "sqlite" in DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if _is_sqlite else {},
    poolclass=StaticPool if _is_sqlite else None,
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ──────────────────────────────────────────────────────────────
# Enum Types
# ──────────────────────────────────────────────────────────────

class AgentStatus(str, PyEnum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    COMPLETED = "completed"

class AgentType(str, PyEnum):
    INFERENCE = "inference"
    REASONING = "reasoning"
    CODE_GEN = "code_gen"
    RESEARCH = "research"
    DATA_ANALYSIS = "data_analysis"

class LogLevel(str, PyEnum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


# ──────────────────────────────────────────────────────────────
# ORM Models
# ──────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        Index("ix_users_username", "username", unique=True),
        Index("ix_users_email", "email", unique=True),
    )

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(64), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(32), default="viewer", nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC),
                       onupdate=lambda: datetime.now(UTC))
    metadata_json = Column(Text, default="{}")

    # Relationships
    agents = relationship("Agent", back_populates="owner", lazy="dynamic")
    api_keys = relationship("ApiKey", back_populates="user", lazy="dynamic")

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "agent_count": self.agents.count() if hasattr(self.agents, 'count') else 0,
            "metadata": json.loads(self.metadata_json or "{}"),
        }


class ApiKey(Base):
    __tablename__ = "api_keys"
    __table_args__ = (
        Index("ix_api_keys_key_hash", "key_hash", unique=True),
        Index("ix_api_keys_user_id", "user_id"),
    )

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    key_hash = Column(String(64), unique=True, nullable=False)
    name = Column(String(128), nullable=False)
    is_active = Column(Boolean, default=True)
    last_used_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    expires_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="api_keys")

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "is_active": self.is_active,
            "last_used_at": self.last_used_at.isoformat() if self.last_used_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
        }


class Agent(Base):
    __tablename__ = "agents"
    __table_args__ = (
        Index("ix_agents_user_id", "user_id"),
        Index("ix_agents_status", "status"),
        Index("ix_agents_type", "type"),
    )

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    name = Column(String(128), nullable=False)
    type = Column(String(32), default=AgentType.INFERENCE.value, nullable=False)
    status = Column(String(32), default=AgentStatus.IDLE.value, nullable=False)
    config_json = Column(Text, default="{}")
    state_json = Column(Text, default="{}")
    precision = Column(Float, default=0.5)
    free_energy = Column(Float, default=0.0)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC),
                       onupdate=lambda: datetime.now(UTC))
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)

    # Relationships
    owner = relationship("User", back_populates="agents")
    metrics = relationship("AgentMetric", back_populates="agent", lazy="dynamic")
    events = relationship("AgentEvent", back_populates="agent", lazy="dynamic")

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "status": self.status,
            "precision": self.precision,
            "free_energy": self.free_energy,
            "config": json.loads(self.config_json or "{}"),
            "state": json.loads(self.state_json or "{}"),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error_message": self.error_message,
        }


class AgentMetric(Base):
    __tablename__ = "agent_metrics"
    __table_args__ = (
        Index("ix_metrics_agent_time", "agent_id", "timestamp"),
        Index("ix_metrics_timestamp", "timestamp"),
    )

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(String(36), ForeignKey("agents.id"), nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(UTC), index=True)
    cpu_usage = Column(Float, default=0.0)
    memory_usage = Column(Float, default=0.0)
    response_time_ms = Column(Float, default=0.0)
    tokens_processed = Column(Integer, default=0)
    error_rate = Column(Float, default=0.0)
    throughput = Column(Float, default=0.0)
    precision = Column(Float, default=0.0)
    custom_metrics_json = Column(Text, default="{}")

    agent = relationship("Agent", back_populates="metrics")

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "cpu_usage": self.cpu_usage,
            "memory_usage": self.memory_usage,
            "response_time_ms": self.response_time_ms,
            "tokens_processed": self.tokens_processed,
            "error_rate": self.error_rate,
            "throughput": self.throughput,
            "precision": self.precision,
            "custom_metrics": json.loads(self.custom_metrics_json or "{}"),
        }


class AgentEvent(Base):
    __tablename__ = "agent_events"
    __table_args__ = (
        Index("ix_events_agent_time", "agent_id", "timestamp"),
        Index("ix_events_type", "event_type"),
        Index("ix_events_severity", "severity"),
    )

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(String(36), ForeignKey("agents.id"), nullable=False)
    event_type = Column(String(64), nullable=False)
    severity = Column(String(16), default=LogLevel.INFO.value)
    message = Column(Text, nullable=False)
    data_json = Column(Text, default="{}")
    timestamp = Column(DateTime, default=lambda: datetime.now(UTC), index=True)

    agent = relationship("Agent", back_populates="events")

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "event_type": self.event_type,
            "severity": self.severity,
            "message": self.message,
            "data": json.loads(self.data_json or "{}"),
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }


class Plugin(Base):
    __tablename__ = "plugins"
    __table_args__ = (
        Index("ix_plugins_name_version", "name", "version", unique=True),
    )

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(128), nullable=False)
    version = Column(String(32), nullable=False)
    description = Column(Text, default="")
    author = Column(String(128), default="")
    is_enabled = Column(Boolean, default=True)
    is_valid = Column(Boolean, default=True)
    validation_errors = Column(Text, default="[]")
    config_json = Column(Text, default="{}")
    installed_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC),
                       onupdate=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "is_enabled": self.is_enabled,
            "is_valid": self.is_valid,
            "validation_errors": json.loads(self.validation_errors or "[]"),
            "config": json.loads(self.config_json or "{}"),
            "installed_at": self.installed_at.isoformat() if self.installed_at else None,
        }


# ──────────────────────────────────────────────────────────────
# Database Session Helper
# ──────────────────────────────────────────────────────────────

def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables (if they don't exist)."""
    try:
        Base.metadata.create_all(bind=engine)
    except Exception:
        pass  # Tables already exist — this is fine


def seed_db():
    """Seed initial data."""
    init_db()
    db = SessionLocal()
    try:
        if db.query(User).count() == 0:
            admin = User(
                id="admin-seed-001",
                username="admin",
                email="admin@neuralblitz.local",
                hashed_password="$2b$12$dummy",  # Replace with real hash
                role="admin",
                is_active=True,
            )
            db.add(admin)
            db.commit()
    finally:
        db.close()


# ──────────────────────────────────────────────────────────────
# CRUD Operations
# ──────────────────────────────────────────────────────────────

class Repository:
    """Generic repository with common CRUD operations."""

    def __init__(self, model: type[Base], db: Session):
        self.model = model
        self.db = db

    def get(self, id: str) -> Any | None:
        return self.db.query(self.model).filter(self.model.id == id).first()

    def list(self, limit: int = 100, offset: int = 0) -> list[Any]:
        return self.db.query(self.model).order_by(
            self.model.created_at.desc()
        ).offset(offset).limit(limit).all()

    def create(self, **kwargs) -> Any:
        instance = self.model(**kwargs)
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)
        return instance

    def update(self, id: str, **kwargs) -> Any | None:
        instance = self.get(id)
        if instance:
            for key, value in kwargs.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
            instance.updated_at = datetime.now(UTC)
            self.db.commit()
            self.db.refresh(instance)
        return instance

    def delete(self, id: str) -> bool:
        instance = self.get(id)
        if instance:
            self.db.delete(instance)
            self.db.commit()
            return True
        return False

    def count(self) -> int:
        return self.db.query(self.model).count()


# ──────────────────────────────────────────────────────────────
# Initialize on import
# ──────────────────────────────────────────────────────────────

init_db()
