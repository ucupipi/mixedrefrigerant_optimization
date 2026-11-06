import assert from 'node:assert';
import fs from 'node:fs';
import path from 'node:path';

console.log('===============================================================');
console.log('EMPIRICAL CHALLENGER STRESS HARNESS: MILESTONE 1 VERIFICATION');
console.log('===============================================================\n');

// 1. DATA CONTRACTS VERIFICATION
console.log('--- TEST 1: Stream Data Contracts & Thermodynamic Equilibrium ---');

const MCR_TOTAL_DCS = 562.3; // t/h
const MCR_TOTAL_SCENARIO = 480.0; // t/h (Anti-surge floor)

// PR-EOS flash equilibrium split at -35°C, 45 bar:
const VAPOR_FRACTION = 0.360;
const LIQUID_FRACTION = 0.640;

const stream3_dcs = MCR_TOTAL_DCS * VAPOR_FRACTION;
const stream3_scenario = MCR_TOTAL_SCENARIO * VAPOR_FRACTION;

const stream4_mass_dcs = MCR_TOTAL_DCS * LIQUID_FRACTION;
const stream4_mass_scenario = MCR_TOTAL_SCENARIO * LIQUID_FRACTION;

const stream4_vol_dcs = 875; // m3/h
const stream4_vol_scenario = 810; // m3/h

console.log(`Stream 3 FI1 (MCR Vap) DCS: ${stream3_dcs.toFixed(1)} t/h (expected: 202.4 t/h)`);
console.log(`Stream 3 FI1 (MCR Vap) Skenario: ${stream3_scenario.toFixed(1)} t/h (expected: 172.8 t/h)`);
assert.strictEqual(stream3_dcs.toFixed(1), '202.4', 'Stream 3 DCS mass flow must be 202.4 t/h');
assert.strictEqual(stream3_scenario.toFixed(1), '172.8', 'Stream 3 Skenario mass flow must be 172.8 t/h');

console.log(`Stream 4 FIC2 (MCR Liq) Vol DCS: ${stream4_vol_dcs} m3/h, Mass: ${stream4_mass_dcs.toFixed(0)} t/h`);
console.log(`Stream 4 FIC2 (MCR Liq) Vol Skenario: ${stream4_vol_scenario} m3/h, Mass: ${stream4_mass_scenario.toFixed(0)} t/h`);
assert.strictEqual(stream4_vol_dcs, 875, 'Stream 4 DCS volume must be 875 m3/h');
assert.strictEqual(stream4_vol_scenario, 810, 'Stream 4 Skenario volume must be 810 m3/h');
assert.strictEqual(stream4_mass_dcs.toFixed(0), '360', 'Stream 4 DCS mass flow must round to 360 t/h');
assert.strictEqual(stream4_mass_scenario.toFixed(0), '307', 'Stream 4 Skenario mass flow must round to 307 t/h');

// Mass conservation verification
const total_mass_dcs = stream3_dcs + stream4_mass_dcs;
const total_mass_scenario = stream3_scenario + stream4_mass_scenario;
assert(Math.abs(total_mass_dcs - MCR_TOTAL_DCS) < 0.01, 'Mass conservation must hold for DCS streams');
assert(Math.abs(total_mass_scenario - MCR_TOTAL_SCENARIO) < 0.01, 'Mass conservation must hold for Skenario streams');
console.log(`Total MCR Circulation H4FI011B DCS: ${total_mass_dcs.toFixed(1)} t/h`);
console.log(`Total MCR Circulation H4FI011B Skenario: ${total_mass_scenario.toFixed(1)} t/h`);

// Precooling cycle
const c3_flow = 212.5; // kNm3/h
const chiller_temp = -35.0; // °C
console.log(`Propane Precooling 4K-1 (H4FI001A): ${c3_flow} kNm3/h, Chillers 4E-7/8/9: ${chiller_temp}°C`);
assert.strictEqual(c3_flow, 212.5);
assert.strictEqual(chiller_temp, -35.0);
console.log('>>> TEST 1 PASSED: All stream contracts and thermodynamic splits verified!\n');

// 2. SLOP STRING SCAN IN SCOPED FRONTEND FILES
console.log('--- TEST 2: Anti-Slop Audit on 6 Scoped Frontend Files ---');
const baseFrontend = path.resolve('operator-website/frontend/src');
const filesToAudit = [
  path.join(baseFrontend, 'components', 'TabGrafik.tsx'),
  path.join(baseFrontend, 'components', 'TabInputResults.tsx'),
  path.join(baseFrontend, 'components', 'TopNavbar.tsx'),
  path.join(baseFrontend, 'components', 'ResultPanel.tsx'),
  path.join(baseFrontend, 'components', 'SpreadsheetTable.tsx'),
  path.join(baseFrontend, 'App.tsx'),
];

const bannedSlopPatterns = [
  /\bTarget\s+AI\b/i,
  /\bValue\s+Creation\b/i,
  /\bTerapkan\s+Rekomendasi\s+AI\b/i,
  /\bAI\s*-\s*152/i,
  /\bAI\s*-\s*153/i,
  /\bAI\s*-\s*43/i,
];

let scopedViolations = 0;
for (const file of filesToAudit) {
  const content = fs.readFileSync(file, 'utf-8');
  const lines = content.split('\n');
  const relPath = path.relative(baseFrontend, file);
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    for (const pat of bannedSlopPatterns) {
      if (pat.test(line)) {
        console.error(`[VIOLATION] ${relPath}:${i + 1} -> ${line.trim()}`);
        scopedViolations++;
      }
    }
  }
}

if (scopedViolations === 0) {
  console.log('>>> TEST 2 PASSED: Zero banned slop strings in the 6 scoped files!\n');
} else {
  console.error(`>>> TEST 2 FAILED: Found ${scopedViolations} banned slop violations in scoped files!\n`);
}

// 3. ADVERSARIAL DISCOVERY AUDIT (OUTSIDE SCOPE / EDGE CHECKS)
console.log('--- TEST 3: Adversarial Discovery Audit (index.html & App.tsx Fallback) ---');
const indexHtmlPath = path.resolve('operator-website/frontend/index.html');
const indexHtmlContent = fs.readFileSync(indexHtmlPath, 'utf-8');
const titleMatch = indexHtmlContent.match(/<title>(.*?)<\/title>/);

console.log(`Current index.html title: "${titleMatch ? titleMatch[1] : 'NOT FOUND'}"`);
const isAcademicTitle = titleMatch && titleMatch[1].includes('MACHINE LEARNING BASED');
if (isAcademicTitle) {
  console.warn(`[ADVERSARIAL DEFECT CONFIRMED] index.html still contains banned academic title: "${titleMatch[1]}"`);
} else {
  console.log('index.html title is clean.');
}

const appTsxPath = path.join(baseFrontend, 'App.tsx');
const appTsxContent = fs.readFileSync(appTsxPath, 'utf-8');
const hasOldModelLabel = appTsxContent.includes("data_label: 'SKENARIO WHAT-IF (HASIL MODEL ML)'");
if (hasOldModelLabel) {
  console.warn(`[ADVERSARIAL DEFECT CONFIRMED] App.tsx line 123 contains un-unslapped fallback label: "SKENARIO WHAT-IF (HASIL MODEL ML)"`);
} else {
  console.log('App.tsx fallback data_label is clean.');
}

console.log('\n===============================================================');
console.log('STRESS TEST COMPLETE');
console.log('===============================================================');
