import uuid
from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    Date, DateTime, Enum, ForeignKey, Integer, String, Text, func
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

HiringStatusEnum = Enum(
    "offered", "accepted", "started", "declined",
    name="hiring_status_enum"
)

ReportedByEnum = Enum(
    "employer", "candidate",
    name="reported_by_enum"
)

FeedbackUserTypeEnum = Enum(
    "candidate", "employer", "host_org",
    name="feedback_user_type_enum"
)


class CandidateEmployerInteraction(Base):
    """Records in-person meeting at a fair (QR scan or manual log)."""
    __tablename__ = "candidate_employer_interactions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    fair_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("job_fairs.id"), nullable=False
    )
    candidate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("candidates.id"), nullable=False
    )
    employer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employers.id"), nullable=False
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    # Private notes visible only to each respective party
    employer_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    candidate_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    employer_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    candidate_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    fair: Mapped["JobFair"] = relationship(back_populates="candidate_employer_interactions")  # noqa: F821
    candidate: Mapped["Candidate"] = relationship()  # noqa: F821
    employer: Mapped["Employer"] = relationship()  # noqa: F821


class HiringOutcome(Base):
    """Tracks hiring results reported by employers or candidates post-fair."""
    __tablename__ = "hiring_outcomes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    fair_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("job_fairs.id"), nullable=False
    )
    candidate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("candidates.id"), nullable=False
    )
    employer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employers.id"), nullable=False
    )
    job_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("job_postings.id"), nullable=True
    )
    status: Mapped[str] = mapped_column(HiringStatusEnum, nullable=False)
    offer_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    accept_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    reported_by: Mapped[str] = mapped_column(ReportedByEnum, nullable=False)
    reported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    fair: Mapped["JobFair"] = relationship(back_populates="hiring_outcomes")  # noqa: F821
    candidate: Mapped["Candidate"] = relationship()  # noqa: F821
    employer: Mapped["Employer"] = relationship()  # noqa: F821


class Feedback(Base):
    """Post-fair feedback from any user type."""
    __tablename__ = "feedback"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    fair_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("job_fairs.id"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    user_type: Mapped[str] = mapped_column(FeedbackUserTypeEnum, nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    comments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    fair: Mapped["JobFair"] = relationship(back_populates="feedback")  # noqa: F821


class Notification(Base):
    """Log of all notifications sent to users."""
    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    # e.g. 'fair_invitation', 'match_ready', 'check_in', 'feedback_request'
    type: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    # ['email', 'sms', 'push']
    sent_via: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    sent_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    read_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
