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

type DcsDisplayMode = 'DCS_ACTUAL' | 'AI_OPTIMIZED' | 'DELTA_DIFF';

interface TagInfo {
  tag: string;
  name: string;
  unit: string;
  valDcs: number | string;
  valAi: number | string;
  limit?: string;
  status?: 'SAFE' | 'WARNING' | 'ALARM';
}

export const TabGrafik: React.FC<TabGrafikProps> = ({
  snapshot: _snapshot,
  scenario,
  actualDcs,
  optimum,
  prediction,
  userMode: _userMode = 'OPERATOR',
}) => {
  const [displayMode, setDisplayMode] = useState<DcsDisplayMode>('AI_OPTIMIZED');
  const [selectedTag, setSelectedTag] = useState<TagInfo | null>(null);

  // Flow values
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
  // Replaces all hardcoded static multipliers (0.360 / 0.640 / 0.4113) with first-principles VLE.
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

  // Propane Precooling Cycle (4K-1 Stage 1 Suction Flow H4FI001A & Chillers 3E-14/17/18)
  const c3PrecoolFlowDcs = 212.5;
  const c3PrecoolFlowAi = 212.5;

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

  const ti29Dcs = -153.6; // H5TI0029: Suhu LNG Rundown Downstream Subcooler (<5PV-15)
  const ti29Ai = -153.8;

  // DCS Mimic GRH0065 Audited Instrumentation Tags
  const ti28Dcs = -129.5; // H5TI0028: MR > W/B (TT28)
  const ti28Ai = -128.0;

  const ti31Dcs = -127.2; // H5TI0031: MRL > 5FV-2 (TT31)
  const ti31Ai = -126.0;

  const ti30Dcs = -149.9; // H5TI0030: MR V > PV-15 sebelum JT Valve (TT30)
  const ti30Ai = -150.2;

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

  const ti27Dcs = -126.3; // H5TI0027: F/G > C/B (TI27)
  const ti27Ai = -125.5;

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
              Daya: <strong style={{ color: '#fbbf24' }}>{totalPower.toFixed(2)}</strong> <span style={{ color: '#64748b' }}>MW</span>
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
                  backgroundColor: displayMode === 'DCS_ACTUAL' ? '#0369a1' : 'transparent',
                  color: displayMode === 'DCS_ACTUAL' ? '#ffffff' : '#94a3b8',
                  border: 'none',
                  borderRadius: '3px',
                  padding: '3px 9px',
                  fontSize: '11px',
                  fontWeight: 700,
                  cursor: 'pointer',
                  transition: 'all 0.15s ease',
                }}
                title="Tampilkan nilai riil DCS Aktual"
              >
                Aktual
              </button>
              <button
                type="button"
                onClick={() => setDisplayMode('AI_OPTIMIZED')}
                style={{
                  backgroundColor: displayMode === 'AI_OPTIMIZED' ? '#065f46' : 'transparent',
                  color: displayMode === 'AI_OPTIMIZED' ? '#34d399' : '#94a3b8',
                  border: 'none',
                  borderRadius: '3px',
                  padding: '3px 9px',
                  fontSize: '11px',
                  fontWeight: 700,
                  cursor: 'pointer',
                  transition: 'all 0.15s ease',
                }}
                title="Tampilkan nilai Skenario Rekomendasi MCR"
              >
                Skenario
              </button>
              <button
                type="button"
                onClick={() => setDisplayMode('DELTA_DIFF')}
                style={{
                  backgroundColor: displayMode === 'DELTA_DIFF' ? '#78350f' : 'transparent',
                  color: displayMode === 'DELTA_DIFF' ? '#fcd34d' : '#94a3b8',
                  border: 'none',
                  borderRadius: '3px',
                  padding: '3px 9px',
                  fontSize: '11px',
                  fontWeight: 700,
                  cursor: 'pointer',
                  transition: 'all 0.15s ease',
                }}
                title="Tampilkan selisih Skenario terhadap Aktual (Delta Δ)"
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

        {/* SVG Centum Graphic Area (Native DCS Coordinate System: 1920 x 800) */}
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

          {/* Title Header on Canvas matching Centum DCS GRH0065 */}
          <text x="960" y="168" fill="#ffffff" fontSize="22" fontWeight="bold" textAnchor="middle" letterSpacing="4">
            MAIN HEAT EXCHANGER (5E-1)
          </text>

          {/* =============================================================== */}
          {/* PROPANE PRECOOLING CYCLE (4K-1 / H4FI001A & CHILLERS 3E-14/17/18) */}
          {/* =============================================================== */}
          <g
            style={{ cursor: 'pointer' }}
            onClick={() => handleTagClick({
              tag: 'H4FI001A',
              name: '4K-1 Propane Precooling Compressor Stage 1 Suction Flow',
              unit: 'kNm³/h',
              valDcs: c3PrecoolFlowDcs.toFixed(1),
              valAi: c3PrecoolFlowAi.toFixed(1),
              limit: 'Floor Anti-Surge ≥ 155.0 kNm³/h (Chillers 3E-14/17/18: -35.0°C)'
            })}
          >
            <rect x="40" y="320" width="200" height="140" fill="#0b1329" stroke="#0284c7" strokeWidth="1.5" rx="6" />
            <rect x="40" y="320" width="200" height="24" fill="#1e293b" rx="6" />
            <rect x="40" y="338" width="200" height="6" fill="#1e293b" />
            <text x="140" y="336" fill="#38bdf8" fontSize="10.5" fontWeight="bold" textAnchor="middle">
              4K-1 C3 PRECOOLING CYCLE
            </text>

            <text x="50" y="358" fill="#94a3b8" fontSize="10">Stage 1 Suct (H4FI001A):</text>
            <text x="50" y="375" fill={fmt('H4FI001A', c3PrecoolFlowDcs, c3PrecoolFlowAi, 1).color} fontSize="13" fontWeight="bold">
              {fmt('H4FI001A', c3PrecoolFlowDcs, c3PrecoolFlowAi, 1).display} <tspan fill="#00ffff" fontSize="10">kNm³/h</tspan>
            </text>

            <text x="50" y="396" fill="#94a3b8" fontSize="10">MCR Chillers 3E-14/17/18:</text>
            <text x="50" y="411" fill="#34d399" fontSize="11" fontWeight="bold">
              -35.0°C <tspan fill="#94a3b8" fontSize="9.5">(Precooled MCR)</tspan>
            </text>

            <text x="50" y="430" fill="#94a3b8" fontSize="10">Feed Chillers 4E-10/12/14:</text>
            <text x="50" y="445" fill="#34d399" fontSize="11" fontWeight="bold">
              -35.0°C <tspan fill="#94a3b8" fontSize="9.5">(Treated Feed)</tspan>
            </text>

            <line x1="240" y1="395" x2="265" y2="395" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="3 3" />
            <line x1="265" y1="395" x2="265" y2="480" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="3 3" />
          </g>

          {/* =============================================================== */}
          {/* VESSEL 5C-2: MCR HIGH-PRESSURE PHASE SEPARATOR (VAPOR / LIQUID)  */}
          {/* =============================================================== */}
          <g>
            {/* Precooled MCR Inflow into 5C-2 */}
            <line x1="95" y1="595" x2="135" y2="595" stroke="#0284c7" strokeWidth="2" strokeDasharray="3 3" />
            
            {/* Vessel 5C-2 Body */}
            <rect x="135" y="530" width="50" height="130" fill="#06101e" stroke="#00ff00" strokeWidth="2.5" />
            <path d="M 135,530 A 25,20 0 0,1 185,530" fill="#06101e" stroke="#00ff00" strokeWidth="2.5" />
            <path d="M 135,660 A 25,20 0 0,0 185,660" fill="#06101e" stroke="#00ff00" strokeWidth="2.5" />
            
            {/* Liquid level fill inside 5C-2 */}
            <rect x="136" y="585" width="48" height="70" fill="#0284c7" opacity="0.45" />

            <text x="160" y="565" fill="#00ff00" fontSize="14" fontWeight="bold" textAnchor="middle">5C-2</text>
            <text x="160" y="578" fill="#94a3b8" fontSize="8.5" textAnchor="middle">MCR SEP</text>

            {/* Tag H5LIC007: Level Controller 5C-2 */}
            <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({
              tag: 'H5LIC007',
              name: '5C-2 MCR High-Pressure Separator Level Controller',
              unit: '%',
              valDcs: lic7Dcs.toFixed(1),
              valAi: lic7Ai.toFixed(1),
              limit: 'Normal 40.0 - 65.0 %'
            })}>
              <rect x="35" y="575" width="85" height="36" fill="#0f172a" stroke="#0284c7" strokeWidth="1" rx="4" />
              <text x="77" y="590" fill="#00ffff" fontSize="10.5" textAnchor="middle" fontWeight="bold">H5LIC007</text>
              <text x="77" y="605" fill={fmt('H5LIC007', lic7Dcs, lic7Ai, 1).color} fontSize="13" textAnchor="middle" fontWeight="bold">
                {fmt('H5LIC007', lic7Dcs, lic7Ai, 1).display} <tspan fill="#00ffff" fontSize="9">%</tspan>
              </text>
              <line x1="120" y1="593" x2="135" y2="593" stroke="#0284c7" strokeWidth="1" strokeDasharray="2 2" />
            </g>
          </g>

          {/* =============================================================== */}
          {/* MAIN VESSEL: MCHE 5E-1 (STEPPED SWAGE GEOMETRY PER DCS GRH0065)  */}
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
            strokeWidth="3"
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

          {/* LI2 Readout Badge beside Cold Spray Tray */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({
            tag: 'H5LI0002',
            name: 'Cold Bundle Separator Liquid Level (5E-1 C/B SEP)',
            unit: '%',
            valDcs: li2Dcs.toFixed(1),
            valAi: li2Ai.toFixed(1),
            limit: 'Normal 25.0 - 50.0 %'
          })}>
            <rect x="895" y="285" width="60" height="24" fill="#0b1329" stroke="#0284c7" strokeWidth="1" rx="3" />
            <text x="925" y="301" fill={fmt('LI2', li2Dcs, li2Ai, 1).color} fontSize="11" textAnchor="middle" fontWeight="bold">
              LI2 <tspan fill="#00ffff">{fmt('LI2', li2Dcs, li2Ai, 1).display}%</tspan>
            </text>
          </g>

          {/* Warm Spray Tray LI3 (U-cup) */}
          <path d="M 830,560 L 830,595 L 880,595 L 880,560" fill="none" stroke="#00ff00" strokeWidth="2" />
          <rect x="831" y="575" width="48" height="19" fill="#0284c7" opacity="0.45" />
          <text x="855" y="612" fill="#00ffff" fontSize="13" textAnchor="middle" fontWeight="bold">x   x   x</text>

          {/* LI3 Readout Badge beside Warm Spray Tray */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({
            tag: '5LI0003',
            name: 'Warm Bundle Separator Liquid Level (5E-1 W/B SEP)',
            unit: '%',
            valDcs: li3Dcs.toFixed(1),
            valAi: li3Ai.toFixed(1),
            limit: 'Normal 35.0 - 60.0 %'
          })}>
            <rect x="895" y="560" width="60" height="24" fill="#0b1329" stroke="#0284c7" strokeWidth="1" rx="3" />
            <text x="925" y="576" fill={fmt('LI3', li3Dcs, li3Ai, 1).color} fontSize="11" textAnchor="middle" fontWeight="bold">
              LI3 <tspan fill="#00ffff">{fmt('LI3', li3Dcs, li3Ai, 1).display}%</tspan>
            </text>
          </g>

          {/* Equipment Label 5E-1 in Bottom Sump */}
          <text x="855" y="785" fill="#00ff00" fontSize="20" fontWeight="bold" textAnchor="middle">
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
          <line x1="814" y1="440" x2="814" y2="245" stroke="#ff0000" strokeWidth="2" strokeDasharray="5 3" />
          <line x1="814" y1="245" x2="915" y2="245" stroke="#e879f9" strokeWidth="2.5" />

          {/* Warm MR internal riser (Yellow) */}
          <line x1="755" y1="784" x2="934" y2="784" stroke="#ffff00" strokeWidth="2" />
          <line x1="934" y1="784" x2="934" y2="520" stroke="#ffff00" strokeWidth="1.8" strokeDasharray="4 3" />
          <line x1="934" y1="520" x2="894" y2="440" stroke="#ffff00" strokeWidth="1.8" strokeDasharray="4 3" />
          <line x1="894" y1="440" x2="894" y2="337" stroke="#ffff00" strokeWidth="1.8" strokeDasharray="4 3" />

          {/* =============================================================== */}
          {/* STREAM 1: FEED GAS INLET (RED LINE y=841)                       */}
          {/* =============================================================== */}
          <text x="145" y="836" fill="#ff0000" fontSize="14" fontWeight="bold">FEED</text>
          <text x="145" y="852" fill="#ff0000" fontSize="14" fontWeight="bold">GAS</text>
          <line x1="180" y1="841" x2="755" y2="841" stroke="#ff0000" strokeWidth="2.5" markerEnd="url(#arrow-red)" />
          <line x1="240" y1="841" x2="240" y2="865" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="3 3" />
          <line x1="390" y1="841" x2="390" y2="865" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="3 3" />
          <line x1="540" y1="841" x2="540" y2="865" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="3 3" />

          {/* =============================================================== */}
          {/* STREAM 2: LNG RUNDOWN DIRECTLY TO 5C-1 FLASH DRUM (ZERO BYPASS) */}
          {/* =============================================================== */}
          {/* Direct clean pipe from MCHE top outlet (x=915, y=245) to 5C-1 */}
          <line x1="915" y1="245" x2="1440" y2="245" stroke="#e879f9" strokeWidth="2.5" />
          <polygon points="980,241 990,245 980,249" fill="#ff0000" />
          <line x1="1440" y1="245" x2="1440" y2="390" stroke="#e879f9" strokeWidth="2.5" />
          <line x1="1440" y1="390" x2="1590" y2="390" stroke="#e879f9" strokeWidth="2.5" markerEnd="url(#arrow-red)" />

          {/* TV1A Diaphragm Control Valve at x=1510, y=390 */}
          <path d="M 1498,382 L 1522,398 L 1522,382 L 1498,398 Z" fill="#d946ef" stroke="#ffffff" strokeWidth="1" />
          <line x1="1510" y1="382" x2="1510" y2="372" stroke="#d946ef" strokeWidth="1.5" />
          <path d="M 1498,372 A 12,12 0 0,1 1522,372 Z" fill="#d946ef" stroke="#ffffff" strokeWidth="1" />
          <text x="1510" y="362" fill="#00ffff" fontSize="12" textAnchor="middle" fontWeight="bold">TV1A</text>

          {/* 5C-1 Flash Drum Vessel Geometry */}
          <g>
            <rect x="1590" y="360" width="55" height="110" fill="#06101e" stroke="#00ff00" strokeWidth="2.5" />
            <path d="M 1590,360 A 27.5,20 0 0,1 1645,360" fill="#06101e" stroke="#00ff00" strokeWidth="2.5" />
            <path d="M 1590,470 A 27.5,20 0 0,0 1645,470" fill="#06101e" stroke="#00ff00" strokeWidth="2.5" />
            
            {/* Liquid level fill inside 5C-1 */}
            <rect x="1591" y="420" width="53" height="50" fill="#0284c7" opacity="0.45" />

            <text x="1618" y="402" fill="#00ff00" fontSize="15" fontWeight="bold" textAnchor="middle">5C-1</text>
            <text x="1618" y="415" fill="#94a3b8" fontSize="9" textAnchor="middle">FLASH DRUM</text>

            {/* Tag H5LI0001 (5LI1): 5C-1 Flash Drum Level */}
            <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({
              tag: 'H5LI0001',
              name: '5C-1 LNG Flash Drum Liquid Level (5C-1 SEP)',
              unit: '%',
              valDcs: li1Dcs.toFixed(1),
              valAi: li1Ai.toFixed(1),
              limit: 'Normal 5.0 - 20.0 %'
            })}>
              <rect x="1500" y="430" width="75" height="34" fill="#0f172a" stroke="#0284c7" strokeWidth="1" rx="4" />
              <text x="1537" y="445" fill="#00ffff" fontSize="11" textAnchor="middle" fontWeight="bold">5LI1</text>
              <text x="1537" y="459" fill={fmt('LI1', li1Dcs, li1Ai, 1).color} fontSize="13" textAnchor="middle" fontWeight="bold">
                {fmt('LI1', li1Dcs, li1Ai, 1).display} <tspan fill="#00ffff" fontSize="9">%</tspan>
              </text>
              <line x1="1575" y1="447" x2="1590" y2="447" stroke="#0284c7" strokeWidth="1" strokeDasharray="2 2" />
            </g>

            {/* 5C-1 Top Vapor Outlet: End Flash Gas (EFG) to Fuel Gas */}
            <line x1="1618" y1="340" x2="1618" y2="305" stroke="#00ffff" strokeWidth="2" />
            <line x1="1618" y1="305" x2="1690" y2="305" stroke="#00ffff" strokeWidth="2" markerEnd="url(#arrow-cyan)" />
            <text x="1695" y="295" fill="#38bdf8" fontSize="11" fontWeight="bold">EFG VAP (Fuel Gas)</text>
            
            <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({
              tag: '5C-1_EFG',
              name: 'End Flash Gas Vapor Flow ke Fuel Gas Header (5C-1 Top)',
              unit: 't/h',
              valDcs: flashVapDcs.toFixed(1),
              valAi: flashVapAi.toFixed(1),
              limit: 'Normal 5.0 - 15.0 t/h'
            })}>
              <rect x="1695" y="305" width="125" height="38" fill="#0f172a" stroke="#0284c7" strokeWidth="1" rx="4" />
              <text x="1757" y="320" fill="#00ffff" fontSize="11" textAnchor="middle" fontWeight="bold">EFG Flow</text>
              <text x="1757" y="337" fill={fmt('EFG_VAP', flashVapDcs, flashVapAi, 1).color} fontSize="15" textAnchor="middle" fontWeight="bold">
                {fmt('EFG_VAP', flashVapDcs, flashVapAi, 1).display} <tspan fill="#00ffff" fontSize="10">t/h</tspan>
              </text>
            </g>

            {/* 5C-1 Bottom Liquid Outlet: LNG Rundown to Storage */}
            <line x1="1618" y1="490" x2="1618" y2="525" stroke="#e879f9" strokeWidth="2.5" />
            <line x1="1618" y1="525" x2="1690" y2="525" stroke="#e879f9" strokeWidth="2.5" markerEnd="url(#arrow-magenta)" />
            <text x="1695" y="515" fill="#e879f9" fontSize="13" fontWeight="bold">LNG &gt; STRG</text>

            {/* FI6A: Laju Alir Produksi LNG Rundown */}
            <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({
              tag: 'H5FI006A',
              name: 'Laju Alir Produksi LNG Rundown ke Tangki Penyimpanan (LNG > STRG)',
              unit: 't/h',
              valDcs: lngFlowDcs.toFixed(1),
              valAi: lngFlowAi.toFixed(1)
            })}>
              <rect x="1695" y="525" width="125" height="40" fill="#0f172a" stroke="#0284c7" strokeWidth="1" rx="4" />
              <text x="1757" y="542" fill="#00ffff" fontSize="12" textAnchor="middle" fontWeight="bold">FI6A (LNG Flow)</text>
              <text x="1757" y="559" fill={fmt('FI6A', lngFlowDcs, lngFlowAi, 1).color} fontSize="15" textAnchor="middle" fontWeight="bold">
                {fmt('FI6A', lngFlowDcs, lngFlowAi, 1).display} <tspan fill="#00ffff" fontSize="10">t/h</tspan>
              </text>
            </g>
          </g>

          {/* =============================================================== */}
          {/* STREAM 3: MR VAPOR INLET (YELLOW LINE y=530 -> x=458 -> y=784)   */}
          {/* =============================================================== */}
          <text x="210" y="514" fill="#ffff00" fontSize="12" fontWeight="bold">MR VAP</text>
          <text x="210" y="526" fill="#ffff00" fontSize="9.5" fontWeight="bold">(Stream 3)</text>
          <line x1="185" y1="530" x2="458" y2="530" stroke="#ffff00" strokeWidth="2.5" />
          <line x1="458" y1="530" x2="458" y2="784" stroke="#ffff00" strokeWidth="2.5" />
          <polygon points="454,720 458,730 462,720" fill="#ffff00" />
          <line x1="458" y1="784" x2="755" y2="784" stroke="#ffff00" strokeWidth="2.5" markerEnd="url(#arrow-yellow)" />

          {/* FI1: MCR Vapor Flow Badge on Stream 3 */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({
            tag: 'FI1',
            name: 'MCR Vapor Flow ke MCHE 5E-1 (Warm Bundle Inlet)',
            unit: 't/h',
            valDcs: mcrVapFlowDcs.toFixed(1),
            valAi: mcrVapFlowAi.toFixed(1),
            limit: 'Coupled with H5TI0047 (-35.1°C DCS / -32.7°C Skenario)'
          })}>
            <rect x="250" y="480" width="135" height="40" fill="#0f172a" stroke="#0284c7" strokeWidth="1" rx="4" />
            <text x="317" y="496" fill="#00ffff" fontSize="11" textAnchor="middle" fontWeight="bold">FI1 (MCR Vap)</text>
            <text x="317" y="514" fill={fmt('FI1', mcrVapFlowDcs, mcrVapFlowAi, 1).color} fontSize="15" textAnchor="middle" fontWeight="bold">
              {fmt('FI1', mcrVapFlowDcs, mcrVapFlowAi, 1).display} <tspan fill="#00ffff" fontSize="10">t/h</tspan>
            </text>
          </g>

          {/* PI1: Tekanan MCR Masuk */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'H5PI0001', name: 'MCR Vapor Pressure', unit: 'KGC2G', valDcs: pi1Dcs.toFixed(2), valAi: pi1Ai.toFixed(2) })}>
            <text x="375" y="618" fill="#00ffff" fontSize="12" fontWeight="bold">PI1</text>
            <text x="375" y="638" fill={fmt('PI1', pi1Dcs, pi1Ai, 2).color} fontSize="15" fontWeight="bold">
              {fmt('PI1', pi1Dcs, pi1Ai, 2).display} <tspan fill="#00ffff" fontSize="10">KGC2G</tspan>
            </text>
          </g>

          {/* TI47: Suhu MCR Masuk (Coupled with FI1) */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'H5TI0047', name: 'MCR Vapor Inlet Temperature (Coupled with FI1)', unit: '°C', valDcs: ti47Dcs.toFixed(1), valAi: ti47Ai.toFixed(1) })}>
            <text x="375" y="670" fill="#00ffff" fontSize="12" fontWeight="bold">TI47 (Vap T)</text>
            <text x="375" y="690" fill={fmt('TI47', ti47Dcs, ti47Ai, 1).color} fontSize="15" fontWeight="bold">
              {fmt('TI47', ti47Dcs, ti47Ai, 1).display} <tspan fill="#00ffff" fontSize="10">°C</tspan>
            </text>
          </g>

          {/* =============================================================== */}
          {/* STREAM 4: MR LIQUID INLET WITH DYNAMIC PR-EOS FLOW READOUT       */}
          {/* =============================================================== */}
          <line x1="160" y1="675" x2="160" y2="760" stroke="#e69138" strokeWidth="2.5" />
          <line x1="160" y1="760" x2="755" y2="760" stroke="#e69138" strokeWidth="2.5" markerEnd="url(#arrow-orange)" />
          <text x="150" y="718" fill="#e69138" fontSize="12" fontWeight="bold" textAnchor="end">MR LIQ</text>
          <text x="150" y="732" fill="#e69138" fontSize="9.5" fontWeight="bold" textAnchor="end">(Stream 4)</text>

          {/* MRL Flow Badge on Stream 4 (PR-EOS Dynamic: Mass t/h & Volumetric m3/h) */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({
            tag: 'MRL_FLOW',
            name: 'MCR Liquid Circulation Flow ke MCHE 5E-1 (PR-EOS Phase Split)',
            unit: 't/h (m³/h)',
            valDcs: `${mcrLiqMassDcs.toFixed(1)} t/h (${fic2Dcs} m³/h)`,
            valAi: `${mcrLiqMassAi.toFixed(1)} t/h (${fic2Ai} m³/h)`,
            limit: 'PR-EOS VLE at -35.0°C, 36.90 kg/cm²G'
          })}>
            <rect x="210" y="728" width="165" height="42" fill="#0f172a" stroke="#e69138" strokeWidth="1" rx="4" />
            <text x="292" y="744" fill="#00ffff" fontSize="11" textAnchor="middle" fontWeight="bold">MRL Flow (PR-EOS)</text>
            <text x="292" y="763" fill={fmt('MRL_FLOW', mcrLiqMassDcs, mcrLiqMassAi, 1).color} fontSize="14" textAnchor="middle" fontWeight="bold">
              {fmt('MRL_FLOW', mcrLiqMassDcs, mcrLiqMassAi, 1).display} <tspan fill="#00ffff" fontSize="10">t/h</tspan> <tspan fill="#94a3b8" fontSize="10">({fmt('FIC2', fic2Dcs, fic2Ai, 0).display} m³/h)</tspan>
            </text>
          </g>

          {/* TI50: MR Liquid Inlet Temperature (H5TI0050) */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({
            tag: 'H5TI0050',
            name: 'Suhu MR Liquid ke MCHE 5E-1 (Warm Bundle Inlet)',
            unit: '°C',
            valDcs: ti50Dcs.toFixed(1),
            valAi: ti50Ai.toFixed(1)
          })}>
            <rect x="390" y="728" width="115" height="42" fill="#0f172a" stroke="#e69138" strokeWidth="1" rx="4" />
            <text x="447" y="744" fill="#00ffff" fontSize="11" textAnchor="middle" fontWeight="bold">TI50 (MR Liq)</text>
            <text x="447" y="763" fill={fmt('TI50', ti50Dcs, ti50Ai, 1).color} fontSize="15" textAnchor="middle" fontWeight="bold">
              {fmt('TI50', ti50Dcs, ti50Ai, 1).display} <tspan fill="#00ffff" fontSize="10">°C</tspan>
            </text>
          </g>

          {/* =============================================================== */}
          {/* STREAM 5: COLD MR LOOPS (LEFT & RIGHT)                          */}
          {/* =============================================================== */}
          {/* Left Cold MR Loop exiting Chinese Hat: x=794, y=290 -> HIC2 -> cold tray */}
          <path d="M 794,290 L 540,290 L 540,310 L 825,310" fill="none" stroke="#e69138" strokeWidth="2.5" markerEnd="url(#arrow-orange)" />
          
          {/* HIC2 Valve */}
          <path d="M 578,282 L 602,298 L 602,282 L 578,298 Z" fill="#e69138" stroke="#ffffff" strokeWidth="1" />
          <line x1="590" y1="282" x2="590" y2="272" stroke="#e69138" strokeWidth="1.5" />
          <rect x="580" y="266" width="20" height="6" fill="#e69138" stroke="#ffffff" strokeWidth="0.8" />
          <text x="590" y="260" fill="#00ffff" fontSize="10" textAnchor="middle">HIC2 100%</text>

          {/* PI28A/B/C Pressure Indication */}
          <text x="475" y="280" fill="#00ffff" fontSize="10" textAnchor="middle" fontWeight="bold">PI28A/B/C</text>
          <text x="475" y="295" fill="#ffffff" fontSize="11" textAnchor="middle">2.64 <tspan fill="#00ffff" fontSize="9">KGC2G</tspan></text>

          {/* TI24 (MRV Top) — Suhu MR Vapor Setelah Chinese Hat */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({
            tag: 'H5TI0024',
            name: 'Suhu MR Vapor Overhead Setelah Chinese Hat (MRV > 5HV-2)',
            unit: '°C',
            valDcs: ti24Dcs.toFixed(1),
            valAi: ti24Ai.toFixed(1)
          })}>
            <rect x="670" y="235" width="110" height="38" fill="#0f172a" stroke="#0284c7" strokeWidth="1" rx="4" />
            <text x="725" y="250" fill="#00ffff" fontSize="12" textAnchor="middle" fontWeight="bold">TI24 (MRV Top)</text>
            <text x="725" y="267" fill={fmt('TI24', ti24Dcs, ti24Ai, 1).color} fontSize="15" textAnchor="middle" fontWeight="bold">
              {fmt('TI24', ti24Dcs, ti24Ai, 1).display} <tspan fill="#00ffff" fontSize="10">°C</tspan>
            </text>
            <line x1="725" y1="273" x2="725" y2="290" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="3 3" />
          </g>

          {/* Right Cold MR Loop with PRIC15 / TT30 / PT8 */}
          <line x1="915" y1="337" x2="1240" y2="337" stroke="#ffff00" strokeWidth="2.5" />
          <path d="M 1228,329 L 1252,345 L 1252,329 L 1228,345 Z" fill="#ffff00" stroke="#ffffff" strokeWidth="1" />
          <line x1="1240" y1="329" x2="1240" y2="319" stroke="#ffff00" strokeWidth="1.5" />
          <path d="M 1228,319 A 12,12 0 0,1 1252,319 Z" fill="#ffff00" stroke="#ffffff" strokeWidth="1" />
          <text x="1240" y="312" fill="#00ffff" fontSize="10.5" textAnchor="middle">PRIC15 18.0</text>
          
          <path d="M 1252,337 L 1311,337 L 1311,281 L 855,281 L 855,295" fill="none" stroke="#e69138" strokeWidth="2.5" markerEnd="url(#arrow-orange)" />

          {/* TT30 (>PV-15 / H5TI0030) */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({
            tag: 'H5TI0030',
            name: 'Suhu MR Vapor Sebelum JT Valve PV-15 (TT30)',
            unit: '°C',
            valDcs: ti30Dcs.toFixed(1),
            valAi: ti30Ai.toFixed(1)
          })}>
            <rect x="990" y="315" width="105" height="38" fill="#0f172a" stroke="#0284c7" strokeWidth="1" rx="4" />
            <text x="1042" y="330" fill="#00ffff" fontSize="11" textAnchor="middle" fontWeight="bold">TT30 (&gt;PV-15)</text>
            <text x="1042" y="347" fill={fmt('TT30', ti30Dcs, ti30Ai, 1).color} fontSize="14" textAnchor="middle" fontWeight="bold">
              {fmt('TT30', ti30Dcs, ti30Ai, 1).display} <tspan fill="#00ffff" fontSize="10">°C</tspan>
            </text>
            <line x1="1042" y1="353" x2="1042" y2="337" stroke="#0284c7" strokeWidth="1" strokeDasharray="2 2" />
          </g>

          {/* PT8 (MR > PV-15 / H5PI0008) */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({
            tag: 'H5PI0008',
            name: 'Tekanan MR Vapor Sebelum JT Valve PV-15 (PT8)',
            unit: 'KGC2G',
            valDcs: pi8Dcs.toFixed(2),
            valAi: pi8Ai.toFixed(2)
          })}>
            <rect x="1105" y="315" width="100" height="38" fill="#0f172a" stroke="#0284c7" strokeWidth="1" rx="4" />
            <text x="1155" y="330" fill="#00ffff" fontSize="11" textAnchor="middle" fontWeight="bold">PT8 (MR&gt;PV15)</text>
            <text x="1155" y="347" fill={fmt('PT8', pi8Dcs, pi8Ai, 2).color} fontSize="14" textAnchor="middle" fontWeight="bold">
              {fmt('PT8', pi8Dcs, pi8Ai, 2).display} <tspan fill="#00ffff" fontSize="9">KGC2G</tspan>
            </text>
          </g>

          {/* PI10 (LNG < 5E-1 / H5PI0010) */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({
            tag: 'H5PI0010',
            name: 'Tekanan LNG Keluar Cold Bundle MCHE 5E-1 (PI10)',
            unit: 'KGC2G',
            valDcs: pi10Dcs.toFixed(2),
            valAi: pi10Ai.toFixed(2)
          })}>
            <text x="1215" y="375" fill="#00ffff" fontSize="11" fontWeight="bold">PI10</text>
            <text x="1215" y="390" fill={fmt('PI10', pi10Dcs, pi10Ai, 2).color} fontSize="13" fontWeight="bold">
              {fmt('PI10', pi10Dcs, pi10Ai, 2).display} <tspan fill="#00ffff" fontSize="9">KGC2G</tspan>
            </text>
          </g>

          {/* =============================================================== */}
          {/* STREAM 6: WARM MR LOOPS (LEFT & RIGHT)                          */}
          {/* =============================================================== */}
          {/* Left Warm MR Loop with HIC3 */}
          <path d="M 755,617 L 563,617 L 563,562 L 755,562" fill="none" stroke="#e69138" strokeWidth="2.5" markerEnd="url(#arrow-orange)" />
          <path d="M 678,554 L 702,570 L 702,554 L 678,570 Z" fill="#e69138" stroke="#ffffff" strokeWidth="1" />
          <line x1="690" y1="554" x2="690" y2="544" stroke="#e69138" strokeWidth="1.5" />
          <rect x="680" y="538" width="20" height="6" fill="#e69138" stroke="#ffffff" strokeWidth="0.8" />
          <text x="690" y="532" fill="#00ffff" fontSize="10" textAnchor="middle">HIC3 100%</text>

          {/* Right Warm MR Loop with HIC51 */}
          <line x1="954" y1="590" x2="1256" y2="590" stroke="#e69138" strokeWidth="2.5" />
          <path d="M 1244,582 L 1268,598 L 1268,582 L 1244,598 Z" fill="#e69138" stroke="#ffffff" strokeWidth="1" />
          <line x1="1256" y1="582" x2="1256" y2="572" stroke="#e69138" strokeWidth="1.5" />
          <path d="M 1244,572 A 12,12 0 0,1 1268,572 Z" fill="#e69138" stroke="#ffffff" strokeWidth="1" />
          <text x="1256" y="565" fill="#00ffff" fontSize="10" textAnchor="middle">HIC51 0%</text>
          <path d="M 1268,590 L 1311,590 L 1311,534 L 855,534 L 855,570" fill="none" stroke="#e69138" strokeWidth="2.5" markerEnd="url(#arrow-orange)" />

          {/* TT28 (MR > W/B / H5TI0028) */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({
            tag: 'H5TI0028',
            name: 'Suhu MR ke Warm Bundle (MR > W/B / TT28)',
            unit: '°C',
            valDcs: ti28Dcs.toFixed(1),
            valAi: ti28Ai.toFixed(1)
          })}>
            <rect x="990" y="530" width="105" height="36" fill="#0f172a" stroke="#0284c7" strokeWidth="1" rx="4" />
            <text x="1042" y="545" fill="#00ffff" fontSize="11" textAnchor="middle" fontWeight="bold">TT28 (MR&gt;W/B)</text>
            <text x="1042" y="561" fill={fmt('TT28', ti28Dcs, ti28Ai, 1).color} fontSize="14" textAnchor="middle" fontWeight="bold">
              {fmt('TT28', ti28Dcs, ti28Ai, 1).display} <tspan fill="#00ffff" fontSize="10">°C</tspan>
            </text>
          </g>

          {/* TT31 (MRL > 5FV-2 / H5TI0031) */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({
            tag: 'H5TI0031',
            name: 'Suhu MR Liquid ke Katup 5FV-2 (TT31)',
            unit: '°C',
            valDcs: ti31Dcs.toFixed(1),
            valAi: ti31Ai.toFixed(1)
          })}>
            <rect x="990" y="585" width="105" height="36" fill="#0f172a" stroke="#0284c7" strokeWidth="1" rx="4" />
            <text x="1042" y="600" fill="#00ffff" fontSize="11" textAnchor="middle" fontWeight="bold">TT31 (MRL&gt;FV2)</text>
            <text x="1042" y="616" fill={fmt('TT31', ti31Dcs, ti31Ai, 1).color} fontSize="14" textAnchor="middle" fontWeight="bold">
              {fmt('TT31', ti31Dcs, ti31Ai, 1).display} <tspan fill="#00ffff" fontSize="10">°C</tspan>
            </text>
          </g>

          {/* PT7 (MR > FV-2 / H5PI0007) */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({
            tag: 'H5PI0007',
            name: 'Tekanan MR Liquid Sebelum Katup 5FV-2 (PT7)',
            unit: 'KGC2G',
            valDcs: pi7Dcs.toFixed(2),
            valAi: pi7Ai.toFixed(2)
          })}>
            <rect x="1105" y="585" width="100" height="36" fill="#0f172a" stroke="#0284c7" strokeWidth="1" rx="4" />
            <text x="1155" y="600" fill="#00ffff" fontSize="11" textAnchor="middle" fontWeight="bold">PT7 (MR&gt;FV2)</text>
            <text x="1155" y="616" fill={fmt('PT7', pi7Dcs, pi7Ai, 2).color} fontSize="14" textAnchor="middle" fontWeight="bold">
              {fmt('PT7', pi7Dcs, pi7Ai, 2).display} <tspan fill="#00ffff" fontSize="9">KGC2G</tspan>
            </text>
          </g>

          {/* FIC2: MCR Liquid Volumetric Flow */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({
            tag: 'H5FIC002',
            name: 'MCR Liquid Circulation Flow ke MCHE 5E-1',
            unit: 'm³/h (t/h)',
            valDcs: `${fic2Dcs} m³/h (${mcrLiqMassDcs.toFixed(0)} t/h)`,
            valAi: `${fic2Ai} m³/h (${mcrLiqMassAi.toFixed(0)} t/h)`
          })}>
            <rect x="1105" y="640" width="155" height="42" fill="#0f172a" stroke="#0284c7" strokeWidth="1" rx="4" />
            <text x="1182" y="656" fill="#00ffff" fontSize="11" textAnchor="middle" fontWeight="bold">FIC2 (MCR Liq)</text>
            <text x="1182" y="674" fill={fmt('FIC2', fic2Dcs, fic2Ai, 0).color} fontSize="13" textAnchor="middle" fontWeight="bold">
              {fmt('FIC2', fic2Dcs, fic2Ai, 0).display} <tspan fill="#00ffff" fontSize="9.5">m³/h</tspan> <tspan fill={fmt('FIC2_MASS', mcrLiqMassDcs, mcrLiqMassAi, 0).color} fontSize="10">({fmt('FIC2_MASS', mcrLiqMassDcs, mcrLiqMassAi, 0).display} t/h)</tspan>
            </text>
          </g>

          {/* =============================================================== */}
          {/* STREAM 7: OVERHEAD OFF-GAS TO LTSS (WHITE LINE y=195)           */}
          {/* =============================================================== */}
          {/* Elevated white line at y=195 to prevent collision with TI24 */}
          <line x1="794" y1="195" x2="127" y2="195" stroke="#ffffff" strokeWidth="2.5" markerEnd="url(#arrow-white)" />
          <text x="127" y="215" fill="#ffffff" fontSize="13" fontWeight="bold">LTSS</text>
          
          {/* Green PIC2 Control Valve symbol at x=200, y=195 */}
          <path d="M 188,187 L 212,203 L 212,187 L 188,203 Z" fill="#00ff00" stroke="#ffffff" strokeWidth="1" />
          <line x1="200" y1="187" x2="200" y2="177" stroke="#00ff00" strokeWidth="1.5" />
          <path d="M 188,177 A 12,12 0 0,1 212,177 Z" fill="#00ff00" stroke="#ffffff" strokeWidth="1" />

          {/* PIC2: Tekanan Overhead ke LTSS (H5PIC002) */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({
            tag: 'H5PIC002',
            name: '5E-1 Overhead Pressure Controller ke LTSS (PIC2)',
            unit: 'KGC2G',
            valDcs: pic2Dcs.toFixed(2),
            valAi: pic2Ai.toFixed(2),
            limit: 'Normal 2.65 - 2.80 KGC2G'
          })}>
            <rect x="200" y="148" width="95" height="36" fill="#0f172a" stroke="#0284c7" strokeWidth="1" rx="4" />
            <text x="247" y="162" fill="#00ffff" fontSize="10.5" textAnchor="middle" fontWeight="bold">PIC2 (OVHD)</text>
            <text x="247" y="178" fill={fmt('PIC2', pic2Dcs, pic2Ai, 2).color} fontSize="13" textAnchor="middle" fontWeight="bold">
              {fmt('PIC2', pic2Dcs, pic2Ai, 2).display} <tspan fill="#00ffff" fontSize="9">KGC2G</tspan>
            </text>
            <line x1="247" y1="184" x2="247" y2="195" stroke="#0284c7" strokeWidth="1" strokeDasharray="2 2" />
          </g>

          {/* TI20 (MCHE Overhead to LTSS upstream PIC2) */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({
            tag: 'H5TI0020',
            name: 'Suhu Overhead MCHE 5E-1 ke LTSS (Upstream PIC2)',
            unit: '°C',
            valDcs: ti20Dcs.toFixed(1),
            valAi: ti20Ai.toFixed(1)
          })}>
            <rect x="320" y="148" width="105" height="36" fill="#0f172a" stroke="#0284c7" strokeWidth="1" rx="4" />
            <text x="372" y="162" fill="#00ffff" fontSize="11" textAnchor="middle" fontWeight="bold">TI20 (OVHD)</text>
            <text x="372" y="178" fill={fmt('TI20', ti20Dcs, ti20Ai, 1).color} fontSize="14" textAnchor="middle" fontWeight="bold">
              {fmt('TI20', ti20Dcs, ti20Ai, 1).display} <tspan fill="#00ffff" fontSize="10">°C</tspan>
            </text>
            <line x1="372" y1="184" x2="372" y2="195" stroke="#ffffff" strokeWidth="1.5" strokeDasharray="3 3" />
          </g>

          {/* =============================================================== */}
          {/* STREAM 8: SHELL-SIDE LP SUCTION RETURN TO 4C-7 (YELLOW y=813)   */}
          {/* =============================================================== */}
          <line x1="954" y1="813" x2="1620" y2="813" stroke="#ffff00" strokeWidth="2.5" markerEnd="url(#arrow-yellow)" />
          <polygon points="1165,809 1175,813 1165,817" fill="#ffff00" />
          <line x1="1056" y1="813" x2="1056" y2="835" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="3 3" />
          <line x1="1350" y1="813" x2="1350" y2="825" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="3 3" />
          
          {/* Red Gate Valve 4HV11 at x=1486, y=813 */}
          <path d="M 1474,801 L 1498,825 L 1498,801 L 1474,825 Z" fill="#ff0000" stroke="#ffffff" strokeWidth="1" />
          <line x1="1486" y1="801" x2="1486" y2="788" stroke="#ff0000" strokeWidth="2" />
          <line x1="1476" y1="788" x2="1496" y2="788" stroke="#ff0000" strokeWidth="2.5" />
          <text x="1486" y="842" fill="#00ffff" fontSize="12" textAnchor="middle" fontWeight="bold">4HV11</text>
          <text x="1635" y="818" fill="#bef264" fontSize="16" fontWeight="bold">4C-7</text>

          {/* =============================================================== */}
          {/* INTERACTIVE DATA-BACKED DCS PROCESS INDICATORS                   */}
          {/* =============================================================== */}

          {/* 1. Feed Gas Tags (Preserves exact regex compatibility for test_bottom_tags_clearance: y=865, h=38) */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'H3FI0004', name: 'Feed Gas Treated Flow ke MCHE 5E-1', unit: 't/h', valDcs: feedFlowDcs.toFixed(1), valAi: feedFlowAi.toFixed(1) })}>
            <rect x="175" y="865" width="130" height="38" fill="#0f172a" stroke="#0284c7" strokeWidth="1" rx="4" />
            <text x="240" y="880" fill="#00ffff" fontSize="11" textAnchor="middle" fontWeight="bold">H3FI0004 (Feed)</text>
            <text x="240" y="897" fill={fmt('H3FI0004', feedFlowDcs, feedFlowAi, 1).color} fontSize="15" textAnchor="middle" fontWeight="bold">
              {fmt('H3FI0004', feedFlowDcs, feedFlowAi, 1).display} <tspan fill="#00ffff" fontSize="10">t/h</tspan>
            </text>
          </g>

          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'H5PI0012', name: 'Feed Gas Inlet Pressure ke 5E-1', unit: 'KGC2G', valDcs: pi12Dcs.toFixed(2), valAi: pi12Ai.toFixed(2) })}>
            <rect x="330" y="865" width="120" height="38" fill="#0f172a" stroke="#0284c7" strokeWidth="1" rx="4" />
            <text x="390" y="880" fill="#00ffff" fontSize="12" textAnchor="middle" fontWeight="bold">PI12 (Inlet P)</text>
            <text x="390" y="897" fill={fmt('PI12', pi12Dcs, pi12Ai, 2).color} fontSize="15" textAnchor="middle" fontWeight="bold">
              {fmt('PI12', pi12Dcs, pi12Ai, 2).display} <tspan fill="#00ffff" fontSize="10">KGC2G</tspan>
            </text>
          </g>

          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'H5TI0023', name: 'Feed Gas Inlet Temperature ke 5E-1', unit: '°C', valDcs: ti23Dcs.toFixed(1), valAi: ti23Ai.toFixed(1) })}>
            <rect x="480" y="865" width="120" height="38" fill="#0f172a" stroke="#0284c7" strokeWidth="1" rx="4" />
            <text x="540" y="880" fill="#00ffff" fontSize="12" textAnchor="middle" fontWeight="bold">TI23 (Inlet T)</text>
            <text x="540" y="897" fill={fmt('TI23', ti23Dcs, ti23Ai, 1).color} fontSize="15" textAnchor="middle" fontWeight="bold">
              {fmt('TI23', ti23Dcs, ti23Ai, 1).display} <tspan fill="#00ffff" fontSize="10">°C</tspan>
            </text>
          </g>

          {/* 2. MCHE DIFFERENTIAL PRESSURE WITH DUAL INSTRUMENT TAPS */}
          {/* PDI4 (Cold Bundle DP): Two taps across Cold Bundle */}
          <circle cx="794" cy="310" r="3" fill="#00ffff" />
          <circle cx="794" cy="425" r="3" fill="#00ffff" />
          <path d="M 794,310 L 685,310 L 685,345" fill="none" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="3 3" />
          <path d="M 794,425 L 685,425 L 685,387" fill="none" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="3 3" />
          
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({
            tag: 'H5PDI004',
            name: 'Cold Bundle Differential Pressure (5E-1 C/B DP)',
            unit: 'KGC2G',
            valDcs: pdiColdDcs.toFixed(3),
            valAi: pdiColdAi.toFixed(3),
            limit: '< 0.100 KGC2G'
          })}>
            <rect x="620" y="345" width="130" height="42" fill="#0f172a" stroke="#0284c7" strokeWidth="1" rx="4" />
            <text x="685" y="362" fill="#00ffff" fontSize="12" textAnchor="middle" fontWeight="bold">PDI4 (Cold DP)</text>
            <text x="685" y="381" fill={fmt('PDI4', pdiColdDcs, pdiColdAi, 3).color} fontSize="16" textAnchor="middle" fontWeight="bold">
              {fmt('PDI4', pdiColdDcs, pdiColdAi, 3).display} <tspan fill="#00ffff" fontSize="10">KGC2G</tspan>
            </text>
          </g>

          {/* PDI3 (Warm Bundle DP): Two taps across Warm Bundle */}
          <circle cx="755" cy="585" r="3" fill="#00ffff" />
          <circle cx="755" cy="770" r="3" fill="#00ffff" />
          <path d="M 755,585 L 680,585 L 680,640" fill="none" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="3 3" />
          <path d="M 755,770 L 680,770 L 680,682" fill="none" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="3 3" />

          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({
            tag: 'H5PDI003',
            name: 'Warm Bundle Differential Pressure (5E-1 W/B)',
            unit: 'KGC2',
            valDcs: pdiWarmDcs.toFixed(3),
            valAi: pdiWarmAi.toFixed(3),
            limit: '< 0.350 KGC2'
          })}>
            <rect x="615" y="640" width="130" height="42" fill="#0f172a" stroke="#0284c7" strokeWidth="1" rx="4" />
            <text x="680" y="657" fill="#00ffff" fontSize="12" textAnchor="middle" fontWeight="bold">PDI3 (Warm DP)</text>
            <text x="680" y="676" fill={fmt('PDI3', pdiWarmDcs, pdiWarmAi, 3).color} fontSize="16" textAnchor="middle" fontWeight="bold">
              {fmt('PDI3', pdiWarmDcs, pdiWarmAi, 3).display} <tspan fill="#00ffff" fontSize="10">KGC2</tspan>
            </text>
          </g>
          <text x="680" y="696" fill="#94a3b8" fontSize="10" textAnchor="middle">PDI25 A: 0.242 | B: 0.240 KGC2</text>

          {/* 3. Left Profile Temperatures: TI25 (C/B In), TI26 (C/B Out), TI22 */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({
            tag: 'H5TI0025',
            name: 'Suhu Keluar MRV Cold Bundle (MRV < C/B)',
            unit: '°C',
            valDcs: ti25Dcs.toFixed(1),
            valAi: ti25Ai.toFixed(1)
          })}>
            <text x="560" y="448" fill="#00ffff" fontSize="12" fontWeight="bold">TI25</text>
            <text x="605" y="448" fill={fmt('TI25', ti25Dcs, ti25Ai, 1).color} fontSize="14" fontWeight="bold">
              {fmt('TI25', ti25Dcs, ti25Ai, 1).display} <tspan fill="#00ffff" fontSize="10">°C</tspan>
            </text>
            <line x1="680" y1="444" x2="794" y2="444" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="3 3" />
          </g>

          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({
            tag: 'H5TI0026',
            name: 'Suhu Gas Umpan Keluar Cold Bundle (F/G > C/B)',
            unit: '°C',
            valDcs: ti26Dcs.toFixed(1),
            valAi: ti26Ai.toFixed(1)
          })}>
            <text x="560" y="478" fill="#00ffff" fontSize="12" fontWeight="bold">TI26</text>
            <text x="605" y="478" fill={fmt('TI26', ti26Dcs, ti26Ai, 1).color} fontSize="14" fontWeight="bold">
              {fmt('TI26', ti26Dcs, ti26Ai, 1).display} <tspan fill="#00ffff" fontSize="10">°C</tspan>
            </text>
            <line x1="680" y1="474" x2="775" y2="474" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="3 3" />
          </g>

          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({
            tag: 'H5TI0022',
            name: 'Suhu MR Liquid ke Katup 5HV-3 (MRL > 5HV-3)',
            unit: '°C',
            valDcs: ti22Dcs.toFixed(1),
            valAi: ti22Ai.toFixed(1)
          })}>
            <text x="560" y="508" fill="#00ffff" fontSize="12" fontWeight="bold">TI22</text>
            <text x="605" y="508" fill={fmt('TI22', ti22Dcs, ti22Ai, 1).color} fontSize="14" fontWeight="bold">
              {fmt('TI22', ti22Dcs, ti22Ai, 1).display} <tspan fill="#00ffff" fontSize="10">°C</tspan>
            </text>
            <line x1="680" y1="504" x2="760" y2="504" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="3 3" />
          </g>

          {/* 4. Right Profile Temperatures: TI21 & TI27 */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({
            tag: 'H5TI0021',
            name: 'Suhu MRV Masuk Cold Bundle (MRV > C/B)',
            unit: '°C',
            valDcs: ti21Dcs.toFixed(1),
            valAi: ti21Ai.toFixed(1)
          })}>
            <text x="980" y="448" fill="#00ffff" fontSize="12" fontWeight="bold">TI21</text>
            <text x="1025" y="448" fill={fmt('TI21', ti21Dcs, ti21Ai, 1).color} fontSize="14" fontWeight="bold">
              {fmt('TI21', ti21Dcs, ti21Ai, 1).display} <tspan fill="#00ffff" fontSize="10">°C</tspan>
            </text>
            <line x1="915" y1="444" x2="975" y2="444" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="3 3" />
          </g>

          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({
            tag: 'H5TI0027',
            name: 'Suhu Gas Umpan Masuk Cold Bundle (F/G > C/B)',
            unit: '°C',
            valDcs: ti27Dcs.toFixed(1),
            valAi: ti27Ai.toFixed(1)
          })}>
            <text x="980" y="478" fill="#00ffff" fontSize="12" fontWeight="bold">TI27</text>
            <text x="1025" y="478" fill={fmt('TI27', ti27Dcs, ti27Ai, 1).color} fontSize="14" fontWeight="bold">
              {fmt('TI27', ti27Dcs, ti27Ai, 1).display} <tspan fill="#00ffff" fontSize="10">°C</tspan>
            </text>
            <line x1="930" y1="474" x2="975" y2="474" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="3 3" />
          </g>

          {/* 5. LNG Rundown: TI29 & TIC1A/B */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({
            tag: 'H5TI0029',
            name: 'Suhu LNG Rundown Downstream Subcooler (<5PV-15)',
            unit: '°C',
            valDcs: ti29Dcs.toFixed(1),
            valAi: ti29Ai.toFixed(1)
          })}>
            <rect x="1110" y="186" width="115" height="38" fill="#0f172a" stroke="#d946ef" strokeWidth="1" rx="4" />
            <text x="1167" y="201" fill="#e879f9" fontSize="12" textAnchor="middle" fontWeight="bold">TI29 (Rundown)</text>
            <text x="1167" y="218" fill={fmt('TI29', ti29Dcs, ti29Ai, 1).color} fontSize="15" textAnchor="middle" fontWeight="bold">
              {fmt('TI29', ti29Dcs, ti29Ai, 1).display} <tspan fill="#00ffff" fontSize="10">°C</tspan>
            </text>
            <line x1="1167" y1="224" x2="1167" y2="245" stroke="#e879f9" strokeWidth="1.5" strokeDasharray="3 3" />
          </g>

          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({
            tag: 'H5TIC01A',
            name: 'LNG Rundown Temperature Controller (TIC1A/B)',
            unit: '°C',
            valDcs: tiLngDcs.toFixed(1),
            valAi: tiLngAi.toFixed(1),
            limit: 'Target ≤ -150.0°C'
          })}>
            <rect x="1310" y="260" width="125" height="40" fill="#0f172a" stroke="#0284c7" strokeWidth="1" rx="4" />
            <text x="1372" y="276" fill="#00ffff" fontSize="11" textAnchor="middle" fontWeight="bold">TIC1A/B (LNG)</text>
            <text x="1372" y="294" fill={fmt('TIC1A/B', tiLngDcs, tiLngAi, 1).color} fontSize="16" textAnchor="middle" fontWeight="bold">
              {fmt('TIC1A/B', tiLngDcs, tiLngAi, 1).display} <tspan fill="#00ffff" fontSize="10">°C</tspan>
            </text>
            <line x1="1435" y1="280" x2="1440" y2="280" stroke="#0284c7" strokeWidth="1" strokeDasharray="2 2" />
          </g>

          {/* 6. Compressor Suction Return Tags: PI9, H4FI011B, TI8 */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({
            tag: 'H4PI014B',
            name: 'MCHE Bottom Outlet / Compressor Suction Pressure',
            unit: 'KGC2G',
            valDcs: pi9Dcs.toFixed(3),
            valAi: pi9Ai.toFixed(3)
          })}>
            <rect x="980" y="835" width="115" height="40" fill="#0f172a" stroke="#0284c7" strokeWidth="1" rx="4" />
            <text x="1037" y="852" fill="#00ffff" fontSize="12" textAnchor="middle" fontWeight="bold">PI9 (Suct Press)</text>
            <text x="1037" y="869" fill={fmt('PI9', pi9Dcs, pi9Ai, 3).color} fontSize="15" textAnchor="middle" fontWeight="bold">
              {fmt('PI9', pi9Dcs, pi9Ai, 3).display} <tspan fill="#00ffff" fontSize="10">KGC2G</tspan>
            </text>
          </g>

          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({
            tag: 'H4FI011B',
            name: 'Laju Alir Sirkulasi MCR Total (Compressor Return Suction Header)',
            unit: 't/h',
            valDcs: mcrFlowDcs.toFixed(1),
            valAi: mcrFlowAi.toFixed(1),
            limit: 'Floor Anti-Surge ≥ 480.0 t/h'
          })}>
            <rect x="1105" y="835" width="145" height="40" fill="#0f172a" stroke="#0284c7" strokeWidth="1" rx="4" />
            <text x="1177" y="852" fill="#00ffff" fontSize="11" textAnchor="middle" fontWeight="bold">H4FI011B (MCR Total)</text>
            <text x="1177" y="869" fill={fmt('H4FI011B', mcrFlowDcs, mcrFlowAi, 1).color} fontSize="15" textAnchor="middle" fontWeight="bold">
              {fmt('H4FI011B', mcrFlowDcs, mcrFlowAi, 1).display} <tspan fill="#00ffff" fontSize="10">t/h</tspan>
            </text>
            <line x1="1177" y1="813" x2="1177" y2="835" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="3 3" />
          </g>

          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({
            tag: 'H4TI004B',
            name: 'MCHE Bottom Outlet / Compressor Suction Temp',
            unit: '°C',
            valDcs: tiSuctDcs.toFixed(1),
            valAi: tiSuctAi.toFixed(1),
            limit: 'TAL Interlock ≥ -45.0°C'
          })}>
            <rect x="1260" y="835" width="165" height="40" fill="#064e3b" stroke="#10b981" strokeWidth="1.5" rx="4" />
            <text x="1342" y="852" fill="#34d399" fontSize="12" textAnchor="middle" fontWeight="bold">TI8 (TAL Interlock)</text>
            <text x="1342" y="869" fill={fmt('TI8', tiSuctDcs, tiSuctAi, 1).color} fontSize="16" textAnchor="middle" fontWeight="bold">
              {fmt('TI8', tiSuctDcs, tiSuctAi, 1).display} <tspan fill="#00ffff" fontSize="11">°C</tspan>
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
              <span style={{ color: '#94a3b8' }}>Target Skenario:</span>
              <strong style={{ color: '#34d399' }}>{selectedTag.valAi} {selectedTag.unit}</strong>
            </div>
            {selectedTag.limit && (
              <div style={{ marginTop: '8px', paddingTop: '6px', borderTop: '1px dashed #334155', fontSize: '11px', color: '#f59e0b' }}>
                ⚠️ Batas Operasi: {selectedTag.limit}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
