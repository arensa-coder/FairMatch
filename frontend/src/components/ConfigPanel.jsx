import { useState } from 'react';

/**
 * Slide-out panel that lets testers switch between mock data and a live API.
 *
 * config shape:
 *   { open, mode, baseUrl, fairId, token }
 */
export default function ConfigPanel({ config, setConfig }) {
  const [draft, setDraft] = useState({
    baseUrl: config.baseUrl ?? '',
    fairId:  config.fairId  ?? '',
    token:   config.token   ?? '',
  });

  function applyApi() {
    setConfig(c => ({
      ...c,
      mode:    'api',
      baseUrl: draft.baseUrl.replace(/\/$/, ''),
      fairId:  draft.fairId,
      token:   draft.token,
      open:    false,
    }));
  }

  function applyMock() {
    setConfig(c => ({ ...c, mode: 'mock', open: false }));
  }

  return (
    <div className="config-panel">
      <h3>Data Source</h3>

      <div style={{ marginBottom: 14 }}>
        <span className={`config-mode-tag ${config.mode === 'api' ? 'api' : ''}`}>
          {config.mode === 'api' ? '🟠 Live API' : '🟢 Demo data'}
        </span>
      </div>

      <div className="config-field">
        <label>API Base URL</label>
        <input
          type="url"
          placeholder="http://localhost:8000"
          value={draft.baseUrl}
          onChange={e => setDraft(d => ({ ...d, baseUrl: e.target.value }))}
        />
      </div>

      <div className="config-field">
        <label>Fair ID (UUID)</label>
        <input
          type="text"
          placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
          value={draft.fairId}
          onChange={e => setDraft(d => ({ ...d, fairId: e.target.value }))}
        />
      </div>

      <div className="config-field">
        <label>Bearer Token (Supabase JWT)</label>
        <input
          type="password"
          placeholder="eyJhbGciOiJS..."
          value={draft.token}
          onChange={e => setDraft(d => ({ ...d, token: e.target.value }))}
        />
      </div>

      <div className="config-actions">
        <button className="btn-secondary" onClick={applyMock}>
          Use Demo Data
        </button>
        <button className="btn-primary" onClick={applyApi}>
          Connect API →
        </button>
      </div>
    </div>
  );
}
