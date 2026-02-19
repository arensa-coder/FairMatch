import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean, DateTime, Enum, ForeignKey, String, Text, func
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

UserTypeEnum = Enum(
    "candidate", "employer", "host_org", "super_admin",
    name="user_type_enum"
)

SubscriptionStatusEnum = Enum(
    "active", "canceled", "past_due",
    name="subscription_status_enum"
)


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    # password_hash omitted — Supabase Auth handles authentication
    user_type: Mapped[str] = mapped_column(UserTypeEnum, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    last_login: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships (one-to-one, at most one profile per user)
    host_organization: Mapped[Optional["HostOrganization"]] = relationship(
        back_populates="user", uselist=False
    )
    employer: Mapped[Optional["Employer"]] = relationship(
        back_populates="user", uselist=False
    )
    candidate: Mapped[Optional["Candidate"]] = relationship(
        back_populates="user", uselist=False
    )


class HostOrganization(Base):
    __tablename__ = "host_organizations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    mission: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    logo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    contact_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    subscription_tier: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    subscription_status: Mapped[Optional[str]] = mapped_column(
        SubscriptionStatusEnum, nullable=True
    )
    stripe_customer_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="host_organization")
    fair_host_orgs: Mapped[list["FairHostOrg"]] = relationship(  # noqa: F821
        back_populates="org"
    )
    employer_relationships: Mapped[list["EmployerRelationship"]] = relationship(  # noqa: F821
        back_populates="host_org"
    )
    employer_notes: Mapped[list["EmployerNote"]] = relationship(  # noqa: F821
        back_populates="host_org"
    )


class Employer(Base):
    __tablename__ = "employers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    industry: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    website: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    contact_person: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="employer")
    addresses: Mapped[list["EmployerAddress"]] = relationship(  # noqa: F821
        back_populates="employer", cascade="all, delete-orphan"
    )
    contacts: Mapped[list["EmployerContact"]] = relationship(  # noqa: F821
        back_populates="employer", cascade="all, delete-orphan"
    )
    relationships: Mapped[list["EmployerRelationship"]] = relationship(  # noqa: F821
        back_populates="employer"
    )
    notes: Mapped[list["EmployerNote"]] = relationship(  # noqa: F821
        back_populates="employer"
    )
    fair_employers: Mapped[list["FairEmployer"]] = relationship(  # noqa: F821
        back_populates="employer"
    )


class Candidate(Base):
    __tablename__ = "candidates"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    # home_address stored but NEVER shared with employers
    home_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    resume_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    linkedin_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    invited_by_org_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("host_organizations.id"), nullable=True
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="candidate")
    skills: Mapped[list["CandidateSkill"]] = relationship(  # noqa: F821
        back_populates="candidate", cascade="all, delete-orphan"
    )
    work_history: Mapped[list["CandidateWorkHistory"]] = relationship(  # noqa: F821
        back_populates="candidate", cascade="all, delete-orphan"
    )
    education: Mapped[list["CandidateEducation"]] = relationship(  # noqa: F821
        back_populates="candidate", cascade="all, delete-orphan"
    )
    certifications: Mapped[list["CandidateCertification"]] = relationship(  # noqa: F821
        back_populates="candidate", cascade="all, delete-orphan"
    )
    preferences: Mapped[Optional["CandidatePreference"]] = relationship(  # noqa: F821
        back_populates="candidate", uselist=False, cascade="all, delete-orphan"
    )
    barriers: Mapped[Optional["CandidateBarrier"]] = relationship(  # noqa: F821
        back_populates="candidate", uselist=False, cascade="all, delete-orphan"
    )
    fair_candidates: Mapped[list["FairCandidate"]] = relationship(  # noqa: F821
        back_populates="candidate"
    )
    match_scores: Mapped[list["MatchScore"]] = relationship(  # noqa: F821
        back_populates="candidate"
    )
    job_interactions: Mapped[list["CandidateJobInteraction"]] = relationship(  # noqa: F821
        back_populates="candidate"
    )
    applications: Mapped[list["CandidateApplication"]] = relationship(  # noqa: F821
        back_populates="candidate"
    )
