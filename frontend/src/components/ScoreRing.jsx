/**
 * Circular SVG score ring.
 *  ≥ 80 → orange   (great match)
 *  60–79 → blue    (good match)
 *  < 60  → slate   (partial match)
 */
export default function ScoreRing({ score }) {
  const r = 28;
  const circ = 2 * Math.PI * r;
  const filled = (Math.min(100, Math.max(0, score)) / 100) * circ;

  const color =
    score >= 80 ? 'var(--orange-500)' :
    score >= 60 ? 'var(--blue-500)'   :
                  'var(--slate-400)';

  const textColor =
    score >= 80 ? 'var(--orange-600)' :
    score >= 60 ? 'var(--blue-700)'   :
                  'var(--slate-500)';

  return (
    <div className="score-ring-wrap">
      <svg width="72" height="72" viewBox="0 0 72 72">
        {/* Track */}
        <circle
          cx="36" cy="36" r={r}
          fill="none"
          stroke="var(--slate-100)"
          strokeWidth="7"
        />
        {/* Fill */}
        <circle
          cx="36" cy="36" r={r}
          fill="none"
          stroke={color}
          strokeWidth="7"
          strokeDasharray={`${filled} ${circ - filled}`}
          strokeLinecap="round"
          transform="rotate(-90 36 36)"
          style={{ transition: 'stroke-dasharray 0.6s ease' }}
        />
      </svg>
      <div className="score-ring-label">
        <span className="score-num" style={{ color: textColor }}>{score}</span>
        <span className="score-pct">%</span>
      </div>
    </div>
  );
}
