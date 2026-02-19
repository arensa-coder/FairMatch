import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Boolean, Date, DateTime, Enum, ForeignKey, Integer,
    Numeric, String, Text, func
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

JobStatusEnum = Enum(
    "active", "inactive", "filled", "closed",
    name="job_status_enum"
)

ContractTypeEnum = Enum(
    "full-time", "part-time", "contract", "seasonal", "temporary", "internship",
    name="contract_type_enum"
)

WageMeasurementEnum = Enum(
    "hourly", "weekly", "monthly", "annual",
    name="wage_measurement_enum"
)

LocationTypeEnum = Enum(
    "on-site", "remote", "hybrid",
    name="location_type_enum"
)

InteractionTypeEnum = Enum(
    "liked", "ignored", "applied", "viewed",
    name="interaction_type_enum"
)

ApplicationTypeEnum = Enum(
    "internal", "external",
    name="application_type_enum"
)

ApplicationStatusEnum = Enum(
    "submitted", "under_review", "interviewing", "offered", "accepted", "rejected",
    name="application_status_enum"
)


class JobPosting(Base):
    __tablename__ = "job_postings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    # Links to employer's participation in a specific fair
    fair_employer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("fair_employers.id"), nullable=False
    )

    # Identification
    job_order_name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    job_order_external_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Basic info
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    description_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    sector: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    employer_industry: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Status
    status: Mapped[str] = mapped_column(JobStatusEnum, nullable=False, default="active")
    # EC-only: rating of employer relationship quality; NEVER shown to employers/candidates
    employer_ranking: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    # EC-only internal notes, never shared
    job_order_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Employment type
    contract_type: Mapped[str] = mapped_column(ContractTypeEnum, nullable=False)
    hours_per_week: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    anticipated_schedule: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    anticipated_start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Compensation
    wage_measurement: Mapped[str] = mapped_column(WageMeasurementEnum, nullable=False)
    wage_min: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    wage_max: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    # wage_average computed in application layer as (wage_min + wage_max) / 2
    # benefits: ["healthcare", "pto", "retirement", ...]
    benefits: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)

    # Location
    location_type: Mapped[str] = mapped_column(LocationTypeEnum, nullable=False)
    remote_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    job_address_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employer_addresses.id"), nullable=True
    )
    job_address_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Supervisor/Contact
    supervisor_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    supervisor_contact_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employer_contacts.id"), nullable=True
    )
    supervisor_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    supervisor_phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Requirements
    education_required: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    certifications_required: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    background_check_required: Mapped[bool] = mapped_column(Boolean, default=False)
    other_requirements: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    experience_level: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    number_of_openings: Mapped[int] = mapped_column(Integer, default=1)
    close_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Application process
    application_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    how_to_apply: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # [{"question": "...", "required": true}, ...]
    screening_questions: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    recommended_attire: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    interview_directions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    uses_internal_application: Mapped[bool] = mapped_column(Boolean, default=False)

    # Anonymous posting: hide employer name until candidate expresses interest
    is_anonymous: Mapped[bool] = mapped_column(Boolean, default=False)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    created_by_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    scraped_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Relationships
    fair_employer: Mapped["FairEmployer"] = relationship(back_populates="job_postings")  # noqa: F821
    required_skills: Mapped[list["JobRequiredSkill"]] = relationship(
        back_populates="job", cascade="all, delete-orphan"
    )
    required_certifications: Mapped[list["JobRequiredCertification"]] = relationship(
        back_populates="job", cascade="all, delete-orphan"
    )
    match_scores: Mapped[list["MatchScore"]] = relationship(back_populates="job")
    candidate_interactions: Mapped[list["CandidateJobInteraction"]] = relationship(
        back_populates="job"
    )
    applications: Mapped[list["CandidateApplication"]] = relationship(
        back_populates="job"
    )

    @property
    def wage_average(self) -> Optional[Decimal]:
        if self.wage_min is not None and self.wage_max is not None:
            return (self.wage_min + self.wage_max) / 2
        return None


class JobRequiredSkill(Base):
    __tablename__ = "job_required_skills"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("job_postings.id"), nullable=False
    )
    skill_name: Mapped[str] = mapped_column(String(255), nullable=False)
    # True = required, False = preferred/nice-to-have
    is_required: Mapped[bool] = mapped_column(Boolean, default=True)

    job: Mapped["JobPosting"] = relationship(back_populates="required_skills")


class JobRequiredCertification(Base):
    __tablename__ = "job_required_certifications"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("job_postings.id"), nullable=False
    )
    certification_name: Mapped[str] = mapped_column(String(255), nullable=False)

    job: Mapped["JobPosting"] = relationship(back_populates="required_certifications")


class MatchScore(Base):
    """Cached match score for a candidate+job pair at a specific fair."""
    __tablename__ = "match_scores"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    candidate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("candidates.id"), nullable=False
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("job_postings.id"), nullable=False
    )
    fair_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("job_fairs.id"), nullable=False
    )
    # 0-100 composite score
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    # {"skills": 85, "commute": 90, "experience": 75, "certifications": 100, ...}
    factors: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    # EC approval: "pending_ec_review", "approved", "declined", "held"
    ec_status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending_ec_review")
    ec_reviewed_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    ec_reviewed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    ec_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    candidate: Mapped["Candidate"] = relationship(back_populates="match_scores")  # noqa: F821
    job: Mapped["JobPosting"] = relationship(back_populates="match_scores")
    fair: Mapped["JobFair"] = relationship(back_populates="match_scores")  # noqa: F821


class CandidateJobInteraction(Base):
    """Records a candidate's like/ignore/apply/view action on a job."""
    __tablename__ = "candidate_job_interactions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    candidate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("candidates.id"), nullable=False
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("job_postings.id"), nullable=False
    )
    interaction_type: Mapped[str] = mapped_column(InteractionTypeEnum, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    # Candidate's private notes about this job
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    candidate: Mapped["Candidate"] = relationship(back_populates="job_interactions")  # noqa: F821
    job: Mapped["JobPosting"] = relationship(back_populates="candidate_interactions")


class CandidateApplication(Base):
    __tablename__ = "candidate_applications"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    candidate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("candidates.id"), nullable=False
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("job_postings.id"), nullable=False
    )
    application_type: Mapped[str] = mapped_column(ApplicationTypeEnum, nullable=False)
    # Stores internal application form answers as JSON
    application_data: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(
        ApplicationStatusEnum, nullable=False, default="submitted"
    )
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    reviewed_by_ec: Mapped[bool] = mapped_column(Boolean, default=False)
    ec_approved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    ec_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    candidate: Mapped["Candidate"] = relationship(back_populates="applications")  # noqa: F821
    job: Mapped["JobPosting"] = relationship(back_populates="applications")
