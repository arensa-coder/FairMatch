"""
FairMatch scoring algorithm (Section 6 of the spec).

Weights:
  Skills       30%
  Commute      25%
  Experience   15%
  Certifications 10%
  Schedule     10%
  Industry     10%

Returns a 0–100 integer score plus a factor breakdown dict.
Matches below 60 are suppressed from candidate views.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.candidate import (
        CandidateSkill,
        CandidateWorkHistory,
        CandidateCertification,
        CandidatePreference,
    )
    from app.models.job import JobPosting, JobRequiredSkill

MATCH_THRESHOLD = 60  # Only show matches at or above this score

# ── Experience level mapping to approximate years ────────────────────────────
_EXP_MIDPOINTS: dict[str, int] = {
    "entry-level": 0,
    "1-3 years":   2,
    "3-5 years":   4,
    "5+ years":    7,
    "10+ years":  12,
}

# ── Industry relatedness (a simplified adjacency map) ────────────────────────
_RELATED_INDUSTRIES: dict[str, set[str]] = {
    "construction": {"manufacturing", "trades", "maintenance"},
    "healthcare":   {"nursing", "medical", "social_services"},
    "retail":       {"sales", "hospitality", "customer_service"},
    "hospitality":  {"food_service", "retail", "tourism"},
    "manufacturing":{"construction", "logistics", "trades"},
    "nonprofit":    {"social_services", "education", "government"},
}


def _skills_score(
    candidate_skills: list["CandidateSkill"],
    required_skills: list["JobRequiredSkill"],
) -> float:
    """
    (Candidate skills ∩ Job requirements) / Total required skills.
    Required skills weighted 2×, preferred 1×.
    """
    if not required_skills:
        return 1.0

    candidate_skill_names = {s.skill_name.lower() for s in candidate_skills}

    total_weight = 0.0
    matched_weight = 0.0

    for rs in required_skills:
        weight = 2.0 if rs.is_required else 1.0
        total_weight += weight
        if rs.skill_name.lower() in candidate_skill_names:
            matched_weight += weight

    return matched_weight / total_weight if total_weight else 0.0


def _commute_score(
    candidate_pref: "CandidatePreference | None",
    job: "JobPosting",
) -> float:
    """
    Returns 1.0 if location type is remote (no commute needed).
    For on-site/hybrid, a placeholder score is used; real implementation
    would call a mapping API (Google Maps Distance Matrix) to get actual
    commute time, then scale linearly against candidate's max preference.
    """
    if job.location_type == "remote":
        return 1.0

    if candidate_pref is None:
        return 0.5  # No preference set → neutral score

    # Placeholder: without address geocoding we return a neutral score.
    # Phase 2 will integrate Google Maps Distance Matrix API here.
    return 0.5


def _experience_score(
    work_history: list["CandidateWorkHistory"],
    job: "JobPosting",
) -> float:
    """
    Estimates candidate's total years of experience from work history,
    then compares against the job's experience_level requirement.
    """
    if not job.experience_level:
        return 1.0  # No requirement → full score

    # Sum months of work history to get total years
    from datetime import date as dt_date

    total_months = 0
    today = dt_date.today()
    for wh in work_history:
        end = wh.end_date or today
        delta = (end.year - wh.start_date.year) * 12 + (end.month - wh.start_date.month)
        total_months += max(delta, 0)
    candidate_years = total_months / 12

    required_years = _EXP_MIDPOINTS.get(job.experience_level.lower(), 0)

    if candidate_years >= required_years:
        # Slight penalty for being heavily overqualified (>2× required)
        if required_years > 0 and candidate_years > required_years * 2:
            return 0.8
        return 1.0

    # Underqualified: scale down proportionally
    if required_years == 0:
        return 1.0
    ratio = candidate_years / required_years
    return max(ratio, 0.0)


def _certifications_score(
    candidate_certs: list["CandidateCertification"],
    job: "JobPosting",
) -> float:
    """
    Binary: 1.0 if candidate holds all required certifications, 0.0 if any missing.
    Bonus: partial credit if no certs required (candidate's extras don't hurt).
    """
    required = job.certifications_required or []
    if not required:
        return 1.0

    candidate_cert_names = {c.certification_name.lower() for c in candidate_certs}
    missing = [r for r in required if r.lower() not in candidate_cert_names]
    return 0.0 if missing else 1.0


def _schedule_score(
    pref: "CandidatePreference | None",
    job: "JobPosting",
) -> float:
    """
    Matches candidate's preferred schedule against the job's contract_type.
    Exact match = 1.0, partial = 0.5, mismatch = 0.0.
    """
    if pref is None or not pref.preferred_schedule:
        return 0.5  # No preference → neutral

    preferred = pref.preferred_schedule.lower()
    contract = job.contract_type.lower()

    # Simple keyword matching; full NLP comparison is a Phase 2 improvement
    if preferred in contract or contract in preferred:
        return 1.0
    # Partial overlaps
    full_time_terms = {"full-time", "full time", "40 hours"}
    part_time_terms = {"part-time", "part time", "flexible"}
    if any(t in preferred for t in full_time_terms) and "full" in contract:
        return 1.0
    if any(t in preferred for t in part_time_terms) and "part" in contract:
        return 1.0
    return 0.0


def _industry_score(
    work_history: list["CandidateWorkHistory"],
    job: "JobPosting",
) -> float:
    """
    Checks if candidate's previous industries align with the job's sector.
    Same = 1.0, related = 0.5, no match = 0.0.
    """
    if not job.sector:
        return 0.5

    job_sector = job.sector.lower()
    # In a real system, work history rows would have an industry field.
    # For now, we do a simple keyword search in company/title descriptions.
    candidate_industries: set[str] = set()
    for wh in work_history:
        text = f"{wh.company} {wh.title} {wh.description or ''}".lower()
        for keyword in _RELATED_INDUSTRIES:
            if keyword in text:
                candidate_industries.add(keyword)

    if job_sector in candidate_industries:
        return 1.0

    related = _RELATED_INDUSTRIES.get(job_sector, set())
    if candidate_industries & related:
        return 0.5

    return 0.0


# ── Public interface ──────────────────────────────────────────────────────────

def calculate_match_score(
    candidate_skills: list,
    candidate_work_history: list,
    candidate_certifications: list,
    candidate_pref: object | None,
    job: "JobPosting",
) -> dict:
    """
    Calculate the composite match score for a candidate↔job pair.

    Returns:
        {
            "score": int (0-100),
            "factors": {
                "skills": int,
                "commute": int,
                "experience": int,
                "certifications": int,
                "schedule": int,
                "industry": int,
            }
        }
    """
    skills      = _skills_score(candidate_skills, job.required_skills)
    commute     = _commute_score(candidate_pref, job)
    experience  = _experience_score(candidate_work_history, job)
    certs       = _certifications_score(candidate_certifications, job)
    schedule    = _schedule_score(candidate_pref, job)
    industry    = _industry_score(candidate_work_history, job)

    composite = (
        skills     * 0.30
        + commute  * 0.25
        + experience * 0.15
        + certs    * 0.10
        + schedule * 0.10
        + industry * 0.10
    )

    return {
        "score": round(composite * 100),
        "factors": {
            "skills":          round(skills * 100),
            "commute":         round(commute * 100),
            "experience":      round(experience * 100),
            "certifications":  round(certs * 100),
            "schedule":        round(schedule * 100),
            "industry":        round(industry * 100),
        },
    }
