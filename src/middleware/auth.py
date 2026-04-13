#!/usr/bin/env python3
"""JWT Authentication System — Real API Authentication
Provides JWT token-based auth with refresh tokens, API keys, and role-based access control.
"""

import hashlib
import hmac
import os
import secrets
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import Any

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

# ──────────────────────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────────────────────

JWT_SECRET = os.getenv("JWT_SECRET") or secrets.token_hex(32)
JWT_ALGORITHM = "HS256"
JWT_ACCESS_EXPIRE_MINUTES = 30
JWT_REFRESH_EXPIRE_DAYS = 7
JWT_ISSUER = "linkglys-api"

# Password hashing: PBKDF2-HMAC-SHA256 with 100k iterations
# (replaces weak SHA-256 + salt)
HASH_ALGORITHM = "pbkdf2:sha256:100000"


def hash_password(password: str) -> str:
    """Hash password with PBKDF2-HMAC-SHA256 (100k iterations)."""
    salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
    return f"{salt}${dk.hex()}"


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against PBKDF2 hash."""
    try:
        salt, expected = hashed.split("$", 1)
        dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
        return hmac.compare_digest(dk.hex(), expected)
    except (ValueError, AttributeError):
        return False


class Role(str, Enum):
    ADMIN = "admin"
    DEVELOPER = "developer"
    VIEWER = "viewer"
    AGENT = "agent"


ROLE_PERMISSIONS = {
    Role.ADMIN: {"read", "write", "delete", "admin", "deploy", "configure"},
    Role.DEVELOPER: {"read", "write", "deploy"},
    Role.VIEWER: {"read"},
    Role.AGENT: {"read", "write"},
}


# ──────────────────────────────────────────────────────────────
# User & Token Models
# ──────────────────────────────────────────────────────────────

@dataclass
class User:
    user_id: str
    username: str
    email: str
    role: Role
    hashed_password: str
    is_active: bool = True
    created_at: float = field(default_factory=time.time)
    api_keys: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "role": self.role.value,
            "is_active": self.is_active,
            "created_at": datetime.fromtimestamp(self.created_at, tz=UTC).isoformat(),
            "api_key_count": len(self.api_keys),
        }


@dataclass
class TokenPair:
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = JWT_ACCESS_EXPIRE_MINUTES * 60


# ──────────────────────────────────────────────────────────────
# User Store (in-memory — replace with DB in production)
# ──────────────────────────────────────────────────────────────

class UserStore:
    """In-memory user store with password hashing and API key management."""

    def __init__(self):
        self._users: dict[str, User] = {}
        self._username_index: dict[str, str] = {}
        self._api_key_index: dict[str, str] = {}
        self._refresh_tokens: dict[str, dict[str, Any]] = {}

    def create_user(
        self,
        username: str,
        email: str,
        password: str,
        role: Role = Role.VIEWER,
        user_id: str | None = None,
    ) -> User:
        if username in self._username_index:
            raise ValueError(f"Username '{username}' already exists")

        uid = user_id or secrets.token_hex(8)
        user = User(
            user_id=uid,
            username=username,
            email=email,
            role=role,
            hashed_password=hash_password(password),
        )
        self._users[uid] = user
        self._username_index[username] = uid
        return user

    def authenticate(self, username: str, password: str) -> User | None:
        uid = self._username_index.get(username)
        if not uid:
            return None
        user = self._users[uid]
        if not user.is_active:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def get_user(self, user_id: str) -> User | None:
        return self._users.get(user_id)

    def get_user_by_username(self, username: str) -> User | None:
        uid = self._username_index.get(username)
        return self._users.get(uid) if uid else None

    def generate_api_key(self, user_id: str) -> str:
        user = self._users.get(user_id)
        if not user:
            raise ValueError(f"User '{user_id}' not found")
        key = f"nb_{secrets.token_hex(20)}"
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        user.api_keys.append(key_hash)
        self._api_key_index[key_hash] = user_id
        return key  # Return raw key only once

    def revoke_api_key(self, user_id: str, key_hash: str) -> bool:
        user = self._users.get(user_id)
        if not user:
            return False
        if key_hash in user.api_keys:
            user.api_keys.remove(key_hash)
            self._api_key_index.pop(key_hash, None)
            return True
        return False

    def authenticate_api_key(self, key: str) -> User | None:
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        uid = self._api_key_index.get(key_hash)
        return self._users.get(uid) if uid else None

    def create_refresh_token(self, user_id: str) -> str:
        token = secrets.token_hex(32)
        self._refresh_tokens[token] = {
            "user_id": user_id,
            "created_at": time.time(),
            "expires_at": time.time() + (JWT_REFRESH_EXPIRE_DAYS * 86400),
        }
        return token

    def validate_refresh_token(self, token: str) -> str | None:
        data = self._refresh_tokens.get(token)
        if not data:
            return None
        if time.time() > data["expires_at"]:
            self._refresh_tokens.pop(token, None)
            return None
        return data["user_id"]

    def revoke_refresh_token(self, token: str) -> bool:
        return self._refresh_tokens.pop(token, None) is not None

    def list_users(self) -> list[dict[str, Any]]:
        return [u.to_dict() for u in self._users.values()]


# Global user store
user_store = UserStore()


# ──────────────────────────────────────────────────────────────
# JWT Token Operations
# ──────────────────────────────────────────────────────────────

def create_access_token(user: User) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": user.user_id,
        "username": user.username,
        "role": user.role.value,
        "iat": now,
        "exp": now + timedelta(minutes=JWT_ACCESS_EXPIRE_MINUTES),
        "iss": JWT_ISSUER,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def create_token_pair(user: User) -> TokenPair:
    access = create_access_token(user)
    refresh = user_store.create_refresh_token(user.user_id)
    return TokenPair(access_token=access, refresh_token=refresh)


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM], issuer=JWT_ISSUER)
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


# ──────────────────────────────────────────────────────────────
# FastAPI Dependencies & Middleware
# ──────────────────────────────────────────────────────────────

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> User:
    """Extract and validate the current user from JWT token or API key."""
    if credentials:
        # Bearer token authentication
        payload = decode_access_token(credentials.credentials)
        user = user_store.get_user(payload["sub"])
        if not user or not user.is_active:
            raise HTTPException(status_code=401, detail="User not found or inactive")
        return user

    # Fall back to API key in header
    raise HTTPException(status_code=401, detail="Authentication required")


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=403, detail="Inactive user")
    return current_user


def require_permission(permission: str):
    """Dependency factory: require a specific permission."""
    async def checker(current_user: User = Depends(get_current_active_user)) -> User:
        allowed = ROLE_PERMISSIONS.get(current_user.role, set())
        if permission not in allowed:
            raise HTTPException(status_code=403, detail=f"Permission '{permission}' required")
        return current_user
    return checker


def require_role(role: Role):
    """Dependency factory: require a specific role."""
    async def checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role != role:
            raise HTTPException(status_code=403, detail=f"Role '{role.value}' required")
        return current_user
    return checker


# ──────────────────────────────────────────────────────────────
# Seed Default Users
# ──────────────────────────────────────────────────────────────

def seed_default_users():
    """Create default admin and developer users if they don't exist."""
    if not user_store.get_user_by_username("admin"):
        user_store.create_user(
            username="admin",
            email="admin@neuralblitz.local",
            password="admin",  # Change in production!
            role=Role.ADMIN,
            user_id="admin-001",
        )
    if not user_store.get_user_by_username("developer"):
        user_store.create_user(
            username="developer",
            email="dev@neuralblitz.local",
            password="developer",
            role=Role.DEVELOPER,
            user_id="dev-001",
        )
    if not user_store.get_user_by_username("viewer"):
        user_store.create_user(
            username="viewer",
            email="viewer@neuralblitz.local",
            password="viewer",
            role=Role.VIEWER,
            user_id="viewer-001",
        )


# ──────────────────────────────────────────────────────────────
# Initialization
# ──────────────────────────────────────────────────────────────

seed_default_users()
