import uuid
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, EmailStr


# ─── User ─────────────────────────────────────────────────────────────────────

class UserBase(BaseModel):
    email: EmailStr
    user_type: Literal["candidate", "employer", "host_org", "super_admin"]


class UserCreate(UserBase):
    """
    Called on first login after Supabase Auth creates the auth record.
    The `id` must match the Supabase user UUID.
    """
    id: uuid.UUID


class UserOut(UserBase):
    id: uuid.UUID
    created_at: datetime
    last_login: Optional[datetime]
    is_active: bool

    model_config = {"from_attributes": True}


# ─── Host Organization ────────────────────────────────────────────────────────

class HostOrgCreate(BaseModel):
    name: str
    mission: Optional[str] = None
    logo_url: Optional[str] = None
    contact_name: Optional[str] = None
    phone: Optional[str] = None


class HostOrgUpdate(BaseModel):
    name: Optional[str] = None
    mission: Optional[str] = None
    logo_url: Optional[str] = None
    contact_name: Optional[str] = None
    phone: Optional[str] = None


class HostOrgOut(HostOrgCreate):
    id: uuid.UUID
    user_id: uuid.UUID
    subscription_tier: Optional[str] = None
    subscription_status: Optional[str] = None

    model_config = {"from_attributes": True}


# ─── Employer ─────────────────────────────────────────────────────────────────

class EmployerCreate(BaseModel):
    company_name: str
    industry: Optional[str] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    contact_person: Optional[str] = None
    description: Optional[str] = None


class EmployerUpdate(BaseModel):
    company_name: Optional[str] = None
    industry: Optional[str] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    contact_person: Optional[str] = None
    description: Optional[str] = None


class EmployerOut(EmployerCreate):
    id: uuid.UUID
    user_id: uuid.UUID

    model_config = {"from_attributes": True}


# ─── Candidate ────────────────────────────────────────────────────────────────

class CandidateCreate(BaseModel):
    first_name: str
    last_name: str
    phone: Optional[str] = None
    home_address: Optional[str] = None
    linkedin_url: Optional[str] = None


class CandidateUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    home_address: Optional[str] = None
    linkedin_url: Optional[str] = None


class CandidateOut(BaseModel):
    """Safe public representation — never exposes home_address or barriers."""
    id: uuid.UUID
    user_id: uuid.UUID
    first_name: str
    last_name: str
    phone: Optional[str]
    linkedin_url: Optional[str]
    resume_url: Optional[str]

    model_config = {"from_attributes": True}


class CandidateDetailOut(CandidateOut):
    """Extended view for ECs only — includes home_address for commute matching."""
    home_address: Optional[str]
