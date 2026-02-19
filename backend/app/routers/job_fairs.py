"""
Job Fair lifecycle: create, invite employers/candidates, RSVP, check-in, QR scan.
"""
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_user, require_candidate, require_employer, require_host_org
from app.database import get_db
from app.models.user import HostOrganization, User, Candidate, Employer
from app.models.job_fair import FairCandidate, FairEmployer, FairHostOrg, JobFair
from app.schemas.job_fair import (
    FairCandidateOut,
    FairEmployerOut,
    InviteCandidatesRequest,
    InviteEmployersRequest,
    JobFairCreate,
    JobFairOut,
    JobFairUpdate,
    QRScanRequest,
    RSVPRequest,
)
from app.models.activity import CandidateEmployerInteraction

router = APIRouter(prefix="/job-fairs", tags=["job-fairs"])


def _get_host_org(user: User, db: Session) -> HostOrganization:
    org = db.query(HostOrganization).filter(HostOrganization.user_id == user.id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Host organization profile not found.")
    return org


def _get_fair_or_404(fair_id: uuid.UUID, db: Session) -> JobFair:
    fair = db.get(JobFair, fair_id)
    if not fair:
        raise HTTPException(status_code=404, detail="Job fair not found.")
    return fair


def _assert_org_owns_fair(fair: JobFair, org: HostOrganization, db: Session) -> None:
    hosting = (
        db.query(FairHostOrg)
        .filter(FairHostOrg.fair_id == fair.id, FairHostOrg.org_id == org.id)
        .first()
    )
    if not hosting:
        raise HTTPException(status_code=403, detail="Your organization does not host this fair.")


# ─── CRUD ─────────────────────────────────────────────────────────────────────

@router.post("", response_model=JobFairOut, status_code=status.HTTP_201_CREATED)
def create_job_fair(
    payload: JobFairCreate,
    current_user: User = Depends(require_host_org),
    db: Session = Depends(get_db),
):
    org = _get_host_org(current_user, db)

    fair = JobFair(created_by_org_id=org.id, **payload.model_dump())
    db.add(fair)
    db.flush()  # get fair.id before adding FairHostOrg

    # The creating org is automatically the primary host
    fho = FairHostOrg(fair_id=fair.id, org_id=org.id, role="primary")
    db.add(fho)
    db.commit()
    db.refresh(fair)
    return fair


@router.get("", response_model=list[JobFairOut])
def list_job_fairs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Host orgs see their own fairs.
    Candidates/employers see fairs they are invited to.
    Public fairs are returned for candidates browsing.
    """
    if current_user.user_type == "host_org":
        org = _get_host_org(current_user, db)
        fairs = (
            db.query(JobFair)
            .join(FairHostOrg, FairHostOrg.fair_id == JobFair.id)
            .filter(FairHostOrg.org_id == org.id)
            .all()
        )
    elif current_user.user_type == "candidate":
        candidate = db.query(Candidate).filter(Candidate.user_id == current_user.id).first()
        if not candidate:
            return []
        fairs = (
            db.query(JobFair)
            .join(FairCandidate, FairCandidate.fair_id == JobFair.id)
            .filter(FairCandidate.candidate_id == candidate.id)
            .all()
        )
    elif current_user.user_type == "employer":
        employer = db.query(Employer).filter(Employer.user_id == current_user.id).first()
        if not employer:
            return []
        fairs = (
            db.query(JobFair)
            .join(FairEmployer, FairEmployer.fair_id == JobFair.id)
            .filter(FairEmployer.employer_id == employer.id)
            .all()
        )
    else:
        fairs = []
    return fairs


@router.get("/{fair_id}", response_model=JobFairOut)
def get_job_fair(
    fair_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return _get_fair_or_404(fair_id, db)


@router.patch("/{fair_id}", response_model=JobFairOut)
def update_job_fair(
    fair_id: uuid.UUID,
    payload: JobFairUpdate,
    current_user: User = Depends(require_host_org),
    db: Session = Depends(get_db),
):
    org = _get_host_org(current_user, db)
    fair = _get_fair_or_404(fair_id, db)
    _assert_org_owns_fair(fair, org, db)

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(fair, field, value)
    db.commit()
    db.refresh(fair)
    return fair


# ─── Employer Invitations ─────────────────────────────────────────────────────

@router.post("/{fair_id}/invite-employers", status_code=status.HTTP_201_CREATED)
def invite_employers(
    fair_id: uuid.UUID,
    payload: InviteEmployersRequest,
    current_user: User = Depends(require_host_org),
    db: Session = Depends(get_db),
):
    org = _get_host_org(current_user, db)
    fair = _get_fair_or_404(fair_id, db)
    _assert_org_owns_fair(fair, org, db)

    added = 0
    for employer_id in payload.employer_ids:
        existing = (
            db.query(FairEmployer)
            .filter(FairEmployer.fair_id == fair_id, FairEmployer.employer_id == employer_id)
            .first()
        )
        if not existing:
            fe = FairEmployer(
                fair_id=fair_id,
                employer_id=employer_id,
                invited_by_org_id=org.id,
            )
            db.add(fe)
            added += 1

    db.commit()
    return {"detail": f"{added} employer(s) invited."}


# ─── Candidate Invitations ────────────────────────────────────────────────────

@router.post("/{fair_id}/invite-candidates", status_code=status.HTTP_201_CREATED)
def invite_candidates(
    fair_id: uuid.UUID,
    payload: InviteCandidatesRequest,
    current_user: User = Depends(require_host_org),
    db: Session = Depends(get_db),
):
    org = _get_host_org(current_user, db)
    fair = _get_fair_or_404(fair_id, db)
    _assert_org_owns_fair(fair, org, db)

    added = 0
    for candidate_id in payload.candidate_ids:
        existing = (
            db.query(FairCandidate)
            .filter(FairCandidate.fair_id == fair_id, FairCandidate.candidate_id == candidate_id)
            .first()
        )
        if not existing:
            fc = FairCandidate(
                fair_id=fair_id,
                candidate_id=candidate_id,
                invited_by_org_id=org.id,
            )
            db.add(fc)
            added += 1

    db.commit()
    return {"detail": f"{added} candidate(s) invited."}


# ─── RSVP ─────────────────────────────────────────────────────────────────────

@router.post("/{fair_id}/rsvp")
def rsvp_to_fair(
    fair_id: uuid.UUID,
    payload: RSVPRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if payload.status not in ("yes", "no"):
        raise HTTPException(status_code=400, detail="status must be 'yes' or 'no'.")

    now = datetime.now(timezone.utc)

    if current_user.user_type == "candidate":
        candidate = db.query(Candidate).filter(Candidate.user_id == current_user.id).first()
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate profile not found.")
        row = (
            db.query(FairCandidate)
            .filter(FairCandidate.fair_id == fair_id, FairCandidate.candidate_id == candidate.id)
            .first()
        )
        if not row:
            raise HTTPException(status_code=404, detail="You are not invited to this fair.")
        row.rsvp_status = payload.status
        db.commit()
        return {"detail": f"RSVP recorded: {payload.status}"}

    elif current_user.user_type == "employer":
        employer = db.query(Employer).filter(Employer.user_id == current_user.id).first()
        if not employer:
            raise HTTPException(status_code=404, detail="Employer profile not found.")
        row = (
            db.query(FairEmployer)
            .filter(FairEmployer.fair_id == fair_id, FairEmployer.employer_id == employer.id)
            .first()
        )
        if not row:
            raise HTTPException(status_code=404, detail="You are not invited to this fair.")
        row.rsvp_status = payload.status
        row.rsvp_at = now

        # Generate QR code token on 'yes' RSVP
        if payload.status == "yes" and not row.qr_code:
            row.qr_code = f"fe:{fair_id}:{employer.id}:{uuid.uuid4().hex[:8]}"

        db.commit()
        return {"detail": f"RSVP recorded: {payload.status}", "qr_code": row.qr_code}

    else:
        raise HTTPException(status_code=403, detail="Only candidates and employers can RSVP.")


# ─── Candidate Check-in ───────────────────────────────────────────────────────

@router.post("/{fair_id}/check-in")
def candidate_check_in(
    fair_id: uuid.UUID,
    current_user: User = Depends(require_candidate),
    db: Session = Depends(get_db),
):
    candidate = db.query(Candidate).filter(Candidate.user_id == current_user.id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate profile not found.")

    row = (
        db.query(FairCandidate)
        .filter(FairCandidate.fair_id == fair_id, FairCandidate.candidate_id == candidate.id)
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="You are not registered for this fair.")
    if row.rsvp_status != "yes":
        raise HTTPException(status_code=400, detail="Please RSVP 'yes' before checking in.")

    row.check_in_time = datetime.now(timezone.utc)
    db.commit()

    # TODO: publish check-in event to Redis pub/sub for WebSocket broadcast
    return {"detail": "Checked in successfully!", "check_in_time": row.check_in_time}


# ─── Employer QR Scan ─────────────────────────────────────────────────────────

@router.post("/{fair_id}/scan-qr")
def scan_employer_qr(
    fair_id: uuid.UUID,
    payload: QRScanRequest,
    current_user: User = Depends(require_candidate),
    db: Session = Depends(get_db),
):
    """
    Candidate scans an employer's booth QR code.
    Logs the interaction and returns the employer's job postings.
    """
    candidate = db.query(Candidate).filter(Candidate.user_id == current_user.id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate profile not found.")

    # Look up employer by QR code
    fair_employer = (
        db.query(FairEmployer)
        .filter(FairEmployer.qr_code == payload.qr_code, FairEmployer.fair_id == fair_id)
        .first()
    )
    if not fair_employer:
        raise HTTPException(status_code=404, detail="Invalid QR code.")

    # Log the interaction
    existing = (
        db.query(CandidateEmployerInteraction)
        .filter(
            CandidateEmployerInteraction.fair_id == fair_id,
            CandidateEmployerInteraction.candidate_id == candidate.id,
            CandidateEmployerInteraction.employer_id == fair_employer.employer_id,
        )
        .first()
    )
    if not existing:
        interaction = CandidateEmployerInteraction(
            fair_id=fair_id,
            candidate_id=candidate.id,
            employer_id=fair_employer.employer_id,
        )
        db.add(interaction)
        db.commit()

    # Return the employer's active job postings for this fair
    jobs = [jp for jp in fair_employer.job_postings if jp.status == "active"]
    return {
        "employer_id": str(fair_employer.employer_id),
        "job_count": len(jobs),
        "jobs": [
            {
                "id": str(j.id),
                "title": j.title,
                "contract_type": j.contract_type,
                "location_type": j.location_type,
                "wage_min": float(j.wage_min) if j.wage_min else None,
                "wage_max": float(j.wage_max) if j.wage_max else None,
                "wage_measurement": j.wage_measurement,
            }
            for j in jobs
        ],
    }
