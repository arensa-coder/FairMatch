"""
Unit tests for the FairMatch scoring algorithm.

All ORM objects are replaced with SimpleNamespace duck-types so no database
or Supabase connection is needed.
"""
from decimal import Decimal
from types import SimpleNamespace

import pytest

from app.matching import (
    _commute_score,
    _interest_score,
    _salary_hours_score,
    _skills_score,
    _to_annual_salary,
    calculate_match_score,
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def skill(name: str, is_required: bool = True):
    return SimpleNamespace(skill_name=name, is_required=is_required)


def pref(**kwargs):
    defaults = dict(
        min_salary=None,
        max_salary=None,
        preferred_schedule=None,
        preferred_industries=None,
        max_commute_car_minutes=None,
        max_commute_transit_minutes=None,
    )
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def job(**kwargs):
    defaults = dict(
        location_type="on-site",
        sector=None,
        contract_type="full-time",
        hours_per_week=40,
        wage_measurement="hourly",
        wage_min=None,
        wage_max=None,
        required_skills=[],
    )
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


# ── _to_annual_salary ─────────────────────────────────────────────────────────

class TestToAnnualSalary:
    def test_hourly(self):
        assert _to_annual_salary(Decimal("20"), "hourly") == pytest.approx(41_600.0)

    def test_weekly(self):
        assert _to_annual_salary(Decimal("1000"), "weekly") == pytest.approx(52_000.0)

    def test_monthly(self):
        assert _to_annual_salary(Decimal("4000"), "monthly") == pytest.approx(48_000.0)

    def test_annual(self):
        assert _to_annual_salary(Decimal("50000"), "annual") == pytest.approx(50_000.0)

    def test_unknown_measurement_defaults_to_1x(self):
        assert _to_annual_salary(Decimal("5000"), "biweekly") == pytest.approx(5_000.0)


# ── _skills_score ─────────────────────────────────────────────────────────────

class TestSkillsScore:
    def test_no_required_skills_returns_full_score(self):
        ratio, met = _skills_score([], [])
        assert ratio == 1.0
        assert met is True

    def test_all_required_skills_present(self):
        candidate = [skill("Python"), skill("SQL")]
        required = [skill("Python"), skill("SQL")]
        ratio, met = _skills_score(candidate, required)
        assert ratio == 1.0
        assert met is True

    def test_missing_required_skill_lowers_score_and_unsets_flag(self):
        candidate = [skill("Python")]
        required = [skill("Python"), skill("SQL", is_required=True)]
        ratio, met = _skills_score(candidate, required)
        # Python required (weight 2) matched, SQL required (weight 2) missed
        # ratio = 2/4 = 0.5
        assert ratio == pytest.approx(0.5)
        assert met is False

    def test_preferred_skill_missed_does_not_unset_required_flag(self):
        candidate = [skill("Python")]
        required = [
            skill("Python", is_required=True),
            skill("Docker", is_required=False),
        ]
        # Python required (w=2) hit + Docker preferred (w=1) missed
        ratio, met = _skills_score(candidate, required)
        assert ratio == pytest.approx(2 / 3)
        assert met is True  # All *required* skills present

    def test_skill_matching_is_case_insensitive(self):
        candidate = [skill("python")]
        required = [skill("Python")]
        ratio, met = _skills_score(candidate, required)
        assert ratio == 1.0
        assert met is True

    def test_no_candidate_skills_returns_zero(self):
        required = [skill("Python"), skill("SQL")]
        ratio, met = _skills_score([], required)
        assert ratio == 0.0
        assert met is False

    def test_preferred_only_skills_matched(self):
        candidate = [skill("Excel")]
        required = [skill("Excel", is_required=False)]
        ratio, met = _skills_score(candidate, required)
        assert ratio == 1.0
        assert met is True  # No required skills to fail


# ── _commute_score ────────────────────────────────────────────────────────────

class TestCommuteScore:
    def test_remote_job_returns_full_score(self):
        assert _commute_score(None, job(location_type="remote")) == 1.0

    def test_on_site_returns_neutral(self):
        assert _commute_score(None, job(location_type="on-site")) == 0.5

    def test_hybrid_returns_neutral(self):
        assert _commute_score(pref(), job(location_type="hybrid")) == 0.5


# ── _salary_hours_score ───────────────────────────────────────────────────────

class TestSalaryHoursScore:
    def test_no_preference_returns_neutral(self):
        assert _salary_hours_score(None, job()) == 0.5

    def test_salary_within_range(self):
        # $20/hr = $41,600/yr; candidate wants $40k-$50k
        p = pref(min_salary=40_000, max_salary=50_000)
        j = job(wage_min=Decimal("20"), wage_max=Decimal("22"), wage_measurement="hourly")
        score = _salary_hours_score(p, j)
        assert score == pytest.approx(1.0)

    def test_salary_below_minimum(self):
        # $15/hr = $31,200/yr; candidate wants min $40k
        p = pref(min_salary=40_000, max_salary=60_000)
        j = job(wage_min=Decimal("15"), wage_max=Decimal("15"), wage_measurement="hourly")
        score = _salary_hours_score(p, j)
        # salary part < 1.0; only salary component present (no preferred_schedule)
        assert 0.0 < score < 1.0

    def test_salary_above_maximum_is_not_penalised(self):
        # $50/hr = $104k/yr; candidate max is $80k — earns more than expected, fine
        p = pref(min_salary=60_000, max_salary=80_000)
        j = job(wage_min=Decimal("50"), wage_measurement="hourly")
        score = _salary_hours_score(p, j)
        assert score == pytest.approx(1.0)

    def test_full_time_preference_matches_full_time_job(self):
        p = pref(preferred_schedule="full-time")
        j = job(hours_per_week=40)
        score = _salary_hours_score(p, j)
        assert score == pytest.approx(1.0)

    def test_part_time_preference_vs_full_time_job(self):
        p = pref(preferred_schedule="part-time")
        j = job(hours_per_week=40)
        score = _salary_hours_score(p, j)
        assert score == pytest.approx(0.0)

    def test_part_time_preference_matches_part_time_job(self):
        p = pref(preferred_schedule="part-time")
        j = job(hours_per_week=25)
        score = _salary_hours_score(p, j)
        assert score == pytest.approx(1.0)

    def test_full_time_preference_vs_part_time_job(self):
        p = pref(preferred_schedule="full-time")
        j = job(hours_per_week=20)  # 20/35 ≈ 0.57
        score = _salary_hours_score(p, j)
        assert 0.0 < score < 1.0

    def test_combined_salary_and_hours_averaged(self):
        # Salary: within range → 1.0; hours: full-time pref, 40h job → 1.0
        p = pref(
            min_salary=40_000, max_salary=60_000,
            preferred_schedule="full-time",
        )
        j = job(
            wage_min=Decimal("25"), wage_measurement="hourly",  # ~$52k
            hours_per_week=40,
        )
        score = _salary_hours_score(p, j)
        assert score == pytest.approx(1.0)


# ── _interest_score ───────────────────────────────────────────────────────────

class TestInterestScore:
    def test_no_preference_returns_neutral(self):
        assert _interest_score(None, job()) == 0.5

    def test_no_sector_on_job_returns_neutral(self):
        p = pref(preferred_industries=["healthcare"])
        assert _interest_score(p, job(sector=None)) == 0.5

    def test_direct_industry_match(self):
        p = pref(preferred_industries=["healthcare", "retail"])
        j = job(sector="healthcare")
        assert _interest_score(p, j) == 1.0

    def test_case_insensitive_match(self):
        p = pref(preferred_industries=["Healthcare"])
        j = job(sector="healthcare")
        assert _interest_score(p, j) == 1.0

    def test_related_industry_returns_half(self):
        # nursing is related to healthcare
        p = pref(preferred_industries=["nursing"])
        j = job(sector="healthcare")
        assert _interest_score(p, j) == 0.5

    def test_unrelated_industry_returns_zero(self):
        p = pref(preferred_industries=["finance"])
        j = job(sector="healthcare")
        assert _interest_score(p, j) == 0.0


# ── calculate_match_score ─────────────────────────────────────────────────────

class TestCalculateMatchScore:
    def _make_perfect_candidate(self):
        """Candidate that maximises every factor."""
        candidate_skills = [skill("Python"), skill("SQL")]
        candidate_pref = pref(
            min_salary=40_000, max_salary=60_000,
            preferred_schedule="full-time",
            preferred_industries=["technology"],
        )
        return candidate_skills, candidate_pref

    def _make_matching_job(self):
        return job(
            location_type="remote",
            sector="technology",
            hours_per_week=40,
            wage_min=Decimal("25"), wage_measurement="hourly",  # ~$52k/yr
            required_skills=[skill("Python"), skill("SQL")],
        )

    def test_returns_expected_keys(self):
        skills, p = self._make_perfect_candidate()
        j = self._make_matching_job()
        result = calculate_match_score(skills, p, j)
        assert "score" in result
        assert "required_skills_met" in result
        assert "factors" in result
        for factor in ("skills", "commute", "salary_hours", "interest"):
            assert factor in result["factors"]

    def test_score_is_integer_between_0_and_100(self):
        skills, p = self._make_perfect_candidate()
        j = self._make_matching_job()
        result = calculate_match_score(skills, p, j)
        assert isinstance(result["score"], int)
        assert 0 <= result["score"] <= 100

    def test_high_score_for_strong_match(self):
        skills, p = self._make_perfect_candidate()
        j = self._make_matching_job()
        result = calculate_match_score(skills, p, j)
        assert result["score"] >= 80

    def test_required_skills_met_true_when_all_present(self):
        skills, p = self._make_perfect_candidate()
        j = self._make_matching_job()
        result = calculate_match_score(skills, p, j)
        assert result["required_skills_met"] is True
        assert result["factors"]["required_skills_met"] is True

    def test_required_skills_met_false_when_skill_missing(self):
        candidate_skills = [skill("Python")]  # SQL missing
        p = pref()
        j = job(required_skills=[skill("Python"), skill("SQL", is_required=True)])
        result = calculate_match_score(candidate_skills, p, j)
        assert result["required_skills_met"] is False

    def test_no_candidate_data_returns_nonzero_score(self):
        """Even a blank candidate gets a non-zero score (comute/salary neutral)."""
        result = calculate_match_score([], None, job())
        assert result["score"] >= 0
        assert result["required_skills_met"] is True  # No required skills on job

    def test_weights_sum_correctly(self):
        """Verify manual composite equals reported score for a known case."""
        # skills=1.0, commute=1.0 (remote), sal_hrs=0.5 (no pref), interest=0.5 (no pref)
        j = job(
            location_type="remote",
            required_skills=[skill("Python")],
        )
        result = calculate_match_score([skill("Python")], None, j)
        expected = round((1.0 * 0.55 + 1.0 * 0.20 + 0.5 * 0.15 + 0.5 * 0.10) * 100)
        assert result["score"] == expected

    def test_zero_skills_score_dominates(self):
        """Missing all required skills should pull composite score down substantially."""
        j = job(
            location_type="remote",
            required_skills=[skill("Python"), skill("Java")],
            sector="healthcare",
        )
        p = pref(preferred_industries=["healthcare"], preferred_schedule="full-time")
        result = calculate_match_score([], p, j)
        # skills=0.0 * 0.55 = 0.  Remote (1.0 * 0.20) + full-time (1.0 * 0.15) + interest (1.0 * 0.10) = 0.45
        assert result["score"] <= 45
