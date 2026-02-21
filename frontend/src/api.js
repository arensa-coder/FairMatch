/**
 * FairMatch API client.
 * Uses the Vite dev proxy (/api → localhost:8000) by default.
 * Set baseUrl to a full URL (e.g. https://api.fairmatch.org) to hit a remote server.
 */

export async function fetchMatches({ baseUrl = '', fairId, token }) {
  const url = `${baseUrl}/api/v1/jobs/matches/me/${fairId}/detailed`;
  const resp = await fetch(url, {
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });
  if (!resp.ok) {
    const body = await resp.json().catch(() => ({}));
    throw new Error(body.detail || `HTTP ${resp.status}`);
  }
  return resp.json();
}
