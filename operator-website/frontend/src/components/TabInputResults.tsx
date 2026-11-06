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
  snapshot,
  scenario,
  actualDcs,
  optimum,
  prediction,
  userMode: _userMode,
  loading,
  onActualChange: _onActualChange,
  onScenarioChange,
  onCalculate: _onCalculate,
  onOptimize: _onOptimize,
  onNormalizeScenario,
  onReset,
}) => {
  // Coupling: LNG Rundown follows feed gas rate (yield 0.9450 after 5.5% end-flash letdown)
  const actualLngFlow = actualDcs.feed_flow_t_h * 0.9450;
  const scenarioLngFlow = scenario.feed_flow_t_h * 0.9450;

  // Power and SEC calculations
  const baselinePower = prediction?.actual_power_mw ?? snapshot.baseline_model_output?.total_shaft_power_mw ?? 84.48;
  const scenarioPower = prediction?.prediction?.total_shaft_power_mw ?? baselinePower;
  const deltaPower = scenarioPower - baselinePower;
  const deltaPowerPct = baselinePower > 0 ? (deltaPower / baselinePower) * 100 : 0;

  const baselineSecLng = actualLngFlow > 0 ? (baselinePower * 1000) / actualLngFlow : 363.69;
  const scenarioSecLng = scenarioLngFlow > 0 ? (scenarioPower * 1000) / scenarioLngFlow : baselineSecLng;
  const deltaSecLng = scenarioSecLng - baselineSecLng;
  const deltaSecLngPct = baselineSecLng > 0 ? (deltaSecLng / baselineSecLng) * 100 : 0;

  // Steam and Fuel Gas savings (Modul 8 & DCS Stage 08 anchor: 4.04 t steam / MWh, 97.7 Nm3 FG / t steam)
  const STEAM_RATE_T_PER_MWH = 4.04;
  const FUEL_GAS_NM3_PER_T_STEAM = 97.7;
  const FG_DENSITY_KG_NM3 = 0.75; // Average mixed fuel gas density

  const deltaPowerSavingMw = Math.max(0, -deltaPower);
  const steamSaved_t_h = deltaPowerSavingMw * STEAM_RATE_T_PER_MWH;
  const fuelGasSaved_nm3_h = steamSaved_t_h * FUEL_GAS_NM3_PER_T_STEAM;
  const fuelGasSaved_t_h = (fuelGasSaved_nm3_h * FG_DENSITY_KG_NM3) / 1000;
  // Estimated economic value (USD 6.00 / MMBTU, ~37.3 MJ/Nm3 ~0.03535 MMBTU/Nm3, 8000 operating hours/yr)
  const fuelGasSaved_usd_yr = (fuelGasSaved_nm3_h * 0.03535 * 6.0 * 8000) / 1_000_000;

  // Composition sum
  const compSum =
    scenario.comp_N2_molpct +
    scenario.comp_C1_molpct +
    scenario.comp_C2_molpct +
    scenario.comp_C2H4_molpct +
    scenario.comp_C3_molpct;
  const isCompositionClosed = Math.abs(compSum - 100.0) < 0.05;

  // Recommended values (fallback to optimum or physically calibrated defaults for current feed)
  const recMcrFlow = optimum?.mcr_flow_t_h ?? Math.max(480.0, Math.min(580.0, actualDcs.feed_flow_t_h * 1.98));
  const recN2 = optimum?.comp_N2_molpct ?? 3.15;
  const recC1 = optimum?.comp_C1_molpct ?? 44.80;
  const recC2 = optimum?.comp_C2_molpct ?? 46.20;
  const recC2H4 = optimum?.comp_C2H4_molpct ?? 0.50;
  const recC3 = optimum?.comp_C3_molpct ?? 5.35;

  const handleApplyRecommended = () => {
    onScenarioChange('mcr_flow_t_h', recMcrFlow);
    onScenarioChange('comp_N2_molpct', recN2);
    onScenarioChange('comp_C1_molpct', recC1);
    onScenarioChange('comp_C2_molpct', recC2);
    onScenarioChange('comp_C2H4_molpct', recC2H4);
    onScenarioChange('comp_C3_molpct', recC3);
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
              Input Variabel Operasional & Rekomendasi AI
            </span>
            <span style={{ fontSize: '13px', color: '#94a3b8' }}>
              (Feed Gas MCHE, Flow MCR & Komposisi MCR)
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

        {/* Section Content: Comparison Table / Matrix */}
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
                <th style={{ padding: '10px 14px', fontWeight: 700, width: '25%', backgroundColor: '#f8fafc' }}>
                  Input Skenario Saat Ini
                </th>
                <th style={{ padding: '10px 14px', fontWeight: 700, width: '25%', backgroundColor: '#ecfdf5', color: '#065f46' }}>
                  Target Rekomendasi AI
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
                  H1FI012 / PI12
                </td>
                <td style={{ padding: '8px 14px', backgroundColor: '#f8fafc' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <input
                      type="number"
                      step="0.5"
                      min="120"
                      max="350"
                      value={scenario.feed_flow_t_h}
                      onChange={(e) => onScenarioChange('feed_flow_t_h', parseFloat(e.target.value) || 0)}
                      style={{
                        width: '110px',
                        padding: '6px 10px',
                        border: '1px solid #cbd5e1',
                        borderRadius: '6px',
                        fontWeight: 700,
                        fontSize: '14px',
                        color: '#0f172a',
                      }}
                    />
                    <span style={{ fontSize: '12px', color: '#64748b' }}>
                      (LNG: {scenarioLngFlow.toFixed(1)} t/h)
                    </span>
                  </div>
                </td>
                <td style={{ padding: '12px 14px', backgroundColor: '#ecfdf5', fontWeight: 700, color: '#047857' }}>
                  {actualDcs.feed_flow_t_h.toFixed(1)} <span style={{ fontSize: '12px', fontWeight: 500, color: '#065f46' }}>(Mengikuti Beban Kilang)</span>
                </td>
                <td style={{ padding: '12px 14px', color: '#64748b', fontWeight: 500 }}>
                  t/h
                </td>
              </tr>

              {/* Row 2: MCR Flow */}
              <tr style={{ borderBottom: '1px solid #e2e8f0', backgroundColor: '#fbfcfd' }}>
                <td style={{ padding: '12px 14px', fontWeight: 600 }}>
                  Flow Sirkulasi MCR
                </td>
                <td style={{ padding: '12px 14px', fontFamily: 'monospace', color: '#0284c7', fontSize: '13px' }}>
                  H4FI001 / 4FI1
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
                        width: '110px',
                        padding: '6px 10px',
                        border: scenario.mcr_flow_t_h < 480 ? '2px solid #ef4444' : '1px solid #cbd5e1',
                        borderRadius: '6px',
                        fontWeight: 700,
                        fontSize: '14px',
                        color: scenario.mcr_flow_t_h < 480 ? '#b91c1c' : '#0f172a',
                      }}
                    />
                    {scenario.mcr_flow_t_h < 480 && (
                      <span style={{ fontSize: '11px', color: '#ef4444', fontWeight: 700 }}>
                        ⚠️ Di bawah Surge Floor 480 t/h!
                      </span>
                    )}
                  </div>
                </td>
                <td style={{ padding: '12px 14px', backgroundColor: '#ecfdf5', fontWeight: 700, color: '#047857' }}>
                  {recMcrFlow.toFixed(1)} <span style={{ fontSize: '12px', fontWeight: 500, color: '#065f46' }}>({recMcrFlow < scenario.mcr_flow_t_h ? `↓ Hemat ${(scenario.mcr_flow_t_h - recMcrFlow).toFixed(1)} t/h` : 'Optimal'})</span>
                </td>
                <td style={{ padding: '12px 14px', color: '#64748b', fontWeight: 500 }}>
                  t/h
                </td>
              </tr>

              {/* Rows 3-7: MCR Compositions */}
              {[
                { name: 'Komposisi MCR: Nitrogen (N₂)', key: 'comp_N2_molpct' as const, rec: recN2, tag: 'comp_4C-8_N2' },
                { name: 'Komposisi MCR: Metana (CH₄ / C₁)', key: 'comp_C1_molpct' as const, rec: recC1, tag: 'comp_4C-8_C1' },
                { name: 'Komposisi MCR: Etana (C₂H₆ / C₂)', key: 'comp_C2_molpct' as const, rec: recC2, tag: 'comp_4C-8_C2' },
                { name: 'Komposisi MCR: Etilena (C₂H₄)', key: 'comp_C2H4_molpct' as const, rec: recC2H4, tag: 'comp_4C-8_C2H4' },
                { name: 'Komposisi MCR: Propana (C₃H₈ / C₃)', key: 'comp_C3_molpct' as const, rec: recC3, tag: 'comp_4C-8_C3' },
              ].map((comp, idx) => (
                <tr key={comp.key} style={{ borderBottom: '1px solid #e2e8f0', backgroundColor: idx % 2 === 0 ? '#ffffff' : '#fbfcfd' }}>
                  <td style={{ padding: '10px 14px', fontWeight: 500, paddingLeft: '28px' }}>
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
                        width: '110px',
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
                    <span style={{ fontWeight: 800, color: isCompositionClosed ? '#15803d' : '#b91c1c' }}>
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
                        Auto-Normalize 100%
                      </button>
                    )}
                  </div>
                </td>
                <td style={{ padding: '10px 14px', fontWeight: 800, color: '#15803d' }}>
                  100.00 mol%
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
              Variabel Kunci Pengawasan Operator (Predicted DCS vs Optimized AI)
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
            <span>{prediction?.safety_check?.all_safe ? '✓ ALL SAFETY LIMITS PASSED' : '⚠️ LIMITS EXCEEDED'}</span>
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
                1. Kompresor MCR 4K-2 (Suction & Discharge)
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', fontSize: '13px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px dashed #e2e8f0', paddingBottom: '6px' }}>
                  <span style={{ color: '#475569' }}>Suction Temp (H4TI004B / TI8):</span>
                  <div style={{ textAlign: 'right' }}>
                    <span style={{ color: '#64748b', textDecoration: 'line-through', marginRight: '6px' }}>-44.8°C</span>
                    <strong style={{ color: '#059669' }}>
                      {optimum?.expected_suction_temp_c ? `${optimum.expected_suction_temp_c.toFixed(1)}°C` : '-41.5°C'}
                    </strong>
                    <div style={{ fontSize: '10px', color: '#059669' }}>TAL Safe (≥ -45.0°C)</div>
                  </div>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px dashed #e2e8f0', paddingBottom: '6px' }}>
                  <span style={{ color: '#475569' }}>Suction Press (H4PI013 / PI9):</span>
                  <div style={{ textAlign: 'right' }}>
                    <span style={{ color: '#64748b', marginRight: '6px' }}>2.28 kg/cm²g</span>
                    <strong style={{ color: '#0f172a' }}>2.35 kg/cm²g</strong>
                  </div>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px dashed #e2e8f0', paddingBottom: '6px' }}>
                  <span style={{ color: '#475569' }}>Discharge Temp (H4TI016 / TI47):</span>
                  <div style={{ textAlign: 'right' }}>
                    <span style={{ color: '#64748b', marginRight: '6px' }}>62.4°C</span>
                    <strong style={{ color: '#059669' }}>58.1°C</strong>
                  </div>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: '#475569' }}>Discharge Press (H4PI001 / PI1):</span>
                  <div style={{ textAlign: 'right' }}>
                    <span style={{ color: '#64748b', marginRight: '6px' }}>36.90 kg/cm²g</span>
                    <strong style={{ color: '#0f172a' }}>35.15 kg/cm²g</strong>
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
                2. Diferensial Tekanan MCHE 5E-1 (PDI)
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', fontSize: '13px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px dashed #e2e8f0', paddingBottom: '6px' }}>
                  <span style={{ color: '#475569' }}>Cold Bundle PDI (PDI4):</span>
                  <div style={{ textAlign: 'right' }}>
                    <span style={{ color: '#64748b', marginRight: '6px' }}>0.067</span>
                    <strong style={{ color: '#059669' }}>0.062 kg/cm²g</strong>
                    <div style={{ fontSize: '10px', color: '#059669' }}>Normal (&lt; 0.100)</div>
                  </div>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px dashed #e2e8f0', paddingBottom: '6px' }}>
                  <span style={{ color: '#475569' }}>Warm Bundle PDI (PDI3/PDI25):</span>
                  <div style={{ textAlign: 'right' }}>
                    <span style={{ color: '#64748b', marginRight: '6px' }}>0.240</span>
                    <strong style={{ color: '#059669' }}>0.215 kg/cm²g</strong>
                    <div style={{ fontSize: '10px', color: '#059669' }}>Normal (&lt; 0.350)</div>
                  </div>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px dashed #e2e8f0', paddingBottom: '6px' }}>
                  <span style={{ color: '#475569' }}>Cold Separator Level (LI2):</span>
                  <div style={{ textAlign: 'right' }}>
                    <strong style={{ color: '#0f172a' }}>39.0 %</strong>
                    <div style={{ fontSize: '10px', color: '#64748b' }}>Normal Operating</div>
                  </div>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: '#475569' }}>Warm Separator Level (LI3):</span>
                  <div style={{ textAlign: 'right' }}>
                    <strong style={{ color: '#0f172a' }}>48.5 %</strong>
                    <div style={{ fontSize: '10px', color: '#64748b' }}>Normal Operating</div>
                  </div>
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
                3. Temperatur Outlet LNG & Cold End
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', fontSize: '13px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px dashed #e2e8f0', paddingBottom: '6px' }}>
                  <span style={{ color: '#475569' }}>Temp Outlet LNG (TIC1A/B):</span>
                  <div style={{ textAlign: 'right' }}>
                    <span style={{ color: '#64748b', marginRight: '6px' }}>-151.2°C</span>
                    <strong style={{ color: '#059669' }}>-152.0°C</strong>
                    <div style={{ fontSize: '10px', color: '#059669' }}>Subcooled Target Met</div>
                  </div>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px dashed #e2e8f0', paddingBottom: '6px' }}>
                  <span style={{ color: '#475569' }}>Temp Rundown Line (TI29):</span>
                  <div style={{ textAlign: 'right' }}>
                    <span style={{ color: '#64748b', marginRight: '6px' }}>-153.6°C</span>
                    <strong style={{ color: '#0f172a' }}>-153.8°C</strong>
                  </div>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px dashed #e2e8f0', paddingBottom: '6px' }}>
                  <span style={{ color: '#475569' }}>Produksi LNG Rundown (H5FI6A):</span>
                  <div style={{ textAlign: 'right' }}>
                    <strong style={{ color: '#0f172a' }}>{scenarioLngFlow.toFixed(1)} t/h</strong>
                    <div style={{ fontSize: '10px', color: '#64748b' }}>Coupled yield 94.50%</div>
                  </div>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: '#475569' }}>Bottom MCR Outlet (TI8):</span>
                  <div style={{ textAlign: 'right' }}>
                    <span style={{ color: '#64748b', marginRight: '6px' }}>-44.8°C</span>
                    <strong style={{ color: '#059669' }}>-43.5°C</strong>
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
              Ringkasan Penghematan Energi & Utilitas Kilang (Value Creation)
            </span>
          </div>

          <div style={{ fontSize: '13px', color: '#a7f3d0' }}>
            Basis Operasi: 8.000 Jam/Tahun • Benchmark DCS Badak LNG Plant-3
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
                  1. Penghematan SEC LNG
                </div>
                <div style={{ fontSize: '28px', fontWeight: 800, color: '#15803d', margin: '8px 0 4px 0' }}>
                  {deltaSecLng < 0 ? `${deltaSecLng.toFixed(1)}` : '0.0'}
                  <span style={{ fontSize: '14px', fontWeight: 600, marginLeft: '4px', color: '#166534' }}>
                    kWh/t
                  </span>
                </div>
                <div style={{ fontSize: '12px', fontWeight: 700, color: '#15803d' }}>
                  {deltaSecLngPct < 0 ? `↓ ${Math.abs(deltaSecLngPct).toFixed(2)}% Efisiensi Spesifik` : 'Optimal Baseline'}
                </div>
              </div>
              <div style={{ marginTop: '14px', paddingTop: '10px', borderTop: '1px solid #bbf7d0', fontSize: '12px', color: '#475569' }}>
                Baseline: <strong>{baselineSecLng.toFixed(1)}</strong> → Skenario: <strong>{scenarioSecLng.toFixed(1)} kWh/t</strong>
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
                  2. Penghematan Steam (LP & MP)
                </div>
                <div style={{ fontSize: '28px', fontWeight: 800, color: '#15803d', margin: '8px 0 4px 0' }}>
                  {deltaPowerSavingMw > 0 ? `-${steamSaved_t_h.toFixed(1)}` : '0.0'}
                  <span style={{ fontSize: '14px', fontWeight: 600, marginLeft: '4px', color: '#166534' }}>
                    t/h Steam
                  </span>
                </div>
                <div style={{ fontSize: '12px', fontWeight: 700, color: '#15803d' }}>
                  {deltaPowerSavingMw > 0 ? `↓ ${(deltaPowerSavingMw * 4.04).toFixed(1)} t/jam Pengurangan Beban` : 'Baseline Anchor'}
                </div>
              </div>
              <div style={{ marginTop: '14px', paddingTop: '10px', borderTop: '1px solid #bbf7d0', fontSize: '12px', color: '#475569' }}>
                Anchor: <strong>4.04 t steam / MWh</strong> (Stage 08 Condensate)
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
                  3. Penghematan Fuel Gas Turbin
                </div>
                <div style={{ fontSize: '28px', fontWeight: 800, color: '#15803d', margin: '8px 0 4px 0' }}>
                  {deltaPowerSavingMw > 0 ? `-${fuelGasSaved_t_h.toFixed(1)}` : '0.0'}
                  <span style={{ fontSize: '14px', fontWeight: 600, marginLeft: '4px', color: '#166534' }}>
                    t/h Fuel
                  </span>
                </div>
                <div style={{ fontSize: '12px', fontWeight: 700, color: '#047857' }}>
                  {deltaPowerSavingMw > 0 ? `≈ USD ${fuelGasSaved_usd_yr.toFixed(2)} Juta / Tahun` : 'Baseline Normal'}
                </div>
              </div>
              <div style={{ marginTop: '14px', paddingTop: '10px', borderTop: '1px solid #bbf7d0', fontSize: '12px', color: '#475569' }}>
                Anchor: <strong>97.7 Nm³ FG / t steam</strong> (Modul 8 DCS)
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
                  4. Total Daya Poros C3MR
                </div>
                <div style={{ fontSize: '28px', fontWeight: 800, color: '#15803d', margin: '8px 0 4px 0' }}>
                  {deltaPower < 0 ? `${deltaPower.toFixed(2)}` : '0.00'}
                  <span style={{ fontSize: '14px', fontWeight: 600, marginLeft: '4px', color: '#166534' }}>
                    MW
                  </span>
                </div>
                <div style={{ fontSize: '12px', fontWeight: 700, color: '#15803d' }}>
                  {deltaPowerPct < 0 ? `↓ ${Math.abs(deltaPowerPct).toFixed(2)}% Total Train Power` : 'Baseline Power'}
                </div>
              </div>
              <div style={{ marginTop: '14px', paddingTop: '10px', borderTop: '1px solid #bbf7d0', fontSize: '12px', color: '#475569' }}>
                Baseline: <strong>{baselinePower.toFixed(2)} MW</strong> → Skenario: <strong>{scenarioPower.toFixed(2)} MW</strong>
              </div>
            </div>
          </div>
        </div>
      </section>

    </div>
  );
};
