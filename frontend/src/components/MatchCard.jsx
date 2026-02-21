import ScoreRing from './ScoreRing.jsx';
import FactorBar from './FactorBar.jsx';

const SECTOR_ICONS = {
  logistics:     '📦',
  warehouse:     '📦',
  healthcare:    '🏥',
  nursing:       '🏥',
  medical:       '🏥',
  retail:        '🛍️',
  sales:         '🛍️',
  hospitality:   '🍽️',
  food_service:  '🍽️',
  construction:  '🏗️',
  trades:        '🔧',
  manufacturing: '⚙️',
  education:     '📚',
  technology:    '💻',
  nonprofit:     '🤝',
  social_services: '🤝',
  government:    '🏛️',
};

function getSectorIcon(sector) {
  return SECTOR_ICONS[sector?.toLowerCase()] ?? '💼';
}

function formatWage(job) {
  const { wage_measurement, wage_min, wage_max } = job;
  if (!wage_min) return null;

  const suffix = { hourly: '/hr', weekly: '/wk', monthly: '/mo', annual: '/yr' }[wage_measurement] ?? '';
  const fmt = (n) => {
    if (wage_measurement === 'annual') return `$${(n / 1000).toFixed(0)}k`;
    return `$${Number(n).toFixed(wage_measurement === 'hourly' ? 2 : 0)}`;
  };

  return wage_max && wage_max !== wage_min
    ? `${fmt(wage_min)}–${fmt(wage_max)}${suffix}`
    : `${fmt(wage_min)}${suffix}`;
}

function formatLocation(job) {
  if (job.location_type === 'remote') return { label: '🌐 Remote', cls: 'remote' };
  if (job.location_type === 'hybrid') {
    const days = job.remote_days ? ` (${job.remote_days}d remote)` : '';
    return { label: `🏠 Hybrid${days}`, cls: 'hybrid' };
  }
  // on-site — show city only
  const city = job.job_address_text?.split(',').slice(1, 2).join('').trim()
    || job.job_address_text
    || 'On-site';
  return { label: `📍 ${city}`, cls: '' };
}

function getAccentColor(score) {
  if (score >= 80) return 'var(--orange-500)';
  if (score >= 60) return 'var(--blue-500)';
  return 'var(--slate-400)';
}

export default function MatchCard({ match, style }) {
  const { score, factors, job } = match;
  if (!job) return null;

  const { required_skills_met } = factors ?? {};
  const wage = formatWage(job);
  const loc  = formatLocation(job);
  const employerName = job.employer_name ?? (job.is_anonymous ? 'Anonymous Employer' : 'Employer');
  const openings = job.number_of_openings;
  const accentColor = getAccentColor(score);

  return (
    <div
      className="match-card"
      style={{ '--card-accent': accentColor, ...style }}
    >
      {/* Top section */}
      <div className="card-top">
        <ScoreRing score={score} />

        <div className="card-meta">
          <div className="card-title">{job.title}</div>
          <div className="card-employer">{employerName}</div>

          <div className="card-chips">
            <span className="chip sector">
              {getSectorIcon(job.sector)} {job.sector ?? 'General'}
            </span>

            {loc.label && (
              <span className={`chip ${loc.cls}`}>{loc.label}</span>
            )}

            {job.contract_type && (
              <span className="chip">
                ⏰ {job.contract_type === 'full-time' ? `Full-time ${job.hours_per_week ?? 40}h` : `Part-time ${job.hours_per_week ?? ''}h`}
              </span>
            )}

            {wage && <span className="chip wage">💰 {wage}</span>}
          </div>
        </div>
      </div>

      {/* Missing skills warning */}
      {required_skills_met === false && (
        <div className="skill-warning">
          ⚠️ You're missing one or more required skills for this role — it may still be worth applying.
        </div>
      )}

      {/* Factor breakdown */}
      {factors && (
        <div className="card-factors">
          <FactorBar label="Skills"        value={factors.skills        ?? 0} />
          <FactorBar label="Commute"       value={factors.commute       ?? 0} />
          <FactorBar label="Salary & Hrs"  value={factors.salary_hours  ?? 0} />
          <FactorBar label="Interest"      value={factors.interest      ?? 0} />
        </div>
      )}

      {/* Footer */}
      <div className="card-footer">
        <div className="card-footer-meta">
          {openings > 1 && <span>{openings} openings · </span>}
          {job.experience_level && <span>{job.experience_level}</span>}
        </div>

        <div className="card-actions">
          <button className="btn-secondary">Details</button>

          {job.uses_internal_application ? (
            <button className="btn-primary">Apply →</button>
          ) : job.application_url ? (
            <a href={job.application_url} target="_blank" rel="noreferrer">
              <button className="btn-primary">Apply →</button>
            </a>
          ) : (
            <button className="btn-primary">Express Interest →</button>
          )}
        </div>
      </div>
    </div>
  );
}
