/**
 * A single factor bar row: label | track | value%
 * Color blends from blue at low end to orange at high end.
 */
export default function FactorBar({ label, value }) {
  const pct = Math.min(100, Math.max(0, value));

  // Gradient: low → blue-500, high → orange-500
  const fillColor =
    pct >= 80 ? 'var(--orange-500)' :
    pct >= 60 ? 'var(--blue-500)'   :
    pct >= 40 ? 'var(--blue-400, #60a5fa)' :
                'var(--slate-400)';

  return (
    <div className="factor-row">
      <span className="factor-label">{label}</span>
      <div className="factor-track">
        <div
          className="factor-fill"
          style={{ width: `${pct}%`, background: fillColor }}
        />
      </div>
      <span className="factor-value">{pct}%</span>
    </div>
  );
}
