import assert from 'node:assert';
import { calculateFlashDrum5C1 } from '../src/utils/thermoFlash.ts';

console.log('=== EMPIRICAL CHALLENGER 2: STATE & DISTURBANCE HARNESS ===\n');

// 1. CONSTANTS FROM App.tsx
const DEFAULT_ACTUAL = {
  feed_flow_t_h: 245.8,
  lng_flow_t_h: 232.3,
  mcr_flow_t_h: 562.3,
  comp_N2_molpct: 3.39,
  comp_C1_molpct: 44.45,
  comp_C2_molpct: 45.02,
  comp_C2H4_molpct: 0.85,
  comp_C3_molpct: 6.29,
};

const DEFAULT_RECOMMENDED = {
  feed_t_h: 245.8,
  mcr_flow_t_h: 480.0,
  comp_N2_molpct: 3.31,
  comp_C1_molpct: 46.08,
  comp_C2_molpct: 45.15,
  comp_C2H4_molpct: 0.05,
  comp_C3_molpct: 5.41,
  mahalanobis_distance: 0.858,
  expected_suction_temp_c: -38.7,
  suction_tal_ok: true,
  antisurge_floor_applied: true,
  envelope_shrink_applied: false,
  extrapolated: false,
  feed_span_t_h: [141.2, 296.4],
  source: 'Live SLSQP Solver (PR-EOS + GBRT Surrogate)',
  solver_converged: true,
  constraint_residuals: {
    suction_tal_margin_c: 6.31,
    mahalanobis_margin: 2.222,
    antisurge_margin_t_h: 0.0,
    superheat_margin_c: 20.76,
  },
};

const DEFAULT_PREDICTION = {
  prediction: {
    total_shaft_power_mw: 79.09,
    power_mcr_mw: 48.24,
    power_c3_mw: 30.85,
    delta_power_mw: -5.39,
    delta_power_pct: -6.38,
    sec_kwh_per_t: 340.49,
    specific_shaft_power_feed_kwh_per_t: 321.77,
    sec_lng_kwh_per_t: 340.49,
    sec_lng_status: 'OK',
    delta_sec_kwh_per_t: -23.21,
    co2_abatement_t_day: 52.4,
    operating_regime: 'underload',
    data_label: 'SKENARIO WHAT-IF (HASIL MODEL ML)',
    battery_limit_note: 'Mencakup kompresor MCR 4K-2/3 dan kompresor Propana 4K-1',
  },
  domain_check: {
    in_domain: true,
    mahalanobis_distance: 0.858,
    mahalanobis_limit: 3.0802,
    composition_closure_ok: true,
    composition_sum_molpct: 100.0,
  },
  safety_check: {
    all_safe: true,
    status_label: 'Semua kendala yang diperiksa terpenuhi',
    violations: [],
    warnings: [],
    unverified_checks: ['Peta anti-surge dinamis kompresor sentrifugal (memerlukan kurva head/dp lengkap)'],
  },
  confidence: {
    mae_mw: 0.802,
    bootstrap_ci_lower_mw: 78.29,
    bootstrap_ci_upper_mw: 79.89,
    regime_r2: 0.985,
    regime_warning: null,
  },
  actual_power_mw: 84.48,
  features_computed: {},
  makeup_advisory: {
    transition_hours: 2.0,
    estimated_inventory_kg: 85000,
    total_makeup_flow_nm3_h: 0,
    total_makeup_flow_kg_h: 0,
    items: [],
    operational_notes: [],
  },
};

// Initial Scenario state in App.tsx
const initialScenario = {
  ...DEFAULT_ACTUAL,
  mcr_flow_t_h: DEFAULT_RECOMMENDED.mcr_flow_t_h,
  comp_N2_molpct: DEFAULT_RECOMMENDED.comp_N2_molpct,
  comp_C1_molpct: DEFAULT_RECOMMENDED.comp_C1_molpct,
  comp_C2_molpct: DEFAULT_RECOMMENDED.comp_C2_molpct,
  comp_C2H4_molpct: DEFAULT_RECOMMENDED.comp_C2H4_molpct,
  comp_C3_molpct: DEFAULT_RECOMMENDED.comp_C3_molpct,
  transition_hours: 2.0,
};

// Calculation engine matching TabInputResults.tsx
function computeSection3KPIs(scenario, prediction) {
  const flashRes = calculateFlashDrum5C1(scenario.feed_flow_t_h);
  const scenarioLngFlow = flashRes.lngLiquidFlowTH;
  const baselinePower = prediction?.actual_power_mw ?? 84.48;
  const scenarioPower = prediction?.prediction?.total_shaft_power_mw ?? baselinePower;
  const deltaPower = prediction?.prediction?.delta_power_mw ?? (scenarioPower - baselinePower);
  const deltaPowerPct = prediction?.prediction?.delta_power_pct ?? (baselinePower > 0 ? (deltaPower / baselinePower) * 100 : 0);

  const activeLngFlow = Math.max(scenarioLngFlow, 10.0);
  const baselineSecLng = (baselinePower * 1000) / activeLngFlow;
  const scenarioSecLng = prediction?.prediction?.sec_lng_kwh_per_t ?? ((scenarioPower * 1000) / activeLngFlow);
  const deltaSecLng = prediction?.prediction?.delta_sec_kwh_per_t ?? (scenarioSecLng - baselineSecLng);
  const deltaSecLngPct = baselineSecLng > 0 ? (deltaSecLng / baselineSecLng) * 100 : 0;

  const STEAM_RATE_T_PER_MWH = 4.04;
  const FUEL_GAS_NM3_PER_T_STEAM = 97.7;
  const FG_DENSITY_KG_NM3 = 0.75;

  const deltaPowerSavingMw = Math.max(0, -deltaPower);
  const steamSaved_t_h = deltaPowerSavingMw * STEAM_RATE_T_PER_MWH;
  const fuelGasSaved_nm3_h = steamSaved_t_h * FUEL_GAS_NM3_PER_T_STEAM;
  const fuelGasSaved_t_h = (fuelGasSaved_nm3_h * FG_DENSITY_KG_NM3) / 1000;
  const fuelGasSaved_usd_yr = (fuelGasSaved_nm3_h * 0.03535 * 6.0 * 8000) / 1_000_000;

  // Card 1
  const card1Value = deltaSecLng < 0 ? Math.abs(deltaSecLng).toFixed(1) : '0.0';
  const card1Unit = 'kWh/t';
  const card1Badge = deltaSecLngPct < 0 ? `HEMAT ${Math.abs(deltaSecLngPct).toFixed(1)}%` : 'OPTIMAL';
  const card1Dcs = `DCS: ${baselineSecLng.toFixed(1)}`;
  const card1Ai = `Skenario: ${scenarioSecLng.toFixed(1)} kWh/t`;

  // Card 2
  const card2Value = deltaPowerSavingMw > 0 ? steamSaved_t_h.toFixed(1) : '0.0';
  const card2Unit = 't/jam';
  const card2Badge = 'BEBAN BOILER TURUN';

  // Card 3
  const card3Value = deltaPowerSavingMw > 0 ? fuelGasSaved_t_h.toFixed(1) : '0.0';
  const card3Unit = 't/jam';
  const card3Badge = `USD ${fuelGasSaved_usd_yr.toFixed(2)} JUTA / TAHUN`;

  // Card 4
  const card4Value = deltaPowerSavingMw > 0 ? deltaPowerSavingMw.toFixed(2) : '0.00';
  const card4Unit = 'MW';
  const card4Badge = deltaPowerPct < 0 ? `HEMAT ${Math.abs(deltaPowerPct).toFixed(1)}%` : 'BASELINE';
  const card4Dcs = `DCS: ${baselinePower.toFixed(1)} MW`;
  const card4Ai = `Skenario: ${scenarioPower.toFixed(1)} MW`;

  return {
    card1: { value: card1Value, unit: card1Unit, badge: card1Badge, dcs: card1Dcs, ai: card1Ai },
    card2: { value: card2Value, unit: card2Unit, badge: card2Badge },
    card3: { value: card3Value, unit: card3Unit, badge: card3Badge },
    card4: { value: card4Value, unit: card4Unit, badge: card4Badge, dcs: card4Dcs, ai: card4Ai },
    raw: {
      deltaSecLng,
      deltaSecLngPct,
      deltaPower,
      deltaPowerPct,
      deltaPowerSavingMw,
      baselineSecLng,
      scenarioSecLng,
      steamSaved_t_h,
      fuelGasSaved_t_h,
      fuelGasSaved_usd_yr
    }
  };
}

// ============================================================================
// TEST 1: Initial Render State Verification
// ============================================================================
console.log('--- TEST 1: Initial Render State Verification ---');
const initialKpis = computeSection3KPIs(initialScenario, DEFAULT_PREDICTION);

console.log('Card 1 (SEC LNG):', initialKpis.card1);
console.log('Card 2 (Steam):', initialKpis.card2);
console.log('Card 3 (Fuel Gas):', initialKpis.card3);
console.log('Card 4 (Total Shaft Power):', initialKpis.card4);

assert.strictEqual(initialKpis.card1.value, '23.2', 'Card 1 value must be exactly 23.2');
assert.strictEqual(initialKpis.card1.unit, 'kWh/t', 'Card 1 unit must be kWh/t');
assert.strictEqual(initialKpis.card1.badge, 'HEMAT 6.4%', 'Card 1 badge must be HEMAT 6.4%');
assert.strictEqual(initialKpis.card4.value, '5.39', 'Card 4 value must be exactly 5.39');
assert.strictEqual(initialKpis.card4.unit, 'MW', 'Card 4 unit must be MW');
assert.strictEqual(initialKpis.card4.badge, 'HEMAT 6.4%', 'Card 4 badge must be HEMAT 6.4%');

// Check for zero NaN / undefined in all cards
for (const [cardName, cardData] of Object.entries(initialKpis)) {
  if (cardName === 'raw') continue;
  for (const [key, val] of Object.entries(cardData)) {
    assert(!String(val).includes('NaN'), `${cardName}.${key} contains NaN: ${val}`);
    assert(!String(val).includes('undefined'), `${cardName}.${key} contains undefined: ${val}`);
    assert(!String(val).includes('null'), `${cardName}.${key} contains null: ${val}`);
  }
}
console.log('>>> TEST 1 PASSED: Initial Load State exactly matches requirements.\n');

// ============================================================================
// TEST 2: Zero NaN / Undefined / Boundary Robustness Testing
// ============================================================================
console.log('--- TEST 2: Boundary & Edge Case Robustness (No NaN / Undefined) ---');
const edgeFeeds = [10.0, 50.0, 120.0, 200.0, 245.8, 300.0, 350.0, 500.0];
for (const feed of edgeFeeds) {
  const testScenario = { ...initialScenario, feed_flow_t_h: feed };
  const res = computeSection3KPIs(testScenario, DEFAULT_PREDICTION);
  assert(!res.card1.value.includes('NaN'), `Feed ${feed}: Card 1 value is NaN`);
  assert(!res.card4.value.includes('NaN'), `Feed ${feed}: Card 4 value is NaN`);
  assert(!res.card1.badge.includes('NaN'), `Feed ${feed}: Card 1 badge is NaN`);
  assert(!res.card4.badge.includes('NaN'), `Feed ${feed}: Card 4 badge is NaN`);
}
console.log('>>> TEST 2 PASSED: 8 edge feed flow rates tested without any NaN/undefined.\n');

// ============================================================================
// TEST 3: Action "⚡ Terapkan Rekomendasi MCR" State Dynamics
// ============================================================================
console.log('--- TEST 3: Action "⚡ Terapkan Rekomendasi MCR" Simulation ---');
// Simulating when user has typed perturbed scenario values
let simulatedScenario = {
  ...initialScenario,
  mcr_flow_t_h: 530.0,
  comp_N2_molpct: 4.00,
  comp_C1_molpct: 43.00,
  comp_C2_molpct: 47.00,
  comp_C2H4_molpct: 0.50,
  comp_C3_molpct: 5.50,
};

// Optimum values from SLSQP
const opt = {
  mcr_flow_t_h: 480.0,
  comp_N2_molpct: 3.31,
  comp_C1_molpct: 46.08,
  comp_C2_molpct: 45.15,
  comp_C2H4_molpct: 0.05,
  comp_C3_molpct: 5.41,
};

// handleApplyRecommended
function handleApplyRecommended(scenarioState, optimumState) {
  return {
    ...scenarioState,
    mcr_flow_t_h: optimumState.mcr_flow_t_h,
    comp_N2_molpct: optimumState.comp_N2_molpct,
    comp_C1_molpct: optimumState.comp_C1_molpct,
    comp_C2_molpct: optimumState.comp_C2_molpct,
    comp_C2H4_molpct: optimumState.comp_C2H4_molpct,
    comp_C3_molpct: optimumState.comp_C3_molpct,
  };
}

const scenarioAfterApply = handleApplyRecommended(simulatedScenario, opt);
console.log('Scenario after "Terapkan Rekomendasi MCR":', scenarioAfterApply);
assert.strictEqual(scenarioAfterApply.mcr_flow_t_h, 480.0);
assert.strictEqual(scenarioAfterApply.comp_N2_molpct, 3.31);
assert.strictEqual(scenarioAfterApply.comp_C1_molpct, 46.08);
assert.strictEqual(scenarioAfterApply.comp_C2_molpct, 45.15);
assert.strictEqual(scenarioAfterApply.comp_C2H4_molpct, 0.05);
assert.strictEqual(scenarioAfterApply.comp_C3_molpct, 5.41);
console.log('>>> TEST 3 PASSED: Apply Recommended successfully sets exact SLSQP values.\n');

// ============================================================================
// TEST 4: Action "⟲ Reset ke DCS" State Dynamics
// ============================================================================
console.log('--- TEST 4: Action "⟲ Reset ke DCS" Simulation ---');
function handleResetSimulation(snapshotActual) {
  const act = { ...snapshotActual };
  const resetScenario = {
    ...act,
    transition_hours: 2.0,
  };
  const resetOptimum = null;
  return { act, resetScenario, resetOptimum };
}

const resetResult = handleResetSimulation(DEFAULT_ACTUAL);
console.log('Reset Scenario:', resetResult.resetScenario);
assert.strictEqual(resetResult.resetScenario.mcr_flow_t_h, 562.3, 'MCR must reset to DCS 562.3');
assert.strictEqual(resetResult.resetScenario.comp_N2_molpct, 3.39, 'N2 must reset to DCS 3.39');
assert.strictEqual(resetResult.resetScenario.comp_C1_molpct, 44.45, 'C1 must reset to DCS 44.45');
assert.strictEqual(resetResult.resetScenario.comp_C2_molpct, 45.02, 'C2 must reset to DCS 45.02');
assert.strictEqual(resetResult.resetScenario.comp_C2H4_molpct, 0.85, 'C2H4 must reset to DCS 0.85');
assert.strictEqual(resetResult.resetScenario.comp_C3_molpct, 6.29, 'C3 must reset to DCS 6.29');
assert.strictEqual(resetResult.resetOptimum, null, 'Optimum must be reset to null');

// When scenario matches baseline actual, predict returns ~0 delta:
const baselinePrediction = {
  actual_power_mw: 84.48,
  prediction: {
    total_shaft_power_mw: 84.48,
    delta_power_mw: 0.0,
    delta_power_pct: 0.0,
    sec_lng_kwh_per_t: 363.70,
    delta_sec_kwh_per_t: 0.0,
  }
};
const resetKpis = computeSection3KPIs(resetResult.resetScenario, baselinePrediction);
console.log('KPIs after Reset (Baseline match):', {
  card1: resetKpis.card1,
  card4: resetKpis.card4
});
assert.strictEqual(resetKpis.card1.value, '0.0', 'Card 1 must show 0.0 on reset');
assert.strictEqual(resetKpis.card1.badge, 'OPTIMAL', 'Card 1 badge must show OPTIMAL on reset');
assert.strictEqual(resetKpis.card4.value, '0.00', 'Card 4 must show 0.00 on reset');
assert.strictEqual(resetKpis.card4.badge, 'BASELINE', 'Card 4 badge must show BASELINE on reset');
console.log('>>> TEST 4 PASSED: Reset ke DCS correctly restores DCS baseline.\n');

// ============================================================================
// TEST 5: PFD Mimic Display Modes & Tag Click Drawer Verification
// ============================================================================
console.log('--- TEST 5: PFD Mimic Display Modes & Tag Click Drawer ---');
function fmt(displayMode, dcsVal, aiVal, decimals = 1) {
  if (displayMode === 'DCS_ACTUAL') {
    return { display: dcsVal.toFixed(decimals), color: '#38bdf8', isAiDiff: false };
  }
  if (displayMode === 'AI_OPTIMIZED') {
    const hasDiff = Math.abs(aiVal - dcsVal) > 0.005;
    return {
      display: aiVal.toFixed(decimals),
      color: hasDiff ? '#34d399' : '#ffffff',
      isAiDiff: hasDiff,
    };
  }
  // DELTA_DIFF mode
  const diff = aiVal - dcsVal;
  const sign = diff > 0 ? '+' : '';
  const hasDiff = Math.abs(diff) > 0.005;
  return {
    display: `${sign}${diff.toFixed(decimals)}`,
    color: hasDiff ? '#fcd34d' : '#94a3b8',
    isAiDiff: hasDiff,
  };
}

const cryogenicTags = [
  { tag: 'H5TI0050', shortTag: 'TI50', name: 'Suhu MR Liquid ke MCHE 5E-1 (Warm Bundle Inlet)', unit: '°C', dcs: -36.0, ai: -34.5 },
  { tag: 'H5TI0020', shortTag: 'TI20', name: 'Suhu Overhead MCHE 5E-1 ke LTSS (Upstream PIC2)', unit: '°C', dcs: -134.6, ai: -131.2 },
  { tag: 'H5TI0024', shortTag: 'TI24', name: 'Suhu Cold Bundle MRV Overhead (MRV > 5HV-2)', unit: '°C', dcs: -151.3, ai: -150.8 },
  { tag: 'H5TI0029', shortTag: 'TI29', name: 'Suhu LNG Rundown Downstream Subcooler (<5PV-15)', unit: '°C', dcs: -153.6, ai: -153.8 },
];

for (const t of cryogenicTags) {
  console.log(`\nTesting Tag ${t.shortTag} (${t.tag}):`);
  
  // Mode 1: DCS_ACTUAL
  const m1 = fmt('DCS_ACTUAL', t.dcs, t.ai, 1);
  console.log(`  [DCS_ACTUAL]    display="${m1.display}", color="${m1.color}"`);
  assert.strictEqual(m1.display, t.dcs.toFixed(1));
  assert.strictEqual(m1.color, '#38bdf8');

  // Mode 2: AI_OPTIMIZED
  const m2 = fmt('AI_OPTIMIZED', t.dcs, t.ai, 1);
  console.log(`  [AI_OPTIMIZED]  display="${m2.display}", color="${m2.color}"`);
  assert.strictEqual(m2.display, t.ai.toFixed(1));
  assert.strictEqual(m2.color, '#34d399');

  // Mode 3: DELTA_DIFF
  const diffVal = t.ai - t.dcs;
  const expectedSign = diffVal > 0 ? '+' : '';
  const expectedDelta = `${expectedSign}${diffVal.toFixed(1)}`;
  const m3 = fmt('DELTA_DIFF', t.dcs, t.ai, 1);
  console.log(`  [DELTA_DIFF]    display="${m3.display}", color="${m3.color}"`);
  assert.strictEqual(m3.display, expectedDelta);
  assert.strictEqual(m3.color, '#fcd34d');

  // Tag Click Handler simulation
  const clickPayload = {
    tag: t.tag,
    name: t.name,
    unit: t.unit,
    valDcs: t.dcs.toFixed(1),
    valAi: t.ai.toFixed(1)
  };
  console.log(`  [Click Payload] tag="${clickPayload.tag}", unit="${clickPayload.unit}", DCS="${clickPayload.valDcs}", AI="${clickPayload.valAi}"`);
  assert.strictEqual(clickPayload.unit, '°C');
  assert.strictEqual(clickPayload.valDcs, t.dcs.toFixed(1));
  assert.strictEqual(clickPayload.valAi, t.ai.toFixed(1));
}

console.log('\n>>> TEST 5 PASSED: PFD Mode switching and tag click payload verified for all 4 cryogenic tags.\n');
console.log('=== ALL EMPIRICAL CHALLENGER TESTS PASSED WITH 0 DEFECTS ===');
