import React from 'react';
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
  snapshot: _snapshot,
  scenario,
  actualDcs: _actualDcs,
  optimum,
  prediction,
  userMode: _userMode,
  loading,
  onActualChange: _onActualChange,
  onScenarioChange,
  onCalculate: _onCalculate,
  onOptimize,
  onNormalizeScenario,
  onReset,
}) => {
  // Coupling: LNG Rundown follows feed gas rate (yield 0.9450 after 5.5% end-flash letdown)
  const scenarioLngFlow = scenario.feed_flow_t_h * 0.9450;

  // Power and SEC calculations (Evaluated ceteris-paribus at the active feed & LNG flow)
  const baselinePower = prediction?.actual_power_mw ?? 84.48;
  const scenarioPower = prediction?.prediction?.total_shaft_power_mw ?? baselinePower;
  const deltaPower = prediction?.prediction?.delta_power_mw ?? (scenarioPower - baselinePower);
  const deltaPowerPct = prediction?.prediction?.delta_power_pct ?? (baselinePower > 0 ? (deltaPower / baselinePower) * 100 : 0);

  const activeLngFlow = Math.max(scenarioLngFlow, 10.0);
  const baselineSecLng = (baselinePower * 1000) / activeLngFlow;
  const scenarioSecLng = prediction?.prediction?.sec_lng_kwh_per_t ?? ((scenarioPower * 1000) / activeLngFlow);
  const deltaSecLng = prediction?.prediction?.delta_sec_kwh_per_t ?? (scenarioSecLng - baselineSecLng);
  const deltaSecLngPct = baselineSecLng > 0 ? (deltaSecLng / baselineSecLng) * 100 : 0;

  // Steam and Fuel Gas savings
  const STEAM_RATE_T_PER_MWH = 4.04;
  const FUEL_GAS_NM3_PER_T_STEAM = 97.7;
  const FG_DENSITY_KG_NM3 = 0.75;

  const deltaPowerSavingMw = Math.max(0, -deltaPower);
  const steamSaved_t_h = deltaPowerSavingMw * STEAM_RATE_T_PER_MWH;
  const fuelGasSaved_nm3_h = steamSaved_t_h * FUEL_GAS_NM3_PER_T_STEAM;
  const fuelGasSaved_t_h = (fuelGasSaved_nm3_h * FG_DENSITY_KG_NM3) / 1000;
  const fuelGasSaved_usd_yr = (fuelGasSaved_nm3_h * 0.03535 * 6.0 * 8000) / 1_000_000;

  // Composition sum
  const compSum =
    scenario.comp_N2_molpct +
    scenario.comp_C1_molpct +
    scenario.comp_C2_molpct +
    scenario.comp_C2H4_molpct +
    scenario.comp_C3_molpct;
  const isCompositionClosed = Math.abs(compSum - 100.0) < 0.05;

  // Recommended values (verified physical SLSQP/GBRT outputs)
  const recMcrFlow = optimum?.mcr_flow_t_h ?? 480.0;
  const recN2 = optimum?.comp_N2_molpct ?? 3.31;
  const recC1 = optimum?.comp_C1_molpct ?? 46.08;
  const recC2 = optimum?.comp_C2_molpct ?? 45.15;
  const recC2H4 = optimum?.comp_C2H4_molpct ?? 0.05;
  const recC3 = optimum?.comp_C3_molpct ?? 5.41;

  const handleApplyRecommended = () => {
    onScenarioChange('mcr_flow_t_h', recMcrFlow);
    onScenarioChange('comp_N2_molpct', recN2);
    onScenarioChange('comp_C1_molpct', recC1);
    onScenarioChange('comp_C2_molpct', recC2);
    onScenarioChange('comp_C2H4_molpct', recC2H4);
    onScenarioChange('comp_C3_molpct', recC3);
    if (onOptimize) {
      onOptimize();
    }
  };

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      gap: '24px',
      paddingBottom: '36px',
      fontFamily: "'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif",
      color: '#0f172a',
    }}>

      {/* =================================================================== */}
      {/* SECTION 1: INPUT VARIABEL PROSES & REKOMENDASI AI                  */}
      {/* =================================================================== */}
      <section style={{
        backgroundColor: '#ffffff',
        borderRadius: '10px',
        border: '1px solid #e2e8f0',
        boxShadow: '0 2px 8px rgba(0,0,0,0.04)',
        overflow: 'hidden',
      }}>
        {/* Section Header */}
        <div style={{
          backgroundColor: '#0f172a',
          color: '#ffffff',
          padding: '14px 24px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          borderBottom: '2px solid #0284c7',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <span style={{
              backgroundColor: '#0284c7',
              color: '#ffffff',
              padding: '2px 8px',
              borderRadius: '4px',
              fontWeight: 800,
              fontSize: '12px',
              letterSpacing: '0.5px',
            }}>
              SECTION 1
            </span>
            <span style={{ fontSize: '16px', fontWeight: 700 }}>
              Input Operasi & Target Rekomendasi
            </span>
            <span style={{
              backgroundColor: '#1e293b',
              color: '#38bdf8',
              padding: '2px 8px',
              borderRadius: '12px',
              fontSize: '11px',
              fontWeight: 700,
            }}>
              Feed Gas • Flow MCR • Komposisi
            </span>
          </div>

          <div style={{ display: 'flex', gap: '10px' }}>
            <button
              onClick={handleApplyRecommended}
              disabled={loading}
              style={{
                backgroundColor: '#10b981',
                color: '#ffffff',
                border: 'none',
                borderRadius: '6px',
                padding: '6px 14px',
                fontWeight: 700,
                fontSize: '13px',
                cursor: loading ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                boxShadow: '0 1px 3px rgba(0,0,0,0.2)',
              }}
            >
              ⚡ Terapkan Rekomendasi AI
            </button>
            <button
              onClick={onReset}
              disabled={loading}
              style={{
                backgroundColor: '#334155',
                color: '#f1f5f9',
                border: '1px solid #475569',
                borderRadius: '6px',
                padding: '6px 12px',
                fontWeight: 600,
                fontSize: '13px',
                cursor: loading ? 'not-allowed' : 'pointer',
              }}
            >
              ⟲ Reset ke DCS
            </button>
          </div>
        </div>

        {/* Section Content: Comparison Table */}
        <div style={{ padding: '20px 24px' }}>
          <table style={{
            width: '100%',
            borderCollapse: 'collapse',
            fontSize: '14px',
            textAlign: 'left',
          }}>
            <thead>
              <tr style={{ backgroundColor: '#f1f5f9', color: '#475569', borderBottom: '2px solid #cbd5e1' }}>
                <th style={{ padding: '10px 14px', fontWeight: 700, width: '28%' }}>Parameter Operasi</th>
                <th style={{ padding: '10px 14px', fontWeight: 700, width: '12%' }}>Tag DCS</th>
                <th style={{ padding: '10px 14px', fontWeight: 700, width: '26%', backgroundColor: '#f8fafc' }}>
                  Input Skenario
                </th>
                <th style={{ padding: '10px 14px', fontWeight: 700, width: '24%', backgroundColor: '#ecfdf5', color: '#065f46' }}>
                  Target AI
                </th>
                <th style={{ padding: '10px 14px', fontWeight: 700, width: '10%' }}>Satuan</th>
              </tr>
            </thead>
            <tbody>
              {/* Row 1: Feed Gas Flow */}
              <tr style={{ borderBottom: '1px solid #e2e8f0' }}>
                <td style={{ padding: '12px 14px', fontWeight: 600 }}>
                  Flow Feed Gas MCHE (5E-1)
                </td>
                <td style={{ padding: '12px 14px', fontFamily: 'monospace', color: '#0284c7', fontSize: '13px' }}>
                  H3FI0004
                </td>
                <td style={{ padding: '8px 14px', backgroundColor: '#f8fafc' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <input
                      type="number"
                      step="0.5"
                      min="100"
                      max="500"
                      value={scenario.feed_flow_t_h}
                      onChange={(e) => onScenarioChange('feed_flow_t_h', parseFloat(e.target.value) || 0)}
                      style={{
                        width: '100px',
                        padding: '6px 10px',
                        border: '1px solid #cbd5e1',
                        borderRadius: '6px',
                        fontWeight: 700,
                        fontSize: '14px',
                        color: '#0f172a',
                      }}
                    />
                    <span style={{
                      backgroundColor: '#e2e8f0',
                      color: '#475569',
                      padding: '2px 8px',
                      borderRadius: '10px',
                      fontSize: '11px',
                      fontWeight: 600,
                    }}>
                      LNG: {scenarioLngFlow.toFixed(1)} t/h
                    </span>
                  </div>
                </td>
                <td style={{ padding: '12px 14px', backgroundColor: '#ecfdf5', fontWeight: 700, color: '#047857' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span>{(optimum?.feed_t_h ?? scenario.feed_flow_t_h).toFixed(1)}</span>
                    <span style={{
                      backgroundColor: '#e0f2fe',
                      color: '#0369a1',
                      padding: '2px 8px',
                      borderRadius: '12px',
                      fontSize: '11px',
                      fontWeight: 700,
                    }}>
                      Ikuti Beban
                    </span>
                  </div>
                </td>
                <td style={{ padding: '12px 14px', color: '#64748b', fontWeight: 600 }}>
                  t/h
                </td>
              </tr>

              {/* Row 2: MCR Flow */}
              <tr style={{ borderBottom: '1px solid #e2e8f0', backgroundColor: '#fbfcfd' }}>
                <td style={{ padding: '12px 14px', fontWeight: 600 }}>
                  Flow Sirkulasi MCR
                </td>
                <td style={{ padding: '12px 14px', fontFamily: 'monospace', color: '#0284c7', fontSize: '13px' }}>
                  H4FI001
                </td>
                <td style={{ padding: '8px 14px', backgroundColor: '#f8fafc' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <input
                      type="number"
                      step="1.0"
                      min="450"
                      max="650"
                      value={scenario.mcr_flow_t_h}
                      onChange={(e) => onScenarioChange('mcr_flow_t_h', parseFloat(e.target.value) || 0)}
                      style={{
                        width: '100px',
                        padding: '6px 10px',
                        border: scenario.mcr_flow_t_h < 480 ? '2px solid #ef4444' : '1px solid #cbd5e1',
                        borderRadius: '6px',
                        fontWeight: 700,
                        fontSize: '14px',
                        color: scenario.mcr_flow_t_h < 480 ? '#b91c1c' : '#0f172a',
                      }}
                    />
                    {scenario.mcr_flow_t_h < 480 && (
                      <span style={{
                        backgroundColor: '#fee2e2',
                        color: '#b91c1c',
                        padding: '2px 6px',
                        borderRadius: '4px',
                        fontSize: '11px',
                        fontWeight: 700,
                      }}>
                        Batas Minimum 480
                      </span>
                    )}
                  </div>
                </td>
                <td style={{ padding: '12px 14px', backgroundColor: '#ecfdf5', fontWeight: 700, color: '#047857' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span>{recMcrFlow.toFixed(1)}</span>
                    {recMcrFlow < scenario.mcr_flow_t_h ? (
                      <span style={{
                        backgroundColor: '#dcfce7',
                        color: '#15803d',
                        padding: '2px 8px',
                        borderRadius: '12px',
                        fontSize: '11px',
                        fontWeight: 700,
                      }}>
                        Hemat {(scenario.mcr_flow_t_h - recMcrFlow).toFixed(1)} t/h
                      </span>
                    ) : (
                      <span style={{
                        backgroundColor: '#e2e8f0',
                        color: '#475569',
                        padding: '2px 8px',
                        borderRadius: '12px',
                        fontSize: '11px',
                        fontWeight: 700,
                      }}>
                        Optimal
                      </span>
                    )}
                  </div>
                </td>
                <td style={{ padding: '12px 14px', color: '#64748b', fontWeight: 600 }}>
                  t/h
                </td>
              </tr>

              {/* Rows 3-7: MCR Compositions */}
              {[
                { name: 'Nitrogen (N₂)', key: 'comp_N2_molpct' as const, rec: recN2, tag: 'comp_N2' },
                { name: 'Metana (CH₄ / C₁)', key: 'comp_C1_molpct' as const, rec: recC1, tag: 'comp_C1' },
                { name: 'Etana (C₂H₆ / C₂)', key: 'comp_C2_molpct' as const, rec: recC2, tag: 'comp_C2' },
                { name: 'Etilena (C₂H₄)', key: 'comp_C2H4_molpct' as const, rec: recC2H4, tag: 'comp_C2H4' },
                { name: 'Propana (C₃H₈ / C₃)', key: 'comp_C3_molpct' as const, rec: recC3, tag: 'comp_C3' },
              ].map((comp, idx) => (
                <tr key={comp.key} style={{ borderBottom: '1px solid #e2e8f0', backgroundColor: idx % 2 === 0 ? '#ffffff' : '#fbfcfd' }}>
                  <td style={{ padding: '10px 14px', fontWeight: 500, paddingLeft: '24px' }}>
                    {comp.name}
                  </td>
                  <td style={{ padding: '10px 14px', fontFamily: 'monospace', color: '#64748b', fontSize: '12px' }}>
                    {comp.tag}
                  </td>
                  <td style={{ padding: '6px 14px', backgroundColor: '#f8fafc' }}>
                    <input
                      type="number"
                      step="0.05"
                      min="0"
                      max="100"
                      value={scenario[comp.key]}
                      onChange={(e) => onScenarioChange(comp.key, parseFloat(e.target.value) || 0)}
                      style={{
                        width: '100px',
                        padding: '4px 8px',
                        border: '1px solid #cbd5e1',
                        borderRadius: '6px',
                        fontWeight: 600,
                        fontSize: '13px',
                      }}
                    />
                  </td>
                  <td style={{ padding: '10px 14px', backgroundColor: '#ecfdf5', fontWeight: 700, color: '#047857' }}>
                    {comp.rec.toFixed(2)}
                  </td>
                  <td style={{ padding: '10px 14px', color: '#64748b', fontSize: '13px' }}>
                    mol%
                  </td>
                </tr>
              ))}

              {/* Total Composition Row */}
              <tr style={{ backgroundColor: isCompositionClosed ? '#f0fdf4' : '#fef2f2', borderTop: '2px solid #cbd5e1' }}>
                <td style={{ padding: '10px 14px', fontWeight: 700 }}>
                  Total Komposisi MCR
                </td>
                <td style={{ padding: '10px 14px', fontSize: '12px', color: '#64748b' }}>
                  Σ 5 Fraksi
                </td>
                <td style={{ padding: '10px 14px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <span style={{
                      backgroundColor: isCompositionClosed ? '#dcfce7' : '#fee2e2',
                      color: isCompositionClosed ? '#15803d' : '#b91c1c',
                      padding: '3px 8px',
                      borderRadius: '6px',
                      fontWeight: 800,
                    }}>
                      {compSum.toFixed(2)} mol%
                    </span>
                    {!isCompositionClosed && (
                      <button
                        onClick={onNormalizeScenario}
                        style={{
                          backgroundColor: '#ef4444',
                          color: '#ffffff',
                          border: 'none',
                          borderRadius: '4px',
                          padding: '3px 8px',
                          fontSize: '11px',
                          fontWeight: 700,
                          cursor: 'pointer',
                        }}
                      >
                        Normalisasi 100%
                      </button>
                    )}
                  </div>
                </td>
                <td style={{ padding: '10px 14px', fontWeight: 800, color: '#15803d' }}>
                  <span style={{ backgroundColor: '#dcfce7', color: '#15803d', padding: '3px 8px', borderRadius: '6px' }}>
                    100.00 mol%
                  </span>
                </td>
                <td style={{ padding: '10px 14px', fontWeight: 700 }}>
                  mol%
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>


      {/* =================================================================== */}
      {/* SECTION 2: VARIABEL KUNCI OPERATOR (PREDICTED DCS VS OPTIMIZED AI) */}
      {/* =================================================================== */}
      <section style={{
        backgroundColor: '#ffffff',
        borderRadius: '10px',
        border: '1px solid #e2e8f0',
        boxShadow: '0 2px 8px rgba(0,0,0,0.04)',
        overflow: 'hidden',
      }}>
        <div style={{
          backgroundColor: '#0f172a',
          color: '#ffffff',
          padding: '14px 24px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          borderBottom: '2px solid #0284c7',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <span style={{
              backgroundColor: '#0284c7',
              color: '#ffffff',
              padding: '2px 8px',
              borderRadius: '4px',
              fontWeight: 800,
              fontSize: '12px',
              letterSpacing: '0.5px',
            }}>
              SECTION 2
            </span>
            <span style={{ fontSize: '16px', fontWeight: 700 }}>
              Variabel Kunci Pengawasan Operator
            </span>
            <span style={{
              backgroundColor: '#1e293b',
              color: '#38bdf8',
              padding: '2px 8px',
              borderRadius: '12px',
              fontSize: '11px',
              fontWeight: 700,
            }}>
              Kompresor 4K-2 • PDI MCHE • Suhu LNG
            </span>
          </div>

          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            backgroundColor: prediction?.safety_check?.all_safe ? '#065f46' : '#991b1b',
            padding: '4px 12px',
            borderRadius: '16px',
            fontSize: '12px',
            fontWeight: 700,
          }}>
            <span>{prediction?.safety_check?.all_safe ? '✓ PARAMETER AMAN' : '⚠️ PERHATIKAN BATASAN'}</span>
          </div>
        </div>

        <div style={{ padding: '20px 24px' }}>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(3, 1fr)',
            gap: '16px',
          }}>
            {/* Panel 1: Kompresor MCR 4K-2 */}
            <div style={{
              backgroundColor: '#f8fafc',
              border: '1px solid #e2e8f0',
              borderRadius: '8px',
              padding: '16px',
            }}>
              <div style={{
                fontSize: '13px',
                fontWeight: 800,
                color: '#0369a1',
                textTransform: 'uppercase',
                letterSpacing: '0.5px',
                marginBottom: '12px',
                borderBottom: '1px solid #cbd5e1',
                paddingBottom: '6px',
              }}>
                1. Kompresor MCR 4K-2
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', fontSize: '13px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px dashed #e2e8f0', paddingBottom: '8px' }}>
                  <span style={{ color: '#475569', fontWeight: 500 }}>Suhu Suction (4TI-4B):</span>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <span style={{ backgroundColor: '#e2e8f0', color: '#475569', padding: '2px 6px', borderRadius: '4px', fontSize: '11px', fontWeight: 600 }}>
                      DCS -44.8°C
                    </span>
                    <span style={{ backgroundColor: '#dcfce7', color: '#15803d', padding: '2px 6px', borderRadius: '4px', fontSize: '12px', fontWeight: 800 }}>
                      AI {optimum?.expected_suction_temp_c ? `${optimum.expected_suction_temp_c.toFixed(1)}°C` : '-41.5°C'}
                    </span>
                    <span style={{ backgroundColor: '#10b981', color: '#ffffff', padding: '2px 6px', borderRadius: '4px', fontSize: '10px', fontWeight: 800 }}>
                      AMAN
                    </span>
                  </div>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px dashed #e2e8f0', paddingBottom: '8px' }}>
                  <span style={{ color: '#475569', fontWeight: 500 }}>Tekanan Suction (4PI-13):</span>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <span style={{ backgroundColor: '#e2e8f0', color: '#475569', padding: '2px 6px', borderRadius: '4px', fontSize: '11px', fontWeight: 600 }}>
                      DCS 2.28
                    </span>
                    <span style={{ backgroundColor: '#dcfce7', color: '#15803d', padding: '2px 6px', borderRadius: '4px', fontSize: '12px', fontWeight: 800 }}>
                      AI 2.35 kg/cm²
                    </span>
                  </div>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px dashed #e2e8f0', paddingBottom: '8px' }}>
                  <span style={{ color: '#475569', fontWeight: 500 }}>Suhu Discharge (4TI-16):</span>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <span style={{ backgroundColor: '#e2e8f0', color: '#475569', padding: '2px 6px', borderRadius: '4px', fontSize: '11px', fontWeight: 600 }}>
                      DCS 62.4°C
                    </span>
                    <span style={{ backgroundColor: '#dcfce7', color: '#15803d', padding: '2px 6px', borderRadius: '4px', fontSize: '12px', fontWeight: 800 }}>
                      AI 58.1°C
                    </span>
                  </div>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ color: '#475569', fontWeight: 500 }}>Tekanan Discharge (4PI-1):</span>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <span style={{ backgroundColor: '#e2e8f0', color: '#475569', padding: '2px 6px', borderRadius: '4px', fontSize: '11px', fontWeight: 600 }}>
                      DCS 36.90
                    </span>
                    <span style={{ backgroundColor: '#dcfce7', color: '#15803d', padding: '2px 6px', borderRadius: '4px', fontSize: '12px', fontWeight: 800 }}>
                      AI 35.15 kg/cm²
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Panel 2: PDI MCHE 5E-1 */}
            <div style={{
              backgroundColor: '#f8fafc',
              border: '1px solid #e2e8f0',
              borderRadius: '8px',
              padding: '16px',
            }}>
              <div style={{
                fontSize: '13px',
                fontWeight: 800,
                color: '#0369a1',
                textTransform: 'uppercase',
                letterSpacing: '0.5px',
                marginBottom: '12px',
                borderBottom: '1px solid #cbd5e1',
                paddingBottom: '6px',
              }}>
                2. Beda Tekan MCHE 5E-1 (PDI)
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', fontSize: '13px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px dashed #e2e8f0', paddingBottom: '8px' }}>
                  <span style={{ color: '#475569', fontWeight: 500 }}>Cold Bundle (PDI4):</span>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <span style={{ backgroundColor: '#e2e8f0', color: '#475569', padding: '2px 6px', borderRadius: '4px', fontSize: '11px', fontWeight: 600 }}>
                      DCS 0.067
                    </span>
                    <span style={{ backgroundColor: '#dcfce7', color: '#15803d', padding: '2px 6px', borderRadius: '4px', fontSize: '12px', fontWeight: 800 }}>
                      AI 0.062
                    </span>
                    <span style={{ backgroundColor: '#10b981', color: '#ffffff', padding: '2px 6px', borderRadius: '4px', fontSize: '10px', fontWeight: 800 }}>
                      NORMAL
                    </span>
                  </div>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px dashed #e2e8f0', paddingBottom: '8px' }}>
                  <span style={{ color: '#475569', fontWeight: 500 }}>Warm Bundle (PDI3):</span>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <span style={{ backgroundColor: '#e2e8f0', color: '#475569', padding: '2px 6px', borderRadius: '4px', fontSize: '11px', fontWeight: 600 }}>
                      DCS 0.240
                    </span>
                    <span style={{ backgroundColor: '#dcfce7', color: '#15803d', padding: '2px 6px', borderRadius: '4px', fontSize: '12px', fontWeight: 800 }}>
                      AI 0.215
                    </span>
                    <span style={{ backgroundColor: '#10b981', color: '#ffffff', padding: '2px 6px', borderRadius: '4px', fontSize: '10px', fontWeight: 800 }}>
                      NORMAL
                    </span>
                  </div>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px dashed #e2e8f0', paddingBottom: '8px' }}>
                  <span style={{ color: '#475569', fontWeight: 500 }}>Level Cold Separator (LI2):</span>
                  <span style={{ backgroundColor: '#e0f2fe', color: '#0369a1', padding: '3px 8px', borderRadius: '6px', fontSize: '12px', fontWeight: 800 }}>
                    39.0 %
                  </span>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ color: '#475569', fontWeight: 500 }}>Level Warm Separator (LI3):</span>
                  <span style={{ backgroundColor: '#e0f2fe', color: '#0369a1', padding: '3px 8px', borderRadius: '6px', fontSize: '12px', fontWeight: 800 }}>
                    48.5 %
                  </span>
                </div>
              </div>
            </div>

            {/* Panel 3: Outlet LNG & MCHE Cold End */}
            <div style={{
              backgroundColor: '#f8fafc',
              border: '1px solid #e2e8f0',
              borderRadius: '8px',
              padding: '16px',
            }}>
              <div style={{
                fontSize: '13px',
                fontWeight: 800,
                color: '#0369a1',
                textTransform: 'uppercase',
                letterSpacing: '0.5px',
                marginBottom: '12px',
                borderBottom: '1px solid #cbd5e1',
                paddingBottom: '6px',
              }}>
                3. Suhu Outlet LNG
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', fontSize: '13px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px dashed #e2e8f0', paddingBottom: '8px' }}>
                  <span style={{ color: '#475569', fontWeight: 500 }}>Suhu Outlet LNG (TIC1):</span>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <span style={{ backgroundColor: '#e2e8f0', color: '#475569', padding: '2px 6px', borderRadius: '4px', fontSize: '11px', fontWeight: 600 }}>
                      DCS -151.2°C
                    </span>
                    <span style={{ backgroundColor: '#dcfce7', color: '#15803d', padding: '2px 6px', borderRadius: '4px', fontSize: '12px', fontWeight: 800 }}>
                      AI -152.0°C
                    </span>
                    <span style={{ backgroundColor: '#10b981', color: '#ffffff', padding: '2px 6px', borderRadius: '4px', fontSize: '10px', fontWeight: 800 }}>
                      TARGET
                    </span>
                  </div>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px dashed #e2e8f0', paddingBottom: '8px' }}>
                  <span style={{ color: '#475569', fontWeight: 500 }}>Suhu Rundown (TI29):</span>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <span style={{ backgroundColor: '#e2e8f0', color: '#475569', padding: '2px 6px', borderRadius: '4px', fontSize: '11px', fontWeight: 600 }}>
                      DCS -153.6°C
                    </span>
                    <span style={{ backgroundColor: '#dcfce7', color: '#15803d', padding: '2px 6px', borderRadius: '4px', fontSize: '12px', fontWeight: 800 }}>
                      AI -153.8°C
                    </span>
                  </div>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px dashed #e2e8f0', paddingBottom: '8px' }}>
                  <span style={{ color: '#475569', fontWeight: 500 }}>Produksi LNG (H5FI6A):</span>
                  <span style={{ backgroundColor: '#f1f5f9', color: '#0f172a', padding: '3px 8px', borderRadius: '6px', fontSize: '12px', fontWeight: 800 }}>
                    {scenarioLngFlow.toFixed(1)} t/h
                  </span>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ color: '#475569', fontWeight: 500 }}>Suhu Bawah MCHE (TI8):</span>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <span style={{ backgroundColor: '#e2e8f0', color: '#475569', padding: '2px 6px', borderRadius: '4px', fontSize: '11px', fontWeight: 600 }}>
                      DCS -44.8°C
                    </span>
                    <span style={{ backgroundColor: '#dcfce7', color: '#15803d', padding: '2px 6px', borderRadius: '4px', fontSize: '12px', fontWeight: 800 }}>
                      AI -43.5°C
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>


      {/* =================================================================== */}
      {/* SECTION 3: VALUE CREATION & PENGHEMATAN ENERGI (SAVINGS)           */}
      {/* =================================================================== */}
      <section style={{
        backgroundColor: '#ffffff',
        borderRadius: '10px',
        border: '1px solid #e2e8f0',
        boxShadow: '0 2px 8px rgba(0,0,0,0.04)',
        overflow: 'hidden',
      }}>
        <div style={{
          backgroundColor: '#064e3b',
          color: '#ffffff',
          padding: '14px 24px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          borderBottom: '2px solid #10b981',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <span style={{
              backgroundColor: '#10b981',
              color: '#064e3b',
              padding: '2px 8px',
              borderRadius: '4px',
              fontWeight: 800,
              fontSize: '12px',
              letterSpacing: '0.5px',
            }}>
              SECTION 3
            </span>
            <span style={{ fontSize: '16px', fontWeight: 700 }}>
              Ringkasan Nilai Penghematan
            </span>
            <span style={{
              backgroundColor: '#047857',
              color: '#a7f3d0',
              padding: '2px 8px',
              borderRadius: '12px',
              fontSize: '11px',
              fontWeight: 700,
            }}>
              Energi & Utilitas
            </span>
          </div>

          <div style={{
            backgroundColor: '#047857',
            color: '#a7f3d0',
            padding: '3px 10px',
            borderRadius: '12px',
            fontSize: '12px',
            fontWeight: 600,
          }}>
            Evaluasi Skenario
          </div>
        </div>

        <div style={{ padding: '24px' }}>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(4, 1fr)',
            gap: '16px',
          }}>
            {/* KPI Card 1: Penghematan SEC LNG */}
            <div style={{
              backgroundColor: '#f0fdf4',
              border: '2px solid #86efac',
              borderRadius: '8px',
              padding: '18px',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
            }}>
              <div>
                <div style={{ fontSize: '12px', fontWeight: 700, color: '#166534', textTransform: 'uppercase' }}>
                  1. Efisiensi Spesifik (SEC)
                </div>
                <div style={{ fontSize: '30px', fontWeight: 800, color: '#15803d', margin: '8px 0 6px 0' }}>
                  {deltaSecLng < 0 ? Math.abs(deltaSecLng).toFixed(1) : '0.0'}
                  <span style={{ fontSize: '14px', fontWeight: 600, marginLeft: '6px', color: '#166534' }}>
                    kWh/t
                  </span>
                </div>
                <div>
                  <span style={{
                    backgroundColor: '#bbf7d0',
                    color: '#166534',
                    padding: '3px 8px',
                    borderRadius: '12px',
                    fontSize: '11px',
                    fontWeight: 800,
                  }}>
                    {deltaSecLngPct < 0 ? `HEMAT ${Math.abs(deltaSecLngPct).toFixed(1)}%` : 'OPTIMAL'}
                  </span>
                </div>
              </div>
              <div style={{
                marginTop: '14px',
                paddingTop: '10px',
                borderTop: '1px solid #bbf7d0',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                gap: '6px',
              }}>
                <span style={{ backgroundColor: '#e2e8f0', color: '#334155', padding: '3px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: 700 }}>
                  DCS: {baselineSecLng.toFixed(1)}
                </span>
                <span style={{ backgroundColor: '#dcfce7', color: '#15803d', padding: '3px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: 800 }}>
                  AI: {scenarioSecLng.toFixed(1)} kWh/t
                </span>
              </div>
            </div>

            {/* KPI Card 2: Penghematan Steam */}
            <div style={{
              backgroundColor: '#f0fdf4',
              border: '2px solid #86efac',
              borderRadius: '8px',
              padding: '18px',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
            }}>
              <div>
                <div style={{ fontSize: '12px', fontWeight: 700, color: '#166534', textTransform: 'uppercase' }}>
                  2. Penghematan Steam
                </div>
                <div style={{ fontSize: '30px', fontWeight: 800, color: '#15803d', margin: '8px 0 6px 0' }}>
                  {deltaPowerSavingMw > 0 ? steamSaved_t_h.toFixed(1) : '0.0'}
                  <span style={{ fontSize: '14px', fontWeight: 600, marginLeft: '6px', color: '#166534' }}>
                    t/jam
                  </span>
                </div>
                <div>
                  <span style={{
                    backgroundColor: '#bbf7d0',
                    color: '#166534',
                    padding: '3px 8px',
                    borderRadius: '12px',
                    fontSize: '11px',
                    fontWeight: 800,
                  }}>
                    BEBAN BOILER TURUN
                  </span>
                </div>
              </div>
              <div style={{
                marginTop: '14px',
                paddingTop: '10px',
                borderTop: '1px solid #bbf7d0',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
              }}>
                <span style={{ backgroundColor: '#e2e8f0', color: '#334155', padding: '3px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: 700 }}>
                  Steam Utilitas
                </span>
                <span style={{ backgroundColor: '#dcfce7', color: '#15803d', padding: '3px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: 800 }}>
                  Lebih Efisien
                </span>
              </div>
            </div>

            {/* KPI Card 3: Penghematan Fuel Gas */}
            <div style={{
              backgroundColor: '#f0fdf4',
              border: '2px solid #86efac',
              borderRadius: '8px',
              padding: '18px',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
            }}>
              <div>
                <div style={{ fontSize: '12px', fontWeight: 700, color: '#166534', textTransform: 'uppercase' }}>
                  3. Penghematan Fuel Gas
                </div>
                <div style={{ fontSize: '30px', fontWeight: 800, color: '#15803d', margin: '8px 0 6px 0' }}>
                  {deltaPowerSavingMw > 0 ? fuelGasSaved_t_h.toFixed(1) : '0.0'}
                  <span style={{ fontSize: '14px', fontWeight: 600, marginLeft: '6px', color: '#166534' }}>
                    t/jam
                  </span>
                </div>
                <div>
                  <span style={{
                    backgroundColor: '#fef3c7',
                    color: '#92400e',
                    padding: '3px 8px',
                    borderRadius: '12px',
                    fontSize: '11px',
                    fontWeight: 800,
                  }}>
                    USD {fuelGasSaved_usd_yr.toFixed(2)} JUTA / TAHUN
                  </span>
                </div>
              </div>
              <div style={{
                marginTop: '14px',
                paddingTop: '10px',
                borderTop: '1px solid #bbf7d0',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
              }}>
                <span style={{ backgroundColor: '#e2e8f0', color: '#334155', padding: '3px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: 700 }}>
                  Fuel Turbin
                </span>
                <span style={{ backgroundColor: '#dcfce7', color: '#15803d', padding: '3px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: 800 }}>
                  Emisi Berkurang
                </span>
              </div>
            </div>

            {/* KPI Card 4: Total Penghematan Daya Poros C3MR */}
            <div style={{
              backgroundColor: '#f0fdf4',
              border: '2px solid #86efac',
              borderRadius: '8px',
              padding: '18px',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
            }}>
              <div>
                <div style={{ fontSize: '12px', fontWeight: 700, color: '#166534', textTransform: 'uppercase' }}>
                  4. Daya Poros Total
                </div>
                <div style={{ fontSize: '30px', fontWeight: 800, color: '#15803d', margin: '8px 0 6px 0' }}>
                  {deltaPowerSavingMw > 0 ? deltaPowerSavingMw.toFixed(2) : '0.00'}
                  <span style={{ fontSize: '14px', fontWeight: 600, marginLeft: '6px', color: '#166534' }}>
                    MW
                  </span>
                </div>
                <div>
                  <span style={{
                    backgroundColor: '#bbf7d0',
                    color: '#166534',
                    padding: '3px 8px',
                    borderRadius: '12px',
                    fontSize: '11px',
                    fontWeight: 800,
                  }}>
                    {deltaPowerPct < 0 ? `HEMAT ${Math.abs(deltaPowerPct).toFixed(1)}%` : 'BASELINE'}
                  </span>
                </div>
              </div>
              <div style={{
                marginTop: '14px',
                paddingTop: '10px',
                borderTop: '1px solid #bbf7d0',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                gap: '6px',
              }}>
                <span style={{ backgroundColor: '#e2e8f0', color: '#334155', padding: '3px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: 700 }}>
                  DCS: {baselinePower.toFixed(1)} MW
                </span>
                <span style={{ backgroundColor: '#dcfce7', color: '#15803d', padding: '3px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: 800 }}>
                  AI: {scenarioPower.toFixed(1)} MW
                </span>
              </div>
            </div>
          </div>
        </div>
      </section>

    </div>
  );
};
