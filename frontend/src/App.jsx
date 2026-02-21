import { useState, useEffect } from 'react';
import './App.css';

import Header from './components/Header.jsx';
import MatchCard from './components/MatchCard.jsx';
import { fetchMatches } from './api.js';
import { MOCK_MATCHES, MOCK_FAIR_NAME, MOCK_FAIR_ID } from './data/mockMatches.js';

const INITIAL_CONFIG = {
  open:    false,
  mode:    'mock',       // 'mock' | 'api'
  baseUrl: '',
  fairId:  MOCK_FAIR_ID,
  token:   '',
};

export default function App() {
  const [config, setConfig]   = useState(INITIAL_CONFIG);
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState(null);

  // Reload whenever mode / connection settings change
  useEffect(() => {
    let cancelled = false;

    async function load() {
      setError(null);

      if (config.mode === 'mock') {
        setMatches(MOCK_MATCHES);
        setLoading(false);
        return;
      }

      // API mode
      if (!config.fairId || !config.token) {
        setError('Enter a Fair ID and Bearer Token in the config panel to load live data.');
        setMatches([]);
        return;
      }

      setLoading(true);
      try {
        const data = await fetchMatches({
          baseUrl: config.baseUrl,
          fairId:  config.fairId,
          token:   config.token,
        });
        if (!cancelled) setMatches(data);
      } catch (err) {
        if (!cancelled) setError(err.message);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    load();
    return () => { cancelled = true; };
  }, [config.mode, config.baseUrl, config.fairId, config.token]);

  const fairName = config.mode === 'mock'
    ? MOCK_FAIR_NAME
    : `Fair ${config.fairId?.slice(0, 8) ?? ''}…`;

  return (
    <div className="app">
      <Header
        fairName={fairName}
        matchCount={matches.length}
        config={config}
        setConfig={setConfig}
      />

      <main className="main-content">
        <div className="section-heading">
          <h2>Your Matches</h2>
          {matches.length > 0 && (
            <span className="count-badge">{matches.length} opportunities</span>
          )}
        </div>

        {loading && (
          <div className="state-box">
            <div className="state-icon">⏳</div>
            <h3>Loading your matches…</h3>
          </div>
        )}

        {error && !loading && (
          <div className="state-box">
            <div className="state-icon">⚠️</div>
            <h3>Could not load matches</h3>
            <p>{error}</p>
          </div>
        )}

        {!loading && !error && matches.length === 0 && (
          <div className="state-box">
            <div className="state-icon">🔍</div>
            <h3>No approved matches yet</h3>
            <p>Your employment coordinator is reviewing matches. Check back soon!</p>
          </div>
        )}

        {!loading && !error && matches.length > 0 && (
          <div className="match-grid">
            {matches.map((m, i) => (
              <MatchCard
                key={m.id}
                match={m}
                style={{ animationDelay: `${i * 60}ms` }}
              />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
