import React, { useState } from 'react';
import { calculateFlashDrum5C1, getEstimatedLngFlow } from '../utils/thermoFlash';
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

  const mcrFlowDcs = actualDcs?.mcr_flow_t_h ?? 562.3;
  const mcrFlowAi = optimum?.mcr_flow_t_h ?? scenario.mcr_flow_t_h;
  const mcrFlow = displayMode === 'DCS_ACTUAL' ? mcrFlowDcs : mcrFlowAi;

  // Refrigeration stream calculations (PR-EOS Equilibrium at -35°C, 43.8 kg/cm²A: 36.0% Vap / 64.0% Liq)
  const MCR_VAPOR_MASS_FRAC = 0.360; // PR-EOS High Pressure Separator vapor fraction
  const MCR_LIQUID_MASS_FRAC = 0.640; // PR-EOS High Pressure Separator liquid fraction
  const MCR_LIQUID_DENSITY_T_M3 = 0.4113; // Liquid MCR density at -35°C, 43.8 kg/cm²A (~411.3 kg/m³)

  const mcrVapFlowDcs = mcrFlowDcs * MCR_VAPOR_MASS_FRAC; // mcrFlowDcs * 0.360
  const mcrVapFlowAi = mcrFlowAi * MCR_VAPOR_MASS_FRAC; // mcrFlowAi * 0.360

  const mcrLiqMassDcs = mcrFlowDcs * MCR_LIQUID_MASS_FRAC; // mcrFlowDcs * 0.640
  const mcrLiqMassAi = mcrFlowAi * MCR_LIQUID_MASS_FRAC; // mcrFlowAi * 0.640

  // FIC2: MCR Liquid Volumetric Flow [m³/h] (Tag H5FIC002) dynamically coupled to liquid mass flow
  // Nominal baselines: const fic2Dcs = 875; const fic2Ai = 810; (legacy) -> dynamic: 747 m³/h at 480 t/h turndown
  const fic2Dcs = Math.round(mcrLiqMassDcs / MCR_LIQUID_DENSITY_T_M3);
  const fic2Ai = Math.round(mcrLiqMassAi / MCR_LIQUID_DENSITY_T_M3);

  // Propane Precooling Cycle (4K-1 Stage 1 Suction Flow H4FI001A & Chillers 3E-14/17/18)
  const c3PrecoolFlowDcs = 212.5;
  const c3PrecoolFlowAi = 212.5;

  // Temperature values: Ground-truth from DCS baseline vs AI optimized / surrogate
  const tiLngDcs = -151.2;
  const tiLngAi = -152.0;

  const tiSuctDcs = -44.8;
  const tiSuctAi = optimum?.expected_suction_temp_c ?? -41.5;

  const ti25Dcs = -130.6; // Cold Bundle MRV Outlet
  const ti25Ai = _snapshot?.values?.t_mche_cold_mrv_out_c?.value ?? -123.5;

  const ti26Dcs = -126.4; // Warm Bundle MRV Outlet
  const ti26Ai = _snapshot?.values?.t_mche_warm_mrv_out_c?.value ?? -122.4;

  const ti21Dcs = -128.5; // Shell Mid Intermediate
  const ti21Ai = _snapshot?.values?.t_mche_shell_mid_c?.value ?? -127.8;

  const ti47Dcs = -35.1; // MCR Vapor Inlet
  const ti47Ai = _snapshot?.values?.t_mche_warm_mrv_in_c?.value ?? -32.7;

  const ti23Dcs = -54.8; // Feed Gas Inlet
  const ti23Ai = -53.5;

  // Additional Cryogenic Tags (PR-EOS & DCS Verified: ORIGINAL_REQUEST Feature 4)
  const ti50Dcs = -36.0; // Suhu MR Liquid Inlet ke MCHE 5E-1
  const ti50Ai = -34.5;  // PR-EOS Skenario

  const ti20Dcs = -134.6; // Suhu MCHE 5E-1 Overhead ke LTSS
  const ti20Ai = -131.2;  // PR-EOS Skenario

  const ti24Dcs = -151.3; // Suhu Cold Bundle MRV Overhead (MRV > 5HV-2)
  const ti24Ai = -150.8;  // PR-EOS Skenario

  const ti29Dcs = -153.6; // Suhu LNG Rundown Downstream Subcooler (<5PV-15)
  const ti29Ai = -153.8;  // PR-EOS Skenario

  // Pressure values
  const pi9Dcs = 2.284;
  const pi9Ai = 2.350;

  const pi1Dcs = 36.90;
  const pi1Ai = 35.15;

  const pi12Dcs = 43.15;
  const pi12Ai = 43.15;

  const pdiColdDcs = 0.067;
  const pdiColdAi = _snapshot?.values?.dp_mche_cold_kgcm2?.value ?? 0.062;

  const pdiWarmDcs = 0.240;
  const pdiWarmAi = _snapshot?.values?.dp_mche_warm_kgcm2?.value ?? 0.215;

  // Total power & SEC
  const totalPower = prediction ? prediction.prediction.total_shaft_power_mw : 84.48;
  const secLng = prediction?.prediction?.sec_lng_kwh_per_t ?? (totalPower * 1000 / lngFlow);

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
        {/* SINGLE INTEGRATED YOKOGAWA CENTUM VP WINDOW HEADER (ZERO VERTICAL STACKING) */}
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
          {/* ZONE 1 (LEFT): Alarm Registers, Badge & Window Tab */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexShrink: 0 }}>
            {/* Alarm Priority Counters (Yokogawa Standard: Red High, Orange Med, Blue Low) */}
            <div style={{ display: 'flex', gap: '2px', alignItems: 'center' }}>
              <span style={{ backgroundColor: '#dc2626', color: '#fff', padding: '1px 6px', fontWeight: 800, borderRadius: '2px', fontSize: '11px' }} title="High Priority Alarm: 0">0</span>
              <span style={{ backgroundColor: '#ea580c', color: '#fff', padding: '1px 6px', fontWeight: 800, borderRadius: '2px', fontSize: '11px' }} title="Medium Priority Alarm: 0">0</span>
              <span style={{ backgroundColor: '#0284c7', color: '#fff', padding: '1px 6px', fontWeight: 800, borderRadius: '2px', fontSize: '11px' }} title="Low / Advisory Alarm: 40">40</span>
            </div>

            {/* DCS PFD REPLICA Badge */}
            <span style={{
              backgroundColor: '#0284c7',
              color: '#ffffff',
              padding: '2px 7px',
              borderRadius: '3px',
              fontWeight: 800,
              fontSize: '10px',
              letterSpacing: '0.5px',
            }}>
              PFD REPLICA
            </span>

            {/* Active Graphic Tab */}
            <div style={{
              backgroundColor: '#0369a1',
              color: '#ffffff',
              padding: '5px 12px',
              fontWeight: 700,
              borderRadius: '4px 4px 0 0',
              borderTop: '2px solid #38bdf8',
              fontSize: '12px',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
            }}>
              <span>GRH0068</span>
              <span style={{ color: '#bae6fd' }}>MCHE (5E-1)</span>
            </div>


          </div>

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
            {/* Centum View Mode Segmented Switcher */}
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
                🔘 Aktual
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
                🟢 Skenario
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
                ⚡ Delta Δ
              </button>
            </div>

            {/* Operator Authority Level & DCS Clock */}
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

        {/* SVG Centum Graphic Area (Native DCS Coordinate System: 1920 x 790 matching image56.png) */}
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
            {/* Arrowhead marker for cyan lines */}
            <marker id="arrow-cyan" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 1 L 10 5 L 0 9 z" fill="#00ffff" />
            </marker>
            {/* Arrowhead marker for magenta lines */}
            <marker id="arrow-magenta" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 1 L 10 5 L 0 9 z" fill="#e879f9" />
            </marker>
            {/* Arrowhead marker for yellow lines */}
            <marker id="arrow-yellow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 1 L 10 5 L 0 9 z" fill="#ffff00" />
            </marker>
            {/* Arrowhead marker for orange lines */}
            <marker id="arrow-orange" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 1 L 10 5 L 0 9 z" fill="#e69138" />
            </marker>
            {/* Arrowhead marker for red lines */}
            <marker id="arrow-red" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 1 L 10 5 L 0 9 z" fill="#ff0000" />
            </marker>
            {/* Arrowhead marker for white lines */}
            <marker id="arrow-white" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 1 L 10 5 L 0 9 z" fill="#ffffff" />
            </marker>
          </defs>

          {/* Title Header on Canvas */}
          <text x="960" y="172" fill="#ffffff" fontSize="24" fontWeight="bold" textAnchor="middle" letterSpacing="4">
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
            {/* Background Card */}
            <rect x="40" y="320" width="205" height="150" fill="#0b1329" stroke="#0284c7" strokeWidth="1.5" rx="6" />
            {/* Header banner */}
            <rect x="40" y="320" width="205" height="26" fill="#1e293b" rx="6" />
            <rect x="40" y="340" width="205" height="6" fill="#1e293b" />
            <text x="142" y="338" fill="#38bdf8" fontSize="11" fontWeight="bold" textAnchor="middle">
              4K-1 C3 PRECOOLING CYCLE
            </text>

            {/* Compressor stage 1 suction flow H4FI001A */}
            <text x="50" y="362" fill="#94a3b8" fontSize="10">Stage 1 Suct (H4FI001A):</text>
            <text x="50" y="380" fill={fmt('H4FI001A', c3PrecoolFlowDcs, c3PrecoolFlowAi, 1).color} fontSize="14" fontWeight="bold">
              {fmt('H4FI001A', c3PrecoolFlowDcs, c3PrecoolFlowAi, 1).display} <tspan fill="#00ffff" fontSize="10">kNm³/h</tspan>
            </text>

            {/* Chillers */}
            <text x="50" y="402" fill="#94a3b8" fontSize="10">MCR Chillers 3E-14/17/18:</text>
            <text x="50" y="418" fill="#34d399" fontSize="12" fontWeight="bold">
              -35.0°C <tspan fill="#94a3b8" fontSize="10">(Precooled MCR)</tspan>
            </text>

            <text x="50" y="438" fill="#94a3b8" fontSize="10">Feed Chillers 4E-10/12/14:</text>
            <text x="50" y="454" fill="#34d399" fontSize="12" fontWeight="bold">
              -35.0°C <tspan fill="#94a3b8" fontSize="10">(Treated Feed)</tspan>
            </text>

            {/* Connecting discharge indicator line to MCR/Feed inlet chillers */}
            <line x1="245" y1="395" x2="275" y2="395" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="3 3" />
            <line x1="275" y1="395" x2="275" y2="495" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="3 3" />
          </g>

          {/* =============================================================== */}
          {/* MAIN VESSEL: MCHE 5E-1 (STEPPED SWAGE GEOMETRY PER IMAGE56.PNG)  */}
          {/* Cold Bundle Neck: x: 794 to 915 (width 121), y: 215 to 440      */}
          {/* Swage Transition: slants outward y: 440 to 520                 */}
          {/* Warm Bundle Body: x: 755 to 954 (width 199), y: 520 to 820      */}
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
          {/* Cold Spray Tray LI2 (U-cup) */}
          <path d="M 825,285 L 825,315 L 885,315 L 885,285" fill="none" stroke="#00ff00" strokeWidth="2" />
          <rect x="826" y="295" width="58" height="19" fill="#0284c7" opacity="0.45" />
          <text x="855" y="332" fill="#00ffff" fontSize="13" textAnchor="middle" fontWeight="bold">x   x</text>

          {/* Warm Spray Tray LI3 (U-cup) */}
          <path d="M 830,560 L 830,595 L 880,595 L 880,560" fill="none" stroke="#00ff00" strokeWidth="2" />
          <rect x="831" y="575" width="48" height="19" fill="#0284c7" opacity="0.45" />
          <text x="855" y="612" fill="#00ffff" fontSize="13" textAnchor="middle" fontWeight="bold">x   x   x</text>

          {/* Equipment Label 5E-1 in Bottom Sump */}
          <text x="855" y="785" fill="#00ff00" fontSize="20" fontWeight="bold" textAnchor="middle">
            5E-1
          </text>

          {/* =============================================================== */}
          {/* INTERNAL PROCESS TUBES INSIDE 5E-1                              */}
          {/* Feed gas tube bundle (Red) rising up to become LNG rundown      */}
          {/* =============================================================== */}
          <line x1="755" y1="841" x2="915" y2="841" stroke="#ff0000" strokeWidth="2.5" />
          {/* Left vertical feed riser */}
          <line x1="795" y1="841" x2="795" y2="815" stroke="#ff0000" strokeWidth="2.5" markerEnd="url(#arrow-red)" />
          <line x1="795" y1="815" x2="795" y2="520" stroke="#ff0000" strokeWidth="2" strokeDasharray="5 3" />
          {/* Right vertical feed riser */}
          <line x1="915" y1="841" x2="915" y2="815" stroke="#ff0000" strokeWidth="2.5" markerEnd="url(#arrow-red)" />
          <line x1="915" y1="815" x2="915" y2="520" stroke="#ff0000" strokeWidth="2" strokeDasharray="5 3" />
          {/* Swage taper risers */}
          <line x1="795" y1="520" x2="814" y2="440" stroke="#ff0000" strokeWidth="2" strokeDasharray="5 3" />
          <line x1="915" y1="520" x2="895" y2="440" stroke="#ff0000" strokeWidth="2" strokeDasharray="5 3" />
          <line x1="814" y1="492" x2="895" y2="492" stroke="#ff0000" strokeWidth="2" />
          {/* Cold bundle feed riser up to top turn */}
          <line x1="814" y1="440" x2="814" y2="253" stroke="#ff0000" strokeWidth="2" strokeDasharray="5 3" />
          {/* Turn right into LNG rundown outlet */}
          <line x1="814" y1="253" x2="915" y2="253" stroke="#e879f9" strokeWidth="2.5" />

          {/* Warm MR internal riser (Yellow) */}
          <line x1="755" y1="784" x2="934" y2="784" stroke="#ffff00" strokeWidth="2" />
          <line x1="934" y1="784" x2="934" y2="520" stroke="#ffff00" strokeWidth="1.8" strokeDasharray="4 3" />
          <line x1="934" y1="520" x2="894" y2="440" stroke="#ffff00" strokeWidth="1.8" strokeDasharray="4 3" />
          <line x1="894" y1="440" x2="894" y2="337" stroke="#ffff00" strokeWidth="1.8" strokeDasharray="4 3" />

          {/* =============================================================== */}
          {/* STREAM 1: FEED GAS INLET (RED LINE y=841)                       */}
          {/* =============================================================== */}
          <text x="145" y="836" fill="#ff0000" fontSize="15" fontWeight="bold">FEED</text>
          <text x="145" y="855" fill="#ff0000" fontSize="15" fontWeight="bold">GAS</text>
          <line x1="180" y1="841" x2="755" y2="841" stroke="#ff0000" strokeWidth="2.5" markerEnd="url(#arrow-red)" />
          {/* Signal drop lines to real feed sensors */}
          <line x1="240" y1="841" x2="240" y2="865" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="3 3" />
          <line x1="390" y1="841" x2="390" y2="865" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="3 3" />
          <line x1="540" y1="841" x2="540" y2="865" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="3 3" />

          {/* =============================================================== */}
          {/* STREAM 2: LNG RUNDOWN (MAGENTA LINE)                            */}
          {/* Horizontal segment y=253, vertical drop x=1487                  */}
          {/* Branches: TV1A to 5C-2 (y=393), HIC6 bypass (y=476), TV1B (y=617)*/}
          {/* =============================================================== */}
          <line x1="915" y1="253" x2="1487" y2="253" stroke="#e879f9" strokeWidth="2.5" />
          <polygon points="980,249 990,253 980,257" fill="#ff0000" />
          <line x1="1487" y1="253" x2="1487" y2="617" stroke="#e879f9" strokeWidth="2.5" />

          {/* Branch 1 (y=393): Main Rundown to 5C-2 */}
          <line x1="1487" y1="393" x2="1670" y2="393" stroke="#e879f9" strokeWidth="2.5" markerEnd="url(#arrow-red)" />
          {/* TV1A Diaphragm Control Valve at x=1570, y=393 */}
          <path d="M 1558,385 L 1582,401 L 1582,385 L 1558,401 Z" fill="#d946ef" stroke="#ffffff" strokeWidth="1" />
          <line x1="1570" y1="385" x2="1570" y2="375" stroke="#d946ef" strokeWidth="1.5" />
          <path d="M 1558,375 A 12,12 0 0,1 1582,375 Z" fill="#d946ef" stroke="#ffffff" strokeWidth="1" />
          <text x="1570" y="365" fill="#00ffff" fontSize="12" textAnchor="middle" fontWeight="bold">TV1A</text>
          <text x="1685" y="425" fill="#00ff00" fontSize="16" fontWeight="bold">5C-2</text>

          {/* Branch 2 (y=476): Bypass with HIC6 */}
          <line x1="1487" y1="476" x2="1608" y2="476" stroke="#e879f9" strokeWidth="2.5" />
          <path d="M 1552,468 L 1576,484 L 1576,468 L 1552,484 Z" fill="#d946ef" stroke="#ffffff" strokeWidth="1" />
          <line x1="1564" y1="468" x2="1564" y2="458" stroke="#d946ef" strokeWidth="1.5" />
          <path d="M 1552,458 A 12,12 0 0,1 1576,458 Z" fill="#d946ef" stroke="#ffffff" strokeWidth="1" />
          <line x1="1608" y1="476" x2="1608" y2="393" stroke="#e879f9" strokeWidth="2.5" markerEnd="url(#arrow-red)" />

          {/* Branch 3 (y=617): TV1B to LNG > STRG PUMP BYPASS */}
          <line x1="1487" y1="617" x2="1675" y2="617" stroke="#e879f9" strokeWidth="2.5" markerEnd="url(#arrow-red)" />
          <path d="M 1613,609 L 1637,625 L 1637,609 L 1613,625 Z" fill="#d946ef" stroke="#ffffff" strokeWidth="1" />
          <line x1="1625" y1="609" x2="1625" y2="599" stroke="#d946ef" strokeWidth="1.5" />
          <path d="M 1613,599 A 12,12 0 0,1 1637,599 Z" fill="#d946ef" stroke="#ffffff" strokeWidth="1" />
          <text x="1625" y="589" fill="#00ffff" fontSize="12" textAnchor="middle" fontWeight="bold">TV1B</text>
          <text x="1690" y="612" fill="#e879f9" fontSize="14" fontWeight="bold">LNG&gt;</text>
          <text x="1690" y="632" fill="#e879f9" fontSize="14" fontWeight="bold">STRG</text>
          <text x="1690" y="668" fill="#e879f9" fontSize="12" fontWeight="bold">PUMP</text>
          <text x="1690" y="688" fill="#e879f9" fontSize="12" fontWeight="bold">BYPASS</text>

          {/* Signal lines for TIC1A/B */}
          <line x1="1487" y1="285" x2="1400" y2="285" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="3 3" />
          <line x1="1400" y1="285" x2="1400" y2="305" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="3 3" />

          {/* =============================================================== */}
          {/* STREAM 3: MR VAPOR INLET (YELLOW LINE y=561 -> x=458 -> y=784)   */}
          {/* =============================================================== */}
          <text x="125" y="562" fill="#ffff00" fontSize="13" fontWeight="bold">MR VAP</text>
          <text x="125" y="578" fill="#ffff00" fontSize="10" fontWeight="bold">(Stream 3)</text>
          <line x1="210" y1="561" x2="458" y2="561" stroke="#ffff00" strokeWidth="2.5" />
          {/* Downward drop at x=458 */}
          <line x1="458" y1="561" x2="458" y2="784" stroke="#ffff00" strokeWidth="2.5" />
          <polygon points="454,720 458,730 462,720" fill="#ffff00" />
          {/* Turn right horizontally into warm bundle entry */}
          <line x1="458" y1="784" x2="755" y2="784" stroke="#ffff00" strokeWidth="2.5" markerEnd="url(#arrow-yellow)" />
          {/* Signal lines for FI1, PI1 */}
          <line x1="340" y1="561" x2="340" y2="525" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="3 3" />
          <line x1="380" y1="561" x2="380" y2="618" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="3 3" />

          {/* =============================================================== */}
          {/* STREAM 4: MR LIQUID INLET (ORANGE LINE y=812)                   */}
          {/* =============================================================== */}
          <text x="135" y="805" fill="#e69138" fontSize="13" fontWeight="bold">MR LIQ</text>
          <text x="135" y="821" fill="#e69138" fontSize="10" fontWeight="bold">(Stream 4)</text>
          <line x1="185" y1="812" x2="755" y2="812" stroke="#e69138" strokeWidth="2.5" markerEnd="url(#arrow-orange)" />

          {/* TI50 (MR Liquid Inlet Temperature - PR-EOS & DCS H4TI0214) */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({
            tag: 'H5TI0050',
            name: 'Suhu MR Liquid ke MCHE 5E-1 (Warm Bundle Inlet)',
            unit: '°C',
            valDcs: ti50Dcs.toFixed(1),
            valAi: ti50Ai.toFixed(1)
          })}>
            <rect x="270" y="746" width="120" height="42" fill="#0f172a" stroke="#e69138" strokeWidth="1" rx="4" />
            <text x="330" y="763" fill="#00ffff" fontSize="12" textAnchor="middle" fontWeight="bold">TI50 (MR Liq)</text>
            <text x="330" y="781" fill={fmt('TI50', ti50Dcs, ti50Ai, 1).color} fontSize="15" textAnchor="middle" fontWeight="bold">
              {fmt('TI50', ti50Dcs, ti50Ai, 1).display} <tspan fill="#00ffff" fontSize="10">°C</tspan>
            </text>
            <line x1="330" y1="788" x2="330" y2="812" stroke="#e69138" strokeWidth="1.5" strokeDasharray="3 3" />
          </g>

          {/* =============================================================== */}
          {/* STREAM 5: COLD MR LOOPS (LEFT & RIGHT)                          */}
          {/* Left: emerging y=337 -> x=551 -> y=310 -> HIC2 -> cold tray     */}
          {/* Right: emerging y=337 -> PRIC15 -> x=1311 -> y=281 -> cold tray*/}
          {/* =============================================================== */}
          {/* Left Cold MR Loop with HIC2 */}
          <path d="M 794,337 L 551,337 L 551,310 L 794,310" fill="none" stroke="#e69138" strokeWidth="2.5" markerEnd="url(#arrow-orange)" />
          <path d="M 583,302 L 607,318 L 607,302 L 583,318 Z" fill="#e69138" stroke="#ffffff" strokeWidth="1" />
          <line x1="595" y1="302" x2="595" y2="292" stroke="#e69138" strokeWidth="1.5" />
          <rect x="585" y="286" width="20" height="6" fill="#e69138" stroke="#ffffff" strokeWidth="0.8" />
          {/* Signal line to PDI4 */}
          <line x1="680" y1="337" x2="680" y2="385" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="3 3" />

          {/* Right Cold MR Loop with PRIC15 */}
          <line x1="915" y1="337" x2="1247" y2="337" stroke="#ffff00" strokeWidth="2.5" />
          <path d="M 1235,329 L 1259,345 L 1259,329 L 1235,345 Z" fill="#ffff00" stroke="#ffffff" strokeWidth="1" />
          <line x1="1247" y1="329" x2="1247" y2="319" stroke="#ffff00" strokeWidth="1.5" />
          <path d="M 1235,319 A 12,12 0 0,1 1259,319 Z" fill="#ffff00" stroke="#ffffff" strokeWidth="1" />
          <path d="M 1259,337 L 1311,337 L 1311,281 L 855,281 L 855,295" fill="none" stroke="#e69138" strokeWidth="2.5" markerEnd="url(#arrow-orange)" />

          {/* =============================================================== */}
          {/* STREAM 6: WARM MR LOOPS (LEFT & RIGHT)                          */}
          {/* Left: emerging y=617 -> x=563 -> y=562 -> HIC3 -> warm tray     */}
          {/* Right: emerging y=590 -> HIC51 -> x=1311 -> y=534 -> warm tray  */}
          {/* =============================================================== */}
          {/* Left Warm MR Loop with HIC3 */}
          <path d="M 755,617 L 563,617 L 563,562 L 755,562" fill="none" stroke="#e69138" strokeWidth="2.5" markerEnd="url(#arrow-orange)" />
          <path d="M 678,554 L 702,570 L 702,554 L 678,570 Z" fill="#e69138" stroke="#ffffff" strokeWidth="1" />
          <line x1="690" y1="554" x2="690" y2="544" stroke="#e69138" strokeWidth="1.5" />
          <rect x="680" y="538" width="20" height="6" fill="#e69138" stroke="#ffffff" strokeWidth="0.8" />
          {/* Signal line to PDI3 */}
          <line x1="680" y1="617" x2="680" y2="640" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="3 3" />

          {/* Right Warm MR Loop with HIC51 */}
          <line x1="954" y1="590" x2="1256" y2="590" stroke="#e69138" strokeWidth="2.5" />
          <path d="M 1244,582 L 1268,598 L 1268,582 L 1244,598 Z" fill="#e69138" stroke="#ffffff" strokeWidth="1" />
          <line x1="1256" y1="582" x2="1256" y2="572" stroke="#e69138" strokeWidth="1.5" />
          <path d="M 1244,572 A 12,12 0 0,1 1268,572 Z" fill="#e69138" stroke="#ffffff" strokeWidth="1" />
          <path d="M 1268,590 L 1311,590 L 1311,534 L 855,534 L 855,570" fill="none" stroke="#e69138" strokeWidth="2.5" markerEnd="url(#arrow-orange)" />

          {/* =============================================================== */}
          {/* STREAM 7: OVERHEAD OFF-GAS TO LTSS (WHITE LINE y=237)           */}
          {/* =============================================================== */}
          <line x1="794" y1="237" x2="127" y2="237" stroke="#ffffff" strokeWidth="2.5" markerEnd="url(#arrow-white)" />
          <text x="127" y="258" fill="#ffffff" fontSize="14" fontWeight="bold">LTSS</text>
          {/* Green PIC2 Control Valve symbol at x=220, y=244 */}
          <path d="M 208,236 L 232,252 L 232,236 L 208,252 Z" fill="#00ff00" stroke="#ffffff" strokeWidth="1" />
          <line x1="220" y1="236" x2="220" y2="226" stroke="#00ff00" strokeWidth="1.5" />
          <path d="M 208,226 A 12,12 0 0,1 232,226 Z" fill="#00ff00" stroke="#ffffff" strokeWidth="1" />

          {/* TI20 (MCHE Overhead to LTSS upstream PIC2) */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({
            tag: 'H5TI0020',
            name: 'Suhu Overhead MCHE 5E-1 ke LTSS (Upstream PIC2)',
            unit: '°C',
            valDcs: ti20Dcs.toFixed(1),
            valAi: ti20Ai.toFixed(1)
          })}>
            <rect x="365" y="186" width="105" height="38" fill="#0f172a" stroke="#0284c7" strokeWidth="1" rx="4" />
            <text x="417" y="201" fill="#00ffff" fontSize="12" textAnchor="middle" fontWeight="bold">TI20 (OVHD)</text>
            <text x="417" y="218" fill={fmt('TI20', ti20Dcs, ti20Ai, 1).color} fontSize="15" textAnchor="middle" fontWeight="bold">
              {fmt('TI20', ti20Dcs, ti20Ai, 1).display} <tspan fill="#00ffff" fontSize="10">°C</tspan>
            </text>
            <line x1="417" y1="224" x2="417" y2="237" stroke="#ffffff" strokeWidth="1.5" strokeDasharray="3 3" />
          </g>

          {/* TI24 (Cold Bundle MRV Overhead) */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({
            tag: 'H5TI0024',
            name: 'Suhu Cold Bundle MRV Overhead (MRV > 5HV-2)',
            unit: '°C',
            valDcs: ti24Dcs.toFixed(1),
            valAi: ti24Ai.toFixed(1)
          })}>
            <rect x="490" y="186" width="105" height="38" fill="#0f172a" stroke="#0284c7" strokeWidth="1" rx="4" />
            <text x="542" y="201" fill="#00ffff" fontSize="12" textAnchor="middle" fontWeight="bold">TI24 (MRV Top)</text>
            <text x="542" y="218" fill={fmt('TI24', ti24Dcs, ti24Ai, 1).color} fontSize="15" textAnchor="middle" fontWeight="bold">
              {fmt('TI24', ti24Dcs, ti24Ai, 1).display} <tspan fill="#00ffff" fontSize="10">°C</tspan>
            </text>
            <line x1="542" y1="224" x2="542" y2="237" stroke="#ffffff" strokeWidth="1.5" strokeDasharray="3 3" />
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
          {/* HANYA MENAMPILKAN TAG / INDIKATOR YANG MEMILIKI DATA AKTUAL/AI  */}
          {/* =============================================================== */}

          {/* 1. Feed Gas Tags: FI4 / H3FI0004 (Rate), PI12 (Press), TI23 (Temp) */}
          {/* FI4: Laju Alir Umpan Gas Treated ke 5E-1 */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'H3FI0004', name: 'Feed Gas Treated Flow ke MCHE 5E-1', unit: 't/h', valDcs: feedFlowDcs.toFixed(1), valAi: feedFlowAi.toFixed(1) })}>
            <rect x="180" y="865" width="120" height="38" fill="#0f172a" stroke="#0284c7" strokeWidth="1" rx="4" />
            <text x="240" y="880" fill="#00ffff" fontSize="12" textAnchor="middle" fontWeight="bold">FI4 (Feed)</text>
            <text x="240" y="897" fill={fmt('FI4', feedFlowDcs, feedFlowAi, 1).color} fontSize="15" textAnchor="middle" fontWeight="bold">
              {fmt('FI4', feedFlowDcs, feedFlowAi, 1).display} <tspan fill="#00ffff" fontSize="10">t/h</tspan>
            </text>
          </g>

          {/* PI12: Tekanan Umpan Masuk */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'H5PI0012', name: 'Feed Gas Inlet Pressure ke 5E-1', unit: 'KGC2G', valDcs: pi12Dcs.toFixed(2), valAi: pi12Ai.toFixed(2) })}>
            <rect x="330" y="865" width="120" height="38" fill="#0f172a" stroke="#0284c7" strokeWidth="1" rx="4" />
            <text x="390" y="880" fill="#00ffff" fontSize="12" textAnchor="middle" fontWeight="bold">PI12 (Inlet P)</text>
            <text x="390" y="897" fill={fmt('PI12', pi12Dcs, pi12Ai, 2).color} fontSize="15" textAnchor="middle" fontWeight="bold">
              {fmt('PI12', pi12Dcs, pi12Ai, 2).display} <tspan fill="#00ffff" fontSize="10">KGC2G</tspan>
            </text>
          </g>

          {/* TI23: Suhu Umpan Masuk */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'H5TI0023', name: 'Feed Gas Inlet Temperature ke 5E-1', unit: '°C', valDcs: ti23Dcs.toFixed(1), valAi: ti23Ai.toFixed(1) })}>
            <rect x="480" y="865" width="120" height="38" fill="#0f172a" stroke="#0284c7" strokeWidth="1" rx="4" />
            <text x="540" y="880" fill="#00ffff" fontSize="12" textAnchor="middle" fontWeight="bold">TI23 (Inlet T)</text>
            <text x="540" y="897" fill={fmt('TI23', ti23Dcs, ti23Ai, 1).color} fontSize="15" textAnchor="middle" fontWeight="bold">
              {fmt('TI23', ti23Dcs, ti23Ai, 1).display} <tspan fill="#00ffff" fontSize="10">°C</tspan>
            </text>
          </g>

          {/* 2. MCR Vapor Inlet Tags: FI1 (MCR Flow), PI1 (Press), TI47 (Temp) */}
          {/* FI1: MCR Vapor Flow (Stream 3 Inlet to Warm Bundle) */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({
            tag: 'FI1',
            name: 'MCR Vapor Flow ke MCHE 5E-1 (Warm Bundle Inlet)',
            unit: 't/h',
            valDcs: mcrVapFlowDcs.toFixed(1),
            valAi: mcrVapFlowAi.toFixed(1),
            limit: 'Coupled with H5TI0047 (-35.1°C DCS / -32.7°C Skenario)'
          })}>
            <rect x="270" y="495" width="140" height="42" fill="#0f172a" stroke="#0284c7" strokeWidth="1" rx="4" />
            <text x="340" y="512" fill="#00ffff" fontSize="12" textAnchor="middle" fontWeight="bold">FI1 (MCR Vap)</text>
            <text x="340" y="531" fill={fmt('FI1', mcrVapFlowDcs, mcrVapFlowAi, 1).color} fontSize="16" textAnchor="middle" fontWeight="bold">
              {fmt('FI1', mcrVapFlowDcs, mcrVapFlowAi, 1).display} <tspan fill="#00ffff" fontSize="11">t/h</tspan>
            </text>
          </g>

          {/* PI1: Tekanan MCR Masuk */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'H5PI0001', name: 'MCR Vapor Pressure', unit: 'KGC2G', valDcs: pi1Dcs.toFixed(2), valAi: pi1Ai.toFixed(2) })}>
            <text x="380" y="618" fill="#00ffff" fontSize="12" fontWeight="bold">PI1</text>
            <text x="380" y="638" fill={fmt('PI1', pi1Dcs, pi1Ai, 2).color} fontSize="15" fontWeight="bold">
              {fmt('PI1', pi1Dcs, pi1Ai, 2).display} <tspan fill="#00ffff" fontSize="10">KGC2G</tspan>
            </text>
          </g>

          {/* TI47: Suhu MCR Masuk (Coupled with FI1) */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'H5TI0047', name: 'MCR Vapor Inlet Temperature (Coupled with FI1)', unit: '°C', valDcs: ti47Dcs.toFixed(1), valAi: ti47Ai.toFixed(1) })}>
            <text x="380" y="670" fill="#00ffff" fontSize="12" fontWeight="bold">TI47 (Vap T)</text>
            <text x="380" y="690" fill={fmt('TI47', ti47Dcs, ti47Ai, 1).color} fontSize="15" fontWeight="bold">
              {fmt('TI47', ti47Dcs, ti47Ai, 1).display} <tspan fill="#00ffff" fontSize="10">°C</tspan>
            </text>
          </g>

          {/* 3. MCHE Differential Pressure: PDI4 (Cold) & PDI3 (Warm) */}
          {/* PDI4 (Cold Bundle DP) */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'H5PDI004', name: 'Cold Bundle Differential Pressure', unit: 'KGC2G', valDcs: pdiColdDcs.toFixed(3), valAi: pdiColdAi.toFixed(3), limit: '< 0.100 KGC2G' })}>
            <rect x="620" y="385" width="130" height="42" fill="#0f172a" stroke="#0284c7" strokeWidth="1" rx="4" />
            <text x="685" y="402" fill="#00ffff" fontSize="12" textAnchor="middle" fontWeight="bold">PDI4 (Cold DP)</text>
            <text x="685" y="421" fill={fmt('PDI4', pdiColdDcs, pdiColdAi, 3).color} fontSize="16" textAnchor="middle" fontWeight="bold">
              {fmt('PDI4', pdiColdDcs, pdiColdAi, 3).display} <tspan fill="#00ffff" fontSize="10">KGC2G</tspan>
            </text>
          </g>

          {/* PDI3 (Warm Bundle DP) */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'H5PDI003', name: 'Warm Bundle Differential Pressure', unit: 'KGC2', valDcs: pdiWarmDcs.toFixed(3), valAi: pdiWarmAi.toFixed(3), limit: '< 0.350 KGC2' })}>
            <rect x="620" y="640" width="130" height="42" fill="#0f172a" stroke="#0284c7" strokeWidth="1" rx="4" />
            <text x="685" y="657" fill="#00ffff" fontSize="12" textAnchor="middle" fontWeight="bold">PDI3 (Warm DP)</text>
            <text x="685" y="676" fill={fmt('PDI3', pdiWarmDcs, pdiWarmAi, 3).color} fontSize="16" textAnchor="middle" fontWeight="bold">
              {fmt('PDI3', pdiWarmDcs, pdiWarmAi, 3).display} <tspan fill="#00ffff" fontSize="10">KGC2</tspan>
            </text>
          </g>

          {/* 4. Internal Profile Temperatures: TI25 (Cold), TI26 (Warm), TI21 (Mid) */}
          {/* TI25 (Cold Bundle MRV Outlet) */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'H5TI0025', name: 'Suhu Keluar MRV Cold Bundle', unit: '°C', valDcs: ti25Dcs.toFixed(1), valAi: ti25Ai.toFixed(1) })}>
            <text x="590" y="450" fill="#00ffff" fontSize="12" fontWeight="bold">TI25</text>
            <text x="635" y="450" fill={fmt('TI25', ti25Dcs, ti25Ai, 1).color} fontSize="14" fontWeight="bold">
              {fmt('TI25', ti25Dcs, ti25Ai, 1).display} <tspan fill="#00ffff" fontSize="10">°C</tspan>
            </text>
            <line x1="710" y1="446" x2="794" y2="446" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="3 3" />
          </g>

          {/* TI26 (Warm Bundle MRV Outlet) */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'H5TI0026', name: 'Suhu Keluar MRV Warm Bundle', unit: '°C', valDcs: ti26Dcs.toFixed(1), valAi: ti26Ai.toFixed(1) })}>
            <text x="590" y="480" fill="#00ffff" fontSize="12" fontWeight="bold">TI26</text>
            <text x="635" y="480" fill={fmt('TI26', ti26Dcs, ti26Ai, 1).color} fontSize="14" fontWeight="bold">
              {fmt('TI26', ti26Dcs, ti26Ai, 1).display} <tspan fill="#00ffff" fontSize="10">°C</tspan>
            </text>
            <line x1="710" y1="476" x2="775" y2="476" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="3 3" />
          </g>

          {/* TI21 (Shell Mid Intermediate Temperature) */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'H5TI0021', name: 'Suhu Shell Tengah MCHE', unit: '°C', valDcs: ti21Dcs.toFixed(1), valAi: ti21Ai.toFixed(1) })}>
            <text x="1010" y="450" fill="#00ffff" fontSize="12" fontWeight="bold">TI21</text>
            <text x="1055" y="450" fill={fmt('TI21', ti21Dcs, ti21Ai, 1).color} fontSize="14" fontWeight="bold">
              {fmt('TI21', ti21Dcs, ti21Ai, 1).display} <tspan fill="#00ffff" fontSize="10">°C</tspan>
            </text>
            <line x1="915" y1="446" x2="1005" y2="446" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="3 3" />
          </g>

          {/* FIC2: MCR Liquid Circulation Flow */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({
            tag: 'H5FIC002',
            name: 'MCR Liquid Circulation Flow ke MCHE 5E-1',
            unit: 'm³/h (t/h)',
            valDcs: `${fic2Dcs} m³/h (${mcrLiqMassDcs.toFixed(0)} t/h)`,
            valAi: `${fic2Ai} m³/h (${mcrLiqMassAi.toFixed(0)} t/h)`
          })}>
            <rect x="1135" y="625" width="160" height="46" fill="#0f172a" stroke="#0284c7" strokeWidth="1" rx="4" />
            <text x="1215" y="642" fill="#00ffff" fontSize="12" textAnchor="middle" fontWeight="bold">FIC2 (MCR Liq)</text>
            <text x="1215" y="661" fill={fmt('FIC2', fic2Dcs, fic2Ai, 0).color} fontSize="13" textAnchor="middle" fontWeight="bold">
              {fmt('FIC2', fic2Dcs, fic2Ai, 0).display} <tspan fill="#00ffff" fontSize="10">m³/h</tspan> <tspan fill={fmt('FIC2_MASS', mcrLiqMassDcs, mcrLiqMassAi, 0).color} fontSize="11">({fmt('FIC2_MASS', mcrLiqMassDcs, mcrLiqMassAi, 0).display} t/h)</tspan>
            </text>
          </g>

          {/* 5. LNG Rundown Tags: TI29 (Subcooler T), TIC1A/B (Temp) & FI6A (Production Flow) */}
          {/* TI29: Suhu LNG Rundown Subcooled */}
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
            <line x1="1167" y1="224" x2="1167" y2="253" stroke="#e879f9" strokeWidth="1.5" strokeDasharray="3 3" />
          </g>

          {/* TIC1A/B: Suhu LNG Rundown */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'H5TIC01A', name: 'LNG Rundown Temperature Controller', unit: '°C', valDcs: tiLngDcs.toFixed(1), valAi: tiLngAi.toFixed(1), limit: 'Target ≤ -150.0°C' })}>
            <rect x="1340" y="270" width="135" height="42" fill="#0f172a" stroke="#0284c7" strokeWidth="1" rx="4" />
            <text x="1407" y="287" fill="#00ffff" fontSize="12" textAnchor="middle" fontWeight="bold">TIC1A/B (LNG)</text>
            <text x="1407" y="306" fill={fmt('TIC1A/B', tiLngDcs, tiLngAi, 1).color} fontSize="17" textAnchor="middle" fontWeight="bold">
              {fmt('TIC1A/B', tiLngDcs, tiLngAi, 1).display} <tspan fill="#00ffff" fontSize="11">°C</tspan>
            </text>
          </g>

          {/* FI6A: Laju Alir Produksi LNG ke Tangki 5C-2 */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'H5FI006A', name: 'Laju Alir Produksi LNG Rundown ke Tangki (5C-2)', unit: 't/h', valDcs: lngFlowDcs.toFixed(1), valAi: lngFlowAi.toFixed(1) })}>
            <rect x="1660" y="360" width="125" height="40" fill="#0f172a" stroke="#0284c7" strokeWidth="1" rx="4" />
            <text x="1722" y="377" fill="#00ffff" fontSize="12" textAnchor="middle" fontWeight="bold">FI6A (LNG Flow)</text>
            <text x="1722" y="394" fill={fmt('FI6A', lngFlowDcs, lngFlowAi, 1).color} fontSize="15" textAnchor="middle" fontWeight="bold">
              {fmt('FI6A', lngFlowDcs, lngFlowAi, 1).display} <tspan fill="#00ffff" fontSize="10">t/h</tspan>
            </text>
          </g>

          {/* 6. Compressor Suction Return Tags: PI9 (Pressure), H4FI011B (MCR Total), & TI8 (TAL Interlock) */}
          {/* PI9: Tekanan Suction Kompresor MCR */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'H4PI014B', name: 'MCHE Bottom Outlet / Compressor Suction Pressure', unit: 'KGC2G', valDcs: pi9Dcs.toFixed(3), valAi: pi9Ai.toFixed(3) })}>
            <rect x="980" y="835" width="115" height="40" fill="#0f172a" stroke="#0284c7" strokeWidth="1" rx="4" />
            <text x="1037" y="852" fill="#00ffff" fontSize="12" textAnchor="middle" fontWeight="bold">PI9 (Suct Press)</text>
            <text x="1037" y="869" fill={fmt('PI9', pi9Dcs, pi9Ai, 3).color} fontSize="15" textAnchor="middle" fontWeight="bold">
              {fmt('PI9', pi9Dcs, pi9Ai, 3).display} <tspan fill="#00ffff" fontSize="10">KGC2G</tspan>
            </text>
          </g>

          {/* H4FI011B: Laju Alir Sirkulasi MCR Total */}
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

          {/* TI8: Suhu Suction Drum / TAL Interlock */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'H4TI004B', name: 'MCHE Bottom Outlet / Compressor Suction Temp', unit: '°C', valDcs: tiSuctDcs.toFixed(1), valAi: tiSuctAi.toFixed(1), limit: 'TAL Interlock ≥ -45.0°C' })}>
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
