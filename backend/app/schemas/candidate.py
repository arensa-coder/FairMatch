import uuid
from datetime import date
from typing import Optional

from pydantic import BaseModel

from app.schemas.base import AppModel


# ─── Skills ───────────────────────────────────────────────────────────────────

class CandidateSkillCreate(BaseModel):
    skill_name: str
    proficiency_level: Optional[str] = None
    years_experience: Optional[int] = None


class CandidateSkillOut(AppModel):
    id: uuid.UUID
    skill_name: str
    proficiency_level: Optional[str] = None
    years_experience: Optional[int] = None


# ─── Work History ─────────────────────────────────────────────────────────────

class WorkHistoryCreate(BaseModel):
    company: str
    title: str
    start_date: date
    end_date: Optional[date] = None
    description: Optional[str] = None


class WorkHistoryOut(AppModel):
    id: uuid.UUID
    company: str
    title: str
    start_date: date
    end_date: Optional[date] = None
    description: Optional[str] = None


# ─── Education ────────────────────────────────────────────────────────────────

class EducationCreate(BaseModel):
    institution: str
    degree: Optional[str] = None
    field: Optional[str] = None
    graduation_year: Optional[int] = None


class EducationOut(AppModel):
    id: uuid.UUID
    institution: str
    degree: Optional[str] = None
    field: Optional[str] = None
    graduation_year: Optional[int] = None


# ─── Certifications ───────────────────────────────────────────────────────────

class CertificationCreate(BaseModel):
    certification_name: str
    issuing_org: Optional[str] = None
    date_obtained: Optional[date] = None
    expiration_date: Optional[date] = None


class CertificationOut(AppModel):
    id: uuid.UUID
    certification_name: str
    issuing_org: Optional[str] = None
    date_obtained: Optional[date] = None
    expiration_date: Optional[date] = None


# ─── Preferences ──────────────────────────────────────────────────────────────

class CandidatePreferenceCreate(BaseModel):
    max_commute_car_minutes: Optional[int] = None
    max_commute_transit_minutes: Optional[int] = None
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None
    preferred_schedule: Optional[str] = None
    preferred_industries: Optional[list[str]] = None


class CandidatePreferenceOut(AppModel):
    id: uuid.UUID
    max_commute_car_minutes: Optional[int] = None
    max_commute_transit_minutes: Optional[int] = None
    # Salary fields excluded from public output — only returned to candidate/EC
    preferred_schedule: Optional[str] = None
    preferred_industries: Optional[list[str]] = None


# ─── Barriers (EC-only) ───────────────────────────────────────────────────────

class CandidateBarrierUpdate(BaseModel):
    """
    Used by ECs to update barrier flags. Never exposed to employers.
    Sensitive text fields are stored encrypted in the DB.
    """
    is_justice_impacted: Optional[bool] = None
    justice_impact_details: Optional[str] = None  # encrypted at rest
    has_housing_instability: Optional[bool] = None
    has_transportation_barriers: Optional[bool] = None
    has_childcare_needs: Optional[bool] = None
    needs_health_accommodations: Optional[bool] = None
    accommodation_details: Optional[str] = None   # encrypted at rest
    has_language_barriers: Optional[bool] = None
    primary_language: Optional[str] = None
    case_management_notes: Optional[str] = None   # encrypted at rest


class CandidateBarrierOut(AppModel):
    """EC-only view of barrier data. Router enforces host_org access."""
    id: uuid.UUID
    is_justice_impacted: bool
    has_housing_instability: bool
    has_transportation_barriers: bool
    has_childcare_needs: bool
    needs_health_accommodations: bool
    has_language_barriers: bool
    primary_language: Optional[str] = None
    # Encrypted detail fields only returned to authorized ECs
    justice_impact_details: Optional[str] = None
    accommodation_details: Optional[str] = None
    case_management_notes: Optional[str] = None
