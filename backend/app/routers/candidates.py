"""
Candidate profile, skills, work history, education, certifications, preferences.
Barrier data (EC-only) is at the bottom with strict host_org gating.
"""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_user, require_candidate, require_host_org
from app.database import get_db
from app.models.user import Candidate, User
from app.models.candidate import (
    CandidateSkill,
    CandidateWorkHistory,
    CandidateEducation,
    CandidateCertification,
    CandidatePreference,
    CandidateBarrier,
)
from app.schemas.user import CandidateCreate, CandidateUpdate, CandidateOut, CandidateDetailOut
from app.schemas.candidate import (
    CandidateSkillCreate, CandidateSkillOut,
    WorkHistoryCreate, WorkHistoryOut,
    EducationCreate, EducationOut,
    CertificationCreate, CertificationOut,
    CandidatePreferenceCreate, CandidatePreferenceOut,
    CandidateBarrierUpdate, CandidateBarrierOut,
)

router = APIRouter(prefix="/candidates", tags=["candidates"])


def _get_candidate_for_user(user: User, db: Session) -> Candidate:
    candidate = db.query(Candidate).filter(Candidate.user_id == user.id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate profile not found.")
    return candidate


# ─── Profile ──────────────────────────────────────────────────────────────────

@router.post("", response_model=CandidateOut, status_code=status.HTTP_201_CREATED)
def create_candidate_profile(
    payload: CandidateCreate,
    current_user: User = Depends(require_candidate),
    db: Session = Depends(get_db),
):
    existing = db.query(Candidate).filter(Candidate.user_id == current_user.id).first()
    if existing:
        raise HTTPException(status_code=409, detail="Candidate profile already exists.")

    candidate = Candidate(user_id=current_user.id, **payload.model_dump())
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    return candidate


@router.get("/me", response_model=CandidateDetailOut)
def get_my_profile(
    current_user: User = Depends(require_candidate),
    db: Session = Depends(get_db),
):
    return _get_candidate_for_user(current_user, db)


@router.patch("/me", response_model=CandidateOut)
def update_my_profile(
    payload: CandidateUpdate,
    current_user: User = Depends(require_candidate),
    db: Session = Depends(get_db),
):
    candidate = _get_candidate_for_user(current_user, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(candidate, field, value)
    db.commit()
    db.refresh(candidate)
    return candidate


# ─── Skills ───────────────────────────────────────────────────────────────────

@router.post("/me/skills", response_model=CandidateSkillOut, status_code=201)
def add_skill(
    payload: CandidateSkillCreate,
    current_user: User = Depends(require_candidate),
    db: Session = Depends(get_db),
):
    candidate = _get_candidate_for_user(current_user, db)
    skill = CandidateSkill(candidate_id=candidate.id, **payload.model_dump())
    db.add(skill)
    db.commit()
    db.refresh(skill)
    return skill


@router.get("/me/skills", response_model=list[CandidateSkillOut])
def list_skills(
    current_user: User = Depends(require_candidate),
    db: Session = Depends(get_db),
):
    candidate = _get_candidate_for_user(current_user, db)
    return candidate.skills


@router.delete("/me/skills/{skill_id}", status_code=204)
def delete_skill(
    skill_id: uuid.UUID,
    current_user: User = Depends(require_candidate),
    db: Session = Depends(get_db),
):
    candidate = _get_candidate_for_user(current_user, db)
    skill = db.get(CandidateSkill, skill_id)
    if not skill or skill.candidate_id != candidate.id:
        raise HTTPException(status_code=404, detail="Skill not found.")
    db.delete(skill)
    db.commit()


# ─── Work History ─────────────────────────────────────────────────────────────

@router.post("/me/work-history", response_model=WorkHistoryOut, status_code=201)
def add_work_history(
    payload: WorkHistoryCreate,
    current_user: User = Depends(require_candidate),
    db: Session = Depends(get_db),
):
    candidate = _get_candidate_for_user(current_user, db)
    entry = CandidateWorkHistory(candidate_id=candidate.id, **payload.model_dump())
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.get("/me/work-history", response_model=list[WorkHistoryOut])
def list_work_history(
    current_user: User = Depends(require_candidate),
    db: Session = Depends(get_db),
):
    candidate = _get_candidate_for_user(current_user, db)
    return candidate.work_history


# ─── Education ────────────────────────────────────────────────────────────────

@router.post("/me/education", response_model=EducationOut, status_code=201)
def add_education(
    payload: EducationCreate,
    current_user: User = Depends(require_candidate),
    db: Session = Depends(get_db),
):
    candidate = _get_candidate_for_user(current_user, db)
    entry = CandidateEducation(candidate_id=candidate.id, **payload.model_dump())
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.get("/me/education", response_model=list[EducationOut])
def list_education(
    current_user: User = Depends(require_candidate),
    db: Session = Depends(get_db),
):
    candidate = _get_candidate_for_user(current_user, db)
    return candidate.education


# ─── Certifications ───────────────────────────────────────────────────────────

@router.post("/me/certifications", response_model=CertificationOut, status_code=201)
def add_certification(
    payload: CertificationCreate,
    current_user: User = Depends(require_candidate),
    db: Session = Depends(get_db),
):
    candidate = _get_candidate_for_user(current_user, db)
    cert = CandidateCertification(candidate_id=candidate.id, **payload.model_dump())
    db.add(cert)
    db.commit()
    db.refresh(cert)
    return cert


# ─── Preferences ──────────────────────────────────────────────────────────────

@router.put("/me/preferences", response_model=CandidatePreferenceOut)
def upsert_preferences(
    payload: CandidatePreferenceCreate,
    current_user: User = Depends(require_candidate),
    db: Session = Depends(get_db),
):
    candidate = _get_candidate_for_user(current_user, db)
    pref = candidate.preferences
    if pref is None:
        pref = CandidatePreference(candidate_id=candidate.id)
        db.add(pref)

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(pref, field, value)
    db.commit()
    db.refresh(pref)
    return pref


# ─── Barrier Data (EC-only) ───────────────────────────────────────────────────

@router.put("/{candidate_id}/barriers", response_model=CandidateBarrierOut)
def upsert_candidate_barriers(
    candidate_id: uuid.UUID,
    payload: CandidateBarrierUpdate,
    current_user: User = Depends(require_host_org),
    db: Session = Depends(get_db),
):
    """
    EC-only endpoint. Creates or updates barrier flags for a candidate.
    Barrier data is NEVER exposed to employers.
    """
    candidate = db.get(Candidate, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found.")

    barrier = candidate.barriers
    if barrier is None:
        barrier = CandidateBarrier(
            candidate_id=candidate_id,
            created_by_ec_id=current_user.id,
        )
        db.add(barrier)

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(barrier, field, value)
    db.commit()
    db.refresh(barrier)
    return barrier


@router.get("/{candidate_id}/barriers", response_model=CandidateBarrierOut)
def get_candidate_barriers(
    candidate_id: uuid.UUID,
    current_user: User = Depends(require_host_org),
    db: Session = Depends(get_db),
):
    """EC-only. Returns barrier data for a candidate. Never exposed to employers."""
    candidate = db.get(Candidate, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found.")
    if not candidate.barriers:
        raise HTTPException(status_code=404, detail="No barrier data recorded.")
    return candidate.barriers
