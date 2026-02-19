import uuid
from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    Boolean, Date, DateTime, Enum, ForeignKey, Integer, String, Text, func
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

AddressTypeEnum = Enum(
    "headquarters", "branch", "job_site", "other",
    name="address_type_enum"
)

ContactTypeEnum = Enum(
    "recruiter", "hiring_manager", "hr", "supervisor", "other",
    name="contact_type_enum"
)

NoteTypeEnum = Enum(
    "general", "red_flag", "success_story", "coaching_needed", "other",
    name="note_type_enum"
)


class EmployerAddress(Base):
    __tablename__ = "employer_addresses"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    employer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employers.id"), nullable=False
    )
    address_type: Mapped[str] = mapped_column(
        AddressTypeEnum, nullable=False, default="headquarters"
    )
    address_line1: Mapped[str] = mapped_column(String(255), nullable=False)
    address_line2: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(String(100), nullable=False)
    zip_code: Mapped[str] = mapped_column(String(20), nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=False, default="USA")
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    employer: Mapped["Employer"] = relationship(back_populates="addresses")  # noqa: F821


class EmployerContact(Base):
    __tablename__ = "employer_contacts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    employer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employers.id"), nullable=False
    )
    contact_type: Mapped[str] = mapped_column(ContactTypeEnum, nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    employer: Mapped["Employer"] = relationship(back_populates="contacts")  # noqa: F821


class EmployerRelationship(Base):
    """EC-only: tracks host org's relationship quality with an employer."""
    __tablename__ = "employer_relationships"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    employer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employers.id"), nullable=False
    )
    host_org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("host_organizations.id"), nullable=False
    )
    # 1-5 star rating; EC-only, NEVER visible to employers or candidates
    ranking: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    ranking_updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    ranking_updated_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    # Encrypted at rest — stores private EC notes about the employer
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_fair_chance: Mapped[bool] = mapped_column(Boolean, default=False)
    first_interaction_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    last_interaction_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    total_fairs_attended: Mapped[int] = mapped_column(Integer, default=0)
    total_candidates_referred: Mapped[int] = mapped_column(Integer, default=0)
    total_hires_made: Mapped[int] = mapped_column(Integer, default=0)

    employer: Mapped["Employer"] = relationship(back_populates="relationships")  # noqa: F821
    host_org: Mapped["HostOrganization"] = relationship(back_populates="employer_relationships")  # noqa: F821


class EmployerNote(Base):
    """Running log of EC observations about an employer. EC-only."""
    __tablename__ = "employer_notes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    employer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employers.id"), nullable=False
    )
    host_org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("host_organizations.id"), nullable=False
    )
    note: Mapped[str] = mapped_column(Text, nullable=False)
    created_by_ec: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    note_type: Mapped[str] = mapped_column(NoteTypeEnum, nullable=False, default="general")

    employer: Mapped["Employer"] = relationship(back_populates="notes")  # noqa: F821
    host_org: Mapped["HostOrganization"] = relationship(back_populates="employer_notes")  # noqa: F821
