"""
Supabase JWT verification for FastAPI.

Supabase issues JWTs signed with HS256 using the project's JWT secret.
We verify the token, extract the user's Supabase UUID (sub claim), then
look up the corresponding row in our local `users` table.

Uses only Python stdlib (hmac + hashlib) so there is no dependency on the
`cryptography` package, which can have native extension issues in some envs.
"""
import base64
import hashlib
import hmac
import json
import time
import uuid
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models.user import User

settings = get_settings()
bearer_scheme = HTTPBearer()


def _b64url_decode(segment: str) -> bytes:
    """Decode a base64url segment, padding as needed."""
    padding = 4 - len(segment) % 4
    if padding != 4:
        segment += "=" * padding
    return base64.urlsafe_b64decode(segment)


def _decode_supabase_jwt(token: str) -> dict:
    """
    Decode and verify a Supabase HS256 JWT using Python stdlib only.
    Raises HTTPException on invalid signature or expired token.
    """
    try:
        parts = token.split(".")
        if len(parts) != 3:
            raise ValueError("Malformed JWT: expected 3 parts")

        header_b64, payload_b64, signature_b64 = parts

        # Verify algorithm from header
        header = json.loads(_b64url_decode(header_b64))
        if header.get("alg") != "HS256":
            raise ValueError(f"Unsupported algorithm: {header.get('alg')}")

        # Verify HMAC-SHA256 signature
        secret = settings.supabase_jwt_secret.encode()
        signing_input = f"{header_b64}.{payload_b64}".encode()
        expected_sig = hmac.new(secret, signing_input, hashlib.sha256).digest()
        actual_sig = _b64url_decode(signature_b64)

        if not hmac.compare_digest(expected_sig, actual_sig):
            raise ValueError("Invalid signature")

        payload = json.loads(_b64url_decode(payload_b64))

        # Validate expiry
        exp = payload.get("exp")
        if exp and time.time() > exp:
            raise ValueError("Token has expired")

        return payload

    except (ValueError, KeyError, json.JSONDecodeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {exc}",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    FastAPI dependency: verify the Supabase JWT and return the local User record.

    The Supabase JWT `sub` claim holds the user's UUID in Supabase Auth.
    We use the same UUID as the primary key in our local `users` table so
    the two are always in sync.
    """
    payload = _decode_supabase_jwt(credentials.credentials)

    supabase_user_id: Optional[str] = payload.get("sub")
    if not supabase_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing subject claim",
        )

    try:
        user_uuid = uuid.UUID(supabase_user_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token",
        ) from exc

    user = db.get(User, user_uuid)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User account not found. Please complete registration.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated.",
        )

    return user


# ─── Role-specific dependencies ──────────────────────────────────────────────

def require_host_org(current_user: User = Depends(get_current_user)) -> User:
    if current_user.user_type != "host_org":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted to host organizations.",
        )
    return current_user


def require_employer(current_user: User = Depends(get_current_user)) -> User:
    if current_user.user_type != "employer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted to employers.",
        )
    return current_user


def require_candidate(current_user: User = Depends(get_current_user)) -> User:
    if current_user.user_type != "candidate":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted to candidates.",
        )
    return current_user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.user_type != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted to administrators.",
        )
    return current_user


def require_host_org_or_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.user_type not in ("host_org", "super_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted to host organizations or administrators.",
        )
    return current_user
