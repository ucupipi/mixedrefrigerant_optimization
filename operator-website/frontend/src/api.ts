// API client service for Operator Decision-Support UI

import type { DemoSnapshot, HistoricalSummary, OptimizeResponse, PredictResponse, ScenarioInput } from './types';

const API_BASE = import.meta.env.VITE_API_URL !== undefined
  ? import.meta.env.VITE_API_URL
  : (typeof window !== 'undefined' && window.location.port === '5173' ? 'http://localhost:3001' : '');


export async function fetchSystemStatus(): Promise<any> {
  const resp = await fetch(`${API_BASE}/api/v1/status`);
  if (!resp.ok) throw new Error(`Status HTTP error ${resp.status}`);
  return resp.json();
}

export async function fetchDemoSnapshot(): Promise<DemoSnapshot> {
  const resp = await fetch(`${API_BASE}/api/v1/demo-snapshot`);
  if (!resp.ok) throw new Error(`Snapshot HTTP error ${resp.status}`);
  return resp.json();
}

export async function fetchHistoricalSummary(): Promise<HistoricalSummary> {
  const resp = await fetch(`${API_BASE}/api/v1/historical-summary`);
  if (!resp.ok) throw new Error(`Historical HTTP error ${resp.status}`);
  return resp.json();
}

export async function predictScenario(scenario: ScenarioInput): Promise<PredictResponse> {
  const resp = await fetch(`${API_BASE}/api/v1/predict`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(scenario),
  });
  if (!resp.ok) {
    const errBody = await resp.text();
    throw new Error(`Prediction API error (${resp.status}): ${errBody}`);
  }
  return resp.json();
}

export async function optimizeForFeed(feedFlowTH: number): Promise<OptimizeResponse> {
  const resp = await fetch(`${API_BASE}/api/v1/optimize`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ feed_flow_t_h: feedFlowTH }),
  });
  if (!resp.ok) {
    const errBody = await resp.text();
    throw new Error(`Optimize API error (${resp.status}): ${errBody}`);
  }
  return resp.json();
}
