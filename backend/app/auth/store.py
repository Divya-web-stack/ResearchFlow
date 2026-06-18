from __future__ import annotations

import hashlib
import hmac
import json
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

AUTH_FILE = Path(__file__).resolve().parents[1] / "auth_store.json"
SESSION_HOURS = 24

bearer_scheme = HTTPBearer()


class AuthStore:
    def __init__(self) -> None:
        self.path = AUTH_FILE

        if not self.path.exists():
            self.save(
                {
                    "users": [],
                    "sessions": []
                }
            )

    def load(self) -> dict[str, Any]:
        return json.loads(
            self.path.read_text(encoding="utf-8")
        )

    def save(self, payload: dict[str, Any]) -> None:
        self.path.write_text(
            json.dumps(payload, indent=2),
            encoding="utf-8"
        )

    def _hash_password(
        self,
        password: str,
        salt: str | None = None
    ) -> tuple[str, str]:

        password_salt = salt or secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            password_salt.encode("utf-8"),
            120000
        ).hex()

        return password_salt, password_hash

    def create_user(
        self,
        name: str,
        email: str,
        password: str
    ) -> dict[str, Any]:

        data = self.load()
        normalized_email = email.strip().lower()

        if self.get_user_by_email(normalized_email):
            raise ValueError("Email is already registered.")

        salt, password_hash = self._hash_password(password)

        user = {
            "id": str(uuid.uuid4()),
            "name": name.strip(),
            "email": normalized_email,
            "password_salt": salt,
            "password_hash": password_hash,
            "created_at": datetime.now(timezone.utc).isoformat()
        }

        data.setdefault("users", []).append(user)
        self.save(data)

        return self.public_user(user)

    def get_user_by_email(
        self,
        email: str
    ) -> dict[str, Any] | None:

        data = self.load()
        normalized_email = email.strip().lower()

        return next(
            (
                user
                for user in data.get("users", [])
                if user.get("email") == normalized_email
            ),
            None
        )

    def get_user_by_id(
        self,
        user_id: str
    ) -> dict[str, Any] | None:

        data = self.load()

        return next(
            (
                user
                for user in data.get("users", [])
                if user.get("id") == user_id
            ),
            None
        )

    def verify_password(
        self,
        user: dict[str, Any],
        password: str
    ) -> bool:

        _, password_hash = self._hash_password(
            password,
            user["password_salt"]
        )

        return hmac.compare_digest(
            password_hash,
            user["password_hash"]
        )

    def create_session(
        self,
        user_id: str
    ) -> dict[str, Any]:

        data = self.load()
        token = secrets.token_urlsafe(32)
        expires_at = (
            datetime.now(timezone.utc)
            + timedelta(hours=SESSION_HOURS)
        ).isoformat()

        session = {
            "token": token,
            "user_id": user_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "expires_at": expires_at
        }

        data.setdefault("sessions", []).append(session)
        self.save(data)

        return session

    def get_session(
        self,
        token: str
    ) -> dict[str, Any] | None:

        data = self.load()

        session = next(
            (
                item
                for item in data.get("sessions", [])
                if item.get("token") == token
            ),
            None
        )

        if not session:
            return None

        expires_at = datetime.fromisoformat(
            session["expires_at"]
        )

        if expires_at < datetime.now(timezone.utc):
            self.delete_session(token)
            return None

        return session

    def delete_session(
        self,
        token: str
    ) -> None:

        data = self.load()
        data["sessions"] = [
            session
            for session in data.get("sessions", [])
            if session.get("token") != token
        ]
        self.save(data)

    def public_user(
        self,
        user: dict[str, Any]
    ) -> dict[str, Any]:

        return {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "created_at": user["created_at"]
        }


auth_store = AuthStore()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
) -> dict[str, Any]:

    session = auth_store.get_session(
        credentials.credentials
    )

    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session."
        )

    user = auth_store.get_user_by_id(
        session["user_id"]
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found."
        )

    return auth_store.public_user(user)
