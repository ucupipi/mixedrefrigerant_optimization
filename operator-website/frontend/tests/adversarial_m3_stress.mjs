// Adversarial Concurrency, Degenerate Input & Multi-Strategy Stress Harness
// Milestone 3 Challenger Verification
// Strict Zero em-dash (U+2014) and Zero en-dash (U+2013) compliance.

import assert from 'node:assert';
import {
  predictScenario,
  optimizeForFeed,
  computeFrontendRecommendation,
  calculateMakeupAdvisory,
} from '../src/api.ts';
import {
  ANTISURGE_FLOW_FLOOR_T_H,
  SUCTION_TAL_DEG_C,
  CHI2_CRITICAL_5COMP,
  enforceSimplexClosure,
} from '../src/utils/physicsEngine.ts';

console.log('====================================================================');
console.log('CHALLENGER M3-1: ADVERSARIAL CONCURRENCY & DEGENERATE STRESS HARNESS');
console.log('====================================================================\n');

let totalChecks = 0;
let passedChecks = 0;
let failedChecks = 0;
const findings = [];

function check(condition, message) {
  totalChecks++;
  if (condition) {
    passedChecks++;
    console.log(`[PASS] ${message}`);
  } else {
    failedChecks++;
    console.error(`[FAIL] ${message}`);
    findings.push(message);
  }
}

// ---------------------------------------------------------------------------
// SUITE 1: Concurrency & Request Cancellation (predictScenario & optimizeForFeed)
// ---------------------------------------------------------------------------
console.log('\n--- SUITE 1: Rapid Concurrency & Request Cancellation (predictScenario) ---');

async function testPredictScenarioConcurrency() {
  const originalFetch = globalThis.fetch;
  const callLog = [];
  const abortSignals = [];

  // Mock global fetch to simulate network delays and track AbortSignal
  globalThis.fetch = async (url, options = {}) => {
    const body = options.body ? JSON.parse(options.body) : {};
    const feed = body.feed_flow_t_h ?? 250;
    const callId = body.callId ?? feed;
    const signal = options.signal;

    abortSignals.push({ callId, signal });

    // Determine delay based on callId (Call 1 slow, Call 5 fast)
    let delayMs = 120;
    if (callId === 1) delayMs = 150;
    if (callId === 2) delayMs = 100;
    if (callId === 3) delayMs = 80;
    if (callId === 4) delayMs = 60;
    if (callId === 5) delayMs = 25;

    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        if (signal?.aborted) {
          const err = new Error('The operation was aborted');
          err.name = 'AbortError';
          reject(err);
        } else {
          callLog.push({ callId, feed, status: 'resolved' });
          resolve({
            ok: true,
            status: 200,
            json: async () => ({
              callId,
              feed_flow_t_h: feed,
              prediction: { total_shaft_power_mw: 80.0 + callId },
              source: `Mock Backend Response for Call ${callId}`,
            }),
          });
        }
      }, delayMs);

      if (signal) {
        signal.addEventListener('abort', () => {
          clearTimeout(timer);
          callLog.push({ callId, feed, status: 'aborted' });
          const err = new Error('The operation was aborted');
          err.name = 'AbortError';
          reject(err);
        });
      }
    });
  };

  try {
    const promises = [];
    const results = [];
    const errors = [];

    // Launch 5 rapid successive calls (<20ms intervals) with varying latencies
    console.log('Dispatching 5 rapid calls to predictScenario (interval 15ms)...');
    for (let i = 1; i <= 5; i++) {
      const p = predictScenario({
        feed_flow_t_h: 150 + i * 20,
        mcr_flow_t_h: 560,
        comp_N2_molpct: 3.39,
        comp_C1_molpct: 44.45,
        comp_C2_molpct: 45.02,
        comp_C2H4_molpct: 0.85,
        comp_C3_molpct: 6.29,
        callId: i,
      })
        .then((res) => {
          results.push({ callId: i, res });
          return res;
        })
        .catch((err) => {
          errors.push({ callId: i, name: err?.name, message: err?.message });
          return { callId: i, error: err };
        });

      promises.push(p);
      await new Promise((r) => setTimeout(r, 15));
    }

    // Wait for all promises to settle
    const settled = await Promise.all(promises);

    // Verify cancellation behavior
    check(
      results.length === 1,
      `Exactly 1 call resolved successfully (got ${results.length} resolved, ${errors.length} aborted)`
    );

    check(
      errors.length === 4,
      `Exactly 4 prior calls were aborted via AbortController (got ${errors.length})`
    );

    const lastResult = results[0]?.res;
    check(
      lastResult?.callId === 5 || lastResult?.feed_flow_t_h === 250,
      `Last call (Call 5) won and resolved with latest payload (callId: ${lastResult?.callId})`
    );

    // Verify all rejected calls had AbortError
    const allAborted = errors.every((e) => e.name === 'AbortError');
    check(allAborted, 'All cancelled calls rejected specifically with AbortError');

    // Verify earlier slow calls did NOT resolve after Call 5
    const resolvedIds = callLog.filter((c) => c.status === 'resolved').map((c) => c.callId);
    check(
      resolvedIds.length === 1 && resolvedIds[0] === 5,
      `Only Call 5 resolved on network; slow earlier calls were cleanly aborted on signal`
    );
  } finally {
    globalThis.fetch = originalFetch;
  }
}

// ---------------------------------------------------------------------------
// SUITE 2: Degenerate Input Stress Testing on calculateMakeupAdvisory
// ---------------------------------------------------------------------------
console.log('\n--- SUITE 2: Degenerate Input Stress Testing (calculateMakeupAdvisory) ---');

function testMakeupAdvisoryDegenerate() {
  const normalAct = { N2: 3.39, C1: 44.45, C2: 45.02, C2H4: 0.85, C3: 6.29 };
  const normalTgt = { N2: 3.31, C1: 46.08, C2: 45.15, C2H4: 0.05, C3: 5.41 };

  const testCases = [
    {
      name: 'Empty object actual composition {}',
      args: [{}, normalTgt, 2.0, 24000.0],
    },
    {
      name: 'Empty object target composition {}',
      args: [normalAct, {}, 2.0, 24000.0],
    },
    {
      name: 'Both compositions empty objects {}',
      args: [{}, {}, 2.0, 24000.0],
    },
    {
      name: 'Null actual composition',
      args: [null, normalTgt, 2.0, 24000.0],
    },
    {
      name: 'Null target composition',
      args: [normalAct, null, 2.0, 24000.0],
    },
    {
      name: 'Undefined compositions',
      args: [undefined, undefined, 2.0, 24000.0],
    },
    {
      name: 'Non-positive loop inventory (-5000 kg)',
      args: [normalAct, normalTgt, 2.0, -5000.0],
    },
    {
      name: 'Zero loop inventory (0.0 kg)',
      args: [normalAct, normalTgt, 2.0, 0.0],
    },
    {
      name: 'NaN loop inventory',
      args: [normalAct, normalTgt, 2.0, NaN],
    },
    {
      name: 'Infinity loop inventory',
      args: [normalAct, normalTgt, 2.0, Infinity],
    },
    {
      name: 'Non-positive transition hours (-1.0 h)',
      args: [normalAct, normalTgt, -1.0, 24000.0],
    },
    {
      name: 'Zero transition hours (0.0 h)',
      args: [normalAct, normalTgt, 0.0, 24000.0],
    },
    {
      name: 'NaN transition hours',
      args: [normalAct, normalTgt, NaN, 24000.0],
    },
    {
      name: 'Missing required core component C3 in actual',
      args: [{ N2: 3.39, C1: 44.45, C2: 45.02, C2H4: 0.85 }, normalTgt, 2.0, 24000.0],
    },
    {
      name: 'Missing required core component C1 in target',
      args: [normalAct, { N2: 3.31, C2: 45.15, C2H4: 0.05, C3: 5.41 }, 2.0, 24000.0],
    },
    {
      name: 'NaN component in actual composition',
      args: [{ N2: NaN, C1: 44.45, C2: 45.02, C2H4: 0.85, C3: 6.29 }, normalTgt, 2.0, 24000.0],
    },
    {
      name: 'NaN component in target composition',
      args: [normalAct, { N2: 3.31, C1: NaN, C2: 45.15, C2H4: 0.05, C3: 5.41 }, 2.0, 24000.0],
    },
    {
      name: 'Zero total moles in actual ({ N2:0, C1:0, C2:0, C3:0 })',
      args: [{ N2: 0, C1: 0, C2: 0, C2H4: 0, C3: 0 }, normalTgt, 2.0, 24000.0],
    },
    {
      name: 'Zero total moles in target ({ N2:0, C1:0, C2:0, C3:0 })',
      args: [normalAct, { N2: 0, C1: 0, C2: 0, C2H4: 0, C3: 0 }, 2.0, 24000.0],
    },
    {
      name: 'Total mole sum outside physical lower limit (<10 mol%)',
      args: [{ N2: 1.0, C1: 2.0, C2: 1.0, C2H4: 0.0, C3: 1.0 }, normalTgt, 2.0, 24000.0],
    },
    {
      name: 'Total mole sum outside physical upper limit (>150 mol%)',
      args: [{ N2: 50.0, C1: 50.0, C2: 50.0, C2H4: 10.0, C3: 50.0 }, normalTgt, 2.0, 24000.0],
    },
  ];

  for (const tc of testCases) {
    let res;
    let threw = false;
    try {
      res = calculateMakeupAdvisory(...tc.args);
    } catch (e) {
      threw = true;
      console.error(`Unexpected exception thrown for: ${tc.name}`, e);
    }

    check(!threw, `No exception thrown for: ${tc.name}`);
    check(res?.status === 'NOT EVALUATED', `Returns status: 'NOT EVALUATED' for: ${tc.name}`);
    check(res?.total_makeup_flow_nm3_h === null, `Returns total_makeup_flow_nm3_h === null for: ${tc.name}`);
    check(res?.total_makeup_flow_kg_h === null, `Returns total_makeup_flow_kg_h === null for: ${tc.name}`);
    check(res?.total_makeup_flow_scfd === null, `Returns total_makeup_flow_scfd === null for: ${tc.name}`);

    // Verify all item flows are null and have clear action
    const items = res?.items || [];
    const allItemsNull = items.every(
      (it) =>
        it.recommended_flow_nm3_h === null &&
        it.recommended_flow_kg_h === null &&
        it.actual_molpct === null &&
        it.action === 'TIDAK DAPAT DIEVALUASI'
    );
    check(allItemsNull, `All 4 controller items have null flows and advisory action for: ${tc.name}`);
  }
}

// ---------------------------------------------------------------------------
// SUITE 3: Degenerate Input Stress Testing on computeFrontendRecommendation
// ---------------------------------------------------------------------------
console.log('\n--- SUITE 3: Degenerate Input Stress Testing (computeFrontendRecommendation) ---');

function testComputeFrontendRecommendationDegenerate() {
  const normalActual = {
    feed_flow_t_h: 245.8,
    lng_flow_t_h: 232.3,
    mcr_flow_t_h: 562.3,
    comp_N2_molpct: 3.39,
    comp_C1_molpct: 44.45,
    comp_C2_molpct: 45.02,
    comp_C2H4_molpct: 0.85,
    comp_C3_molpct: 6.29,
  };

  // 3.1 Invalid feedFlowTH (should return null)
  const invalidFeeds = [
    { name: 'Null feedFlowTH', val: null },
    { name: 'Undefined feedFlowTH', val: undefined },
    { name: 'Zero feedFlowTH (0.0)', val: 0.0 },
    { name: 'Negative feedFlowTH (-50.0)', val: -50.0 },
    { name: 'NaN feedFlowTH', val: NaN },
    { name: 'Infinity feedFlowTH', val: Infinity },
    { name: '-Infinity feedFlowTH', val: -Infinity },
  ];

  for (const tc of invalidFeeds) {
    let res;
    let threw = false;
    try {
      res = computeFrontendRecommendation(tc.val, normalActual);
    } catch (e) {
      threw = true;
    }
    check(!threw, `No exception thrown for invalid feed: ${tc.name}`);
    check(res === null, `Returns null for invalid feed: ${tc.name}`);
  }

  // 3.2 Extreme valid feedFlowTH (below/above typical range)
  {
    const low = computeFrontendRecommendation(20.0, normalActual, 0.30, 'CONDITION_DEPENDENT');
    check(low !== null, 'Low feed (20 t/h) returns non-null recommendation');
    check(low.mcr_flow_t_h >= ANTISURGE_FLOW_FLOOR_T_H, 'Low feed enforces anti-surge flow floor (>= 480 t/h)');
    check(!isNaN(low.comp_N2_molpct), 'Low feed comp_N2_molpct is not NaN');
    check(low.extrapolated === true, 'Low feed flags extrapolated = true');

    const high = computeFrontendRecommendation(500.0, normalActual, 0.30, 'CONDITION_DEPENDENT');
    check(high !== null, 'High feed (500 t/h) returns non-null recommendation');
    check(high.mcr_flow_t_h > 600.0, 'High feed scales MCR circulation above 600 t/h');
    check(!isNaN(high.comp_N2_molpct), 'High feed comp_N2_molpct is not NaN');
    check(high.extrapolated === true, 'High feed flags extrapolated = true');
  }

  // 3.3 Adversarial testing of actualDcs in MINIMUM_INTERVENTION strategy
  console.log('\nTesting MINIMUM_INTERVENTION handling of incomplete/degenerate actualDcs:');
  {
    // Case A: actualDcs is undefined
    const resUndefined = computeFrontendRecommendation(250.0, undefined, 0.30, 'MINIMUM_INTERVENTION');
    check(resUndefined !== null, 'Undefined actualDcs returns non-null recommendation');
    check(!isNaN(resUndefined.comp_N2_molpct), 'Undefined actualDcs uses default and avoids NaN');

    // Case B: actualDcs is empty object {}
    const resEmpty = computeFrontendRecommendation(250.0, {}, 0.30, 'MINIMUM_INTERVENTION');
    const hasNaNEmpty = isNaN(resEmpty?.comp_N2_molpct);
    if (hasNaNEmpty) {
      findings.push('CRITICAL FINDING: computeFrontendRecommendation(feed, {}, 0.30, "MINIMUM_INTERVENTION") returns NaN composition due to missing object property defaults.');
      check(false, 'Empty object actualDcs {} produced NaN in MINIMUM_INTERVENTION strategy (DEFECT DETECTED)');
    } else {
      check(true, 'Empty object actualDcs {} handled safely without NaN');
    }

    // Case C: actualDcs with partial/missing components
    const resPartial = computeFrontendRecommendation(250.0, { comp_N2_molpct: 3.39 }, 0.30, 'MINIMUM_INTERVENTION');
    const hasNaNPartial = isNaN(resPartial?.comp_C1_molpct);
    if (hasNaNPartial) {
      findings.push('CRITICAL FINDING: computeFrontendRecommendation with partial actualDcs produces NaN for missing components in MINIMUM_INTERVENTION.');
      check(false, 'Partial actualDcs produced NaN in MINIMUM_INTERVENTION strategy (DEFECT DETECTED)');
    } else {
      check(true, 'Partial actualDcs handled safely without NaN');
    }

    // Case D: actualDcs with NaN component
    const resNaN = computeFrontendRecommendation(
      250.0,
      { comp_N2_molpct: NaN, comp_C1_molpct: 44.45, comp_C2_molpct: 45.02, comp_C2H4_molpct: 0.85, comp_C3_molpct: 6.29 },
      0.30,
      'MINIMUM_INTERVENTION'
    );
    const hasNaNInRes = isNaN(resNaN?.comp_N2_molpct);
    if (hasNaNInRes) {
      findings.push('FINDING: computeFrontendRecommendation with NaN in actualDcs propagates NaN to output composition in MINIMUM_INTERVENTION.');
      check(false, 'NaN in actualDcs component produced NaN output in MINIMUM_INTERVENTION (DEFECT DETECTED)');
    } else {
      check(true, 'NaN in actualDcs component sanitized without NaN');
    }
  }
}

// ---------------------------------------------------------------------------
// SUITE 4: Multi-Strategy Transition Validation across Operating Envelope
// ---------------------------------------------------------------------------
console.log('\n--- SUITE 4: Strategy Switch & Transition Invariants ---');

function testStrategyTransitions() {
  const normalActual = {
    feed_flow_t_h: 245.8,
    lng_flow_t_h: 232.3,
    mcr_flow_t_h: 562.3,
    comp_N2_molpct: 3.39,
    comp_C1_molpct: 44.45,
    comp_C2_molpct: 45.02,
    comp_C2H4_molpct: 0.85,
    comp_C3_molpct: 6.29,
  };

  const feedRates = [140.0, 180.0, 220.0, 245.8, 280.0, 320.0];

  for (const feed of feedRates) {
    const sCond = computeFrontendRecommendation(feed, normalActual, 0.30, 'CONDITION_DEPENDENT');
    const sFix = computeFrontendRecommendation(feed, normalActual, 0.30, 'FIXED_RECIPE');
    const sMin = computeFrontendRecommendation(feed, normalActual, 0.30, 'MINIMUM_INTERVENTION');

    check(sCond !== null && sFix !== null && sMin !== null, `All 3 strategies evaluate at feed ${feed} t/h`);

    // Verify 100.00% simplex closure
    const sumCond = sCond.comp_N2_molpct + sCond.comp_C1_molpct + sCond.comp_C2_molpct + sCond.comp_C2H4_molpct + sCond.comp_C3_molpct;
    const sumFix = sFix.comp_N2_molpct + sFix.comp_C1_molpct + sFix.comp_C2_molpct + sFix.comp_C2H4_molpct + sFix.comp_C3_molpct;
    const sumMin = sMin.comp_N2_molpct + sMin.comp_C1_molpct + sMin.comp_C2_molpct + sMin.comp_C2H4_molpct + sMin.comp_C3_molpct;

    check(Math.abs(sumCond - 100.0) < 0.01, `CONDITION_DEPENDENT closure exactly 100.00% at feed ${feed} (got ${sumCond.toFixed(2)})`);
    check(Math.abs(sumFix - 100.0) < 0.01, `FIXED_RECIPE closure exactly 100.00% at feed ${feed} (got ${sumFix.toFixed(2)})`);
    check(Math.abs(sumMin - 100.0) < 0.01, `MINIMUM_INTERVENTION closure exactly 100.00% at feed ${feed} (got ${sumMin.toFixed(2)})`);

    // Verify FIXED_RECIPE composition is invariant across loads
    check(
      sFix.comp_N2_molpct === 3.77 &&
      sFix.comp_C1_molpct === 42.21 &&
      sFix.comp_C2_molpct === 43.67 &&
      sFix.comp_C2H4_molpct === 1.53 &&
      sFix.comp_C3_molpct === 8.82,
      `FIXED_RECIPE maintains exact certified invariant recipe [3.77, 42.21, 43.67, 1.53, 8.82] at feed ${feed}`
    );

    // Verify anti-surge floor
    check(
      sCond.mcr_flow_t_h >= ANTISURGE_FLOW_FLOOR_T_H &&
      sFix.mcr_flow_t_h >= ANTISURGE_FLOW_FLOOR_T_H &&
      sMin.mcr_flow_t_h >= ANTISURGE_FLOW_FLOOR_T_H,
      `All 3 strategies satisfy anti-surge flow floor (>= 480.0 t/h) at feed ${feed}`
    );

    // Verify suction TAL safety
    check(
      sCond.expected_suction_temp_c >= SUCTION_TAL_DEG_C &&
      sFix.expected_suction_temp_c >= SUCTION_TAL_DEG_C &&
      sMin.expected_suction_temp_c >= SUCTION_TAL_DEG_C,
      `All 3 strategies satisfy suction TAL temperature limit (>= -45.0 C) at feed ${feed}`
    );

    // Verify Mahalanobis distance within envelope (D_M <= 3.0802)
    check(
      sCond.mahalanobis_distance <= CHI2_CRITICAL_5COMP,
      `CONDITION_DEPENDENT Mahalanobis distance (${sCond.mahalanobis_distance.toFixed(3)}) within envelope at feed ${feed}`
    );
    check(
      sMin.mahalanobis_distance <= CHI2_CRITICAL_5COMP,
      `MINIMUM_INTERVENTION Mahalanobis distance (${sMin.mahalanobis_distance.toFixed(3)}) within envelope at feed ${feed}`
    );

    // Verify distinct explanations
    check(
      sCond.explanation.includes('Strategy B') &&
      sFix.explanation.includes('Strategy A') &&
      sMin.explanation.includes('Strategy C'),
      `Explanations explicitly distinguish Strategy A, B, and C at feed ${feed}`
    );
  }
}

// ---------------------------------------------------------------------------
// Main Execution
// ---------------------------------------------------------------------------
async function main() {
  await testPredictScenarioConcurrency();
  testMakeupAdvisoryDegenerate();
  testComputeFrontendRecommendationDegenerate();
  testStrategyTransitions();

  console.log('\n====================================================================');
  console.log(`TOTAL CHECKS: ${totalChecks} | PASSED: ${passedChecks} | FAILED: ${failedChecks}`);
  console.log('====================================================================');

  if (findings.length > 0) {
    console.log('\nDEFECTS & FINDINGS IDENTIFIED:');
    findings.forEach((f, i) => console.log(`  ${i + 1}. ${f}`));
  }

  process.exit(failedChecks > 0 ? 1 : 0);
}

main().catch((err) => {
  console.error('Test harness crashed:', err);
  process.exit(2);
});
