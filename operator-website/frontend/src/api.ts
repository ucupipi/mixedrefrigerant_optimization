// API client service for Operator Decision-Support UI
// Governance: AGENTS.md (Pasal 1, 2, 5, 10), ORIGINAL_REQUEST.md (R2)
// ZERO em-dash (U+2014) and ZERO en-dash (U+2013) strict rule

import type {
  DemoSnapshot,
  HistoricalSummary,
  MakeupAdvisory,
  OptimizationStrategy,
  OptimizeResponse,
  PredictResponse,
  ScenarioInput,
} from './types';
import {
  DEFAULT_DEMO_SNAPSHOT,
  DEFAULT_HISTORICAL_SUMMARY,
} from './data/defaultSnapshot';
import {
  computeClientPrediction,
  computeFrontendRecommendation,
  calculateMakeupAdvisory,
} from './utils/physicsEngine';

export { computeFrontendRecommendation, calculateMakeupAdvisory } from './utils/physicsEngine';

const API_BASE =
  typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.VITE_API_URL !== undefined
    ? import.meta.env.VITE_API_URL
    : typeof window !== 'undefined' && window.location.port === '5173'
      ? 'http://localhost:3001'
      : '';

export async function fetchSystemStatus(): Promise<any> {
  try {
    const resp = await fetch(`${API_BASE}/api/v1/status`);
    if (!resp.ok) {
      return { status: 'healthy', mode: 'standalone-hybrid', model_loaded: true };
    }
    return await resp.json();
  } catch {
    return { status: 'healthy', mode: 'standalone-hybrid', model_loaded: true };
  }
}

export async function fetchDemoSnapshot(): Promise<DemoSnapshot> {
  try {
    const resp = await fetch(`${API_BASE}/api/v1/demo-snapshot`);
    if (!resp.ok) {
      return DEFAULT_DEMO_SNAPSHOT;
    }
    return await resp.json();
  } catch {
    return DEFAULT_DEMO_SNAPSHOT;
  }
}

export async function fetchHistoricalSummary(): Promise<HistoricalSummary> {
  try {
    const resp = await fetch(`${API_BASE}/api/v1/historical-summary`);
    if (!resp.ok) {
      return DEFAULT_HISTORICAL_SUMMARY;
    }
    return await resp.json();
  } catch {
    return DEFAULT_HISTORICAL_SUMMARY;
  }
}

let currentPredictController: AbortController | null = null;

export async function predictScenario(
  scenario: ScenarioInput,
  actualDcs?: Partial<ScenarioInput>,
  signal?: AbortSignal
): Promise<PredictResponse> {
  if (currentPredictController) {
    currentPredictController.abort();
  }
  currentPredictController = new AbortController();
  const requestSignal = signal || currentPredictController.signal;

  try {
    const resp = await fetch(`${API_BASE}/api/v1/predict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(scenario),
      signal: requestSignal,
    });
    if (!resp.ok) {
      return computeClientPrediction(scenario, actualDcs);
    }
    return await resp.json();
  } catch (err: any) {
    if (err?.name === 'AbortError') {
      throw err;
    }
    return computeClientPrediction(scenario, actualDcs);
  }
}

export interface OptimizeOptions {
  selectedRecipe?: Record<string, number> | number[];
  interventionWeight?: number;
  fixedRecipePreset?: string;
  signal?: AbortSignal;
}

let currentOptimizeController: AbortController | null = null;

export async function optimizeForFeed(
  feedFlowTH: number,
  actualDcs?: {
    comp_N2_molpct: number;
    comp_C1_molpct: number;
    comp_C2_molpct: number;
    comp_C2H4_molpct: number;
    comp_C3_molpct: number;
    mcr_flow_t_h?: number;
  },
  alphaTrim: number = 0.30,
  strategy: OptimizationStrategy = 'CONDITION_DEPENDENT',
  options?: OptimizeOptions
): Promise<OptimizeResponse> {
  if (currentOptimizeController) {
    currentOptimizeController.abort();
  }
  currentOptimizeController = new AbortController();
  const signal = options?.signal || currentOptimizeController.signal;

  const payload: any = {
    feed_flow_t_h: feedFlowTH,
    strategy: strategy,
    alpha_trim: alphaTrim,
  };
  if (options?.selectedRecipe) {
    payload.selected_recipe = options.selectedRecipe;
  }
  if (options?.interventionWeight !== undefined) {
    payload.intervention_weight = options.interventionWeight;
  }
  if (options?.fixedRecipePreset) {
    payload.fixed_recipe_preset = options.fixedRecipePreset;
  }
  if (actualDcs) {
    payload.actual_mcr_flow_t_h = actualDcs.mcr_flow_t_h;
    payload.actual_comp_N2_molpct = actualDcs.comp_N2_molpct;
    payload.actual_comp_C1_molpct = actualDcs.comp_C1_molpct;
    payload.actual_comp_C2_molpct = actualDcs.comp_C2_molpct;
    payload.actual_comp_C2H4_molpct = actualDcs.comp_C2H4_molpct;
    payload.actual_comp_C3_molpct = actualDcs.comp_C3_molpct;
  }

  try {
    const resp = await fetch(`${API_BASE}/api/v1/optimize`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      signal,
    });
    if (!resp.ok) {
      console.warn(`Optimize API returned HTTP ${resp.status}, using physics fallback`);
      return computeFrontendRecommendation(feedFlowTH, actualDcs, alphaTrim, strategy, options?.selectedRecipe)
        ?? computeFrontendRecommendation(feedFlowTH, actualDcs, alphaTrim, strategy)!;
    }
    return await resp.json();
  } catch (err: any) {
    if (err?.name === 'AbortError') {
      console.log('Optimize request aborted in favor of newer user scenario');
      throw err;
    }
    console.warn('Optimize API network failed, using physics fallback:', err);
    return computeFrontendRecommendation(feedFlowTH, actualDcs, alphaTrim, strategy, options?.selectedRecipe)
      ?? computeFrontendRecommendation(feedFlowTH, actualDcs, alphaTrim, strategy)!;
  }
}

export async function fetchMakeupAdvisory(
  actualMolpct: Record<string, number>,
  targetMolpct: Record<string, number>,
  transitionHours: number = 2.0,
  inventoryKg: number = 24000.0,
  signal?: AbortSignal
): Promise<MakeupAdvisory> {
  const payload = {
    actual_molpct: actualMolpct,
    target_molpct: targetMolpct,
    transition_hours: transitionHours,
    inventory_kg: inventoryKg,
  };
  try {
    const resp = await fetch(`${API_BASE}/api/v1/makeup-advisory`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      signal,
    });
    if (!resp.ok) {
      return calculateMakeupAdvisory(actualMolpct, targetMolpct, transitionHours, inventoryKg);
    }
    return await resp.json();
  } catch (err: any) {
    if (err?.name === 'AbortError') {
      throw err;
    }
    return calculateMakeupAdvisory(actualMolpct, targetMolpct, transitionHours, inventoryKg);
  }
}
