"""
pytest configuration for the backend test suite.

app.database calls create_engine() at module import time with a PostgreSQL
URL.  In CI / test environments without a real Postgres, we intercept that
call and replace it with an in-memory SQLite engine before any app module
is imported.

All router tests override the ``get_db`` dependency with a MagicMock session
anyway, so the SQLite engine is only needed to satisfy SQLAlchemy's
SessionLocal constructor — it is never actually queried.
"""
import os
import sys

# ── 1. Environment variables (pydantic-settings reads these at startup) ───────
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("SUPABASE_JWT_SECRET", "test-secret")
os.environ.setdefault("SUPABASE_URL", "https://test.supabase.co")
os.environ.setdefault("SUPABASE_ANON_KEY", "test-anon")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "test-service")
os.environ.setdefault("FIELD_ENCRYPTION_KEY", "")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")

# ── 2. Replace create_engine so the default postgres URL becomes SQLite ───────
# This must happen *before* app.database is first imported.
import sqlalchemy as _sa
_real_create_engine = _sa.create_engine


def _test_create_engine(url, **kwargs):
    """Route any postgres:// URL to an in-memory SQLite engine for tests."""
    url_str = str(url)
    sqlite_url = url_str
    if url_str.startswith("postgresql") or url_str.startswith("postgres"):
        sqlite_url = "sqlite:///:memory:"

    if sqlite_url.startswith("sqlite"):
        # Strip kwargs that are invalid for SQLite
        kwargs.pop("pool_size", None)
        kwargs.pop("max_overflow", None)
        kwargs.pop("pool_pre_ping", None)
        return _real_create_engine(
            sqlite_url,
            connect_args={"check_same_thread": False},
            **kwargs,
        )
    return _real_create_engine(url, **kwargs)


_sa.create_engine = _test_create_engine
