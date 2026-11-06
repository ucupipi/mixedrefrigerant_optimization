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

        {/* SVG Centum Graphic Area (Native DCS Coordinate System: 1920 x 755 matching image56.png) */}
        <svg
          viewBox="0 140 1920 755"
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
            MAIN HEAT EXCHANGER
          </text>
          <text x="1450" y="185" fill="#1d4ed8" fontSize="15" fontWeight="bold">
            RESET 5HC25
          </text>

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
          {/* Cold Spray Nozzle Crosses */}
          <text x="855" y="332" fill="#00ffff" fontSize="13" textAnchor="middle" fontWeight="bold">x   x</text>
          {/* Signal line from LI2 tray to tag */}
          <line x1="885" y1="305" x2="990" y2="305" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="4 3" />

          {/* Warm Spray Tray LI3 (U-cup) */}
          <path d="M 830,560 L 830,595 L 880,595 L 880,560" fill="none" stroke="#00ff00" strokeWidth="2" />
          <rect x="831" y="575" width="48" height="19" fill="#0284c7" opacity="0.45" />
          {/* Warm Spray Nozzle Crosses */}
          <text x="855" y="612" fill="#00ffff" fontSize="13" textAnchor="middle" fontWeight="bold">x   x   x</text>
          {/* Signal line from LI3 tray to tag */}
          <line x1="880" y1="585" x2="990" y2="585" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="4 3" />

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
          {/* Cross marks on Feed Gas line */}
          <text x="345" y="845" fill="#ff0000" fontSize="14" textAnchor="middle" fontWeight="bold">x</text>
          <text x="525" y="845" fill="#ff0000" fontSize="14" textAnchor="middle" fontWeight="bold">x</text>
          <text x="680" y="845" fill="#ff0000" fontSize="14" textAnchor="middle" fontWeight="bold">x</text>
          {/* Signal drop lines to feed sensors */}
          <line x1="345" y1="841" x2="345" y2="865" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="3 3" />
          <line x1="525" y1="841" x2="525" y2="865" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="3 3" />
          <line x1="680" y1="841" x2="680" y2="865" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="3 3" />

          {/* =============================================================== */}
          {/* STREAM 2: LNG RUNDOWN (MAGENTA LINE)                            */}
          {/* Horizontal segment y=253, vertical drop x=1487                  */}
          {/* Branches: TV1A to 5C-2 (y=393), HIC6 bypass (y=476), TV1B (y=617)*/}
          {/* =============================================================== */}
          <line x1="915" y1="253" x2="1487" y2="253" stroke="#e879f9" strokeWidth="2.5" />
          {/* Arrow on horizontal LNG line */}
          <polygon points="980,249 990,253 980,257" fill="#ff0000" />
          <line x1="1487" y1="253" x2="1487" y2="617" stroke="#e879f9" strokeWidth="2.5" />
          {/* Cross marks on vertical LNG header */}
          <text x="1487" y="289" fill="#ff0000" fontSize="14" textAnchor="middle" fontWeight="bold">x</text>
          <text x="1487" y="480" fill="#ff0000" fontSize="14" textAnchor="middle" fontWeight="bold">x</text>
          <text x="1487" y="621" fill="#ff0000" fontSize="14" textAnchor="middle" fontWeight="bold">x</text>

          {/* Branch 1 (y=393): Main Rundown to 5C-2 */}
          <line x1="1487" y1="393" x2="1670" y2="393" stroke="#e879f9" strokeWidth="2.5" markerEnd="url(#arrow-red)" />
          {/* TV1A Diaphragm Control Valve at x=1570, y=393 */}
          <path d="M 1558,385 L 1582,401 L 1582,385 L 1558,401 Z" fill="#d946ef" stroke="#ffffff" strokeWidth="1" />
          <line x1="1570" y1="385" x2="1570" y2="375" stroke="#d946ef" strokeWidth="1.5" />
          <path d="M 1558,375 A 12,12 0 0,1 1582,375 Z" fill="#d946ef" stroke="#ffffff" strokeWidth="1" />
          <text x="1570" y="365" fill="#00ffff" fontSize="12" textAnchor="middle" fontWeight="bold">TV1A</text>
          <text x="1685" y="415" fill="#00ff00" fontSize="16" fontWeight="bold">5C-2</text>

          {/* Branch 2 (y=476): Bypass with HIC6 */}
          <line x1="1487" y1="476" x2="1608" y2="476" stroke="#e879f9" strokeWidth="2.5" />
          {/* HIC6 Diaphragm Control Valve at x=1564, y=476 */}
          <path d="M 1552,468 L 1576,484 L 1576,468 L 1552,484 Z" fill="#d946ef" stroke="#ffffff" strokeWidth="1" />
          <line x1="1564" y1="468" x2="1564" y2="458" stroke="#d946ef" strokeWidth="1.5" />
          <path d="M 1552,458 A 12,12 0 0,1 1576,458 Z" fill="#d946ef" stroke="#ffffff" strokeWidth="1" />
          {/* Upward riser merging into 5C-2 line */}
          <line x1="1608" y1="476" x2="1608" y2="393" stroke="#e879f9" strokeWidth="2.5" markerEnd="url(#arrow-red)" />
          <text x="1625" y="520" fill="#00ffff" fontSize="12" fontWeight="bold">HIC6</text>
          <text x="1610" y="540" fill="#ffffff" fontSize="15" fontWeight="bold">0.0 <tspan fill="#00ffff" fontSize="11">%</tspan></text>

          {/* Branch 3 (y=617): TV1B to LNG > STRG PUMP BYPASS */}
          <line x1="1487" y1="617" x2="1675" y2="617" stroke="#e879f9" strokeWidth="2.5" markerEnd="url(#arrow-red)" />
          {/* TV1B Diaphragm Control Valve at x=1625, y=617 */}
          <path d="M 1613,609 L 1637,625 L 1637,609 L 1613,625 Z" fill="#d946ef" stroke="#ffffff" strokeWidth="1" />
          <line x1="1625" y1="609" x2="1625" y2="599" stroke="#d946ef" strokeWidth="1.5" />
          <path d="M 1613,599 A 12,12 0 0,1 1637,599 Z" fill="#d946ef" stroke="#ffffff" strokeWidth="1" />
          <text x="1625" y="589" fill="#00ffff" fontSize="12" textAnchor="middle" fontWeight="bold">TV1B</text>
          {/* Cross mark before TV1B for FAL FI6B */}
          <text x="1550" y="621" fill="#ff0000" fontSize="14" textAnchor="middle" fontWeight="bold">x</text>
          <line x1="1550" y1="617" x2="1550" y2="690" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="3 3" />
          {/* Destination Labels */}
          <text x="1690" y="612" fill="#e879f9" fontSize="14" fontWeight="bold">LNG&gt;</text>
          <text x="1690" y="632" fill="#e879f9" fontSize="14" fontWeight="bold">STRG</text>
          <text x="1690" y="668" fill="#e879f9" fontSize="12" fontWeight="bold">PUMP</text>
          <text x="1690" y="688" fill="#e879f9" fontSize="12" fontWeight="bold">BYPASS</text>

          {/* Signal lines around LNG rundown */}
          <line x1="1487" y1="285" x2="1400" y2="285" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="3 3" />
          <line x1="1487" y1="285" x2="1550" y2="285" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="3 3" />
          <line x1="1550" y1="285" x2="1550" y2="230" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="3 3" />
          <line x1="1550" y1="230" x2="1720" y2="230" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="3 3" markerEnd="url(#arrow-cyan)" />
          <text x="1730" y="235" fill="#00ffff" fontSize="13" fontWeight="bold">FIC4</text>
          <line x1="1550" y1="285" x2="1550" y2="370" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="3 3" />
          <line x1="1550" y1="370" x2="1570" y2="370" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="3 3" />
          <line x1="1487" y1="476" x2="1420" y2="476" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="3 3" />

          {/* =============================================================== */}
          {/* STREAM 3: MR VAPOR INLET (YELLOW LINE y=561 -> x=458 -> y=784)   */}
          {/* =============================================================== */}
          <text x="125" y="566" fill="#ffff00" fontSize="14" fontWeight="bold">MR VAP</text>
          <line x1="210" y1="561" x2="458" y2="561" stroke="#ffff00" strokeWidth="2.5" />
          <text x="340" y="565" fill="#ffff00" fontSize="14" textAnchor="middle" fontWeight="bold">x</text>
          <text x="398" y="565" fill="#ffff00" fontSize="14" textAnchor="middle" fontWeight="bold">x</text>
          {/* Downward drop at x=458 */}
          <line x1="458" y1="561" x2="458" y2="784" stroke="#ffff00" strokeWidth="2.5" />
          <polygon points="454,720 458,730 462,720" fill="#ffff00" />
          {/* Turn right horizontally into warm bundle entry */}
          <line x1="458" y1="784" x2="755" y2="784" stroke="#ffff00" strokeWidth="2.5" markerEnd="url(#arrow-yellow)" />
          {/* Signal lines for FI1, PI1 */}
          <line x1="398" y1="561" x2="398" y2="495" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="3 3" />
          <line x1="340" y1="561" x2="340" y2="600" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="3 3" />

          {/* =============================================================== */}
          {/* STREAM 4: MR LIQUID INLET (ORANGE LINE y=812)                   */}
          {/* =============================================================== */}
          <text x="430" y="805" fill="#e69138" fontSize="14" fontWeight="bold">MR LIQ</text>
          <line x1="380" y1="812" x2="755" y2="812" stroke="#e69138" strokeWidth="2.5" markerEnd="url(#arrow-orange)" />
          <text x="680" y="816" fill="#e69138" fontSize="14" textAnchor="middle" fontWeight="bold">x</text>

          {/* =============================================================== */}
          {/* STREAM 5: COLD MR LOOPS (LEFT & RIGHT)                          */}
          {/* Left: emerging y=337 -> x=551 -> y=310 -> HIC2 -> cold tray     */}
          {/* Right: emerging y=337 -> PRIC15 -> x=1311 -> y=281 -> cold tray*/}
          {/* =============================================================== */}
          {/* Left Cold MR Loop with HIC2 */}
          <path d="M 794,337 L 551,337 L 551,310 L 794,310" fill="none" stroke="#e69138" strokeWidth="2.5" markerEnd="url(#arrow-orange)" />
          {/* HIC2 Hand/Throttle Valve at x=595, y=310 */}
          <path d="M 583,302 L 607,318 L 607,302 L 583,318 Z" fill="#e69138" stroke="#ffffff" strokeWidth="1" />
          <line x1="595" y1="302" x2="595" y2="292" stroke="#e69138" strokeWidth="1.5" />
          <rect x="585" y="286" width="20" height="6" fill="#e69138" stroke="#ffffff" strokeWidth="0.8" />
          <text x="595" y="348" fill="#00ffff" fontSize="12" textAnchor="middle" fontWeight="bold">HIC2</text>
          <text x="595" y="368" fill="#ffffff" fontSize="14" textAnchor="middle" fontWeight="bold">100.0 <tspan fill="#00ffff" fontSize="10">%</tspan></text>
          <text x="648" y="314" fill="#e69138" fontSize="14" textAnchor="middle" fontWeight="bold">x</text>
          {/* Blue signal line to PDI4 */}
          <line x1="648" y1="310" x2="648" y2="390" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="3 3" />
          <line x1="794" y1="345" x2="760" y2="345" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="3 3" />
          <text x="794" y="349" fill="#00ffff" fontSize="13" textAnchor="middle" fontWeight="bold">x</text>

          {/* Right Cold MR Loop with PRIC15 */}
          <line x1="915" y1="337" x2="1247" y2="337" stroke="#ffff00" strokeWidth="2.5" />
          <text x="1000" y="341" fill="#ffff00" fontSize="14" textAnchor="middle" fontWeight="bold">x</text>
          <text x="1170" y="341" fill="#ffff00" fontSize="14" textAnchor="middle" fontWeight="bold">x</text>
          {/* PRIC15 Diaphragm Control Valve at x=1247, y=337 */}
          <path d="M 1235,329 L 1259,345 L 1259,329 L 1235,345 Z" fill="#ffff00" stroke="#ffffff" strokeWidth="1" />
          <line x1="1247" y1="329" x2="1247" y2="319" stroke="#ffff00" strokeWidth="1.5" />
          <path d="M 1235,319 A 12,12 0 0,1 1259,319 Z" fill="#ffff00" stroke="#ffffff" strokeWidth="1" />
          {/* Loop across and into top tray */}
          <path d="M 1259,337 L 1311,337 L 1311,281 L 855,281 L 855,295" fill="none" stroke="#e69138" strokeWidth="2.5" markerEnd="url(#arrow-orange)" />
          <text x="1280" y="285" fill="#e69138" fontSize="14" textAnchor="middle" fontWeight="bold">x</text>
          {/* Signal line from PRIC15 valve */}
          <line x1="1247" y1="319" x2="1247" y2="300" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="3 3" />
          <line x1="1247" y1="300" x2="1360" y2="300" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="3 3" />
          <text x="1380" y="345" fill="#00ffff" fontSize="13" fontWeight="bold">PRIC15</text>
          <text x="1380" y="365" fill="#ffffff" fontSize="16" fontWeight="bold">18.00</text>

          {/* =============================================================== */}
          {/* STREAM 6: WARM MR LOOPS (LEFT & RIGHT)                          */}
          {/* Left: emerging y=617 -> x=563 -> y=562 -> HIC3 -> warm tray     */}
          {/* Right: emerging y=590 -> HIC51 -> x=1311 -> y=534 -> warm tray  */}
          {/* =============================================================== */}
          {/* Left Warm MR Loop with HIC3 */}
          <path d="M 755,617 L 563,617 L 563,562 L 755,562" fill="none" stroke="#e69138" strokeWidth="2.5" markerEnd="url(#arrow-orange)" />
          {/* HIC3 Hand/Throttle Valve at x=690, y=562 */}
          <path d="M 678,554 L 702,570 L 702,554 L 678,570 Z" fill="#e69138" stroke="#ffffff" strokeWidth="1" />
          <line x1="690" y1="554" x2="690" y2="544" stroke="#e69138" strokeWidth="1.5" />
          <rect x="680" y="538" width="20" height="6" fill="#e69138" stroke="#ffffff" strokeWidth="0.8" />
          <text x="720" y="600" fill="#00ffff" fontSize="12" fontWeight="bold">HIC3</text>
          <text x="720" y="620" fill="#ffffff" fontSize="14" fontWeight="bold">100.0 <tspan fill="#00ffff" fontSize="10">%</tspan></text>
          <text x="648" y="566" fill="#e69138" fontSize="14" textAnchor="middle" fontWeight="bold">x</text>
          {/* Blue signal lines to PDI3 */}
          <line x1="755" y1="617" x2="725" y2="617" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="3 3" />
          <text x="755" y="621" fill="#00ffff" fontSize="13" textAnchor="middle" fontWeight="bold">x</text>

          {/* Right Warm MR Loop with HIC51 */}
          <line x1="954" y1="590" x2="1256" y2="590" stroke="#e69138" strokeWidth="2.5" />
          <text x="1050" y="594" fill="#e69138" fontSize="14" textAnchor="middle" fontWeight="bold">x</text>
          <text x="1100" y="594" fill="#e69138" fontSize="14" textAnchor="middle" fontWeight="bold">x</text>
          <text x="1170" y="594" fill="#e69138" fontSize="14" textAnchor="middle" fontWeight="bold">x</text>
          {/* HIC51 Diaphragm Control Valve at x=1256, y=590 */}
          <path d="M 1244,582 L 1268,598 L 1268,582 L 1244,598 Z" fill="#e69138" stroke="#ffffff" strokeWidth="1" />
          <line x1="1256" y1="582" x2="1256" y2="572" stroke="#e69138" strokeWidth="1.5" />
          <path d="M 1244,572 A 12,12 0 0,1 1268,572 Z" fill="#e69138" stroke="#ffffff" strokeWidth="1" />
          {/* Loop across and into warm tray */}
          <path d="M 1268,590 L 1311,590 L 1311,534 L 855,534 L 855,570" fill="none" stroke="#e69138" strokeWidth="2.5" markerEnd="url(#arrow-orange)" />
          <text x="1280" y="538" fill="#e69138" fontSize="14" textAnchor="middle" fontWeight="bold">x</text>
          {/* Signal line from HIC51 to TI32 */}
          <line x1="1256" y1="572" x2="1256" y2="515" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="3 3" />
          <text x="1270" y="525" fill="#00ffff" fontSize="12" fontWeight="bold">HIC51</text>
          <text x="1270" y="546" fill="#ffffff" fontSize="15" fontWeight="bold">0.000 <tspan fill="#00ffff" fontSize="10">%</tspan></text>

          {/* =============================================================== */}
          {/* STREAM 7: OVERHEAD OFF-GAS TO LTSS (WHITE LINE y=237)           */}
          {/* =============================================================== */}
          <line x1="794" y1="237" x2="127" y2="237" stroke="#ffffff" strokeWidth="2.5" markerEnd="url(#arrow-white)" />
          <text x="127" y="258" fill="#ffffff" fontSize="14" fontWeight="bold">LTSS</text>
          {/* Green PIC2 Control Valve at x=220, y=244 */}
          <path d="M 208,236 L 232,252 L 232,236 L 208,252 Z" fill="#00ff00" stroke="#ffffff" strokeWidth="1" />
          <line x1="220" y1="236" x2="220" y2="226" stroke="#00ff00" strokeWidth="1.5" />
          <path d="M 208,226 A 12,12 0 0,1 232,226 Z" fill="#00ff00" stroke="#ffffff" strokeWidth="1" />
          {/* Signal line from line to PIC2 valve */}
          <line x1="265" y1="237" x2="265" y2="205" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="3 3" />
          <line x1="265" y1="205" x2="220" y2="205" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="3 3" />
          <line x1="220" y1="205" x2="220" y2="226" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="3 3" />
          {/* Cross marks on LTSS line */}
          <text x="265" y="241" fill="#ffffff" fontSize="14" textAnchor="middle" fontWeight="bold">x</text>
          <text x="422" y="241" fill="#ffffff" fontSize="14" textAnchor="middle" fontWeight="bold">x</text>
          <text x="648" y="241" fill="#ffffff" fontSize="14" textAnchor="middle" fontWeight="bold">x</text>
          {/* Signal lines to PI28, TI20, TI24 */}
          <line x1="422" y1="237" x2="422" y2="260" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="3 3" />
          <line x1="648" y1="237" x2="648" y2="205" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="3 3" />
          <line x1="648" y1="205" x2="740" y2="205" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="3 3" />
          <line x1="648" y1="237" x2="648" y2="268" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="3 3" />
          <line x1="648" y1="268" x2="740" y2="268" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="3 3" />

          {/* =============================================================== */}
          {/* STREAM 8: SHELL-SIDE LP SUCTION RETURN TO 4C-7 (YELLOW y=813)   */}
          {/* =============================================================== */}
          <line x1="954" y1="813" x2="1620" y2="813" stroke="#ffff00" strokeWidth="2.5" markerEnd="url(#arrow-yellow)" />
          {/* Cross marks on suction return line */}
          <text x="1056" y="817" fill="#ffff00" fontSize="14" textAnchor="middle" fontWeight="bold">x</text>
          <polygon points="1165,809 1175,813 1165,817" fill="#ffff00" />
          <text x="1350" y="817" fill="#ffff00" fontSize="14" textAnchor="middle" fontWeight="bold">x</text>
          <line x1="1056" y1="813" x2="1056" y2="835" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="3 3" />
          <line x1="1350" y1="813" x2="1350" y2="835" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="3 3" />
          {/* Red Gate Valve 4HV11 at x=1486, y=813 */}
          <path d="M 1474,801 L 1498,825 L 1498,801 L 1474,825 Z" fill="#ff0000" stroke="#ffffff" strokeWidth="1" />
          <line x1="1486" y1="801" x2="1486" y2="788" stroke="#ff0000" strokeWidth="2" />
          <line x1="1476" y1="788" x2="1496" y2="788" stroke="#ff0000" strokeWidth="2.5" />
          <text x="1486" y="842" fill="#00ffff" fontSize="12" textAnchor="middle" fontWeight="bold">4HV11</text>
          <text x="1635" y="818" fill="#bef264" fontSize="16" fontWeight="bold">4C-7</text>

          {/* =============================================================== */}
          {/* INTERACTIVE DCS INSTRUMENT TAG READINGS                         */}
          {/* Clickable boxes with live values according to active mode       */}
          {/* =============================================================== */}

          {/* 1. Feed Gas Tags: PI12, TI23, TI50 */}
          {/* PI12 */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'PI12', name: 'Feed Gas Inlet Pressure', unit: 'KGC2G', valDcs: 43.15, valAi: 43.15 })}>
            <text x="345" y="865" fill="#00ffff" fontSize="12" textAnchor="middle" fontWeight="bold">PI12</text>
            <text x="345" y="885" fill={displayMode === 'AI_OPTIMIZED' ? '#34d399' : '#ffffff'} fontSize="15" textAnchor="middle" fontWeight="bold">
              {fmt('PI12', 43.15, 43.15, 2).display} <tspan fill="#00ffff" fontSize="10">KGC2G</tspan>
            </text>
          </g>

          {/* TI23 */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'TI23', name: 'Feed Gas Inlet Temperature', unit: '°C', valDcs: -54.8, valAi: -54.8 })}>
            <text x="525" y="865" fill="#00ffff" fontSize="12" textAnchor="middle" fontWeight="bold">TI23</text>
            <text x="525" y="885" fill="#ffffff" fontSize="15" textAnchor="middle" fontWeight="bold">
              -54.8 <tspan fill="#00ffff" fontSize="10">°C</tspan>
            </text>
          </g>

          {/* TI50 */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'TI50', name: 'Feed Gas Chilled Temperature', unit: '°C', valDcs: -36.0, valAi: -36.0 })}>
            <text x="680" y="865" fill="#00ffff" fontSize="12" textAnchor="middle" fontWeight="bold">TI50</text>
            <text x="680" y="885" fill="#ffffff" fontSize="15" textAnchor="middle" fontWeight="bold">
              -36.0 <tspan fill="#00ffff" fontSize="10">°C</tspan>
            </text>
          </g>

          {/* 2. Top Off-gas Tags: PIC2, PI28A/B/C, TI20, TI24 */}
          {/* PIC2 */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'PIC2', name: 'Overhead Off-gas Pressure Controller', unit: 'KGC2G', valDcs: 2.70, valAi: 2.70 })}>
            <text x="405" y="215" fill="#00ffff" fontSize="12" fontWeight="bold">PIC2</text>
            <text x="405" y="235" fill="#ffffff" fontSize="15" fontWeight="bold">
              2.70 <tspan fill="#00ffff" fontSize="10">KGC2G</tspan>
            </text>
          </g>

          {/* PI28A/B/C */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'PI28A/B/C', name: 'Off-gas Pressure 3-out-of-1', unit: 'KGC2G', valDcs: 2.64, valAi: 2.64 })}>
            <text x="390" y="268" fill="#00ffff" fontSize="12" fontWeight="bold">PI28A/B/C</text>
            <text x="340" y="292" fill="#ffffff" fontSize="13">A  <tspan fontWeight="bold">2.643</tspan> <tspan fill="#00ffff" fontSize="10">KGC2G</tspan></text>
            <text x="340" y="314" fill="#ffffff" fontSize="13">B  <tspan fontWeight="bold">2.640</tspan> <tspan fill="#00ffff" fontSize="10">KGC2G</tspan></text>
            <text x="340" y="336" fill="#ffffff" fontSize="13">C  <tspan fontWeight="bold">2.645</tspan> <tspan fill="#00ffff" fontSize="10">KGC2G</tspan></text>
          </g>

          {/* TI20 & TI24 */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'TI20', name: 'Overhead Vapor Temp Upper', unit: '°C', valDcs: -134.6, valAi: -134.6 })}>
            <text x="745" y="205" fill="#00ffff" fontSize="12" fontWeight="bold">TI20</text>
            <text x="745" y="225" fill="#ffffff" fontSize="15" fontWeight="bold">-134.6 <tspan fill="#00ffff" fontSize="10">°C</tspan></text>
          </g>
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'TI24', name: 'Overhead Vapor Temp Lower', unit: '°C', valDcs: -151.3, valAi: -151.3 })}>
            <text x="745" y="268" fill="#00ffff" fontSize="12" fontWeight="bold">TI24</text>
            <text x="745" y="288" fill="#ffffff" fontSize="15" fontWeight="bold">-151.3 <tspan fill="#00ffff" fontSize="10">°C</tspan></text>
          </g>

          {/* 3. Separator Levels: LI2 (Cold) & LI3 (Warm) */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'LI2', name: 'Cold Bundle Distributor Level', unit: '%', valDcs: 39.0, valAi: 39.0 })}>
            <text x="1000" y="308" fill="#00ffff" fontSize="13" fontWeight="bold">LI2</text>
            <text x="1040" y="308" fill="#ffffff" fontSize="16" fontWeight="bold">39.0 <tspan fill="#00ffff" fontSize="11">%</tspan></text>
          </g>
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'LI3', name: 'Warm Bundle Distributor Level', unit: '%', valDcs: 48.5, valAi: 48.5 })}>
            <text x="1000" y="588" fill="#00ffff" fontSize="13" fontWeight="bold">LI3</text>
            <text x="1040" y="588" fill="#ffffff" fontSize="16" fontWeight="bold">48.5 <tspan fill="#00ffff" fontSize="11">%</tspan></text>
          </g>

          {/* 4. Differential Pressure: PDI4 (Cold) & PDI3 (Warm) */}
          {/* PDI4 */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'PDI4', name: 'Cold Bundle Differential Pressure', unit: 'KGC2G', valDcs: 0.067, valAi: pdiCold, limit: '< 0.100 KGC2G' })}>
            <text x="680" y="390" fill="#00ffff" fontSize="13" fontWeight="bold">PDI4</text>
            <text x="640" y="415" fill={displayMode === 'AI_OPTIMIZED' ? '#34d399' : '#ffffff'} fontSize="18" fontWeight="bold">
              {fmt('PDI4', 0.067, pdiCold, 3).display} <tspan fill="#00ffff" fontSize="11">KGC2G</tspan>
            </text>
          </g>

          {/* PDI3 */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'PDI3', name: 'Warm Bundle Differential Pressure', unit: 'KGC2', valDcs: 0.240, valAi: pdiWarm, limit: '< 0.350 KGC2' })}>
            <text x="680" y="655" fill="#00ffff" fontSize="13" fontWeight="bold">PDI3</text>
            <text x="640" y="680" fill={displayMode === 'AI_OPTIMIZED' ? '#34d399' : '#ffffff'} fontSize="18" fontWeight="bold">
              {fmt('PDI3', 0.240, pdiWarm, 3).display} <tspan fill="#00ffff" fontSize="11">KGC2</tspan>
            </text>
          </g>

          {/* Intermediate Column Wall Temperatures (Left) */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'TI25', name: 'Cold Bundle Tube Inlet Temp', unit: '°C', valDcs: -130.6, valAi: -130.6 })}>
            <text x="590" y="450" fill="#00ffff" fontSize="12" fontWeight="bold">TI25</text>
            <text x="640" y="450" fill="#ffffff" fontSize="14" fontWeight="bold">-130.6 <tspan fill="#00ffff" fontSize="10">°C</tspan></text>
            <line x1="715" y1="446" x2="794" y2="446" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="3 3" />
          </g>
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'TI26', name: 'Warm Bundle Tube Outlet Temp', unit: '°C', valDcs: -126.4, valAi: -126.4 })}>
            <text x="590" y="475" fill="#00ffff" fontSize="12" fontWeight="bold">TI26</text>
            <text x="640" y="475" fill="#ffffff" fontSize="14" fontWeight="bold">-126.4 <tspan fill="#00ffff" fontSize="10">°C</tspan></text>
            <line x1="715" y1="471" x2="775" y2="471" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="3 3" />
          </g>
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'TI22', name: 'Warm Bundle Upper Temperature', unit: '°C', valDcs: -132.4, valAi: -132.4 })}>
            <text x="590" y="500" fill="#00ffff" fontSize="12" fontWeight="bold">TI22</text>
            <text x="640" y="500" fill="#ffffff" fontSize="14" fontWeight="bold">-132.4 <tspan fill="#00ffff" fontSize="10">°C</tspan></text>
            <line x1="715" y1="496" x2="755" y2="496" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="3 3" />
          </g>

          {/* 5. MR Vapor Inlet Tags: FI1, PI1, 5C-1, TI47, PDI25 */}
          {/* FI1 */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'FI1', name: 'MR Vapor Flow Rate', unit: 'KNM3/H', valDcs: 128.0, valAi: 128.0 })}>
            <text x="398" y="450" fill="#00ffff" fontSize="13" textAnchor="middle" fontWeight="bold">FI1</text>
            <text x="398" y="475" fill="#ffffff" fontSize="16" textAnchor="middle" fontWeight="bold">
              128.0 <tspan fill="#00ffff" fontSize="11">KNM3/H</tspan>
            </text>
          </g>

          {/* PI1 */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'PI1', name: 'MR Vapor Pressure', unit: 'KGC2G', valDcs: 36.90, valAi: 35.15 })}>
            <text x="380" y="618" fill="#00ffff" fontSize="12" fontWeight="bold">PI1</text>
            <text x="380" y="638" fill={displayMode === 'AI_OPTIMIZED' ? '#34d399' : '#ffffff'} fontSize="15" fontWeight="bold">
              {fmt('PI1', 36.90, 35.15, 2).display} <tspan fill="#00ffff" fontSize="10">KGC2G</tspan>
            </text>
          </g>

          {/* 5C-1/5LI1 */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: '5C-1/5LI1', name: 'MR Suction Separator Level', unit: '%', valDcs: 7.0, valAi: 7.0 })}>
            <text x="380" y="660" fill="#00ffff" fontSize="12" fontWeight="bold">5C-1/5LI1</text>
            <text x="380" y="680" fill="#ffffff" fontSize="14" fontWeight="bold">7.0 <tspan fill="#00ffff" fontSize="10">%</tspan></text>
          </g>

          {/* TI47 */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'TI47', name: 'MR Vapor Temperature', unit: '°C', valDcs: -35.1, valAi: -35.1 })}>
            <text x="380" y="702" fill="#00ffff" fontSize="12" fontWeight="bold">TI47</text>
            <text x="380" y="722" fill="#ffffff" fontSize="15" fontWeight="bold">-35.1 <tspan fill="#00ffff" fontSize="10">°C</tspan></text>
          </g>

          {/* PDI25 */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'PDI25', name: 'MR Vapor Filter Differential Pressure', unit: 'KGC2', valDcs: 0.242, valAi: 0.242 })}>
            <text x="230" y="705" fill="#00ffff" fontSize="12" fontWeight="bold">PDI25</text>
            <text x="180" y="728" fill="#ffffff" fontSize="13">A  <tspan fontWeight="bold">0.242</tspan> <tspan fill="#00ffff" fontSize="10">KGC2</tspan></text>
            <text x="180" y="750" fill="#ffffff" fontSize="13">B  <tspan fontWeight="bold">0.240</tspan> <tspan fill="#00ffff" fontSize="10">KGC2</tspan></text>
          </g>

          {/* 6. LNG Rundown Tags: TIC1A/B, TI29, PI10 */}
          {/* TIC1A/B */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'TIC1A/B', name: 'LNG Rundown Temperature Controller', unit: '°C', valDcs: -151.2, valAi: lngTemp, limit: 'Target ≤ -150.0°C' })}>
            <text x="1560" y="285" fill="#00ffff" fontSize="13" fontWeight="bold">TIC1A/B</text>
            <text x="1550" y="310" fill={displayMode === 'AI_OPTIMIZED' ? '#34d399' : '#ffffff'} fontSize="18" fontWeight="bold">
              {fmt('TIC1A/B', -151.2, lngTemp, 1).display} <tspan fill="#00ffff" fontSize="12">°C</tspan>
            </text>
          </g>

          {/* TI29 */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'TI29', name: 'LNG Product Rundown Temperature', unit: '°C', valDcs: -153.6, valAi: -153.8 })}>
            <text x="1370" y="285" fill="#00ffff" fontSize="12" fontWeight="bold">TI29</text>
            <text x="1350" y="307" fill="#ffffff" fontSize="16" fontWeight="bold">-153.6 <tspan fill="#00ffff" fontSize="11">°C</tspan></text>
          </g>

          {/* PI10 */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'PI10', name: 'LNG Header Pressure', unit: 'KGC2G', valDcs: 39.77, valAi: 39.77 })}>
            <text x="1420" y="475" fill="#00ffff" fontSize="12" fontWeight="bold">PI10</text>
            <text x="1370" y="498" fill="#ffffff" fontSize="16" fontWeight="bold">39.77 <tspan fill="#00ffff" fontSize="11">KGC2G</tspan></text>
          </g>

          {/* FAL FI6B */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'FI6B', name: 'LNG Rundown Low Flow Alarm', unit: 'M3/H', valDcs: 0, valAi: 0 })}>
            <text x="1530" y="695" fill="#fbbf24" fontSize="13" fontWeight="bold">FAL <tspan fill="#00ffff">FI6B</tspan></text>
            <text x="1600" y="720" fill="#ffffff" fontSize="15" fontWeight="bold">0 <tspan fill="#00ffff" fontSize="11">M3/H</tspan></text>
          </g>

          {/* 7. Cold Bundle Intermediate Tags: TI30, PI8, TI21, TI27 */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'TI30', name: 'Cold Bundle Flash Temperature', unit: '°C', valDcs: -149.9, valAi: -149.9 })}>
            <text x="960" y="375" fill="#00ffff" fontSize="12" fontWeight="bold">TI30</text>
            <text x="940" y="398" fill="#ffffff" fontSize="15" fontWeight="bold">-149.9 <tspan fill="#00ffff" fontSize="10">°C</tspan></text>
          </g>
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'PI8', name: 'Cold Bundle Flash Pressure', unit: 'KGC2G', valDcs: 25.05, valAi: 25.05 })}>
            <text x="1080" y="375" fill="#00ffff" fontSize="12" fontWeight="bold">PI8</text>
            <text x="1060" y="398" fill="#ffffff" fontSize="15" fontWeight="bold">25.05</text>
            <text x="1060" y="414" fill="#00ffff" fontSize="10">KGC2G</text>
          </g>
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'TI21', name: 'Cold Bundle Tube Temperature 1', unit: '°C', valDcs: -128.5, valAi: -128.5 })}>
            <text x="1040" y="445" fill="#00ffff" fontSize="12" fontWeight="bold">TI21</text>
            <text x="1085" y="445" fill="#ffffff" fontSize="14" fontWeight="bold">-128.5 <tspan fill="#00ffff" fontSize="10">°C</tspan></text>
            <line x1="915" y1="442" x2="1035" y2="442" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="3 3" />
          </g>
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'TI27', name: 'Cold Bundle Tube Temperature 2', unit: '°C', valDcs: -126.3, valAi: -126.3 })}>
            <text x="1040" y="475" fill="#00ffff" fontSize="12" fontWeight="bold">TI27</text>
            <text x="1085" y="475" fill="#ffffff" fontSize="14" fontWeight="bold">-126.3 <tspan fill="#00ffff" fontSize="10">°C</tspan></text>
            <line x1="915" y1="472" x2="1035" y2="472" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="3 3" />
          </g>

          {/* 8. Warm Bundle Intermediate Tags: TI32, TI28, TI31, FIC2, PI7 */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'TI32', name: 'Warm MR Header Temperature', unit: '°C', valDcs: -132.6, valAi: -132.6 })}>
            <text x="1270" y="455" fill="#00ffff" fontSize="12" fontWeight="bold">TI32</text>
            <text x="1245" y="478" fill="#ffffff" fontSize="15" fontWeight="bold">-132.6 <tspan fill="#00ffff" fontSize="10">°C</tspan></text>
          </g>
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'TI28', name: 'Warm Bundle Tube Temperature 1', unit: '°C', valDcs: -129.5, valAi: -129.5 })}>
            <text x="1010" y="635" fill="#00ffff" fontSize="12" fontWeight="bold">TI28</text>
            <text x="980" y="658" fill="#ffffff" fontSize="15" fontWeight="bold">-129.5 <tspan fill="#00ffff" fontSize="10">°C</tspan></text>
            <line x1="954" y1="635" x2="1005" y2="635" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="3 3" />
          </g>
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'TI31', name: 'Warm Bundle Tube Temperature 2', unit: '°C', valDcs: -127.2, valAi: -127.2 })}>
            <text x="970" y="705" fill="#00ffff" fontSize="12" fontWeight="bold">TI31</text>
            <text x="1010" y="730" fill="#ffffff" fontSize="15" fontWeight="bold">-127.2 <tspan fill="#00ffff" fontSize="10">°C</tspan></text>
            <line x1="954" y1="705" x2="1005" y2="705" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="3 3" />
          </g>
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'FIC2', name: 'MCR Liquid Circulation Flow', unit: 'M3/H', valDcs: 875, valAi: 810 })}>
            <text x="1170" y="635" fill="#00ffff" fontSize="13" fontWeight="bold">FIC2</text>
            <text x="1190" y="660" fill={displayMode === 'AI_OPTIMIZED' ? '#34d399' : '#ffffff'} fontSize="18" fontWeight="bold">
              {fmt('FIC2', 875, 810, 0).display} <tspan fill="#00ffff" fontSize="11">M3/H</tspan>
            </text>
            <line x1="1265" y1="635" x2="1205" y2="635" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="3 3" markerEnd="url(#arrow-cyan)" />
          </g>
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'PI7', name: 'MCR Liquid Pressure', unit: 'KGC2G', valDcs: 31.96, valAi: 31.96 })}>
            <text x="1135" y="725" fill="#00ffff" fontSize="12" fontWeight="bold">PI7</text>
            <text x="1110" y="748" fill="#ffffff" fontSize="15" fontWeight="bold">31.96 <tspan fill="#00ffff" fontSize="10">KGC2G</tspan></text>
            <line x1="1100" y1="590" x2="1100" y2="710" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="3 3" />
          </g>
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'FI1_Right', name: 'Total Gas Flow Indication', unit: 'KNM3/H', valDcs: 128.0, valAi: 128.0 })}>
            <text x="1335" y="725" fill="#00ffff" fontSize="12" fontWeight="bold">FI1</text>
            <text x="1335" y="748" fill="#ffffff" fontSize="15" fontWeight="bold">128.0 <tspan fill="#00ffff" fontSize="10">KNM3/H</tspan></text>
            <line x1="1335" y1="710" x2="1335" y2="640" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="3 3" markerEnd="url(#arrow-cyan)" />
          </g>

          {/* 9. Bottom Sump & Return: TI49, TI48, PI9, TI8 */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'TI49', name: 'Warm Shell Bottom Temperature 1', unit: '°C', valDcs: -43.4, valAi: -43.4 })}>
            <text x="1000" y="760" fill="#00ffff" fontSize="12" fontWeight="bold">TI49: <tspan fill="#ffffff">-43.4 °C</tspan></text>
            <line x1="954" y1="756" x2="995" y2="756" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="3 3" />
          </g>
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'TI48', name: 'Warm Shell Bottom Temperature 2', unit: '°C', valDcs: -43.6, valAi: -43.6 })}>
            <text x="1000" y="785" fill="#00ffff" fontSize="12" fontWeight="bold">TI48: <tspan fill="#ffffff">-43.6 °C</tspan></text>
            <line x1="954" y1="781" x2="995" y2="781" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="3 3" />
          </g>

          {/* PI9 (Suction Pressure) */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'PI9', name: 'MCHE Bottom Outlet / Compressor Suction Pressure', unit: 'KGC2G', valDcs: 2.284, valAi: suctPress })}>
            <text x="1056" y="835" fill="#00ffff" fontSize="12" textAnchor="middle" fontWeight="bold">PI9</text>
            <text x="1056" y="855" fill={displayMode === 'AI_OPTIMIZED' ? '#34d399' : '#ffffff'} fontSize="15" textAnchor="middle" fontWeight="bold">
              {fmt('PI9', 2.284, suctPress, 3).display} <tspan fill="#00ffff" fontSize="10">KGC2G</tspan>
            </text>
          </g>

          {/* TI8 (TAL Suction Temperature to 4C-7 / 4K-2) */}
          <g style={{ cursor: 'pointer' }} onClick={() => handleTagClick({ tag: 'TI8', name: 'MCHE Bottom Outlet / Compressor Suction Temp', unit: '°C', valDcs: -44.8, valAi: suctTemp, limit: 'TAL Interlock ≥ -45.0°C' })}>
            <text x="1350" y="835" fill="#00ffff" fontSize="13" textAnchor="middle" fontWeight="bold">TI8</text>
            <text x="1350" y="855" fill={displayMode === 'AI_OPTIMIZED' ? '#34d399' : '#ffffff'} fontSize="16" textAnchor="middle" fontWeight="bold">
              {fmt('TI8', -44.8, suctTemp, 1).display} <tspan fill="#00ffff" fontSize="11">°C</tspan>
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
