"""
Integration tests for the /jobs router.

The database and Supabase JWT are replaced with in-process mocks via
FastAPI dependency overrides, so no real Postgres or Supabase connection
is required.
"""
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.auth import get_current_user
from app.database import get_db


# ── Test fixtures ─────────────────────────────────────────────────────────────

def _make_user(user_type: str = "host_org") -> SimpleNamespace:
    return SimpleNamespace(
        id=uuid.uuid4(),
        user_type=user_type,
        is_active=True,
        email="test@example.com",
    )


def _make_candidate(user_id=None) -> SimpleNamespace:
    return SimpleNamespace(
        id=uuid.uuid4(),
        user_id=user_id or uuid.uuid4(),
        home_address=None,
        skills=[],
        preferences=None,
        work_history=[],
        certifications=[],
    )


def _make_job(fair_employer_id=None) -> SimpleNamespace:
    return SimpleNamespace(
        id=uuid.uuid4(),
        fair_employer_id=fair_employer_id or uuid.uuid4(),
        title="Software Engineer",
        job_order_name="SE-001",
        status="active",
        contract_type="full-time",
        location_type="remote",
        wage_measurement="hourly",
        wage_min=Decimal("25"),
        wage_max=Decimal("30"),
        hours_per_week=40,
        sector="technology",
        required_skills=[],
        certifications_required=[],
        experience_level=None,
        description=None,
        description_url=None,
        employer_industry=None,
        anticipated_schedule=None,
        anticipated_start_date=None,
        benefits=None,
        remote_days=None,
        job_address_text=None,
        education_required=None,
        background_check_required=False,
        other_requirements=None,
        number_of_openings=1,
        close_date=None,
        application_url=None,
        uses_internal_application=False,
        is_anonymous=False,
        recommended_attire=None,
        wage_average=Decimal("27.5"),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


def _make_match_score(candidate_id, job_id, fair_id, score=75) -> SimpleNamespace:
    return SimpleNamespace(
        id=uuid.uuid4(),
        candidate_id=candidate_id,
        job_id=job_id,
        fair_id=fair_id,
        score=score,
        factors={"skills": 80, "commute": 100, "salary_hours": 60, "interest": 50},
        ec_status="approved",
        ec_reviewed_by=None,
        ec_reviewed_at=None,
        ec_note=None,
        generated_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def mock_db():
    return MagicMock()


def override_db(mock_session):
    def _override():
        yield mock_session
    return _override


def override_user(user):
    def _override():
        return user
    return _override


# ── Health check ──────────────────────────────────────────────────────────────

def test_health_check():
    client = TestClient(app)
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


# ── GET /jobs/matches/me/{fair_id} ────────────────────────────────────────────

class TestMyMatchesForFair:
    def setup_method(self):
        self.fair_id = uuid.uuid4()
        self.user = _make_user("candidate")
        self.candidate = _make_candidate(user_id=self.user.id)
        self.db = MagicMock()

    def _client(self):
        app.dependency_overrides[get_current_user] = override_user(self.user)
        app.dependency_overrides[get_db] = override_db(self.db)
        return TestClient(app)

    def teardown_method(self):
        app.dependency_overrides.clear()

    def test_returns_all_approved_matches_no_threshold(self):
        """Endpoint must return approved matches of any score — no 60-pt floor."""
        job1 = _make_job()
        low_score_match = _make_match_score(
            self.candidate.id, job1.id, self.fair_id, score=20
        )
        high_score_match = _make_match_score(
            self.candidate.id, job1.id, self.fair_id, score=90
        )

        # Simulate DB query chain returning both matches
        query_mock = MagicMock()
        query_mock.filter.return_value = query_mock
        query_mock.order_by.return_value = query_mock
        query_mock.all.return_value = [high_score_match, low_score_match]

        self.db.query.return_value = query_mock

        # Simulate candidate lookup
        candidate_query = MagicMock()
        candidate_query.filter.return_value = candidate_query
        candidate_query.first.return_value = self.candidate

        # db.query is called twice: once for Candidate, once for MatchScore
        self.db.query.side_effect = [candidate_query, query_mock]

        client = self._client()
        resp = client.get(f"/api/v1/jobs/matches/me/{self.fair_id}")

        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2
        scores = [d["score"] for d in data]
        assert 20 in scores
        assert 90 in scores

    def test_returns_sorted_by_score_descending(self):
        match_low = _make_match_score(self.candidate.id, uuid.uuid4(), self.fair_id, score=30)
        match_high = _make_match_score(self.candidate.id, uuid.uuid4(), self.fair_id, score=85)

        query_mock = MagicMock()
        query_mock.filter.return_value = query_mock
        query_mock.order_by.return_value = query_mock
        query_mock.all.return_value = [match_high, match_low]

        candidate_query = MagicMock()
        candidate_query.filter.return_value = candidate_query
        candidate_query.first.return_value = self.candidate

        self.db.query.side_effect = [candidate_query, query_mock]

        client = self._client()
        resp = client.get(f"/api/v1/jobs/matches/me/{self.fair_id}")

        assert resp.status_code == 200
        scores = [d["score"] for d in resp.json()]
        assert scores == sorted(scores, reverse=True)

    def test_empty_result_returns_empty_list(self):
        query_mock = MagicMock()
        query_mock.filter.return_value = query_mock
        query_mock.order_by.return_value = query_mock
        query_mock.all.return_value = []

        candidate_query = MagicMock()
        candidate_query.filter.return_value = candidate_query
        candidate_query.first.return_value = self.candidate

        self.db.query.side_effect = [candidate_query, query_mock]

        client = self._client()
        resp = client.get(f"/api/v1/jobs/matches/me/{self.fair_id}")

        assert resp.status_code == 200
        assert resp.json() == []

    def test_returns_404_when_candidate_profile_missing(self):
        candidate_query = MagicMock()
        candidate_query.filter.return_value = candidate_query
        candidate_query.first.return_value = None  # No candidate profile

        self.db.query.return_value = candidate_query

        client = self._client()
        resp = client.get(f"/api/v1/jobs/matches/me/{self.fair_id}")
        assert resp.status_code == 404


# ── POST /jobs/{job_id}/compute-match/{candidate_id} ─────────────────────────

class TestComputeMatch:
    def setup_method(self):
        self.ec_user = _make_user("host_org")
        self.db = MagicMock()

    def _client(self):
        app.dependency_overrides[get_current_user] = override_user(self.ec_user)
        app.dependency_overrides[get_db] = override_db(self.db)
        return TestClient(app)

    def teardown_method(self):
        app.dependency_overrides.clear()

    def test_computes_and_returns_match_score(self):
        job = _make_job()
        fair_employer = SimpleNamespace(id=job.fair_employer_id, fair_id=uuid.uuid4())
        candidate = _make_candidate()

        self.db.get.side_effect = lambda model, pk: {
            job.id: job,
            candidate.id: candidate,
            fair_employer.id: fair_employer,
        }.get(pk)

        # No existing match score → insert path
        ms_query = MagicMock()
        ms_query.filter.return_value = ms_query
        ms_query.first.return_value = None
        self.db.query.return_value = ms_query

        # Capture the MatchScore added to the session
        added_objects = []
        self.db.add.side_effect = added_objects.append

        new_ms = _make_match_score(candidate.id, job.id, fair_employer.fair_id, score=75)

        def mock_refresh(obj):
            # Simulate DB assigning id / generated_at
            obj.__dict__.update(new_ms.__dict__)

        self.db.refresh.side_effect = mock_refresh

        client = self._client()
        resp = client.post(
            f"/api/v1/jobs/{job.id}/compute-match/{candidate.id}"
        )

        assert resp.status_code == 200
        data = resp.json()
        assert "score" in data
        assert "factors" in data
        assert isinstance(data["score"], int)

    def test_requires_host_org_role(self):
        employer_user = _make_user("employer")
        app.dependency_overrides[get_current_user] = override_user(employer_user)
        app.dependency_overrides[get_db] = override_db(self.db)

        client = TestClient(app)
        resp = client.post(
            f"/api/v1/jobs/{uuid.uuid4()}/compute-match/{uuid.uuid4()}"
        )
        assert resp.status_code == 403
        app.dependency_overrides.clear()

    def test_returns_404_for_missing_job(self):
        self.db.get.return_value = None

        client = self._client()
        resp = client.post(
            f"/api/v1/jobs/{uuid.uuid4()}/compute-match/{uuid.uuid4()}"
        )
        assert resp.status_code == 404


# ── EC match review ───────────────────────────────────────────────────────────

class TestMatchReview:
    def setup_method(self):
        self.ec_user = _make_user("host_org")
        self.db = MagicMock()

    def _client(self):
        app.dependency_overrides[get_current_user] = override_user(self.ec_user)
        app.dependency_overrides[get_db] = override_db(self.db)
        return TestClient(app)

    def teardown_method(self):
        app.dependency_overrides.clear()

    def test_approve_sets_ec_status(self):
        ms = _make_match_score(uuid.uuid4(), uuid.uuid4(), uuid.uuid4())
        self.db.get.return_value = ms

        client = self._client()
        resp = client.post(
            f"/api/v1/jobs/matches/{ms.id}/review",
            json={"action": "approved", "ec_note": "Good fit"},
        )
        assert resp.status_code == 200
        assert ms.ec_status == "approved"
        assert ms.ec_note == "Good fit"

    def test_decline_sets_ec_status(self):
        ms = _make_match_score(uuid.uuid4(), uuid.uuid4(), uuid.uuid4())
        self.db.get.return_value = ms

        client = self._client()
        resp = client.post(
            f"/api/v1/jobs/matches/{ms.id}/review",
            json={"action": "declined"},
        )
        assert resp.status_code == 200
        assert ms.ec_status == "declined"

    def test_invalid_action_returns_400(self):
        client = self._client()
        resp = client.post(
            f"/api/v1/jobs/matches/{uuid.uuid4()}/review",
            json={"action": "banana"},
        )
        assert resp.status_code == 400

    def test_missing_match_returns_404(self):
        self.db.get.return_value = None
        client = self._client()
        resp = client.post(
            f"/api/v1/jobs/matches/{uuid.uuid4()}/review",
            json={"action": "approved"},
        )
        assert resp.status_code == 404


# ── List pending matches ──────────────────────────────────────────────────────

class TestListPendingMatches:
    def setup_method(self):
        self.ec_user = _make_user("host_org")
        self.db = MagicMock()

    def _client(self):
        app.dependency_overrides[get_current_user] = override_user(self.ec_user)
        app.dependency_overrides[get_db] = override_db(self.db)
        return TestClient(app)

    def teardown_method(self):
        app.dependency_overrides.clear()

    def test_returns_pending_matches_sorted_by_score(self):
        m1 = _make_match_score(uuid.uuid4(), uuid.uuid4(), uuid.uuid4(), score=70)
        m2 = _make_match_score(uuid.uuid4(), uuid.uuid4(), uuid.uuid4(), score=90)
        m1.ec_status = "pending_ec_review"
        m2.ec_status = "pending_ec_review"

        query_mock = MagicMock()
        query_mock.filter.return_value = query_mock
        query_mock.order_by.return_value = query_mock
        query_mock.all.return_value = [m2, m1]
        self.db.query.return_value = query_mock

        client = self._client()
        resp = client.get("/api/v1/jobs/matches/pending")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_candidate_cannot_access_pending_matches(self):
        candidate_user = _make_user("candidate")
        app.dependency_overrides[get_current_user] = override_user(candidate_user)
        app.dependency_overrides[get_db] = override_db(self.db)
        client = TestClient(app)
        resp = client.get("/api/v1/jobs/matches/pending")
        assert resp.status_code == 403
        app.dependency_overrides.clear()
