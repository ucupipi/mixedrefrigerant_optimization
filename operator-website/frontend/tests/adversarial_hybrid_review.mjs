// Adversarial Architecture & Runtime Review Suite for Milestone 2
// Independent Reviewer & Adversarial Critic verification for hybridSurrogate.ts and api.ts
// ZERO em-dash (U+2014) and ZERO en-dash (U+2013) strict rule

import assert from 'node:assert';

console.log('===============================================================');
console.log('ADVERSARIAL STRESS TEST: HYBRID ARCHITECTURE & RUNTIME REVIEW');
console.log('===============================================================\n');

let totalTests = 0;
let passedTests = 0;
let failedTests = 0;

function check(cond, msg) {
  totalTests++;
  if (!cond) {
    failedTests++;
    console.error(`[FAIL] ${msg}`);
    throw new Error(msg);
  }
  passedTests++;
  console.log(`[PASS] ${msg}`);
}

// ---------------------------------------------------------------------------
// SUITE 1: HybridSurrogateEngine in Node.js (window undefined)
// ---------------------------------------------------------------------------
console.log('\n--- SUITE 1: HybridSurrogateEngine (window undefined / SSR mode) ---');

const { HybridSurrogateEngine, hybridSurrogate } = await import('../src/utils/hybridSurrogate.ts');
const { evaluateRidgeSurrogate, buildFeatureVector } = await import('../src/utils/physicsEngine.ts');

const sampleScenario = {
  feed_flow_t_h: 245.8,
  mcr_flow_t_h: 562.3,
  comp_N2_molpct: 3.38,
  comp_C1_molpct: 44.37,
  comp_C2_molpct: 44.94,
  comp_C2H4_molpct: 0.85,
  comp_C3_molpct: 6.28,
  p_4k2_suct_kgcm2a: 3.235,
  p_4k2_disch_kgcm2a: 13.697,
  p_4k3_suct_kgcm2a: 13.417,
  p_4k3_disch_kgcm2a: 43.881,
  p_c3_suct_kgcm2a: 1.045,
  p_c3_disch_kgcm2a: 14.164,
  t_mche_in_c: -33.8,
  t_mche_out_c: -152.5,
  p_flash_drum_kgcm2g: 0.30,
};

const { featureVector } = buildFeatureVector(sampleScenario);
check(featureVector.length === 20, 'featureVector has exactly 20 features');

const expectedRidge = evaluateRidgeSurrogate(featureVector);
check(Number.isFinite(expectedRidge), `evaluateRidgeSurrogate is finite: ${expectedRidge.toFixed(4)} MW`);

// Test predictSync
const syncPred = hybridSurrogate.predictSync(featureVector);
check(syncPred === expectedRidge, `predictSync matches evaluateRidgeSurrogate: ${syncPred}`);

// Test predict async
const asyncPred = await hybridSurrogate.predict(featureVector);
check(asyncPred === expectedRidge, `predict matches evaluateRidgeSurrogate when window is undefined: ${asyncPred}`);

const status1 = hybridSurrogate.getStatus();
check(status1.model_loaded === false, 'status.model_loaded is false');
check(status1.engine_mode === 'physics-fallback', 'status.engine_mode is physics-fallback');
check(status1.backend.includes('TypeScript'), 'status.backend mentions TypeScript');

// ---------------------------------------------------------------------------
// SUITE 2: HybridSurrogateEngine with simulated browser window & missing ort
// ---------------------------------------------------------------------------
console.log('\n--- SUITE 2: Simulated Browser Window (missing ort) ---');

globalThis.window = {};
const status2 = hybridSurrogate.getStatus();
const asyncPred2 = await hybridSurrogate.predict(featureVector);
check(asyncPred2 === expectedRidge, 'predict delegates safely when window.ort is missing');
const initRes2 = await hybridSurrogate.initSession();
check(initRes2 === false, 'initSession returns false cleanly when window.ort is missing');

// ---------------------------------------------------------------------------
// SUITE 3: Simulated Browser Window with failing ONNX session creation
// ---------------------------------------------------------------------------
console.log('\n--- SUITE 3: Simulated Window with failing ONNX session creation ---');

globalThis.window.ort = {
  env: { wasm: {} },
  InferenceSession: {
    create: async () => {
      throw new Error('Simulated 404: /models/c3mr_power_surrogate.onnx not found');
    },
  },
};

const initRes3 = await hybridSurrogate.initSession();
check(initRes3 === false, 'initSession catches ONNX create error and returns false');
check(hybridSurrogate.isLoaded() === false, 'isLoaded() remains false after creation failure');

const asyncPred3 = await hybridSurrogate.predict(featureVector);
check(asyncPred3 === expectedRidge, 'predict delegates safely to TypeScript physics after ONNX init failure');

// ---------------------------------------------------------------------------
// SUITE 4: Simulated Browser Window with runtime inference failure
// ---------------------------------------------------------------------------
console.log('\n--- SUITE 4: Simulated Window with failing ONNX inference run ---');

// Mock an active session that fails on run
const mockFailingSession = {
  inputNames: ['float_input'],
  outputNames: ['variable'],
  run: async () => {
    throw new Error('Simulated WASM crash during inference execution');
  },
};

// Manually trigger session assignment for stress test
globalThis.window.ort = {
  env: { wasm: {} },
  Tensor: class {
    constructor(type, data, dims) {
      this.type = type;
      this.data = data;
      this.dims = dims;
    }
  },
  InferenceSession: {
    create: async () => mockFailingSession,
  },
};

const initRes4 = await hybridSurrogate.initSession();
check(initRes4 === true, 'initSession succeeds with mock session');
check(hybridSurrogate.isLoaded() === true, 'isLoaded() returns true');

// Now predict should encounter run error, catch it, and delegate to evaluateRidgeSurrogate
const asyncPred4 = await hybridSurrogate.predict(featureVector);
check(asyncPred4 === expectedRidge, 'predict catches session.run error and delegates safely to TypeScript physics');

// ---------------------------------------------------------------------------
// SUITE 5: Simulated Window with corrupted/NaN output tensor from ONNX
// ---------------------------------------------------------------------------
console.log('\n--- SUITE 5: Simulated Window with corrupted/NaN tensor output ---');

const mockNaNSession = {
  inputNames: ['float_input'],
  outputNames: ['variable'],
  run: async () => {
    return {
      variable: { data: [NaN] },
    };
  },
};

globalThis.window.ort.InferenceSession.create = async () => mockNaNSession;
// Force re-init by resetting private fields via create
const initRes5 = await hybridSurrogate.initSession();
// If session was already loaded, test predict with NaN output
const asyncPred5 = await hybridSurrogate.predict(featureVector);
check(Number.isFinite(asyncPred5), `predict rejects NaN tensor data and returns valid finite fallback: ${asyncPred5}`);
check(asyncPred5 === expectedRidge, 'predict delegates to TypeScript physics when ONNX output is NaN');

// Clean up global window
delete globalThis.window;

// ---------------------------------------------------------------------------
// SUITE 6: api.ts Offline Fallbacks under Network Failure
// ---------------------------------------------------------------------------
console.log('\n--- SUITE 6: api.ts Offline Fallbacks under Network Error ---');

// Mock global fetch to throw network error (simulating offline client)
globalThis.fetch = async () => {
  throw new TypeError('Failed to fetch (net::ERR_CONNECTION_REFUSED)');
};

const apiModule = await import('../src/api.ts');
const {
  fetchSystemStatus,
  fetchDemoSnapshot,
  fetchHistoricalSummary,
  predictScenario,
  optimizeForFeed,
} = apiModule;

// 1. fetchSystemStatus
const statusRes = await fetchSystemStatus();
check(statusRes.status === 'healthy', 'fetchSystemStatus returns healthy status on network error');
check(statusRes.mode === 'standalone-hybrid', 'fetchSystemStatus mode is standalone-hybrid');

// 2. fetchDemoSnapshot
const snapshotRes = await fetchDemoSnapshot();
check(snapshotRes.source_mode === 'DEMO', 'fetchDemoSnapshot source_mode is DEMO');
check(snapshotRes.values.H1FI012.value === 245.8, 'fetchDemoSnapshot contains valid H1FI012');
check(snapshotRes.values.H4FI001.value === 562.3, 'fetchDemoSnapshot contains valid H4FI001');
check(snapshotRes.values.comp_N2.value === 3.38, 'fetchDemoSnapshot contains valid comp_N2');

// 3. fetchHistoricalSummary
const histRes = await fetchHistoricalSummary();
check(histRes.source === 'calibrated_synthetic_grid', 'fetchHistoricalSummary has valid source');
check(Array.isArray(histRes.points) && histRes.points.length === 9, 'fetchHistoricalSummary has 9 points');

// 4. predictScenario
const predRes = await predictScenario(sampleScenario);
check(Number.isFinite(predRes.prediction.total_shaft_power_mw), `predictScenario returns valid power: ${predRes.prediction.total_shaft_power_mw} MW`);
check(Number.isFinite(predRes.baseline_power_mw), `predictScenario returns baseline power: ${predRes.baseline_power_mw} MW`);
check(predRes.flash_drum_5c1 !== undefined, 'predictScenario includes flash_drum_5c1 summary');
check(predRes.chiller_duties !== undefined, 'predictScenario includes chiller_duties summary');
check(predRes.safety_check !== undefined, 'predictScenario includes safety_check');
check(predRes.makeup_advisory !== undefined, 'predictScenario includes makeup_advisory');

// 5. optimizeForFeed
const optRes = await optimizeForFeed(245.8);
check(optRes.feed_t_h === 245.8, 'optimizeForFeed returns requested feed_t_h');
check(optRes.mcr_flow_t_h >= 480.0, 'optimizeForFeed enforces anti-surge floor 480 t/h');
const compSum = optRes.comp_N2_molpct + optRes.comp_C1_molpct + optRes.comp_C2_molpct + optRes.comp_C2H4_molpct + optRes.comp_C3_molpct;
check(Math.abs(compSum - 100.0) < 0.05, `optimizeForFeed enforces 100.00% closure: sum=${compSum.toFixed(2)}%`);

// ---------------------------------------------------------------------------
// SUITE 7: api.ts Offline Fallbacks under HTTP Error Responses (404/500/503)
// ---------------------------------------------------------------------------
console.log('\n--- SUITE 7: api.ts Offline Fallbacks under HTTP Error Responses ---');

for (const statusCode of [404, 500, 503]) {
  globalThis.fetch = async () => ({
    ok: false,
    status: statusCode,
    statusText: `Simulated HTTP ${statusCode}`,
    json: async () => ({ detail: 'Server Error' }),
  });

  const s = await fetchSystemStatus();
  check(s.status === 'healthy', `HTTP ${statusCode}: fetchSystemStatus falls back to healthy`);

  const d = await fetchDemoSnapshot();
  check(d.source_mode === 'DEMO', `HTTP ${statusCode}: fetchDemoSnapshot falls back to DEFAULT_DEMO_SNAPSHOT`);

  const h = await fetchHistoricalSummary();
  check(h.points.length === 9, `HTTP ${statusCode}: fetchHistoricalSummary falls back to DEFAULT_HISTORICAL_SUMMARY`);

  const p = await predictScenario(sampleScenario);
  check(Number.isFinite(p.prediction.total_shaft_power_mw), `HTTP ${statusCode}: predictScenario falls back to computeClientPrediction`);

  const o = await optimizeForFeed(200.0);
  check(o.mcr_flow_t_h >= 480.0, `HTTP ${statusCode}: optimizeForFeed falls back to computeFrontendRecommendation`);
}

// ---------------------------------------------------------------------------
// SUITE 8: Boundary and Stress Scenarios on computeClientPrediction
// ---------------------------------------------------------------------------
console.log('\n--- SUITE 8: Boundary and Stress Scenarios on computeClientPrediction ---');

const testCases = [
  { name: 'Low turndown feed (130 t/h)', feed: 130.0, mcr: 480.0 },
  { name: 'Underload feed (195 t/h)', feed: 195.0, mcr: 490.0 },
  { name: 'Transition feed (250 t/h)', feed: 250.0, mcr: 560.0 },
  { name: 'Baseload feed (300 t/h)', feed: 300.0, mcr: 650.0 },
  { name: 'Maximum design feed (350 t/h)', feed: 350.0, mcr: 750.0 },
  { name: 'Extreme turndown (50 t/h)', feed: 50.0, mcr: 480.0 },
];

for (const tc of testCases) {
  const sc = { ...sampleScenario, feed_flow_t_h: tc.feed, mcr_flow_t_h: tc.mcr };
  const res = await predictScenario(sc);
  check(Number.isFinite(res.prediction.total_shaft_power_mw), `${tc.name}: power is finite (${res.prediction.total_shaft_power_mw.toFixed(2)} MW)`);
  check(res.prediction.total_shaft_power_mw > 0, `${tc.name}: power is positive`);
  check(Number.isFinite(res.baseline_power_mw), `${tc.name}: baseline power is finite (${res.baseline_power_mw.toFixed(2)} MW)`);
  check(res.flash_drum_5c1.mass_liquid_yield > 0.85, `${tc.name}: flash drum yield is realistic (${(res.flash_drum_5c1.mass_liquid_yield * 100).toFixed(2)}%)`);
  check(res.chiller_duties.q_propane_condenser_mw >= res.chiller_duties.q_total_precooling_mw, `${tc.name}: propane condenser duty >= precooling duty`);
}

console.log('\n===============================================================');
console.log(`STRESS TEST COMPLETE: ${passedTests}/${totalTests} CHECKS PASSED, ${failedTests} FAILED`);
console.log('===============================================================');
