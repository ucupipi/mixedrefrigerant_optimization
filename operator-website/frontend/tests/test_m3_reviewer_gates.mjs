import assert from 'node:assert';
import {
  closure,
  ilrForward,
  ilrInverse,
  enforceSimplexClosure,
  invertMatrix5x5,
  validateMakeupInputs,
  buildUnevaluatedMakeupResponse,
  calculateMakeupAdvisory,
  computeFrontendRecommendation,
  computeMahalanobisDistance,
  PARETO_QUANTILES,
  INVARIANT_RECIPE_MOLPCT,
  DEFAULT_STREAM_PURITY_MATRIX,
  MW_SPECIES,
  ESTIMATED_MCR_LOOP_INVENTORY_KG,
  NORMAL_MOLAR_VOLUME_NM3_PER_KMOL,
} from '../src/utils/physicsEngine.ts';

console.log('================================================================');
console.log('REVIEWER M3-1 ADVERSARIAL STRESS TEST & GATES VERIFICATION');
console.log('================================================================\n');

let totalChecks = 0;
let passedChecks = 0;

function check(name, condition, extraInfo = '') {
  totalChecks++;
  if (condition) {
    passedChecks++;
    console.log(`[PASS] ${name}`);
  } else {
    console.error(`[FAIL] ${name} ${extraInfo}`);
    throw new Error(`Assertion failed: ${name} ${extraInfo}`);
  }
}

// ============================================================================
// GATE 1: Simplex Geometry & Isometric Log-Ratio Transformations
// ============================================================================
console.log('\n--- GATE 1: Simplex Geometry & ILR Transformation ---');

// 1.1 Roundtrip Isometry
{
  const testComps = [
    [0.0338, 0.4437, 0.4494, 0.0085, 0.0646],
    [0.02, 0.50, 0.40, 0.01, 0.07],
    [0.05, 0.42, 0.45, 0.02, 0.06],
    [0.01, 0.60, 0.30, 0.001, 0.089],
  ];

  for (let idx = 0; idx < testComps.length; idx++) {
    const orig = testComps[idx];
    const xi = ilrForward(orig);
    const recovered = ilrInverse(xi);
    let maxDiff = 0.0;
    for (let i = 0; i < 5; i++) {
      const diff = Math.abs(orig[i] - recovered[i]);
      if (diff > maxDiff) maxDiff = diff;
    }
    check(`ILR roundtrip test case #${idx + 1} max error < 1e-6`, maxDiff < 1e-6, `maxDiff=${maxDiff}`);
  }
}

// 1.2 Simplex Closure and C1 Residual Absorption Across Physical Operating Envelope
{
  console.log('Testing 10,000 points in operational Mahalanobis ellipsoid (D_M <= 3.0802)...');
  let allClosedExactly = true;
  let allStrictlyPositive = true;

  // Historical mean xi: [-0.6614, 2.0585, 2.8666, -2.2384]
  const meanXi = [-0.6613989652, 2.0585004114, 2.8666052438, -2.2383652824];

  let seed = 123456789;
  function rand() {
    seed = (seed * 1664525 + 1013904223) % 4294967296;
    return seed / 4294967296;
  }

  let testedOperational = 0;
  while (testedOperational < 10000) {
    const dxi = [
      (rand() - 0.5) * 1.5,
      (rand() - 0.5) * 0.5,
      (rand() - 0.5) * 0.8,
      (rand() - 0.5) * 3.0,
    ];
    const xi = [meanXi[0] + dxi[0], meanXi[1] + dxi[1], meanXi[2] + dxi[2], meanXi[3] + dxi[3]];
    const dm = computeMahalanobisDistance(xi);
    if (dm <= 3.0802) {
      testedOperational++;
      const rounded = enforceSimplexClosure(xi);
      const sum = Math.round(rounded.reduce((a, b) => a + b, 0.0) * 100) / 100;
      if (Math.abs(sum - 100.00) > 1e-9) allClosedExactly = false;
      for (let i = 0; i < 5; i++) {
        if (rounded[i] <= 0.0) allStrictlyPositive = false;
      }
    }
  }

  check('All 10,000 operational points achieve exact 100.00% closure', allClosedExactly);
  check('All 10,000 operational points have strictly positive mole fractions (> 0.0)', allStrictlyPositive);
}

// 1.3 Sweep of all 3 strategies across 120-360 t/h feed loads
{
  const strategies = ['CONDITION_DEPENDENT', 'FIXED_RECIPE', 'MINIMUM_INTERVENTION'];
  let allSweepClosed = true;
  let allSweepPositive = true;

  for (const strat of strategies) {
    for (let feed = 120.0; feed <= 360.0; feed += 2.0) {
      const rec = computeFrontendRecommendation(feed, undefined, 0.30, strat);
      if (!rec) continue;
      const sum = Math.round(
        (rec.comp_N2_molpct + rec.comp_C1_molpct + rec.comp_C2_molpct + rec.comp_C2H4_molpct + rec.comp_C3_molpct) * 100
      ) / 100;
      if (Math.abs(sum - 100.00) > 1e-9) allSweepClosed = false;
      if (
        rec.comp_N2_molpct <= 0 ||
        rec.comp_C1_molpct <= 0 ||
        rec.comp_C2_molpct <= 0 ||
        rec.comp_C2H4_molpct <= 0 ||
        rec.comp_C3_molpct <= 0
      ) {
        allSweepPositive = false;
      }
    }
  }

  check('Full load sweep (120-360 t/h) across all 3 strategies sums to identically 100.00%', allSweepClosed);
  check('Full load sweep across all 3 strategies yields strictly positive fractions (>0)', allSweepPositive);
}

// ============================================================================
// GATE 2: 5x5 Matrix Inversion & Partial Pivoting
// ============================================================================
console.log('\n--- GATE 2: 5x5 Matrix Inversion ---');

// 2.1 Default Purity Matrix Inversion Accuracy
{
  const comps = ['N2', 'C1', 'C2', 'C2H4', 'C3'];
  const Y = [];
  for (let i = 0; i < 5; i++) {
    Y[i] = [];
    for (let j = 0; j < 5; j++) {
      const streamJ = comps[j];
      const compI = comps[i];
      Y[i][j] = DEFAULT_STREAM_PURITY_MATRIX[streamJ][compI];
    }
  }

  // Column normalization
  for (let j = 0; j < 5; j++) {
    let colSum = 0.0;
    for (let i = 0; i < 5; i++) colSum += Y[i][j];
    for (let i = 0; i < 5; i++) Y[i][j] /= colSum;
  }

  const YInv = invertMatrix5x5(Y);

  // Compute product Y * YInv
  let maxProductDiff = 0.0;
  for (let i = 0; i < 5; i++) {
    for (let j = 0; j < 5; j++) {
      let dot = 0.0;
      for (let k = 0; k < 5; k++) {
        dot += Y[i][k] * YInv[k][j];
      }
      const expected = i === j ? 1.0 : 0.0;
      const diff = Math.abs(dot - expected);
      if (diff > maxProductDiff) maxProductDiff = diff;
    }
  }

  check('Purity matrix Y * Y^-1 equals I_5 within 1e-12', maxProductDiff < 1e-12, `maxDiff=${maxProductDiff}`);
}

// 2.2 Identity Matrix Inversion
{
  const I = [
    [1, 0, 0, 0, 0],
    [0, 1, 0, 0, 0],
    [0, 0, 1, 0, 0],
    [0, 0, 0, 1, 0],
    [0, 0, 0, 0, 1],
  ];
  const IInv = invertMatrix5x5(I);
  let isIdentical = true;
  for (let i = 0; i < 5; i++) {
    for (let j = 0; j < 5; j++) {
      if (Math.abs(IInv[i][j] - I[i][j]) > 1e-15) isIdentical = false;
    }
  }
  check('Identity matrix inversion yields identity matrix', isIdentical);
}

// 2.3 Singular and Degenerate Matrix Fallback
{
  const singularZero = [
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
  ];
  const resZero = invertMatrix5x5(singularZero);
  check('All-zeros singular matrix returns identity fallback safely', resZero[0][0] === 1 && resZero[0][1] === 0);

  const duplicateRows = [
    [1, 2, 3, 4, 5],
    [1, 2, 3, 4, 5],
    [0, 1, 0, 0, 0],
    [0, 0, 1, 0, 0],
    [0, 0, 0, 1, 0],
  ];
  const resDup = invertMatrix5x5(duplicateRows);
  check('Duplicate rows singular matrix returns identity fallback safely', resDup[0][0] === 1 && resDup[1][1] === 1 && resDup[0][1] === 0);
}

// ============================================================================
// GATE 3: Closed-Loop Species Molar Balance & Inventory Standard
// ============================================================================
console.log('\n--- GATE 3: Closed-Loop Species Molar Balance ---');

// 3.1 Inventory baseline standard is exactly 24,000.0 kg
check('ESTIMATED_MCR_LOOP_INVENTORY_KG constant is exactly 24000.0', ESTIMATED_MCR_LOOP_INVENTORY_KG === 24000.0);

// 3.2 Exact Closed-Loop Conservation Across Diverse Scenarios
{
  const testScenarios = [
    {
      name: 'Standard C1/N2 Enrichment',
      actual: { N2: 3.39, C1: 44.45, C2: 45.02, C2H4: 0.85, C3: 6.29 },
      target: { N2: 4.50, C1: 46.50, C2: 42.00, C2H4: 0.50, C3: 6.50 },
    },
    {
      name: 'High N2 Make-up Injection',
      actual: { N2: 2.00, C1: 45.00, C2: 45.00, C2H4: 0.50, C3: 7.50 },
      target: { N2: 4.00, C1: 44.00, C2: 44.00, C2H4: 0.50, C3: 7.50 },
    },
    {
      name: 'C2 Deficit Injection',
      actual: { N2: 3.50, C1: 46.00, C2: 42.00, C2H4: 0.50, C3: 8.00 },
      target: { N2: 3.50, C1: 44.00, C2: 44.50, C2H4: 0.50, C3: 7.50 },
    },
    {
      name: 'C3 Deficit Injection',
      actual: { N2: 3.50, C1: 46.00, C2: 45.00, C2H4: 0.50, C3: 5.00 },
      target: { N2: 3.50, C1: 44.00, C2: 44.00, C2H4: 0.50, C3: 8.00 },
    },
  ];

  const comps = ['N2', 'C1', 'C2', 'C2H4', 'C3'];

  // Setup purity matrix Y
  const Y = [];
  for (let i = 0; i < 5; i++) {
    Y[i] = [];
    for (let j = 0; j < 5; j++) {
      const streamJ = comps[j];
      const compI = comps[i];
      Y[i][j] = DEFAULT_STREAM_PURITY_MATRIX[streamJ][compI];
    }
  }
  for (let j = 0; j < 5; j++) {
    let colSum = 0.0;
    for (let i = 0; i < 5; i++) colSum += Y[i][j];
    for (let i = 0; i < 5; i++) Y[i][j] /= colSum;
  }

  for (const sc of testScenarios) {
    const adv = calculateMakeupAdvisory(sc.actual, sc.target, 2.0, 24000.0, true);
    check(`${sc.name}: Advisory returned status EVALUATED`, adv.status === 'EVALUATED');
    check(`${sc.name}: Inventory matches 24000.0 kg`, adv.estimated_inventory_kg === 24000.0);
    check(`${sc.name}: Transition hours matches 2.0`, adv.transition_hours === 2.0);

    // Reconstruct final state from initial moles and injected stream kmol
    const actSum = comps.reduce((acc, k) => acc + sc.actual[k], 0.0);
    const tgtSum = comps.reduce((acc, k) => acc + sc.target[k], 0.0);
    const x0 = comps.map((k) => sc.actual[k] / actSum);
    const xTgt = comps.map((k) => sc.target[k] / tgtSum);

    const mwVec = comps.map((k) => MW_SPECIES[k]);
    let avgMwAct = 0.0;
    for (let i = 0; i < 5; i++) avgMwAct += x0[i] * mwVec[i];
    const n0 = 24000.0 / avgMwAct;

    // Injected kmol for each stream
    const uKmol = [0, 0, 0, 0, 0];
    for (const item of adv.items) {
      const idx = comps.indexOf(item.component);
      if (idx >= 0 && item.recommended_flow_nm3_h != null) {
        const flowNm3H = item.recommended_flow_nm3_h;
        const totalNm3 = flowNm3H * 2.0;
        uKmol[idx] = totalNm3 / NORMAL_MOLAR_VOLUME_NM3_PER_KMOL;
      }
    }

    // Moles of each species added: Y * u
    const addedMoles = [0, 0, 0, 0, 0];
    for (let i = 0; i < 5; i++) {
      for (let j = 0; j < 5; j++) {
        addedMoles[i] += Y[i][j] * uKmol[j];
      }
    }

    // Final moles of each species in the loop
    const finalSpeciesMoles = [0, 0, 0, 0, 0];
    let totalFinalMoles = 0.0;
    for (let i = 0; i < 5; i++) {
      finalSpeciesMoles[i] = n0 * x0[i] + addedMoles[i];
      totalFinalMoles += finalSpeciesMoles[i];
    }

    // Final mole fraction
    let maxCompErrorPct = 0.0;
    for (let i = 0; i < 5; i++) {
      const finalFrac = finalSpeciesMoles[i] / totalFinalMoles;
      const finalMolPct = finalFrac * 100.0;
      const tgtMolPct = xTgt[i] * 100.0;
      const diff = Math.abs(finalMolPct - tgtMolPct);
      if (diff > maxCompErrorPct) maxCompErrorPct = diff;
    }

    check(
      `${sc.name}: Final closed-loop composition matches target within 0.10 mol%`,
      maxCompErrorPct < 0.10,
      `maxError=${maxCompErrorPct.toFixed(4)}%`
    );
  }
}

// 3.3 Zero Deficit (Balanced Recipe) Case
{
  const balanced = { N2: 3.39, C1: 44.45, C2: 45.02, C2H4: 0.85, C3: 6.29 };
  const adv = calculateMakeupAdvisory(balanced, balanced, 2.0, 24000.0);
  check('Balanced recipe: expansion_ratio is 1.0000', Math.abs((adv.expansion_ratio || 1.0) - 1.0) < 1e-4);
  check('Balanced recipe: total make-up flow is 0.0 Nm3/h', adv.total_makeup_flow_nm3_h === 0.0);
  check('Balanced recipe: actions are all STABIL / SEIMBANG', adv.items.every(it => it.action === 'STABIL / SEIMBANG'));
}

// ============================================================================
// GATE 4: Input Validation & Null Contracts (NOT EVALUATED Status)
// ============================================================================
console.log('\n--- GATE 4: Input Validation & Null Contracts ---');

// 4.1 Missing or Null Actual Composition
{
  const advNullAct = calculateMakeupAdvisory(null, { N2: 3.5, C1: 45.0, C2: 45.0, C3: 6.5 }, 2.0);
  check('Null actual composition returns NOT EVALUATED', advNullAct.status === 'NOT EVALUATED');
  check('Null actual composition returns null total_makeup_flow_nm3_h', advNullAct.total_makeup_flow_nm3_h === null);
  check('Null actual composition returns null total_makeup_flow_kg_h', advNullAct.total_makeup_flow_kg_h === null);
  check('Null actual composition returns null for all recommended item flows', advNullAct.items.every(it => it.recommended_flow_nm3_h === null));
  check('Null actual composition returns null for all needed_kg', advNullAct.items.every(it => it.needed_kg === null));
}

// 4.2 Missing or Null Target Composition
{
  const advNullTgt = calculateMakeupAdvisory({ N2: 3.5, C1: 45.0, C2: 45.0, C3: 6.5 }, null, 2.0);
  check('Null target composition returns NOT EVALUATED', advNullTgt.status === 'NOT EVALUATED');
  check('Null target composition returns null total_makeup_flow_nm3_h', advNullTgt.total_makeup_flow_nm3_h === null);
  check('Null target composition returns null item flows', advNullTgt.items.every(it => it.recommended_flow_nm3_h === null));
}

// 4.3 Degenerate Inventory Values (negative, zero, NaN, Infinity)
{
  const badInventories = [-100, 0, NaN, Infinity, -Infinity];
  for (const inv of badInventories) {
    const adv = calculateMakeupAdvisory(
      { N2: 3.5, C1: 45.0, C2: 45.0, C3: 6.5 },
      { N2: 4.0, C1: 45.0, C2: 45.0, C3: 6.0 },
      2.0,
      inv
    );
    check(`Degenerate inventory (${inv}) returns NOT EVALUATED`, adv.status === 'NOT EVALUATED');
    check(`Degenerate inventory (${inv}) returns null flows`, adv.total_makeup_flow_nm3_h === null);
  }
}

// 4.4 Degenerate Transition Hours (negative, zero, NaN, Infinity)
{
  const badHours = [-1.0, 0.0, NaN, Infinity];
  for (const th of badHours) {
    const adv = calculateMakeupAdvisory(
      { N2: 3.5, C1: 45.0, C2: 45.0, C3: 6.5 },
      { N2: 4.0, C1: 45.0, C2: 45.0, C3: 6.0 },
      th,
      24000.0
    );
    check(`Degenerate transition hours (${th}) returns NOT EVALUATED`, adv.status === 'NOT EVALUATED');
    check(`Degenerate transition hours (${th}) returns null flows`, adv.total_makeup_flow_nm3_h === null);
  }
}

// 4.5 Missing Required Core Component
{
  const missingN2 = { C1: 45.0, C2: 45.0, C3: 10.0 };
  const targetOk = { N2: 3.5, C1: 45.0, C2: 45.0, C3: 6.5 };
  const adv = calculateMakeupAdvisory(missingN2, targetOk, 2.0);
  check('Missing core component N2 returns NOT EVALUATED', adv.status === 'NOT EVALUATED');
  check('Missing core component returns null flows', adv.total_makeup_flow_nm3_h === null);
}

// 4.6 Out-of-Physical Range Sum (< 10% or > 150%)
{
  const lowSum = { N2: 0.1, C1: 1.0, C2: 1.0, C3: 0.5 };
  const highSum = { N2: 50.0, C1: 60.0, C2: 60.0, C3: 50.0 };
  const targetOk = { N2: 3.5, C1: 45.0, C2: 45.0, C3: 6.5 };

  const advLow = calculateMakeupAdvisory(lowSum, targetOk, 2.0);
  check('Sum < 10% returns NOT EVALUATED', advLow.status === 'NOT EVALUATED');

  const advHigh = calculateMakeupAdvisory(highSum, targetOk, 2.0);
  check('Sum > 150% returns NOT EVALUATED', advHigh.status === 'NOT EVALUATED');
}

// ============================================================================
// GATE 5: Integrity Verification (No hardcoded fake shortcuts)
// ============================================================================
console.log('\n--- GATE 5: Integrity Verification ---');

// Check that make-up rates scale linearly with inventory
{
  const actual = { N2: 3.39, C1: 44.45, C2: 45.02, C2H4: 0.85, C3: 6.29 };
  const target = { N2: 4.50, C1: 46.50, C2: 42.00, C2H4: 0.50, C3: 6.50 };

  const adv24k = calculateMakeupAdvisory(actual, target, 2.0, 24000.0);
  const adv48k = calculateMakeupAdvisory(actual, target, 2.0, 48000.0);

  const ratio = (adv48k.total_makeup_flow_kg_h || 0) / (adv24k.total_makeup_flow_kg_h || 1);
  check('Make-up flow scales linearly with loop inventory (ratio 48k/24k == 2.0)', Math.abs(ratio - 2.0) < 0.01, `ratio=${ratio.toFixed(4)}`);
}

// Check that make-up rates scale inversely with transition hours
{
  const actual = { N2: 3.39, C1: 44.45, C2: 45.02, C2H4: 0.85, C3: 6.29 };
  const target = { N2: 4.50, C1: 46.50, C2: 42.00, C2H4: 0.50, C3: 6.50 };

  const adv2h = calculateMakeupAdvisory(actual, target, 2.0, 24000.0);
  const adv4h = calculateMakeupAdvisory(actual, target, 4.0, 24000.0);

  const ratio = (adv2h.total_makeup_flow_kg_h || 0) / (adv4h.total_makeup_flow_kg_h || 1);
  check('Make-up flow scales inversely with transition hours (ratio 2h/4h == 2.0)', Math.abs(ratio - 2.0) < 0.01, `ratio=${ratio.toFixed(4)}`);
}

console.log('\n================================================================');
console.log(`ALL GATES PASSED: ${passedChecks}/${totalChecks} checks verified.`);
console.log('================================================================');
