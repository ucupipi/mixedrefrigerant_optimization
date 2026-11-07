// Unit Tests for physicsEngine computeFrontendRecommendation Remediation
// Governance: AGENTS.md (Zero NaN, Simplex Closure, Zero Em-Dash/En-Dash)

import { computeFrontendRecommendation } from '../utils/physicsEngine';

function assertTrue(condition: unknown, msg: string): asserts condition {
  if (!condition) {
    throw new Error(`Assertion failed: ${msg}`);
  }
}

function assertStrictEqual(actual: unknown, expected: unknown, msg: string): void {
  if (actual !== expected) {
    throw new Error(`Assertion failed: ${msg}. Expected ${String(expected)}, got ${String(actual)}`);
  }
}

export function runPhysicsEngineTests(): void {
  // Test 1: actualDcs = {} (empty object) under MINIMUM_INTERVENTION
  {
    const res = computeFrontendRecommendation(250.0, {} as any, 0.30, 'MINIMUM_INTERVENTION');
    assertTrue(res !== null, 'Empty actualDcs {} should return non-null recommendation');
    assertTrue(Number.isFinite(res.comp_N2_molpct), 'comp_N2_molpct must be finite');
    assertTrue(Number.isFinite(res.comp_C1_molpct), 'comp_C1_molpct must be finite');
    assertTrue(Number.isFinite(res.comp_C2_molpct), 'comp_C2_molpct must be finite');
    assertTrue(Number.isFinite(res.comp_C2H4_molpct), 'comp_C2H4_molpct must be finite');
    assertTrue(Number.isFinite(res.comp_C3_molpct), 'comp_C3_molpct must be finite');
    assertTrue(Number.isFinite(res.mahalanobis_distance), 'mahalanobis_distance must be finite');

    const residuals = res.constraint_residuals || {};
    assertTrue(Number.isFinite(residuals.mahalanobis_margin), 'mahalanobis_margin must be finite');

    const sum = Math.round((res.comp_N2_molpct + res.comp_C1_molpct + res.comp_C2_molpct + res.comp_C2H4_molpct + res.comp_C3_molpct) * 100) / 100;
    assertStrictEqual(sum, 100.00, `Simplex closure must equal 100.00% (got ${sum}%)`);
  }

  // Test 2: actualDcs = undefined under MINIMUM_INTERVENTION
  {
    const res = computeFrontendRecommendation(250.0, undefined, 0.30, 'MINIMUM_INTERVENTION');
    assertTrue(res !== null, 'Undefined actualDcs should return non-null recommendation');
    assertTrue(Number.isFinite(res.comp_N2_molpct), 'Undefined actualDcs: comp_N2_molpct must be finite');
    assertTrue(Number.isFinite(res.comp_C1_molpct), 'Undefined actualDcs: comp_C1_molpct must be finite');
    assertTrue(Number.isFinite(res.comp_C2_molpct), 'Undefined actualDcs: comp_C2_molpct must be finite');
    assertTrue(Number.isFinite(res.comp_C2H4_molpct), 'Undefined actualDcs: comp_C2H4_molpct must be finite');
    assertTrue(Number.isFinite(res.comp_C3_molpct), 'Undefined actualDcs: comp_C3_molpct must be finite');
    assertTrue(Number.isFinite(res.mahalanobis_distance), 'Undefined actualDcs: mahalanobis_distance must be finite');

    const sum = Math.round((res.comp_N2_molpct + res.comp_C1_molpct + res.comp_C2_molpct + res.comp_C2H4_molpct + res.comp_C3_molpct) * 100) / 100;
    assertStrictEqual(sum, 100.00, `Simplex closure must equal 100.00% (got ${sum}%)`);
  }

  // Test 3: Partial actualDcs with missing components
  {
    const res = computeFrontendRecommendation(250.0, { comp_N2_molpct: 3.39 } as any, 0.30, 'MINIMUM_INTERVENTION');
    assertTrue(res !== null, 'Partial actualDcs should return non-null recommendation');
    assertTrue(Number.isFinite(res.comp_N2_molpct), 'Partial actualDcs: comp_N2_molpct must be finite');
    assertTrue(Number.isFinite(res.comp_C1_molpct), 'Partial actualDcs: comp_C1_molpct must be finite');
    assertTrue(Number.isFinite(res.comp_C2_molpct), 'Partial actualDcs: comp_C2_molpct must be finite');
    assertTrue(Number.isFinite(res.comp_C2H4_molpct), 'Partial actualDcs: comp_C2H4_molpct must be finite');
    assertTrue(Number.isFinite(res.comp_C3_molpct), 'Partial actualDcs: comp_C3_molpct must be finite');

    const sum = Math.round((res.comp_N2_molpct + res.comp_C1_molpct + res.comp_C2_molpct + res.comp_C2H4_molpct + res.comp_C3_molpct) * 100) / 100;
    assertStrictEqual(sum, 100.00, `Simplex closure must equal 100.00% (got ${sum}%)`);
  }

  // Test 4: actualDcs with NaN component
  {
    const res = computeFrontendRecommendation(
      250.0,
      { comp_N2_molpct: NaN, comp_C1_molpct: 44.45, comp_C2_molpct: 45.02, comp_C2H4_molpct: 0.85, comp_C3_molpct: 6.29 } as any,
      0.30,
      'MINIMUM_INTERVENTION'
    );
    assertTrue(res !== null, 'NaN in actualDcs should return non-null recommendation');
    assertTrue(Number.isFinite(res.comp_N2_molpct), 'NaN actualDcs: comp_N2_molpct must be finite');
    assertTrue(Number.isFinite(res.comp_C1_molpct), 'NaN actualDcs: comp_C1_molpct must be finite');
    assertTrue(!isNaN(res.mahalanobis_distance), 'NaN actualDcs: mahalanobis_distance must not be NaN');

    const sum = Math.round((res.comp_N2_molpct + res.comp_C1_molpct + res.comp_C2_molpct + res.comp_C2H4_molpct + res.comp_C3_molpct) * 100) / 100;
    assertStrictEqual(sum, 100.00, `Simplex closure must equal 100.00% (got ${sum}%)`);
  }

  // Test 5: FIXED_RECIPE with selectedRecipe = {}
  {
    const res = computeFrontendRecommendation(250.0, undefined, 0.30, 'FIXED_RECIPE', {});
    assertTrue(res !== null, 'Empty selectedRecipe {} should return non-null recommendation');
    assertTrue(Number.isFinite(res.comp_N2_molpct), 'FIXED_RECIPE empty recipe: comp_N2_molpct must be finite');
    assertTrue(Number.isFinite(res.comp_C1_molpct), 'FIXED_RECIPE empty recipe: comp_C1_molpct must be finite');

    const sum = Math.round((res.comp_N2_molpct + res.comp_C1_molpct + res.comp_C2_molpct + res.comp_C2H4_molpct + res.comp_C3_molpct) * 100) / 100;
    assertStrictEqual(sum, 100.00, `Simplex closure must equal 100.00% (got ${sum}%)`);
  }
}

// Auto-run when executed directly
runPhysicsEngineTests();

