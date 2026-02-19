"""
Host Organization endpoints — profile management and employer relationship tools.

All mutating endpoints require user_type == 'host_org'.
"""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_user, require_host_org
from app.database import get_db
from app.models.user import HostOrganization, User
from app.models.employer import EmployerRelationship, EmployerNote
from app.schemas.user import HostOrgCreate, HostOrgUpdate, HostOrgOut

router = APIRouter(prefix="/host-orgs", tags=["host-orgs"])


def _get_org_or_404(org_id: uuid.UUID, db: Session) -> HostOrganization:
    org = db.get(HostOrganization, org_id)
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found.")
    return org


def _assert_owns_org(org: HostOrganization, current_user: User) -> None:
    if org.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your organization.")


# ─── Profile ──────────────────────────────────────────────────────────────────

@router.post("", response_model=HostOrgOut, status_code=status.HTTP_201_CREATED)
def create_host_org(
    payload: HostOrgCreate,
    current_user: User = Depends(require_host_org),
    db: Session = Depends(get_db),
):
    existing = (
        db.query(HostOrganization)
        .filter(HostOrganization.user_id == current_user.id)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Organization profile already exists for this account.",
        )

    org = HostOrganization(user_id=current_user.id, **payload.model_dump())
    db.add(org)
    db.commit()
    db.refresh(org)
    return org


@router.get("/me", response_model=HostOrgOut)
def get_my_org(
    current_user: User = Depends(require_host_org),
    db: Session = Depends(get_db),
):
    org = (
        db.query(HostOrganization)
        .filter(HostOrganization.user_id == current_user.id)
        .first()
    )
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No organization profile found.")
    return org


@router.patch("/me", response_model=HostOrgOut)
def update_my_org(
    payload: HostOrgUpdate,
    current_user: User = Depends(require_host_org),
    db: Session = Depends(get_db),
):
    org = (
        db.query(HostOrganization)
        .filter(HostOrganization.user_id == current_user.id)
        .first()
    )
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No organization profile found.")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(org, field, value)
    db.commit()
    db.refresh(org)
    return org


# ─── Employer Relationship Management (EC-only) ───────────────────────────────

@router.patch("/me/employer-relationships/{employer_id}/ranking")
def update_employer_ranking(
    employer_id: uuid.UUID,
    ranking: int,
    current_user: User = Depends(require_host_org),
    db: Session = Depends(get_db),
):
    """
    Set the EC's 1–5 star ranking for an employer relationship.
    NEVER visible to employers or candidates.
    """
    if ranking < 1 or ranking > 5:
        raise HTTPException(status_code=400, detail="Ranking must be between 1 and 5.")

    org = (
        db.query(HostOrganization)
        .filter(HostOrganization.user_id == current_user.id)
        .first()
    )
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found.")

    rel = (
        db.query(EmployerRelationship)
        .filter(
            EmployerRelationship.employer_id == employer_id,
            EmployerRelationship.host_org_id == org.id,
        )
        .first()
    )
    if not rel:
        rel = EmployerRelationship(employer_id=employer_id, host_org_id=org.id)
        db.add(rel)

    rel.ranking = ranking
    rel.ranking_updated_by = current_user.id
    from datetime import datetime, timezone
    rel.ranking_updated_at = datetime.now(timezone.utc)
    db.commit()
    return {"detail": "Ranking updated."}


@router.post("/me/employer-notes/{employer_id}")
def add_employer_note(
    employer_id: uuid.UUID,
    note: str,
    note_type: str = "general",
    current_user: User = Depends(require_host_org),
    db: Session = Depends(get_db),
):
    """Add a private EC note about an employer. Never visible to employer or candidate."""
    org = (
        db.query(HostOrganization)
        .filter(HostOrganization.user_id == current_user.id)
        .first()
    )
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found.")

    new_note = EmployerNote(
        employer_id=employer_id,
        host_org_id=org.id,
        note=note,
        note_type=note_type,
        created_by_ec=current_user.id,
    )
    db.add(new_note)
    db.commit()
    return {"detail": "Note added."}
