"""
POST /users         — register a local profile after Supabase Auth signup
GET  /users/me      — return the current user's profile
PATCH /users/me     — update last_login (called automatically on login)
"""
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserOut

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserCreate, db: Session = Depends(get_db)):
    """
    Creates the local user profile row that mirrors a Supabase Auth account.
    Called once from the frontend immediately after Supabase sign-up succeeds.
    The `id` in the payload must equal the Supabase user UUID.
    """
    existing = db.get(User, payload.id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User profile already exists.",
        )

    user = User(
        id=payload.id,
        email=payload.email,
        user_type=payload.user_type,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me/last-login", response_model=UserOut)
def update_last_login(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Called by the frontend on every successful login to update last_login."""
    current_user.last_login = datetime.now(timezone.utc)
    db.commit()
    db.refresh(current_user)
    return current_user
