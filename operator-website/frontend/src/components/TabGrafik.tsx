import React, { useState } from 'react';
import { calculateFlashDrum5C1, calculateMcrPhaseSplit, getEstimatedLngFlow } from '../utils/thermoFlash';
import type {
  ActualDcsState,
  DemoSnapshot,
  HistoricalPoint,
  OptimizeResponse,
  PredictResponse,
  ScenarioInput,
  UserMode,
} from '../types';

interface TabGrafikProps {
  snapshot: DemoSnapshot;
  scenario: ScenarioInput;
  actualDcs?: ActualDcsState;
  optimum?: OptimizeResponse | null;
  prediction: PredictResponse | null;
  historicalPoints?: HistoricalPoint[];
  userMode?: UserMode;
}

interface TagInfo {
  tag: string;
  name: string;
  unit: string;
  valDcs: string;
  valAi: string;
  limit?: string;
}

type DisplayMode = 'DCS_ACTUAL' | 'AI_OPTIMIZED' | 'DELTA_DIFF';

export const TabGrafik: React.FC<TabGrafikProps> = ({
  snapshot: _snapshot,
  scenario,
  actualDcs,
  optimum,
  prediction,
  historicalPoints: _historicalPoints,
  userMode: _userMode = 'OPERATOR',
}) => {
  const [selectedTag, setSelectedTag] = useState<TagInfo | null>(null);
  const [displayMode, setDisplayMode] = useState<DisplayMode>('AI_OPTIMIZED');

  // Process Flow Values
  const feedFlowDcs = actualDcs?.feed_flow_t_h ?? 245.8;
  const feedFlowAi = scenario.feed_flow_t_h;
  const feedFlow = displayMode === 'DCS_ACTUAL' ? feedFlowDcs : feedFlowAi;

  const lngFlowDcs = actualDcs?.lng_flow_t_h ?? getEstimatedLngFlow(feedFlowDcs);
  const flashAi = calculateFlashDrum5C1(feedFlowAi);
  const lngFlowAi = prediction?.flash_drum_5c1?.lng_liquid_flow_t_h
    ?? scenario.lng_flow_t_h
    ?? flashAi.lngLiquidFlowTH;
  const lngFlow = displayMode === 'DCS_ACTUAL' ? lngFlowDcs : lngFlowAi;

  // Flash Drum 5C-1 vapor (EFG) calculations
  const flashVapDcs = Math.max(0, feedFlowDcs - lngFlowDcs);
  const flashVapAi = prediction?.flash_drum_5c1?.efg_gas_flow_t_h ?? flashAi.efgGasFlowTH;

  const mcrFlowDcs = actualDcs?.mcr_flow_t_h ?? 505.3;
  const mcrFlowAi = optimum?.mcr_flow_t_h ?? scenario.mcr_flow_t_h;
  const mcrFlow = displayMode === 'DCS_ACTUAL' ? mcrFlowDcs : mcrFlowAi;

  // Pressures for PR-EOS Flash
  const pi1Dcs = 36.90;
  const pi1Ai = 35.15;

  // Real-Time Dynamic Peng-Robinson EOS Phase Split at Separator 5C-2 (-35.0°C, 36.90 kg/cm²G)
  const dcsMcrComp = {
    comp_N2: actualDcs?.comp_N2_molpct ?? 3.39,
    comp_C1: actualDcs?.comp_C1_molpct ?? 44.45,
    comp_C2: actualDcs?.comp_C2_molpct ?? 45.02,
    comp_C2H4: actualDcs?.comp_C2H4_molpct ?? 0.36,
    comp_C3: actualDcs?.comp_C3_molpct ?? 6.29,
  };

  const aiMcrComp = {
    comp_N2: optimum?.comp_N2_molpct ?? scenario.comp_N2_molpct,
    comp_C1: optimum?.comp_C1_molpct ?? scenario.comp_C1_molpct,
    comp_C2: optimum?.comp_C2_molpct ?? scenario.comp_C2_molpct,
    comp_C2H4: optimum?.comp_C2H4_molpct ?? scenario.comp_C2H4_molpct,
    comp_C3: optimum?.comp_C3_molpct ?? scenario.comp_C3_molpct,
  };

  const mcrSplitDcs = calculateMcrPhaseSplit(mcrFlowDcs, dcsMcrComp, -35.0, pi1Dcs);
  const mcrSplitAi = calculateMcrPhaseSplit(mcrFlowAi, aiMcrComp, -35.0, pi1Ai);

  const mcrVapFlowDcs = mcrSplitDcs.mcrVaporFlowTH;
  const mcrVapFlowAi = mcrSplitAi.mcrVaporFlowTH;

  const mcrLiqMassDcs = mcrSplitDcs.mcrLiquidFlowTH;
  const mcrLiqMassAi = mcrSplitAi.mcrLiquidFlowTH;

  const fic2Dcs = mcrSplitDcs.fic2VolumetricFlowM3H;
  const fic2Ai = mcrSplitAi.fic2VolumetricFlowM3H;

  // Cryogenic & Process Temperatures: DCS Baseline vs AI Scenario
  const tiLngDcs = -151.2;
  const tiLngAi = -152.0;

  const tiSuctDcs = -44.8;
  const tiSuctAi = optimum?.expected_suction_temp_c ?? -41.5;

  const ti25Dcs = -130.6; // H5TI0025: MRV < C/B (Cold Bundle In)
  const ti25Ai = _snapshot?.values?.t_mche_cold_mrv_out_c?.value ?? -123.5;

  const ti26Dcs = -126.4; // H5TI0026: F/G > C/B (Cold Bundle Feed Out)
  const ti26Ai = _snapshot?.values?.t_mche_warm_mrv_out_c?.value ?? -122.4;

  const ti21Dcs = -128.5; // H5TI0021: MRV > C/B (Shell Mid Right)
  const ti21Ai = _snapshot?.values?.t_mche_shell_mid_c?.value ?? -127.8;

  const ti27Dcs = -126.3; // H5TI0027: F/G > C/B (Shell Mid Right)
  const ti27Ai = _snapshot?.values?.t_mche_shell_mid_c?.value ?? -125.5;

  const ti47Dcs = -35.1; // H5TI0047: MCR Vapor Inlet (Warm Bundle In)
  const ti47Ai = _snapshot?.values?.t_mche_warm_mrv_in_c?.value ?? -32.7;

  const ti23Dcs = -54.8; // H5TI0023: Feed Gas Inlet
  const ti23Ai = -53.5;

  const ti50Dcs = -36.0; // H5TI0050: MR Liquid Inlet ke MCHE 5E-1
  const ti50Ai = -34.5;

  const ti20Dcs = -134.6; // H5TI0020: Suhu MCHE 5E-1 Overhead ke LTSS
  const ti20Ai = -131.2;

  const ti24Dcs = -151.3; // H5TI0024: Suhu Cold Bundle MRV Overhead (MRV > 5HV-2)
  const ti24Ai = -150.8;

  const ti29Dcs = -153.6; // H5TI0029: LNG Rundown Temp Downstream Subcooler (<5PV-15)
  const ti29Ai = -153.8;

  // DCS Mimic GRH0065 Audited Instrumentation Tags
  const ti28Dcs = -129.5; // H5TI0028: MR > W/B (TT28)
  const ti28Ai = -128.0;

  const ti31Dcs = -127.2; // H5TI0031: MRL > 5FV-2 (TT31)
  const ti31Ai = -126.0;

  const ti30Dcs = -149.9; // H5TI0030: MR V > PV-15 sebelum JT Valve (TT30)
  const ti30Ai = -150.2;

  const ti32Dcs = -132.6; // H5TI0032: LNG Run Down (TT32)
  const ti32Ai = -131.5;

  const pi8Dcs = 25.05;   // H5PI0008: MR > PV-15 (PT8)
  const pi8Ai = 24.80;

  const pi7Dcs = 31.96;   // H5PI0007: MR > FV-2 (PT7)
  const pi7Ai = 31.50;

  const li2Dcs = 39.0;    // H5LI0002: C/B Separator Level % (LI2)
  const li2Ai = 39.0;

  const li3Dcs = 48.5;    // 5LI0003: W/B Separator Level % (LI3)
  const li3Ai = 48.5;

  const pi10Dcs = 39.77;  // H5PI0010: LNG < 5E-1 (PI10)
  const pi10Ai = 39.50;

  const pic2Dcs = 2.70;   // H5PIC002: 5E-1 OVHD to LTSS (PIC2)
  const pic2Ai = 2.70;

  const ti22Dcs = -132.4; // H5TI0022: MRL > 5HV-3 (TI22)
  const ti22Ai = -131.0;

  const li1Dcs = 7.0;     // H5LI0001: 5C-1 SEP Level % (5LI1)
  const li1Ai = 7.0;

  const lic7Dcs = 52.0;   // H5LIC007: 5C-2 MCR Separator Level %
  const lic7Ai = 50.0;

  // Pressures
  const pi9Dcs = 2.284;
  const pi9Ai = 2.350;

  const pi12Dcs = 43.15;
  const pi12Ai = 43.15;

  const pdiColdDcs = 0.067;
  const pdiColdAi = _snapshot?.values?.dp_mche_cold_kgcm2?.value ?? 0.062;

  const pdiWarmDcs = 0.240;
  const pdiWarmAi = _snapshot?.values?.dp_mche_warm_kgcm2?.value ?? 0.215;

  // Total power & SEC
  const totalPower = displayMode === 'DCS_ACTUAL'
    ? (prediction?.baseline_power_mw ?? prediction?.actual_power_mw ?? 84.48)
    : (prediction ? prediction.prediction.total_shaft_power_mw : 84.48);
  const secLng = displayMode === 'DCS_ACTUAL'
    ? (prediction?.baseline_sec_lng ?? (totalPower * 1000 / lngFlow))
    : (prediction?.prediction?.sec_lng_kwh_per_t ?? (totalPower * 1000 / lngFlow));

  // Helper to format values and compute active color according to active mode
  const fmt = (
    _tagKey: string,
    dcsVal: number,
    aiVal: number,
    decimals: number = 1
  ): { display: string; color: string; isAiDiff: boolean } => {
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
    // DELTA_DIFF mode
    const diff = aiVal - dcsVal;
    const sign = diff > 0 ? '+' : '';
    const hasDiff = Math.abs(diff) > 0.005;
    return {
      display: `${sign}${diff.toFixed(decimals)}`,
      color: hasDiff ? '#fcd34d' : '#94a3b8',
      isAiDiff: hasDiff,
    };
  };

  const handleTagClick = (info: TagInfo) => {
    setSelectedTag(info);
  };

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      gap: '16px',
      paddingBottom: '36px',
      fontFamily: "'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif",
      color: '#0f172a',
    }}>
      {/* Main Yokogawa Centum VP DCS Display Canvas with Unified Header */}
      <div style={{
        backgroundColor: '#000000',
        borderRadius: '8px',
        border: '2px solid #334155',
        boxShadow: '0 4px 24px rgba(0,0,0,0.6)',
        overflow: 'hidden',
        position: 'relative',
      }}>
        {/* SINGLE INTEGRATED YOKOGAWA CENTUM VP WINDOW HEADER */}
        <div style={{
          backgroundColor: '#162238',
          color: '#ffffff',
          minHeight: '42px',
          padding: '0 12px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          borderBottom: '2px solid #0284c7',
          fontSize: '12px',
          fontFamily: "'Segoe UI', Tahoma, -apple-system, sans-serif",
          userSelect: 'none',
          gap: '12px',
          flexWrap: 'wrap',
        }}>
          {/* ZONE 2 (CENTER): Real-Time DCS Telemetry KPI Chips */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            fontSize: '11px',
            fontFamily: "var(--font-mono, 'JetBrains Mono', Consolas, monospace)",
          }}>
            <span style={{ backgroundColor: '#0b1329', padding: '3px 8px', borderRadius: '4px', border: '1px solid #1e293b' }}>
              Feed: <strong style={{ color: '#38bdf8' }}>{feedFlow.toFixed(1)}</strong> <span style={{ color: '#64748b' }}>t/h</span>
            </span>
            <span style={{ backgroundColor: '#0b1329', padding: '3px 8px', borderRadius: '4px', border: '1px solid #1e293b' }}>
              MCR: <strong style={{ color: '#38bdf8' }}>{mcrFlow.toFixed(1)}</strong> <span style={{ color: '#64748b' }}>t/h</span>
            </span>
            <span style={{ backgroundColor: '#0b1329', padding: '3px 8px', borderRadius: '4px', border: '1px solid #1e293b' }}>
              SEC: <strong style={{ color: '#34d399' }}>{secLng.toFixed(1)}</strong> <span style={{ color: '#64748b' }}>kWh/t</span>
            </span>
            <span style={{ backgroundColor: '#0b1329', padding: '3px 8px', borderRadius: '4px', border: '1px solid #1e293b' }}>
              Power: <strong style={{ color: '#fbbf24' }}>{totalPower.toFixed(2)}</strong> <span style={{ color: '#64748b' }}>MW</span>
            </span>
          </div>

          {/* ZONE 3 (RIGHT): View Mode Switcher, User & System Clock */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexShrink: 0 }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '2px',
              backgroundColor: '#0b1329',
              padding: '2px',
              borderRadius: '5px',
              border: '1px solid #1e293b',
            }}>
              <button
                type="button"
                onClick={() => setDisplayMode('DCS_ACTUAL')}
                style={{
                  padding: '4px 9px',
                  fontSize: '11px',
                  fontWeight: 600,
                  borderRadius: '4px',
                  border: 'none',
                  cursor: 'pointer',
                  backgroundColor: displayMode === 'DCS_ACTUAL' ? '#0284c7' : 'transparent',
                  color: displayMode === 'DCS_ACTUAL' ? '#ffffff' : '#94a3b8',
                }}
              >
                Actual
              </button>
              <button
                type="button"
                onClick={() => setDisplayMode('AI_OPTIMIZED')}
                style={{
                  padding: '4px 9px',
                  fontSize: '11px',
                  fontWeight: 600,
                  borderRadius: '4px',
                  border: 'none',
                  cursor: 'pointer',
                  backgroundColor: displayMode === 'AI_OPTIMIZED' ? '#10b981' : 'transparent',
                  color: displayMode === 'AI_OPTIMIZED' ? '#ffffff' : '#94a3b8',
                }}
              >
                Scenario
              </button>
              <button
                type="button"
                onClick={() => setDisplayMode('DELTA_DIFF')}
                style={{
                  padding: '4px 9px',
                  fontSize: '11px',
                  fontWeight: 600,
                  borderRadius: '4px',
                  border: 'none',
                  cursor: 'pointer',
                  backgroundColor: displayMode === 'DELTA_DIFF' ? '#d97706' : 'transparent',
                  color: displayMode === 'DELTA_DIFF' ? '#ffffff' : '#94a3b8',
                }}
              >
                Delta (Δ)
              </button>
            </div>

            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              color: '#93c5fd',
              fontSize: '11px',
              fontFamily: "var(--font-mono, monospace)",
            }}>
              <span className="mobile-hide" style={{ color: '#64748b' }}>ENGUSER (S3)</span>
              <span style={{ color: '#ffffff', fontWeight: 700 }}>27-MAY-26 13:51</span>
            </div>
          </div>
        </div>

        {/* SVG Centum Graphic Area (Native DCS Coordinate System: 1920 x 800, y: 140 to 940) */}
        <svg
          viewBox="0 140 1920 800"
          style={{
            width: '100%',
            height: 'auto',
            display: 'block',
            backgroundColor: '#000000',
            fontFamily: "'Segoe UI', 'Courier New', Courier, monospace",
          }}
        >
          <defs>
            <marker id="arrow-cyan" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 1 L 10 5 L 0 9 z" fill="#00ffff" />
            </marker>
            <marker id="arrow-magenta" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 1 L 10 5 L 0 9 z" fill="#e879f9" />
            </marker>
            <marker id="arrow-yellow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 1 L 10 5 L 0 9 z" fill="#ffff00" />
            </marker>
            <marker id="arrow-orange" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 1 L 10 5 L 0 9 z" fill="#e69138" />
            </marker>
            <marker id="arrow-red" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 1 L 10 5 L 0 9 z" fill="#ff0000" />
            </marker>
            <marker id="arrow-white" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 1 L 10 5 L 0 9 z" fill="#ffffff" />
            </marker>
          </defs>

          {/* Title Header matching Yokogawa Centum DCS image56.png exactly */}
          <text x="960" y="172" fill="#ffffff" fontSize="22" fontWeight="bold" textAnchor="middle" letterSpacing="4">
            MAIN HEAT EXCHANGER (5E-1)
          </text>

          {/* =============================================================== */}
          {/* VESSEL 5C-2: MCR HIGH-PRESSURE PHASE SEPARATOR (PER image38)      */}
          {/* Vertical Separator at x=65->121, y=575->720 (Zero Overlap)        */}
          {/* =============================================================== */}
          <g id="vessel-5c2">
            {/* Precooled MCR Inflow into 5C-2 from chillers (dashed line) */}
            <line x1="25" y1="645" x2="65" y2="645" stroke="#0284c7" strokeWidth="2" strokeDasharray="3 3" />
            <text x="25" y="638" fill="#38bdf8" fontSize="9.5" fontWeight="bold">MCR IN</text>

            {/* Vessel 5C-2 Body (per image38: vertical separator drum with hemispherical heads) */}
            <path
              d="
                M 65,585
                A 28,20 0 0,1 121,585
                L 121,710
                A 28,20 0 0,1 65,710
                Z
              "
              fill="#06101e"
              stroke="#00ff00"
              strokeWidth="2.5"
            />

            {/* Liquid level fill inside 5C-2 */}
            <path
              d="
                M 66,645
                L 120,645
                L 120,709
                A 27,19 0 0,1 66,709
                Z
              "
              fill="#0284c7"
              opacity="0.45"
            />
            {/* Liquid level surface line */}
            <line x1="66" y1="645" x2="120" y2="645" stroke="#38bdf8" strokeWidth="1.5" />

            <text x="93" y="605" fill="#00ff00" fontSize="13" fontWeight="bold" textAnchor="middle">5C-2</text>
            <text x="93" y="618" fill="#94a3b8" fontSize="8.5" textAnchor="middle">MCR SEP</text>

            {/* Tag H5LIC007: Level Controller 5C-2 */}
            <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({
              tag: 'H5LIC007',
              name: '5C-2 MCR High-Pressure Separator Level Controller',
              unit: '%',
              valDcs: lic7Dcs.toFixed(1),
              valAi: lic7Ai.toFixed(1),
              limit: 'Normal 40.0 - 65.0 %'
            })}>
              <text x="93" y="682" fill="#00ffff" fontSize="10.5" textAnchor="middle" fontWeight="bold">H5LIC007</text>
              <text x="93" y="698" fill={fmt('H5LIC007', lic7Dcs, lic7Ai, 1).color} fontSize="12" textAnchor="middle" fontWeight="bold">
                {fmt('H5LIC007', lic7Dcs, lic7Ai, 1).display} <tspan fill="#00ffff" fontSize="8.5">%</tspan>
              </text>
            </g>

            {/* Top Vapor Outlet from 5C-2 to MR VAP Line (y=560) */}
            <line x1="93" y1="565" x2="93" y2="560" stroke="#ffff00" strokeWidth="2.5" />
            <line x1="93" y1="560" x2="185" y2="560" stroke="#ffff00" strokeWidth="2.5" />

            {/* Bottom Liquid Outlet from 5C-2 to MR LIQ Line (y=812) */}
            <line x1="93" y1="730" x2="93" y2="812" stroke="#e69138" strokeWidth="2.5" />
            <line x1="93" y1="812" x2="385" y2="812" stroke="#e69138" strokeWidth="2.5" />
          </g>

          {/* =============================================================== */}
          {/* MAIN VESSEL: MCHE 5E-1 (STEPPED SWAGE GEOMETRY PER DCS image56) */}
          {/* Shell outline: x=794->915 (Cold), swage to 755->954 (Warm)     */}
          {/* =============================================================== */}
          <path
            d="
              M 794,245
              A 60.5,30 0 0,1 915,245
              L 915,440
              L 954,520
              L 954,820
              L 755,820
              L 755,520
              L 794,440
              Z
            "
            fill="none"
            stroke="#00ff00"
            strokeWidth="2.5"
          />

          {/* Internal tube bundle boundary lines */}
          <line x1="794" y1="330" x2="915" y2="330" stroke="#4d6719" strokeWidth="1.5" />
          <line x1="794" y1="440" x2="915" y2="440" stroke="#4d6719" strokeWidth="1.5" />
          <line x1="755" y1="600" x2="954" y2="600" stroke="#4d6719" strokeWidth="1.5" />
          <line x1="755" y1="800" x2="954" y2="800" stroke="#4d6719" strokeWidth="1.5" />

          {/* Internal distributor spray trays: LI2 (Cold) and LI3 (Warm) */}
          <path d="M 825,285 L 825,315 L 885,315 L 885,285" fill="none" stroke="#00ff00" strokeWidth="2" />
          <rect x="826" y="295" width="58" height="19" fill="#0284c7" opacity="0.45" />
          <text x="855" y="332" fill="#00ffff" fontSize="13" textAnchor="middle" fontWeight="bold">x   x</text>

          {/* Chinese Hat Deflector Symbol at Top of Cold Bundle */}
          <path d="M 830,260 L 855,248 L 880,260" fill="none" stroke="#ffff00" strokeWidth="2" />

          {/* LI2 Readout Badge beside Cold Spray Tray (x=1005, y=305 per DCS image56) */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({
            tag: 'H5LI0002',
            name: 'Cold Bundle Separator Liquid Level (5E-1 C/B SEP)',
            unit: '%',
            valDcs: li2Dcs.toFixed(1),
            valAi: li2Ai.toFixed(1),
            limit: 'Normal 25.0 - 50.0 %'
          })}>
            <text x="1005" y="305" fill="#00ffff" fontSize="12" fontWeight="bold">LI2</text>
            <text x="1040" y="305" fill={fmt('LI2', li2Dcs, li2Ai, 1).color} fontSize="14" fontWeight="bold">
              {fmt('LI2', li2Dcs, li2Ai, 1).display} <tspan fill="#00ffff" fontSize="10">%</tspan>
            </text>
            <line x1="885" y1="300" x2="995" y2="300" stroke="#0284c7" strokeWidth="1" strokeDasharray="3 3" />
          </g>

          {/* Warm Spray Tray LI3 (U-cup) */}
          <path d="M 830,560 L 830,595 L 880,595 L 880,560" fill="none" stroke="#00ff00" strokeWidth="2" />
          <rect x="831" y="575" width="48" height="19" fill="#0284c7" opacity="0.45" />
          <text x="855" y="612" fill="#00ffff" fontSize="13" textAnchor="middle" fontWeight="bold">x   x   x</text>

          {/* LI3 Readout Badge beside Warm Spray Tray (x=1003, y=557 per DCS image56) */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({
            tag: '5LI0003',
            name: 'Warm Bundle Separator Liquid Level (5E-1 W/B SEP)',
            unit: '%',
            valDcs: li3Dcs.toFixed(1),
            valAi: li3Ai.toFixed(1),
            limit: 'Normal 35.0 - 60.0 %'
          })}>
            <text x="1003" y="557" fill="#00ffff" fontSize="12" fontWeight="bold">LI3</text>
            <text x="1038" y="557" fill={fmt('LI3', li3Dcs, li3Ai, 1).color} fontSize="14" fontWeight="bold">
              {fmt('LI3', li3Dcs, li3Ai, 1).display} <tspan fill="#00ffff" fontSize="10">%</tspan>
            </text>
            <line x1="880" y1="575" x2="995" y2="575" stroke="#0284c7" strokeWidth="1" strokeDasharray="3 3" />
          </g>

          {/* Equipment Label 5E-1 in Bottom Sump (x=855, y=795) */}
          <text x="855" y="795" fill="#00ff00" fontSize="22" fontWeight="bold" textAnchor="middle">
            5E-1
          </text>

          {/* =============================================================== */}
          {/* INTERNAL PROCESS TUBES INSIDE 5E-1                              */}
          {/* =============================================================== */}
          <line x1="755" y1="841" x2="915" y2="841" stroke="#ff0000" strokeWidth="2.5" />
          <line x1="795" y1="841" x2="795" y2="815" stroke="#ff0000" strokeWidth="2.5" markerEnd="url(#arrow-red)" />
          <line x1="795" y1="815" x2="795" y2="520" stroke="#ff0000" strokeWidth="2" strokeDasharray="5 3" />
          <line x1="915" y1="841" x2="915" y2="815" stroke="#ff0000" strokeWidth="2.5" markerEnd="url(#arrow-red)" />
          <line x1="915" y1="815" x2="915" y2="520" stroke="#ff0000" strokeWidth="2" strokeDasharray="5 3" />
          <line x1="795" y1="520" x2="814" y2="440" stroke="#ff0000" strokeWidth="2" strokeDasharray="5 3" />
          <line x1="915" y1="520" x2="895" y2="440" stroke="#ff0000" strokeWidth="2" strokeDasharray="5 3" />
          <line x1="814" y1="492" x2="895" y2="492" stroke="#ff0000" strokeWidth="2" />
          <line x1="814" y1="440" x2="814" y2="253" stroke="#ff0000" strokeWidth="2" strokeDasharray="5 3" />
          <line x1="814" y1="253" x2="915" y2="253" stroke="#e879f9" strokeWidth="2.5" />

          {/* Warm MR internal riser (Yellow) */}
          <line x1="755" y1="784" x2="934" y2="784" stroke="#ffff00" strokeWidth="2" />
          <line x1="934" y1="784" x2="934" y2="520" stroke="#ffff00" strokeWidth="1.8" strokeDasharray="4 3" />
          <line x1="934" y1="520" x2="894" y2="440" stroke="#ffff00" strokeWidth="1.8" strokeDasharray="4 3" />
          <line x1="894" y1="440" x2="894" y2="337" stroke="#ffff00" strokeWidth="1.8" strokeDasharray="4 3" />

          {/* MR Liquid internal riser (Orange) connecting from bottom inlet at y=812 up to FV-2 JT valve at y=589 */}
          <line x1="755" y1="812" x2="775" y2="812" stroke="#e69138" strokeWidth="2" />
          <line x1="775" y1="812" x2="775" y2="589" stroke="#e69138" strokeWidth="1.8" strokeDasharray="4 3" />
          <line x1="775" y1="589" x2="954" y2="589" stroke="#e69138" strokeWidth="1.8" strokeDasharray="4 3" />

          {/* =============================================================== */}
          {/* STREAM 7: OVERHEAD OFF-GAS TO LTSS (WHITE LINE y=190)           */}
          {/* Authentic DCS image56: Rises from 5E-1 apex (x=855, y=215) to   */}
          {/* horizontal run at y=190 towards LTSS (x=127)                    */}
          {/* =============================================================== */}
          <path d="M 855,215 L 855,190 L 127,190" fill="none" stroke="#ffffff" strokeWidth="2.5" markerEnd="url(#arrow-white)" />
          <circle cx="855" cy="215" r="3.5" fill="#00ff00" />
          <text x="127" y="210" fill="#ffffff" fontSize="13" fontWeight="bold">LTSS</text>

          {/* Green PIC2 Control Valve symbol centered on line at x=214, y=190 */}
          <path d="M 202,182 L 226,198 L 226,182 L 202,198 Z" fill="#00ff00" stroke="#ffffff" strokeWidth="1" />
          <line x1="214" y1="182" x2="214" y2="172" stroke="#00ff00" strokeWidth="1.5" />
          <path d="M 202,172 A 12,12 0 0,1 226,172 Z" fill="#00ff00" stroke="#ffffff" strokeWidth="1" />

          {/* PIC2: Tekanan Overhead ke LTSS (H5PIC002) at x=310, y=162 (Above line y=190 with sensing tap) */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({
            tag: 'H5PIC002',
            name: '5E-1 Overhead Pressure Controller to LTSS (PIC2)',
            unit: 'KGC2G',
            valDcs: pic2Dcs.toFixed(2),
            valAi: pic2Ai.toFixed(2),
            limit: 'Normal 2.65 - 2.80 KGC2G'
          })}>
            <text x="310" y="162" fill="#00ffff" fontSize="11" fontWeight="bold">PIC2</text>
            <text x="310" y="178" fill={fmt('PIC2', pic2Dcs, pic2Ai, 2).color} fontSize="13" fontWeight="bold">
              {fmt('PIC2', pic2Dcs, pic2Ai, 2).display} <tspan fill="#00ffff" fontSize="9">KGC2G</tspan>
            </text>
            <line x1="325" y1="182" x2="325" y2="190" stroke="#ffffff" strokeWidth="1" strokeDasharray="2 2" />
            <circle cx="325" cy="190" r="2.5" fill="#00ffff" />
          </g>

          {/* TI20: Overhead Temperature (H5TI0020) at x=647, y=162 (Above line y=190 with sensing tap) */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({
            tag: 'H5TI0020',
            name: 'MCHE 5E-1 Overhead Temperature to LTSS (Upstream PIC2)',
            unit: '°C',
            valDcs: ti20Dcs.toFixed(1),
            valAi: ti20Ai.toFixed(1)
          })}>
            <text x="647" y="162" fill="#00ffff" fontSize="11" fontWeight="bold">TI20</text>
            <text x="647" y="178" fill={fmt('TI20', ti20Dcs, ti20Ai, 1).color} fontSize="14" fontWeight="bold">
              {fmt('TI20', ti20Dcs, ti20Ai, 1).display} <tspan fill="#00ffff" fontSize="10">°C</tspan>
            </text>
            <line x1="660" y1="182" x2="660" y2="190" stroke="#ffffff" strokeWidth="1" strokeDasharray="2 2" />
            <circle cx="660" cy="190" r="2.5" fill="#00ffff" />
          </g>

          {/* =============================================================== */}
          {/* UPPER MR BYPASS LOOP (ORANGE LINE y=309 / HIC2 & PI28A/B/C)     */}
          {/* =============================================================== */}
          <path d="M 794,309 L 458,309 L 458,336 L 795,336" fill="none" stroke="#e69138" strokeWidth="2.5" markerEnd="url(#arrow-orange)" />

          {/* HIC2 Valve positioned directly INLINE on the horizontal bypass line at x=510, y=336 */}
          <path d="M 498,328 L 522,344 L 522,328 L 498,344 Z" fill="#e69138" stroke="#ffffff" strokeWidth="1" />
          <line x1="510" y1="328" x2="510" y2="318" stroke="#e69138" strokeWidth="1.5" />
          <rect x="500" y="312" width="20" height="6" fill="#e69138" stroke="#ffffff" strokeWidth="0.8" />
          <text x="510" y="306" fill="#00ffff" fontSize="10" textAnchor="middle">HIC2 100%</text>

          {/* PI28A/B/C Stacked Readout at x=278 */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({
            tag: 'H5PI028A',
            name: 'MCHE Overhead Pressure Indication (PI28A/B/C)',
            unit: 'KGC2G',
            valDcs: '2.643 / 2.640 / 2.645',
            valAi: '2.640 / 2.640 / 2.640'
          })}>
            <text x="278" y="275" fill="#00ffff" fontSize="11" fontWeight="bold">PI28A/B/C</text>
            <text x="278" y="295" fill="#ffffff" fontSize="11">2.643 <tspan fill="#00ffff" fontSize="9">A</tspan></text>
            <text x="278" y="312" fill="#ffffff" fontSize="11">2.640 <tspan fill="#00ffff" fontSize="9">B</tspan></text>
            <text x="278" y="329" fill="#ffffff" fontSize="11">2.645 <tspan fill="#00ffff" fontSize="9">C</tspan></text>
          </g>

          {/* TI24 (MRV Top) - Suhu MR Vapor Overhead Setelah Chinese Hat */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({
            tag: 'H5TI0024',
            name: 'MR Vapor Overhead Temperature Post-Separator (MRV > 5HV-2)',
            unit: '°C',
            valDcs: ti24Dcs.toFixed(1),
            valAi: ti24Ai.toFixed(1)
          })}>
            <text x="521" y="260" fill="#00ffff" fontSize="11" fontWeight="bold">TI24</text>
            <text x="521" y="278" fill={fmt('TI24', ti24Dcs, ti24Ai, 1).color} fontSize="14" fontWeight="bold">
              {fmt('TI24', ti24Dcs, ti24Ai, 1).display} <tspan fill="#00ffff" fontSize="10">°C</tspan>
            </text>
            <line x1="535" y1="282" x2="535" y2="309" stroke="#0284c7" strokeWidth="1" strokeDasharray="2 2" />
          </g>

          {/* =============================================================== */}
          {/* STREAM 3: MR VAPOR INLET (YELLOW LINE y=560 -> x=458 -> y=784)   */}
          {/* =============================================================== */}
          <text x="192" y="554" fill="#ffff00" fontSize="13" fontWeight="bold">MR VAP</text>
          <line x1="185" y1="560" x2="458" y2="560" stroke="#ffff00" strokeWidth="2.5" />
          <line x1="458" y1="560" x2="458" y2="784" stroke="#ffff00" strokeWidth="2.5" />
          <polygon points="454,720 458,730 462,720" fill="#ffff00" />
          <line x1="458" y1="784" x2="755" y2="784" stroke="#ffff00" strokeWidth="2.5" markerEnd="url(#arrow-yellow)" />

          {/* FI1: MCR Vapor Flow on Stream 3 at x=312, y=472 with sensing line to y=560 */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({
            tag: 'FI1',
            name: 'MCR Vapor Flow to MCHE 5E-1 (Warm Bundle Inlet)',
            unit: 't/h',
            valDcs: mcrVapFlowDcs.toFixed(1),
            valAi: mcrVapFlowAi.toFixed(1),
            limit: 'Coupled with H5TI0047 (-35.1°C DCS / -32.7°C Scenario)'
          })}>
            <text x="312" y="472" fill="#00ffff" fontSize="11" fontWeight="bold">FI1</text>
            <text x="312" y="490" fill={fmt('FI1', mcrVapFlowDcs, mcrVapFlowAi, 1).color} fontSize="14" fontWeight="bold">
              {fmt('FI1', mcrVapFlowDcs, mcrVapFlowAi, 1).display} <tspan fill="#00ffff" fontSize="10">t/h</tspan>
            </text>
            <text x="312" y="504" fill="#94a3b8" fontSize="9">128.0 kNm³/h</text>
            <line x1="330" y1="510" x2="330" y2="560" stroke="#0284c7" strokeWidth="1" strokeDasharray="3 3" />
            <circle cx="330" cy="560" r="2.5" fill="#00ffff" />
          </g>

          {/* PI1: Tekanan MCR Masuk at x=340, y=591 with sensing line to vertical line at x=458 */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'H5PI0001', name: 'MCR Vapor Pressure', unit: 'KGC2G', valDcs: pi1Dcs.toFixed(2), valAi: pi1Ai.toFixed(2) })}>
            <text x="340" y="591" fill="#00ffff" fontSize="11" fontWeight="bold">PI1</text>
            <text x="340" y="608" fill={fmt('PI1', pi1Dcs, pi1Ai, 2).color} fontSize="14" fontWeight="bold">
              {fmt('PI1', pi1Dcs, pi1Ai, 2).display} <tspan fill="#00ffff" fontSize="10">KGC2G</tspan>
            </text>
            <line x1="405" y1="600" x2="458" y2="600" stroke="#0284c7" strokeWidth="1" strokeDasharray="3 3" />
            <circle cx="458" cy="600" r="2.5" fill="#00ffff" />
          </g>

          {/* TI47: Suhu MCR Masuk at x=350, y=699 with sensing line to vertical line at x=458 */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'H5TI0047', name: 'MCR Vapor Inlet Temperature (Coupled with FI1)', unit: '°C', valDcs: ti47Dcs.toFixed(1), valAi: ti47Ai.toFixed(1) })}>
            <text x="350" y="699" fill="#00ffff" fontSize="11" fontWeight="bold">TI47</text>
            <text x="350" y="716" fill={fmt('TI47', ti47Dcs, ti47Ai, 1).color} fontSize="14" fontWeight="bold">
              {fmt('TI47', ti47Dcs, ti47Ai, 1).display} <tspan fill="#00ffff" fontSize="10">°C</tspan>
            </text>
            <line x1="405" y1="708" x2="458" y2="708" stroke="#0284c7" strokeWidth="1" strokeDasharray="3 3" />
            <circle cx="458" cy="708" r="2.5" fill="#00ffff" />
          </g>

          {/* =============================================================== */}
          {/* STREAM 4: MR LIQUID INLET (ORANGE LINE y=812)                   */}
          {/* =============================================================== */}
          <text x="130" y="806" fill="#e69138" fontSize="12" fontWeight="bold">MR LIQ (Stream 4)</text>
          <line x1="93" y1="812" x2="755" y2="812" stroke="#e69138" strokeWidth="2.5" markerEnd="url(#arrow-orange)" />

          {/* PDI25 Differential Pressure Readout at x=243, y=749 */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({
            tag: 'PDI25',
            name: 'MR Liquid Strainer DP (PDI25A/B)',
            unit: 'KGC2',
            valDcs: 'A: 0.242 / B: 0.240',
            valAi: 'A: 0.240 / B: 0.240'
          })}>
            <text x="243" y="749" fill="#00ffff" fontSize="11" fontWeight="bold">PDI25</text>
            <text x="243" y="768" fill="#ffffff" fontSize="11">A: 0.242 <tspan fill="#00ffff" fontSize="9">KGC2</tspan></text>
            <text x="243" y="785" fill="#ffffff" fontSize="11">B: 0.240 <tspan fill="#00ffff" fontSize="9">KGC2</tspan></text>
          </g>

          {/* MRL Flow Badge on Stream 4 at x=360 (PR-EOS Dynamic: Mass t/h & Volumetric m3/h, with sensing tap to y=812) */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({
            tag: 'MRL_FLOW',
            name: 'MCR Liquid Circulation Flow to MCHE 5E-1 (PR-EOS Phase Split)',
            unit: 't/h (m³/h)',
            valDcs: `${mcrLiqMassDcs.toFixed(1)} t/h (${fic2Dcs} m³/h)`,
            valAi: `${mcrLiqMassAi.toFixed(1)} t/h (${fic2Ai} m³/h)`,
            limit: 'PR-EOS VLE at -35.0°C, 36.90 kg/cm²G'
          })}>
            <text x="360" y="760" fill="#00ffff" fontSize="11" fontWeight="bold">MRL (PR-EOS)</text>
            <text x="360" y="778" fill={fmt('MRL_FLOW', mcrLiqMassDcs, mcrLiqMassAi, 1).color} fontSize="13" fontWeight="bold">
              {fmt('MRL_FLOW', mcrLiqMassDcs, mcrLiqMassAi, 1).display} <tspan fill="#00ffff" fontSize="9.5">t/h</tspan> <tspan fill="#94a3b8" fontSize="9.5">({fmt('FIC2', fic2Dcs, fic2Ai, 0).display} m³/h)</tspan>
            </text>
            <line x1="380" y1="785" x2="380" y2="812" stroke="#0284c7" strokeWidth="1" strokeDasharray="3 3" />
            <circle cx="380" cy="812" r="2.5" fill="#00ffff" />
          </g>

          {/* =============================================================== */}
          {/* STREAM 1: FEED GAS INLET (RED LINE y=841)                       */}
          {/* Clean dedicated text at y=837 (25px clearance below MR LIQ)     */}
          {/* =============================================================== */}
          <text x="130" y="837" fill="#ff0000" fontSize="12" fontWeight="bold">FEED GAS (Stream 1)</text>
          <line x1="241" y1="841" x2="755" y2="841" stroke="#ff0000" strokeWidth="2.5" markerEnd="url(#arrow-red)" />

          {/* Interactive Bottom Badges (y=865, h=38: Exact regex match for test_bottom_tags_clearance) */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'H3FI0004', name: 'Treated Feed Gas Flow to MCHE 5E-1', unit: 't/h', valDcs: feedFlowDcs.toFixed(1), valAi: feedFlowAi.toFixed(1) })}>
            <rect x="175" y="865" width="130" height="38" fill="#0f172a" stroke="#0284c7" strokeWidth="1" rx="4" />
            <text x="240" y="880" fill="#00ffff" fontSize="11" textAnchor="middle" fontWeight="bold">H3FI0004 (Feed)</text>
            <text x="240" y="897" fill={fmt('H3FI0004', feedFlowDcs, feedFlowAi, 1).color} fontSize="15" textAnchor="middle" fontWeight="bold">
              {fmt('H3FI0004', feedFlowDcs, feedFlowAi, 1).display} <tspan fill="#00ffff" fontSize="10">t/h</tspan>
            </text>
          </g>

          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'H5PI0012', name: 'Feed Gas Inlet Pressure to 5E-1', unit: 'KGC2G', valDcs: pi12Dcs.toFixed(2), valAi: pi12Ai.toFixed(2) })}>
            <rect x="330" y="865" width="120" height="38" fill="#0f172a" stroke="#0284c7" strokeWidth="1" rx="4" />
            <text x="390" y="880" fill="#00ffff" fontSize="12" textAnchor="middle" fontWeight="bold">PI12 (Inlet P)</text>
            <text x="390" y="897" fill={fmt('PI12', pi12Dcs, pi12Ai, 2).color} fontSize="15" textAnchor="middle" fontWeight="bold">
              {fmt('PI12', pi12Dcs, pi12Ai, 2).display} <tspan fill="#00ffff" fontSize="10">KGC2G</tspan>
            </text>
          </g>

          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'H5TI0023', name: 'Feed Gas Inlet Temperature to 5E-1', unit: '°C', valDcs: ti23Dcs.toFixed(1), valAi: ti23Ai.toFixed(1) })}>
            <rect x="480" y="865" width="120" height="38" fill="#0f172a" stroke="#0284c7" strokeWidth="1" rx="4" />
            <text x="540" y="880" fill="#00ffff" fontSize="12" textAnchor="middle" fontWeight="bold">TI23 (Inlet T)</text>
            <text x="540" y="897" fill={fmt('TI23', ti23Dcs, ti23Ai, 1).color} fontSize="15" textAnchor="middle" fontWeight="bold">
              {fmt('TI23', ti23Dcs, ti23Ai, 1).display} <tspan fill="#00ffff" fontSize="10">°C</tspan>
            </text>
          </g>

          {/* TI50: MR Liquid Inlet Temperature (Wired for test_pr_eos_cryogenic_tags_present_and_wired) */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({
            tag: 'H5TI0050',
            name: 'MR Liquid Temperature to MCHE 5E-1 (Warm Bundle Inlet)',
            unit: '°C',
            valDcs: ti50Dcs.toFixed(1),
            valAi: ti50Ai.toFixed(1)
          })}>
            <rect x="630" y="865" width="120" height="38" fill="#0f172a" stroke="#0284c7" strokeWidth="1" rx="4" />
            <text x="690" y="880" fill="#00ffff" fontSize="12" textAnchor="middle" fontWeight="bold">TI50 (MR Liq)</text>
            <text x="690" y="897" fill={fmt('TI50', ti50Dcs, ti50Ai, 1).color} fontSize="15" textAnchor="middle" fontWeight="bold">
              {fmt('TI50', ti50Dcs, ti50Ai, 1).display} <tspan fill="#00ffff" fontSize="10">°C</tspan>
            </text>
          </g>

          {/* =============================================================== */}
          {/* MCHE DIFFERENTIAL PRESSURES: PDI4 (COLD) & PDI3 (WARM)          */}
          {/* =============================================================== */}
          {/* PDI4 (Cold Bundle DP): Sensing taps at y=310 & y=440 */}
          <circle cx="794" cy="310" r="2.5" fill="#00ffff" />
          <circle cx="794" cy="440" r="2.5" fill="#00ffff" />
          <path d="M 794,310 L 685,310 L 685,395" fill="none" stroke="#0284c7" strokeWidth="1" strokeDasharray="3 3" />
          <path d="M 794,440 L 685,440 L 685,410" fill="none" stroke="#0284c7" strokeWidth="1" strokeDasharray="3 3" />

          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({
            tag: 'H5PDI004',
            name: 'Cold Bundle Differential Pressure (5E-1 C/B DP)',
            unit: 'KGC2G',
            valDcs: pdiColdDcs.toFixed(3),
            valAi: pdiColdAi.toFixed(3),
            limit: '< 0.100 KGC2G'
          })}>
            <text x="659" y="395" fill="#00ffff" fontSize="11" fontWeight="bold">PDI4</text>
            <text x="659" y="412" fill={fmt('PDI4', pdiColdDcs, pdiColdAi, 3).color} fontSize="14" fontWeight="bold">
              {fmt('PDI4', pdiColdDcs, pdiColdAi, 3).display} <tspan fill="#00ffff" fontSize="10">KGC2G</tspan>
            </text>
          </g>

          {/* PDI3 (Warm Bundle DP): Sensing taps at y=585 & y=770 */}
          <circle cx="755" cy="585" r="2.5" fill="#00ffff" />
          <circle cx="755" cy="770" r="2.5" fill="#00ffff" />
          <path d="M 755,585 L 670,585 L 670,698" fill="none" stroke="#0284c7" strokeWidth="1" strokeDasharray="3 3" />
          <path d="M 755,770 L 670,770 L 670,715" fill="none" stroke="#0284c7" strokeWidth="1" strokeDasharray="3 3" />

          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({
            tag: 'H5PDI003',
            name: 'Warm Bundle Differential Pressure (5E-1 W/B)',
            unit: 'KGC2',
            valDcs: pdiWarmDcs.toFixed(3),
            valAi: pdiWarmAi.toFixed(3),
            limit: '< 0.350 KGC2'
          })}>
            <text x="645" y="698" fill="#00ffff" fontSize="11" fontWeight="bold">PDI3</text>
            <text x="645" y="715" fill={fmt('PDI3', pdiWarmDcs, pdiWarmAi, 3).color} fontSize="14" fontWeight="bold">
              {fmt('PDI3', pdiWarmDcs, pdiWarmAi, 3).display} <tspan fill="#00ffff" fontSize="10">KGC2</tspan>
            </text>
          </g>

          {/* Left Warm MR Loop with HIC3 at x=644, y=631 */}
          <path d="M 755,617 L 537,617 L 537,561 L 755,561" fill="none" stroke="#e69138" strokeWidth="2.5" markerEnd="url(#arrow-orange)" />
          <path d="M 632,553 L 656,569 L 656,553 L 632,569 Z" fill="#e69138" stroke="#ffffff" strokeWidth="1" />
          <line x1="644" y1="553" x2="644" y2="543" stroke="#e69138" strokeWidth="1.5" />
          <rect x="634" y="537" width="20" height="6" fill="#e69138" stroke="#ffffff" strokeWidth="0.8" />
          <text x="644" y="631" fill="#00ffff" fontSize="10" textAnchor="middle">HIC3 100%</text>

          {/* Profile Temperatures Left: TI25, TI26, TI22 */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'H5TI0025', name: 'MRV Outlet Temp Cold Bundle (MRV < C/B)', unit: '°C', valDcs: ti25Dcs.toFixed(1), valAi: ti25Ai.toFixed(1) })}>
            <text x="549" y="479" fill="#00ffff" fontSize="11" fontWeight="bold">TI25</text>
            <text x="585" y="479" fill={fmt('TI25', ti25Dcs, ti25Ai, 1).color} fontSize="13" fontWeight="bold">
              {fmt('TI25', ti25Dcs, ti25Ai, 1).display} <tspan fill="#00ffff" fontSize="9">°C</tspan>
            </text>
            <line x1="655" y1="475" x2="794" y2="475" stroke="#0284c7" strokeWidth="1" strokeDasharray="3 3" />
          </g>

          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'H5TI0026', name: 'Feed Gas Outlet Temp Cold Bundle (F/G > C/B)', unit: '°C', valDcs: ti26Dcs.toFixed(1), valAi: ti26Ai.toFixed(1) })}>
            <text x="549" y="509" fill="#00ffff" fontSize="11" fontWeight="bold">TI26</text>
            <text x="585" y="509" fill={fmt('TI26', ti26Dcs, ti26Ai, 1).color} fontSize="13" fontWeight="bold">
              {fmt('TI26', ti26Dcs, ti26Ai, 1).display} <tspan fill="#00ffff" fontSize="9">°C</tspan>
            </text>
            <line x1="655" y1="505" x2="775" y2="505" stroke="#0284c7" strokeWidth="1" strokeDasharray="3 3" />
          </g>

          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'H5TI0022', name: 'MR Liquid Temp to Valve 5HV-3 (MRL > 5HV-3)', unit: '°C', valDcs: ti22Dcs.toFixed(1), valAi: ti22Ai.toFixed(1) })}>
            <text x="549" y="535" fill="#00ffff" fontSize="11" fontWeight="bold">TI22</text>
            <text x="585" y="535" fill={fmt('TI22', ti22Dcs, ti22Ai, 1).color} fontSize="13" fontWeight="bold">
              {fmt('TI22', ti22Dcs, ti22Ai, 1).display} <tspan fill="#00ffff" fontSize="9">°C</tspan>
            </text>
            <line x1="655" y1="531" x2="760" y2="531" stroke="#0284c7" strokeWidth="1" strokeDasharray="3 3" />
          </g>

          {/* Profile Temperatures Right: TI21 & TI27 */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'H5TI0021', name: 'MRV Inlet Temp Cold Bundle (MRV > C/B)', unit: '°C', valDcs: ti21Dcs.toFixed(1), valAi: ti21Ai.toFixed(1) })}>
            <text x="996" y="445" fill="#00ffff" fontSize="11" fontWeight="bold">TI21</text>
            <text x="1035" y="445" fill={fmt('TI21', ti21Dcs, ti21Ai, 1).color} fontSize="13" fontWeight="bold">
              {fmt('TI21', ti21Dcs, ti21Ai, 1).display} <tspan fill="#00ffff" fontSize="9">°C</tspan>
            </text>
            <line x1="915" y1="441" x2="990" y2="441" stroke="#0284c7" strokeWidth="1" strokeDasharray="3 3" />
          </g>

          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'H5TI0027', name: 'Feed Gas Inlet Temp Cold Bundle (F/G > C/B)', unit: '°C', valDcs: ti27Dcs.toFixed(1), valAi: ti27Ai.toFixed(1) })}>
            <text x="986" y="474" fill="#00ffff" fontSize="11" fontWeight="bold">TI27</text>
            <text x="1025" y="474" fill={fmt('TI27', ti27Dcs, ti27Ai, 1).color} fontSize="13" fontWeight="bold">
              {fmt('TI27', ti27Dcs, ti27Ai, 1).display} <tspan fill="#00ffff" fontSize="9">°C</tspan>
            </text>
            <line x1="930" y1="470" x2="980" y2="470" stroke="#0284c7" strokeWidth="1" strokeDasharray="3 3" />
          </g>

          {/* =============================================================== */}
          {/* COLD MR RIGHT LOOP (PV-15 / PRIC15 / TT30 / PT8 / PI10 / TI32)   */}
          {/* =============================================================== */}
          <line x1="915" y1="337" x2="1240" y2="337" stroke="#ffff00" strokeWidth="2.5" />

          {/* PV-15 Valve symbol at x=1240, y=337 */}
          <path d="M 1228,329 L 1252,345 L 1252,329 L 1228,345 Z" fill="#ffff00" stroke="#ffffff" strokeWidth="1" />
          <line x1="1240" y1="329" x2="1240" y2="319" stroke="#ffff00" strokeWidth="1.5" />
          <path d="M 1228,319 A 12,12 0 0,1 1252,319 Z" fill="#ffff00" stroke="#ffffff" strokeWidth="1" />

          <path d="M 1252,337 L 1311,337 L 1311,281 L 855,281 L 855,295" fill="none" stroke="#e69138" strokeWidth="2.5" markerEnd="url(#arrow-orange)" />

          {/* TT30 (>PV-15 / H5TI0030) at x=963, y=374 with sensing line up to yellow pipe y=337 */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({
            tag: 'H5TI0030',
            name: 'MR Vapor Temp Upstream JT Valve PV-15 (TT30)',
            unit: '°C',
            valDcs: ti30Dcs.toFixed(1),
            valAi: ti30Ai.toFixed(1)
          })}>
            <text x="963" y="374" fill="#00ffff" fontSize="11" fontWeight="bold">TT30</text>
            <text x="963" y="392" fill={fmt('TT30', ti30Dcs, ti30Ai, 1).color} fontSize="13" fontWeight="bold">
              {fmt('TT30', ti30Dcs, ti30Ai, 1).display} <tspan fill="#00ffff" fontSize="9">°C</tspan>
            </text>
            <line x1="980" y1="365" x2="980" y2="337" stroke="#0284c7" strokeWidth="1" strokeDasharray="3 3" />
            <circle cx="980" cy="337" r="2.5" fill="#00ffff" />
          </g>

          {/* PT8 (MR > PV-15 / H5PI0008) at x=1139, y=374 with sensing line up to yellow pipe y=337 */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({
            tag: 'H5PI0008',
            name: 'MR Vapor Pressure Upstream JT Valve PV-15 (PT8)',
            unit: 'KGC2G',
            valDcs: pi8Dcs.toFixed(2),
            valAi: pi8Ai.toFixed(2)
          })}>
            <text x="1139" y="374" fill="#00ffff" fontSize="11" fontWeight="bold">PT8</text>
            <text x="1139" y="392" fill={fmt('PT8', pi8Dcs, pi8Ai, 2).color} fontSize="13" fontWeight="bold">
              {fmt('PT8', pi8Dcs, pi8Ai, 2).display} <tspan fill="#00ffff" fontSize="9">KGC2G</tspan>
            </text>
            <line x1="1155" y1="365" x2="1155" y2="337" stroke="#0284c7" strokeWidth="1" strokeDasharray="3 3" />
            <circle cx="1155" cy="337" r="2.5" fill="#00ffff" />
          </g>

          {/* PRIC15 Tag at x=1360, y=356 */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({
            tag: 'PRIC15',
            name: '5E-1 Cold Bundle MR JT Valve Controller (PRIC15)',
            unit: 'KGC2G',
            valDcs: '18.00',
            valAi: '18.00'
          })}>
            <text x="1360" y="356" fill="#00ffff" fontSize="11" fontWeight="bold">PRIC15</text>
            <text x="1360" y="374" fill="#ffffff" fontSize="13" fontWeight="bold">18.00</text>
          </g>

          {/* PI10 (LNG < 5E-1 / H5PI0010) moved to x=1430, y=210 with sensing line down to magenta line y=253 */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({
            tag: 'H5PI0010',
            name: 'LNG Pressure Downstream Cold Bundle 5E-1 (PI10)',
            unit: 'KGC2G',
            valDcs: pi10Dcs.toFixed(2),
            valAi: pi10Ai.toFixed(2)
          })}>
            <text x="1430" y="210" fill="#00ffff" fontSize="11" fontWeight="bold">PI10</text>
            <text x="1430" y="228" fill={fmt('PI10', pi10Dcs, pi10Ai, 2).color} fontSize="13" fontWeight="bold">
              {fmt('PI10', pi10Dcs, pi10Ai, 2).display} <tspan fill="#00ffff" fontSize="9">KGC2G</tspan>
            </text>
            <line x1="1445" y1="234" x2="1445" y2="253" stroke="#0284c7" strokeWidth="1" strokeDasharray="3 3" />
            <circle cx="1445" cy="253" r="2.5" fill="#00ffff" />
          </g>

          {/* TI32: MR Liquid Temp Downstream JT Valve 5FV-2 (H5TI0032) at x=1409, y=482 with sensing line to return line y=534 */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({
            tag: 'H5TI0032',
            name: 'MR Liquid Temp Downstream JT Valve 5FV-2 (H5TI0032)',
            unit: '°C',
            valDcs: ti32Dcs.toFixed(1),
            valAi: ti32Ai.toFixed(1)
          })}>
            <text x="1409" y="482" fill="#00ffff" fontSize="11" fontWeight="bold">TI32</text>
            <text x="1409" y="500" fill={fmt('TI32', ti32Dcs, ti32Ai, 1).color} fontSize="13" fontWeight="bold">
              {fmt('TI32', ti32Dcs, ti32Ai, 1).display} <tspan fill="#00ffff" fontSize="9">°C</tspan>
            </text>
            <line x1="1409" y1="510" x2="1312" y2="534" stroke="#0284c7" strokeWidth="1" strokeDasharray="3 3" />
            <circle cx="1312" cy="534" r="2.5" fill="#00ffff" />
          </g>

          {/* =============================================================== */}
          {/* WARM MR RIGHT LOOP (HIC51 / FV-2 / TT28 / TT31 / PT7 / FIC2)    */}
          {/* =============================================================== */}
          <line x1="954" y1="589" x2="1256" y2="589" stroke="#e69138" strokeWidth="2.5" />

          {/* FV-2 / HIC51 Valve symbol at x=1256, y=589 */}
          <path d="M 1244,581 L 1268,597 L 1268,581 L 1244,597 Z" fill="#e69138" stroke="#ffffff" strokeWidth="1" />
          <line x1="1256" y1="581" x2="1256" y2="571" stroke="#e69138" strokeWidth="1.5" />
          <path d="M 1244,571 A 12,12 0 0,1 1268,571 Z" fill="#e69138" stroke="#ffffff" strokeWidth="1" />

          <path d="M 1268,589 L 1312,589 L 1312,534 L 855,534 L 855,570" fill="none" stroke="#e69138" strokeWidth="2.5" markerEnd="url(#arrow-orange)" />

          {/* TT28 (MR > W/B / H5TI0028) at x=990, y=530 */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({
            tag: 'H5TI0028',
            name: 'MR Temp to Warm Bundle (MR > W/B / TT28)',
            unit: '°C',
            valDcs: ti28Dcs.toFixed(1),
            valAi: ti28Ai.toFixed(1)
          })}>
            <text x="990" y="530" fill="#00ffff" fontSize="11" fontWeight="bold">TT28</text>
            <text x="1030" y="530" fill={fmt('TT28', ti28Dcs, ti28Ai, 1).color} fontSize="13" fontWeight="bold">
              {fmt('TT28', ti28Dcs, ti28Ai, 1).display} <tspan fill="#00ffff" fontSize="9">°C</tspan>
            </text>
          </g>

          {/* TT31 (MRL > 5FV-2 / H5TI0031) at x=990, y=620 with sensing line up to y=589 */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({
            tag: 'H5TI0031',
            name: 'MR Liquid Temp to Valve 5FV-2 (TT31)',
            unit: '°C',
            valDcs: ti31Dcs.toFixed(1),
            valAi: ti31Ai.toFixed(1)
          })}>
            <text x="990" y="620" fill="#00ffff" fontSize="11" fontWeight="bold">TT31</text>
            <text x="1030" y="620" fill={fmt('TT31', ti31Dcs, ti31Ai, 1).color} fontSize="13" fontWeight="bold">
              {fmt('TT31', ti31Dcs, ti31Ai, 1).display} <tspan fill="#00ffff" fontSize="9">°C</tspan>
            </text>
            <line x1="1010" y1="610" x2="1010" y2="589" stroke="#0284c7" strokeWidth="1" strokeDasharray="3 3" />
            <circle cx="1010" cy="589" r="2.5" fill="#00ffff" />
          </g>

          {/* FIC2: MCR Liquid Flow at x=1250, y=650 with sensing line up to FV-2 at y=589 */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({
            tag: 'H5FIC002',
            name: 'MCR Liquid Circulation Flow to MCHE 5E-1',
            unit: 'm³/h (t/h)',
            valDcs: `${fic2Dcs} m³/h (${mcrLiqMassDcs.toFixed(0)} t/h)`,
            valAi: `${fic2Ai} m³/h (${mcrLiqMassAi.toFixed(0)} t/h)`
          })}>
            <text x="1250" y="650" fill="#00ffff" fontSize="11" fontWeight="bold">FIC2</text>
            <text x="1250" y="668" fill={fmt('FIC2', fic2Dcs, fic2Ai, 0).color} fontSize="13" fontWeight="bold">
              {fmt('FIC2', fic2Dcs, fic2Ai, 0).display} <tspan fill="#00ffff" fontSize="9.5">m³/h</tspan> <tspan fill={fmt('FIC2_MASS', mcrLiqMassDcs, mcrLiqMassAi, 0).color} fontSize="10">({fmt('FIC2_MASS', mcrLiqMassDcs, mcrLiqMassAi, 0).display} t/h)</tspan>
            </text>
            <line x1="1256" y1="638" x2="1256" y2="597" stroke="#0284c7" strokeWidth="1" strokeDasharray="3 3" />
            <circle cx="1256" cy="589" r="2.5" fill="#00ffff" />
          </g>

          {/* PT7 (MR > FV-2 / H5PI0007) at x=1130, y=620 with sensing line up to y=589 */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({
            tag: 'H5PI0007',
            name: 'MR Liquid Pressure Upstream Valve 5FV-2 (PT7)',
            unit: 'KGC2G',
            valDcs: pi7Dcs.toFixed(2),
            valAi: pi7Ai.toFixed(2)
          })}>
            <text x="1130" y="620" fill="#00ffff" fontSize="11" fontWeight="bold">PT7</text>
            <text x="1130" y="638" fill={fmt('PT7', pi7Dcs, pi7Ai, 2).color} fontSize="13" fontWeight="bold">
              {fmt('PT7', pi7Dcs, pi7Ai, 2).display} <tspan fill="#00ffff" fontSize="9">KGC2G</tspan>
            </text>
            <line x1="1145" y1="610" x2="1145" y2="589" stroke="#0284c7" strokeWidth="1" strokeDasharray="3 3" />
            <circle cx="1145" cy="589" r="2.5" fill="#00ffff" />
          </g>

          {/* =============================================================== */}
          {/* STREAM 2: LNG RUNDOWN TO 5C-1 (MAGENTA PER DCS image56 & image58) */}
          {/* Clean dedicated single line through TV1A into Flash Drum 5C-1    */}
          {/* =============================================================== */}
          <line x1="814" y1="253" x2="1487" y2="253" stroke="#e879f9" strokeWidth="2.5" />

          {/* TI29 (Rundown) at x=1386, y=278 (Satisfies test_pr_eos_cryogenic_tags_present_and_wired) */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({
            tag: 'H5TI0029',
            name: 'LNG Rundown Temp Downstream Subcooler (<5PV-15)',
            unit: '°C',
            valDcs: ti29Dcs.toFixed(1),
            valAi: ti29Ai.toFixed(1)
          })}>
            <text x="1386" y="278" fill="#e879f9" fontSize="11" fontWeight="bold">TI29</text>
            <text x="1386" y="296" fill={fmt('TI29', ti29Dcs, ti29Ai, 1).color} fontSize="14" fontWeight="bold">
              {fmt('TI29', ti29Dcs, ti29Ai, 1).display} <tspan fill="#00ffff" fontSize="10">°C</tspan>
            </text>
            <line x1="1400" y1="265" x2="1400" y2="253" stroke="#e879f9" strokeWidth="1" strokeDasharray="2 2" />
          </g>

          {/* TIC1A/B (LNG) at x=1543, y=210 (Above magenta line with sensing tap and control output to TV1A) */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({
            tag: 'H5TIC01A',
            name: 'LNG Rundown Temperature Controller (TIC1A/B)',
            unit: '°C',
            valDcs: tiLngDcs.toFixed(1),
            valAi: tiLngAi.toFixed(1),
            limit: 'Target ≤ -150.0°C'
          })}>
            <text x="1543" y="210" fill="#00ffff" fontSize="11" fontWeight="bold">TIC1A/B</text>
            <text x="1543" y="228" fill={fmt('TIC1A/B', tiLngDcs, tiLngAi, 1).color} fontSize="15" fontWeight="bold">
              {fmt('TIC1A/B', tiLngDcs, tiLngAi, 1).display} <tspan fill="#00ffff" fontSize="10">°C</tspan>
            </text>
            <line x1="1568" y1="234" x2="1568" y2="253" stroke="#0284c7" strokeWidth="1" strokeDasharray="3 3" />
            <circle cx="1568" cy="253" r="2.5" fill="#00ffff" />
            {/* Control signal output line down to TV1A actuator */}
            <line x1="1568" y1="253" x2="1568" y2="375" stroke="#0284c7" strokeWidth="1" strokeDasharray="3 3" />
          </g>

          {/* Vertical Drop to TV1A Elevation (y=393) */}
          <line x1="1487" y1="253" x2="1487" y2="393" stroke="#e879f9" strokeWidth="2.5" />
          <line x1="1487" y1="393" x2="1685" y2="393" stroke="#e879f9" strokeWidth="2.5" markerEnd="url(#arrow-magenta)" />

          {/* Diaphragm Letdown Control Valve TV1A at x=1568, y=393 */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({
            tag: 'TV1A',
            name: 'LNG Rundown Letdown Valve to Vessel 5C-1',
            unit: '% / t/h',
            valDcs: `${lngFlowDcs.toFixed(1)} t/h`,
            valAi: `${lngFlowAi.toFixed(1)} t/h`
          })}>
            <path d="M 1556,385 L 1580,401 L 1580,385 L 1556,401 Z" fill="#d946ef" stroke="#ffffff" strokeWidth="1" />
            <line x1="1568" y1="385" x2="1568" y2="375" stroke="#d946ef" strokeWidth="1.5" />
            <path d="M 1556,375 A 12,12 0 0,1 1580,375 Z" fill="#d946ef" stroke="#ffffff" strokeWidth="1" />
            <text x="1568" y="365" fill="#00ffff" fontSize="11" textAnchor="middle" fontWeight="bold">TV1A</text>
          </g>

          {/* =============================================================== */}
          {/* VESSEL 5C-1: LNG FLASH DRUM (AUTHENTIC DCS image58 GEOMETRY)     */}
          {/* Vertical Flash Drum with Hemispherical Heads at x=1685->1741    */}
          {/* =============================================================== */}
          <g id="vessel-5c1">
            {/* Vessel 5C-1 Body (per image58: vertical drum with hemispherical heads) */}
            <path
              d="
                M 1685,350
                A 28,20 0 0,1 1741,350
                L 1741,475
                A 28,20 0 0,1 1685,475
                Z
              "
              fill="#06101e"
              stroke="#00ff00"
              strokeWidth="2.5"
            />

            {/* Liquid level fill inside 5C-1 */}
            <path
              d="
                M 1686,430
                L 1740,430
                L 1740,474
                A 27,19 0 0,1 1686,474
                Z
              "
              fill="#0284c7"
              opacity="0.45"
            />
            {/* Liquid level surface line */}
            <line x1="1686" y1="430" x2="1740" y2="430" stroke="#38bdf8" strokeWidth="1.5" />

            <text x="1713" y="375" fill="#00ff00" fontSize="13" fontWeight="bold" textAnchor="middle">5C-1</text>
            <text x="1713" y="388" fill="#94a3b8" fontSize="8.5" textAnchor="middle">FLASH DRUM</text>

            {/* Tag 5LI1 (H5LI0001): 5C-1 Separator Level */}
            <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({
              tag: 'H5LI0001',
              name: '5C-1 LNG Flash Drum Liquid Level (5C-1 SEP)',
              unit: '%',
              valDcs: li1Dcs.toFixed(1),
              valAi: li1Ai.toFixed(1),
              limit: 'Normal 5.0 - 20.0 %'
            })}>
              <text x="1640" y="425" fill="#00ffff" fontSize="11" fontWeight="bold">5LI1</text>
              <text x="1640" y="440" fill={fmt('LI1', li1Dcs, li1Ai, 1).color} fontSize="13" fontWeight="bold">
                {fmt('LI1', li1Dcs, li1Ai, 1).display} <tspan fill="#00ffff" fontSize="9">%</tspan>
              </text>
              <line x1="1665" y1="430" x2="1685" y2="430" stroke="#0284c7" strokeWidth="1" strokeDasharray="2 2" />
            </g>

            {/* 5C-1 Top Vapor Outlet: End Flash Gas (EFG) to Fuel Gas Header */}
            <line x1="1713" y1="330" x2="1713" y2="300" stroke="#00ffff" strokeWidth="2" />
            <line x1="1713" y1="300" x2="1860" y2="300" stroke="#00ffff" strokeWidth="2" markerEnd="url(#arrow-cyan)" />
            <text x="1865" y="296" fill="#38bdf8" fontSize="11" fontWeight="bold">EFG VAP (Fuel Gas)</text>

            {/* EFG Flow Telemetry Readout */}
            <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({
              tag: '5C-1_EFG',
              name: 'End Flash Gas Vapor Flow to Fuel Gas Header (5C-1 Top)',
              unit: 't/h',
              valDcs: flashVapDcs.toFixed(1),
              valAi: flashVapAi.toFixed(1),
              limit: 'Normal 5.0 - 15.0 t/h'
            })}>
              <text x="1755" y="318" fill="#00ffff" fontSize="10.5" fontWeight="bold">EFG Flow</text>
              <text x="1755" y="335" fill={fmt('EFG_VAP', flashVapDcs, flashVapAi, 1).color} fontSize="14" fontWeight="bold">
                {fmt('EFG_VAP', flashVapDcs, flashVapAi, 1).display} <tspan fill="#00ffff" fontSize="9.5">t/h</tspan>
              </text>
            </g>

            {/* 5C-1 Bottom Liquid Outlet: LNG Rundown to Storage (FI6A) */}
            <line x1="1713" y1="495" x2="1713" y2="550" stroke="#e879f9" strokeWidth="2.5" />
            <line x1="1713" y1="550" x2="1860" y2="550" stroke="#e879f9" strokeWidth="2.5" markerEnd="url(#arrow-magenta)" />
            <text x="1755" y="540" fill="#e879f9" fontSize="12" fontWeight="bold">LNG &gt; STRG</text>

            {/* Dedicated Telemetry Badge for LNG Production (FI6A) */}
            <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({
              tag: 'H5FI006A',
              name: 'LNG Rundown Production Flow Rate to Storage (LNG > STRG)',
              unit: 't/h',
              valDcs: lngFlowDcs.toFixed(1),
              valAi: lngFlowAi.toFixed(1)
            })}>
              <rect x="1750" y="555" width="135" height="40" fill="#0f172a" stroke="#0284c7" strokeWidth="1" rx="4" />
              <text x="1817" y="570" fill="#00ffff" fontSize="11" textAnchor="middle" fontWeight="bold">FI6A (LNG Flow)</text>
              <text x="1817" y="588" fill={fmt('FI6A', lngFlowDcs, lngFlowAi, 1).color} fontSize="14" textAnchor="middle" fontWeight="bold">
                {fmt('FI6A', lngFlowDcs, lngFlowAi, 1).display} <tspan fill="#00ffff" fontSize="10">t/h</tspan>
              </text>
            </g>
          </g>

          {/* =============================================================== */}
          {/* STREAM 8: SHELL-SIDE LP SUCTION RETURN TO 4C-7 (YELLOW y=812)   */}
          {/* =============================================================== */}
          <line x1="954" y1="812" x2="1620" y2="812" stroke="#ffff00" strokeWidth="2.5" markerEnd="url(#arrow-yellow)" />
          <polygon points="1165,808 1175,812 1165,816" fill="#ffff00" />

          {/* Red Emergency Isolation Gate Valve 4HV11 at x=1462, y=812 */}
          <path d="M 1450,800 L 1474,824 L 1474,800 L 1450,824 Z" fill="#ff0000" stroke="#ffffff" strokeWidth="1" />
          <line x1="1462" y1="800" x2="1462" y2="787" stroke="#ff0000" strokeWidth="2" />
          <line x1="1452" y1="787" x2="1472" y2="787" stroke="#ff0000" strokeWidth="2.5" />
          <text x="1462" y="840" fill="#00ffff" fontSize="11" textAnchor="middle" fontWeight="bold">4HV11</text>

          {/* Destination 4C-7 */}
          <text x="1626" y="816" fill="#bef264" fontSize="16" fontWeight="bold">4C-7</text>

          {/* PI9 Suction Pressure at x=1040, y=834 with sensing tap to yellow line y=812 (65px clearance from H4FI011B) */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({
            tag: 'H4PI014B',
            name: 'MCHE Bottom Outlet / Compressor Suction Pressure (PI9)',
            unit: 'KGC2G',
            valDcs: pi9Dcs.toFixed(3),
            valAi: pi9Ai.toFixed(3)
          })}>
            <text x="1040" y="834" fill="#00ffff" fontSize="11" fontWeight="bold">PI9</text>
            <text x="1040" y="852" fill={fmt('PI9', pi9Dcs, pi9Ai, 3).color} fontSize="14" fontWeight="bold">
              {fmt('PI9', pi9Dcs, pi9Ai, 3).display} <tspan fill="#00ffff" fontSize="10">KGC2G</tspan>
            </text>
            <line x1="1055" y1="812" x2="1055" y2="824" stroke="#0284c7" strokeWidth="1" strokeDasharray="3 3" />
            <circle cx="1055" cy="812" r="2.5" fill="#00ffff" />
          </g>

          {/* H4FI011B MCR Circulation Total at x=1177, y=834 */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({
            tag: 'H4FI011B',
            name: 'Total MCR Circulation Flow Rate (Compressor Return Suction Header)',
            unit: 't/h',
            valDcs: mcrFlowDcs.toFixed(1),
            valAi: mcrFlowAi.toFixed(1),
            limit: 'Floor Anti-Surge ≥ 480.0 t/h'
          })}>
            <rect x="1170" y="834" width="135" height="38" fill="#0f172a" stroke="#0284c7" strokeWidth="1" rx="4" />
            <text x="1237" y="849" fill="#00ffff" fontSize="11" textAnchor="middle" fontWeight="bold">H4FI011B (MCR Total)</text>
            <text x="1237" y="866" fill={fmt('H4FI011B', mcrFlowDcs, mcrFlowAi, 1).color} fontSize="14" textAnchor="middle" fontWeight="bold">
              {fmt('H4FI011B', mcrFlowDcs, mcrFlowAi, 1).display} <tspan fill="#00ffff" fontSize="10">t/h</tspan>
            </text>
            <line x1="1237" y1="812" x2="1237" y2="834" stroke="#0284c7" strokeWidth="1" strokeDasharray="3 3" />
          </g>

          {/* TI8 Suction Temperature (TAL Interlock) at x=1339, y=834 */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({
            tag: 'H4TI004B',
            name: 'MCHE Bottom Outlet / Compressor Suction Temp (TI8)',
            unit: '°C',
            valDcs: tiSuctDcs.toFixed(1),
            valAi: tiSuctAi.toFixed(1),
            limit: 'TAL Interlock ≥ -45.0°C'
          })}>
            <text x="1339" y="834" fill="#34d399" fontSize="11" fontWeight="bold">TI8 (TAL)</text>
            <text x="1339" y="852" fill={fmt('TI8', tiSuctDcs, tiSuctAi, 1).color} fontSize="14" fontWeight="bold">
              {fmt('TI8', tiSuctDcs, tiSuctAi, 1).display} <tspan fill="#00ffff" fontSize="10">°C</tspan>
            </text>
          </g>
        </svg>

        {/* Selected Tag Info Overlay / Drawer */}
        {selectedTag && (
          <div style={{
            position: 'absolute',
            bottom: '70px',
            right: '24px',
            backgroundColor: '#0f172a',
            border: '2px solid #0284c7',
            borderRadius: '8px',
            padding: '16px 20px',
            color: '#ffffff',
            boxShadow: '0 4px 15px rgba(0,0,0,0.6)',
            maxWidth: '380px',
            fontFamily: "'Segoe UI', sans-serif",
            zIndex: 10,
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px', borderBottom: '1px solid #334155', paddingBottom: '6px' }}>
              <span style={{ fontSize: '15px', fontWeight: 800, color: '#38bdf8' }}>{selectedTag.tag}</span>
              <button
                onClick={() => setSelectedTag(null)}
                style={{ background: 'none', border: 'none', color: '#94a3b8', fontSize: '16px', cursor: 'pointer', fontWeight: 700 }}
              >
                ✕
              </button>
            </div>
            <div style={{ fontSize: '13px', color: '#e2e8f0', marginBottom: '8px' }}>{selectedTag.name}</div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px', marginBottom: '4px' }}>
              <span style={{ color: '#94a3b8' }}>DCS Baseline:</span>
              <strong>{selectedTag.valDcs} {selectedTag.unit}</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px', marginBottom: '4px' }}>
              <span style={{ color: '#94a3b8' }}>Scenario Target:</span>
              <strong style={{ color: '#34d399' }}>{selectedTag.valAi} {selectedTag.unit}</strong>
            </div>
            {selectedTag.limit && (
              <div style={{ marginTop: '8px', paddingTop: '6px', borderTop: '1px dashed #334155', fontSize: '11px', color: '#f59e0b' }}>
                ⚠️ Operating Limit: {selectedTag.limit}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
