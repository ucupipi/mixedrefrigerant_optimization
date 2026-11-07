import { computeFrontendRecommendation } from '../src/utils/physicsEngine.ts';

const testCases = [
  { desc: 'actualDcs = {}', actualDcs: {}, strat: 'MINIMUM_INTERVENTION' },
  { desc: 'actualDcs = null', actualDcs: null, strat: 'MINIMUM_INTERVENTION' },
  { desc: 'actualDcs = undefined', actualDcs: undefined, strat: 'MINIMUM_INTERVENTION' },
  { desc: 'actualDcs = { comp_N2_molpct: NaN }', actualDcs: { comp_N2_molpct: NaN }, strat: 'MINIMUM_INTERVENTION' },
  { desc: 'actualDcs = { comp_N2_molpct: 3.5 } (partial object)', actualDcs: { comp_N2_molpct: 3.5 }, strat: 'MINIMUM_INTERVENTION' },
  { desc: 'actualDcs with all fields NaN', actualDcs: { comp_N2_molpct: NaN, comp_C1_molpct: NaN, comp_C2_molpct: NaN, comp_C2H4_molpct: NaN, comp_C3_molpct: NaN }, strat: 'MINIMUM_INTERVENTION' },
  { desc: 'actualDcs with Infinity / -Infinity', actualDcs: { comp_N2_molpct: Infinity, comp_C1_molpct: -Infinity }, strat: 'MINIMUM_INTERVENTION' },
  { desc: 'actualDcs with string / boolean', actualDcs: { comp_N2_molpct: 'invalid', comp_C1_molpct: true }, strat: 'MINIMUM_INTERVENTION' },
  { desc: 'selectedRecipe = {}', recipe: {}, strat: 'FIXED_RECIPE' },
  { desc: 'selectedRecipe = { N2: NaN }', recipe: { N2: NaN }, strat: 'FIXED_RECIPE' },
  { desc: 'selectedRecipe = null', recipe: null, strat: 'FIXED_RECIPE' },
  { desc: 'selectedRecipe = undefined', recipe: undefined, strat: 'FIXED_RECIPE' },
  { desc: 'selectedRecipe = all NaN', recipe: { N2: NaN, C1: NaN, C2: NaN, C2H4: NaN, C3: NaN }, strat: 'FIXED_RECIPE' },
  { desc: 'selectedRecipe = partial', recipe: { N2: 4.0, C1: 40.0 }, strat: 'FIXED_RECIPE' },
  { desc: 'selectedRecipe = Infinity / strings', recipe: { N2: Infinity, C1: 'test' }, strat: 'FIXED_RECIPE' },
];

let allPassed = true;
let total = 0;
let passedCount = 0;

console.log('================================================================');
console.log('DEGENERATE INPUT FUZZING HARNESS: computeFrontendRecommendation');
console.log('================================================================');

for (const tc of testCases) {
  total++;
  const res = computeFrontendRecommendation(
    250,
    tc.actualDcs !== undefined ? tc.actualDcs : {},
    0.30,
    tc.strat,
    tc.recipe !== undefined ? tc.recipe : null
  );

  const comps = [
    res.comp_N2_molpct,
    res.comp_C1_molpct,
    res.comp_C2_molpct,
    res.comp_C2H4_molpct,
    res.comp_C3_molpct
  ];

  const sum = comps.reduce((a, b) => a + b, 0);
  const roundedSum = Math.round(sum * 100) / 100;
  const hasNan = comps.some(v => isNaN(v)) || isNaN(res.mahalanobis_distance) || Object.values(res.constraint_residuals).some(v => isNaN(v));
  const isFiniteAll = comps.every(v => Number.isFinite(v)) && Number.isFinite(res.mahalanobis_distance) && Object.values(res.constraint_residuals).every(v => Number.isFinite(v));
  const exactClosure = roundedSum === 100.00;

  const passed = !hasNan && isFiniteAll && exactClosure;
  if (passed) {
    passedCount++;
  } else {
    allPassed = false;
  }
  console.log(`[${passed ? 'PASS' : 'FAIL'}] ${tc.desc} (${tc.strat}): sum=${roundedSum.toFixed(2)}%, Dm=${res.mahalanobis_distance}, comps=[${comps.join(', ')}]`);
}

console.log('----------------------------------------------------------------');
console.log(`TOTAL: ${total} | PASSED: ${passedCount} | FAILED: ${total - passedCount}`);
console.log('================================================================');

if (!allPassed) {
  process.exit(1);
} else {
  console.log('ALL DEGENERATE FUZZ CHECKS PASSED WITH ZERO NANS AND 100.00% CLOSURE.');
}
