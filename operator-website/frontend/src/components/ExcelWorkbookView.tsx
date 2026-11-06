import React, { useState } from 'react';
import type { ActualDcsState, DemoSnapshot, HistoricalPoint, OptimizeResponse, PredictResponse, ScenarioInput } from '../types';
import { calculateFlashDrum5C1, getEstimatedLngFlow } from '../utils/thermoFlash';
import { TabGrafik } from './TabGrafik';
import { TabPanduan } from './TabPanduan';

export type ExcelSheetTabId = 'sheet-01' | 'sheet-02' | 'sheet-03';

interface ExcelWorkbookViewProps {
  snapshot: DemoSnapshot;
  scenario: ScenarioInput;
  actualDcs: ActualDcsState;
  optimum: OptimizeResponse | null;
  onActualChange: (key: keyof ActualDcsState, value: number) => void;
  onOptimize: () => void;
  onNormalizeActual?: () => void;
  onNormalizeScenario?: () => void;
  prediction: PredictResponse | null;
  historicalPoints: HistoricalPoint[];
  onScenarioChange: (key: keyof ScenarioInput, value: number) => void;
  onReset: () => void;
  onCalculate?: () => void;
  loading: boolean;
  onExportCsv: () => void;
  modelReady: boolean;
  autoCalculate?: boolean;
}

/* ============================================================================
   HELPER: Reusable cell styles for the Excel-like grid
   ============================================================================ */
const B = '1px solid #d1d5db'; // cell border (Excel grey)
const BH = '1px solid #9ca3af'; // header border
const mono = "'Consolas', 'Courier New', monospace";
const cellPad = '5px 8px';

/* Flow conversion constants — single source: data/MASTER_DATASET_REBUILD_20261014/scripts/08_enrich_physics_features.py
   treated_gas_mass_flow_t_h = H3FI0004 [kNm3/h] x 0.760 ; H3FI0004 soft-sensor = 0.8136 x H1FI0009 */
const TREATED_GAS_T_PER_KNM3 = 0.760;
const TREATED_TO_FEED_RATIO = 0.8136;

const hdrStyle: React.CSSProperties = {
  backgroundColor: '#1e3a5f',
  color: '#ffffff',
  fontWeight: 700,
  fontSize: '0.73rem',
  textAlign: 'center',
  padding: '7px 8px',
  border: BH,
  whiteSpace: 'nowrap',
};

const sectionHdrStyle = (bg: string): React.CSSProperties => ({
  backgroundColor: bg,
  color: '#ffffff',
  fontWeight: 700,
  fontSize: '0.78rem',
  padding: '5px 12px',
  letterSpacing: '0.03em',
  border: B,
});

const tagCell: React.CSSProperties = {
  fontFamily: mono,
  fontWeight: 600,
  color: '#0369a1',
  fontSize: '0.8rem',
  padding: cellPad,
  border: B,
  whiteSpace: 'nowrap',
};

const nameCell: React.CSSProperties = {
  fontWeight: 500,
  fontSize: '0.8rem',
  padding: cellPad,
  border: B,
};

const valCell: React.CSSProperties = {
  fontFamily: mono,
  fontWeight: 600,
  textAlign: 'right',
  fontSize: '0.82rem',
  padding: cellPad,
  border: B,
};

const unitCell: React.CSSProperties = {
  textAlign: 'center',
  color: '#6b7280',
  fontSize: '0.78rem',
  padding: cellPad,
  border: B,
};

const noteCell: React.CSSProperties = {
  color: '#6b7280',
  fontSize: '0.74rem',
  padding: cellPad,
  border: B,
};

const inputStyle: React.CSSProperties = {
  width: '100%',
  border: '1.5px solid #86efac',
  borderRadius: '3px',
  backgroundColor: '#ffffff',
  padding: '4px 6px',
  textAlign: 'right',
  fontFamily: mono,
  fontWeight: 700,
  color: '#15803d',
  outline: 'none',
  fontSize: '0.85rem',
};

/* Actual DCS input (operator types current PV / GC result) — blue to distinguish from target */
const actualInputStyle: React.CSSProperties = {
  ...inputStyle,
  border: '1.5px solid #93c5fd',
  color: '#1d4ed8',
};

const COMP_KEYS = ['comp_N2_molpct', 'comp_C1_molpct', 'comp_C2_molpct', 'comp_C2H4_molpct', 'comp_C3_molpct'] as const;
type CompKey = typeof COMP_KEYS[number];

const fmtDelta = (d: number, digits: number): string => `${d > 0 ? '+' : ''}${d.toFixed(digits)}`;

/* ============================================================================
   MAIN COMPONENT
   ============================================================================ */
export const ExcelWorkbookView: React.FC<ExcelWorkbookViewProps> = ({
  snapshot,
  scenario,
  actualDcs,
  optimum,
  onActualChange,
  onOptimize,
  onNormalizeActual,
  onNormalizeScenario,
  prediction,
  historicalPoints,
  onScenarioChange,
  onReset,
  loading,
  onExportCsv,
  modelReady,
}) => {
  const [activeSheetTab, setActiveSheetTab] = useState<ExcelSheetTabId>('sheet-01');
  const [transitionHours, setTransitionHours] = useState<number>(scenario.transition_hours || 2.0);

  /* Derived values — baseline = same surrogate evaluated at the operator's Aktual DCS state */
  const snapshotPower = snapshot.baseline_model_output?.total_shaft_power_mw ?? 84.48;
  const baselinePower = prediction?.baseline_power_mw ?? prediction?.actual_power_mw ?? snapshotPower;
  const currentPower = prediction ? prediction.prediction.total_shaft_power_mw : baselinePower;
  const deltaPower = prediction?.prediction?.delta_power_mw ?? (currentPower - baselinePower);
  const deltaPct = prediction?.prediction?.delta_power_pct ?? (baselinePower > 0 ? (deltaPower / baselinePower) * 100 : 0);

  // LNG Production Rundown (H5FI6A)
  // Authoritative mass balance: PR-EOS 5C-1 Flash Drum thermodynamic phase split (~94.53 wt% liquid yield)
  // LNG strictly follows feed gas entering MCHE (H3FI0004)
  const actualLngFlow = actualDcs.lng_flow_t_h ?? getEstimatedLngFlow(actualDcs.feed_flow_t_h);
  const scenarioFlash = calculateFlashDrum5C1(scenario.feed_flow_t_h);
  const scenarioLngFlow = prediction?.flash_drum_5c1?.lng_liquid_flow_t_h 
    ?? scenario.lng_flow_t_h 
    ?? scenarioFlash.lngLiquidFlowTH;

  // SEC LNG: kWh per tonne of LNG (Basis: Meter Fiskal H5FI6A)
  const secLng = prediction?.prediction.sec_lng_kwh_per_t ?? (currentPower * 1000 / Math.max(scenarioLngFlow, 1));
  const baselineSecLng = prediction?.baseline_sec_lng ?? (baselinePower * 1000 / Math.max(scenarioLngFlow, 1));
  const deltaSecLng = prediction?.prediction?.delta_sec_kwh_per_t ?? (secLng - baselineSecLng);

  // Specific Shaft Power per Treated Feed: kWh per tonne of treated feed (H3FI0004)
  const specPowerFeed = prediction?.prediction.specific_shaft_power_feed_kwh_per_t ?? (currentPower * 1000 / Math.max(scenario.feed_flow_t_h, 1));
  const baselineSpecPowerFeed = baselinePower * 1000 / Math.max(actualDcs.feed_flow_t_h, 1);

  const compSum = COMP_KEYS.reduce((acc, k) => acc + (scenario[k] as number), 0);
  const actualCompSum = COMP_KEYS.reduce((acc, k) => acc + actualDcs[k], 0);
  const optimumStale = optimum !== null && Math.abs(optimum.feed_t_h - actualDcs.feed_flow_t_h) > 0.05;

  const makeup = prediction?.makeup_advisory;
  const feat = prediction?.features_computed ?? {};
  const pred = prediction?.prediction;
  const domain = prediction?.domain_check;
  const hasViolations = Boolean(prediction?.safety_check.violations && prediction.safety_check.violations.length > 0);

  /* Snapshot DCS values for read-only display */
  const sv = snapshot.values;
  const dcsVal = (key: string): string => {
    const v = sv[key];
    return v ? String(v.value) : '—';
  };

  /* ========================================================================= */
  return (
    <div style={{
      width: '100%',
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column',
      backgroundColor: '#0f172a',
      fontFamily: "'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif",
      color: '#f8fafc',
    }}>
      {/* ==================================================================== */}
      {/* HEADER BAR (STICKY AT TOP) */}
      {/* ==================================================================== */}
      <div style={{
        position: 'sticky',
        top: 0,
        zIndex: 100,
        padding: '8px 18px',
        backgroundColor: '#111827',
        borderBottom: '1px solid #1f2937',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '10px',
        userSelect: 'none',
        boxShadow: '0 2px 8px rgba(0,0,0,0.4)',
      }}>
        {/* Left: Brand + Title */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{
            backgroundColor: '#107c41',
            color: '#fff',
            fontWeight: 800,
            padding: '4px 10px',
            borderRadius: '4px',
            fontSize: '0.82rem',
            letterSpacing: '0.03em',
          }}>BADAK LNG</div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: '0.92rem', fontWeight: 700 }}>
                Plant-5 Train H — C3MR Liquefaction & Make-Up Advisory
              </span>
              <span style={{
                fontSize: '0.65rem',
                backgroundColor: '#1e293b',
                color: '#38bdf8',
                padding: '2px 8px',
                borderRadius: '3px',
                fontWeight: 600,
              }}>ADVISORY — TIDAK MENULIS KE DCS</span>
            </div>
            <div style={{ fontSize: '0.68rem', color: '#64748b', marginTop: '1px' }}>
              Dukungan Keputusan Operator — Siklus Refrigerasi Campuran MCR & C3
            </div>
          </div>
        </div>

        {/* Right: Controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          {/* Live Status */}
          <div style={{
            backgroundColor: '#1e293b',
            padding: '4px 10px',
            borderRadius: '4px',
            border: '1px solid #334155',
            fontSize: '0.72rem',
            display: 'flex',
            alignItems: 'center',
            gap: '5px',
          }}>
            <span style={{
              width: '7px',
              height: '7px',
              borderRadius: '50%',
              backgroundColor: loading ? '#f59e0b' : '#10b981',
              boxShadow: loading ? '0 0 5px #f59e0b' : '0 0 5px #10b981',
            }} />
            <span style={{ color: loading ? '#fcd34d' : '#86efac', fontWeight: 600 }}>
              {loading ? 'Menghitung...' : 'Real-time'}
            </span>
          </div>

          {/* Model Badge */}
          <div style={{
            fontSize: '0.72rem',
            color: '#94a3b8',
            backgroundColor: '#1e293b',
            padding: '4px 10px',
            borderRadius: '4px',
            border: '1px solid #334155',
          }}>
            Model: <span style={{ color: modelReady ? '#86efac' : '#fcd34d', fontWeight: 600 }}>
              {modelReady ? 'PhysicsResidual (R²=0.836)' : 'Memuat...'}
            </span>
          </div>

          {/* Transition Duration */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '5px', fontSize: '0.72rem', color: '#cbd5e1' }}>
            <span>Durasi:</span>
            <select
              value={transitionHours}
              onChange={(e) => {
                const val = parseFloat(e.target.value);
                setTransitionHours(val);
                onScenarioChange('transition_hours', val);
              }}
              style={{
                backgroundColor: '#1e293b',
                color: '#f8fafc',
                border: '1px solid #475569',
                borderRadius: '4px',
                padding: '4px 6px',
                fontSize: '0.72rem',
                fontWeight: 600,
                outline: 'none',
                cursor: 'pointer',
              }}
            >
              <option value={1.0}>1.0 Jam</option>
              <option value={2.0}>2.0 Jam (SOP)</option>
              <option value={4.0}>4.0 Jam</option>
            </select>
          </div>

          {/* AI recommendation */}
          <button
            onClick={onOptimize}
            disabled={loading}
            style={{
              backgroundColor: optimumStale ? '#b45309' : '#7c3aed',
              color: '#fff',
              border: 'none',
              padding: '5px 14px',
              borderRadius: '4px',
              fontSize: '0.75rem',
              fontWeight: 700,
              cursor: loading ? 'wait' : 'pointer',
              boxShadow: '0 1px 3px rgba(0,0,0,0.3)',
            }}
            title="Cari laju alir MCR & komposisi MCR optimum untuk feed Aktual DCS (SLSQP 7-kuantil, interpolasi ILR)"
          >{optimumStale ? '⟳ Hitung Ulang Rekomendasi AI' : '✨ Hitung Rekomendasi AI'}</button>

          {/* Reset */}
          <button
            onClick={onReset}
            style={{
              backgroundColor: '#334155',
              color: '#f8fafc',
              border: '1px solid #475569',
              padding: '5px 12px',
              borderRadius: '4px',
              fontSize: '0.75rem',
              fontWeight: 600,
              cursor: 'pointer',
            }}
            title="Kembalikan Aktual DCS & Target ke snapshot DCS"
          >⟲ Reset</button>

          {/* Export */}
          <button
            onClick={onExportCsv}
            style={{
              backgroundColor: '#107c41',
              color: '#fff',
              border: 'none',
              padding: '5px 12px',
              borderRadius: '4px',
              fontSize: '0.75rem',
              fontWeight: 700,
              cursor: 'pointer',
              boxShadow: '0 1px 3px rgba(0,0,0,0.3)',
            }}
            title="Unduh seluruh data skenario & rekomendasi make-up ke file CSV/Excel"
          >⬇ Excel/CSV</button>
        </div>
      </div>

      {/* ==================================================================== */}
      {/* SHEET TABS (STICKY BELOW HEADER) */}
      {/* ==================================================================== */}
      <div style={{
        position: 'sticky',
        top: '49px',
        zIndex: 90,
        display: 'flex',
        alignItems: 'center',
        backgroundColor: '#1e293b',
        borderBottom: '2px solid #107c41',
        padding: '0 18px',
        gap: '3px',
        userSelect: 'none',
        boxShadow: '0 2px 6px rgba(0,0,0,0.3)',
      }}>
        {[
          { id: 'sheet-01' as ExcelSheetTabId, label: 'Lembar 1: Skenario & Rekomendasi Make-Up', dot: hasViolations },
          { id: 'sheet-02' as ExcelSheetTabId, label: 'Lembar 2: Grafik Kinerja & Profil MCHE', dot: false },
          { id: 'sheet-03' as ExcelSheetTabId, label: 'Lembar 3: Panduan Operasi & Safety Interlock', dot: false },
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveSheetTab(tab.id)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '8px 18px',
              backgroundColor: activeSheetTab === tab.id ? '#ffffff' : 'transparent',
              color: activeSheetTab === tab.id ? '#107c41' : '#94a3b8',
              border: 'none',
              borderRadius: '5px 5px 0 0',
              fontWeight: 700,
              fontSize: '0.8rem',
              cursor: 'pointer',
              boxShadow: activeSheetTab === tab.id ? '0 -2px 5px rgba(0,0,0,0.2)' : 'none',
              transition: 'all 0.12s ease',
            }}
          >
            {tab.label}
            {tab.dot && (
              <span style={{ width: '7px', height: '7px', borderRadius: '50%', backgroundColor: '#ef4444' }} />
            )}
          </button>
        ))}
      </div>

      {/* ==================================================================== */}
      {/* SHEET 1: SPREADSHEET TABLE */}
      {/* ==================================================================== */}
      {activeSheetTab === 'sheet-01' && (
        <div style={{
          flex: 1,
          backgroundColor: '#f1f5f9',
          color: '#1e293b',
          padding: '16px 20px 40px 20px',
          display: 'flex',
          flexDirection: 'column',
          gap: '12px',
        }}>
          {/* KPI Summary Cards */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(215px, 1fr))',
            gap: '10px',
          }}>
            {/* Card: Total Power */}
            <div style={{ backgroundColor: '#fff', borderRadius: '5px', padding: '10px 14px', border: '1px solid #e2e8f0', boxShadow: '0 1px 2px rgba(0,0,0,0.04)' }}>
              <div style={{ fontSize: '0.68rem', color: '#64748b', fontWeight: 600, textTransform: 'uppercase' }}>Total Daya Poros C3MR</div>
              <div style={{ fontSize: '1.3rem', fontWeight: 800, color: '#107c41', marginTop: '3px' }}>
                {currentPower.toFixed(2)} <span style={{ fontSize: '0.85rem', fontWeight: 600 }}>MW</span>
              </div>
              <div style={{ fontSize: '0.74rem', marginTop: '3px', fontWeight: 600, color: deltaPower <= 0 ? '#107c41' : '#b45309' }}>
                {deltaPower <= 0 ? `Hemat ${Math.abs(deltaPower).toFixed(2)} MW (${Math.abs(deltaPct).toFixed(1)}%)` : `Naik +${deltaPower.toFixed(2)} MW`} vs Aktual DCS
              </div>
            </div>

            {/* Card: Specific Energy Consumption SEC LNG (H5FI6A) */}
            <div style={{ backgroundColor: '#fff', borderRadius: '5px', padding: '10px 14px', border: '1px solid #e2e8f0', boxShadow: '0 1px 2px rgba(0,0,0,0.04)' }}>
              <div style={{ fontSize: '0.68rem', color: '#107c41', fontWeight: 700, textTransform: 'uppercase' }}>
                SEC LNG (Spesifik per Ton LNG — H5FI6A)
              </div>
              <div style={{ fontSize: '1.3rem', fontWeight: 800, color: '#0f172a', marginTop: '3px' }}>
                {secLng.toFixed(1)} <span style={{ fontSize: '0.85rem', fontWeight: 600 }}>kWh/t LNG</span>
              </div>
              <div style={{ fontSize: '0.72rem', color: '#64748b', marginTop: '3px' }}>
                Aktual DCS: {baselineSecLng.toFixed(1)} kWh/t LNG · <span style={{ color: deltaSecLng <= 0 ? '#107c41' : '#b45309', fontWeight: 600 }}>
                  {deltaSecLng <= 0 ? `Hemat ${Math.abs(deltaSecLng).toFixed(1)} kWh/t` : `+${deltaSecLng.toFixed(1)} kWh/t`}
                </span>
              </div>
              <div style={{ fontSize: '0.68rem', color: '#94a3b8', marginTop: '2px' }}>
                Produksi LNG H5FI6A: {scenarioLngFlow.toFixed(1)} t/h (Feed: {specPowerFeed.toFixed(1)} kWh/t feed)
              </div>
            </div>

            {/* Card: Make-Up */}
            <div style={{ backgroundColor: '#fff', borderRadius: '5px', padding: '10px 14px', border: '1px solid #e2e8f0', boxShadow: '0 1px 2px rgba(0,0,0,0.04)' }}>
              <div style={{ fontSize: '0.68rem', color: '#64748b', fontWeight: 600, textTransform: 'uppercase' }}>Injeksi Make-Up Hidrokarbon</div>
              <div style={{ fontSize: '1.3rem', fontWeight: 800, color: '#c2410c', marginTop: '3px' }}>
                {makeup ? `${makeup.total_makeup_flow_nm3_h.toFixed(1)}` : '0.0'} <span style={{ fontSize: '0.85rem', fontWeight: 600 }}>Nm³/h</span>
              </div>
              <div style={{ fontSize: '0.74rem', color: '#c2410c', marginTop: '3px', fontWeight: 600 }}>
                {makeup ? `${makeup.total_makeup_flow_kg_h.toFixed(1)} kg/h · ${transitionHours.toFixed(1)} jam` : 'Tidak perlu injeksi'}
              </div>
            </div>

            {/* Card: Bounded Safety Checks */}
            <div style={{ backgroundColor: '#fff', borderRadius: '5px', padding: '10px 14px', border: '1px solid #e2e8f0', boxShadow: '0 1px 2px rgba(0,0,0,0.04)' }}>
              <div style={{ fontSize: '0.68rem', color: '#64748b', fontWeight: 600, textTransform: 'uppercase' }}>Status Pemeriksaan Kendala</div>
              <div style={{
                fontSize: '0.92rem',
                fontWeight: 800,
                color: (domain?.in_domain ?? true) && scenario.mcr_flow_t_h >= 480.0 ? '#107c41' : '#dc2626',
                marginTop: '4px',
                display: 'flex',
                alignItems: 'center',
                gap: '5px',
              }}>
                {(domain?.in_domain ?? true) && scenario.mcr_flow_t_h >= 480.0 ? '✓ Kendala Terperiksa Terpenuhi' : '⚠ Perlu Ditinjau'}
              </div>
              <div style={{ fontSize: '0.71rem', color: '#64748b', marginTop: '3px' }}>
                D<sub>M</sub>: {domain ? domain.mahalanobis_distance.toFixed(2) : '—'} (≤3.08) · Floor ≥480 t/h · Peta dinamis: Belum dievaluasi
              </div>
            </div>
          </div>

          {/* ============================================================= */}
          {/* WORKFLOW / AI RECOMMENDATION STATUS STRIP */}
          {/* ============================================================= */}
          <div style={{
            backgroundColor: optimum ? (optimumStale ? '#fffbeb' : '#f5f3ff') : '#eff6ff',
            border: `1px solid ${optimum ? (optimumStale ? '#fcd34d' : '#c4b5fd') : '#bfdbfe'}`,
            borderRadius: '5px',
            padding: '8px 14px',
            fontSize: '0.78rem',
            color: '#1e293b',
            lineHeight: 1.5,
          }}>
            {!optimum && (
              <span>
                <strong>Langkah operator:</strong> (1) Isi kolom <strong style={{ color: '#1d4ed8' }}>Aktual DCS</strong> dengan PV DCS saat ini
                (H3FI0004, H4FI011B) dan hasil GC MCR shift terakhir → (2) klik <strong style={{ color: '#7c3aed' }}>✨ Hitung Rekomendasi AI</strong> →
                (3) baca laju alir MCR, komposisi target, dan set point injeksi make-up H4FIC005/006/007 di Seksi D.
              </span>
            )}
            {optimum && (
              <span>
                <strong style={{ color: optimumStale ? '#b45309' : '#6d28d9' }}>
                  {optimumStale ? '⚠ Rekomendasi kedaluwarsa' : 'Rekomendasi AI aktif'}
                </strong>
                {' '}untuk feed {optimum.feed_t_h.toFixed(1)} t/h
                {optimumStale && ` (feed aktual sekarang ${actualDcs.feed_flow_t_h.toFixed(1)} t/h — klik hitung ulang)`}
                {' · '}D<sub>M</sub> = {optimum.mahalanobis_distance.toFixed(3)} (≤ 3.0802)
                {' · '}Estimasi H4TI004B = {optimum.expected_suction_temp_c.toFixed(1)} °C ({optimum.suction_tal_ok ? '≥ −45.0 °C AMAN' : '⚠ TAL'})
                {optimum.antisurge_floor_applied && ' · Laju MCR dijepit ke batas anti-surge 480.0 t/h'}
                {optimum.envelope_shrink_applied && ' · Komposisi ditarik ke batas elipsoid D_M'}
                {optimum.extrapolated && ` · Feed di luar rentang optimasi ${optimum.feed_span_t_h[0]}–${optimum.feed_span_t_h[1]} t/h: dipakai titik ujung terdekat`}
                <div style={{ fontSize: '0.72rem', color: '#475569', marginTop: '3px', fontFamily: mono }}>
                  Mesin solver: <strong>{optimum.source}</strong> · Batas: T_suct ≥ −45.0 °C, D_M ≤ 3.0802, superheat PR-EOS ≥ 3.0 °C, MCR ≥ 480 t/h.
                </div>
              </span>
            )}
          </div>

          {/* ============================================================= */}
          {/* MAIN SPREADSHEET TABLE */}
          {/* ============================================================= */}
          <div style={{
            backgroundColor: '#ffffff',
            borderRadius: '5px',
            border: '1px solid #cbd5e1',
            overflow: 'hidden',
            boxShadow: '0 1px 3px rgba(0,0,0,0.06)',
          }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.82rem' }}>
              <thead>
                <tr>
                  <th style={{ ...hdrStyle, width: '115px' }}>Tag DCS</th>
                  <th style={{ ...hdrStyle, minWidth: '240px', textAlign: 'left' }}>Nama Parameter</th>
                  <th style={{ ...hdrStyle, width: '120px', textAlign: 'right', backgroundColor: '#1d4ed8' }}>Aktual DCS<br /><span style={{ fontWeight: 400, fontSize: '0.65rem' }}>(input operator)</span></th>
                  <th style={{ ...hdrStyle, width: '140px', textAlign: 'right', backgroundColor: '#107c41' }}>Rekomendasi AI / Target</th>
                  <th style={{ ...hdrStyle, width: '70px' }}>Satuan</th>
                  <th style={{ ...hdrStyle, width: '160px', textAlign: 'left' }}>Status</th>
                  <th style={{ ...hdrStyle, minWidth: '220px', textAlign: 'left' }}>Batas Operasi & Keterangan</th>
                </tr>
              </thead>
              <tbody>
                {/* ============================================================= */}
                {/* SEKSI A — INPUT SKENARIO (WHAT-IF, DAPAT DIEDIT) */}
                {/* ============================================================= */}
                <tr><td colSpan={7} style={sectionHdrStyle('#0d9488')}>
                  ▎ SEKSI A — AKTUAL DCS (DIISI OPERATOR) vs REKOMENDASI AI (LAJU MCR & KOMPOSISI MCR)
                </td></tr>

                {/* A1: Treated Gas Flow (model feature key: feed_flow_t_h) — disturbance, target follows actual */}
                <tr style={{ backgroundColor: '#fff' }}>
                  <td style={tagCell}>H3FI0004</td>
                  <td style={{ ...nameCell, fontWeight: 600 }}>Laju Alir Treated Gas 3C-2 → MCHE 5E-1 (massa)</td>
                  <td style={{ ...valCell, backgroundColor: '#eff6ff', padding: '3px 5px' }}>
                    <input type="number" step="1" value={actualDcs.feed_flow_t_h}
                      onChange={(e) => onActualChange('feed_flow_t_h', parseFloat(e.target.value) || 0)}
                      style={actualInputStyle} />
                  </td>
                  <td style={{ ...valCell, color: '#334155' }}>{scenario.feed_flow_t_h.toFixed(1)}</td>
                  <td style={unitCell}>t/h</td>
                  <td style={{ ...nameCell, color: '#1d4ed8', fontWeight: 600, fontSize: '0.76rem' }}>GANGGUAN (ikut aktual)</td>
                  <td style={noteCell}>= H3FI0004 [kNm³/h] × 0.760; feed bukan variabel keputusan; rentang data latih 130 – 340 t/h</td>
                </tr>

                {/* A1b: LNG Rundown Flow (H5FI6A) */}
                <tr style={{ backgroundColor: '#f0fdf4' }}>
                  <td style={{ ...tagCell, color: '#107c41', fontWeight: 700 }}>H5FI6A</td>
                  <td style={{ ...nameCell, fontWeight: 700, color: '#107c41' }}>
                    Laju Alir Produksi LNG Rundown ke Tangki (H5FI6A)
                  </td>
                  <td style={{ ...valCell, fontWeight: 700, color: '#0f172a' }}>
                    {actualLngFlow.toFixed(1)}
                  </td>
                  <td style={{ ...valCell, fontWeight: 800, color: '#107c41', backgroundColor: '#dcfce7' }}>
                    {scenarioLngFlow.toFixed(1)}
                  </td>
                  <td style={{ ...unitCell, fontWeight: 700, color: '#107c41' }}>t/h LNG</td>
                  <td style={{ ...nameCell, color: '#107c41', fontWeight: 700, fontSize: '0.76rem' }}>
                    OTOMATIS (PR-EOS 5C-1 Flash)
                  </td>
                  <td style={noteCell}>
                    Hasil hilir MCHE dihitung via VLE PR-EOS 5C-1 Flash Drum (~94.53 wt% pada -152.5°C, 0.30 kg/cm²G). Mengikuti laju umpan gas; denominator resmi SEC LNG.
                  </td>
                </tr>

                {/* A2: MCR Flow */}
                <tr style={{ backgroundColor: '#fafafa' }}>
                  <td style={tagCell}>H4FI011B</td>
                  <td style={{ ...nameCell, fontWeight: 600 }}>Laju Alir Sirkulasi MCR (massa, discharge 4K-3)</td>
                  <td style={{ ...valCell, backgroundColor: '#eff6ff', padding: '3px 5px' }}>
                    <input type="number" step="1" value={actualDcs.mcr_flow_t_h}
                      onChange={(e) => onActualChange('mcr_flow_t_h', parseFloat(e.target.value) || 0)}
                      style={actualInputStyle} />
                  </td>
                  <td style={{ ...valCell, backgroundColor: '#f0fdf4', padding: '3px 5px' }}>
                    <input type="number" step="1" value={scenario.mcr_flow_t_h}
                      onChange={(e) => onScenarioChange('mcr_flow_t_h', parseFloat(e.target.value) || 0)}
                      style={inputStyle} />
                  </td>
                  <td style={unitCell}>t/h</td>
                  <td style={{
                    ...nameCell,
                    fontWeight: 600,
                    color: scenario.mcr_flow_t_h >= 480.0 ? '#107c41' : '#dc2626',
                  }}>
                    {scenario.mcr_flow_t_h >= 480.0 ? '≥ 480.0 (AMAN)' : '⚠ < 480 SURGE'}
                    <span style={{ color: '#475569', fontWeight: 500 }}> Δ {fmtDelta(scenario.mcr_flow_t_h - actualDcs.mcr_flow_t_h, 1)}</span>
                  </td>
                  <td style={noteCell}>= H4FI011B [k m³/h] × 36.8 kg/m³; Safe Floor ≥ 480.0 t/h (4UV-53)</td>
                </tr>

                {/* A3-A7: MCR Composition */}
                {[
                  { tag: 'comp_4C-8_N2', name: 'MCR Nitrogen (N₂)', key: 'comp_N2_molpct' as CompKey, note: 'Mengontrol suhu cold bundle & TAL; 0.5–8.5%' },
                  { tag: 'comp_4C-8_C1', name: 'MCR Metana (CH₄)', key: 'comp_C1_molpct' as CompKey, note: 'Subcooling LNG rundown; 35–55%' },
                  { tag: 'comp_4C-8_C2', name: 'MCR Etana (C₂H₆)', key: 'comp_C2_molpct' as CompKey, note: 'Pendinginan bundle tengah; 30–55%' },
                  { tag: 'comp_4C-8_C2H4', name: 'MCR Etilena (C₂H₄)', key: 'comp_C2H4_molpct' as CompKey, note: 'Modifikasi kurva transisi; 0–45%' },
                  { tag: 'comp_4C-8_C3', name: 'MCR Propana (C₃H₈)', key: 'comp_C3_molpct' as CompKey, note: 'Pendinginan warm end; 0–12%' },
                ].map((row, i) => {
                  const d = (scenario[row.key] as number) - actualDcs[row.key];
                  return (
                    <tr key={row.tag} style={{ backgroundColor: i % 2 === 0 ? '#fff' : '#fafafa' }}>
                      <td style={{ ...tagCell, color: '#64748b' }}>{row.tag}</td>
                      <td style={nameCell}>{row.name}</td>
                      <td style={{ ...valCell, backgroundColor: '#eff6ff', padding: '3px 5px' }}>
                        <input type="number" step="0.01" value={actualDcs[row.key]}
                          onChange={(e) => onActualChange(row.key, parseFloat(e.target.value) || 0)}
                          style={actualInputStyle} />
                      </td>
                      <td style={{ ...valCell, backgroundColor: '#f0fdf4', padding: '3px 5px' }}>
                        <input type="number" step="0.01"
                          value={scenario[row.key] as number}
                          onChange={(e) => onScenarioChange(row.key, parseFloat(e.target.value) || 0)}
                          style={inputStyle} />
                      </td>
                      <td style={unitCell}>mol%</td>
                      <td style={{ ...nameCell, fontSize: '0.76rem', fontWeight: 600, color: Math.abs(d) < 0.02 ? '#64748b' : (d > 0 ? '#c2410c' : '#1d4ed8') }}>
                        Δ {fmtDelta(d, 2)} {Math.abs(d) < 0.02 ? '(tetap)' : (d > 0 ? '(naikkan)' : '(turunkan)')}
                      </td>
                      <td style={noteCell}>{row.note}</td>
                    </tr>
                  );
                })}

                {/* A8: Composition Sum */}
                <tr style={{ backgroundColor: '#f8fafc' }}>
                  <td style={{ ...tagCell, color: '#475569', fontWeight: 700 }}>TOTAL_COMP</td>
                  <td style={{ ...nameCell, fontWeight: 700 }}>Total Penjumlahan Komposisi MCR</td>
                  <td style={{ ...valCell, color: Math.abs(actualCompSum - 100.0) < 0.05 ? '#1d4ed8' : '#b45309' }}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: '6px' }}>
                      <span style={{ fontWeight: 700 }}>{actualCompSum.toFixed(2)}</span>
                      {Math.abs(actualCompSum - 100.0) >= 0.01 && onNormalizeActual && (
                        <button
                          type="button"
                          onClick={onNormalizeActual}
                          title="Normalisasi komposisi aktual DCS ke 100.00% (distribusi residu ke C1)"
                          style={{
                            padding: '1px 5px',
                            fontSize: '0.68rem',
                            fontWeight: 700,
                            borderRadius: '3px',
                            border: '1px solid #93c5fd',
                            backgroundColor: '#eff6ff',
                            color: '#1d4ed8',
                            cursor: 'pointer',
                          }}
                        >
                          ⚡ 100%
                        </button>
                      )}
                    </div>
                  </td>
                  <td style={{
                    ...valCell,
                    fontWeight: 700,
                    color: Math.abs(compSum - 100.0) < 0.05 ? '#107c41' : '#b45309',
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: '6px' }}>
                      <span style={{ fontWeight: 700 }}>{compSum.toFixed(2)}</span>
                      {Math.abs(compSum - 100.0) >= 0.01 && onNormalizeScenario && (
                        <button
                          type="button"
                          onClick={onNormalizeScenario}
                          title="Normalisasi komposisi target ke 100.00% (distribusi residu ke C1)"
                          style={{
                            padding: '1px 5px',
                            fontSize: '0.68rem',
                            fontWeight: 700,
                            borderRadius: '3px',
                            border: '1px solid #86efac',
                            backgroundColor: '#f0fdf4',
                            color: '#15803d',
                            cursor: 'pointer',
                          }}
                        >
                          ⚡ 100%
                        </button>
                      )}
                    </div>
                  </td>
                  <td style={unitCell}>mol%</td>
                  <td style={{
                    ...nameCell,
                    color: Math.abs(compSum - 100.0) < 0.05 ? '#107c41' : '#b45309',
                    fontWeight: 600,
                  }}>
                    {Math.abs(compSum - 100.0) < 0.05 ? '✓ 100.00% SEIMBANG' : 'PERLU NORMALISASI'}
                  </td>
                  <td style={noteCell}>Wajib presisi 100.00 mol% (Hukum Kekekalan Massa & Simpleks S⁵)</td>
                </tr>

                {/* ============================================================= */}
                {/* SEKSI B — KONDISI PROSES & KOMPRESOR (DCS PVs, READ-ONLY) */}
                {/* ============================================================= */}
                <tr><td colSpan={7} style={sectionHdrStyle('#1e40af')}>
                  ▎ SEKSI B — KONDISI PROSES & KOMPRESOR 4K-2/4K-3 (DCS — READ-ONLY)
                </td></tr>

                {/* B0a: Treated gas volumetric (inverse of stage-08 density factor 0.760 t/kNm3) */}
                <tr style={{ backgroundColor: '#fff' }}>
                  <td style={{ ...tagCell, color: '#64748b' }}>H3FI0004</td>
                  <td style={nameCell}>Treated Gas 3C-2 → MCHE 5E-1 (volumetrik)</td>
                  <td style={valCell}>{(actualDcs.feed_flow_t_h / TREATED_GAS_T_PER_KNM3).toFixed(1)}</td>
                  <td style={{ ...valCell, color: '#334155' }}>{(scenario.feed_flow_t_h / TREATED_GAS_T_PER_KNM3).toFixed(1)}</td>
                  <td style={unitCell}>kNm³/h</td>
                  <td style={{ ...nameCell, color: '#64748b', fontSize: '0.76rem' }}>DIHITUNG</td>
                  <td style={noteCell}>= massa treated gas / 0.760 t/kNm³ (stage 08)</td>
                </tr>

                {/* B0b: Natural feed gas inlet (stage-08 mass-balance soft-sensor H3FI0004 = 0.8136 × H1FI0009) */}
                <tr style={{ backgroundColor: '#fafafa' }}>
                  <td style={{ ...tagCell, color: '#64748b' }}>H1FI0009</td>
                  <td style={nameCell}>Umpan Gas Alam F/G → 1C-1 (estimasi)</td>
                  <td style={valCell}>{(actualDcs.feed_flow_t_h / TREATED_GAS_T_PER_KNM3 / TREATED_TO_FEED_RATIO).toFixed(1)}</td>
                  <td style={{ ...valCell, color: '#334155' }}>{(scenario.feed_flow_t_h / TREATED_GAS_T_PER_KNM3 / TREATED_TO_FEED_RATIO).toFixed(1)}</td>
                  <td style={unitCell}>kNm³/h</td>
                  <td style={{ ...nameCell, color: '#b45309', fontSize: '0.76rem' }}>SOFT-SENSOR</td>
                  <td style={noteCell}>= H3FI0004 / 0.8136 (neraca massa stage 08); ganti dengan PV DCS bila tersedia</td>
                </tr>

                {/* B1: 4K-2 LP Suction Pressure */}
                <tr style={{ backgroundColor: '#fff' }}>
                  <td style={{ ...tagCell, color: '#64748b' }}>H4PI014B</td>
                  <td style={nameCell}>Tekanan Suction 4K-2 (LP MCR)</td>
                  <td style={valCell}>{dcsVal('p_4k2_suct_kgcm2a')}</td>
                  <td style={{ ...valCell, color: '#334155' }}>{dcsVal('p_4k2_suct_kgcm2a')}</td>
                  <td style={unitCell}>kg/cm²A</td>
                  <td style={{ ...nameCell, color: '#64748b', fontSize: '0.76rem' }}>BACA DCS</td>
                  <td style={noteCell}>Rentang tipikal: 2.4 – 3.5 kg/cm²A</td>
                </tr>

                {/* B2: 4K-2 LP Discharge Pressure */}
                <tr style={{ backgroundColor: '#fafafa' }}>
                  <td style={{ ...tagCell, color: '#64748b' }}>H4PI015A</td>
                  <td style={nameCell}>Tekanan Discharge 4K-2 (LP MCR)</td>
                  <td style={valCell}>{dcsVal('p_4k2_disch_kgcm2a')}</td>
                  <td style={{ ...valCell, color: '#334155' }}>{dcsVal('p_4k2_disch_kgcm2a')}</td>
                  <td style={unitCell}>kg/cm²A</td>
                  <td style={{ ...nameCell, color: '#64748b', fontSize: '0.76rem' }}>BACA DCS</td>
                  <td style={noteCell}>Rentang tipikal: 12.0 – 15.5 kg/cm²A</td>
                </tr>

                {/* B3: 4K-3 HP Suction Pressure */}
                <tr style={{ backgroundColor: '#fff' }}>
                  <td style={{ ...tagCell, color: '#64748b' }}>H4PI016B</td>
                  <td style={nameCell}>Tekanan Suction 4K-3 (HP MCR)</td>
                  <td style={valCell}>{dcsVal('p_4k3_suct_kgcm2a')}</td>
                  <td style={{ ...valCell, color: '#334155' }}>{dcsVal('p_4k3_suct_kgcm2a')}</td>
                  <td style={unitCell}>kg/cm²A</td>
                  <td style={{ ...nameCell, color: '#64748b', fontSize: '0.76rem' }}>BACA DCS</td>
                  <td style={noteCell}>Setelah intercooler 4E-5</td>
                </tr>

                {/* B4: 4K-3 HP Discharge Pressure */}
                <tr style={{ backgroundColor: '#fafafa' }}>
                  <td style={{ ...tagCell, color: '#64748b' }}>H4PI017B</td>
                  <td style={nameCell}>Tekanan Discharge 4K-3 (HP MCR)</td>
                  <td style={valCell}>{dcsVal('p_4k3_disch_kgcm2a')}</td>
                  <td style={{ ...valCell, color: '#334155' }}>{dcsVal('p_4k3_disch_kgcm2a')}</td>
                  <td style={unitCell}>kg/cm²A</td>
                  <td style={{ ...nameCell, color: '#64748b', fontSize: '0.76rem' }}>BACA DCS</td>
                  <td style={noteCell}>Rentang tipikal: 42.0 – 48.0 kg/cm²A</td>
                </tr>

                {/* B5: Pressure Ratio LP */}
                <tr style={{ backgroundColor: '#fff' }}>
                  <td style={{ ...tagCell, color: '#64748b' }}>rp_LP_MCR</td>
                  <td style={nameCell}>Rasio Tekanan LP 4K-2 (P<sub>disch</sub>/P<sub>suct</sub>)</td>
                  <td style={valCell}>4.23</td>
                  <td style={{ ...valCell, color: '#334155' }}>{(feat.rp_LP_MCR ?? 4.23).toFixed(2)}</td>
                  <td style={unitCell}>—</td>
                  <td style={{ ...nameCell, color: '#64748b', fontSize: '0.76rem' }}>DIHITUNG</td>
                  <td style={noteCell}>Manual Book §3.3: r<sub>p,LP</sub> = 13.50/3.15 = 4.286</td>
                </tr>

                {/* B6: Pressure Ratio HP */}
                <tr style={{ backgroundColor: '#fafafa' }}>
                  <td style={{ ...tagCell, color: '#64748b' }}>rp_HP_MCR</td>
                  <td style={nameCell}>Rasio Tekanan HP 4K-3 (P<sub>disch</sub>/P<sub>suct</sub>)</td>
                  <td style={valCell}>3.27</td>
                  <td style={{ ...valCell, color: '#334155' }}>{(feat.rp_HP_MCR ?? 3.27).toFixed(2)}</td>
                  <td style={unitCell}>—</td>
                  <td style={{ ...nameCell, color: '#64748b', fontSize: '0.76rem' }}>DIHITUNG</td>
                  <td style={noteCell}>Manual Book §3.3: r<sub>p,HP</sub> = 43.60/13.50 = 3.230</td>
                </tr>

                {/* B7: Pressure Ratio Total MCR */}
                <tr style={{ backgroundColor: '#fff' }}>
                  <td style={{ ...tagCell, color: '#64748b' }}>rp_MCR_total</td>
                  <td style={nameCell}>Rasio Tekanan Total MCR (LP × HP)</td>
                  <td style={valCell}>13.56</td>
                  <td style={{ ...valCell, color: '#334155' }}>{(feat.rp_MCR_total ?? 13.56).toFixed(2)}</td>
                  <td style={unitCell}>—</td>
                  <td style={{ ...nameCell, color: '#64748b', fontSize: '0.76rem' }}>DIHITUNG</td>
                  <td style={noteCell}>r<sub>p,Total</sub> = r<sub>p,LP</sub> × r<sub>p,HP</sub></td>
                </tr>

                {/* B8: dP Interstage 4E-5 */}
                <tr style={{ backgroundColor: '#fafafa' }}>
                  <td style={{ ...tagCell, color: '#64748b' }}>dp_4E-5</td>
                  <td style={nameCell}>ΔP Interstage Cooler 4E-5</td>
                  <td style={valCell}>0.28</td>
                  <td style={{ ...valCell, color: '#334155' }}>{(feat.dp_interstage_4E5 ?? 0.28).toFixed(2)}</td>
                  <td style={unitCell}>kg/cm²</td>
                  <td style={{ ...nameCell, color: '#64748b', fontSize: '0.76rem' }}>DIHITUNG</td>
                  <td style={noteCell}>P<sub>disch,4K-2</sub> − P<sub>suct,4K-3</sub></td>
                </tr>

                {/* B9: Propane 4K-1 Suction */}
                <tr style={{ backgroundColor: '#fff' }}>
                  <td style={{ ...tagCell, color: '#64748b' }}>H4PIC002</td>
                  <td style={nameCell}>Tekanan Suction Propana 4K-1</td>
                  <td style={valCell}>{dcsVal('p_c3_suct_kgcm2a')}</td>
                  <td style={{ ...valCell, color: '#334155' }}>{dcsVal('p_c3_suct_kgcm2a')}</td>
                  <td style={unitCell}>kg/cm²A</td>
                  <td style={{ ...nameCell, color: '#64748b', fontSize: '0.76rem' }}>BACA DCS</td>
                  <td style={noteCell}>LP Propane evaporator</td>
                </tr>

                {/* B10: Propane 4K-1 Discharge */}
                <tr style={{ backgroundColor: '#fafafa' }}>
                  <td style={{ ...tagCell, color: '#64748b' }}>H4PI006B</td>
                  <td style={nameCell}>Tekanan Discharge Propana 4K-1</td>
                  <td style={valCell}>{dcsVal('p_c3_disch_kgcm2a')}</td>
                  <td style={{ ...valCell, color: '#334155' }}>{dcsVal('p_c3_disch_kgcm2a')}</td>
                  <td style={unitCell}>kg/cm²A</td>
                  <td style={{ ...nameCell, color: '#64748b', fontSize: '0.76rem' }}>BACA DCS</td>
                  <td style={noteCell}>Rentang tipikal: 13.0 – 15.0 kg/cm²A</td>
                </tr>

                {/* B11: rp_C3_total */}
                <tr style={{ backgroundColor: '#fff' }}>
                  <td style={{ ...tagCell, color: '#64748b' }}>rp_C3_total</td>
                  <td style={nameCell}>Rasio Tekanan Total Propana 4K-1</td>
                  <td style={valCell}>13.56</td>
                  <td style={{ ...valCell, color: '#334155' }}>{(feat.rp_C3_total ?? 13.56).toFixed(2)}</td>
                  <td style={unitCell}>—</td>
                  <td style={{ ...nameCell, color: '#64748b', fontSize: '0.76rem' }}>DIHITUNG</td>
                  <td style={noteCell}>r<sub>p,C3</sub> = P<sub>disch</sub>/P<sub>suct</sub> (4K-1)</td>
                </tr>

                {/* B12: Suction Drum Temp */}
                <tr style={{ backgroundColor: '#fafafa' }}>
                  <td style={{ ...tagCell, color: '#64748b' }}>H4TI004B</td>
                  <td style={nameCell}>Suhu Suction Drum 4C-8</td>
                  <td style={valCell}>{dcsVal('H4TI004B')}</td>
                  <td style={{ ...valCell, color: parseFloat(dcsVal('H4TI004B') || '-40.5') >= -45.0 ? '#107c41' : '#dc2626', fontWeight: 700 }}>
                    {dcsVal('H4TI004B')}
                  </td>
                  <td style={unitCell}>°C</td>
                  <td style={{
                    ...nameCell,
                    fontWeight: 700,
                    color: parseFloat(dcsVal('H4TI004B') || '-40.5') >= -45.0 ? '#107c41' : '#dc2626',
                    fontSize: '0.78rem',
                  }}>
                    {parseFloat(dcsVal('H4TI004B') || '-40.5') >= -45.0 ? '✅ > −45°C' : '⚠ TAL'}
                  </td>
                  <td style={noteCell}>TAL: ≥ −45.0°C (Modul 4, mencegah liquid carryover)</td>
                </tr>

                {/* B13-B18: MCHE Temperatures */}
                {[
                  { tag: 'H5TI0047', key: 't_mche_warm_mrv_in_c', name: 'Suhu Masuk MRV Warm End', note: 'MRV inlet warm bundle' },
                  { tag: 'H5TI0026', key: 't_mche_warm_mrv_out_c', name: 'Suhu Keluar MRV Warm Bundle', note: 'MRV outlet warm bundle' },
                  { tag: 'H5TI0021', key: 't_mche_shell_mid_c', name: 'Suhu Shell Tengah MCHE', note: 'Mid-shell LNG side' },
                  { tag: 'H5TI0025', key: 't_mche_cold_mrv_out_c', name: 'Suhu Keluar MRV Cold Bundle', note: 'MRV outlet cold bundle' },
                  { tag: 'H5TI0029', key: 't_lng_rundown_c', name: 'Suhu LNG Rundown ke Tangki', note: 'Target: −152 s/d −158°C' },
                  { tag: 'H5TI0027', key: 't_fg_cb_in_c', name: 'Suhu Feed Gas Masuk Cold Bundle', note: 'FG inlet cold bundle' },
                ].map((row, i) => (
                  <tr key={row.tag} style={{ backgroundColor: i % 2 === 0 ? '#fff' : '#fafafa' }}>
                    <td style={{ ...tagCell, color: '#64748b' }}>{row.tag}</td>
                    <td style={nameCell}>{row.name}</td>
                    <td style={valCell}>{dcsVal(row.key)}</td>
                    <td style={{ ...valCell, color: '#334155' }}>{dcsVal(row.key)}</td>
                    <td style={unitCell}>°C</td>
                    <td style={{ ...nameCell, color: '#64748b', fontSize: '0.76rem' }}>BACA DCS</td>
                    <td style={noteCell}>{row.note}</td>
                  </tr>
                ))}

                {/* B19-B20: MCHE dT computed */}
                <tr style={{ backgroundColor: '#fff' }}>
                  <td style={{ ...tagCell, color: '#64748b' }}>ΔT_cold</td>
                  <td style={nameCell}>Approach Suhu Cold Bundle MCHE</td>
                  <td style={valCell}>5.4</td>
                  <td style={{ ...valCell, color: '#334155' }}>{(feat.MCHE_dT_cold_bundle_approach ?? 5.4).toFixed(1)}</td>
                  <td style={unitCell}>°C</td>
                  <td style={{ ...nameCell, color: '#64748b', fontSize: '0.76rem' }}>DIHITUNG</td>
                  <td style={noteCell}>MITA ≥ 1.50°C (Modul 2, Hukum Termodinamika II)</td>
                </tr>
                <tr style={{ backgroundColor: '#fafafa' }}>
                  <td style={{ ...tagCell, color: '#64748b' }}>ΔT_shell</td>
                  <td style={nameCell}>Rentang Suhu Shell MCHE</td>
                  <td style={valCell}>90.8</td>
                  <td style={{ ...valCell, color: '#334155' }}>{(feat.MCHE_dT_shell_span ?? 90.8).toFixed(1)}</td>
                  <td style={unitCell}>°C</td>
                  <td style={{ ...nameCell, color: '#64748b', fontSize: '0.76rem' }}>DIHITUNG</td>
                  <td style={noteCell}>H5TI0047 − H5TI0025 (warm inlet − cold outlet MRV)</td>
                </tr>

                {/* B21: MW_MCR */}
                <tr style={{ backgroundColor: '#fff' }}>
                  <td style={{ ...tagCell, color: '#64748b' }}>MW_MCR</td>
                  <td style={nameCell}>Berat Molekul Semu MCR</td>
                  <td style={valCell}>27.5</td>
                  <td style={{ ...valCell, color: '#334155' }}>{(feat.MW_MCR ?? 27.5).toFixed(2)}</td>
                  <td style={unitCell}>g/mol</td>
                  <td style={{ ...nameCell, color: '#64748b', fontSize: '0.76rem' }}>DIHITUNG</td>
                  <td style={noteCell}>Σ(xi · MWi) dari komposisi 5-komponen</td>
                </tr>

                {/* B22-B23: Valve positions */}
                <tr style={{ backgroundColor: '#fafafa' }}>
                  <td style={{ ...tagCell, color: '#64748b' }}>4UV-53</td>
                  <td style={nameCell}>Bukaan Katup Kickback 4UV-53</td>
                  <td style={valCell}>{dcsVal('valve_4uv53_pct')}</td>
                  <td style={{ ...valCell, color: '#334155' }}>{dcsVal('valve_4uv53_pct')}</td>
                  <td style={unitCell}>%</td>
                  <td style={{ ...nameCell, color: '#64748b', fontSize: '0.76rem' }}>BACA DCS</td>
                  <td style={noteCell}>Safety constraint: recycle anti-surge</td>
                </tr>
                <tr style={{ backgroundColor: '#fff' }}>
                  <td style={{ ...tagCell, color: '#64748b' }}>4TV-510</td>
                  <td style={nameCell}>Bukaan Katup Reheat 4TV-510</td>
                  <td style={valCell}>{dcsVal('valve_4tv510_pct')}</td>
                  <td style={{ ...valCell, color: '#334155' }}>{dcsVal('valve_4tv510_pct')}</td>
                  <td style={unitCell}>%</td>
                  <td style={{ ...nameCell, color: '#64748b', fontSize: '0.76rem' }}>BACA DCS</td>
                  <td style={noteCell}>Hot gas reheat drum suction (Modul 4)</td>
                </tr>

                {/* ============================================================= */}
                {/* SEKSI C — DAMPAK KINERJA & ENERGI (OUTPUT MODEL ML) */}
                {/* ============================================================= */}
                <tr><td colSpan={7} style={sectionHdrStyle('#107c41')}>
                  ▎ SEKSI C — DAMPAK KINERJA & ENERGI (HASIL PREDIKSI MODEL ML)
                </td></tr>

                {/* C1: Total Power */}
                <tr style={{ backgroundColor: '#f0fdf4' }}>
                  <td style={{ ...tagCell, color: '#107c41', fontWeight: 700 }}>TOTAL_POWER</td>
                  <td style={{ ...nameCell, fontWeight: 700, color: '#107c41' }}>Total Daya Poros C3MR (4KT-1 + 4KT-2/3)</td>
                  <td style={{ ...valCell, fontWeight: 700 }}>{baselinePower.toFixed(2)}</td>
                  <td style={{
                    ...valCell,
                    fontSize: '0.95rem',
                    fontWeight: 800,
                    color: '#107c41',
                    backgroundColor: '#dcfce7',
                  }}>{currentPower.toFixed(2)}</td>
                  <td style={{ ...unitCell, fontWeight: 700, color: '#107c41' }}>MW</td>
                  <td style={{
                    ...nameCell,
                    fontWeight: 700,
                    color: deltaPower <= 0 ? '#107c41' : '#b45309',
                  }}>
                    {deltaPower <= 0 ? `HEMAT ${Math.abs(deltaPower).toFixed(2)} MW` : `NAIK +${deltaPower.toFixed(2)} MW`}
                  </td>
                  <td style={noteCell}>Batas sistem: Total Train C3MR (Propana + MCR LP/HP). Kolom aktual = model pada kondisi Aktual DCS</td>
                </tr>

                {/* C2: MCR Power Decomposition */}
                <tr style={{ backgroundColor: '#fff' }}>
                  <td style={{ ...tagCell, color: '#64748b' }}>4KT-2/3</td>
                  <td style={nameCell}>Daya Kompresor MCR (4K-2 LP + 4K-3 HP)</td>
                  <td style={{ ...valCell, color: '#94a3b8' }}>—</td>
                  <td style={{ ...valCell, fontWeight: 700, color: '#1e40af' }}>
                    {pred?.power_mcr_mw != null ? pred.power_mcr_mw.toFixed(2) : '—'}
                  </td>
                  <td style={unitCell}>MW</td>
                  <td style={{ ...nameCell, color: '#1e40af', fontWeight: 600, fontSize: '0.76rem' }}>DEKOMPOSISI</td>
                  <td style={noteCell}>Ẇ<sub>shaft</sub> = ṁ · Δh<sub>s</sub> / η<sub>p</sub> (Modul 3)</td>
                </tr>

                {/* C3: C3 Power Decomposition */}
                <tr style={{ backgroundColor: '#fafafa' }}>
                  <td style={{ ...tagCell, color: '#64748b' }}>4KT-1</td>
                  <td style={nameCell}>Daya Kompresor Propana C3 (4K-1)</td>
                  <td style={{ ...valCell, color: '#94a3b8' }}>—</td>
                  <td style={{ ...valCell, fontWeight: 700, color: '#7c3aed' }}>
                    {pred?.power_c3_mw != null ? pred.power_c3_mw.toFixed(2) : '—'}
                  </td>
                  <td style={unitCell}>MW</td>
                  <td style={{ ...nameCell, color: '#7c3aed', fontWeight: 600, fontSize: '0.76rem' }}>DEKOMPOSISI</td>
                  <td style={noteCell}>Precooling C3 loop (chiller 3E-14/17/18)</td>
                </tr>

                {/* C4: Delta Power */}
                <tr style={{ backgroundColor: '#fff' }}>
                  <td style={{ ...tagCell, color: '#64748b' }}>DELTA_POWER</td>
                  <td style={nameCell}>Selisih Daya Target vs Aktual DCS</td>
                  <td style={{ ...valCell, color: '#94a3b8' }}>0.00</td>
                  <td style={{
                    ...valCell,
                    fontWeight: 700,
                    color: deltaPower <= 0 ? '#107c41' : '#b45309',
                  }}>
                    {deltaPower > 0 ? '+' : ''}{deltaPower.toFixed(2)} ({deltaPct > 0 ? '+' : ''}{deltaPct.toFixed(1)}%)
                  </td>
                  <td style={unitCell}>MW / %</td>
                  <td style={{
                    ...nameCell,
                    fontWeight: 600,
                    color: deltaPower <= 0 ? '#107c41' : '#b45309',
                  }}>
                    {deltaPower <= 0 ? 'EFISIENSI ↑' : 'BEBAN ↑'}
                  </td>
                  <td style={noteCell}>Penurunan daya menurunkan konsumsi uap boiler</td>
                </tr>

                {/* C5: SEC LNG per tonne of LNG (H5FI6A) */}
                <tr style={{ backgroundColor: '#f0fdf4' }}>
                  <td style={{ ...tagCell, color: '#107c41', fontWeight: 700 }}>SEC_LNG</td>
                  <td style={{ ...nameCell, fontWeight: 700, color: '#107c41' }}>
                    SEC LNG (Specific Energy Consumption per Ton LNG)
                  </td>
                  <td style={{ ...valCell, fontWeight: 700 }}>{baselineSecLng.toFixed(1)}</td>
                  <td style={{
                    ...valCell,
                    fontWeight: 800,
                    color: '#107c41',
                    fontSize: '0.95rem',
                    backgroundColor: '#dcfce7',
                  }}>{secLng.toFixed(1)}</td>
                  <td style={{ ...unitCell, fontWeight: 700, color: '#107c41' }}>kWh/t LNG</td>
                  <td style={{
                    ...nameCell,
                    fontWeight: 700,
                    color: deltaSecLng <= 0 ? '#107c41' : '#b45309',
                  }}>
                    {deltaSecLng <= 0 ? `HEMAT ${Math.abs(deltaSecLng).toFixed(1)} kWh/t` : `NAIK +${deltaSecLng.toFixed(1)} kWh/t`}
                  </td>
                  <td style={noteCell}>
                    = (Total Power × 1000) / H5FI6A [t/h LNG]. Metrik efisiensi resmi Plant-5 Train H (Liquefaction)
                  </td>
                </tr>

                {/* C5b: Specific Shaft Power per tonne of Treated Feed */}
                <tr style={{ backgroundColor: '#fafafa' }}>
                  <td style={{ ...tagCell, color: '#64748b' }}>SPEC_POWER_FEED</td>
                  <td style={{ ...nameCell, fontWeight: 600 }}>Daya Poros Spesifik Umpan Treated Gas</td>
                  <td style={valCell}>{baselineSpecPowerFeed.toFixed(1)}</td>
                  <td style={{ ...valCell, fontWeight: 700, color: '#0f172a' }}>{specPowerFeed.toFixed(1)}</td>
                  <td style={unitCell}>kWh/t feed</td>
                  <td style={{ ...nameCell, color: '#64748b' }}>Daya / Umpan</td>
                  <td style={noteCell}>= (Total Power × 1000) / Treated Feed H3FI0004 [t/h feed]</td>
                </tr>

                {/* C6: CO2 Abatement */}
                <tr style={{ backgroundColor: '#fff' }}>
                  <td style={{ ...tagCell, color: '#64748b' }}>CO2_REDUKSI</td>
                  <td style={nameCell}>Estimasi Pengurangan Emisi CO₂ Boiler</td>
                  <td style={{ ...valCell, color: '#94a3b8' }}>—</td>
                  <td style={{
                    ...valCell,
                    fontWeight: 700,
                    color: (pred?.co2_abatement_t_day ?? 0) > 0 ? '#107c41' : '#64748b',
                  }}>
                    {pred?.co2_abatement_t_day != null ? `−${pred.co2_abatement_t_day.toFixed(1)}` : '—'}
                  </td>
                  <td style={unitCell}>t CO₂/hari</td>
                  <td style={{ ...nameCell, color: '#107c41', fontSize: '0.76rem' }}>
                    {(pred?.co2_abatement_t_day ?? 0) > 0 ? 'PENGURANGAN' : '—'}
                  </td>
                  <td style={noteCell}>Faktor emisi: 0.587 tCO₂/MWh (Modul 8)</td>
                </tr>

                {/* C7: Model Accuracy */}
                <tr style={{ backgroundColor: '#fafafa' }}>
                  <td style={{ ...tagCell, color: '#64748b' }}>MODEL_AKURASI</td>
                  <td style={nameCell}>Akurasi Model & Ketidakpastian (CI 95%)</td>
                  <td style={{ ...valCell, color: '#94a3b8' }}>R² = 0.836</td>
                  <td style={{ ...valCell, fontWeight: 600, color: '#107c41' }}>± 0.80 MW (0.93%)</td>
                  <td style={unitCell}>MW</td>
                  <td style={{ ...nameCell, color: '#107c41', fontWeight: 600 }}>TERVALIDASI</td>
                  <td style={noteCell}>Diuji pada 295 shift independen (MAE &lt; 1.0 MW)</td>
                </tr>

                {/* ============================================================= */}
                {/* SEKSI D — REKOMENDASI INJEKSI MAKE-UP HIDROKARBON */}
                {/* ============================================================= */}
                <tr><td colSpan={7} style={sectionHdrStyle('#c2410c')}>
                  ▎ SEKSI D — REKOMENDASI LAJU INJEKSI MAKE-UP HIDROKARBON (H4FIC005 – H4FIC007)
                </td></tr>

                {makeup?.items ? (
                  makeup.items.map((item, idx) => {
                    const isInj = item.action === 'INJEKSI';
                    return (
                      <tr key={idx} style={{ backgroundColor: isInj ? '#fffbeb' : '#fff' }}>
                        <td style={{ ...tagCell, color: isInj ? '#c2410c' : '#64748b' }}>{item.tag_dcs}</td>
                        <td style={nameCell}>{item.description}</td>
                        <td style={valCell}>{item.actual_molpct.toFixed(2)}</td>
                        <td style={{
                          ...valCell,
                          fontWeight: 700,
                          color: isInj ? '#c2410c' : '#107c41',
                        }}>
                          {item.recommended_flow_nm3_h.toFixed(1)} Nm³/h
                        </td>
                        <td style={unitCell}>{item.recommended_flow_kg_h.toFixed(1)} kg/h</td>
                        <td style={{
                          ...nameCell,
                          fontWeight: 700,
                          color: isInj ? '#c2410c' : '#107c41',
                        }}>
                          {isInj ? `🔶 ${item.action}` : item.action}
                        </td>
                        <td style={noteCell}>{item.instruction}</td>
                      </tr>
                    );
                  })
                ) : (
                  <tr>
                    <td colSpan={7} style={{ padding: '10px', textAlign: 'center', color: '#64748b', border: B }}>
                      Memuat rekomendasi make-up refrigeran...
                    </td>
                  </tr>
                )}

                {/* D-Total */}
                {makeup && (
                  <tr style={{ backgroundColor: '#fffbeb', fontWeight: 700 }}>
                    <td style={{ ...tagCell, color: '#c2410c' }}>TOTAL_MAKEUP</td>
                    <td style={{ ...nameCell, fontWeight: 700 }}>Total Laju Injeksi Hidrokarbon / N₂</td>
                    <td style={{ ...valCell, color: '#94a3b8' }}>—</td>
                    <td style={{
                      ...valCell,
                      color: '#9a3412',
                      fontSize: '0.9rem',
                      fontWeight: 800,
                    }}>
                      {makeup.total_makeup_flow_nm3_h.toFixed(1)} Nm³/h
                    </td>
                    <td style={{ ...unitCell, color: '#9a3412', fontWeight: 700 }}>
                      {makeup.total_makeup_flow_kg_h.toFixed(1)} kg/h
                    </td>
                    <td style={{ ...nameCell, color: '#9a3412', fontWeight: 700 }}>
                      DURASI {transitionHours.toFixed(1)} JAM
                    </td>
                    <td style={noteCell}>
                      Total massa make-up ke active loop inventory (~24.000 kg)
                    </td>
                  </tr>
                )}

                {/* ============================================================= */}
                {/* SEKSI E — AUDIT KESELAMATAN & DOMAIN ENVELOPE */}
                {/* ============================================================= */}
                <tr><td colSpan={7} style={sectionHdrStyle('#334155')}>
                  ▎ SEKSI E — AUDIT BATAS KESELAMATAN & JARAK MAHALANOBIS
                </td></tr>

                {/* E1: Mahalanobis */}
                <tr style={{ backgroundColor: '#fff' }}>
                  <td style={{ ...tagCell, color: '#64748b' }}>D_M</td>
                  <td style={{ ...nameCell, fontWeight: 600 }}>Jarak Mahalanobis Komposisi MCR</td>
                  <td style={valCell}>1.025</td>
                  <td style={{
                    ...valCell,
                    fontWeight: 700,
                    color: (domain?.in_domain ?? true) ? '#107c41' : '#dc2626',
                  }}>
                    {domain ? domain.mahalanobis_distance.toFixed(3) : '1.025'}
                  </td>
                  <td style={unitCell}>—</td>
                  <td style={{
                    ...nameCell,
                    fontWeight: 700,
                    color: (domain?.in_domain ?? true) ? '#107c41' : '#dc2626',
                  }}>
                    {(domain?.in_domain ?? true) ? '✅ DALAM DOMAIN' : '⚠ LUAR DOMAIN'}
                  </td>
                  <td style={noteCell}>Batas χ²₀.₉₅,₆: ≤ 3.0802 (Elipsoid 95%)</td>
                </tr>

                {/* E2: Anti-Surge Flow Floor */}
                <tr style={{ backgroundColor: '#fafafa' }}>
                  <td style={{ ...tagCell, color: '#64748b' }}>4UV-53_FLOOR</td>
                  <td style={nameCell}>Safe Operating Flow Floor Kompresor MCR</td>
                  <td style={valCell}>{actualDcs.mcr_flow_t_h.toFixed(1)}</td>
                  <td style={{
                    ...valCell,
                    fontWeight: 700,
                    color: scenario.mcr_flow_t_h >= 480.0 ? '#107c41' : '#dc2626',
                  }}>
                    {scenario.mcr_flow_t_h.toFixed(1)}
                  </td>
                  <td style={unitCell}>t/h</td>
                  <td style={{
                    ...nameCell,
                    fontWeight: 700,
                    color: scenario.mcr_flow_t_h >= 480.0 ? '#107c41' : '#dc2626',
                  }}>
                    {scenario.mcr_flow_t_h >= 480.0 ? '✅ MEMENUHI' : '❌ PELANGGARAN'}
                  </td>
                  <td style={noteCell}>Batas bawah aliran sirkulasi MCR via kickback 4UV-53 (≥ 480.0 t/h)</td>
                </tr>

                {/* E2b: Dynamic Compressor Map (Audit B2.2) */}
                <tr style={{ backgroundColor: '#ffffff' }}>
                  <td style={{ ...tagCell, color: '#64748b' }}>SURGE_MAP</td>
                  <td style={nameCell}>Peta Anti-Surge Dinamis Kompresor Sentrifugal</td>
                  <td style={{ ...valCell, color: '#94a3b8' }}>—</td>
                  <td style={{ ...valCell, color: '#94a3b8' }}>—</td>
                  <td style={unitCell}>% margin</td>
                  <td style={{ ...nameCell, color: '#64748b', fontSize: '0.74rem' }}>Belum Dievaluasi</td>
                  <td style={noteCell}>Memerlukan kurva head/dp lengkap — Saat ini hanya flow floor 480.0 t/h yang dievaluasi</td>
                </tr>

                {/* E3: TAL */}
                <tr style={{ backgroundColor: '#fff' }}>
                  <td style={{ ...tagCell, color: '#64748b' }}>H4TI004B_TAL</td>
                  <td style={nameCell}>Suction Drum 4C-8 Temperature Alarm Low</td>
                  <td style={valCell}>{dcsVal('H4TI004B')}</td>
                  <td style={{
                    ...valCell,
                    fontWeight: 700,
                    color: parseFloat(dcsVal('H4TI004B') || '-40.5') >= -45.0 ? '#107c41' : '#dc2626',
                  }}>
                    {dcsVal('H4TI004B')}
                  </td>
                  <td style={unitCell}>°C</td>
                  <td style={{
                    ...nameCell,
                    fontWeight: 700,
                    color: parseFloat(dcsVal('H4TI004B') || '-40.5') >= -45.0 ? '#107c41' : '#dc2626',
                  }}>
                    {parseFloat(dcsVal('H4TI004B') || '-40.5') >= -45.0 ? '✅ AMAN (> −45°C)' : '⚠ TAL ALARM'}
                  </td>
                  <td style={noteCell}>TAL: ≥ −45.0°C (Modul 4, mencegah liquid carryover)</td>
                </tr>

                {/* E4: Composition Closure */}
                <tr style={{ backgroundColor: '#fafafa' }}>
                  <td style={{ ...tagCell, color: '#64748b' }}>COMP_CLOSURE</td>
                  <td style={nameCell}>Closure Komposisi MCR (Σ mol%)</td>
                  <td style={valCell}>{actualCompSum.toFixed(2)}</td>
                  <td style={{
                    ...valCell,
                    fontWeight: 700,
                    color: Math.abs(compSum - 100.0) < 1.0 ? '#107c41' : '#b45309',
                  }}>
                    {compSum.toFixed(2)}
                  </td>
                  <td style={unitCell}>mol%</td>
                  <td style={{
                    ...nameCell,
                    fontWeight: 700,
                    color: Math.abs(compSum - 100.0) < 1.0 ? '#107c41' : '#b45309',
                  }}>
                    {Math.abs(compSum - 100.0) < 1.0 ? '✅ OK' : '⚠ KOREKSI'}
                  </td>
                  <td style={noteCell}>Simpleks S⁵: Σ fraksi mol = 100.0%</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* LEMBAR 2: GRAFIK */}
      {activeSheetTab === 'sheet-02' && (
        <div style={{ flex: 1, backgroundColor: '#0b1329', padding: '20px 24px 60px 24px' }}>
          <TabGrafik
            snapshot={snapshot}
            scenario={scenario}
            prediction={prediction}
            historicalPoints={historicalPoints}
          />
        </div>
      )}

      {/* LEMBAR 3: PANDUAN */}
      {activeSheetTab === 'sheet-03' && (
        <div style={{ flex: 1, backgroundColor: '#0b1329', padding: '20px 24px 60px 24px' }}>
          <TabPanduan />
        </div>
      )}

      {/* ==================================================================== */}
      {/* STATUS BAR (BOTTOM) */}
      {/* ==================================================================== */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        backgroundColor: '#111827',
        borderTop: '1px solid #1f2937',
        padding: '5px 18px',
        fontSize: '0.72rem',
        color: '#94a3b8',
        userSelect: 'none',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <span style={{ color: '#86efac', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '4px' }}>
            <span style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: '#10b981' }} />
            Sistem Siap
          </span>
          <span>PT Badak NGL — Plant-5 Train H (Liquefaction)</span>
          <span>Disiplin: AGENTS.md</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <span>Total: <strong style={{ color: '#fff' }}>{currentPower.toFixed(2)} MW</strong></span>
          <span>MCR: <strong style={{ color: '#93c5fd' }}>{pred?.power_mcr_mw != null ? `${pred.power_mcr_mw.toFixed(1)} MW` : '—'}</strong></span>
          <span>C3: <strong style={{ color: '#c4b5fd' }}>{pred?.power_c3_mw != null ? `${pred.power_c3_mw.toFixed(1)} MW` : '—'}</strong></span>
          <span>Komp: <strong style={{ color: '#fff' }}>{compSum.toFixed(1)}%</strong></span>
          <span>Make-Up: <strong style={{ color: '#f59e0b' }}>{makeup ? `${makeup.total_makeup_flow_nm3_h.toFixed(1)} Nm³/h` : '0.0 Nm³/h'}</strong></span>
        </div>
      </div>
    </div>
  );
};
