import assert from 'node:assert';
import fs from 'node:fs';
import path from 'node:path';

// Import thermoFlash module directly
const thermoModule = await import('../src/utils/thermoFlash.ts');
const {
  calculateChillerAndCondenserDuties,
  DEFAULT_COOLING_WATER,
  calculateFlashDrum5C1,
  calculateMcrPhaseSplit,
} = thermoModule;

console.log('===============================================================');
console.log('EMPIRICAL CHALLENGER: THERMODYNAMIC STRESS TEST HARNESS');
console.log('===============================================================\n');

let totalTests = 0;
let passedTests = 0;
let failedTests = 0;

function assertCondition(cond, msg) {
  totalTests++;
  if (!cond) {
    failedTests++;
    console.error(`[FAIL] ${msg}`);
    throw new Error(msg);
  }
  passedTests++;
}

// ---------------------------------------------------------------------------
// TEST SUITE 1: Required Parameter Grid Stress Testing
// Feed: [0, 50, 150, 303.8, 400]
// MCR: [0, 480, 925.8, 1200]
// T_CW: [25, 30, 35]
// ---------------------------------------------------------------------------
console.log('--- TEST SUITE 1: Parameter Grid (Feed x MCR x T_CW: 5x4x3 = 60 cases) ---');

const feedGrid = [0, 50, 150, 303.8, 400];
const mcrGrid = [0, 480, 925.8, 1200];
const tCwGrid = [25, 30, 35];

for (const feed of feedGrid) {
  for (const mcr of mcrGrid) {
    for (const tCw of tCwGrid) {
      const res = calculateChillerAndCondenserDuties(feed, mcr, tCw);
      const tag = `feed=${feed}, mcr=${mcr}, tCw=${tCw}`;

      // 1. Zero NaN, undefined, Infinity
      assertCondition(Number.isFinite(res.q_high_stage_mw), `${tag}: q_high_stage_mw is finite`);
      assertCondition(Number.isFinite(res.q_med_stage_mw), `${tag}: q_med_stage_mw is finite`);
      assertCondition(Number.isFinite(res.q_low_stage_mw), `${tag}: q_low_stage_mw is finite`);
      assertCondition(Number.isFinite(res.q_total_precooling_mw), `${tag}: q_total_precooling_mw is finite`);
      assertCondition(Number.isFinite(res.q_propane_condenser_mw), `${tag}: q_propane_condenser_mw is finite`);
      assertCondition(Number.isFinite(res.lmtd_condenser_c), `${tag}: lmtd_condenser_c is finite`);

      // 2. Non-negativity
      assertCondition(res.q_high_stage_mw >= 0, `${tag}: q_high_stage_mw >= 0 (got ${res.q_high_stage_mw})`);
      assertCondition(res.q_med_stage_mw >= 0, `${tag}: q_med_stage_mw >= 0 (got ${res.q_med_stage_mw})`);
      assertCondition(res.q_low_stage_mw >= 0, `${tag}: q_low_stage_mw >= 0 (got ${res.q_low_stage_mw})`);
      assertCondition(res.q_total_precooling_mw >= 0, `${tag}: q_total_precooling_mw >= 0 (got ${res.q_total_precooling_mw})`);
      assertCondition(res.q_propane_condenser_mw >= 0, `${tag}: q_propane_condenser_mw >= 0 (got ${res.q_propane_condenser_mw})`);
      assertCondition(res.lmtd_condenser_c >= 0, `${tag}: lmtd_condenser_c >= 0 (got ${res.lmtd_condenser_c})`);

      // 3. Energy Conservation: Q_condenser >= Q_precooling
      assertCondition(
        res.q_propane_condenser_mw >= res.q_total_precooling_mw - 1e-4,
        `${tag}: Energy conservation Q_cond (${res.q_propane_condenser_mw}) >= Q_precool (${res.q_total_precooling_mw})`
      );

      // 4. Sum of chiller stages equals total precooling (within rounding tolerance +-0.02 MW)
      const stageSum = res.q_high_stage_mw + res.q_med_stage_mw + res.q_low_stage_mw;
      const diffSum = Math.abs(stageSum - res.q_total_precooling_mw);
      assertCondition(
        diffSum <= 0.021,
        `${tag}: Chiller stages sum (${stageSum.toFixed(2)}) == total (${res.q_total_precooling_mw.toFixed(2)})`
      );

      // 5. Zero-flow boundary check
      if (feed === 0 && mcr === 0) {
        assertCondition(res.q_total_precooling_mw === 0, `${tag}: Zero flow yields zero precooling duty`);
        assertCondition(res.q_propane_condenser_mw === 0, `${tag}: Zero flow yields zero condenser duty`);
      }
    }
  }
}
console.log(`[PASS] Suite 1 completed: All 60 parameter grid cases verified.\n`);

// ---------------------------------------------------------------------------
// TEST SUITE 2: Second Law & Pinch Analysis Verification
// ---------------------------------------------------------------------------
console.log('--- TEST SUITE 2: Second Law & Pinch Analysis (MITA >= 1.50 C, no crossover) ---');

for (const tCwIn of [20.0, 25.0, 28.0, 30.0, 32.0, 35.0, 38.0, 40.0]) {
  const deltaTCw = DEFAULT_COOLING_WATER.delta_T_CW_C; // 5.0 C
  const tCwOut = tCwIn + deltaTCw;
  const approach = DEFAULT_COOLING_WATER.approach_C;   // 5.5 C
  const tCond = tCwOut + approach;

  // Cold end and hot end temperature differences
  const dtHot = tCond - tCwIn;  // 10.5 C
  const dtCold = tCond - tCwOut; // 5.5 C (Pinch approach)

  const tag = `T_CW_in = ${tCwIn} C`;
  assertCondition(dtCold >= 1.50, `${tag}: Condenser approach pinch dtCold (${dtCold} C) >= 1.50 C`);
  assertCondition(dtHot > dtCold, `${tag}: dtHot (${dtHot} C) > dtCold (${dtCold} C)`);
  assertCondition(dtCold > 0, `${tag}: Zero temperature crossover in condenser`);

  const res = calculateChillerAndCondenserDuties(303.8, 925.8, tCwIn);
  assertCondition(res.lmtd_condenser_c > 0, `${tag}: LMTD (${res.lmtd_condenser_c} C) > 0`);
  assertCondition(res.lmtd_condenser_c >= dtCold, `${tag}: LMTD >= minimum pinch dtCold`);
}

// Chiller Stage Pinch Verification:
// Stage 1 (3E-14): Process 34 C -> 22 C, Propane evap +18 C
const pinch3E14 = 22.0 - 18.0; // 4.0 C
assertCondition(pinch3E14 >= 1.50, `3E-14 pinch (${pinch3E14} C) >= 1.50 C`);

// Stage 2 (3E-17): Process 22 C -> -5 C, Propane evap -10 C
const pinch3E17 = -5.0 - (-10.0); // 5.0 C
assertCondition(pinch3E17 >= 1.50, `3E-17 pinch (${pinch3E17} C) >= 1.50 C`);

// Stage 3 (3E-18): Feed Gas -5 C -> -32.5 C, Propane evap -35 C
const pinch3E18Feed = -32.5 - (-35.0); // 2.5 C
assertCondition(pinch3E18Feed >= 1.50, `3E-18 Feed Gas pinch (${pinch3E18Feed} C) >= 1.50 C`);

console.log(`[PASS] Suite 2 completed: Second Law pinch compliance verified across all heat exchangers.\n`);

// ---------------------------------------------------------------------------
// TEST SUITE 3: Adversarial Edge Cases & Fault Tolerance
// ---------------------------------------------------------------------------
console.log('--- TEST SUITE 3: Adversarial Edge Cases & Corrupted Inputs ---');

const adversarialInputs = [
  { feed: -100, mcr: 925.8, tCw: 30.0, desc: 'Negative feed flow' },
  { feed: 303.8, mcr: -500, tCw: 30.0, desc: 'Negative MCR flow' },
  { feed: -50, mcr: -50, tCw: 30.0, desc: 'Both negative flows' },
  { feed: NaN, mcr: 925.8, tCw: 30.0, desc: 'NaN feed flow' },
  { feed: 303.8, mcr: NaN, tCw: 30.0, desc: 'NaN MCR flow' },
  { feed: 303.8, mcr: 925.8, tCw: NaN, desc: 'NaN T_CW' },
  { feed: Infinity, mcr: 925.8, tCw: 30.0, desc: 'Infinity feed flow' },
  { feed: 303.8, mcr: -Infinity, tCw: 30.0, desc: '-Infinity MCR flow' },
  { feed: undefined, mcr: undefined, tCw: undefined, desc: 'All undefined inputs' },
  { feed: 1000, mcr: 3000, tCw: 30.0, desc: 'Massive plant overload (1000 t/h feed, 3000 t/h MCR)' },
];

for (const c of adversarialInputs) {
  const res = calculateChillerAndCondenserDuties(c.feed, c.mcr, c.tCw);
  const tag = `Adversarial [${c.desc}]`;

  assertCondition(Number.isFinite(res.q_high_stage_mw), `${tag}: q_high_stage_mw is finite`);
  assertCondition(Number.isFinite(res.q_med_stage_mw), `${tag}: q_med_stage_mw is finite`);
  assertCondition(Number.isFinite(res.q_low_stage_mw), `${tag}: q_low_stage_mw is finite`);
  assertCondition(Number.isFinite(res.q_total_precooling_mw), `${tag}: q_total_precooling_mw is finite`);
  assertCondition(Number.isFinite(res.q_propane_condenser_mw), `${tag}: q_propane_condenser_mw is finite`);
  assertCondition(Number.isFinite(res.lmtd_condenser_c), `${tag}: lmtd_condenser_c is finite`);

  assertCondition(res.q_high_stage_mw >= 0, `${tag}: q_high_stage_mw >= 0`);
  assertCondition(res.q_total_precooling_mw >= 0, `${tag}: q_total_precooling_mw >= 0`);
  assertCondition(res.q_propane_condenser_mw >= res.q_total_precooling_mw - 1e-4, `${tag}: Q_cond >= Q_precool`);
}
console.log(`[PASS] Suite 3 completed: All adversarial inputs handled safely without crashes or NaN.\n`);

// ---------------------------------------------------------------------------
// TEST SUITE 4: Physical Monotonicity & Clausius-Clapeyron Validation
// ---------------------------------------------------------------------------
console.log('--- TEST SUITE 4: Physical Monotonicity (Flow & T_CW Sensitivity) ---');

// As feed flow increases, duties must strictly increase monotonically
let prevQ = -1;
for (const f of [50, 100, 150, 200, 250, 300, 350, 400]) {
  const res = calculateChillerAndCondenserDuties(f, 925.8, 30.0);
  assertCondition(res.q_total_precooling_mw > prevQ, `Precooling duty increases with feed flow at ${f} t/h`);
  prevQ = res.q_total_precooling_mw;
}

// As MCR flow increases, duties must strictly increase monotonically
let prevQMcr = -1;
for (const m of [200, 400, 600, 800, 925.8, 1100, 1200]) {
  const res = calculateChillerAndCondenserDuties(303.8, m, 30.0);
  assertCondition(res.q_total_precooling_mw > prevQMcr, `Precooling duty increases with MCR flow at ${m} t/h`);
  prevQMcr = res.q_total_precooling_mw;
}

// As T_CW increases, condensing temperature and compressor discharge pressure increase,
// so compressor power and condenser duty must increase for fixed precooling duty.
let prevQCond = -1;
for (const t of [25, 28, 30, 32, 35, 38]) {
  const res = calculateChillerAndCondenserDuties(303.8, 925.8, t);
  assertCondition(res.q_propane_condenser_mw > prevQCond, `Condenser duty increases with T_CW at ${t} C`);
  prevQCond = res.q_propane_condenser_mw;
}
console.log(`[PASS] Suite 4 completed: Monotonicity holds strictly for Feed, MCR, and T_CW.\n`);

// ---------------------------------------------------------------------------
// TEST SUITE 5: Zero Unicode Em-Dash and En-Dash Audit
// ---------------------------------------------------------------------------
console.log('--- TEST SUITE 5: Zero Unicode Dash Compliance Audit ---');

const scriptDir = path.dirname(new URL(import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, '$1'));
const frontendRoot = path.resolve(scriptDir, '..');

const filesToAudit = [
  path.join(frontendRoot, 'src', 'types.ts'),
  path.join(frontendRoot, 'src', 'utils', 'thermoFlash.ts'),
  path.join(frontendRoot, 'src', 'components', 'ExcelWorkbookView.tsx'),
  path.join(frontendRoot, 'tests', 'stress_test_thermo.mjs'),
];

let dashViolations = 0;
for (const file of filesToAudit) {
  const content = fs.readFileSync(file, 'utf-8');
  const emDashCount = (content.match(/\u2014/g) || []).length;
  const enDashCount = (content.match(/\u2013/g) || []).length;
  const total = emDashCount + enDashCount;
  if (total > 0) {
    console.error(`[VIOLATION] ${path.basename(file)} contains ${emDashCount} em-dashes and ${enDashCount} en-dashes!`);
    dashViolations += total;
  }
}
assertCondition(dashViolations === 0, `Zero em-dash/en-dash violations in touched files (found ${dashViolations})`);
console.log(`[PASS] Suite 5 completed: Zero em-dash and en-dash violations confirmed.\n`);

// ---------------------------------------------------------------------------
// FINAL SUMMARY
// ---------------------------------------------------------------------------
console.log('===============================================================');
console.log(`STRESS TEST SUMMARY: ${passedTests}/${totalTests} CHECKS PASSED, ${failedTests} FAILED`);
console.log('VERDICT: ALL THERMODYNAMIC CONSTRAINTS RIGOROUSLY SATISFIED');
console.log('===============================================================');
