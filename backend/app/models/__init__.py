# Import all models so Alembic can detect them for migrations
from app.models.user import User, HostOrganization, Employer, Candidate  # noqa: F401
from app.models.employer import (  # noqa: F401
    EmployerAddress,
    EmployerContact,
    EmployerRelationship,
    EmployerNote,
)
from app.models.candidate import (  # noqa: F401
    CandidateSkill,
    CandidateWorkHistory,
    CandidateEducation,
    CandidateCertification,
    CandidatePreference,
    CandidateBarrier,
)
from app.models.job_fair import JobFair, FairHostOrg, FairEmployer, FairCandidate  # noqa: F401
from app.models.job import (  # noqa: F401
    JobPosting,
    JobRequiredSkill,
    JobRequiredCertification,
    MatchScore,
    CandidateJobInteraction,
    CandidateApplication,
)
from app.models.activity import (  # noqa: F401
    CandidateEmployerInteraction,
    HiringOutcome,
    Feedback,
    Notification,
)
