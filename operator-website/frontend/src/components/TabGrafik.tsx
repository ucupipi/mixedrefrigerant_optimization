import React, { useState } from 'react';
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

  // Dynamic values based on scenario and baseline
  const feedFlow = displayMode === 'DCS_ACTUAL' ? (actualDcs?.feed_flow_t_h ?? 245.8) : scenario.feed_flow_t_h;
  const lngFlow = feedFlow * 0.9450;
  const mcrFlow = displayMode === 'DCS_ACTUAL' ? (actualDcs?.mcr_flow_t_h ?? 562.3) : scenario.mcr_flow_t_h;

  // Key temperatures and pressures
  const suctTemp = displayMode === 'DCS_ACTUAL' ? -44.8 : (optimum?.expected_suction_temp_c ?? -41.5);
  const suctPress = displayMode === 'DCS_ACTUAL' ? 2.284 : 2.350;
  const pdiCold = displayMode === 'DCS_ACTUAL' ? 0.067 : 0.062;
  const pdiWarm = displayMode === 'DCS_ACTUAL' ? 0.240 : 0.215;
  const lngTemp = displayMode === 'DCS_ACTUAL' ? -151.2 : -152.0;

  // Total power & SEC
  const totalPower = prediction ? prediction.prediction.total_shaft_power_mw : 84.48;
  const secLng = prediction?.prediction?.sec_lng_kwh_per_t ?? (totalPower * 1000 / lngFlow);

  // Helper to format values according to active mode
  const fmt = (_tagKey: string, dcsVal: number, aiVal: number, decimals: number = 1): { display: string; isAiDiff: boolean } => {
    if (displayMode === 'DCS_ACTUAL') {
      return { display: dcsVal.toFixed(decimals), isAiDiff: false };
    }
    if (displayMode === 'AI_OPTIMIZED') {
      return { display: aiVal.toFixed(decimals), isAiDiff: Math.abs(aiVal - dcsVal) > 0.01 };
    }
    // DELTA_DIFF mode
    const diff = aiVal - dcsVal;
    const sign = diff > 0 ? '+' : '';
    return { display: `${sign}${diff.toFixed(decimals)}`, isAiDiff: Math.abs(diff) > 0.01 };
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
      {/* Top Controls & Status Bar */}
      <div style={{
        backgroundColor: '#1e293b',
        color: '#ffffff',
        padding: '12px 20px',
        borderRadius: '8px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <span style={{
            backgroundColor: '#0284c7',
            color: '#ffffff',
            padding: '3px 8px',
            borderRadius: '4px',
            fontWeight: 800,
            fontSize: '12px',
          }}>
            DCS PFD REPLICA
          </span>
          <span style={{ fontSize: '15px', fontWeight: 700 }}>
            Yokogawa CENTUM VP: GRH0068 MAIN HEAT EXCHNG (MCHE 5E-1)
          </span>
          <span style={{ fontSize: '12px', color: '#94a3b8' }}>
            Ref: Plant-3 DCS Graphic & PFD image56.png
          </span>
          {/* Real-time KPI Chips */}
          <div style={{ display: 'flex', gap: '8px', marginLeft: '12px', fontSize: '11px' }}>
            <span style={{ backgroundColor: '#0f172a', padding: '3px 8px', borderRadius: '4px', border: '1px solid #334155' }}>
              MCR: <strong style={{ color: '#38bdf8' }}>{mcrFlow.toFixed(1)} t/h</strong>
            </span>
            <span style={{ backgroundColor: '#0f172a', padding: '3px 8px', borderRadius: '4px', border: '1px solid #334155' }}>
              SEC: <strong style={{ color: '#34d399' }}>{secLng.toFixed(1)} kWh/t</strong>
            </span>
            <span style={{ backgroundColor: '#0f172a', padding: '3px 8px', borderRadius: '4px', border: '1px solid #334155' }}>
              Daya: <strong style={{ color: '#fbbf24' }}>{totalPower.toFixed(2)} MW</strong>
            </span>
          </div>
        </div>

        {/* View Mode Switcher */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', backgroundColor: '#0f172a', padding: '4px', borderRadius: '6px' }}>
          <button
            onClick={() => setDisplayMode('DCS_ACTUAL')}
            style={{
              backgroundColor: displayMode === 'DCS_ACTUAL' ? '#334155' : 'transparent',
              color: displayMode === 'DCS_ACTUAL' ? '#38bdf8' : '#94a3b8',
              border: 'none',
              borderRadius: '4px',
              padding: '6px 12px',
              fontSize: '12px',
              fontWeight: 700,
              cursor: 'pointer',
            }}
          >
            🔘 DCS Aktual (Baseline)
          </button>
          <button
            onClick={() => setDisplayMode('AI_OPTIMIZED')}
            style={{
              backgroundColor: displayMode === 'AI_OPTIMIZED' ? '#065f46' : 'transparent',
              color: displayMode === 'AI_OPTIMIZED' ? '#34d399' : '#94a3b8',
              border: 'none',
              borderRadius: '4px',
              padding: '6px 12px',
              fontSize: '12px',
              fontWeight: 700,
              cursor: 'pointer',
            }}
          >
            🟢 AI Optimized (Skenario)
          </button>
          <button
            onClick={() => setDisplayMode('DELTA_DIFF')}
            style={{
              backgroundColor: displayMode === 'DELTA_DIFF' ? '#78350f' : 'transparent',
              color: displayMode === 'DELTA_DIFF' ? '#fcd34d' : '#94a3b8',
              border: 'none',
              borderRadius: '4px',
              padding: '6px 12px',
              fontSize: '12px',
              fontWeight: 700,
              cursor: 'pointer',
            }}
          >
            ⚡ Perbandingan (Delta Δ)
          </button>
        </div>
      </div>

      {/* Main Yokogawa Centum VP DCS Display Canvas */}
      <div style={{
        backgroundColor: '#000000',
        borderRadius: '8px',
        border: '3px solid #334155',
        boxShadow: '0 4px 20px rgba(0,0,0,0.5)',
        overflow: 'hidden',
        position: 'relative',
      }}>
        {/* Centum VP Window Header Bar */}
        <div style={{
          backgroundColor: '#1b2a4a',
          color: '#ffffff',
          height: '36px',
          padding: '0 12px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          borderBottom: '2px solid #0284c7',
          fontSize: '12px',
          fontFamily: "'Segoe UI', Tahoma, sans-serif",
          userSelect: 'none',
        }}>
          {/* Left: Alarms and Tabs */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{ display: 'flex', gap: '2px' }}>
              <span style={{ backgroundColor: '#dc2626', color: '#fff', padding: '1px 6px', fontWeight: 800, borderRadius: '2px', fontSize: '11px' }}>0</span>
              <span style={{ backgroundColor: '#ea580c', color: '#fff', padding: '1px 6px', fontWeight: 800, borderRadius: '2px', fontSize: '11px' }}>0</span>
              <span style={{ backgroundColor: '#0284c7', color: '#fff', padding: '1px 6px', fontWeight: 800, borderRadius: '2px', fontSize: '11px' }}>40</span>
            </div>
            <div style={{
              backgroundColor: '#0369a1',
              color: '#ffffff',
              padding: '4px 10px',
              fontWeight: 700,
              borderRadius: '3px 3px 0 0',
              borderTop: '2px solid #38bdf8',
            }}>
              GRH0068 MAIN HEAT EXCHNG
            </div>
            <span style={{ color: '#94a3b8', fontSize: '11px' }}>GRH0067 2K-1 L.O</span>
            <span style={{ color: '#94a3b8', fontSize: '11px' }}>GRH0066 2K-1 VIBRATION</span>
            <span style={{ color: '#94a3b8', fontSize: '11px' }}>GRH0065 FUEL GAS COMP</span>
            <span style={{ color: '#94a3b8', fontSize: '11px' }}>GRH0064 4K-3 L.O</span>
          </div>

          {/* Right: DCS User & Clock */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', color: '#93c5fd', fontSize: '11px' }}>
            <span>YOKOGAWA CENTUM VP</span>
            <span>ENGUSER (S3)</span>
            <span style={{ color: '#ffffff', fontWeight: 700 }}>27-MAY-26 13:51</span>
          </div>
        </div>

        {/* SVG Centum Graphic Area (1600 x 860) */}
        <svg
          viewBox="0 0 1600 860"
          style={{
            width: '100%',
            height: 'auto',
            display: 'block',
            backgroundColor: '#000000',
            fontFamily: "'Courier New', Courier, monospace",
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
            {/* Arrowhead marker for red lines */}
            <marker id="arrow-red" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 1 L 10 5 L 0 9 z" fill="#ff0000" />
            </marker>
          </defs>

          {/* Title Header on Canvas */}
          <text x="800" y="55" fill="#ffffff" fontSize="22" fontWeight="bold" textAnchor="middle" letterSpacing="3">
            MAIN HEAT EXCHANGER
          </text>
          <text x="1240" y="65" fill="#1d4ed8" fontSize="14" fontWeight="bold">
            RESET 5HC25
          </text>

          {/* =============================================================== */}
          {/* MAIN VESSEL: MCHE 5E-1 (STEPPED SWAGE GEOMETRY)                 */}
          {/* =============================================================== */}
          {/* Cold Bundle Neck: x: 670 to 790, y: 130 to 360 */}
          {/* Swage Transition: y: 360 to 410 */}
          {/* Warm Bundle Body: x: 630 to 830, y: 410 to 720 */}
          <path
            d="
              M 670,200
              A 60,60 0 0,1 790,200
              L 790,360
              L 830,410
              L 830,720
              A 100,30 0 0,1 630,720
              L 630,410
              L 670,360
              Z
            "
            fill="none"
            stroke="#00ff00"
            strokeWidth="3.5"
          />

          {/* Internal separator trays & distributor representations */}
          {/* Cold Spray Tray */}
          <line x1="685" y1="280" x2="775" y2="280" stroke="#00ff00" strokeWidth="2" strokeDasharray="4 3" />
          <text x="730" y="276" fill="#00ffff" fontSize="11" textAnchor="middle">* * *</text>
          {/* Liquid level LI2 fill rectangle */}
          <rect x="685" y="280" width="90" height="18" fill="#0284c7" opacity="0.4" />

          {/* Warm Spray Tray */}
          <line x1="645" y1="510" x2="815" y2="510" stroke="#00ff00" strokeWidth="2" strokeDasharray="4 3" />
          <text x="730" y="506" fill="#00ffff" fontSize="11" textAnchor="middle">* * * * *</text>
          {/* Liquid level LI3 fill rectangle */}
          <rect x="645" y="510" width="170" height="24" fill="#0284c7" opacity="0.4" />

          {/* Sump text */}
          <text x="730" y="695" fill="#ffffff" fontSize="20" fontWeight="bold" textAnchor="middle">
            5E-1
          </text>

          {/* =============================================================== */}
          {/* STREAM 1: FEED GAS INLET & LNG PRODUCT (RED & MAGENTA)          */}
          {/* =============================================================== */}
          {/* FEED GAS Label */}
          <text x="140" y="725" fill="#ff0000" fontSize="14" fontWeight="bold">FEED</text>
          <text x="140" y="742" fill="#ff0000" fontSize="14" fontWeight="bold">GAS</text>

          {/* Red line from left into 5E-1 bottom tube bundle */}
          <line x1="180" y1="735" x2="670" y2="735" stroke="#ff0000" strokeWidth="3" markerEnd="url(#arrow-red)" />
          {/* Inside tube rising all the way to top */}
          <path
            d="M 670,735 L 700,735 L 700,190 L 730,190"
            fill="none"
            stroke="#ff0000"
            strokeWidth="2.5"
          />

          {/* LNG Overhead Outlet line (Magenta) */}
          <path
            d="M 730,190 L 730,160 L 1230,160"
            fill="none"
            stroke="#e879f9"
            strokeWidth="3.5"
            markerEnd="url(#arrow-magenta)"
          />

          {/* LNG split to 5C-2 and Storage */}
          <line x1="1230" y1="160" x2="1230" y2="290" stroke="#e879f9" strokeWidth="3" />
          
          {/* Valve TV1A */}
          <path d="M 1220,290 L 1240,310 L 1240,290 L 1220,310 Z" fill="#ff1e1e" stroke="#ffffff" strokeWidth="1" />
          <line x1="1230" y1="310" x2="1230" y2="350" stroke="#e879f9" strokeWidth="3" markerEnd="url(#arrow-magenta)" />
          <text x="1275" y="355" fill="#00ff00" fontSize="14" fontWeight="bold">5C-2</text>

          {/* Bypass line down to LNG > STRG */}
          <line x1="1230" y1="210" x2="1320" y2="210" stroke="#e879f9" strokeWidth="2.5" />
          <line x1="1320" y1="210" x2="1320" y2="470" stroke="#e879f9" strokeWidth="2.5" />
          {/* Valve TV1B */}
          <path d="M 1310,470 L 1330,490 L 1330,470 L 1310,490 Z" fill="#ff1e1e" stroke="#ffffff" strokeWidth="1" />
          <line x1="1320" y1="490" x2="1320" y2="540" stroke="#e879f9" strokeWidth="2.5" markerEnd="url(#arrow-magenta)" />
          <text x="1350" y="530" fill="#e879f9" fontSize="13" fontWeight="bold">LNG&gt;</text>
          <text x="1350" y="546" fill="#e879f9" fontSize="13" fontWeight="bold">STRG</text>
          <text x="1350" y="570" fill="#e879f9" fontSize="11">PUMP BYPASS</text>

          {/* =============================================================== */}
          {/* STREAM 2: MR VAPOR INLET (YELLOW)                               */}
          {/* =============================================================== */}
          <text x="140" y="515" fill="#ffff00" fontSize="14" fontWeight="bold">MR VAP</text>
          <line x1="205" y1="510" x2="350" y2="510" stroke="#ffff00" strokeWidth="3" markerEnd="url(#arrow-yellow)" />
          
          {/* Tube inside warm bundle and up to Cold JT Valve HIC2 */}
          <path
            d="M 350,510 L 420,510 L 420,240 L 710,240"
            fill="none"
            stroke="#ffff00"
            strokeWidth="2.5"
          />
          {/* Top Spray Valve HIC2 */}
          <path d="M 540,230 L 560,250 L 560,230 L 540,250 Z" fill="#e69138" stroke="#ffffff" strokeWidth="1" />
          {/* Spray downwards into cold bundle */}
          <line x1="710" y1="240" x2="710" y2="270" stroke="#ffff00" strokeWidth="2.5" markerEnd="url(#arrow-yellow)" />

          {/* =============================================================== */}
          {/* STREAM 3: MR LIQUID INLET & WARM JT SPRAY (YELLOW)              */}
          {/* =============================================================== */}
          <text x="280" y="735" fill="#ffff00" fontSize="14" fontWeight="bold">MR LIQ</text>
          <line x1="345" y1="730" x2="630" y2="730" stroke="#ffff00" strokeWidth="3" markerEnd="url(#arrow-yellow)" />
          
          {/* Mid spray header loop from warm tube to warm spray valve HIC3 */}
          <path
            d="M 630,560 L 510,560 L 510,560"
            fill="none"
            stroke="#ffff00"
            strokeWidth="2.5"
          />
          {/* Warm Spray Valve HIC3 */}
          <path d="M 520,550 L 540,570 L 540,550 L 520,570 Z" fill="#e69138" stroke="#ffffff" strokeWidth="1" />
          <path d="M 540,560 L 670,560 L 670,490" fill="none" stroke="#ffff00" strokeWidth="2.5" markerEnd="url(#arrow-yellow)" />

          {/* Right warm spray line */}
          <path
            d="M 790,560 L 1030,560 L 1030,530"
            fill="none"
            stroke="#ffff00"
            strokeWidth="2.5"
          />
          <path d="M 1020,520 L 1040,540 L 1040,520 L 1020,540 Z" fill="#e69138" stroke="#ffffff" strokeWidth="1" />

          {/* =============================================================== */}
          {/* STREAM 4: OVERHEAD VAPOR TO LTSS (CYAN / DASHED)                */}
          {/* =============================================================== */}
          <path
            d="M 730,135 L 730,105 L 180,105"
            fill="none"
            stroke="#00ffff"
            strokeWidth="2.5"
            strokeDasharray="6 3"
          />
          {/* Valve on LTSS line */}
          <path d="M 280,95 L 300,115 L 300,95 L 280,115 Z" fill="#00ff00" stroke="#ffffff" strokeWidth="1" />
          <text x="140" y="110" fill="#00ffff" fontSize="13" fontWeight="bold">LTSS</text>

          {/* =============================================================== */}
          {/* STREAM 5: SHELL LP RETURN TO 4C-7 / 4K-2 (YELLOW)               */}
          {/* =============================================================== */}
          <path
            d="M 730,735 L 730,765 L 1220,765"
            fill="none"
            stroke="#ffff00"
            strokeWidth="3.5"
          />
          {/* Shutoff Valve 4HV11 */}
          <path d="M 1220,755 L 1240,775 L 1240,755 L 1220,775 Z" fill="#ff1e1e" stroke="#ffffff" strokeWidth="1" />
          <line x1="1240" y1="765" x2="1340" y2="765" stroke="#ffff00" strokeWidth="3.5" markerEnd="url(#arrow-yellow)" />
          <text x="1350" y="770" fill="#ffff00" fontSize="14" fontWeight="bold">4C-7</text>
          <text x="1225" y="795" fill="#ffff00" fontSize="11">4HV11</text>

          {/* =============================================================== */}
          {/* DCS INSTRUMENT TAG BOXES & READINGS (INTERACTIVE)               */}
          {/* =============================================================== */}

          {/* 1. Feed Gas Inlet: PI12, TI23, TI50 */}
          {/* PI12 */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'PI12', name: 'Feed Gas Inlet Pressure', unit: 'KGC2G', valDcs: 43.15, valAi: 43.15 })}>
            <text x="240" y="785" fill="#00ffff" fontSize="12" fontWeight="bold">PI12</text>
            <text x="220" y="805" fill={displayMode === 'AI_OPTIMIZED' ? '#34d399' : '#ffffff'} fontSize="16" fontWeight="bold">
              {fmt('PI12', 43.15, 43.15, 2).display}
            </text>
            <text x="275" y="805" fill="#00ffff" fontSize="10">KGC2G</text>
          </g>

          {/* TI23 */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'TI23', name: 'Feed Gas Inlet Temperature', unit: '°C', valDcs: -54.8, valAi: -54.8 })}>
            <text x="380" y="785" fill="#00ffff" fontSize="12" fontWeight="bold">TI23</text>
            <text x="360" y="805" fill="#ffffff" fontSize="16" fontWeight="bold">-54.8</text>
            <text x="420" y="805" fill="#00ffff" fontSize="11">°C</text>
          </g>

          {/* TI50 */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'TI50', name: 'Feed Gas Chilled Temperature', unit: '°C', valDcs: -36.0, valAi: -36.0 })}>
            <text x="500" y="785" fill="#00ffff" fontSize="12" fontWeight="bold">TI50</text>
            <text x="480" y="805" fill="#ffffff" fontSize="16" fontWeight="bold">-36.0</text>
            <text x="540" y="805" fill="#00ffff" fontSize="11">°C</text>
          </g>

          {/* 2. Cold Separator Level: LI2 */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'LI2', name: 'Cold Bundle Separator Level', unit: '%', valDcs: 39.0, valAi: 39.0 })}>
            <text x="800" y="275" fill="#00ffff" fontSize="13" fontWeight="bold">LI2</text>
            <text x="840" y="275" fill="#ffffff" fontSize="16" fontWeight="bold">39.0</text>
            <text x="880" y="275" fill="#00ffff" fontSize="11">%</text>
          </g>

          {/* 3. Warm Separator Level: LI3 */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'LI3', name: 'Warm Bundle Separator Level', unit: '%', valDcs: 48.5, valAi: 48.5 })}>
            <text x="800" y="520" fill="#00ffff" fontSize="13" fontWeight="bold">LI3</text>
            <text x="840" y="520" fill="#ffffff" fontSize="16" fontWeight="bold">48.5</text>
            <text x="880" y="520" fill="#00ffff" fontSize="11">%</text>
          </g>

          {/* 4. Cold Differential Pressure: PDI4 */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'PDI4', name: 'Cold Bundle Differential Pressure', unit: 'KGC2G', valDcs: 0.067, valAi: 0.062, limit: '< 0.100 KGC2G' })}>
            <text x="530" y="340" fill="#00ffff" fontSize="13" fontWeight="bold">PDI4</text>
            <text x="500" y="365" fill={displayMode === 'AI_OPTIMIZED' ? '#34d399' : '#ffffff'} fontSize="18" fontWeight="bold">
              {fmt('PDI4', 0.067, pdiCold, 3).display}
            </text>
            <text x="575" y="365" fill="#00ffff" fontSize="11">KGC2G</text>
          </g>

          {/* HIC2 Valve Position */}
          <text x="520" y="270" fill="#00ffff" fontSize="12" fontWeight="bold">HIC2</text>
          <text x="520" y="288" fill="#ffffff" fontSize="14" fontWeight="bold">100.0 %</text>

          {/* 5. Warm Differential Pressure: PDI3 */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'PDI3', name: 'Warm Bundle Differential Pressure', unit: 'KGC2', valDcs: 0.240, valAi: 0.215, limit: '< 0.350 KGC2' })}>
            <text x="510" y="630" fill="#00ffff" fontSize="13" fontWeight="bold">PDI3</text>
            <text x="490" y="655" fill={displayMode === 'AI_OPTIMIZED' ? '#34d399' : '#ffffff'} fontSize="18" fontWeight="bold">
              {fmt('PDI3', 0.240, pdiWarm, 3).display}
            </text>
            <text x="560" y="655" fill="#00ffff" fontSize="11">KGC2</text>
          </g>

          {/* HIC3 Valve Position */}
          <text x="500" y="590" fill="#00ffff" fontSize="12" fontWeight="bold">HIC3</text>
          <text x="500" y="608" fill="#ffffff" fontSize="14" fontWeight="bold">100.0 %</text>

          {/* 6. LNG Rundown Outlet: TIC1A/B and TI29 */}
          {/* TIC1A/B */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'TIC1A/B', name: 'LNG Rundown Temperature Controller', unit: '°C', valDcs: -151.2, valAi: lngTemp, limit: 'Target ≤ -150.0°C' })}>
            <text x="1190" y="240" fill="#00ffff" fontSize="13" fontWeight="bold">TIC1A/B</text>
            <text x="1180" y="265" fill={displayMode === 'AI_OPTIMIZED' ? '#34d399' : '#ffffff'} fontSize="18" fontWeight="bold">
              {fmt('TIC1A/B', -151.2, lngTemp, 1).display}
            </text>
            <text x="1255" y="265" fill="#00ffff" fontSize="12">°C</text>
          </g>

          {/* TI29 */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'TI29', name: 'LNG Product Temperature', unit: '°C', valDcs: -153.6, valAi: -153.8 })}>
            <text x="1100" y="240" fill="#00ffff" fontSize="12" fontWeight="bold">TI29</text>
            <text x="1080" y="262" fill="#ffffff" fontSize="16" fontWeight="bold">-153.6</text>
            <text x="1145" y="262" fill="#00ffff" fontSize="11">°C</text>
          </g>

          {/* 7. MR Vapor Inlet Tags: FI1, PI1, TI47 */}
          {/* FI1 */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'FI1', name: 'MR Vapor Flow Rate', unit: 'KNM3/H', valDcs: 128.0, valAi: 128.0 })}>
            <text x="240" y="440" fill="#00ffff" fontSize="13" fontWeight="bold">FI1</text>
            <text x="220" y="465" fill="#ffffff" fontSize="16" fontWeight="bold">128.0</text>
            <text x="280" y="465" fill="#00ffff" fontSize="11">KNM3/H</text>
          </g>

          {/* PI1 */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'PI1', name: 'MR Vapor Pressure', unit: 'KGC2G', valDcs: 36.90, valAi: 35.15 })}>
            <text x="280" y="540" fill="#00ffff" fontSize="12" fontWeight="bold">PI1</text>
            <text x="260" y="562" fill={displayMode === 'AI_OPTIMIZED' ? '#34d399' : '#ffffff'} fontSize="16" fontWeight="bold">
              {fmt('PI1', 36.90, 35.15, 2).display}
            </text>
            <text x="320" y="562" fill="#00ffff" fontSize="10">KGC2G</text>
          </g>

          {/* TI47 */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'TI47', name: 'MR Vapor Temperature', unit: '°C', valDcs: -35.1, valAi: -35.1 })}>
            <text x="280" y="620" fill="#00ffff" fontSize="12" fontWeight="bold">TI47</text>
            <text x="260" y="642" fill="#ffffff" fontSize="16" fontWeight="bold">-35.1</text>
            <text x="315" y="642" fill="#00ffff" fontSize="11">°C</text>
          </g>

          {/* 8. Shell Bottom Return: TI8, PI9, TI48, TI49 */}
          {/* TI8 (Suction Temp returning to 4C-7 / 4K-2) */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'TI8', name: 'MCHE Bottom Outlet / Compressor Suction Temp', unit: '°C', valDcs: -44.8, valAi: suctTemp, limit: 'TAL Interlock ≥ -45.0°C' })}>
            <rect x="1080" y="745" width="115" height="42" fill="#064e3b" stroke="#10b981" strokeWidth="1.5" rx="4" />
            <text x="1090" y="762" fill="#34d399" fontSize="12" fontWeight="bold">TI8 (TAL)</text>
            <text x="1090" y="780" fill="#ffffff" fontSize="16" fontWeight="bold">
              {fmt('TI8', -44.8, suctTemp, 1).display} °C
            </text>
          </g>

          {/* PI9 (Suction Pressure) */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'PI9', name: 'MCHE Bottom Outlet / Compressor Suction Pressure', unit: 'KGC2G', valDcs: 2.284, valAi: suctPress })}>
            <text x="960" y="775" fill="#00ffff" fontSize="12" fontWeight="bold">PI9</text>
            <text x="940" y="795" fill={displayMode === 'AI_OPTIMIZED' ? '#34d399' : '#ffffff'} fontSize="16" fontWeight="bold">
              {fmt('PI9', 2.284, suctPress, 3).display}
            </text>
            <text x="1000" y="795" fill="#00ffff" fontSize="10">KGC2G</text>
          </g>

          {/* TI48 & TI49 */}
          <text x="860" y="670" fill="#00ffff" fontSize="11">TI49: <tspan fill="#ffffff" fontWeight="bold">-43.4 °C</tspan></text>
          <text x="860" y="690" fill="#00ffff" fontSize="11">TI48: <tspan fill="#ffffff" fontWeight="bold">-43.6 °C</tspan></text>

          {/* 9. MCR Liquid Flow Rate: FIC2 */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'FIC2', name: 'MCR Liquid Circulation Flow', unit: 'M3/H', valDcs: 875, valAi: 810 })}>
            <text x="1060" y="550" fill="#00ffff" fontSize="13" fontWeight="bold">FIC2</text>
            <text x="1040" y="575" fill={displayMode === 'AI_OPTIMIZED' ? '#34d399' : '#ffffff'} fontSize="18" fontWeight="bold">
              {fmt('FIC2', 875, 810, 0).display}
            </text>
            <text x="1100" y="575" fill="#00ffff" fontSize="11">M3/H</text>
          </g>

          {/* 10. Overhead Vapor Tags: PIC2, TI20, TI24 */}
          {/* PIC2 */}
          <text x="280" y="75" fill="#00ffff" fontSize="12" fontWeight="bold">PIC2</text>
          <text x="280" y="92" fill="#ffffff" fontSize="15" fontWeight="bold">2.70 <tspan fill="#00ffff" fontSize="10">KGC2G</tspan></text>

          {/* TI20 & TI24 */}
          <text x="490" y="75" fill="#00ffff" fontSize="12" fontWeight="bold">TI20</text>
          <text x="490" y="92" fill="#ffffff" fontSize="15" fontWeight="bold">-134.6 <tspan fill="#00ffff" fontSize="10">°C</tspan></text>
          <text x="490" y="115" fill="#00ffff" fontSize="12" fontWeight="bold">TI24</text>
          <text x="490" y="132" fill="#ffffff" fontSize="15" fontWeight="bold">-151.3 <tspan fill="#00ffff" fontSize="10">°C</tspan></text>

          {/* =============================================================== */}
          {/* BOTTOM CENTUM VP SOFTKEY BAR                                    */}
          {/* =============================================================== */}
          {['CG0269', 'CG0270', 'CG0271', 'CG0272', 'CG0273', 'CG0274', 'TG0129', 'TG0130'].map((btn, idx) => (
            <g key={btn} transform={`translate(${140 + idx * 165}, 815)`}>
              <rect width="135" height="35" fill="#334155" stroke="#64748b" strokeWidth="1" rx="2" />
              <text x="67" y="23" fill="#f8fafc" fontSize="13" fontWeight="bold" textAnchor="middle">
                {btn}
              </text>
            </g>
          ))}
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
              <span style={{ color: '#94a3b8' }}>AI Skenario:</span>
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
