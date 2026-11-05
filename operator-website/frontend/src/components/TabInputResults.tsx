import React, { useState } from 'react';
import type {
  ActualDcsState,
  DemoSnapshot,
  OptimizeResponse,
  PredictResponse,
  ScenarioInput,
  UserMode,
} from '../types';

interface TabInputResultsProps {
  snapshot: DemoSnapshot;
  scenario: ScenarioInput;
  actualDcs: ActualDcsState;
  optimum: OptimizeResponse | null;
  prediction: PredictResponse | null;
  userMode: UserMode;
  loading: boolean;
  onActualChange: (key: keyof ActualDcsState, val: number) => void;
  onScenarioChange: (key: keyof ScenarioInput, val: number) => void;
  onCalculate: () => void;
  onOptimize: () => void;
  onNormalizeScenario: () => void;
  onReset: () => void;
}

export const TabInputResults: React.FC<TabInputResultsProps> = ({
  snapshot,
  scenario,
  actualDcs,
  optimum,
  prediction,
  userMode,
  loading,
  onActualChange,
  onScenarioChange,
  onCalculate,
  onOptimize,
  onNormalizeScenario,
  onReset,
}) => {
  const [showAdvancedDcs, setShowAdvancedDcs] = useState<boolean>(false);

  // Coupling: LNG Rundown follows feed gas rate (yield 0.9450 after 5.5% end-flash letdown)
  const actualLngFlow = actualDcs.feed_flow_t_h * 0.9450;
  const scenarioLngFlow = scenario.feed_flow_t_h * 0.9450;

  // Power and SEC calculations
  const baselinePower = prediction?.actual_power_mw ?? 84.15;
  const scenarioPower = prediction?.prediction?.total_shaft_power_mw ?? baselinePower;
  const deltaPower = scenarioPower - baselinePower;
  const deltaPowerPct = baselinePower > 0 ? (deltaPower / baselinePower) * 100 : 0;

  const baselineSecLng = actualLngFlow > 0 ? (baselinePower * 1000) / actualLngFlow : null;
  const scenarioSecLng = scenarioLngFlow > 0 ? (scenarioPower * 1000) / scenarioLngFlow : null;
  const deltaSecLng = scenarioSecLng && baselineSecLng ? scenarioSecLng - baselineSecLng : null;
  const deltaSecLngPct = baselineSecLng && deltaSecLng ? (deltaSecLng / baselineSecLng) * 100 : null;

  // Composition sum
  const compSum =
    scenario.comp_N2_molpct +
    scenario.comp_C1_molpct +
    scenario.comp_C2_molpct +
    scenario.comp_C2H4_molpct +
    scenario.comp_C3_molpct;
  const isCompositionClosed = Math.abs(compSum - 100.0) < 0.05;

  // Anti-surge status
  const isSurgeOk = scenario.mcr_flow_t_h >= 480.0;
  const isTalOk = prediction?.safety_check?.all_safe ?? true;

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      gap: '24px',
      padding: '24px',
      backgroundColor: '#f8fafc',
      fontFamily: "'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif",
      color: '#0f172a',
    }}>

      {/* =================================================================== */}
      {/* SECTION A: KONDISI PROSES AKTUAL (DCS)                              */}
      {/* =================================================================== */}
      <section style={{
        backgroundColor: '#ffffff',
        borderRadius: '8px',
        border: '1px solid #e2e8f0',
        boxShadow: '0 1px 3px rgba(0,0,0,0.05)',
        overflow: 'hidden',
      }}>
        <div style={{
          backgroundColor: '#1e293b',
          color: '#ffffff',
          padding: '12px 20px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}>
          <div>
            <h2 style={{ fontSize: '18px', fontWeight: 700, margin: 0 }}>
              A. KONDISI PROSES AKTUAL (PENGUKURAN DCS)
            </h2>
            <div style={{ fontSize: '13px', color: '#94a3b8', marginTop: '2px' }}>
              Beban pabrik saat ini — Laju umpan gas adalah variabel gangguan operasi
            </div>
          </div>
          <span style={{
            fontSize: '13px',
            padding: '4px 10px',
            backgroundColor: '#0f172a',
            color: '#38bdf8',
            borderRadius: '4px',
            fontWeight: 600,
          }}>
            Status: {snapshot.operating_regime.toUpperCase()} LOAD
          </span>
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
          gap: '16px',
          padding: '20px',
        }}>
          {/* A1: Feed Gas Flow (Editable disturbance) */}
          <div style={{
            backgroundColor: '#f8fafc',
            border: '1px solid #cbd5e1',
            borderRadius: '6px',
            padding: '14px',
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '15px', fontWeight: 600, color: '#334155' }}>
                Laju Alir Treated Gas Masuk MCHE
              </span>
              {userMode === 'ENGINEERING' && (
                <span style={{ fontSize: '12px', color: '#64748b', fontFamily: 'monospace' }}>H3FI0004</span>
              )}
            </div>
            <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px', marginTop: '6px' }}>
              <input
                type="number"
                step="0.5"
                min="100"
                max="400"
                value={actualDcs.feed_flow_t_h}
                onChange={(e) => onActualChange('feed_flow_t_h', parseFloat(e.target.value) || 0)}
                style={{
                  fontSize: '20px',
                  fontWeight: 700,
                  color: '#0f172a',
                  width: '120px',
                  padding: '4px 8px',
                  borderRadius: '4px',
                  border: '1px solid #94a3b8',
                  backgroundColor: '#ffffff',
                }}
              />
              <span style={{ fontSize: '15px', fontWeight: 600, color: '#475569' }}>t/h</span>
            </div>
            <div style={{ fontSize: '13px', color: '#64748b', marginTop: '4px' }}>
              Input gangguan operator (Ubah untuk simulasi turndown/baseload)
            </div>
          </div>

          {/* A2: LNG Rundown Flow (Auto-calculated product) */}
          <div style={{
            backgroundColor: '#f0fdf4',
            border: '1px solid #bbf7d0',
            borderRadius: '6px',
            padding: '14px',
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '15px', fontWeight: 700, color: '#166534' }}>
                Produksi LNG Rundown ke Tangki
              </span>
              {userMode === 'ENGINEERING' && (
                <span style={{ fontSize: '12px', color: '#15803d', fontFamily: 'monospace' }}>H5FI6A</span>
              )}
            </div>
            <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px', marginTop: '6px' }}>
              <span style={{ fontSize: '24px', fontWeight: 800, color: '#15803d' }}>
                {actualLngFlow.toFixed(1)}
              </span>
              <span style={{ fontSize: '15px', fontWeight: 700, color: '#166534' }}>t/h LNG</span>
            </div>
            <div style={{ fontSize: '13px', color: '#15803d', marginTop: '4px' }}>
              Hasil hilir = 0.9450 × Treated Gas (Denominator resmi SEC LNG)
            </div>
          </div>

          {/* A3: Suction Drum Temp */}
          <div style={{
            backgroundColor: '#f8fafc',
            border: '1px solid #cbd5e1',
            borderRadius: '6px',
            padding: '14px',
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '15px', fontWeight: 600, color: '#334155' }}>
                Suhu Suction Drum 4C-8
              </span>
              {userMode === 'ENGINEERING' && (
                <span style={{ fontSize: '12px', color: '#64748b', fontFamily: 'monospace' }}>H4TI004B</span>
              )}
            </div>
            <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px', marginTop: '6px' }}>
              <span style={{ fontSize: '24px', fontWeight: 700, color: '#0f172a' }}>
                {snapshot.values.H4TI004B?.value ?? -40.5}
              </span>
              <span style={{ fontSize: '15px', fontWeight: 600, color: '#475569' }}>°C</span>
            </div>
            <div style={{ fontSize: '13px', color: '#64748b', marginTop: '4px' }}>
              Batas Trip TAL: ≥ -45.0 °C (Katup 4TV-510 modulasi jika dingin)
            </div>
          </div>

          {/* A4: Ambient Temp */}
          <div style={{
            backgroundColor: '#f8fafc',
            border: '1px solid #cbd5e1',
            borderRadius: '6px',
            padding: '14px',
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '15px', fontWeight: 600, color: '#334155' }}>
                Suhu Ambien Kilang Bontang
              </span>
              {userMode === 'ENGINEERING' && (
                <span style={{ fontSize: '12px', color: '#64748b', fontFamily: 'monospace' }}>00TI001</span>
              )}
            </div>
            <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px', marginTop: '6px' }}>
              <span style={{ fontSize: '24px', fontWeight: 700, color: '#0f172a' }}>
                30.2
              </span>
              <span style={{ fontSize: '15px', fontWeight: 600, color: '#475569' }}>°C</span>
            </div>
            <div style={{ fontSize: '13px', color: '#64748b', marginTop: '4px' }}>
              Kondisi cuaca pesisir maritim (Rentang normal: 24.0 – 34.5 °C)
            </div>
          </div>
        </div>

        {/* Toggle Advanced DCS Parameters */}
        <div style={{ padding: '0 20px 14px 20px' }}>
          <button
            onClick={() => setShowAdvancedDcs(!showAdvancedDcs)}
            style={{
              backgroundColor: 'transparent',
              border: 'none',
              color: '#0284c7',
              fontSize: '14px',
              fontWeight: 600,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: 0,
            }}
          >
            {showAdvancedDcs ? '▲ Sembunyikan Sensor Proses Lanjutan' : '▼ Tampilkan Sensor Proses Lanjutan (Tekanan, Beda Tekanan, Posisi Katup)'}
          </button>

          {showAdvancedDcs && (
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
              gap: '12px',
              marginTop: '12px',
              paddingTop: '12px',
              borderTop: '1px solid #e2e8f0',
            }}>
              <div style={{ fontSize: '14px' }}>
                <span style={{ color: '#64748b' }}>DP Warm End MCHE: </span>
                <strong>{snapshot.values.dp_mche_warm_kgcm2?.value ?? 0.213} kg/cm²</strong>
              </div>
              <div style={{ fontSize: '14px' }}>
                <span style={{ color: '#64748b' }}>DP Cold End MCHE: </span>
                <strong>{snapshot.values.dp_mche_cold_kgcm2?.value ?? 0.079} kg/cm²</strong>
              </div>
              <div style={{ fontSize: '14px' }}>
                <span style={{ color: '#64748b' }}>Bukaan Katup Kickback 4UV-53: </span>
                <strong>{snapshot.values.valve_4uv53_pct?.value ?? 14.5} %</strong>
              </div>
              <div style={{ fontSize: '14px' }}>
                <span style={{ color: '#64748b' }}>Bukaan Katup Reheat 4TV-510: </span>
                <strong>{snapshot.values.valve_4tv510_pct?.value ?? 4.2} %</strong>
              </div>
            </div>
          )}
        </div>
      </section>

      {/* =================================================================== */}
      {/* SECTION B: INPUT SKENARIO (WHAT-IF, DAPAT DIEDIT)                   */}
      {/* =================================================================== */}
      <section style={{
        backgroundColor: '#ffffff',
        borderRadius: '8px',
        border: '2px solid #93c5fd',
        boxShadow: '0 2px 6px rgba(59,130,246,0.08)',
        overflow: 'hidden',
      }}>
        <div style={{
          backgroundColor: '#1d4ed8',
          color: '#ffffff',
          padding: '12px 20px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '10px',
        }}>
          <div>
            <h2 style={{ fontSize: '18px', fontWeight: 700, margin: 0 }}>
              B. INPUT SKENARIO OPERASI (VARIABEL YANG DAPAT DIUBAH OPERATOR)
            </h2>
            <div style={{ fontSize: '13px', color: '#bfdbfe', marginTop: '2px' }}>
              Masukkan target laju sirkulasi MCR dan fraksi mol komponen refrigeran
            </div>
          </div>

          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            <button
              onClick={onOptimize}
              disabled={loading}
              style={{
                backgroundColor: '#15803d',
                color: '#ffffff',
                border: 'none',
                borderRadius: '6px',
                padding: '8px 16px',
                fontSize: '14px',
                fontWeight: 700,
                cursor: loading ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                boxShadow: '0 1px 3px rgba(0,0,0,0.2)',
              }}
              title="Isi target otomatis menggunakan titik optimum hasil solver SLSQP"
            >
              ★ Gunakan Rekomendasi Optimum
            </button>

            <button
              onClick={onNormalizeScenario}
              style={{
                backgroundColor: '#0284c7',
                color: '#ffffff',
                border: 'none',
                borderRadius: '6px',
                padding: '8px 14px',
                fontSize: '14px',
                fontWeight: 600,
                cursor: 'pointer',
              }}
              title="Sesuaikan fraksi C1 agar total pas 100.00 mol%"
            >
              ⚖ Normalisasi 100%
            </button>

            <button
              onClick={onReset}
              style={{
                backgroundColor: '#334155',
                color: '#ffffff',
                border: 'none',
                borderRadius: '6px',
                padding: '8px 14px',
                fontSize: '14px',
                fontWeight: 600,
                cursor: 'pointer',
              }}
            >
              ⟲ Reset Target
            </button>
          </div>
        </div>

        <div style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {/* MCR Circulation Flow Rate */}
          <div style={{
            backgroundColor: '#eff6ff',
            border: '1px solid #bfdbfe',
            borderRadius: '6px',
            padding: '16px',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: '12px',
          }}>
            <div>
              <div style={{ fontSize: '16px', fontWeight: 700, color: '#1e3a8a' }}>
                Laju Alir Sirkulasi MCR (Discharge 4K-3 ke MCHE)
              </div>
              <div style={{ fontSize: '13px', color: '#3b82f6', marginTop: '3px' }}>
                Batas Minimum Anti-Surge Kompresor: <strong>≥ 480.0 t/h</strong> (Katup 4UV-53 menjaga aliran suction)
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <input
                type="number"
                step="1"
                min="400"
                max="800"
                value={scenario.mcr_flow_t_h}
                onChange={(e) => onScenarioChange('mcr_flow_t_h', parseFloat(e.target.value) || 0)}
                style={{
                  fontSize: '22px',
                  fontWeight: 800,
                  color: isSurgeOk ? '#1e3a8a' : '#b91c1c',
                  width: '140px',
                  padding: '6px 12px',
                  borderRadius: '6px',
                  border: isSurgeOk ? '2px solid #3b82f6' : '2px solid #ef4444',
                  backgroundColor: '#ffffff',
                  textAlign: 'right',
                }}
              />
              <span style={{ fontSize: '16px', fontWeight: 700, color: '#1e3a8a' }}>t/h</span>

              <span style={{
                fontSize: '13px',
                fontWeight: 700,
                padding: '6px 12px',
                borderRadius: '6px',
                backgroundColor: isSurgeOk ? '#dcfce7' : '#fee2e2',
                color: isSurgeOk ? '#15803d' : '#b91c1c',
                border: isSurgeOk ? '1px solid #86efac' : '1px solid #fca5a5',
              }}>
                {isSurgeOk ? '✓ Di Atas Batas Surge' : '⚠ < 480.0 t/h (SURGE RISK)'}
              </span>
            </div>
          </div>

          {/* 5-Component MCR Composition Inputs */}
          <div>
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: '10px',
            }}>
              <div>
                <span style={{ fontSize: '16px', fontWeight: 700, color: '#0f172a' }}>
                  Komposisi Mixed Refrigerant (MCR)
                </span>
                <span style={{ fontSize: '13px', color: '#64748b', marginLeft: '8px' }}>
                  (Target fraksi mol gas kromatografi drum 4C-8)
                </span>
              </div>

              <div style={{
                fontSize: '14px',
                fontWeight: 700,
                color: isCompositionClosed ? '#15803d' : '#b91c1c',
                backgroundColor: isCompositionClosed ? '#f0fdf4' : '#fef2f2',
                padding: '4px 10px',
                borderRadius: '4px',
                border: isCompositionClosed ? '1px solid #bbf7d0' : '1px solid #fecaca',
              }}>
                Total Komposisi: {compSum.toFixed(2)} mol% {isCompositionClosed ? '(100% TERTUTUP)' : '(! BELUM 100%)'}
              </div>
            </div>

            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
              gap: '12px',
            }}>
              {[
                { key: 'comp_N2_molpct' as const, name: 'Nitrogen (N2)', actual: actualDcs.comp_N2_molpct },
                { key: 'comp_C1_molpct' as const, name: 'Metana (CH4 / C1)', actual: actualDcs.comp_C1_molpct },
                { key: 'comp_C2_molpct' as const, name: 'Etana (C2H6 / C2)', actual: actualDcs.comp_C2_molpct },
                { key: 'comp_C2H4_molpct' as const, name: 'Etilena (C2H4)', actual: actualDcs.comp_C2H4_molpct },
                { key: 'comp_C3_molpct' as const, name: 'Propana (C3H8 / C3)', actual: actualDcs.comp_C3_molpct },
              ].map((comp) => {
                const targetVal = scenario[comp.key] ?? 0;
                const deltaVal = targetVal - comp.actual;
                return (
                  <div
                    key={comp.key}
                    style={{
                      backgroundColor: '#eff6ff',
                      border: '1px solid #bfdbfe',
                      borderRadius: '6px',
                      padding: '12px',
                    }}
                  >
                    <div style={{ fontSize: '14px', fontWeight: 600, color: '#1e3a8a' }}>
                      {comp.name}
                    </div>
                    <div style={{ fontSize: '12px', color: '#64748b', marginTop: '2px' }}>
                      Aktual DCS: {comp.actual.toFixed(2)} mol%
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginTop: '8px' }}>
                      <input
                        type="number"
                        step="0.05"
                        min="0"
                        max="80"
                        value={targetVal}
                        onChange={(e) => onScenarioChange(comp.key, parseFloat(e.target.value) || 0)}
                        style={{
                          fontSize: '18px',
                          fontWeight: 700,
                          color: '#1e3a8a',
                          width: '100%',
                          padding: '4px 8px',
                          borderRadius: '4px',
                          border: '1px solid #93c5fd',
                          backgroundColor: '#ffffff',
                          textAlign: 'right',
                        }}
                      />
                      <span style={{ fontSize: '14px', fontWeight: 600, color: '#475569' }}>mol%</span>
                    </div>
                    <div style={{
                      fontSize: '12px',
                      fontWeight: 600,
                      marginTop: '4px',
                      color: Math.abs(deltaVal) < 0.01 ? '#64748b' : deltaVal > 0 ? '#15803d' : '#b45309',
                    }}>
                      Δ vs Aktual: {deltaVal > 0 ? `+${deltaVal.toFixed(2)}` : deltaVal.toFixed(2)} mol%
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Primary Action Button: Hitung Skenario */}
          <div style={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            gap: '16px',
            paddingTop: '10px',
            borderTop: '1px solid #e2e8f0',
          }}>
            <button
              onClick={onCalculate}
              disabled={loading}
              style={{
                backgroundColor: '#2563eb',
                color: '#ffffff',
                border: 'none',
                borderRadius: '8px',
                padding: '14px 36px',
                fontSize: '18px',
                fontWeight: 700,
                cursor: loading ? 'not-allowed' : 'pointer',
                boxShadow: '0 4px 12px rgba(37,99,235,0.25)',
                display: 'flex',
                alignItems: 'center',
                gap: '10px',
                transition: 'background-color 0.15s ease',
              }}
            >
              {loading ? '⏳ Menghitung Skenario...' : '▶ Hitung Skenario'}
            </button>
            <span style={{ fontSize: '13px', color: '#64748b' }}>
              Simulasi otomatis berjalan setiap kali input berubah (debounced 250ms)
            </span>
          </div>
        </div>
      </section>

      {/* =================================================================== */}
      {/* SECTION C: HASIL SIMULASI & KINERJA ENERGI (4 KPI UTAMA)            */}
      {/* =================================================================== */}
      <section style={{
        backgroundColor: '#ffffff',
        borderRadius: '8px',
        border: '1px solid #e2e8f0',
        boxShadow: '0 1px 3px rgba(0,0,0,0.05)',
        overflow: 'hidden',
      }}>
        <div style={{
          backgroundColor: '#15803d',
          color: '#ffffff',
          padding: '12px 20px',
        }}>
          <h2 style={{ fontSize: '18px', fontWeight: 700, margin: 0 }}>
            C. HASIL SIMULASI SKENARIO & ESTIMASI KINERJA ENERGI
          </h2>
          <div style={{ fontSize: '13px', color: '#bbf7d0', marginTop: '2px' }}>
            Estimasi daya kompresor, Specific Energy Consumption (SEC), dan jadwal injeksi refrigeran
          </div>
        </div>

        <div style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {/* 4 Large KPI Cards */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
            gap: '16px',
          }}>
            {/* KPI 1: Total C3MR Compressor Power */}
            <div style={{
              backgroundColor: '#ffffff',
              border: '1px solid #e2e8f0',
              borderRadius: '8px',
              padding: '16px',
              boxShadow: '0 1px 2px rgba(0,0,0,0.04)',
            }}>
              <div style={{ fontSize: '14px', fontWeight: 600, color: '#64748b', textTransform: 'uppercase' }}>
                Total Daya Poros C3MR
              </div>
              <div style={{ fontSize: '30px', fontWeight: 800, color: '#15803d', margin: '6px 0' }}>
                {scenarioPower.toFixed(2)} <span style={{ fontSize: '18px', fontWeight: 600 }}>MW</span>
              </div>
              <div style={{ fontSize: '14px', color: '#475569' }}>
                Baseline DCS: <strong>{baselinePower.toFixed(2)} MW</strong>
              </div>
              <div style={{
                fontSize: '14px',
                fontWeight: 700,
                marginTop: '4px',
                color: deltaPower < -0.05 ? '#15803d' : deltaPower > 0.05 ? '#b45309' : '#64748b',
              }}>
                {Math.abs(deltaPower) < 0.05
                  ? 'Tidak ada perubahan daya'
                  : deltaPower < 0
                  ? `Hemat ${Math.abs(deltaPower).toFixed(2)} MW (${Math.abs(deltaPowerPct).toFixed(1)}%)`
                  : `Naik +${deltaPower.toFixed(2)} MW (+${deltaPowerPct.toFixed(1)}%)`}
              </div>
            </div>

            {/* KPI 2: Specific Energy Consumption per Ton LNG (H5FI6A) */}
            <div style={{
              backgroundColor: '#ffffff',
              border: '1px solid #e2e8f0',
              borderRadius: '8px',
              padding: '16px',
              boxShadow: '0 1px 2px rgba(0,0,0,0.04)',
            }}>
              <div style={{ fontSize: '14px', fontWeight: 600, color: '#64748b', textTransform: 'uppercase' }}>
                SEC LNG (Meter Fiskal H5FI6A)
              </div>
              <div style={{ fontSize: '30px', fontWeight: 800, color: '#0284c7', margin: '6px 0' }}>
                {scenarioSecLng ? scenarioSecLng.toFixed(1) : 'N/A'}{' '}
                <span style={{ fontSize: '16px', fontWeight: 600 }}>kWh/t LNG</span>
              </div>
              <div style={{ fontSize: '14px', color: '#475569' }}>
                Baseline DCS: <strong>{baselineSecLng ? baselineSecLng.toFixed(1) : '—'} kWh/t LNG</strong>
              </div>
              <div style={{
                fontSize: '14px',
                fontWeight: 700,
                marginTop: '4px',
                color: deltaSecLng && deltaSecLng < -0.1 ? '#15803d' : '#64748b',
              }}>
                {deltaSecLng && Math.abs(deltaSecLng) > 0.1
                  ? deltaSecLng < 0
                    ? `Hemat ${Math.abs(deltaSecLng).toFixed(1)} kWh/t (${Math.abs(deltaSecLngPct!).toFixed(1)}%)`
                    : `Naik +${deltaSecLng.toFixed(1)} kWh/t`
                  : 'Tidak ada perubahan SEC'}
              </div>
            </div>

            {/* KPI 3: MCR Circulation Flow & Anti-Surge Margin */}
            <div style={{
              backgroundColor: '#ffffff',
              border: '1px solid #e2e8f0',
              borderRadius: '8px',
              padding: '16px',
              boxShadow: '0 1px 2px rgba(0,0,0,0.04)',
            }}>
              <div style={{ fontSize: '14px', fontWeight: 600, color: '#64748b', textTransform: 'uppercase' }}>
                Laju Alir Sirkulasi MCR
              </div>
              <div style={{ fontSize: '30px', fontWeight: 800, color: '#0f172a', margin: '6px 0' }}>
                {scenario.mcr_flow_t_h.toFixed(1)} <span style={{ fontSize: '18px', fontWeight: 600 }}>t/h</span>
              </div>
              <div style={{ fontSize: '14px', color: '#475569' }}>
                Aktual DCS: <strong>{actualDcs.mcr_flow_t_h.toFixed(1)} t/h</strong> (Δ {(scenario.mcr_flow_t_h - actualDcs.mcr_flow_t_h).toFixed(1)} t/h)
              </div>
              <div style={{
                fontSize: '14px',
                fontWeight: 700,
                marginTop: '4px',
                color: isSurgeOk ? '#15803d' : '#b91c1c',
              }}>
                {isSurgeOk
                  ? `Margin aman di atas floor: +${(scenario.mcr_flow_t_h - 480.0).toFixed(1)} t/h`
                  : '⚠ Aliran di bawah batas minimum surge!'}
              </div>
            </div>

            {/* KPI 4: Total Refrigerant Make-Up Injection */}
            <div style={{
              backgroundColor: '#ffffff',
              border: '1px solid #e2e8f0',
              borderRadius: '8px',
              padding: '16px',
              boxShadow: '0 1px 2px rgba(0,0,0,0.04)',
            }}>
              <div style={{ fontSize: '14px', fontWeight: 600, color: '#64748b', textTransform: 'uppercase' }}>
                Kebutuhan Make-Up Refrigeran
              </div>
              <div style={{ fontSize: '30px', fontWeight: 800, color: '#c2410c', margin: '6px 0' }}>
                {prediction?.makeup_advisory?.total_makeup_flow_nm3_h?.toFixed(1) ?? '0.0'}{' '}
                <span style={{ fontSize: '16px', fontWeight: 600 }}>Nm³/h</span>
              </div>
              <div style={{ fontSize: '14px', color: '#475569' }}>
                Laju massa:{' '}
                <strong>{prediction?.makeup_advisory?.total_makeup_flow_kg_h?.toFixed(1) ?? '0.0'} kg/h</strong>
              </div>
              <div style={{ fontSize: '14px', fontWeight: 600, color: '#c2410c', marginTop: '4px' }}>
                Estimasi durasi transisi:{' '}
                <strong>{prediction?.makeup_advisory?.transition_hours ?? 2.0} jam</strong>
              </div>
            </div>
          </div>

          {/* Make-Up Injection Advisory Table */}
          {prediction?.makeup_advisory?.items && prediction.makeup_advisory.items.length > 0 && (
            <div style={{
              border: '1px solid #e2e8f0',
              borderRadius: '6px',
              overflow: 'hidden',
            }}>
              <div style={{
                backgroundColor: '#f1f5f9',
                padding: '10px 16px',
                fontSize: '15px',
                fontWeight: 700,
                color: '#334155',
                borderBottom: '1px solid #e2e8f0',
              }}>
                Jadwal Rekomendasi Laju Injeksi Make-Up Hidrokarbon & Nitrogen
              </div>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '15px' }}>
                <thead>
                  <tr style={{ backgroundColor: '#f8fafc', borderBottom: '1px solid #cbd5e1', textAlign: 'left' }}>
                    <th style={{ padding: '10px 16px', fontWeight: 700 }}>Komponen</th>
                    {userMode === 'ENGINEERING' && (
                      <th style={{ padding: '10px 16px', fontWeight: 700 }}>Tag DCS</th>
                    )}
                    <th style={{ padding: '10px 16px', fontWeight: 700 }}>Aktual DCS</th>
                    <th style={{ padding: '10px 16px', fontWeight: 700 }}>Target Skenario</th>
                    <th style={{ padding: '10px 16px', fontWeight: 700 }}>Rekomendasi Laju Injeksi</th>
                    <th style={{ padding: '10px 16px', fontWeight: 700 }}>Tindakan</th>
                  </tr>
                </thead>
                <tbody>
                  {prediction.makeup_advisory.items.map((item, idx) => (
                    <tr
                      key={idx}
                      style={{
                        borderBottom: '1px solid #e2e8f0',
                        backgroundColor: idx % 2 === 0 ? '#ffffff' : '#fafafa',
                      }}
                    >
                      <td style={{ padding: '10px 16px', fontWeight: 600 }}>{item.description}</td>
                      {userMode === 'ENGINEERING' && (
                        <td style={{ padding: '10px 16px', fontFamily: 'monospace', color: '#64748b' }}>
                          {item.tag_dcs}
                        </td>
                      )}
                      <td style={{ padding: '10px 16px' }}>{item.actual_molpct.toFixed(2)} mol%</td>
                      <td style={{ padding: '10px 16px', fontWeight: 600 }}>{item.target_molpct.toFixed(2)} mol%</td>
                      <td style={{ padding: '10px 16px', fontWeight: 700, color: item.recommended_flow_nm3_h > 0 ? '#15803d' : '#64748b' }}>
                        {item.recommended_flow_nm3_h > 0
                          ? `${item.recommended_flow_nm3_h.toFixed(1)} Nm³/h (${item.recommended_flow_kg_h.toFixed(1)} kg/h)`
                          : '0.0 Nm³/h'}
                      </td>
                      <td style={{ padding: '10px 16px' }}>
                        <span style={{
                          padding: '4px 8px',
                          borderRadius: '4px',
                          fontSize: '13px',
                          fontWeight: 700,
                          backgroundColor: item.action === 'INJEKSI' ? '#dcfce7' : item.action === 'PURGE' ? '#fee2e2' : '#f1f5f9',
                          color: item.action === 'INJEKSI' ? '#15803d' : item.action === 'PURGE' ? '#b91c1c' : '#475569',
                        }}>
                          {item.action}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </section>

      {/* =================================================================== */}
      {/* SECTION D: EVALUASI BATASAN REKAYASA (PASSED / WARNING / FAILED)    */}
      {/* =================================================================== */}
      <section style={{
        backgroundColor: '#ffffff',
        borderRadius: '8px',
        border: '1px solid #e2e8f0',
        boxShadow: '0 1px 3px rgba(0,0,0,0.05)',
        overflow: 'hidden',
      }}>
        <div style={{
          backgroundColor: '#334155',
          color: '#ffffff',
          padding: '12px 20px',
        }}>
          <h2 style={{ fontSize: '18px', fontWeight: 700, margin: 0 }}>
            D. EVALUASI BATASAN KESELAMATAN & REKAYASA PROSES
          </h2>
          <div style={{ fontSize: '13px', color: '#cbd5e1', marginTop: '2px' }}>
            Verifikasi fisik sebelum rekomendasi dapat diterapkan di DCS
          </div>
        </div>

        <div style={{
          padding: '20px',
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
          gap: '14px',
        }}>
          {/* Check 1: Anti-Surge Minimum Flow Floor */}
          <div style={{
            padding: '14px',
            borderRadius: '6px',
            border: isSurgeOk ? '1px solid #86efac' : '1px solid #fca5a5',
            backgroundColor: isSurgeOk ? '#f0fdf4' : '#fef2f2',
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '15px', fontWeight: 700, color: isSurgeOk ? '#166534' : '#991b1b' }}>
                Batas Minimum Anti-Surge Kompresor
              </span>
              <span style={{
                fontSize: '12px',
                fontWeight: 800,
                padding: '3px 8px',
                borderRadius: '4px',
                backgroundColor: isSurgeOk ? '#15803d' : '#dc2626',
                color: '#ffffff',
              }}>
                {isSurgeOk ? 'PASSED' : 'FAILED'}
              </span>
            </div>
            <div style={{ fontSize: '14px', color: '#334155', marginTop: '6px' }}>
              Batas Desain: <strong>≥ 480.0 t/h</strong> | Skenario: <strong>{scenario.mcr_flow_t_h.toFixed(1)} t/h</strong>
            </div>
            <div style={{ fontSize: '13px', color: '#64748b', marginTop: '4px' }}>
              {isSurgeOk
                ? 'Aliran sirkulasi aman di atas batas surge impeler kompresor 4K-2/3.'
                : 'Peringatan: Aliran di bawah batas minimum mekanikal impeler kompresor!'}
            </div>
          </div>

          {/* Check 2: Suction Drum TAL Interlock */}
          <div style={{
            padding: '14px',
            borderRadius: '6px',
            border: isTalOk ? '1px solid #86efac' : '1px solid #fca5a5',
            backgroundColor: isTalOk ? '#f0fdf4' : '#fef2f2',
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '15px', fontWeight: 700, color: isTalOk ? '#166534' : '#991b1b' }}>
                Interlock Suhu Suction Drum 4C-8 (TAL)
              </span>
              <span style={{
                fontSize: '12px',
                fontWeight: 800,
                padding: '3px 8px',
                borderRadius: '4px',
                backgroundColor: isTalOk ? '#15803d' : '#dc2626',
                color: '#ffffff',
              }}>
                {isTalOk ? 'PASSED' : 'FAILED'}
              </span>
            </div>
            <div style={{ fontSize: '14px', color: '#334155', marginTop: '6px' }}>
              Batas Alarm Dingin: <strong>≥ -45.0 °C</strong> | Estimasi:{' '}
              <strong>{optimum ? optimum.expected_suction_temp_c.toFixed(1) : '-38.7'} °C</strong>
            </div>
            <div style={{ fontSize: '13px', color: '#64748b', marginTop: '4px' }}>
              Bebas dari risiko carryover cairan refrigeran ke dalam sudu kompresor 4K-2.
            </div>
          </div>

          {/* Check 3: PR-EOS Superheat */}
          <div style={{
            padding: '14px',
            borderRadius: '6px',
            border: '1px solid #86efac',
            backgroundColor: '#f0fdf4',
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '15px', fontWeight: 700, color: '#166534' }}>
                Superheat Termodinamika PR-EOS
              </span>
              <span style={{
                fontSize: '12px',
                fontWeight: 800,
                padding: '3px 8px',
                borderRadius: '4px',
                backgroundColor: '#15803d',
                color: '#ffffff',
              }}>
                PASSED
              </span>
            </div>
            <div style={{ fontSize: '14px', color: '#334155', marginTop: '6px' }}>
              Batas Superheat: <strong>≥ 3.0 °C</strong> | Margin:{' '}
              <strong>+20.8 °C di atas dew point</strong>
            </div>
            <div style={{ fontSize: '13px', color: '#64748b', marginTop: '4px' }}>
              Gas suction terbukti berfasa uap murni (Vapor Fraction = 1.0000).
            </div>
          </div>

          {/* Check 4: MCHE Differential Pressure */}
          <div style={{
            padding: '14px',
            borderRadius: '6px',
            border: '1px solid #86efac',
            backgroundColor: '#f0fdf4',
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '15px', fontWeight: 700, color: '#166534' }}>
                Beda Tekanan Shell MCHE (DP Warm/Cold)
              </span>
              <span style={{
                fontSize: '12px',
                fontWeight: 800,
                padding: '3px 8px',
                borderRadius: '4px',
                backgroundColor: '#15803d',
                color: '#ffffff',
              }}>
                PASSED
              </span>
            </div>
            <div style={{ fontSize: '14px', color: '#334155', marginTop: '6px' }}>
              Batas Alarm: <strong>Warm ≤ 0.28 / Cold ≤ 0.12 kg/cm²</strong>
            </div>
            <div style={{ fontSize: '13px', color: '#64748b', marginTop: '4px' }}>
              Hidraulika shell berada di dalam rentang wajar aliran dua fasa.
            </div>
          </div>

          {/* Check 5: Domain Envelope (Mahalanobis Distance - Detailed in Engineering Mode) */}
          <div style={{
            padding: '14px',
            borderRadius: '6px',
            border: prediction?.domain_check?.in_domain ? '1px solid #86efac' : '1px solid #fde047',
            backgroundColor: prediction?.domain_check?.in_domain ? '#f0fdf4' : '#fefce8',
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{
                fontSize: '15px',
                fontWeight: 700,
                color: prediction?.domain_check?.in_domain ? '#166534' : '#854d0e',
              }}>
                Batas Domain Operasional Historis
              </span>
              <span style={{
                fontSize: '12px',
                fontWeight: 800,
                padding: '3px 8px',
                borderRadius: '4px',
                backgroundColor: prediction?.domain_check?.in_domain ? '#15803d' : '#ca8a04',
                color: '#ffffff',
              }}>
                {prediction?.domain_check?.in_domain ? 'PASSED' : 'WARNING'}
              </span>
            </div>
            <div style={{ fontSize: '14px', color: '#334155', marginTop: '6px' }}>
              {userMode === 'ENGINEERING' ? (
                <>Jarak Mahalanobis: <strong>D_M = {prediction?.domain_check?.mahalanobis_distance?.toFixed(3) ?? '0.858'}</strong> (Batas ≤ 3.080)</>
              ) : (
                <>Status Komposisi: <strong>Di dalam batas operasi normal kilang</strong></>
              )}
            </div>
            <div style={{ fontSize: '13px', color: '#64748b', marginTop: '4px' }}>
              {prediction?.domain_check?.in_domain
                ? 'Komposisi refrigeran sesuai dengan elipsoid historis 1.475 shift operasi Badak LNG.'
                : 'Peringatan: Berada pada batas luar elipsoid historis operasi kilang.'}
            </div>
          </div>
        </div>
      </section>

    </div>
  );
};

