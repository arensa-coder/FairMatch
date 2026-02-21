import ConfigPanel from './ConfigPanel.jsx';

/**
 * Simple geometric SVG face avatars — diverse skin tones and hair styles.
 * Deliberately illustrative (not photorealistic) and friendly-looking.
 */
const AVATARS = [
  // Dark brown skin, black afro
  {
    ring: '#1d4ed8',
    skin: '#5C3317',
    hairColor: '#0d0d0d',
    hair: 'afro',
    eyeShade: 'rgba(255,230,180,0.85)',
  },
  // Light peach skin, golden-brown long hair
  {
    ring: '#ea580c',
    skin: '#FDDBB4',
    hairColor: '#b5813d',
    hair: 'long',
    eyeShade: 'rgba(0,0,0,0.65)',
  },
  // Medium brown skin, dark braids
  {
    ring: '#7c3aed',
    skin: '#8D5524',
    hairColor: '#3b1f0e',
    hair: 'braids',
    eyeShade: 'rgba(0,0,0,0.65)',
  },
  // Golden-tan skin, teal hijab
  {
    ring: '#059669',
    skin: '#C68642',
    hairColor: '#0f766e',
    hair: 'hijab',
    eyeShade: 'rgba(0,0,0,0.65)',
  },
  // Deep brown skin, short natural hair
  {
    ring: '#dc2626',
    skin: '#3b1f0e',
    hairColor: '#1a0a00',
    hair: 'short',
    eyeShade: 'rgba(255,220,160,0.9)',
  },
  // Light olive skin, short dark hair
  {
    ring: '#d97706',
    skin: '#E8C99A',
    hairColor: '#1a1a1a',
    hair: 'shortstraight',
    eyeShade: 'rgba(0,0,0,0.65)',
  },
];

function hairPath(style, hairColor) {
  switch (style) {
    case 'afro':
      return <ellipse cx="25" cy="19" rx="17" ry="15" fill={hairColor} />;
    case 'long':
      // Long hair: tall rounded rectangle behind face, curves out at bottom
      return (
        <>
          <rect x="9" y="11" width="32" height="35" rx="16" fill={hairColor} />
        </>
      );
    case 'braids':
      return (
        <>
          <ellipse cx="25" cy="19" rx="14" ry="13" fill={hairColor} />
          <rect x="9"  y="26" width="5" height="20" rx="2.5" fill={hairColor} />
          <rect x="36" y="26" width="5" height="20" rx="2.5" fill={hairColor} />
        </>
      );
    case 'hijab':
      // Hijab: large dome covering top and sides of face
      return (
        <path
          d="M 6 28 Q 6 6 25 6 Q 44 6 44 28 Q 44 40 40 46 L 10 46 Q 6 40 6 28 Z"
          fill={hairColor}
        />
      );
    case 'short':
      return <ellipse cx="25" cy="20" rx="14" ry="11" fill={hairColor} />;
    case 'shortstraight':
    default:
      return <rect x="11" y="10" width="28" height="14" rx="14" fill={hairColor} />;
  }
}

function FaceAvatar({ config, size = 52 }) {
  const { ring, skin, hairColor, hair, eyeShade } = config;
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 50 50"
      style={{ borderRadius: '50%', display: 'block', flexShrink: 0 }}
    >
      {/* Colored ring border */}
      <circle cx="25" cy="25" r="24" fill={ring} />
      {/* White inner background */}
      <circle cx="25" cy="25" r="22" fill="white" />

      {/* Hair (drawn behind face) */}
      {hairPath(hair, hairColor)}

      {/* Face */}
      <ellipse cx="25" cy="29" rx="13" ry="14" fill={skin} />

      {/* Eyes */}
      <ellipse cx="20" cy="27" rx="2"   ry="2.2" fill={eyeShade} />
      <ellipse cx="30" cy="27" rx="2"   ry="2.2" fill={eyeShade} />

      {/* Subtle smile */}
      <path
        d="M 20 33 Q 25 37 30 33"
        stroke={eyeShade}
        strokeWidth="1.4"
        fill="none"
        strokeLinecap="round"
      />
    </svg>
  );
}

export default function Header({ fairName, matchCount, config, setConfig }) {
  return (
    <header className="site-header">
      <div className="header-inner">
        {/* Logo */}
        <div className="header-logo">
          <div className="header-logo-mark">FM</div>
          <div>
            <div className="header-brand">FairMatch</div>
            <div className="header-tag">Connecting talent with opportunity</div>
          </div>
        </div>

        {/* Config toggle */}
        <div className="config-panel-wrap">
          <button className="config-toggle" onClick={() => setConfig(c => ({ ...c, open: !c.open }))}>
            ⚙ {config.mode === 'api' ? 'API mode' : 'Demo mode'}
          </button>
          {config.open && <ConfigPanel config={config} setConfig={setConfig} />}
        </div>
      </div>

      {/* Banner row */}
      <div className="header-banner">
        {/* Diverse avatar group */}
        <div className="header-avatars" aria-hidden="true">
          {AVATARS.map((av, i) => (
            <FaceAvatar key={i} config={av} />
          ))}
        </div>

        <div className="header-copy">
          <h1>Your Matched Opportunities</h1>
          <p>Ranked by how well each role fits your skills, location, and goals.</p>
          {fairName && (
            <div className="header-fair-tag">
              📅 {fairName}
              {matchCount != null && ` · ${matchCount} match${matchCount !== 1 ? 'es' : ''}`}
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
