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

function createTimedController(timeoutMs: number, externalSignal?: AbortSignal): {
  controller: AbortController;
  cleanup: () => void;
  isTimedOut: () => boolean;
} {
  const controller = new AbortController();
  let timedOut = false;
  const timer = setTimeout(() => {
    timedOut = true;
    controller.abort();
  }, timeoutMs);

  const onExternalAbort = () => controller.abort();
  if (externalSignal) {
    if (externalSignal.aborted) {
      clearTimeout(timer);
      controller.abort();
    } else {
      externalSignal.addEventListener('abort', onExternalAbort, { once: true });
    }
  }

  return {
    controller,
    cleanup: () => {
      clearTimeout(timer);
      if (externalSignal) {
        externalSignal.removeEventListener('abort', onExternalAbort);
      }
    },
    isTimedOut: () => timedOut,
  };
}

export async function fetchSystemStatus(): Promise<any> {
  const { controller, cleanup } = createTimedController(2500);
  try {
    const resp = await fetch(`${API_BASE}/api/v1/status`, { signal: controller.signal });
    if (!resp.ok) {
      return { status: 'healthy', mode: 'standalone-hybrid', model_loaded: true };
    }
    return await resp.json();
  } catch {
    return { status: 'healthy', mode: 'standalone-hybrid', model_loaded: true };
  } finally {
    cleanup();
  }
}

export async function fetchDemoSnapshot(): Promise<DemoSnapshot> {
  const { controller, cleanup } = createTimedController(2500);
  try {
    const resp = await fetch(`${API_BASE}/api/v1/demo-snapshot`, { signal: controller.signal });
    if (!resp.ok) {
      return DEFAULT_DEMO_SNAPSHOT;
    }
    return await resp.json();
  } catch {
    return DEFAULT_DEMO_SNAPSHOT;
  } finally {
    cleanup();
  }
}

export async function fetchHistoricalSummary(): Promise<HistoricalSummary> {
  const { controller, cleanup } = createTimedController(2500);
  try {
    const resp = await fetch(`${API_BASE}/api/v1/historical-summary`, { signal: controller.signal });
    if (!resp.ok) {
      return DEFAULT_HISTORICAL_SUMMARY;
    }
    return await resp.json();
  } catch {
    return DEFAULT_HISTORICAL_SUMMARY;
  } finally {
    cleanup();
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
  const callerController = new AbortController();
  currentPredictController = callerController;
  const effectiveExternal = signal || callerController.signal;
  const { controller, cleanup, isTimedOut } = createTimedController(4000, effectiveExternal);

  try {
    const resp = await fetch(`${API_BASE}/api/v1/predict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(scenario),
      signal: controller.signal,
    });
    if (!resp.ok) {
      return computeClientPrediction(scenario, actualDcs);
    }
    return await resp.json();
  } catch (err: any) {
    if (err?.name === 'AbortError' && !isTimedOut()) {
      throw err;
    }
    return computeClientPrediction(scenario, actualDcs);
  } finally {
    cleanup();
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
  const callerController = new AbortController();
  currentOptimizeController = callerController;
  const effectiveExternal = options?.signal || callerController.signal;
  const { controller, cleanup, isTimedOut } = createTimedController(4000, effectiveExternal);

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
      signal: controller.signal,
    });
    if (!resp.ok) {
      console.warn(`Optimize API returned HTTP ${resp.status}, using physics fallback`);
      return computeFrontendRecommendation(feedFlowTH, actualDcs, alphaTrim, strategy, options?.selectedRecipe)
        ?? computeFrontendRecommendation(feedFlowTH, actualDcs, alphaTrim, strategy)!;
    }
    return await resp.json();
  } catch (err: any) {
    if (err?.name === 'AbortError' && !isTimedOut()) {
      console.log('Optimize request aborted in favor of newer user scenario');
      throw err;
    }
    console.warn('Optimize API network failed or timed out, using physics fallback:', err);
    return computeFrontendRecommendation(feedFlowTH, actualDcs, alphaTrim, strategy, options?.selectedRecipe)
      ?? computeFrontendRecommendation(feedFlowTH, actualDcs, alphaTrim, strategy)!;
  } finally {
    cleanup();
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
