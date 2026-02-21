"""
FairMatch scoring algorithm.

Factor weights
--------------
  Skills        55%  — primary/required factor
  Commute       20%  — nice-to-have
  Salary/Hours  15%  — nice-to-have
  Interest      10%  — nice-to-have (preferred-industry alignment)

All four factors contribute to the 0-100 composite score.
``required_skills_met`` in the result flags whether the candidate holds
every skill marked ``is_required=True`` on the posting.

Matches are never suppressed by score — every job is shown to candidates,
ordered by score descending.  The old MATCH_THRESHOLD constant has been
removed.
"""
from __future__ import annotations

import logging
from decimal import Decimal
from typing import TYPE_CHECKING

import httpx

if TYPE_CHECKING:
    from app.models.candidate import CandidateSkill, CandidatePreference
    from app.models.job import JobPosting, JobRequiredSkill

log = logging.getLogger(__name__)

# ── Wage normalisation to approximate annual salary ──────────────────────────
_TO_ANNUAL: dict[str, float] = {
    "hourly":  2080.0,   # 40 h/wk × 52 wk
    "weekly":  52.0,
    "monthly": 12.0,
    "annual":  1.0,
}


def _to_annual_salary(amount: Decimal | float, measurement: str) -> float:
    """Convert a wage amount to an approximate annual figure."""
    factor = _TO_ANNUAL.get(measurement.lower(), 1.0)
    return float(amount) * factor


# ── Industry relatedness map ──────────────────────────────────────────────────
_RELATED_INDUSTRIES: dict[str, set[str]] = {
    "construction":  {"manufacturing", "trades", "maintenance"},
    "healthcare":    {"nursing", "medical", "social_services"},
    "retail":        {"sales", "hospitality", "customer_service"},
    "hospitality":   {"food_service", "retail", "tourism"},
    "manufacturing": {"construction", "logistics", "trades"},
    "nonprofit":     {"social_services", "education", "government"},
}


# ── Scoring sub-functions ─────────────────────────────────────────────────────

def _skills_score(
    candidate_skills: list["CandidateSkill"],
    required_skills: list["JobRequiredSkill"],
) -> tuple[float, bool]:
    """
    Returns ``(ratio, required_skills_met)``.

    ratio
        Weighted proportion of job skills the candidate satisfies.
        Required skills (``is_required=True``) count 2× ; preferred count 1×.

    required_skills_met
        True only when every ``is_required`` skill is present on the candidate.
    """
    if not required_skills:
        return 1.0, True

    candidate_names = {s.skill_name.lower() for s in candidate_skills}

    total_weight = 0.0
    matched_weight = 0.0
    all_required_met = True

    for rs in required_skills:
        weight = 2.0 if rs.is_required else 1.0
        total_weight += weight
        if rs.skill_name.lower() in candidate_names:
            matched_weight += weight
        elif rs.is_required:
            all_required_met = False

    ratio = matched_weight / total_weight if total_weight else 0.0
    return ratio, all_required_met


_GMAPS_URL = "https://maps.googleapis.com/maps/api/distancematrix/json"


def _duration_to_score(actual_minutes: float, max_minutes: float) -> float:
    """1.0 if within limit; linearly decays to 0.0 at 2× the limit."""
    if actual_minutes <= max_minutes:
        return 1.0
    return max(0.0, 1.0 - (actual_minutes - max_minutes) / max_minutes)


def _gmaps_duration_minutes(
    origin: str,
    destination: str,
    mode: str,
    api_key: str,
) -> float | None:
    """
    Call Google Maps Distance Matrix API and return travel time in minutes.
    Returns None on any error (network, quota, no route).
    """
    try:
        resp = httpx.get(
            _GMAPS_URL,
            params={
                "origins": origin,
                "destinations": destination,
                "mode": mode,
                "key": api_key,
            },
            timeout=5.0,
        )
        resp.raise_for_status()
        data = resp.json()
        element = data["rows"][0]["elements"][0]
        if element.get("status") != "OK":
            return None
        return element["duration"]["value"] / 60.0  # seconds → minutes
    except Exception as exc:  # noqa: BLE001
        log.warning("Google Maps API error (%s %s): %s", mode, destination, exc)
        return None


def _commute_score(
    candidate_pref: "CandidatePreference | None",
    job: "JobPosting",
    candidate_address: str | None = None,
) -> float:
    """
    1.0  — remote job (no commute).
    0.0–1.0 — scored against candidate's max commute preferences via Google
               Maps Distance Matrix API (transit and/or driving).
    0.5  — neutral fallback when addresses or API key are missing/unavailable.
    """
    if getattr(job, "location_type", None) == "remote":
        return 1.0

    job_address = getattr(job, "job_address_text", None)
    if not candidate_address or not job_address:
        return 0.5  # No address data available

    # Import here to avoid circular imports at module load time
    from app.config import get_settings  # noqa: PLC0415
    api_key = get_settings().google_maps_api_key
    if not api_key:
        return 0.5  # API key not configured

    max_transit = getattr(candidate_pref, "max_commute_transit_minutes", None)
    max_car = getattr(candidate_pref, "max_commute_car_minutes", None)

    if not max_transit and not max_car:
        return 0.5  # Candidate has no commute preference set

    scores: list[float] = []

    if max_transit:
        mins = _gmaps_duration_minutes(candidate_address, job_address, "transit", api_key)
        if mins is not None:
            scores.append(_duration_to_score(mins, float(max_transit)))

    if max_car:
        mins = _gmaps_duration_minutes(candidate_address, job_address, "driving", api_key)
        if mins is not None:
            scores.append(_duration_to_score(mins, float(max_car)))

    return sum(scores) / len(scores) if scores else 0.5


def _salary_hours_score(
    candidate_pref: "CandidatePreference | None",
    job: "JobPosting",
) -> float:
    """
    Average of two sub-scores: salary fit and hours fit.
    Returns 0.5 (neutral) when either side has no data.

    Salary
        Job's wage range normalised to annual and compared against the
        candidate's ``min_salary`` / ``max_salary`` preference (assumed annual).
        - Within range → 1.0
        - Above max    → 1.0 (earning more than desired is fine)
        - Below min    → scaled down proportionally

    Hours
        ``job.hours_per_week`` compared against ``preferred_schedule``.
        - "full-time" preference → 1.0 for ≥ 35 h/wk, scales to 0 below
        - "part-time"/"flexible" → 1.0 for ≤ 30 h/wk, scales to 0 above 40
    """
    parts: list[float] = []

    # ── Salary component ──────────────────────────────────────────────────────
    cand_min = getattr(candidate_pref, "min_salary", None)
    cand_max = getattr(candidate_pref, "max_salary", None)
    job_wage_min = getattr(job, "wage_min", None)

    if (cand_min is not None or cand_max is not None) and job_wage_min is not None:
        job_annual_min = _to_annual_salary(job.wage_min, job.wage_measurement)
        raw_max = getattr(job, "wage_max", None) or job.wage_min
        job_annual_max = _to_annual_salary(raw_max, job.wage_measurement)
        job_mid = (job_annual_min + job_annual_max) / 2

        lo = float(cand_min) if cand_min is not None else 0.0
        hi = float(cand_max) if cand_max is not None else float("inf")

        if lo <= job_mid <= hi:
            parts.append(1.0)
        elif job_mid < lo:
            gap_ratio = (lo - job_mid) / lo if lo > 0 else 0.0
            parts.append(max(0.0, 1.0 - gap_ratio))
        else:
            # Pays more than candidate's maximum preference — not a problem
            parts.append(1.0)

    # ── Hours component ───────────────────────────────────────────────────────
    preferred_schedule = getattr(candidate_pref, "preferred_schedule", None)
    hours = getattr(job, "hours_per_week", None)

    if preferred_schedule and hours is not None:
        preferred = preferred_schedule.lower()
        if any(t in preferred for t in ("full-time", "full time", "40")):
            hours_score = 1.0 if hours >= 35 else max(0.0, hours / 35)
        elif any(t in preferred for t in ("part-time", "part time", "flexible")):
            hours_score = 1.0 if hours <= 30 else max(0.0, (40 - hours) / 10)
        else:
            hours_score = 0.5
        parts.append(hours_score)

    return sum(parts) / len(parts) if parts else 0.5


def _interest_score(
    candidate_pref: "CandidatePreference | None",
    job: "JobPosting",
) -> float:
    """
    Compares ``candidate_pref.preferred_industries`` (list of strings) against
    ``job.sector``.

    - Direct match  → 1.0
    - Related sector → 0.5
    - No match       → 0.0
    - Missing data   → 0.5 (neutral)
    """
    preferred = getattr(candidate_pref, "preferred_industries", None)
    sector = getattr(job, "sector", None)

    if not preferred or not sector:
        return 0.5  # No preference data → neutral

    preferred_set = {i.lower() for i in preferred}
    job_sector = sector.lower()

    if job_sector in preferred_set:
        return 1.0

    related = _RELATED_INDUSTRIES.get(job_sector, set())
    if preferred_set & related:
        return 0.5

    return 0.0


# ── Public interface ──────────────────────────────────────────────────────────

def calculate_match_score(
    candidate_skills: list,
    candidate_pref: object | None,
    job: "JobPosting",
    candidate_address: str | None = None,
) -> dict:
    """
    Calculate the composite match score for a candidate↔job pair.

    Parameters
    ----------
    candidate_skills
        List of ``CandidateSkill`` ORM objects (or duck-typed equivalents).
    candidate_pref
        ``CandidatePreference`` ORM object, or ``None`` if not set.
    job
        ``JobPosting`` ORM object.

    Returns
    -------
    dict::

        {
            "score":               int,   # 0-100 composite
            "required_skills_met": bool,  # False → candidate missing a required skill
            "factors": {
                "skills":               int,  # 0-100
                "commute":              int,
                "salary_hours":         int,
                "interest":             int,
                "required_skills_met":  bool,  # also stored here for DB persistence
            },
        }
    """
    skills_ratio, required_skills_met = _skills_score(
        candidate_skills, getattr(job, "required_skills", [])
    )
    commute  = _commute_score(candidate_pref, job, candidate_address)
    sal_hrs  = _salary_hours_score(candidate_pref, job)
    interest = _interest_score(candidate_pref, job)

    composite = (
        skills_ratio * 0.55
        + commute    * 0.20
        + sal_hrs    * 0.15
        + interest   * 0.10
    )

    return {
        "score": round(composite * 100),
        "required_skills_met": required_skills_met,
        "factors": {
            "skills":              round(skills_ratio * 100),
            "commute":             round(commute * 100),
            "salary_hours":        round(sal_hrs * 100),
            "interest":            round(interest * 100),
            "required_skills_met": required_skills_met,
        },
    }
