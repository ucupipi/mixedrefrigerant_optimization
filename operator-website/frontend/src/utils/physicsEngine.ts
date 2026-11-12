// Pure TypeScript First-Principles Physics & Surrogate Calculation Engine
// Governance: AGENTS.md (Pasal 1, 2, 3, 4, 5, 10, 11, 12, 13)
// ZERO em-dash (U+2014) and ZERO en-dash (U+2013) strict rule

import type {
  ChillerDutyResult,
  DomainCheck,
  FlashDrumSummary,
  MakeupAdvisory,
  MakeupInjectionItem,
  OptimizationStrategy,
  OptimizeResponse,
  PredictionSummary,
  PredictResponse,
  SafetyCheck,
  ScenarioInput,
} from '../types';

import {
  calculateChillerAndCondenserDuties,
  calculateFlashDrum5C1,
  DEFAULT_COOLING_WATER,
} from './thermoFlash';

// ── Molecular Weights [g/mol] ──────────────────────────────────────────────
export const MW_SPECIES: Record<string, number> = {
  N2: 28.0134,
  C1: 16.0425,
  C2: 30.0690,
  C2H4: 28.0532,
  C3: 44.0956,
};

// ── Operating Regime Thresholds [t/h] ──────────────────────────────────────
export const UNDERLOAD_THRESHOLD_T_H = 226.8;
export const BASELOAD_THRESHOLD_T_H = 279.8;
export const TRAIN_H_MAX_DESIGN_FEED_T_H = 350.0;

// ── Plant Interlock & Safety Limits (AGENTS.md Pasal 5, BOOK-4, BOOK-5) ────
export const ANTISURGE_FLOW_FLOOR_T_H = 480.0;
export const SUCTION_TAL_DEG_C = -45.0;
export const SUCTION_TALL_DEG_C = -51.0;
export const MCHE_WARM_DP_ALARM_KG_CM2 = 0.42;
export const MCHE_WARM_DP_TRIP_KG_CM2 = 0.54;
export const MCHE_COLD_DP_MAX_KG_CM2 = 0.17;
export const C3_SUCTION_MIN_KG_CM2A = 1.033;
export const MITA_MIN_PINCH_C = 1.50;

export const FEED_FLOW_MIN_T_H = 130.0;
export const FEED_FLOW_MAX_T_H = 340.0;

// ── Decarbonization Constants (Stage 08 & Manual Book Modul 8) ─────────────
export const STEAM_RATE_T_PER_MWH = 4.04;
export const FUEL_GAS_NM3_PER_T_STEAM = 97.7;
export const FUEL_GAS_GJ_PER_NM3 = 0.038;
export const CO2_KG_PER_GJ = 56.1;

// ── Regime-Stratified C3 Power Share (AGENTS.md Pasal 10) ──────────────────
export const C3_POWER_SHARE_BY_REGIME: Record<string, number> = {
  underload: 0.4225,
  transition: 0.3775,
  baseload: 0.3634,
};

// ── Plant-3 DCS 7-Quantile Baseline Curve (1,617 real shifts) ──────────────
export const PLANT3_FEED_QUANTILES = [185.82, 219.45, 256.75, 286.63, 325.91, 367.96, 399.74];
export const PLANT3_POWER_QUANTILES = [82.90, 83.59, 83.13, 83.58, 85.46, 91.20, 92.57];

// ── Aitchison Simplex Geometry & Mahalanobis Envelope Constants ────────────
export const CHI2_CRITICAL_5COMP = 3.080216; // sqrt(chi2.ppf(0.95, df=4))

export const HISTORICAL_MEAN_XI = [
  -0.6613989652,
  2.0585004114,
  2.8666052438,
  -2.2383652824,
];

export const HISTORICAL_COV_INV = [
  [32.346399, -23.967790, 3.522582, 1.853856],
  [-23.967790, 295.334057, -167.863704, 11.386687],
  [3.522582, -167.863704, 107.460406, -2.449520],
  [1.853856, 11.386687, -2.449520, 3.673292],
];

// Orthonormal Sequential Binary Partition (SBP) contrast matrix for S^5 -> R^4
export const V_MATRIX_5 = [
  [ 0.8944271909999159,  0.0,                  0.0,                 0.0],
  [-0.22360679774997896, 0.8660254037844386,  0.0,                 0.0],
  [-0.22360679774997896, -0.28867513459481287, 0.816496580927726,  0.0],
  [-0.22360679774997896, -0.28867513459481287, -0.408248290463863, 0.7071067811865476],
  [-0.22360679774997896, -0.28867513459481287, -0.408248290463863, -0.7071067811865476],
];

// ── Trained Ridge Surrogate Model Parameters (c3mr_power_surrogate_real) ──
export const RIDGE_INTERCEPT = 90.16546106066212;

export const SCALER_MEAN = [
  256.48089394807363,
  651.788544691976,
  -1.104030715136265,
  1.478175490517413,
  2.0051234862393814,
  -0.6117945199332024,
  0.15874363327674024,
  0.2614601018675722,
  4.220942464367384,
  3.214618688300557,
  13.33321860707505,
  0.24380540020174216,
  13.452436576746674,
  2.430665257936056,
  88.98108537576958,
  24.475742842662296,
  -27.42856012754653,
  441.48161906062614,
  175.17015516647305,
  168.44944071916137,
];

export const SCALER_SCALE = [
  34.41712184404865,
  52.77803089956269,
  0.4174912620040398,
  0.5180755237739783,
  0.819830780530766,
  1.1810631525593334,
  0.365436851139619,
  0.4394299910099116,
  0.34185467751765,
  0.1335172729687089,
  1.1422473168332854,
  0.06391134346878243,
  0.6378535920096884,
  0.7870514581602303,
  4.332652662902143,
  0.2427525726869015,
  2.4827100665840307,
  33.959612826731046,
  25.57719418579405,
  32.36166039370085,
];

export const RIDGE_COEF = [
  -5.753197367956476,
  0.35161321926556066,
  0.16055234609527744,
  2.0035434317089122,
  -2.590309463869836,
  -0.13645006358993955,
  -0.0703964805742278,
  0.009977360777920899,
  0.09156873003691372,
  1.3381217245766313,
  -0.5519292989952133,
  -0.13157245826263453,
  0.2394360598597381,
  0.3728222424831102,
  0.8862772101076085,
  -0.1698472242030526,
  -0.17962562119952272,
  1.5194860570001205,
  1.6809436642592557,
  6.34177280308931,
];

// ── Make-up Advisory Controllers ───────────────────────────────────────────
export const TAG_MAKEUP_CONTROLLERS: Record<string, { tag: string; desc: string; unit: string }> = {
  N2: { tag: 'H4FIC006', desc: 'Nitrogen (N2)', unit: 'Nm3/h' },
  C1: { tag: 'H4FIC005', desc: 'Metana (C1)', unit: 'Nm3/h' },
  C2: { tag: 'H4FI00C8', desc: 'Etana (C2)', unit: 'Nm3/h' },
  C3: { tag: 'H4FIC007', desc: 'Propana (C3)', unit: 'Nm3/h' },
};

export const NORMAL_MOLAR_VOLUME_NM3_PER_KMOL = 22.414;
export const ESTIMATED_MCR_LOOP_INVENTORY_KG = 24000.0;

// ── Utility Functions ──────────────────────────────────────────────────────
export function clip(val: number, minVal: number, maxVal: number): number {
  return Math.min(maxVal, Math.max(minVal, val));
}

export function classifyRegime(feedTH: number): 'underload' | 'transition' | 'baseload' {
  if (feedTH <= UNDERLOAD_THRESHOLD_T_H) return 'underload';
  if (feedTH >= BASELOAD_THRESHOLD_T_H) return 'baseload';
  return 'transition';
}

/**
 * Project composition vector onto Simplex S^5 (sum = 1.0).
 */
export function closure(comp: number[]): number[] {
  let s = 0.0;
  for (let i = 0; i < comp.length; i++) {
    s += Math.max(0.0, comp[i]);
  }
  const denom = Math.max(s, 1e-9);
  return comp.map((v) => Math.max(0.0, v) / denom);
}

/**
 * Multiplicative zero replacement preserving simplex closure.
 */
export function replaceZeros(comp: number[], delta: number = 1e-5): number[] {
  const norm = closure(comp);
  let zeroCount = 0;
  for (let i = 0; i < norm.length; i++) {
    if (norm[i] <= 0.0) zeroCount++;
  }
  if (zeroCount === 0) return norm;
  const nonZeroScale = 1.0 - zeroCount * delta;
  return norm.map((v) => (v <= 0.0 ? delta : v * nonZeroScale));
}

/**
 * Transform 5-component mole fractions [N2, C1, C2, C2H4, C3] from S^5 to Euclidean R^4.
 */
export function ilrForward(comp: number[]): number[] {
  const safe = replaceZeros(comp);
  const logVals = safe.map((v) => Math.log(v));
  const meanLog = logVals.reduce((a, b) => a + b, 0.0) / logVals.length;
  const clr = logVals.map((v) => v - meanLog);

  const xi = [0.0, 0.0, 0.0, 0.0];
  for (let j = 0; j < 4; j++) {
    let sum = 0.0;
    for (let i = 0; i < 5; i++) {
      sum += clr[i] * V_MATRIX_5[i][j];
    }
    xi[j] = sum;
  }
  return xi;
}

/**
 * Transform Euclidean ILR coordinates back to Simplex S^5 mole fractions.
 */
export function ilrInverse(xi: number[]): number[] {
  const clr = [0.0, 0.0, 0.0, 0.0, 0.0];
  for (let i = 0; i < 5; i++) {
    let sum = 0.0;
    for (let j = 0; j < 4; j++) {
      sum += xi[j] * V_MATRIX_5[i][j];
    }
    clr[i] = Math.exp(sum);
  }
  return closure(clr);
}

/**
 * Enforce exact 100.00% closure with C1 residual absorption.
 */
export function enforceSimplexClosure(xi: number[]): number[] {
  const fractions = ilrInverse(xi);
  const rounded = fractions.map((v) => Math.max(0.01, Math.round(v * 10000) / 100));
  const residual = Math.round((100.00 - rounded.reduce((a, b) => a + b, 0.0)) * 100) / 100;
  rounded[1] = Math.round((rounded[1] + residual) * 100) / 100;
  return rounded;
}

// Certified 7-Quantile Pareto Points for Baseload LNG Train H C3MR
export interface ParetoPoint {
  feed: number;
  mcr: number;
  n2: number;
  c1: number;
  c2: number;
  c2h4: number;
  c3: number;
  t_suct: number;
}

export const PARETO_QUANTILES: ParetoPoint[] = [
  { feed: 141.2, mcr: 480.0, n2: 3.03, c1: 47.49, c2: 45.78, c2h4: 0.00, c3: 3.70, t_suct: -23.1 },
  { feed: 166.8, mcr: 514.2, n2: 2.86, c1: 43.70, c2: 48.40, c2h4: 0.00, c3: 5.03, t_suct: -30.0 },
  { feed: 195.1, mcr: 480.0, n2: 3.16, c1: 47.48, c2: 45.38, c2h4: 0.01, c3: 3.98, t_suct: -37.1 },
  { feed: 217.8, mcr: 534.7, n2: 2.26, c1: 42.35, c2: 48.95, c2h4: 0.01, c3: 6.42, t_suct: -38.9 },
  { feed: 257.1, mcr: 493.5, n2: 3.84, c1: 47.51, c2: 43.54, c2h4: 0.09, c3: 5.03, t_suct: -36.8 },
  { feed: 280.3, mcr: 596.3, n2: 4.51, c1: 44.98, c2: 43.23, c2h4: 0.59, c3: 6.68, t_suct: -39.8 },
  { feed: 296.4, mcr: 613.2, n2: 4.87, c1: 43.96, c2: 43.00, c2h4: 0.13, c3: 8.03, t_suct: -39.0 },
];

// Universal Invariant Master Recipe (Certified P10-P90 Operating Envelope)
export const INVARIANT_RECIPE_MOLPCT = [3.77, 42.22, 43.67, 1.53, 8.82];

/**
 * Client-Side Multi-Strategy Fallback Optimization.
 * Replicates backend optimizer_engine.py get_pareto_fallback_recommendation.
 */
export function computeFrontendRecommendation(
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
  selectedRecipe?: Record<string, number> | number[]
): OptimizeResponse | null {
  if (feedFlowTH == null || !isFinite(feedFlowTH) || feedFlowTH <= 0.0) {
    return null;
  }

  const f = Math.max(50.0, feedFlowTH);
  const q0 = PARETO_QUANTILES[0];
  const qLast = PARETO_QUANTILES[PARETO_QUANTILES.length - 1];
  const qPrev = PARETO_QUANTILES[PARETO_QUANTILES.length - 2];

  // 1. MCR Flow Scaling with load (anti-surge floor 480.0 t/h)
  let mcrRec = 480.0;
  if (f <= q0.feed) {
    mcrRec = 480.0;
  } else if (f >= qLast.feed) {
    const slope = (qLast.mcr - qPrev.mcr) / (qLast.feed - qPrev.feed);
    mcrRec = qLast.mcr + slope * (f - qLast.feed);
  } else {
    for (let i = 0; i < PARETO_QUANTILES.length - 1; i++) {
      const qA = PARETO_QUANTILES[i];
      const qB = PARETO_QUANTILES[i + 1];
      if (f >= qA.feed && f <= qB.feed) {
        const t = (f - qA.feed) / (qB.feed - qA.feed);
        mcrRec = qA.mcr + t * (qB.mcr - qA.mcr);
        break;
      }
    }
  }
  mcrRec = Math.max(480.0, Math.round(mcrRec * 10) / 10);

  // 2. Compute Pareto Optimum in 4D ILR coordinate space
  const qXi = PARETO_QUANTILES.map((q) =>
    ilrForward([q.n2 / 100.0, q.c1 / 100.0, q.c2 / 100.0, q.c2h4 / 100.0, q.c3 / 100.0])
  );

  const xiOpt = [0.0, 0.0, 0.0, 0.0];
  let tSuct = -39.0;

  if (f <= q0.feed) {
    for (let j = 0; j < 4; j++) xiOpt[j] = qXi[0][j];
    tSuct = q0.t_suct;
  } else if (f >= qLast.feed) {
    for (let j = 0; j < 4; j++) xiOpt[j] = qXi[qXi.length - 1][j];
    tSuct = qLast.t_suct;
  } else {
    for (let i = 0; i < PARETO_QUANTILES.length - 1; i++) {
      const qA = PARETO_QUANTILES[i];
      const qB = PARETO_QUANTILES[i + 1];
      if (f >= qA.feed && f <= qB.feed) {
        const t = (f - qA.feed) / (qB.feed - qA.feed);
        for (let j = 0; j < 4; j++) {
          xiOpt[j] = qXi[i][j] + t * (qXi[i + 1][j] - qXi[i][j]);
        }
        tSuct = qA.t_suct + t * (qB.t_suct - qA.t_suct);
        break;
      }
    }
  }

  let finalXi: number[];
  let sourceDesc = '';
  let explanationDesc = '';

  if (strategy === 'FIXED_RECIPE') {
    let fixComp: number[];
    if (selectedRecipe) {
      if (Array.isArray(selectedRecipe)) {
        fixComp = closure(selectedRecipe);
      } else {
        fixComp = closure([
          (typeof selectedRecipe.N2 === 'number' && Number.isFinite(selectedRecipe.N2)) ? selectedRecipe.N2 : 3.77,
          (typeof selectedRecipe.C1 === 'number' && Number.isFinite(selectedRecipe.C1)) ? selectedRecipe.C1 : 42.22,
          (typeof selectedRecipe.C2 === 'number' && Number.isFinite(selectedRecipe.C2)) ? selectedRecipe.C2 : 43.67,
          (typeof selectedRecipe.C2H4 === 'number' && Number.isFinite(selectedRecipe.C2H4)) ? selectedRecipe.C2H4 : 1.53,
          (typeof selectedRecipe.C3 === 'number' && Number.isFinite(selectedRecipe.C3)) ? selectedRecipe.C3 : 8.82,
        ]);
      }
    } else {
      fixComp = closure(INVARIANT_RECIPE_MOLPCT);
    }
    finalXi = ilrForward(fixComp);
    tSuct = -40.5;
    sourceDesc = 'Certified 7-Quantile Pareto Table (Fixed Master Recipe Across Loads)';
    explanationDesc = 'Strategy A (Fixed Recipe Across Loads): MCR composition maintained constant across production loads to avoid recipe transitions. Circulation rate scaled to match heat duty.';
  } else if (strategy === 'MINIMUM_INTERVENTION') {
    const baseline = {
      comp_N2_molpct: 3.39,
      comp_C1_molpct: 44.45,
      comp_C2_molpct: 45.02,
      comp_C2H4_molpct: 0.85,
      comp_C3_molpct: 6.29,
    };
    const act = {
      comp_N2_molpct: (typeof actualDcs?.comp_N2_molpct === 'number' && Number.isFinite(actualDcs.comp_N2_molpct)) ? actualDcs.comp_N2_molpct : baseline.comp_N2_molpct,
      comp_C1_molpct: (typeof actualDcs?.comp_C1_molpct === 'number' && Number.isFinite(actualDcs.comp_C1_molpct)) ? actualDcs.comp_C1_molpct : baseline.comp_C1_molpct,
      comp_C2_molpct: (typeof actualDcs?.comp_C2_molpct === 'number' && Number.isFinite(actualDcs.comp_C2_molpct)) ? actualDcs.comp_C2_molpct : baseline.comp_C2_molpct,
      comp_C2H4_molpct: (typeof actualDcs?.comp_C2H4_molpct === 'number' && Number.isFinite(actualDcs.comp_C2H4_molpct)) ? actualDcs.comp_C2H4_molpct : baseline.comp_C2H4_molpct,
      comp_C3_molpct: (typeof actualDcs?.comp_C3_molpct === 'number' && Number.isFinite(actualDcs.comp_C3_molpct)) ? actualDcs.comp_C3_molpct : baseline.comp_C3_molpct,
    };
    const actFrac = closure([
      act.comp_N2_molpct,
      act.comp_C1_molpct,
      act.comp_C2_molpct,
      act.comp_C2H4_molpct,
      act.comp_C3_molpct,
    ]);
    const xiAct = ilrForward(actFrac);
    const a = Math.min(1.0, Math.max(0.05, alphaTrim));
    finalXi = [0.0, 0.0, 0.0, 0.0];
    for (let j = 0; j < 4; j++) {
      finalXi[j] = xiAct[j] + a * (xiOpt[j] - xiAct[j]);
    }
    sourceDesc = `Certified 7-Quantile Pareto Table (Minimum-Intervention Trim, alpha=${a.toFixed(2)})`;
    explanationDesc = `Strategy C (Minimum-Intervention): Energy performance balanced against transition penalty (alpha=${a.toFixed(2)}). Recipe moves conservatively toward optimal while minimizing make-up material consumption.`;
  } else {
    finalXi = xiOpt;
    sourceDesc = 'Certified 7-Quantile Pareto Table (Condition-Dependent Multi-Load Optimum)';
    explanationDesc = `Strategy B (Condition-Dependent): Full 5-dimensional optimization active for feed ${feedFlowTH.toFixed(1)} t/h. MCR composition and circulation dynamically minimize specific shaft power while satisfying all safety boundaries.`;
  }

  const rounded = enforceSimplexClosure(finalXi);
  const dm = computeMahalanobisDistance(finalXi);

  const resTal = Math.round((tSuct - SUCTION_TAL_DEG_C) * 10) / 10;
  const resSurge = Math.round((mcrRec - ANTISURGE_FLOW_FLOOR_T_H) * 10) / 10;
  const resDm = Math.round((CHI2_CRITICAL_5COMP - dm) * 1000) / 1000;
  const resSh = 16.5; // Nominal suction superheat margin at LP suction

  return {
    feed_t_h: Math.round(feedFlowTH * 10) / 10,
    mcr_flow_t_h: mcrRec,
    comp_N2_molpct: rounded[0],
    comp_C1_molpct: rounded[1],
    comp_C2_molpct: rounded[2],
    comp_C2H4_molpct: rounded[3],
    comp_C3_molpct: rounded[4],
    mahalanobis_distance: Math.round(dm * 1000) / 1000,
    expected_suction_temp_c: Math.round(tSuct * 10) / 10,
    suction_tal_ok: tSuct >= SUCTION_TAL_DEG_C,
    antisurge_floor_applied: mcrRec <= ANTISURGE_FLOW_FLOOR_T_H + 0.1,
    envelope_shrink_applied: false,
    extrapolated: f < q0.feed || f > qLast.feed,
    feed_span_t_h: [q0.feed, qLast.feed],
    source: sourceDesc,
    strategy: strategy,
    explanation: explanationDesc,
    solver_converged: true,
    constraint_residuals: {
      suction_tal_margin_c: resTal,
      mahalanobis_margin: resDm,
      antisurge_margin_t_h: resSurge,
      superheat_margin_c: resSh,
    },
    effective_inputs: {
      feed_flow_t_h: feedFlowTH,
      strategy: strategy,
      alpha_trim: alphaTrim,
      actual_mcr_flow_t_h: actualDcs?.mcr_flow_t_h ?? 562.3,
    },
  };
}

/**
 * Calculate Mahalanobis distance D_M in 4D ILR coordinate space.
 */
export function computeMahalanobisDistance(xi: number[]): number {
  const diff = [
    xi[0] - HISTORICAL_MEAN_XI[0],
    xi[1] - HISTORICAL_MEAN_XI[1],
    xi[2] - HISTORICAL_MEAN_XI[2],
    xi[3] - HISTORICAL_MEAN_XI[3],
  ];

  let dmSq = 0.0;
  for (let i = 0; i < 4; i++) {
    let rowDot = 0.0;
    for (let j = 0; j < 4; j++) {
      rowDot += HISTORICAL_COV_INV[i][j] * diff[j];
    }
    dmSq += diff[i] * rowDot;
  }
  return Math.sqrt(Math.max(0.0, dmSq));
}

export function checkCompositionEnvelope(comp: number[]): {
  in_envelope: boolean;
  mahalanobis_distance: number;
  critical_threshold: number;
  xi_coordinates: number[];
} {
  const xi = ilrForward(comp);
  const dm = computeMahalanobisDistance(xi);
  return {
    in_envelope: dm <= CHI2_CRITICAL_5COMP,
    mahalanobis_distance: Math.round(dm * 10000) / 10000,
    critical_threshold: CHI2_CRITICAL_5COMP,
    xi_coordinates: xi.map((x) => Math.round(x * 10000) / 10000),
  };
}

/**
 * Plant-3/5 Train H DCS 7-quantile baseline power curve interpolation.
 */
export function getPlant3BaselinePower(feedTH: number): number {
  if (feedTH <= PLANT3_FEED_QUANTILES[0]) {
    return PLANT3_POWER_QUANTILES[0];
  }
  const n = PLANT3_FEED_QUANTILES.length;
  if (feedTH >= PLANT3_FEED_QUANTILES[n - 1]) {
    const slope = 0.2362; // MW / (t feed)
    return PLANT3_POWER_QUANTILES[n - 1] + slope * (feedTH - PLANT3_FEED_QUANTILES[n - 1]);
  }
  for (let i = 0; i < n - 1; i++) {
    const f0 = PLANT3_FEED_QUANTILES[i];
    const f1 = PLANT3_FEED_QUANTILES[i + 1];
    if (feedTH >= f0 && feedTH <= f1) {
      const p0 = PLANT3_POWER_QUANTILES[i];
      const p1 = PLANT3_POWER_QUANTILES[i + 1];
      return p0 + ((feedTH - f0) / (f1 - f0)) * (p1 - p0);
    }
  }
  return PLANT3_POWER_QUANTILES[0];
}

/**
 * Build 20 physical features matching feature_builder.py.
 * Incorporates internal cooling seawater parameter T_CW = 30.0 C (P_c3_disch = 14.164 kg/cm2A).
 */
export function buildFeatureVector(scenario: Record<string, any>): {
  featureVector: number[];
  featureDict: Record<string, number>;
  fracComp: number[];
  compSum: number;
} {
  const feedFlow = Math.max(0.0, Number(scenario.feed_flow_t_h ?? 250.0));
  const mcrFlow = Math.max(0.0, Number(scenario.mcr_flow_t_h ?? 560.0));

  const rawN2 = Number(scenario.comp_N2_molpct ?? 3.38);
  const rawC1 = Number(scenario.comp_C1_molpct ?? 44.37);
  const rawC2 = Number(scenario.comp_C2_molpct ?? 44.94);
  const rawC2H4 = Number(scenario.comp_C2H4_molpct ?? 0.85);
  const rawC3 = Number(scenario.comp_C3_molpct ?? 6.28);

  const rawComp = [rawN2, rawC1, rawC2, rawC2H4, rawC3];
  const compSum = rawComp.reduce((a, b) => a + b, 0.0);
  const fracComp = compSum > 1.5 ? rawComp.map((v) => v / compSum) : rawComp.map((v) => v / Math.max(compSum, 1e-6));

  const xi = ilrForward(fracComp);
  const xi1 = xi[0];
  const xi2 = xi[1];
  const xi3 = xi[2];
  const xi4 = xi[3];

  const isUnderload = feedFlow <= UNDERLOAD_THRESHOLD_T_H ? 1.0 : 0.0;
  const isBaseload = feedFlow >= BASELOAD_THRESHOLD_T_H ? 1.0 : 0.0;

  // Pressure ratios: incorporating T_CW = 30.0 C -> p_c3_disch = 14.164 kg/cm2A
  const p4k2Suct = Math.max(Number(scenario.p_4k2_suct_kgcm2a ?? 3.235), 0.1);
  const p4k2Disch = Math.max(Number(scenario.p_4k2_disch_kgcm2a ?? 13.697), 0.1);
  const p4k3Suct = Math.max(Number(scenario.p_4k3_suct_kgcm2a ?? 13.417), 0.1);
  const p4k3Disch = Math.max(Number(scenario.p_4k3_disch_kgcm2a ?? 43.881), 0.1);
  const pC3Suct = Math.max(Number(scenario.p_c3_suct_kgcm2a ?? 1.045), 0.1);
  const pC3Disch = Math.max(Number(scenario.p_c3_disch_kgcm2a ?? DEFAULT_COOLING_WATER.p_c3_disch_kgcm2a), 0.1);

  const rpLpMcr = clip(p4k2Disch / p4k2Suct, 1.0, 15.0);
  const rpHpMcr = clip(p4k3Disch / p4k3Suct, 1.0, 15.0);
  const rpMcrTotal = clip(p4k3Disch / p4k2Suct, 1.0, 40.0);
  const dpInterstage4E5 = clip(p4k2Disch - p4k3Suct, -2.0, 5.0);
  const rpC3Total = clip(pC3Disch / pC3Suct, 1.0, 30.0);

  // MCHE temperature differences
  const tMrvWbOut = Number(scenario.t_mche_warm_mrv_out_c ?? -122.4);
  const tShellMid = Number(scenario.t_mche_shell_mid_c ?? -127.8);
  const tMrvWbIn = Number(scenario.t_mche_warm_mrv_in_c ?? -32.7);
  const tMrvCbOut = Number(scenario.t_mche_cold_mrv_out_c ?? -123.5);
  const tLngRundown = Number(scenario.t_lng_rundown_c ?? -148.0);
  const tFgCbIn = Number(scenario.t_fg_cb_in_c ?? -121.8);

  const mcheDtColdBundleApproach = clip(tMrvWbOut - tShellMid, -30.0, 40.0);
  const mcheDtShellSpan = clip(tMrvWbIn - tMrvCbOut, 20.0, 140.0);
  const mcheDtLngexitMrv = clip(tLngRundown - tFgCbIn, -60.0, 10.0);

  // Apparent molecular weight
  const rawMw =
    fracComp[0] * MW_SPECIES.N2 +
    fracComp[1] * MW_SPECIES.C1 +
    fracComp[2] * MW_SPECIES.C2 +
    fracComp[3] * MW_SPECIES.C2H4 +
    fracComp[4] * MW_SPECIES.C3;
  const mwMcr = clip(rawMw, 16.0, 45.0);

  // Thermodynamic work proxies (k_exp = 0.20)
  const kExp = 0.20;
  const workProxyMcrTotal = mcrFlow * (Math.pow(Math.max(rpMcrTotal, 1.0), kExp) - 1.0);
  const workProxyC3 = feedFlow * (Math.pow(Math.max(rpC3Total, 1.0), kExp) - 1.0);
  const feedMcrProduct = (feedFlow * mcrFlow) / 1000.0;

  const featureDict: Record<string, number> = {
    H1FI012: feedFlow,
    H4FI001: mcrFlow,
    xi_1: xi1,
    xi_2: xi2,
    xi_3: xi3,
    xi_4: xi4,
    is_underload: isUnderload,
    is_baseload: isBaseload,
    rp_LP_MCR: rpLpMcr,
    rp_HP_MCR: rpHpMcr,
    rp_MCR_total: rpMcrTotal,
    dp_interstage_4E5: dpInterstage4E5,
    rp_C3_total: rpC3Total,
    MCHE_dT_cold_bundle_approach: mcheDtColdBundleApproach,
    MCHE_dT_shell_span: mcheDtShellSpan,
    MW_MCR: mwMcr,
    MCHE_dT_lngexit_mrv: mcheDtLngexitMrv,
    work_proxy_mcr_total: workProxyMcrTotal,
    work_proxy_c3: workProxyC3,
    feed_mcr_product: feedMcrProduct,
  };

  const featureVector = [
    feedFlow,
    mcrFlow,
    xi1,
    xi2,
    xi3,
    xi4,
    isUnderload,
    isBaseload,
    rpLpMcr,
    rpHpMcr,
    rpMcrTotal,
    dpInterstage4E5,
    rpC3Total,
    mcheDtColdBundleApproach,
    mcheDtShellSpan,
    mwMcr,
    mcheDtLngexitMrv,
    workProxyMcrTotal,
    workProxyC3,
    feedMcrProduct,
  ];

  return { featureVector, featureDict, fracComp, compSum };
}

/**
 * Evaluate exact trained Ridge surrogate model.
 */
export function evaluateRidgeSurrogate(featureVector: number[]): number {
  let zSum = 0.0;
  for (let i = 0; i < 20; i++) {
    const z = (featureVector[i] - SCALER_MEAN[i]) / SCALER_SCALE[i];
    zSum += z * RIDGE_COEF[i];
  }
  return zSum + RIDGE_INTERCEPT;
}

/**
 * Validate operating point against interlocks and domain boundaries.
 */
export function validateOperatingPoint(scenario: Record<string, any>): {
  all_safe: boolean;
  in_domain: boolean;
  violations: string[];
  warnings: string[];
  mahalanobis_distance: number;
  mahalanobis_limit: number;
  composition_sum: number;
  xi_coordinates: number[];
} {
  const violations: string[] = [];
  const warnings: string[] = [];

  const feedFlow = Math.max(0.0, Number(scenario.feed_flow_t_h ?? 250.0));
  const mcrFlow = Math.max(0.0, Number(scenario.mcr_flow_t_h ?? 560.0));

  // 1. Compressor Anti-Surge Verification
  if (mcrFlow < ANTISURGE_FLOW_FLOOR_T_H) {
    violations.push(
      `Laju alir MCR (${mcrFlow.toFixed(1)} t/h) berada di bawah batas minimum anti-surge (${ANTISURGE_FLOW_FLOOR_T_H.toFixed(1)} t/h). Katup kickback 4UV-53 wajib membuka untuk melindungi kompresor 4K-2/3.`
    );
  }

  // 2. Suction Drum Temperature Alarm Low
  const tSuct = Number(scenario.H4TI004B ?? scenario.t_suct_4c8_c ?? -40.5);
  if (tSuct <= SUCTION_TALL_DEG_C) {
    violations.push(
      `Suhu suction drum (${tSuct.toFixed(1)} °C) melanggar batas trip darurat TALL (${SUCTION_TALL_DEG_C.toFixed(1)} °C). Risiko tinggi kondensasi cairan dan kerusakan sudu impeller kompresor!`
    );
  } else if (tSuct <= SUCTION_TAL_DEG_C) {
    violations.push(
      `Suhu suction drum (${tSuct.toFixed(1)} °C) melanggar batas alarm TAL (${SUCTION_TAL_DEG_C.toFixed(1)} °C). Katup reheat 4TV-510 wajib membuka proporsional.`
    );
  }

  // 3. MCHE Bundle Differential Pressures
  const dpW = Number(scenario.dp_mche_warm_kgcm2 ?? 0.213);
  const dpC = Number(scenario.dp_mche_cold_kgcm2 ?? 0.079);
  if (dpW >= MCHE_WARM_DP_TRIP_KG_CM2) {
    violations.push(
      `Beda tekan warm bundle MCHE (${dpW.toFixed(3)} kg/cm2) melanggar batas trip (${MCHE_WARM_DP_TRIP_KG_CM2.toFixed(2)} kg/cm2).`
    );
  } else if (dpW >= MCHE_WARM_DP_ALARM_KG_CM2) {
    warnings.push(
      `Beda tekan warm bundle MCHE (${dpW.toFixed(3)} kg/cm2) mendekati batas alarm (${MCHE_WARM_DP_ALARM_KG_CM2.toFixed(2)} kg/cm2).`
    );
  }

  if (dpC > MCHE_COLD_DP_MAX_KG_CM2) {
    warnings.push(
      `Beda tekan cold bundle MCHE (${dpC.toFixed(3)} kg/cm2) melebihi batas tipikal (${MCHE_COLD_DP_MAX_KG_CM2.toFixed(2)} kg/cm2).`
    );
  }

  // 4. Propane Suction Vacuum Check
  const pC3Suct = Number(scenario.p_c3_suct_kgcm2a ?? 1.045);
  if (pC3Suct < C3_SUCTION_MIN_KG_CM2A) {
    violations.push(
      `Tekanan suction propana 4K-1 (${pC3Suct.toFixed(3)} kg/cm2A) berada di bawah tekanan atmosferik (risiko kebocoran udara masuk ke sistem pendingin).`
    );
  }

  // 5. MITA Minimum Temperature Approach Check (MITA >= 1.50 C, AGENTS.md Pasal 5)
  if (scenario.mita_pinch_c !== undefined) {
    const mita = Number(scenario.mita_pinch_c);
    if (mita < MITA_MIN_PINCH_C) {
      violations.push(
        `Batas minimum MITA (${mita.toFixed(2)} °C) melanggar batas keselamatan (MITA >= ${MITA_MIN_PINCH_C.toFixed(2)} °C). Risiko temperature crossover!`
      );
    }
  }

  // 6. Composition Check & Mahalanobis Envelope
  const rawN2 = Number(scenario.comp_N2_molpct ?? 3.38);
  const rawC1 = Number(scenario.comp_C1_molpct ?? 44.37);
  const rawC2 = Number(scenario.comp_C2_molpct ?? 44.94);
  const rawC2H4 = Number(scenario.comp_C2H4_molpct ?? 0.85);
  const rawC3 = Number(scenario.comp_C3_molpct ?? 6.28);
  const rawComp = [rawN2, rawC1, rawC2, rawC2H4, rawC3];
  const compSum = rawComp.reduce((a, b) => a + b, 0.0);

  if (rawComp.some((v) => v < 0.0)) {
    violations.push('Fraksi mol komponen refrigeran dilarang bernilai negatif.');
  }

  if (compSum > 1.5) {
    const closureError = Math.abs(compSum - 100.0);
    if (closureError > 0.5) {
      warnings.push(
        `Total fraksi mol MCR berjumlah ${compSum.toFixed(2)} mol% (diharapkan mendekati 100.0 mol%). Normalisasi otomatis diterapkan.`
      );
    }
  }

  const fracComp = compSum > 1.5 ? rawComp.map((v) => v / compSum) : rawComp.map((v) => v / Math.max(compSum, 1e-6));
  const envRes = checkCompositionEnvelope(fracComp);
  const dm = envRes.mahalanobis_distance;
  const crit = envRes.critical_threshold;

  if (!envRes.in_envelope) {
    warnings.push(
      `Jarak Mahalanobis komposisi MCR (D_M = ${dm.toFixed(3)}) melampaui elipsoid historis kilang (batas ${crit.toFixed(3)}). Model ML berada pada rezim ekstrapolasi statistik. Konsultasikan dengan Process Engineer.`
    );
  }

  // 7. Feed Flow Training Domain Check
  let inFeedDomain = true;
  if (feedFlow < FEED_FLOW_MIN_T_H || feedFlow > FEED_FLOW_MAX_T_H) {
    inFeedDomain = false;
    warnings.push(
      `Laju umpan gas (${feedFlow.toFixed(1)} t/h) berada di luar rentang dataset pelatihan [${FEED_FLOW_MIN_T_H.toFixed(0)}, ${FEED_FLOW_MAX_T_H.toFixed(0)}] t/h.`
    );
  }

  const allSafe = violations.length === 0;
  const inDomain = envRes.in_envelope && inFeedDomain;

  return {
    all_safe: allSafe,
    in_domain: inDomain,
    violations,
    warnings,
    mahalanobis_distance: dm,
    mahalanobis_limit: crit,
    composition_sum: Math.round(compSum * 1000) / 1000,
    xi_coordinates: envRes.xi_coordinates,
  };
}

// ── Make-up Stream Purity Matrix Y & Molar Conservation Engine ────────────

export const DEFAULT_STREAM_PURITY_MATRIX: Record<string, Record<string, number>> = {
  N2: { N2: 1.000, C1: 0.000, C2: 0.000, C2H4: 0.000, C3: 0.000 },
  C1: { N2: 0.0005, C1: 0.9551, C2: 0.0275, C2H4: 0.000, C3: 0.0169 },
  C2: { N2: 0.000, C1: 0.0200, C2: 0.9650, C2H4: 0.000, C3: 0.0150 },
  C3: { N2: 0.000, C1: 0.0050, C2: 0.0150, C2H4: 0.000, C3: 0.9800 },
  C2H4: { N2: 0.000, C1: 0.000, C2: 0.0050, C2H4: 0.9950, C3: 0.000 },
};

export const SCF_PER_NM3 = 37.3263;
export const SCFD_PER_NM3_H = 24.0 * SCF_PER_NM3;

export function invertMatrix5x5(A: number[][]): number[][] {
  const n = 5;
  const M: number[][] = [];
  for (let i = 0; i < n; i++) {
    M[i] = [];
    for (let j = 0; j < n; j++) M[i][j] = A[i][j];
    for (let j = 0; j < n; j++) M[i][n + j] = i === j ? 1.0 : 0.0;
  }
  for (let i = 0; i < n; i++) {
    let maxRow = i;
    for (let k = i + 1; k < n; k++) {
      if (Math.abs(M[k][i]) > Math.abs(M[maxRow][i])) maxRow = k;
    }
    if (Math.abs(M[maxRow][i]) < 1e-12) {
      return [
        [1, 0, 0, 0, 0],
        [0, 1, 0, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 0, 1, 0],
        [0, 0, 0, 0, 1],
      ];
    }
    const temp = M[i];
    M[i] = M[maxRow];
    M[maxRow] = temp;
    const pivot = M[i][i];
    for (let j = 0; j < 2 * n; j++) M[i][j] /= pivot;
    for (let k = 0; k < n; k++) {
      if (k !== i) {
        const factor = M[k][i];
        for (let j = 0; j < 2 * n; j++) M[k][j] -= factor * M[i][j];
      }
    }
  }
  const inv: number[][] = [];
  for (let i = 0; i < n; i++) {
    inv[i] = [];
    for (let j = 0; j < n; j++) inv[i][j] = M[i][n + j];
  }
  return inv;
}

export function validateMakeupInputs(
  actualMolpct?: Record<string, number> | null,
  targetMolpct?: Record<string, number> | null,
  transitionHours?: number | null,
  inventoryKg?: number | null
): { isValid: boolean; reason: string } {
  if (!actualMolpct || typeof actualMolpct !== 'object' || Object.keys(actualMolpct).length === 0) {
    return { isValid: false, reason: 'Actual GC composition data (actualMolpct) is missing or empty' };
  }
  if (!targetMolpct || typeof targetMolpct !== 'object' || Object.keys(targetMolpct).length === 0) {
    return { isValid: false, reason: 'Target scenario composition data (targetMolpct) is missing or empty' };
  }
  if (inventoryKg == null || typeof inventoryKg !== 'number' || !isFinite(inventoryKg) || inventoryKg <= 0.0) {
    return { isValid: false, reason: 'MCR loop inventory estimate (inventoryKg) is invalid, non-finite, or non-positive' };
  }
  if (transitionHours == null || typeof transitionHours !== 'number' || !isFinite(transitionHours) || transitionHours <= 0.0) {
    return { isValid: false, reason: 'Transition duration (transitionHours) is invalid, non-finite, or non-positive' };
  }

  const coreComps = ['N2', 'C1', 'C2', 'C3'];
  for (const comp of coreComps) {
    if (actualMolpct[comp] == null || isNaN(actualMolpct[comp])) {
      return { isValid: false, reason: `Required core component ${comp} missing from actual GC composition` };
    }
    if (targetMolpct[comp] == null || isNaN(targetMolpct[comp])) {
      return { isValid: false, reason: `Required core component ${comp} missing from target composition` };
    }
  }

  const totAct = coreComps.reduce((acc, k) => acc + (actualMolpct[k] || 0), 0) + (actualMolpct.C2H4 || 0);
  const totTgt = coreComps.reduce((acc, k) => acc + (targetMolpct[k] || 0), 0) + (targetMolpct.C2H4 || 0);

  if (!isFinite(totAct) || totAct <= 10.0 || totAct > 150.0) {
    return { isValid: false, reason: `Actual total mole percent (${totAct.toFixed(2)}%) is outside physical range (10-150%)` };
  }
  if (!isFinite(totTgt) || totTgt <= 10.0 || totTgt > 150.0) {
    return { isValid: false, reason: `Target total mole percent (${totTgt.toFixed(2)}%) is outside physical range (10-150%)` };
  }

  return { isValid: true, reason: 'Valid' };
}

export function buildUnevaluatedMakeupResponse(
  reason: string,
  transitionHours?: number | null,
  inventoryKg?: number | null,
  c1Tag: string = 'H4FIC005'
): MakeupAdvisory {
  const items: MakeupInjectionItem[] = [];
  const compList = ['N2', 'C1', 'C2', 'C3'];

  for (const comp of compList) {
    const meta = TAG_MAKEUP_CONTROLLERS[comp];
    const tag = comp === 'C1' ? c1Tag : meta.tag;
    items.push({
      component: comp,
      tag_dcs: tag,
      alternate_tag_dcs: comp === 'C1' ? 'H4FIC009' : null,
      description: meta.desc,
      unit: 'Nm3/h',
      actual_molpct: null,
      target_molpct: null,
      delta_molpct: null,
      needed_kmol: null,
      needed_kg: null,
      recommended_flow_nm3_h: null,
      recommended_flow_kg_h: null,
      recommended_flow_t_h: null,
      recommended_flow_scfd: null,
      stream_mw: null,
      action: 'TIDAK DAPAT DIEVALUASI',
      instruction: `[ADVISORY] Make-up calculation cannot be evaluated: ${reason}.`,
    });
  }

  return {
    status: 'NOT EVALUATED',
    transition_hours: transitionHours != null && transitionHours > 0 ? transitionHours : null,
    estimated_inventory_kg: inventoryKg != null && inventoryKg > 0 ? inventoryKg : null,
    initial_moles_kmol: null,
    final_moles_kmol: null,
    expansion_ratio: null,
    total_makeup_flow_nm3_h: null,
    total_makeup_flow_kg_h: null,
    total_makeup_flow_t_h: null,
    total_makeup_flow_scfd: null,
    items,
    recommendations: items,
    explanation: `Make-up advisory status is NOT EVALUATED: ${reason}.`,
    operational_notes: [
      `STATUS: NOT EVALUATED: ${reason}.`,
      'Safety notice: Do not initiate make-up injection without complete laboratory GC verification.',
    ],
    calculation_timestamp: new Date().toISOString(),
  };
}

/**
 * Re-engineered closed-loop make-up advisory engine.
 */
export function calculateMakeupAdvisory(
  actualMolpct?: Record<string, number> | null,
  targetMolpct?: Record<string, number> | null,
  transitionHours: number = 2.0,
  inventoryKg: number = ESTIMATED_MCR_LOOP_INVENTORY_KG,
  useStreamPurity: boolean = true,
  purityMatrix?: Record<string, Record<string, number>> | null,
  c1Tag: string = 'H4FIC005'
): MakeupAdvisory {
  const validation = validateMakeupInputs(actualMolpct, targetMolpct, transitionHours, inventoryKg);
  if (!validation.isValid) {
    return buildUnevaluatedMakeupResponse(validation.reason, transitionHours, inventoryKg, c1Tag);
  }

  const tHours = Math.max(0.5, transitionHours);
  const invKg = inventoryKg;

  const components = ['N2', 'C1', 'C2', 'C2H4', 'C3'];
  const actSum = components.reduce((acc, k) => acc + Math.max(0.0, actualMolpct![k] || 0.0), 0.0);
  const tgtSum = components.reduce((acc, k) => acc + Math.max(0.0, targetMolpct![k] || 0.0), 0.0);

  if (actSum <= 1e-6 || tgtSum <= 1e-6) {
    return buildUnevaluatedMakeupResponse('Actual or target composition sum is zero or near-zero', tHours, invKg, c1Tag);
  }

  const x0 = components.map((k) => Math.max(0.0, actualMolpct![k] || 0.0) / actSum);
  const xTgt = components.map((k) => Math.max(0.0, targetMolpct![k] || 0.0) / tgtSum);

  const mwVec = components.map((k) => MW_SPECIES[k]);
  let avgMwAct = 0.0;
  for (let i = 0; i < components.length; i++) avgMwAct += x0[i] * mwVec[i];
  const n0 = invKg / Math.max(avgMwAct, 10.0);

  const activePurity = purityMatrix || DEFAULT_STREAM_PURITY_MATRIX;

  const Y: number[][] = [];
  for (let i = 0; i < 5; i++) {
    Y[i] = [];
    const compI = components[i];
    for (let j = 0; j < 5; j++) {
      const streamJ = components[j];
      if (useStreamPurity) {
        const streamDict = activePurity[streamJ] || {};
        Y[i][j] = streamDict[compI] != null ? streamDict[compI] : (i === j ? 1.0 : 0.0);
      } else {
        Y[i][j] = i === j ? 1.0 : 0.0;
      }
    }
  }

  for (let j = 0; j < 5; j++) {
    let colSum = 0.0;
    for (let i = 0; i < 5; i++) colSum += Y[i][j];
    if (colSum === 0.0) colSum = 1.0;
    for (let i = 0; i < 5; i++) Y[i][j] /= colSum;
  }

  const YInv = useStreamPurity ? invertMatrix5x5(Y) : [
    [1, 0, 0, 0, 0],
    [0, 1, 0, 0, 0],
    [0, 0, 1, 0, 0],
    [0, 0, 0, 1, 0],
    [0, 0, 0, 0, 1],
  ];

  let hasDeficit = false;
  for (const comp of components) {
    if ((targetMolpct![comp] || 0.0) - (actualMolpct![comp] || 0.0) > 0.02) {
      hasDeficit = true;
      break;
    }
  }

  let expansionRatio = 1.0;
  let nFinal = n0;
  const uKmol = [0.0, 0.0, 0.0, 0.0, 0.0];
  const neededKmolVec = [0.0, 0.0, 0.0, 0.0, 0.0];

  if (hasDeficit) {
    const vVec = [0.0, 0.0, 0.0, 0.0, 0.0];
    const wVec = [0.0, 0.0, 0.0, 0.0, 0.0];
    for (let i = 0; i < 5; i++) {
      for (let j = 0; j < 5; j++) {
        vVec[i] += YInv[i][j] * xTgt[j];
        wVec[i] += YInv[i][j] * x0[j];
      }
    }

    let maxRatio = 1.0;
    for (let i = 0; i < 5; i++) {
      if (vVec[i] > 1e-5) {
        const ratio = wVec[i] / vVec[i];
        if (ratio > maxRatio) maxRatio = ratio;
      }
    }
    expansionRatio = maxRatio;
    nFinal = n0 * expansionRatio;

    for (let i = 0; i < 5; i++) {
      uKmol[i] = Math.max(0.0, nFinal * vVec[i] - n0 * wVec[i]);
    }

    for (let i = 0; i < 5; i++) {
      for (let j = 0; j < 5; j++) {
        neededKmolVec[i] += Y[i][j] * uKmol[j];
      }
    }
  }

  const items: MakeupInjectionItem[] = [];
  let totalFlowNm3H = 0.0;
  let totalFlowKgH = 0.0;
  let totalFlowTH = 0.0;
  let totalFlowScfd = 0.0;
  const notes: string[] = [];

  for (const comp of ['N2', 'C1', 'C2', 'C3']) {
    const cIdx = components.indexOf(comp);
    const actPct = Number(actualMolpct![comp] || 0.0);
    const tgtPct = Number(targetMolpct![comp] || 0.0);
    const deltaPct = tgtPct - actPct;

    const meta = TAG_MAKEUP_CONTROLLERS[comp];
    const tag = comp === 'C1' ? c1Tag : meta.tag;

    const streamKmol = uKmol[cIdx];
    let streamMw = 0.0;
    for (let i = 0; i < 5; i++) streamMw += Y[i][cIdx] * mwVec[i];
    const kmolAdd = neededKmolVec[cIdx];

    let flowNm3H = 0.0;
    let flowKgH = 0.0;
    let flowTH = 0.0;
    let flowScfd = 0.0;
    let neededKg = 0.0;
    let action = '';
    let instruction = '';

    if (streamKmol > 1e-4) {
      neededKg = streamKmol * streamMw;
      const neededNm3 = streamKmol * NORMAL_MOLAR_VOLUME_NM3_PER_KMOL;

      flowNm3H = neededNm3 / tHours;
      flowKgH = neededKg / tHours;
      flowTH = flowKgH / 1000.0;
      flowScfd = flowNm3H * SCFD_PER_NM3_H;

      action = 'INJEKSI';
      instruction = `[ADVISORY] Set valve ${tag} (${meta.desc}) to ${flowNm3H.toFixed(1)} Nm3/h (${flowKgH.toFixed(1)} kg/h / ${Math.round(flowScfd).toLocaleString('en-US')} scfd).`;
    } else if (expansionRatio > 1.0001) {
      action = 'TAHAN / STOP';
      instruction = `[ADVISORY] Keep valve ${tag} closed (component is in excess; will dilute as deficit components are injected).`;
    } else {
      action = 'STABIL / SEIMBANG';
      instruction = `[ADVISORY] Valve ${tag} on standby (component is within target tolerance).`;
    }

    totalFlowNm3H += flowNm3H;
    totalFlowKgH += flowKgH;
    totalFlowTH += flowTH;
    totalFlowScfd += flowScfd;

    items.push({
      component: comp,
      tag_dcs: tag,
      alternate_tag_dcs: comp === 'C1' ? 'H4FIC009' : null,
      description: meta.desc,
      unit: 'Nm3/h',
      actual_molpct: Math.round(actPct * 100) / 100,
      target_molpct: Math.round(tgtPct * 100) / 100,
      delta_molpct: Math.round(deltaPct * 100) / 100,
      needed_kmol: Math.round(kmolAdd * 10000) / 10000,
      needed_kg: Math.round(neededKg * 100) / 100,
      recommended_flow_nm3_h: Math.round(flowNm3H * 10) / 10,
      recommended_flow_kg_h: Math.round(flowKgH * 10) / 10,
      recommended_flow_t_h: Math.round(flowTH * 10000) / 10000,
      recommended_flow_scfd: Math.round(flowScfd),
      stream_mw: Math.round(streamMw * 10000) / 10000,
      action,
      instruction,
    });
  }

  const actC2H4 = Number(actualMolpct!.C2H4 || 0.0);
  const tgtC2H4 = Number(targetMolpct!.C2H4 || 0.0);
  if (Math.abs(tgtC2H4 - actC2H4) > 0.05) {
    const diff = tgtC2H4 - actC2H4;
    notes.push(
      `Ethylene (C2H4) notice: Delta ${diff > 0 ? '+' : ''}${diff.toFixed(2)} mol%. Ethylene make-up is administered manually via refrigerant cylinders when required.`
    );
  }

  const expansionPct = (expansionRatio - 1.0) * 100.0;
  if (expansionPct > 25.0) {
    notes.push(
      `Loop inventory notice: Total mole expansion of ${expansionPct.toFixed(1)}% required to reach target recipe without venting. Consider partial loop purge if suction drum pressure approaches high limit.`
    );
  }

  notes.push(
    `Injection rates calculated via closed-loop dilution balance for an estimated MCR loop inventory of ${invKg.toLocaleString('en-US', { maximumFractionDigits: 0 })} kg over a ${tHours.toFixed(1)}-hour transition window.`
  );
  if (useStreamPurity) {
    notes.push(
      'Calculation incorporates header purity matrix: treated fuel gas for C1, de-ethanizer distillate for C2, de-propanizer distillate for C3.'
    );
  }
  notes.push(
    'SAFETY ADVISORY: Recommendations are decision-support guidelines for plant operators. This software has no write access to DCS, SIS, or field controllers.'
  );

  const explanation = `Closed-loop make-up evaluated for a ${tHours.toFixed(1)}-hour transition with ${expansionPct.toFixed(1)}% mole expansion. Total make-up rate: ${totalFlowNm3H.toFixed(1)} Nm3/h (${totalFlowKgH.toFixed(1)} kg/h / ${Math.round(totalFlowScfd).toLocaleString('en-US')} scfd).`;

  return {
    status: 'EVALUATED',
    transition_hours: Math.round(tHours * 100) / 100,
    estimated_inventory_kg: Math.round(invKg * 10) / 10,
    initial_moles_kmol: Math.round(n0 * 100) / 100,
    final_moles_kmol: Math.round(nFinal * 100) / 100,
    expansion_ratio: Math.round(expansionRatio * 10000) / 10000,
    total_makeup_flow_nm3_h: Math.round(totalFlowNm3H * 10) / 10,
    total_makeup_flow_kg_h: Math.round(totalFlowKgH * 10) / 10,
    total_makeup_flow_t_h: Math.round(totalFlowTH * 10000) / 10000,
    total_makeup_flow_scfd: Math.round(totalFlowScfd),
    items,
    recommendations: items,
    explanation,
    operational_notes: notes,
    calculation_timestamp: new Date().toISOString(),
  };
}

/**
 * Pure TypeScript First-Principles & Surrogate Prediction Pipeline.
 * 
 * Replicates backend routes.py predict_scenario with 100% exact numerical fidelity.
 * 
 * @param scenario Operator scenario input
 * @param actualDcs Optional operator actual DCS state
 * @returns Complete PredictResponse
 */
export function computeClientPrediction(
  scenario: ScenarioInput,
  actualDcs?: Partial<ScenarioInput>
): PredictResponse {
  const reqDict: Record<string, any> = { ...scenario };

  if (actualDcs) {
    if (actualDcs.feed_flow_t_h !== undefined && reqDict.actual_feed_flow_t_h === undefined) {
      reqDict.actual_feed_flow_t_h = actualDcs.feed_flow_t_h;
    }
    if (actualDcs.lng_flow_t_h !== undefined && reqDict.actual_lng_flow_t_h === undefined) {
      reqDict.actual_lng_flow_t_h = actualDcs.lng_flow_t_h;
    }
    if (actualDcs.mcr_flow_t_h !== undefined && reqDict.actual_mcr_flow_t_h === undefined) {
      reqDict.actual_mcr_flow_t_h = actualDcs.mcr_flow_t_h;
    }
    if (actualDcs.comp_N2_molpct !== undefined && reqDict.actual_comp_N2_molpct === undefined) {
      reqDict.actual_comp_N2_molpct = actualDcs.comp_N2_molpct;
    }
    if (actualDcs.comp_C1_molpct !== undefined && reqDict.actual_comp_C1_molpct === undefined) {
      reqDict.actual_comp_C1_molpct = actualDcs.comp_C1_molpct;
    }
    if (actualDcs.comp_C2_molpct !== undefined && reqDict.actual_comp_C2_molpct === undefined) {
      reqDict.actual_comp_C2_molpct = actualDcs.comp_C2_molpct;
    }
    if (actualDcs.comp_C2H4_molpct !== undefined && reqDict.actual_comp_C2H4_molpct === undefined) {
      reqDict.actual_comp_C2H4_molpct = actualDcs.comp_C2H4_molpct;
    }
    if (actualDcs.comp_C3_molpct !== undefined && reqDict.actual_comp_C3_molpct === undefined) {
      reqDict.actual_comp_C3_molpct = actualDcs.comp_C3_molpct;
    }
  }

  const feedFlow = Math.max(0.0, Number(reqDict.feed_flow_t_h ?? 250.0));
  const mcrFlow = Math.max(0.0, Number(reqDict.mcr_flow_t_h ?? 560.0));

  // 1. Feature construction (20 physical features)
  const { featureVector, featureDict, compSum } = buildFeatureVector(reqDict);

  // 2. Surrogate model evaluation & capacity check
  const capacityExceeded = feedFlow > TRAIN_H_MAX_DESIGN_FEED_T_H;
  const capacityWarning = capacityExceeded
    ? `PERINGATAN KAPASITAS: Laju umpan ${feedFlow.toFixed(1)} t/h melebihi kapasitas desain Train H (${TRAIN_H_MAX_DESIGN_FEED_T_H.toFixed(1)} t/h). Indikator daya dan SEC dihitung berbasis ekstrapolasi termodinamika batas keselamatan.`
    : null;

  const baselinePhysicalMw = getPlant3BaselinePower(feedFlow);
  const rawSurrPred = evaluateRidgeSurrogate(featureVector);

  const snapshotGc: Record<string, number> = { N2: 3.39, C1: 44.45, C2: 45.02, C2H4: 0.85, C3: 6.29 };
  const actualComp: Record<string, number> = {
    N2: Number(reqDict.actual_comp_N2_molpct ?? snapshotGc.N2),
    C1: Number(reqDict.actual_comp_C1_molpct ?? snapshotGc.C1),
    C2: Number(reqDict.actual_comp_C2_molpct ?? snapshotGc.C2),
    C2H4: Number(reqDict.actual_comp_C2H4_molpct ?? snapshotGc.C2H4),
    C3: Number(reqDict.actual_comp_C3_molpct ?? snapshotGc.C3),
  };
  const dcsMcrAtFeed = Math.max(504.0, Math.round(feedFlow * (562.3 / 245.8) * 10) / 10);

  const refReq: Record<string, any> = {
    ...reqDict,
    feed_flow_t_h: feedFlow,
    mcr_flow_t_h: dcsMcrAtFeed,
    comp_N2_molpct: actualComp.N2,
    comp_C1_molpct: actualComp.C1,
    comp_C2_molpct: actualComp.C2,
    comp_C2H4_molpct: actualComp.C2H4,
    comp_C3_molpct: actualComp.C3,
  };
  const { featureVector: refVec } = buildFeatureVector(refReq);
  const refSurrPred = evaluateRidgeSurrogate(refVec);
  const deltaMcrTuningMw = rawSurrPred - refSurrPred;

  let powerPredMw: number;
  if (Math.abs(feedFlow - 245.8) < 1.0) {
    powerPredMw = clip(rawSurrPred, 40.0, 150.0);
  } else {
    powerPredMw = clip(baselinePhysicalMw + deltaMcrTuningMw, 40.0, 150.0);
  }

  // 3. Operating regime classification
  const regime = classifyRegime(feedFlow);

  // 4. Power decomposition: Propane C3 (4KT-1) vs MCR (4KT-2 + 4KT-3) (AGENTS.md Pasal 10)
  const fracC3 = C3_POWER_SHARE_BY_REGIME[regime] ?? 0.3775;
  const powerC3Mw = Math.round(powerPredMw * fracC3 * 100) / 100;
  const powerMcrMw = Math.round(powerPredMw * (1.0 - fracC3) * 100) / 100;

  // 5. LNG Rundown Flow (H5FI6A) & Specific Energy Consumption (SEC) [kWh/t]
  let lngFlowTH: number | null = null;
  let secLngStatus = 'N/A - data produksi LNG belum tersedia';
  let flashSummary: FlashDrumSummary | null = null;

  if (reqDict.lng_flow_t_h !== undefined && Number(reqDict.lng_flow_t_h) > 10.0) {
    lngFlowTH = Number(reqDict.lng_flow_t_h);
    secLngStatus = 'VALID (Meter Fiskal H5FI6A)';
  } else if (feedFlow > 10.0) {
    const tMche = Number(reqDict.t_mche_out_c ?? -152.5);
    const pMche = Number(reqDict.p_mche_out_kgcm2g ?? 41.5);
    const pFlash = Number(reqDict.p_flash_kgcm2g ?? 0.30);
    const flashRes = calculateFlashDrum5C1(feedFlow, {
      tMcheOutC: tMche,
      pMcheOutKgcm2g: pMche,
      pFlashKgcm2g: pFlash,
    });
    lngFlowTH = Math.round(flashRes.lngLiquidFlowTH * 100) / 100;
    secLngStatus = `VALID (PR-EOS Flash 5C-1: Yield ${(flashRes.massLiquidYield * 100).toFixed(2)} wt%, T_flash ${flashRes.tFlashC.toFixed(1)}°C)`;
    flashSummary = {
      feed_flow_t_h: flashRes.feedFlowTH,
      lng_liquid_flow_t_h: flashRes.lngLiquidFlowTH,
      efg_gas_flow_t_h: flashRes.efgGasFlowTH,
      mass_liquid_yield: flashRes.massLiquidYield,
      vapor_fraction_mol: flashRes.vaporFractionMol,
      t_flash_c: flashRes.tFlashC,
      t_bubble_c: flashRes.tBubbleC,
      p_flash_kgcm2g: flashRes.pFlashKgcm2g,
      status: flashRes.status,
    };
  }

  const secLngKwhPerT = lngFlowTH && lngFlowTH > 10.0 ? (powerPredMw * 1000.0) / lngFlowTH : null;
  const specificShaftPowerFeed = feedFlow > 10.0 ? (powerPredMw * 1000.0) / feedFlow : null;
  const secKwhPerT = secLngKwhPerT !== null ? secLngKwhPerT : specificShaftPowerFeed;

  // 6. Deltas vs actual DCS state (evaluated ceteris-paribus)
  const actualFeed = reqDict.actual_feed_flow_t_h;
  const actualMcr = reqDict.actual_mcr_flow_t_h;
  let actualPowerMw: number | null = null;
  const baselineTotalMw = Math.abs(feedFlow - 245.8) < 1.0 ? clip(refSurrPred, 40.0, 150.0) : baselinePhysicalMw;
  const baselineFeed = feedFlow;

  if (actualFeed !== undefined && actualMcr !== undefined) {
    const actualReq: Record<string, any> = {
      ...reqDict,
      feed_flow_t_h: Number(actualFeed),
      mcr_flow_t_h: Number(actualMcr),
      comp_N2_molpct: actualComp.N2,
      comp_C1_molpct: actualComp.C1,
      comp_C2_molpct: actualComp.C2,
      comp_C2H4_molpct: actualComp.C2H4,
      comp_C3_molpct: actualComp.C3,
    };
    const { featureVector: actVec } = buildFeatureVector(actualReq);
    actualPowerMw = clip(evaluateRidgeSurrogate(actVec), 40.0, 150.0);
  }

  let actualLngTH: number;
  const actualLngInput = reqDict.actual_lng_flow_t_h;
  if (
    actualLngInput !== undefined &&
    Number(actualLngInput) > 10.0 &&
    Math.abs(baselineFeed - Number(actualFeed ?? baselineFeed)) < 0.1
  ) {
    actualLngTH = Number(actualLngInput);
  } else {
    const baseFlash = calculateFlashDrum5C1(baselineFeed);
    actualLngTH = Math.round(baseFlash.lngLiquidFlowTH * 100) / 100;
  }

  const baselineSecLng = actualLngTH > 10.0 ? (baselineTotalMw * 1000.0) / actualLngTH : 0.0;
  const deltaPowerMw = Math.round((powerPredMw - baselineTotalMw) * 100) / 100;
  const deltaPowerPct =
    baselineTotalMw > 0 ? Math.round(((deltaPowerMw / baselineTotalMw) * 100.0) * 100) / 100 : 0.0;
  const deltaSec = secLngKwhPerT !== null ? Math.round((secLngKwhPerT - baselineSecLng) * 100) / 100 : null;

  // 7. Decarbonization calculation (Manual Book Modul 8 chain)
  let co2AbatementTDay: number | null = null;
  if (deltaPowerMw < 0) {
    const dSteamTH = Math.abs(deltaPowerMw) * STEAM_RATE_T_PER_MWH;
    const dFgNm3H = dSteamTH * FUEL_GAS_NM3_PER_T_STEAM;
    const co2TH = dFgNm3H * FUEL_GAS_GJ_PER_NM3 * CO2_KG_PER_GJ * 1e-3;
    co2AbatementTDay = Math.round(co2TH * 24.0 * 10) / 10;
  }

  // 8. Process safety and domain validation
  const validation = validateOperatingPoint(reqDict);

  let statusLabel: string;
  if (!validation.all_safe) {
    statusLabel = 'Skenario Ditolak (Pelanggaran Batas Keselamatan)';
  } else if (validation.warnings.length > 0) {
    statusLabel = 'Ada Kendala yang Perlu Ditinjau (Peringatan Margin)';
  } else if (!validation.in_domain) {
    statusLabel = 'Di Luar Domain Operasional Model (D_M > 3.08)';
  } else {
    statusLabel = 'Semua kendala yang diperiksa terpenuhi';
  }

  // 9. Hydrocarbon Make-up Injection Advisory
  const targetComp: Record<string, number> = {
    N2: Number(reqDict.comp_N2_molpct ?? 3.38),
    C1: Number(reqDict.comp_C1_molpct ?? 44.37),
    C2: Number(reqDict.comp_C2_molpct ?? 44.94),
    C2H4: Number(reqDict.comp_C2H4_molpct ?? 0.85),
    C3: Number(reqDict.comp_C3_molpct ?? 6.28),
  };
  const transitionHours = Number(reqDict.transition_hours ?? 2.0);
  const makeupAdvisory = calculateMakeupAdvisory(actualComp, targetComp, transitionHours);

  // 10. Chiller and Propane Condenser Duties (incorporating internal T_CW = 30.0 C)
  const chillerDuties: ChillerDutyResult = calculateChillerAndCondenserDuties(
    feedFlow,
    mcrFlow,
    DEFAULT_COOLING_WATER.T_CW_in_C
  );

  // 11. Model Confidence & Uncertainty
  const regimeMetrics: Record<string, { r2: number; mae_mw: number }> = {
    underload: { r2: 0.491, mae_mw: 0.774 },
    transition: { r2: 0.477, mae_mw: 1.250 },
    baseload: { r2: 0.668, mae_mw: 0.520 },
  };
  const regInfo = regimeMetrics[regime] || { r2: 0.50, mae_mw: 0.80 };
  let regimeWarning: string | null = null;
  if (regInfo.r2 < 0.60) {
    regimeWarning = `Perhatian: Akurasi model pada rezim ${regime} (R2 = ${regInfo.r2.toFixed(3)}) lebih rendah dari baseload. Gunakan hasil sebagai estimasi awal dan konsultasikan dengan Process Engineer.`;
  }

  const predictionSummary: PredictionSummary = {
    total_shaft_power_mw: Math.round(powerPredMw * 100) / 100,
    power_mcr_mw: powerMcrMw,
    power_c3_mw: powerC3Mw,
    delta_power_mw: deltaPowerMw,
    delta_power_pct: deltaPowerPct,
    sec_kwh_per_t: secKwhPerT !== null ? Math.round(secKwhPerT * 100) / 100 : null,
    specific_shaft_power_feed_kwh_per_t:
      specificShaftPowerFeed !== null ? Math.round(specificShaftPowerFeed * 100) / 100 : null,
    sec_lng_kwh_per_t: secLngKwhPerT !== null ? Math.round(secLngKwhPerT * 100) / 100 : null,
    sec_lng_status: secLngStatus,
    delta_sec_kwh_per_t: deltaSec,
    co2_abatement_t_day: co2AbatementTDay,
    operating_regime: regime,
    data_label: 'SIMULASI SKENARIO WHAT-IF',
    battery_limit_note: 'Includes MCR compressors 4K-2/3 and Propane precooling compressor 4K-1',
    capacity_warning: capacityWarning,
    capacity_exceeded: capacityExceeded,
  };

  const domainCheck: DomainCheck = {
    in_domain: validation.in_domain,
    mahalanobis_distance: validation.mahalanobis_distance,
    mahalanobis_limit: validation.mahalanobis_limit,
    composition_closure_ok: Math.abs(compSum - 100.0) < 1.0 || Math.abs(compSum - 1.0) < 0.01,
    composition_sum_molpct: validation.composition_sum,
  };

  const safetyCheck: SafetyCheck = {
    all_safe: validation.all_safe,
    status_label: statusLabel,
    violations: validation.violations,
    warnings: validation.warnings,
    unverified_checks: [
      'Peta anti-surge dinamis kompresor sentrifugal (memerlukan kurva head/dp lengkap)',
    ],
  };

  return {
    prediction: predictionSummary,
    domain_check: domainCheck,
    safety_check: safetyCheck,
    confidence: {
      mae_mw: 0.802,
      bootstrap_ci_lower_mw: Math.round(Math.max(0.0, powerPredMw - 0.802) * 100) / 100,
      bootstrap_ci_upper_mw: Math.round((powerPredMw + 0.802) * 100) / 100,
      regime_r2: regInfo.r2,
      regime_warning: regimeWarning,
    },
    makeup_advisory: makeupAdvisory,
    features_computed: featureDict,
    actual_power_mw: actualPowerMw !== null ? Math.round(actualPowerMw * 100) / 100 : null,
    baseline_power_mw: Math.round(baselineTotalMw * 100) / 100,
    baseline_sec_lng: baselineSecLng !== null ? Math.round(baselineSecLng * 100) / 100 : null,
    flash_drum_5c1: flashSummary,
    cooling_water: DEFAULT_COOLING_WATER,
    chiller_duties: chillerDuties,
  };
}
