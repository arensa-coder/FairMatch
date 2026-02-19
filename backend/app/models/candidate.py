import uuid
from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    Boolean, Date, DateTime, ForeignKey, Integer, String, Text, func
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class CandidateSkill(Base):
    __tablename__ = "candidate_skills"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    candidate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("candidates.id"), nullable=False
    )
    skill_name: Mapped[str] = mapped_column(String(255), nullable=False)
    proficiency_level: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    years_experience: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    candidate: Mapped["Candidate"] = relationship(back_populates="skills")  # noqa: F821


class CandidateWorkHistory(Base):
    __tablename__ = "candidate_work_history"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    candidate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("candidates.id"), nullable=False
    )
    company: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    candidate: Mapped["Candidate"] = relationship(back_populates="work_history")  # noqa: F821


class CandidateEducation(Base):
    __tablename__ = "candidate_education"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    candidate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("candidates.id"), nullable=False
    )
    institution: Mapped[str] = mapped_column(String(255), nullable=False)
    degree: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    field: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    graduation_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    candidate: Mapped["Candidate"] = relationship(back_populates="education")  # noqa: F821


class CandidateCertification(Base):
    __tablename__ = "candidate_certifications"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    candidate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("candidates.id"), nullable=False
    )
    certification_name: Mapped[str] = mapped_column(String(255), nullable=False)
    issuing_org: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    date_obtained: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    expiration_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    candidate: Mapped["Candidate"] = relationship(back_populates="certifications")  # noqa: F821


class CandidatePreference(Base):
    __tablename__ = "candidate_preferences"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    candidate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("candidates.id"), unique=True, nullable=False
    )
    max_commute_car_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    max_commute_transit_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    # min/max salary hidden from employers — used only for matching
    min_salary: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    max_salary: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    preferred_schedule: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    # e.g. ["construction", "healthcare", "retail"]
    preferred_industries: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    candidate: Mapped["Candidate"] = relationship(back_populates="preferences")  # noqa: F821


class CandidateBarrier(Base):
    """
    EC-only barrier tracking. NEVER shared with employers.
    Sensitive fields encrypted at rest (AES-256).
    """
    __tablename__ = "candidate_barriers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    candidate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("candidates.id"), unique=True, nullable=False
    )

    # Justice-involved
    is_justice_impacted: Mapped[bool] = mapped_column(Boolean, default=False)
    # Stored as encrypted ciphertext
    justice_impact_details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Housing
    has_housing_instability: Mapped[bool] = mapped_column(Boolean, default=False)

    # Transportation
    has_transportation_barriers: Mapped[bool] = mapped_column(Boolean, default=False)

    # Childcare
    has_childcare_needs: Mapped[bool] = mapped_column(Boolean, default=False)

    # Health/Disability
    needs_health_accommodations: Mapped[bool] = mapped_column(Boolean, default=False)
    # Stored as encrypted ciphertext
    accommodation_details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Language
    has_language_barriers: Mapped[bool] = mapped_column(Boolean, default=False)
    primary_language: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # EC notes — encrypted
    case_management_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    created_by_ec_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )

    candidate: Mapped["Candidate"] = relationship(back_populates="barriers")  # noqa: F821
