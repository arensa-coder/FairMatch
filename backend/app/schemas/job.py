import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Optional

from pydantic import BaseModel, model_validator

from app.schemas.base import AppModel


# ─── Job Posting ──────────────────────────────────────────────────────────────

class JobPostingCreate(BaseModel):
    fair_employer_id: uuid.UUID
    job_order_name: str
    job_order_external_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    description_url: Optional[str] = None
    sector: Optional[str] = None
    employer_industry: Optional[str] = None
    status: str = "active"
    job_order_notes: Optional[str] = None  # EC-only
    contract_type: str
    hours_per_week: Optional[int] = None
    anticipated_schedule: Optional[str] = None
    anticipated_start_date: Optional[date] = None
    wage_measurement: str
    wage_min: Optional[Decimal] = None
    wage_max: Optional[Decimal] = None
    benefits: Optional[list[str]] = None
    location_type: str
    remote_days: Optional[int] = None
    job_address_id: Optional[uuid.UUID] = None
    job_address_text: Optional[str] = None
    supervisor_name: Optional[str] = None
    supervisor_contact_id: Optional[uuid.UUID] = None
    supervisor_email: Optional[str] = None
    supervisor_phone: Optional[str] = None
    education_required: Optional[str] = None
    certifications_required: Optional[list[str]] = None
    background_check_required: bool = False
    other_requirements: Optional[str] = None
    experience_level: Optional[str] = None
    number_of_openings: int = 1
    close_date: Optional[date] = None
    application_url: Optional[str] = None
    how_to_apply: Optional[str] = None
    screening_questions: Optional[list[dict[str, Any]]] = None
    recommended_attire: Optional[str] = None
    interview_directions: Optional[str] = None
    uses_internal_application: bool = False
    is_anonymous: bool = False
    required_skills: Optional[list[dict[str, Any]]] = None  # [{"skill_name": ..., "is_required": bool}]


class JobPostingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    job_order_notes: Optional[str] = None
    contract_type: Optional[str] = None
    hours_per_week: Optional[int] = None
    anticipated_schedule: Optional[str] = None
    anticipated_start_date: Optional[date] = None
    wage_measurement: Optional[str] = None
    wage_min: Optional[Decimal] = None
    wage_max: Optional[Decimal] = None
    benefits: Optional[list[str]] = None
    location_type: Optional[str] = None
    remote_days: Optional[int] = None
    job_address_text: Optional[str] = None
    education_required: Optional[str] = None
    background_check_required: Optional[bool] = None
    experience_level: Optional[str] = None
    number_of_openings: Optional[int] = None
    close_date: Optional[date] = None
    uses_internal_application: Optional[bool] = None
    is_anonymous: Optional[bool] = None


class JobPostingOut(AppModel):
    id: uuid.UUID
    fair_employer_id: uuid.UUID
    job_order_name: str
    title: str
    description: Optional[str] = None
    sector: Optional[str] = None
    status: str
    contract_type: str
    hours_per_week: Optional[int] = None
    anticipated_schedule: Optional[str] = None
    anticipated_start_date: Optional[date] = None
    wage_measurement: str
    wage_min: Optional[Decimal] = None
    wage_max: Optional[Decimal] = None
    wage_average: Optional[Decimal] = None
    benefits: Optional[list[str]] = None
    location_type: str
    remote_days: Optional[int] = None
    job_address_text: Optional[str] = None
    education_required: Optional[str] = None
    certifications_required: Optional[list[str]] = None
    background_check_required: bool
    experience_level: Optional[str] = None
    number_of_openings: int
    close_date: Optional[date] = None
    application_url: Optional[str] = None
    uses_internal_application: bool
    is_anonymous: bool
    recommended_attire: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class JobPostingECOut(JobPostingOut):
    """Extended view for ECs — includes internal notes and employer ranking."""
    job_order_notes: Optional[str] = None
    employer_ranking: Optional[int] = None
    job_order_external_id: Optional[str] = None


# ─── Match Scores ─────────────────────────────────────────────────────────────

class MatchScoreOut(AppModel):
    id: uuid.UUID
    candidate_id: uuid.UUID
    job_id: uuid.UUID
    fair_id: uuid.UUID
    score: int
    factors: Optional[dict[str, Any]] = None
    ec_status: str
    generated_at: datetime


class MatchWithJobOut(MatchScoreOut):
    """Match score with embedded job details — used by the candidate match list view."""
    job: Optional["JobPostingOut"] = None


class MatchReviewAction(BaseModel):
    """EC's decision on a pending match."""
    action: str  # "approved" | "declined" | "held"
    ec_note: Optional[str] = None


# ─── Candidate Job Interactions ───────────────────────────────────────────────

class InteractionCreate(BaseModel):
    job_id: uuid.UUID
    interaction_type: str  # "liked" | "ignored" | "applied" | "viewed"
    notes: Optional[str] = None


class InteractionOut(AppModel):
    id: uuid.UUID
    candidate_id: uuid.UUID
    job_id: uuid.UUID
    interaction_type: str
    timestamp: datetime
    notes: Optional[str] = None


# ─── Applications ─────────────────────────────────────────────────────────────

class ApplicationCreate(BaseModel):
    job_id: uuid.UUID
    application_type: str  # "internal" | "external"
    application_data: Optional[dict[str, Any]] = None


class ApplicationOut(AppModel):
    id: uuid.UUID
    candidate_id: uuid.UUID
    job_id: uuid.UUID
    application_type: str
    status: str
    submitted_at: datetime
    reviewed_by_ec: bool
    ec_approved_at: Optional[datetime] = None


# ─── Hiring Outcomes ─────────────────────────────────────────────────────────

class HiringOutcomeCreate(BaseModel):
    candidate_id: uuid.UUID
    employer_id: uuid.UUID
    job_id: Optional[uuid.UUID] = None
    status: str  # "offered" | "accepted" | "started" | "declined"
    offer_date: Optional[date] = None
    accept_date: Optional[date] = None
    start_date: Optional[date] = None
