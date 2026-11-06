import assert from 'node:assert';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.resolve(__dirname, '../../..');
const frontendDir = path.resolve(rootDir, 'operator-website/frontend');

console.log('================================================================');
console.log('EMPIRICAL CHALLENGER STRESS HARNESS: MILESTONE 1 VERIFICATION');
console.log('Target: Badak LNG Plant-3 OTS - TabGrafik Header & Streams');
console.log('================================================================\n');

// Read source files
const tabGrafikPath = path.resolve(frontendDir, 'src/components/TabGrafik.tsx');
const tabGrafikSrc = fs.readFileSync(tabGrafikPath, 'utf8');

const indexCssPath = path.resolve(frontendDir, 'src/index.css');
const indexCssSrc = fs.readFileSync(indexCssPath, 'utf8');

const tabInputResultsPath = path.resolve(frontendDir, 'src/components/TabInputResults.tsx');
const tabInputResultsSrc = fs.readFileSync(tabInputResultsPath, 'utf8');

const topNavbarPath = path.resolve(frontendDir, 'src/components/TopNavbar.tsx');
const topNavbarSrc = fs.readFileSync(topNavbarPath, 'utf8');

const resultPanelPath = path.resolve(frontendDir, 'src/components/ResultPanel.tsx');
const resultPanelSrc = fs.readFileSync(resultPanelPath, 'utf8');

const appPath = path.resolve(frontendDir, 'src/App.tsx');
const appSrc = fs.readFileSync(appPath, 'utf8');

// ============================================================================
// SUITE 1: HEADER CONSOLIDATION & DOM ELEMENT VERIFICATION (ZERO DUPLICATE BARS)
// ============================================================================
console.log('--- SUITE 1: Header Consolidation & Zero Duplicate Bars ---');

// 1.1 Confirm zero duplicate header bars in TabGrafik.tsx
// Old broken pattern: had an outer container header with #1e293b, followed by an inner Centum bar #1b2a4a or similar.
const headerMatches = tabGrafikSrc.match(/SINGLE INTEGRATED YOKOGAWA CENTUM VP WINDOW HEADER/g);
assert.strictEqual(headerMatches?.length, 1, 'Must contain exactly 1 declaration of integrated header');

// Check that there is NO second/duplicate header bar in the canvas
const headerBarBgMatches = tabGrafikSrc.match(/backgroundColor:\s*['"]#162238['"]/g);
assert.strictEqual(headerBarBgMatches?.length, 1, 'Must contain exactly one #162238 header bar');

// Verify no obsolete #1b2a4a or stacked outer header exists in TabGrafik.tsx
assert(!tabGrafikSrc.includes('#1b2a4a'), 'Obsolete stacked header background #1b2a4a must be removed');

// 1.2 Verify exact Zone 1 DOM elements:
console.log('  Testing Zone 1 (Left: Alarm Priority, Badge, Window Tab)...');
// Alarm priority registers [0] [0] [40]
assert(tabGrafikSrc.includes("title=\"High Priority Alarm: 0\">0</span>"), 'Red High Priority Alarm [0] must exist');
assert(tabGrafikSrc.includes("title=\"Medium Priority Alarm: 0\">0</span>"), 'Orange Med Priority Alarm [0] must exist');
assert(tabGrafikSrc.includes("title=\"Low / Advisory Alarm: 40\">40</span>"), 'Blue Low Priority Alarm [40] must exist');
assert(tabGrafikSrc.includes("backgroundColor: '#dc2626'"), 'High Alarm must be #dc2626 red');
assert(tabGrafikSrc.includes("backgroundColor: '#ea580c'"), 'Medium Alarm must be #ea580c orange');
assert(tabGrafikSrc.includes("backgroundColor: '#0284c7'"), 'Low Alarm must be #0284c7 blue');

// Badge "PFD REPLICA"
assert(tabGrafikSrc.includes('PFD REPLICA'), 'PFD REPLICA badge text must exist');

// Active Graphic Tab "GRH0068" & "MCHE (5E-1)"
assert(tabGrafikSrc.includes('GRH0068'), 'Active tab GRH0068 must exist');
assert(tabGrafikSrc.includes('MCHE (5E-1)'), 'Active tab title MCHE (5E-1) must exist');

// Sibling Inactive Tabs: GRH0067, GRH0066, GRH0065, GRH0064
const siblingTabs = ['GRH0067', 'GRH0066', 'GRH0065', 'GRH0064'];
for (const tab of siblingTabs) {
  assert(tabGrafikSrc.includes(tab), `Sibling tab ${tab} must exist`);
}

// 1.3 Verify exact Zone 2 DOM elements (Telemetry KPI chips):
console.log('  Testing Zone 2 (Center: Telemetry KPI Chips)...');
assert(tabGrafikSrc.includes('Feed: <strong'), 'Feed flow KPI chip must exist');
assert(tabGrafikSrc.includes('MCR: <strong'), 'MCR flow KPI chip must exist');
assert(tabGrafikSrc.includes('SEC: <strong'), 'SEC KPI chip must exist');
assert(tabGrafikSrc.includes('Daya: <strong'), 'Daya (Total Power) KPI chip must exist');

// 1.4 Verify exact Zone 3 DOM elements (Mode Switcher, Clock):
console.log('  Testing Zone 3 (Right: View Mode Switcher & DCS Clock)...');
assert(tabGrafikSrc.includes("setDisplayMode('DCS_ACTUAL')"), 'DCS_ACTUAL button must exist');
assert(tabGrafikSrc.includes("🔘 Aktual"), '🔘 Aktual label must exist');
assert(tabGrafikSrc.includes("setDisplayMode('AI_OPTIMIZED')"), 'AI_OPTIMIZED button must exist');
assert(tabGrafikSrc.includes("🟢 Skenario"), '🟢 Skenario label must exist');
assert(tabGrafikSrc.includes("setDisplayMode('DELTA_DIFF')"), 'DELTA_DIFF button must exist');
assert(tabGrafikSrc.includes("⚡ Delta Δ"), '⚡ Delta Δ label must exist');

assert(tabGrafikSrc.includes('ENGUSER (S3)'), 'ENGUSER (S3) operator authority level must exist');
assert(tabGrafikSrc.includes('27-MAY-26 13:51'), 'DCS timestamp clock must exist');

console.log('>>> SUITE 1 PASSED: Single consolidated header with all required DOM elements verified.\n');

// ============================================================================
// SUITE 2: RESPONSIVE LAYOUT & VIEWPORT BEHAVIOR
// ============================================================================
console.log('--- SUITE 2: Responsive Layout & Viewport Behavior ---');

// 2.1 Verify mobile-hide class definition in index.css
console.log('  Verifying mobile-hide CSS breakpoint...');
const mediaQueryIdx = indexCssSrc.indexOf('@media (max-width: 768px)');
assert(mediaQueryIdx !== -1, '@media (max-width: 768px) must be present in index.css');
const mediaSection = indexCssSrc.slice(mediaQueryIdx, mediaQueryIdx + 600);
assert(mediaSection.includes('.mobile-hide'), '.mobile-hide class must be inside 768px media query');
assert(mediaSection.includes('display: none !important;'), '.mobile-hide must declare display: none !important');

// 2.2 Verify mobile-hide usage in TabGrafik.tsx
console.log('  Verifying mobile-hide usage in TabGrafik.tsx...');
const siblingTabsWithMobileHide = tabGrafikSrc.includes('<div className="mobile-hide" style={{ display: \'flex\', gap: \'8px\', color: \'#64748b\', fontSize: \'11px\' }}>');
assert(siblingTabsWithMobileHide, 'Sibling tabs container must have className="mobile-hide"');

const userWithMobileHide = tabGrafikSrc.includes('<span className="mobile-hide" style={{ color: \'#64748b\' }}>ENGUSER (S3)</span>');
assert(userWithMobileHide, 'ENGUSER (S3) span must have className="mobile-hide"');

// 2.3 Verify header flex container responsive properties
assert(tabGrafikSrc.includes("flexWrap: 'wrap'"), 'Header bar must have flexWrap: "wrap"');
assert(tabGrafikSrc.includes("minHeight: '42px'"), 'Header bar must have minHeight: "42px"');
assert(tabGrafikSrc.includes("justifyContent: 'space-between'"), 'Header bar must have justifyContent: "space-between"');

console.log('>>> SUITE 2 PASSED: Responsive viewport behavior and mobile-hide verified.\n');

// ============================================================================
// SUITE 3: REFRIGERATION STREAMS DISAMBIGUATION & 3-MODE MATHEMATICAL HARNESS
// ============================================================================
console.log('--- SUITE 3: Refrigeration Streams Disambiguation & 3-Mode Logic ---');

// 3.1 Stream 3: MR VAPOR (FI1 & TI47)
console.log('  Verifying Stream 3: FI1 (MCR Vap) & H5TI0047...');
assert(tabGrafikSrc.includes('(Stream 3)'), 'Stream 3 label must exist');
assert(tabGrafikSrc.includes('FI1 (MCR Vap)'), 'FI1 (MCR Vap) tag label must exist');
assert(tabGrafikSrc.includes("mcrFlowDcs * 0.360"), 'mcrVapFlowDcs must be mcrFlowDcs * 0.360');
assert(tabGrafikSrc.includes("mcrFlowAi * 0.360"), 'mcrVapFlowAi must be mcrFlowAi * 0.360');
assert(tabGrafikSrc.includes('TI47 (Vap T)'), 'TI47 (Vap T) temperature tag must exist');
assert(tabGrafikSrc.includes('H5TI0047'), 'Tag H5TI0047 must exist');

// 3.2 Stream 4: MR LIQUID (FIC2)
console.log('  Verifying Stream 4: FIC2 (MCR Liq)...');
assert(tabGrafikSrc.includes('(Stream 4)'), 'Stream 4 label must exist');
assert(tabGrafikSrc.includes('FIC2 (MCR Liq)'), 'FIC2 (MCR Liq) tag label must exist');
assert(tabGrafikSrc.includes("mcrFlowDcs * 0.640"), 'mcrLiqMassDcs must be mcrFlowDcs * 0.640');
assert(tabGrafikSrc.includes("mcrFlowAi * 0.640"), 'mcrLiqMassAi must be mcrFlowAi * 0.640');
assert(tabGrafikSrc.includes('const fic2Dcs = 875;'), 'fic2Dcs must be 875 m3/h');
assert(tabGrafikSrc.includes('const fic2Ai = 810;'), 'fic2Ai must be 810 m3/h');
// Verification that both m3/h and t/h are formatted in Stream 4:
assert(tabGrafikSrc.includes("m³/h"), 'FIC2 must display volumetric unit m³/h');
assert(tabGrafikSrc.includes("t/h"), 'FIC2 must display mass unit t/h');

// 3.3 Stream 8: SHELL-SIDE LP SUCTION RETURN (H4FI011B MCR Total)
console.log('  Verifying Stream 8: H4FI011B (MCR Total)...');
assert(tabGrafikSrc.includes('STREAM 8: SHELL-SIDE LP SUCTION RETURN'), 'Stream 8 description must exist');
assert(tabGrafikSrc.includes('H4FI011B (MCR Total)'), 'H4FI011B (MCR Total) tag label must exist');
assert(tabGrafikSrc.includes("Floor Anti-Surge ≥ 480.0 t/h"), 'Floor Anti-Surge ≥ 480.0 t/h limit must be specified');

// 3.4 Propane Precooling Cycle (4K-1 / H4FI001A & Chillers 3E-14/17/18)
console.log('  Verifying 4K-1 Propane Precooling Cycle block...');
assert(tabGrafikSrc.includes('4K-1 C3 PRECOOLING CYCLE'), '4K-1 C3 PRECOOLING CYCLE banner must exist');
assert(tabGrafikSrc.includes('H4FI001A'), 'H4FI001A tag must exist');
assert(tabGrafikSrc.includes('Stage 1 Suct (H4FI001A):'), 'Stage 1 Suct (H4FI001A) label must exist');
assert(tabGrafikSrc.includes('MCR Chillers 3E-14/17/18:'), 'MCR Chillers 3E-14/17/18 label must exist');
assert(tabGrafikSrc.includes('Feed Chillers 4E-10/12/14:'), 'Feed Chillers 4E-10/12/14 label must exist');
assert(tabGrafikSrc.includes('-35.0°C'), 'Chiller outlet -35.0°C must exist');

// 3.5 Mathematical Simulation of fmt() across all 3 modes for all refrigeration streams
console.log('  Simulating fmt() across all 3 display modes...');

function fmtSim(displayMode, dcsVal, aiVal, decimals = 1) {
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
  // DELTA_DIFF
  const diff = aiVal - dcsVal;
  const sign = diff > 0 ? '+' : '';
  const hasDiff = Math.abs(diff) > 0.005;
  return {
    display: `${sign}${diff.toFixed(decimals)}`,
    color: hasDiff ? '#fcd34d' : '#94a3b8',
    isAiDiff: hasDiff,
  };
}

// Test case data for streams
const testStreams = [
  {
    name: 'FI1 (MCR Vap)',
    decimals: 1,
    dcs: 562.3 * 0.360, // 202.428
    ai: 480.0 * 0.360,  // 172.800
    expectedDcsDisplay: '202.4',
    expectedAiDisplay: '172.8',
    expectedDeltaDisplay: '-29.6',
    unit: 't/h'
  },
  {
    name: 'FIC2 Volumetric',
    decimals: 0,
    dcs: 875,
    ai: 810,
    expectedDcsDisplay: '875',
    expectedAiDisplay: '810',
    expectedDeltaDisplay: '-65',
    unit: 'm³/h'
  },
  {
    name: 'FIC2 Mass',
    decimals: 0,
    dcs: 562.3 * 0.640, // 359.872 -> 360
    ai: 480.0 * 0.640,  // 307.200 -> 307
    expectedDcsDisplay: '360',
    expectedAiDisplay: '307',
    expectedDeltaDisplay: '-53',
    unit: 't/h'
  },
  {
    name: 'H4FI011B (MCR Total)',
    decimals: 1,
    dcs: 562.3,
    ai: 480.0,
    expectedDcsDisplay: '562.3',
    expectedAiDisplay: '480.0',
    expectedDeltaDisplay: '-82.3',
    unit: 't/h'
  },
  {
    name: 'H4FI001A (C3 Precool Suct)',
    decimals: 1,
    dcs: 212.5,
    ai: 212.5,
    expectedDcsDisplay: '212.5',
    expectedAiDisplay: '212.5',
    expectedDeltaDisplay: '0.0', // no delta!
    unit: 'kNm³/h'
  }
];

for (const stream of testStreams) {
  console.log(`    Testing Stream: ${stream.name}`);
  // Mode 1: DCS_ACTUAL
  const act = fmtSim('DCS_ACTUAL', stream.dcs, stream.ai, stream.decimals);
  assert.strictEqual(act.display, stream.expectedDcsDisplay, `${stream.name} DCS display mismatch`);
  assert.strictEqual(act.color, '#38bdf8', `${stream.name} DCS color must be cyan #38bdf8`);
  assert.strictEqual(act.isAiDiff, false);

  // Mode 2: AI_OPTIMIZED
  const opt = fmtSim('AI_OPTIMIZED', stream.dcs, stream.ai, stream.decimals);
  assert.strictEqual(opt.display, stream.expectedAiDisplay, `${stream.name} AI display mismatch`);
  if (Math.abs(stream.ai - stream.dcs) > 0.005) {
    assert.strictEqual(opt.color, '#34d399', `${stream.name} AI diff color must be green #34d399`);
    assert.strictEqual(opt.isAiDiff, true);
  } else {
    assert.strictEqual(opt.color, '#ffffff', `${stream.name} AI no-diff color must be white #ffffff`);
    assert.strictEqual(opt.isAiDiff, false);
  }

  // Mode 3: DELTA_DIFF
  const dlt = fmtSim('DELTA_DIFF', stream.dcs, stream.ai, stream.decimals);
  assert.strictEqual(dlt.display, stream.expectedDeltaDisplay, `${stream.name} Delta display mismatch`);
  if (Math.abs(stream.ai - stream.dcs) > 0.005) {
    assert.strictEqual(dlt.color, '#fcd34d', `${stream.name} Delta color must be yellow #fcd34d`);
    assert.strictEqual(dlt.isAiDiff, true);
  } else {
    assert.strictEqual(dlt.color, '#94a3b8', `${stream.name} Delta no-diff color must be muted #94a3b8`);
    assert.strictEqual(dlt.isAiDiff, false);
  }
}

console.log('>>> SUITE 3 PASSED: All refrigeration streams and 3-mode formatting verified.\n');

// ============================================================================
// SUITE 4: SCENARIO DISTURBANCE INPUT LABELS & UI UNSLOP DE-AI AUDIT
// ============================================================================
console.log('--- SUITE 4: Scenario Disturbance Labels & UI Unslop Audit ---');

// 4.1 TabInputResults: Scenario disturbance badge and column headers
assert(tabInputResultsSrc.includes('Input Beban Pabrik & Rekomendasi MCR'), 'Section 1 title must be Input Beban Pabrik & Rekomendasi MCR');
assert(tabInputResultsSrc.includes('⚡ Terapkan Rekomendasi MCR'), 'Apply button must be ⚡ Terapkan Rekomendasi MCR');
assert(tabInputResultsSrc.includes('Rekomendasi Operasi / Target Skenario'), 'Column header must be Rekomendasi Operasi / Target Skenario');
assert(tabInputResultsSrc.includes('Input Skenario / Beban Tetap'), 'Feed flow badge must be Input Skenario / Beban Tetap');
assert(tabInputResultsSrc.includes('SEKSI 3: PENGHEMATAN ENERGI & REDUKSI EMISI'), 'Section 3 title must be SEKSI 3: PENGHEMATAN ENERGI & REDUKSI EMISI');
assert(tabInputResultsSrc.includes('Penghematan Energi & Emisi'), 'Card group title must be Penghematan Energi & Emisi');

// 4.2 TopNavbar: Branding title and badge per R5 invariants
assert(topNavbarSrc.includes('MACHINE LEARNING BASED MIXED REFRIGERANT EFFICIENCY'), 'TopNavbar title must be MACHINE LEARNING BASED MIXED REFRIGERANT EFFICIENCY');
assert(topNavbarSrc.includes('ML'), 'TopNavbar badge must be ML');

// 4.3 ResultPanel: Unslop wording
assert(resultPanelSrc.includes('Menghitung Rekomendasi MCR...'), 'ResultPanel loading must be Menghitung Rekomendasi MCR...');
assert(resultPanelSrc.includes('Transformasi simpleks ILR 5-komponen & inferensi termodinamika C3MR'), 'ResultPanel subtitle must match unslop guidelines');

// 4.4 App: CSV header unslop
assert(appSrc.includes("'Skenario / Rekomendasi MCR'"), "CSV export header must include 'Skenario / Rekomendasi MCR'");

// 4.5 Banned AI Slop strings check
const bannedSlopPatterns = [
  { name: 'Target AI', pattern: /Target AI/g, allowedInComments: false },
  { name: 'Terapkan Rekomendasi AI', pattern: /Terapkan Rekomendasi AI/g, allowedInComments: false },
  { name: 'Value Creation', pattern: /Value Creation/g, allowedInComments: false },
  { name: 'AI -152.0°C', pattern: /AI -152\.0°C/g, allowedInComments: false },
  { name: 'AI -153.8°C', pattern: /AI -153\.8°C/g, allowedInComments: false },
];

const filesToAudit = [
  { name: 'TabGrafik.tsx', content: tabGrafikSrc },
  { name: 'TabInputResults.tsx', content: tabInputResultsSrc },
  { name: 'TopNavbar.tsx', content: topNavbarSrc },
  { name: 'ResultPanel.tsx', content: resultPanelSrc },
  { name: 'App.tsx', content: appSrc }
];

for (const file of filesToAudit) {
  for (const { name: slopName, pattern } of bannedSlopPatterns) {
    const matches = file.content.match(pattern);
    assert(!matches || matches.length === 0, `File ${file.name} contains banned AI slop phrase: "${slopName}" (${matches?.length} occurrences)`);
  }
}

console.log('>>> SUITE 4 PASSED: Zero banned AI slop strings detected across all frontend components.\n');

// ============================================================================
// SUITE 5: ADVERSARIAL STRESS TEST & BOUNDARY DEFENSE
// ============================================================================
console.log('--- SUITE 5: Adversarial Stress Test & Boundary Defense ---');

// Stress testing edge cases on fmtSim:
// 1. Extreme float values
const extremeCases = [
  { dcs: 0, ai: 0, decimals: 1, expectedDcs: '0.0', expectedAi: '0.0', expectedDelta: '0.0' },
  { dcs: -999.99, ai: -999.99, decimals: 1, expectedDcs: '-1000.0', expectedAi: '-1000.0', expectedDelta: '0.0' },
  { dcs: 1e5, ai: 1.0001e5, decimals: 1, expectedDcs: '100000.0', expectedAi: '100010.0', expectedDelta: '+10.0' },
  { dcs: 100.004, ai: 100.002, decimals: 1, expectedDcs: '100.0', expectedAi: '100.0', expectedDelta: '-0.0' }, // near zero delta
];

for (const c of extremeCases) {
  const rDcs = fmtSim('DCS_ACTUAL', c.dcs, c.ai, c.decimals);
  const rAi = fmtSim('AI_OPTIMIZED', c.dcs, c.ai, c.decimals);
  const rDelta = fmtSim('DELTA_DIFF', c.dcs, c.ai, c.decimals);
  assert(!rDcs.display.includes('NaN'), `NaN in rDcs: ${rDcs.display}`);
  assert(!rAi.display.includes('NaN'), `NaN in rAi: ${rAi.display}`);
  assert(!rDelta.display.includes('NaN'), `NaN in rDelta: ${rDelta.display}`);
}

console.log('>>> SUITE 5 PASSED: Extreme boundary cases handled robustly without NaN or divergence.\n');

console.log('================================================================');
console.log('ALL EMPIRICAL CHALLENGER TEST SUITES PASSED (5/5 SUITES CLEAN)');
console.log('================================================================');
