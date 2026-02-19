import uuid
from datetime import date, datetime, time
from typing import Optional

from pydantic import BaseModel

from app.schemas.base import AppModel


# ─── Job Fair ─────────────────────────────────────────────────────────────────

class JobFairCreate(BaseModel):
    name: str
    location: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    theme: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    is_public: bool = False


class JobFairUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    theme: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    is_public: Optional[bool] = None
    status: Optional[str] = None


class JobFairOut(AppModel):
    id: uuid.UUID
    name: str
    location: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    theme: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    is_public: bool
    status: str
    created_by_org_id: uuid.UUID
    created_at: datetime


# ─── Fair invitations ─────────────────────────────────────────────────────────

class InviteEmployersRequest(BaseModel):
    """Body for bulk-inviting employers to a fair."""
    employer_ids: list[uuid.UUID]


class InviteEmployersByEmailRequest(BaseModel):
    """Body for inviting new employers by email (creates accounts if needed)."""
    emails: list[str]


class InviteCandidatesRequest(BaseModel):
    """Body for bulk-inviting existing candidates to a fair."""
    candidate_ids: list[uuid.UUID]


class InviteCandidatesByEmailRequest(BaseModel):
    """Body for inviting new candidates by email."""
    emails: list[str]


# ─── RSVP ─────────────────────────────────────────────────────────────────────

class RSVPRequest(BaseModel):
    status: str  # "yes" | "no"


class FairEmployerOut(AppModel):
    id: uuid.UUID
    fair_id: uuid.UUID
    employer_id: uuid.UUID
    rsvp_status: str
    qr_code: Optional[str] = None
    invited_at: datetime
    rsvp_at: Optional[datetime] = None


class FairCandidateOut(AppModel):
    id: uuid.UUID
    fair_id: uuid.UUID
    candidate_id: uuid.UUID
    rsvp_status: str
    check_in_time: Optional[datetime] = None
    request_status: Optional[str] = None


# ─── Check-in ─────────────────────────────────────────────────────────────────

class CheckInRequest(BaseModel):
    """Candidate self-check-in. fair_id comes from the URL path."""
    pass  # No body needed — identity from JWT, fair from path


class QRScanRequest(BaseModel):
    """Candidate scans an employer's booth QR code."""
    qr_code: str
