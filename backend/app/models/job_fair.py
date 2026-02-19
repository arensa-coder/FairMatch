import uuid
from datetime import date, datetime, time
from typing import Optional

from sqlalchemy import (
    Boolean, Date, DateTime, Enum, Float, ForeignKey, String, Text, Time, func
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

FairStatusEnum = Enum(
    "draft", "published", "active", "completed",
    name="fair_status_enum"
)

FairHostRoleEnum = Enum(
    "primary", "co-host",
    name="fair_host_role_enum"
)

EmployerRsvpEnum = Enum(
    "invited", "yes", "no",
    name="employer_rsvp_enum"
)

CandidateRsvpEnum = Enum(
    "invited", "yes", "no",
    name="candidate_rsvp_enum"
)

RequestStatusEnum = Enum(
    "pending", "approved", "rejected",
    name="request_status_enum"
)


class JobFair(Base):
    __tablename__ = "job_fairs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    lat: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    lng: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    start_time: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    end_time: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    theme: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(FairStatusEnum, nullable=False, default="draft")
    created_by_org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("host_organizations.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    host_orgs: Mapped[list["FairHostOrg"]] = relationship(
        back_populates="job_fair", cascade="all, delete-orphan"
    )
    fair_employers: Mapped[list["FairEmployer"]] = relationship(
        back_populates="job_fair", cascade="all, delete-orphan"
    )
    fair_candidates: Mapped[list["FairCandidate"]] = relationship(
        back_populates="job_fair", cascade="all, delete-orphan"
    )
    match_scores: Mapped[list["MatchScore"]] = relationship(  # noqa: F821
        back_populates="fair"
    )
    candidate_employer_interactions: Mapped[list["CandidateEmployerInteraction"]] = relationship(  # noqa: F821
        back_populates="fair"
    )
    hiring_outcomes: Mapped[list["HiringOutcome"]] = relationship(  # noqa: F821
        back_populates="fair"
    )
    feedback: Mapped[list["Feedback"]] = relationship(  # noqa: F821
        back_populates="fair"
    )


class FairHostOrg(Base):
    """Many-to-many: a fair can have multiple co-hosting orgs."""
    __tablename__ = "fair_host_orgs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    fair_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("job_fairs.id"), nullable=False
    )
    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("host_organizations.id"), nullable=False
    )
    role: Mapped[str] = mapped_column(FairHostRoleEnum, nullable=False, default="primary")

    job_fair: Mapped["JobFair"] = relationship(back_populates="host_orgs")
    org: Mapped["HostOrganization"] = relationship(back_populates="fair_host_orgs")  # noqa: F821


class FairEmployer(Base):
    """Join table: employers invited/RSVPed to a specific fair."""
    __tablename__ = "fair_employers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    fair_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("job_fairs.id"), nullable=False
    )
    employer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employers.id"), nullable=False
    )
    rsvp_status: Mapped[str] = mapped_column(
        EmployerRsvpEnum, nullable=False, default="invited"
    )
    # Unique QR code for this employer at this fair
    qr_code: Mapped[Optional[str]] = mapped_column(String(500), unique=True, nullable=True)
    invited_by_org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("host_organizations.id"), nullable=False
    )
    invited_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    rsvp_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    job_fair: Mapped["JobFair"] = relationship(back_populates="fair_employers")
    employer: Mapped["Employer"] = relationship(back_populates="fair_employers")  # noqa: F821
    job_postings: Mapped[list["JobPosting"]] = relationship(  # noqa: F821
        back_populates="fair_employer"
    )


class FairCandidate(Base):
    """Join table: candidates invited/RSVPed to a specific fair."""
    __tablename__ = "fair_candidates"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    fair_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("job_fairs.id"), nullable=False
    )
    candidate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("candidates.id"), nullable=False
    )
    rsvp_status: Mapped[str] = mapped_column(
        CandidateRsvpEnum, nullable=False, default="invited"
    )
    check_in_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    invited_by_org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("host_organizations.id"), nullable=False
    )
    # For public fairs: candidate requests to join
    request_status: Mapped[Optional[str]] = mapped_column(
        RequestStatusEnum, nullable=True
    )
    requested_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    job_fair: Mapped["JobFair"] = relationship(back_populates="fair_candidates")
    candidate: Mapped["Candidate"] = relationship(back_populates="fair_candidates")  # noqa: F821
