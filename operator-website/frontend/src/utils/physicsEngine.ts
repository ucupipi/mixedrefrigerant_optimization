// Pure TypeScript First-Principles Physics & Surrogate Calculation Engine
// Governance: AGENTS.md (Pasal 1, 2, 3, 4, 5, 10, 11, 12, 13)
// ZERO em-dash (U+2014) and ZERO en-dash (U+2013) strict rule

import type {
  ChillerDutyResult,
  DomainCheck,
  FlashDrumSummary,
  MakeupAdvisory,
  MakeupInjectionItem,
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

/**
 * Calculate recommended make-up injection rates for each component.
 */
export function calculateMakeupAdvisory(
  actualMolpct: Record<string, number>,
  targetMolpct: Record<string, number>,
  transitionHours: number = 2.0,
  inventoryKg: number = ESTIMATED_MCR_LOOP_INVENTORY_KG
): MakeupAdvisory {
  const tHours = Math.max(0.5, transitionHours);

  let totActMol = 0.0;
  for (const sp of Object.keys(MW_SPECIES)) {
    totActMol += actualMolpct[sp] || 0.0;
  }
  const normActual: Record<string, number> = {};
  for (const sp of Object.keys(MW_SPECIES)) {
    normActual[sp] = (actualMolpct[sp] || 0.0) / Math.max(totActMol, 1e-6);
  }

  let avgMw = 0.0;
  for (const sp of Object.keys(MW_SPECIES)) {
    avgMw += normActual[sp] * MW_SPECIES[sp];
  }

  const totalKmolLoop = inventoryKg / Math.max(avgMw, 10.0);

  const items: MakeupInjectionItem[] = [];
  let totalFlowNm3H = 0.0;
  let totalFlowKgH = 0.0;
  const notes: string[] = [];

  for (const comp of ['N2', 'C1', 'C2', 'C3']) {
    const act = Number(actualMolpct[comp] ?? 0.0);
    const tgt = Number(targetMolpct[comp] ?? 0.0);
    const deltaPct = tgt - act;
    const deltaFrac = deltaPct / 100.0;

    const meta = TAG_MAKEUP_CONTROLLERS[comp];
    const tag = meta.tag;
    const mw = MW_SPECIES[comp];

    let flowNm3H = 0.0;
    let flowKgH = 0.0;
    let action = '';
    let instruction = '';

    if (deltaPct > 0.02) {
      const neededKmol = deltaFrac * totalKmolLoop;
      const neededNm3 = neededKmol * NORMAL_MOLAR_VOLUME_NM3_PER_KMOL;
      const neededKg = neededKmol * mw;

      flowNm3H = neededNm3 / tHours;
      flowKgH = neededKg / tHours;

      totalFlowNm3H += flowNm3H;
      totalFlowKgH += flowKgH;

      action = 'INJEKSI';
      instruction = `Buka katup ${tag} ke ${flowNm3H.toFixed(1)} Nm3/h (${flowKgH.toFixed(1)} kg/h).`;
    } else if (deltaPct < -0.05) {
      action = 'TAHAN / STOP';
      instruction = `Tutup katup ${tag} (kadar sudah berlebih +${Math.abs(deltaPct).toFixed(2)}%).`;
    } else {
      action = 'STABIL / SEIMBANG';
      instruction = `Katup ${tag} standby (kadar sudah sesuai).`;
    }

    items.push({
      component: comp,
      tag_dcs: tag,
      description: meta.desc,
      unit: 'Nm3/h',
      actual_molpct: Math.round(act * 100) / 100,
      target_molpct: Math.round(tgt * 100) / 100,
      delta_molpct: Math.round(deltaPct * 100) / 100,
      recommended_flow_nm3_h: Math.round(flowNm3H * 10) / 10,
      recommended_flow_kg_h: Math.round(flowKgH * 10) / 10,
      action,
      instruction,
    });
  }

  const actC2H4 = Number(actualMolpct.C2H4 ?? 0.0);
  const tgtC2H4 = Number(targetMolpct.C2H4 ?? 0.0);
  if (Math.abs(tgtC2H4 - actC2H4) > 0.05) {
    const diff = tgtC2H4 - actC2H4;
    notes.push(
      `Perhatian C2H4 (Etilena): Selisih ${diff > 0 ? '+' : ''}${diff.toFixed(2)} mol%. Injeksi C2H4 dilakukan manual via silinder jika diperlukan.`
    );
  }

  notes.push(
    `Laju injeksi dihitung berdasarkan estimasi inventory loop MCR sebesar ${inventoryKg.toLocaleString('en-US', { maximumFractionDigits: 0 })} kg dengan durasi transisi ${tHours.toFixed(1)} jam untuk mencegah lonjakan termal pada MCHE.`
  );

  return {
    transition_hours: tHours,
    estimated_inventory_kg: inventoryKg,
    total_makeup_flow_nm3_h: Math.round(totalFlowNm3H * 10) / 10,
    total_makeup_flow_kg_h: Math.round(totalFlowKgH * 10) / 10,
    items,
    operational_notes: notes,
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

  const refReq: Record<string, any> = { ...reqDict, feed_flow_t_h: 245.8, mcr_flow_t_h: 505.3 };
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
  let baselineTotalMw = baselinePhysicalMw;
  const baselineFeed = feedFlow;

  const snapshotGc: Record<string, number> = { N2: 3.38, C1: 44.37, C2: 44.94, C2H4: 0.85, C3: 6.28 };
  const actualComp: Record<string, number> = {
    N2: Number(reqDict.actual_comp_N2_molpct ?? snapshotGc.N2),
    C1: Number(reqDict.actual_comp_C1_molpct ?? snapshotGc.C1),
    C2: Number(reqDict.actual_comp_C2_molpct ?? snapshotGc.C2),
    C2H4: Number(reqDict.actual_comp_C2H4_molpct ?? snapshotGc.C2H4),
    C3: Number(reqDict.actual_comp_C3_molpct ?? snapshotGc.C3),
  };

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

    if (Math.abs(feedFlow - Number(actualFeed)) < 0.5 && actualPowerMw !== null) {
      baselineTotalMw = actualPowerMw;
    } else {
      baselineTotalMw = baselinePhysicalMw;
    }
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
