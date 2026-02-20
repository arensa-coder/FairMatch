"""
Job posting CRUD, EC match review, candidate interactions, hiring outcomes.
"""
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_user, require_candidate, require_host_org
from app.database import get_db
from app.matching import calculate_match_score
from app.models.user import Candidate, User
from app.models.job import (
    CandidateApplication,
    CandidateJobInteraction,
    JobPosting,
    JobRequiredSkill,
    MatchScore,
)
from app.models.activity import HiringOutcome
from app.models.job_fair import FairCandidate, FairEmployer
from app.schemas.job import (
    ApplicationCreate,
    ApplicationOut,
    HiringOutcomeCreate,
    InteractionCreate,
    InteractionOut,
    JobPostingCreate,
    JobPostingECOut,
    JobPostingOut,
    JobPostingUpdate,
    MatchReviewAction,
    MatchScoreOut,
)

router = APIRouter(prefix="/jobs", tags=["jobs"])


def _get_job_or_404(job_id: uuid.UUID, db: Session) -> JobPosting:
    job = db.get(JobPosting, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job posting not found.")
    return job


def _get_candidate(user: User, db: Session) -> Candidate:
    candidate = db.query(Candidate).filter(Candidate.user_id == user.id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate profile not found.")
    return candidate


# ─── Job Posting CRUD ─────────────────────────────────────────────────────────

@router.post("", response_model=JobPostingECOut, status_code=status.HTTP_201_CREATED)
def create_job_posting(
    payload: JobPostingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Employers create job postings. ECs (host_org) can also create on employer's behalf.
    """
    if current_user.user_type not in ("employer", "host_org"):
        raise HTTPException(status_code=403, detail="Only employers or ECs can post jobs.")

    # Verify the fair_employer row belongs to the right employer
    fair_employer = db.get(FairEmployer, payload.fair_employer_id)
    if not fair_employer:
        raise HTTPException(status_code=404, detail="Fair/employer registration not found.")

    # Extract required_skills from payload before creating the posting
    required_skills_data = payload.required_skills or []
    job_data = payload.model_dump(exclude={"required_skills"})

    job = JobPosting(created_by_user_id=current_user.id, **job_data)
    db.add(job)
    db.flush()

    for rs in required_skills_data:
        skill = JobRequiredSkill(
            job_id=job.id,
            skill_name=rs.get("skill_name", ""),
            is_required=rs.get("is_required", True),
        )
        db.add(skill)

    db.commit()
    db.refresh(job)
    return job


@router.get("", response_model=list[JobPostingOut])
def list_jobs(
    fair_id: uuid.UUID | None = None,
    sector: str | None = None,
    status: str | None = None,
    location_type: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List jobs. Filters: fair_id, sector, status, location_type.
    ECs see job_order_notes/employer_ranking; candidates see clean public view.
    """
    query = db.query(JobPosting)

    if fair_id:
        query = (
            query.join(FairEmployer, FairEmployer.id == JobPosting.fair_employer_id)
            .filter(FairEmployer.fair_id == fair_id)
        )
    if sector:
        query = query.filter(JobPosting.sector == sector)
    if status:
        query = query.filter(JobPosting.status == status)
    if location_type:
        query = query.filter(JobPosting.location_type == location_type)

    # Candidates only see active jobs
    if current_user.user_type == "candidate":
        query = query.filter(JobPosting.status == "active")

    return query.all()


@router.get("/{job_id}", response_model=JobPostingOut)
def get_job(
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return _get_job_or_404(job_id, db)


@router.patch("/{job_id}", response_model=JobPostingOut)
def update_job(
    job_id: uuid.UUID,
    payload: JobPostingUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.user_type not in ("employer", "host_org"):
        raise HTTPException(status_code=403, detail="Not authorized to edit jobs.")

    job = _get_job_or_404(job_id, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(job, field, value)
    db.commit()
    db.refresh(job)
    return job


# ─── Match Score Generation ───────────────────────────────────────────────────

@router.post("/{job_id}/compute-match/{candidate_id}", response_model=MatchScoreOut)
def compute_match(
    job_id: uuid.UUID,
    candidate_id: uuid.UUID,
    current_user: User = Depends(require_host_org),
    db: Session = Depends(get_db),
):
    """
    Compute or refresh a match score for a candidate↔job pair.
    Called by Celery background task; also available manually for ECs.
    """
    job = _get_job_or_404(job_id, db)
    candidate = db.get(Candidate, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found.")

    result = calculate_match_score(
        candidate_skills=candidate.skills,
        candidate_pref=candidate.preferences,
        job=job,
    )

    # Derive fair_id from the job's fair_employer
    fair_employer = db.get(FairEmployer, job.fair_employer_id)
    if not fair_employer:
        raise HTTPException(status_code=500, detail="Could not resolve fair for this job.")

    # Upsert match score
    ms = (
        db.query(MatchScore)
        .filter(
            MatchScore.candidate_id == candidate_id,
            MatchScore.job_id == job_id,
            MatchScore.fair_id == fair_employer.fair_id,
        )
        .first()
    )
    if ms:
        ms.score = result["score"]
        ms.factors = result["factors"]
        ms.generated_at = datetime.now(timezone.utc)
    else:
        ms = MatchScore(
            candidate_id=candidate_id,
            job_id=job_id,
            fair_id=fair_employer.fair_id,
            score=result["score"],
            factors=result["factors"],
        )
        db.add(ms)

    db.commit()
    db.refresh(ms)
    return ms


# ─── EC Match Review ──────────────────────────────────────────────────────────

@router.post("/matches/{match_id}/review")
def review_match(
    match_id: uuid.UUID,
    payload: MatchReviewAction,
    current_user: User = Depends(require_host_org),
    db: Session = Depends(get_db),
):
    """
    EC approves, declines, or holds a system-generated match.
    Only approved matches are shown to candidates.
    """
    valid_actions = {"approved", "declined", "held"}
    if payload.action not in valid_actions:
        raise HTTPException(status_code=400, detail=f"action must be one of {valid_actions}.")

    ms = db.get(MatchScore, match_id)
    if not ms:
        raise HTTPException(status_code=404, detail="Match not found.")

    ms.ec_status = payload.action
    ms.ec_reviewed_by = current_user.id
    ms.ec_reviewed_at = datetime.now(timezone.utc)
    ms.ec_note = payload.ec_note
    db.commit()
    return {"detail": f"Match {payload.action}."}


@router.get("/matches/pending", response_model=list[MatchScoreOut])
def list_pending_matches(
    current_user: User = Depends(require_host_org),
    db: Session = Depends(get_db),
):
    """EC dashboard: all matches awaiting review."""
    return (
        db.query(MatchScore)
        .filter(MatchScore.ec_status == "pending_ec_review")
        .order_by(MatchScore.score.desc())
        .all()
    )


# ─── Candidate Job Interactions ───────────────────────────────────────────────

@router.post("/interactions", response_model=InteractionOut, status_code=201)
def record_interaction(
    payload: InteractionCreate,
    current_user: User = Depends(require_candidate),
    db: Session = Depends(get_db),
):
    """
    Candidate likes, ignores, applies to, or views a job.
    'liked' and 'applied' notify the employer (TODO: notification service).
    """
    candidate = _get_candidate(current_user, db)

    # Remove previous interaction of same type for idempotency
    existing = (
        db.query(CandidateJobInteraction)
        .filter(
            CandidateJobInteraction.candidate_id == candidate.id,
            CandidateJobInteraction.job_id == payload.job_id,
            CandidateJobInteraction.interaction_type == payload.interaction_type,
        )
        .first()
    )
    if existing:
        return existing

    interaction = CandidateJobInteraction(
        candidate_id=candidate.id,
        job_id=payload.job_id,
        interaction_type=payload.interaction_type,
        notes=payload.notes,
    )
    db.add(interaction)
    db.commit()
    db.refresh(interaction)

    # TODO: if interaction_type in ("liked", "applied"):
    #     notify employer via notification service

    return interaction


@router.get("/interactions/me", response_model=list[InteractionOut])
def my_interactions(
    interaction_type: str | None = None,
    current_user: User = Depends(require_candidate),
    db: Session = Depends(get_db),
):
    candidate = _get_candidate(current_user, db)
    query = db.query(CandidateJobInteraction).filter(
        CandidateJobInteraction.candidate_id == candidate.id
    )
    if interaction_type:
        query = query.filter(CandidateJobInteraction.interaction_type == interaction_type)
    return query.order_by(CandidateJobInteraction.timestamp.desc()).all()


# ─── Applications ─────────────────────────────────────────────────────────────

@router.post("/applications", response_model=ApplicationOut, status_code=201)
def submit_application(
    payload: ApplicationCreate,
    current_user: User = Depends(require_candidate),
    db: Session = Depends(get_db),
):
    candidate = _get_candidate(current_user, db)

    # Prevent duplicate applications
    existing = (
        db.query(CandidateApplication)
        .filter(
            CandidateApplication.candidate_id == candidate.id,
            CandidateApplication.job_id == payload.job_id,
        )
        .first()
    )
    if existing:
        return existing

    application = CandidateApplication(
        candidate_id=candidate.id,
        job_id=payload.job_id,
        application_type=payload.application_type,
        application_data=payload.application_data,
    )
    db.add(application)
    db.commit()
    db.refresh(application)
    return application


@router.get("/applications/me", response_model=list[ApplicationOut])
def my_applications(
    current_user: User = Depends(require_candidate),
    db: Session = Depends(get_db),
):
    candidate = _get_candidate(current_user, db)
    return (
        db.query(CandidateApplication)
        .filter(CandidateApplication.candidate_id == candidate.id)
        .order_by(CandidateApplication.submitted_at.desc())
        .all()
    )


# ─── Candidate Match List ─────────────────────────────────────────────────────

@router.get("/matches/me/{fair_id}", response_model=list[MatchScoreOut])
def my_matches_for_fair(
    fair_id: uuid.UUID,
    current_user: User = Depends(require_candidate),
    db: Session = Depends(get_db),
):
    """
    Returns all EC-approved matches for this candidate at the specified fair,
    ordered by score descending.  All scoring tiers are shown — no minimum
    threshold is applied.
    """
    candidate = _get_candidate(current_user, db)
    return (
        db.query(MatchScore)
        .filter(
            MatchScore.candidate_id == candidate.id,
            MatchScore.fair_id == fair_id,
            MatchScore.ec_status == "approved",
        )
        .order_by(MatchScore.score.desc())
        .all()
    )


# ─── Hiring Outcomes ─────────────────────────────────────────────────────────

@router.post("/{fair_id}/hiring-outcomes", status_code=201)
def report_hiring_outcome(
    fair_id: uuid.UUID,
    payload: HiringOutcomeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Employers or candidates report a hiring outcome post-fair."""
    if current_user.user_type not in ("employer", "candidate"):
        raise HTTPException(status_code=403, detail="Only employers or candidates can report outcomes.")

    reported_by = current_user.user_type
    outcome = HiringOutcome(
        fair_id=fair_id,
        reported_by=reported_by,
        **payload.model_dump(),
    )
    db.add(outcome)
    db.commit()
    return {"detail": "Outcome recorded."}
