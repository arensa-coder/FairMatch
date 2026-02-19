"""
FairMatch API — FastAPI application entrypoint.

All routes are versioned under /api/v1/.
Swagger UI available at /docs (disabled in production).
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import candidates, employers, host_orgs, job_fairs, jobs, users

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: could initialize Redis connection pool, etc.
    yield
    # Shutdown: cleanup resources


app = FastAPI(
    title=settings.app_name,
    description=(
        "FairMatch API — connecting nonprofits, job seekers, and employers "
        "through intelligent job fair matching."
    ),
    version="0.1.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan,
)

# ─── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routers ──────────────────────────────────────────────────────────────────
PREFIX = settings.api_prefix  # /api/v1

app.include_router(users.router, prefix=PREFIX)
app.include_router(host_orgs.router, prefix=PREFIX)
app.include_router(employers.router, prefix=PREFIX)
app.include_router(candidates.router, prefix=PREFIX)
app.include_router(job_fairs.router, prefix=PREFIX)
app.include_router(jobs.router, prefix=PREFIX)


# ─── Health check ─────────────────────────────────────────────────────────────
@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok", "service": settings.app_name}
