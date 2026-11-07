// Adversarial API Standalone Offline Fallback Verification
// Target: operator-website/frontend/src/api.ts
// Strict Zero em-dash (U+2014) and Zero en-dash (U+2013) compliance.

import assert from 'node:assert';
import {
  fetchSystemStatus,
  fetchDemoSnapshot,
  fetchHistoricalSummary,
  predictScenario,
  computeFrontendRecommendation,
  optimizeForFeed,
} from '../src/api.ts';

console.log('===============================================================');
console.log('EMPIRICAL CHALLENGER: API STANDALONE FALLBACK HARNESS');
console.log('===============================================================\n');

let totalChecks = 0;
let passedChecks = 0;

function check(condition, message) {
  totalChecks++;
  if (!condition) {
    console.error(`[FAIL] ${message}`);
    throw new Error(`Assertion failed: ${message}`);
  }
  passedChecks++;
  console.log(`[PASS] ${message}`);
}

// 1. fetchSystemStatus fallback
const status = await fetchSystemStatus();
check(status.status === 'healthy', 'fetchSystemStatus returns healthy status offline');
check(status.mode === 'standalone-hybrid', 'fetchSystemStatus returns standalone-hybrid mode');

// 2. fetchDemoSnapshot fallback
const snap = await fetchDemoSnapshot();
check(snap.source_mode === 'DEMO', 'fetchDemoSnapshot returns DEMO snapshot offline');
check(snap.values.H1FI012.value === 245.8, 'Default snapshot has H1FI012 = 245.8 t/h');
check(snap.values.H4FI001.value === 562.3, 'Default snapshot has H4FI001 = 562.3 t/h');

// 3. fetchHistoricalSummary fallback
const hist = await fetchHistoricalSummary();
check(Array.isArray(hist.regime_points), 'Historical summary contains regime_points array');
check(hist.regime_points.length === 9, 'Historical summary has 9 calibrated regime points');

// 4. predictScenario offline fallback
const pred = await predictScenario({
  feed_flow_t_h: 245.8,
  mcr_flow_t_h: 562.3,
  comp_N2_molpct: 3.38,
  comp_C1_molpct: 44.37,
  comp_C2_molpct: 44.94,
  comp_C2H4_molpct: 0.85,
  comp_C3_molpct: 6.28,
});
check(typeof pred.prediction.total_shaft_power_mw === 'number', 'predictScenario returns power prediction offline');
check(pred.prediction.total_shaft_power_mw > 40 && pred.prediction.total_shaft_power_mw < 150, 'Power prediction is in valid range [40, 150] MW');
check(pred.safety_check.all_safe === true, 'Safe scenario has all_safe === true');

// 5. computeFrontendRecommendation anti-surge floor
const recUnderload = computeFrontendRecommendation(120.0);
check(recUnderload.mcr_flow_t_h >= 480.0, 'Recommendation at 120 t/h enforces flow floor >= 480.0 t/h');
check(recUnderload.antisurge_floor_applied === true, 'antisurge_floor_applied flag is true');
check(recUnderload.suction_tal_ok === true, 'suction_tal_ok flag is true');

// 6. optimizeForFeed offline fallback
const opt = await optimizeForFeed(250.0);
check(opt.mcr_flow_t_h >= 480.0, 'optimizeForFeed offline fallback returns valid recommendation');
check(opt.solver_converged === true, 'optimizeForFeed reports solver_converged = true');

console.log('\n===============================================================');
console.log(`API OFFLINE SUMMARY: ${passedChecks}/${totalChecks} CHECKS PASSED, 0 FAILED.`);
console.log('===============================================================\n');
