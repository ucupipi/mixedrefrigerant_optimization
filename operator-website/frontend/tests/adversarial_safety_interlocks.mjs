// Adversarial Safety & Interlocks Verification Harness
// Target: operator-website/frontend/src/utils/physicsEngine.ts
// Strict Zero em-dash (U+2014) and Zero en-dash (U+2013) compliance.

import assert from 'node:assert';
import {
  validateOperatingPoint,
  computeClientPrediction,
  ANTISURGE_FLOW_FLOOR_T_H,
  SUCTION_TAL_DEG_C,
  SUCTION_TALL_DEG_C,
  MITA_MIN_PINCH_C,
} from '../src/utils/physicsEngine.ts';

console.log('===============================================================');
console.log('EMPIRICAL CHALLENGER: ADVERSARIAL SAFETY & INTERLOCKS HARNESS');
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

// ---------------------------------------------------------------------------
// SUITE 1: Suction Drum TAL & TALL Interlock Verification
// ---------------------------------------------------------------------------
console.log('\n--- SUITE 1: Suction Drum TAL & TALL Interlock Verification ---');

// Constant verification
check(SUCTION_TAL_DEG_C === -45.0, 'SUCTION_TAL_DEG_C constant is exactly -45.0 C');
check(SUCTION_TALL_DEG_C === -51.0, 'SUCTION_TALL_DEG_C constant is exactly -51.0 C');

// 1.1 Safe operating points
{
  const res = validateOperatingPoint({ feed_flow_t_h: 250, mcr_flow_t_h: 560, H4TI004B: -40.5 });
  const hasTal = res.violations.some((v) => v.includes('TAL') || v.includes('4TV-510'));
  const hasTall = res.violations.some((v) => v.includes('TALL'));
  check(!hasTal && !hasTall, 'Suction temp -40.5 C triggers no TAL/TALL violations');
}
{
  const res = validateOperatingPoint({ feed_flow_t_h: 250, mcr_flow_t_h: 560, H4TI004B: -44.9 });
  const hasTal = res.violations.some((v) => v.includes('TAL') || v.includes('4TV-510'));
  check(!hasTal, 'Suction temp -44.9 C is above -45.0 C and triggers no TAL');
}

// 1.2 Boundary point: exactly -45.0 C
{
  const res = validateOperatingPoint({ feed_flow_t_h: 250, mcr_flow_t_h: 560, H4TI004B: -45.0 });
  const hasTal = res.violations.some((v) => v.includes('TAL') && v.includes('4TV-510'));
  check(hasTal, 'Suction temp -45.0 C triggers TAL alarm and mentions reheat valve 4TV-510');
  check(res.all_safe === false, 'all_safe is false when TAL is violated');
}

// 1.3 Alarm zone: -45.1 C and -48.0 C
{
  const res = validateOperatingPoint({ feed_flow_t_h: 250, mcr_flow_t_h: 560, H4TI004B: -45.1 });
  const hasTal = res.violations.some((v) => v.includes('TAL') && v.includes('4TV-510'));
  check(hasTal, 'Suction temp -45.1 C triggers TAL alarm');
  check(res.all_safe === false, 'all_safe is false at -45.1 C');
}
{
  const res = validateOperatingPoint({ feed_flow_t_h: 250, mcr_flow_t_h: 560, t_suct_4c8_c: -48.0 });
  const hasTal = res.violations.some((v) => v.includes('TAL') && v.includes('4TV-510'));
  check(hasTal, 'Suction temp -48.0 C via t_suct_4c8_c triggers TAL alarm');
}

// 1.4 Trip zone: -51.0 C and below (TALL)
{
  const res = validateOperatingPoint({ feed_flow_t_h: 250, mcr_flow_t_h: 560, H4TI004B: -51.0 });
  const hasTall = res.violations.some((v) => v.includes('TALL') && v.includes('trip darurat'));
  check(hasTall, 'Suction temp -51.0 C triggers emergency trip TALL');
  check(res.all_safe === false, 'all_safe is false at -51.0 C');
}
{
  const res = validateOperatingPoint({ feed_flow_t_h: 250, mcr_flow_t_h: 560, H4TI004B: -55.0 });
  const hasTall = res.violations.some((v) => v.includes('TALL') && v.includes('trip darurat'));
  check(hasTall, 'Suction temp -55.0 C triggers emergency trip TALL');
}

// 1.5 Full predict response verification for TAL
{
  const pred = computeClientPrediction({ feed_flow_t_h: 250, mcr_flow_t_h: 560, H4TI004B: -47.0 });
  check(pred.safety_check.all_safe === false, 'computeClientPrediction reflects all_safe = false on TAL');
  check(
    pred.safety_check.status_label === 'Skenario Ditolak (Pelanggaran Batas Keselamatan)',
    'Status label indicates scenario rejected on TAL violation'
  );
  check(
    pred.safety_check.violations.some((v) => v.includes('4TV-510')),
    'Violations list in PredictResponse includes 4TV-510 directive'
  );
}

// ---------------------------------------------------------------------------
// SUITE 2: Anti-Surge Flow Floor (480.0 t/h) & 4UV-53 Kickback Verification
// ---------------------------------------------------------------------------
console.log('\n--- SUITE 2: Anti-Surge Flow Floor (480.0 t/h) & Kickback Verification ---');

// Constant verification
check(ANTISURGE_FLOW_FLOOR_T_H === 480.0, 'ANTISURGE_FLOW_FLOOR_T_H constant is exactly 480.0 t/h');

// 2.1 Safe operating points
{
  const res = validateOperatingPoint({ feed_flow_t_h: 250, mcr_flow_t_h: 560.0 });
  const hasSurge = res.violations.some((v) => v.includes('anti-surge') || v.includes('4UV-53'));
  check(!hasSurge, 'MCR flow 560.0 t/h triggers no anti-surge violation');
}
{
  const res = validateOperatingPoint({ feed_flow_t_h: 250, mcr_flow_t_h: 480.0 });
  const hasSurge = res.violations.some((v) => v.includes('anti-surge') || v.includes('4UV-53'));
  check(!hasSurge, 'MCR flow exactly 480.0 t/h is at flow floor and triggers no violation');
}

// 2.2 Violation points below 480.0 t/h
{
  const res = validateOperatingPoint({ feed_flow_t_h: 250, mcr_flow_t_h: 479.9 });
  const hasSurge = res.violations.some(
    (v) => v.includes('anti-surge') && v.includes('4UV-53') && v.includes('480.0')
  );
  check(hasSurge, 'MCR flow 479.9 t/h triggers anti-surge violation and mandates kickback 4UV-53');
  check(res.all_safe === false, 'all_safe is false when MCR flow < 480.0 t/h');
}
{
  const res = validateOperatingPoint({ feed_flow_t_h: 250, mcr_flow_t_h: 350.0 });
  const hasSurge = res.violations.some((v) => v.includes('4UV-53'));
  check(hasSurge, 'MCR flow 350.0 t/h triggers kickback 4UV-53 violation');
}
{
  const res = validateOperatingPoint({ feed_flow_t_h: 250, mcr_flow_t_h: 0.0 });
  const hasSurge = res.violations.some((v) => v.includes('4UV-53'));
  check(hasSurge, 'MCR flow 0.0 t/h triggers kickback 4UV-53 violation');
}

// 2.3 Full predict response verification for Anti-Surge
{
  const pred = computeClientPrediction({ feed_flow_t_h: 250, mcr_flow_t_h: 450.0 });
  check(pred.safety_check.all_safe === false, 'computeClientPrediction reflects all_safe = false on surge flow');
  check(
    pred.safety_check.violations.some((v) => v.includes('4UV-53')),
    'Violations list in PredictResponse includes 4UV-53 kickback command'
  );
}

// ---------------------------------------------------------------------------
// SUITE 3: MITA Minimum Temperature Approach (MITA >= 1.50 C) Verification
// ---------------------------------------------------------------------------
console.log('\n--- SUITE 3: MITA Minimum Temperature Approach Verification ---');

// Constant verification
check(MITA_MIN_PINCH_C === 1.50, 'MITA_MIN_PINCH_C constant is exactly 1.50 C');

// 3.1 Safe operating points
{
  const res = validateOperatingPoint({ feed_flow_t_h: 250, mcr_flow_t_h: 560, mita_pinch_c: 2.50 });
  const hasMita = res.violations.some((v) => v.includes('MITA'));
  check(!hasMita, 'MITA 2.50 C triggers no pinch violation');
}
{
  const res = validateOperatingPoint({ feed_flow_t_h: 250, mcr_flow_t_h: 560, mita_pinch_c: 1.50 });
  const hasMita = res.violations.some((v) => v.includes('MITA'));
  check(!hasMita, 'MITA exactly 1.50 C is at boundary and triggers no violation');
}

// 3.2 Violation points below 1.50 C
{
  const res = validateOperatingPoint({ feed_flow_t_h: 250, mcr_flow_t_h: 560, mita_pinch_c: 1.49 });
  const hasMita = res.violations.some(
    (v) => v.includes('MITA') && v.includes('temperature crossover') && v.includes('1.50')
  );
  check(hasMita, 'MITA 1.49 C triggers MITA violation and warns of temperature crossover');
  check(res.all_safe === false, 'all_safe is false when MITA < 1.50 C');
}
{
  const res = validateOperatingPoint({ feed_flow_t_h: 250, mcr_flow_t_h: 560, mita_pinch_c: 0.0 });
  const hasMita = res.violations.some((v) => v.includes('temperature crossover'));
  check(hasMita, 'MITA 0.0 C (zero pinch) triggers crossover violation');
}
{
  const res = validateOperatingPoint({ feed_flow_t_h: 250, mcr_flow_t_h: 560, mita_pinch_c: -1.2 });
  const hasMita = res.violations.some((v) => v.includes('temperature crossover'));
  check(hasMita, 'MITA -1.2 C (negative pinch) triggers crossover violation');
}

// 3.3 Full predict response verification for MITA
{
  const pred = computeClientPrediction({ feed_flow_t_h: 250, mcr_flow_t_h: 560, mita_pinch_c: 1.20 });
  check(pred.safety_check.all_safe === false, 'computeClientPrediction reflects all_safe = false on pinch violation');
  check(
    pred.safety_check.violations.some((v) => v.includes('MITA')),
    'Violations list in PredictResponse includes MITA violation message'
  );
}

// ---------------------------------------------------------------------------
// SUITE 4: Combined Multi-Interlock Stress Testing
// ---------------------------------------------------------------------------
console.log('\n--- SUITE 4: Combined Multi-Interlock Stress Testing ---');

{
  // Triple violation: TAL + Flow Floor + MITA Pinch
  const res = validateOperatingPoint({
    feed_flow_t_h: 250,
    mcr_flow_t_h: 420.0,    // Flow floor violation
    H4TI004B: -46.5,        // TAL violation
    mita_pinch_c: 0.85,     // MITA violation
  });

  check(res.all_safe === false, 'Triple fault: all_safe is false');
  check(res.violations.length >= 3, `Triple fault: at least 3 violations recorded (got ${res.violations.length})`);
  const hasTal = res.violations.some((v) => v.includes('TAL'));
  const hasSurge = res.violations.some((v) => v.includes('4UV-53'));
  const hasMita = res.violations.some((v) => v.includes('MITA'));
  check(hasTal, 'Triple fault: TAL violation is present');
  check(hasSurge, 'Triple fault: 4UV-53 surge violation is present');
  check(hasMita, 'Triple fault: MITA pinch violation is present');
}

// ---------------------------------------------------------------------------
// SUITE 5: Default Snapshot Operating Point Safety Audit
// ---------------------------------------------------------------------------
console.log('\n--- SUITE 5: Default Snapshot Operating Point Safety Audit ---');

const defaultSnap = await import('../src/data/defaultSnapshot.ts');
const snapshot = defaultSnap.DEFAULT_DEMO_SNAPSHOT;

check(snapshot !== undefined, 'DEFAULT_DEMO_SNAPSHOT is exported and loaded');
check(
  snapshot.values.H4FI001.value >= 480.0,
  `Default DCS MCR flow (${snapshot.values.H4FI001.value} t/h) >= 480.0 t/h`
);
check(
  snapshot.values.H4TI004B.value >= -45.0,
  `Default DCS suction temp (${snapshot.values.H4TI004B.value} C) >= -45.0 C`
);

// Map snapshot values to scenario inputs and run through client prediction
const actualDcs = {
  feed_flow_t_h: snapshot.values.H1FI012.value,
  mcr_flow_t_h: snapshot.values.H4FI001.value,
  comp_N2_molpct: snapshot.values.comp_N2.value,
  comp_C1_molpct: snapshot.values.comp_C1.value,
  comp_C2_molpct: snapshot.values.comp_C2.value,
  comp_C2H4_molpct: snapshot.values.comp_C2H4.value,
  comp_C3_molpct: snapshot.values.comp_C3.value,
  lng_flow_t_h: snapshot.values.H5FI006A?.value,
};
const predDefault = computeClientPrediction(actualDcs, actualDcs);
check(predDefault.safety_check.all_safe === true, 'Default snapshot scenario passes all safety interlocks');
check(
  predDefault.safety_check.status_label === 'Semua kendala yang diperiksa terpenuhi',
  `Default scenario status: "${predDefault.safety_check.status_label}"`
);

console.log('\n===============================================================');
console.log(`STRESS TEST SUMMARY: ${passedChecks}/${totalChecks} CHECKS PASSED, 0 FAILED.`);
console.log('===============================================================\n');
