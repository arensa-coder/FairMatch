"""
Employer profile, addresses, contacts endpoints.
"""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_user, require_employer
from app.database import get_db
from app.models.user import Employer, User
from app.models.employer import EmployerAddress, EmployerContact
from app.schemas.user import EmployerCreate, EmployerUpdate, EmployerOut

router = APIRouter(prefix="/employers", tags=["employers"])


# ─── Profile ──────────────────────────────────────────────────────────────────

@router.post("", response_model=EmployerOut, status_code=status.HTTP_201_CREATED)
def create_employer_profile(
    payload: EmployerCreate,
    current_user: User = Depends(require_employer),
    db: Session = Depends(get_db),
):
    existing = db.query(Employer).filter(Employer.user_id == current_user.id).first()
    if existing:
        raise HTTPException(status_code=409, detail="Employer profile already exists.")

    employer = Employer(user_id=current_user.id, **payload.model_dump())
    db.add(employer)
    db.commit()
    db.refresh(employer)
    return employer


@router.get("/me", response_model=EmployerOut)
def get_my_employer_profile(
    current_user: User = Depends(require_employer),
    db: Session = Depends(get_db),
):
    employer = db.query(Employer).filter(Employer.user_id == current_user.id).first()
    if not employer:
        raise HTTPException(status_code=404, detail="Employer profile not found.")
    return employer


@router.patch("/me", response_model=EmployerOut)
def update_employer_profile(
    payload: EmployerUpdate,
    current_user: User = Depends(require_employer),
    db: Session = Depends(get_db),
):
    employer = db.query(Employer).filter(Employer.user_id == current_user.id).first()
    if not employer:
        raise HTTPException(status_code=404, detail="Employer profile not found.")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(employer, field, value)
    db.commit()
    db.refresh(employer)
    return employer


@router.get("/{employer_id}", response_model=EmployerOut)
def get_employer_by_id(
    employer_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Accessible by host orgs (to view employer profiles in their network)."""
    employer = db.get(Employer, employer_id)
    if not employer:
        raise HTTPException(status_code=404, detail="Employer not found.")
    return employer


# ─── Addresses ────────────────────────────────────────────────────────────────

@router.post("/me/addresses", status_code=status.HTTP_201_CREATED)
def add_employer_address(
    address_type: str,
    address_line1: str,
    city: str,
    state: str,
    zip_code: str,
    is_primary: bool = False,
    address_line2: str | None = None,
    current_user: User = Depends(require_employer),
    db: Session = Depends(get_db),
):
    employer = db.query(Employer).filter(Employer.user_id == current_user.id).first()
    if not employer:
        raise HTTPException(status_code=404, detail="Employer profile not found.")

    addr = EmployerAddress(
        employer_id=employer.id,
        address_type=address_type,
        address_line1=address_line1,
        address_line2=address_line2,
        city=city,
        state=state,
        zip_code=zip_code,
        is_primary=is_primary,
    )
    db.add(addr)
    db.commit()
    db.refresh(addr)
    return {"id": str(addr.id), "detail": "Address added."}


# ─── Contacts ─────────────────────────────────────────────────────────────────

@router.post("/me/contacts", status_code=status.HTTP_201_CREATED)
def add_employer_contact(
    contact_type: str,
    first_name: str,
    last_name: str,
    email: str,
    title: str | None = None,
    phone: str | None = None,
    is_primary: bool = False,
    current_user: User = Depends(require_employer),
    db: Session = Depends(get_db),
):
    employer = db.query(Employer).filter(Employer.user_id == current_user.id).first()
    if not employer:
        raise HTTPException(status_code=404, detail="Employer profile not found.")

    contact = EmployerContact(
        employer_id=employer.id,
        contact_type=contact_type,
        first_name=first_name,
        last_name=last_name,
        title=title,
        email=email,
        phone=phone,
        is_primary=is_primary,
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return {"id": str(contact.id), "detail": "Contact added."}
