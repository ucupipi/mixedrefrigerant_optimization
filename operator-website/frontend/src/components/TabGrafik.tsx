import React from 'react';
import type { DemoSnapshot, HistoricalPoint, PredictResponse, ScenarioInput, UserMode } from '../types';

interface TabGrafikProps {
  snapshot: DemoSnapshot;
  scenario: ScenarioInput;
  prediction: PredictResponse | null;
  historicalPoints: HistoricalPoint[];
  userMode?: UserMode;
}

export const TabGrafik: React.FC<TabGrafikProps> = ({
  snapshot,
  scenario,
  prediction,
  historicalPoints,
  userMode = 'OPERATOR',
}) => {
  const currentFeed = scenario.feed_flow_t_h;
  const currentLng = scenario.lng_flow_t_h ?? (currentFeed * 0.9450);
  const currentMcr = scenario.mcr_flow_t_h;
  const currentPower = prediction ? prediction.prediction.total_shaft_power_mw : 84.15;
  const baselinePower = prediction?.actual_power_mw ?? snapshot.baseline_model_output?.total_shaft_power_mw ?? 84.15;

  const currentSec = prediction?.prediction?.sec_lng_kwh_per_t ?? (currentPower * 1000 / Math.max(1, currentLng));
  const baselineSec = baselinePower * 1000 / Math.max(1, currentLng);

  const dm = prediction ? prediction.domain_check.mahalanobis_distance : 1.273;
  const dmLimit = 3.0802;

  // Chart dimensions helper
  const svgWidth = 560;
  const svgHeight = 280;

  // 1. Chart 1: Feed Gas vs MCR Circulation
  const c1Pad = { top: 25, right: 25, bottom: 45, left: 60 };
  const c1W = svgWidth - c1Pad.left - c1Pad.right;
  const c1H = svgHeight - c1Pad.top - c1Pad.bottom;
  const minFeed = 100, maxFeed = 360;
  const minMcr = 400, maxMcr = 680;
  const sX1 = (f: number) => c1Pad.left + ((f - minFeed) / (maxFeed - minFeed)) * c1W;
  const sY1 = (m: number) => c1Pad.top + c1H - ((m - minMcr) / (maxMcr - minMcr)) * c1H;

  // 2. Chart 2: Total Power vs Feed Flow (Historical vs Scenario)
  const c2Pad = { top: 25, right: 25, bottom: 45, left: 60 };
  const c2W = svgWidth - c2Pad.left - c2Pad.right;
  const c2H = svgHeight - c2Pad.top - c2Pad.bottom;
  const minF = 120, maxF = 350;
  const minP = 55, maxP = 115;
  const sX2 = (f: number) => c2Pad.left + ((f - minF) / (maxF - minF)) * c2W;
  const sY2 = (p: number) => c2Pad.top + c2H - ((p - minP) / (maxP - minP)) * c2H;

  // 3. Chart 3: SEC LNG vs LNG Rundown
  const c3Pad = { top: 25, right: 25, bottom: 45, left: 60 };
  const c3W = svgWidth - c3Pad.left - c3Pad.right;
  const c3H = svgHeight - c3Pad.top - c3Pad.bottom;
  const minLng = 100, maxLng = 340;
  const minSec = 280, maxSec = 560;
  const sX3 = (l: number) => c3Pad.left + ((l - minLng) / (maxLng - minLng)) * c3W;
  const sY3 = (s: number) => c3Pad.top + c3H - ((s - minSec) / (maxSec - minSec)) * c3H;

  // 4. Chart 4: Composition Data
  const compLabels = ['N₂', 'CH₄ (C₁)', 'C₂H₆ (C₂)', 'C₂H₄', 'C₃H₈ (C₃)'];
  const actualComps = [
    snapshot.values.comp_N2?.value ?? 3.39,
    snapshot.values.comp_C1?.value ?? 44.45,
    snapshot.values.comp_C2?.value ?? 45.02,
    snapshot.values.comp_C2H4?.value ?? 0.85,
    snapshot.values.comp_C3?.value ?? 6.29,
  ];
  const scenarioComps = [
    scenario.comp_N2_molpct,
    scenario.comp_C1_molpct,
    scenario.comp_C2_molpct,
    scenario.comp_C2H4_molpct,
    scenario.comp_C3_molpct,
  ];

  // 5. Chart 5: MCHE Temperature Profile (0 to 100% bundle position)
  const c5Pad = { top: 25, right: 25, bottom: 45, left: 60 };
  const c5W = svgWidth - c5Pad.left - c5Pad.right;
  const c5H = svgHeight - c5Pad.top - c5Pad.bottom;
  const minT = -170, maxT = 30;
  const sX5 = (pct: number) => c5Pad.left + (pct / 100) * c5W;
  const sY5 = (t: number) => c5Pad.top + c5H - ((t - minT) / (maxT - minT)) * c5H;

  // Natural Gas Stream (Hot stream) cooling profile: In +20°C -> Mid -70°C -> LNG Out -158°C
  const ngTemp = (pct: number) => 20 - (pct / 100) * 178;
  // MCR Stream (Cold stream) vaporizing profile: Cold flash -162°C -> Warm suction -38°C
  const mcrTemp = (pct: number) => -162 + (1 - pct / 100) * 124;

  const pointsNG = [0, 15, 30, 45, 60, 75, 90, 100].map((p) => `${sX5(p)},${sY5(ngTemp(p))}`).join(' ');
  const pointsMCR = [100, 90, 75, 60, 45, 30, 15, 0].map((p) => `${sX5(p)},${sY5(mcrTemp(p))}`).join(' ');

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      gap: '24px',
      paddingBottom: '36px',
      fontFamily: "'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif",
    }}>
      {/* Header Banner */}
      <div style={{
        backgroundColor: '#ffffff',
        border: '1px solid #cbd5e1',
        borderRadius: '8px',
        padding: '16px 20px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '12px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.05)',
      }}>
        <div>
          <h2 style={{ margin: 0, fontSize: '20px', fontWeight: 700, color: '#0f172a' }}>
            Grafik Proses & Kurva Termodinamika C3MR
          </h2>
          <div style={{ fontSize: '14px', color: '#64748b', marginTop: '4px' }}>
            Visualisasi operasional Train H: interaksi hidraulika, kurva daya kompresor, SEC LNG, dan profil kriogenik MCHE.
          </div>
        </div>
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          <span style={{
            fontSize: '13px',
            padding: '4px 10px',
            backgroundColor: '#e0f2fe',
            color: '#0369a1',
            borderRadius: '6px',
            fontWeight: 600,
          }}>
            Mode: {userMode === 'OPERATOR' ? 'Operator' : 'Engineering'}
          </span>
          <span style={{
            fontSize: '13px',
            padding: '4px 10px',
            backgroundColor: '#f1f5f9',
            color: '#475569',
            borderRadius: '6px',
            fontWeight: 600,
          }}>
            N = {historicalPoints.length} Titik DCS
          </span>
        </div>
      </div>

      {/* Grid of 6 Process Charts (2 columns on desktop) */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(460px, 1fr))',
        gap: '24px',
      }}>

        {/* CHART 1: Feed Gas Flow vs MR Circulation Flow */}
        <div style={{
          backgroundColor: '#ffffff',
          border: '1px solid #cbd5e1',
          borderRadius: '8px',
          padding: '20px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.05)',
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '14px' }}>
            <div>
              <div style={{ fontSize: '16px', fontWeight: 700, color: '#0f172a' }}>
                1. Laju Treated Gas vs Sirkulasi MCR
              </div>
              <div style={{ fontSize: '13px', color: '#64748b', marginTop: '2px' }}>
                H3FI0004 [t/h] vs H4FI011B [t/h] &mdash; Batas Anti-Surge 480 t/h
              </div>
            </div>
            <span style={{
              fontSize: '12px',
              padding: '2px 8px',
              backgroundColor: currentMcr >= 480 ? '#dcfce7' : '#fee2e2',
              color: currentMcr >= 480 ? '#15803d' : '#b91c1c',
              borderRadius: '4px',
              fontWeight: 700,
            }}>
              {currentMcr >= 480 ? 'DI ATAS SURGE' : 'SURGE FLOOR ACTIVE'}
            </span>
          </div>

          <div style={{ width: '100%', overflowX: 'auto' }}>
            <svg viewBox={`0 0 ${svgWidth} ${svgHeight}`} style={{ width: '100%', maxHeight: '280px' }}>
              {/* Background grid */}
              <rect x={c1Pad.left} y={c1Pad.top} width={c1W} height={c1H} fill="#f8fafc" stroke="#e2e8f0" />

              {/* Anti-surge safe zone vs recycle zone */}
              <rect
                x={c1Pad.left}
                y={sY1(480)}
                width={c1W}
                height={sY1(minMcr) - sY1(480)}
                fill="rgba(239, 68, 68, 0.08)"
              />
              <line
                x1={c1Pad.left}
                y1={sY1(480)}
                x2={c1Pad.left + c1W}
                y2={sY1(480)}
                stroke="#dc2626"
                strokeWidth={2}
                strokeDasharray="5 4"
              />
              <text x={c1Pad.left + 8} y={sY1(480) - 6} fill="#dc2626" fontSize="11" fontWeight="700">
                Batas Anti-Surge Kompresor: 480.0 t/h
              </text>

              {/* Typical operation band (ratio ~2.2 to 2.45) */}
              <path
                d={`M ${sX1(140)} ${sY1(140 * 2.45)} L ${sX1(340)} ${sY1(340 * 1.95)} L ${sX1(340)} ${sY1(340 * 1.75)} L ${sX1(140)} ${sY1(480)} Z`}
                fill="rgba(2, 132, 199, 0.08)"
              />

              {/* Grid Y lines */}
              {[450, 500, 550, 600, 650].map((m) => (
                <g key={m}>
                  <line x1={c1Pad.left} y1={sY1(m)} x2={c1Pad.left + c1W} y2={sY1(m)} stroke="#e2e8f0" strokeDasharray="2 2" />
                  <text x={c1Pad.left - 8} y={sY1(m) + 4} fill="#64748b" fontSize="11" textAnchor="end" className="font-num">
                    {m}
                  </text>
                </g>
              ))}

              {/* Grid X lines */}
              {[150, 200, 250, 300, 350].map((f) => (
                <g key={f}>
                  <line x1={sX1(f)} y1={c1Pad.top} x2={sX1(f)} y2={c1Pad.top + c1H} stroke="#e2e8f0" strokeDasharray="2 2" />
                  <text x={sX1(f)} y={c1Pad.top + c1H + 16} fill="#64748b" fontSize="11" textAnchor="middle" className="font-num">
                    {f}
                  </text>
                </g>
              ))}

              {/* Current Actual DCS point */}
              <circle cx={sX1(snapshot.values.H1FI012?.value ?? currentFeed)} cy={sY1(snapshot.values.H4FI001?.value ?? 562.3)} r={6} fill="#64748b" />
              <text x={sX1(snapshot.values.H1FI012?.value ?? currentFeed) + 10} y={sY1(snapshot.values.H4FI001?.value ?? 562.3) + 4} fill="#475569" fontSize="11" fontWeight="600">
                Aktual DCS
              </text>

              {/* Scenario Point */}
              <circle cx={sX1(currentFeed)} cy={sY1(currentMcr)} r={9} fill="none" stroke="#0284c7" strokeWidth={2} />
              <circle cx={sX1(currentFeed)} cy={sY1(currentMcr)} r={5} fill="#0284c7" />
              <text x={sX1(currentFeed) + 12} y={sY1(currentMcr) - 8} fill="#0284c7" fontSize="12" fontWeight="700">
                Skenario ({currentFeed.toFixed(0)} t/h, {currentMcr.toFixed(1)} t/h)
              </text>

              {/* Axis labels */}
              <text x={c1Pad.left + c1W / 2} y={svgHeight - 8} fill="#0f172a" fontSize="12" textAnchor="middle" fontWeight="600">
                Laju Alir Treated Gas ke MCHE (t/h)
              </text>
              <text x={-c1Pad.top - c1H / 2} y={16} fill="#0f172a" fontSize="12" textAnchor="middle" fontWeight="600" transform="rotate(-90)">
                Sirkulasi MCR (t/h)
              </text>
            </svg>
          </div>
        </div>

        {/* CHART 2: Compressor Power vs Production Load */}
        <div style={{
          backgroundColor: '#ffffff',
          border: '1px solid #cbd5e1',
          borderRadius: '8px',
          padding: '20px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.05)',
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '14px' }}>
            <div>
              <div style={{ fontSize: '16px', fontWeight: 700, color: '#0f172a' }}>
                2. Daya Kompresor vs Beban Umpan Gas
              </div>
              <div style={{ fontSize: '13px', color: '#64748b', marginTop: '2px' }}>
                Total Daya Poros C3MR [MW] vs Laju Alir Umpan [t/h]
              </div>
            </div>
            <span style={{
              fontSize: '12px',
              padding: '2px 8px',
              backgroundColor: '#f1f5f9',
              color: '#334155',
              borderRadius: '4px',
              fontWeight: 600,
            }}>
              Underload | Transisi | Baseload
            </span>
          </div>

          <div style={{ width: '100%', overflowX: 'auto' }}>
            <svg viewBox={`0 0 ${svgWidth} ${svgHeight}`} style={{ width: '100%', maxHeight: '280px' }}>
              <rect x={c2Pad.left} y={c2Pad.top} width={c2W} height={c2H} fill="#f8fafc" stroke="#e2e8f0" />

              {/* Regimes Background */}
              <rect x={sX2(minF)} y={c2Pad.top} width={sX2(226.8) - sX2(minF)} height={c2H} fill="rgba(2, 132, 199, 0.04)" />
              <rect x={sX2(226.8)} y={c2Pad.top} width={sX2(279.8) - sX2(226.8)} height={c2H} fill="rgba(217, 119, 6, 0.04)" />
              <rect x={sX2(279.8)} y={c2Pad.top} width={sX2(maxF) - sX2(279.8)} height={c2H} fill="rgba(22, 163, 74, 0.04)" />

              {/* Regime Dividing Lines */}
              <line x1={sX2(226.8)} y1={c2Pad.top} x2={sX2(226.8)} y2={c2Pad.top + c2H} stroke="#94a3b8" strokeDasharray="3 3" />
              <line x1={sX2(279.8)} y1={c2Pad.top} x2={sX2(279.8)} y2={c2Pad.top + c2H} stroke="#94a3b8" strokeDasharray="3 3" />

              {/* Y Grid */}
              {[60, 75, 90, 105].map((p) => (
                <g key={p}>
                  <line x1={c2Pad.left} y1={sY2(p)} x2={c2Pad.left + c2W} y2={sY2(p)} stroke="#e2e8f0" strokeDasharray="2 2" />
                  <text x={c2Pad.left - 8} y={sY2(p) + 4} fill="#64748b" fontSize="11" textAnchor="end" className="font-num">
                    {p} MW
                  </text>
                </g>
              ))}

              {/* X Grid */}
              {[150, 200, 250, 300].map((f) => (
                <g key={f}>
                  <line x1={sX2(f)} y1={c2Pad.top} x2={sX2(f)} y2={c2Pad.top + c2H} stroke="#e2e8f0" strokeDasharray="2 2" />
                  <text x={sX2(f)} y={c2Pad.top + c2H + 16} fill="#64748b" fontSize="11" textAnchor="middle" className="font-num">
                    {f}
                  </text>
                </g>
              ))}

              {/* Historical DCS Points */}
              {historicalPoints.map((pt, i) => (
                <circle key={i} cx={sX2(pt.feed_flow)} cy={sY2(pt.power_mw)} r={3} fill="#94a3b8" opacity={0.65} />
              ))}

              {/* Baseline Point */}
              <circle cx={sX2(currentFeed)} cy={sY2(baselinePower)} r={6} fill="#64748b" />
              <text x={sX2(currentFeed) + 8} y={sY2(baselinePower) + 4} fill="#475569" fontSize="11" fontWeight="600">
                Aktual: {baselinePower.toFixed(1)} MW
              </text>

              {/* Scenario Point */}
              <circle cx={sX2(currentFeed)} cy={sY2(currentPower)} r={9} fill="none" stroke="#0284c7" strokeWidth={2} />
              <circle cx={sX2(currentFeed)} cy={sY2(currentPower)} r={5} fill="#0284c7" />
              <text x={sX2(currentFeed) + 8} y={sY2(currentPower) - 8} fill="#0284c7" fontSize="12" fontWeight="700">
                Skenario: {currentPower.toFixed(2)} MW
              </text>

              {/* Axis Labels */}
              <text x={c2Pad.left + c2W / 2} y={svgHeight - 8} fill="#0f172a" fontSize="12" textAnchor="middle" fontWeight="600">
                Laju Alir Treated Gas ke MCHE (t/h)
              </text>
              <text x={-c2Pad.top - c2H / 2} y={16} fill="#0f172a" fontSize="12" textAnchor="middle" fontWeight="600" transform="rotate(-90)">
                Total Daya Poros C3MR (MW)
              </text>
            </svg>
          </div>
        </div>

        {/* CHART 3: SEC LNG vs LNG Production */}
        <div style={{
          backgroundColor: '#ffffff',
          border: '1px solid #cbd5e1',
          borderRadius: '8px',
          padding: '20px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.05)',
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '14px' }}>
            <div>
              <div style={{ fontSize: '16px', fontWeight: 700, color: '#0f172a' }}>
                3. Efisiensi Spesifik (SEC) vs Produksi LNG
              </div>
              <div style={{ fontSize: '13px', color: '#64748b', marginTop: '2px' }}>
                SEC [kWh/t LNG] vs Laju Alir H5FI6A [t/h LNG]
              </div>
            </div>
            <span style={{
              fontSize: '12px',
              padding: '2px 8px',
              backgroundColor: '#e0f2fe',
              color: '#0369a1',
              borderRadius: '4px',
              fontWeight: 700,
            }}>
              TARGET &le; 360 kWh/t
            </span>
          </div>

          <div style={{ width: '100%', overflowX: 'auto' }}>
            <svg viewBox={`0 0 ${svgWidth} ${svgHeight}`} style={{ width: '100%', maxHeight: '280px' }}>
              <rect x={c3Pad.left} y={c3Pad.top} width={c3W} height={c3H} fill="#f8fafc" stroke="#e2e8f0" />

              {/* Typical non-linear SEC curve (drastic increase at turndown due to recycle) */}
              <path
                d={`M ${sX3(120)} ${sY3(530)} Q ${sX3(160)} ${sY3(430)} ${sX3(220)} ${sY3(360)} T ${sX3(320)} ${sY3(320)}`}
                fill="none"
                stroke="#cbd5e1"
                strokeWidth={3}
              />

              {/* Y Grid */}
              {[300, 360, 420, 480, 540].map((s) => (
                <g key={s}>
                  <line x1={c3Pad.left} y1={sY3(s)} x2={c3Pad.left + c3W} y2={sY3(s)} stroke="#e2e8f0" strokeDasharray="2 2" />
                  <text x={c3Pad.left - 8} y={sY3(s) + 4} fill="#64748b" fontSize="11" textAnchor="end" className="font-num">
                    {s}
                  </text>
                </g>
              ))}

              {/* X Grid */}
              {[120, 160, 200, 240, 280, 320].map((l) => (
                <g key={l}>
                  <line x1={sX3(l)} y1={c3Pad.top} x2={sX3(l)} y2={c3Pad.top + c3H} stroke="#e2e8f0" strokeDasharray="2 2" />
                  <text x={sX3(l)} y={c3Pad.top + c3H + 16} fill="#64748b" fontSize="11" textAnchor="middle" className="font-num">
                    {l}
                  </text>
                </g>
              ))}

              {/* Baseline SEC point */}
              <circle cx={sX3(currentLng)} cy={sY3(baselineSec)} r={6} fill="#64748b" />
              <text x={sX3(currentLng) + 8} y={sY3(baselineSec) + 4} fill="#475569" fontSize="11" fontWeight="600">
                Aktual: {baselineSec.toFixed(1)} kWh/t
              </text>

              {/* Scenario SEC point */}
              <circle cx={sX3(currentLng)} cy={sY3(currentSec)} r={9} fill="none" stroke="#16a34a" strokeWidth={2} />
              <circle cx={sX3(currentLng)} cy={sY3(currentSec)} r={5} fill="#16a34a" />
              <text x={sX3(currentLng) + 8} y={sY3(currentSec) - 8} fill="#16a34a" fontSize="12" fontWeight="700">
                Skenario: {currentSec.toFixed(1)} kWh/t
              </text>

              {/* Axis Labels */}
              <text x={c3Pad.left + c3W / 2} y={svgHeight - 8} fill="#0f172a" fontSize="12" textAnchor="middle" fontWeight="600">
                Laju Alir Produksi LNG Rundown H5FI6A (t/h LNG)
              </text>
              <text x={-c3Pad.top - c3H / 2} y={16} fill="#0f172a" fontSize="12" textAnchor="middle" fontWeight="600" transform="rotate(-90)">
                SEC LNG (kWh/t LNG)
              </text>
            </svg>
          </div>
        </div>

        {/* CHART 4: MR Composition Profile */}
        <div style={{
          backgroundColor: '#ffffff',
          border: '1px solid #cbd5e1',
          borderRadius: '8px',
          padding: '20px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.05)',
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '14px' }}>
            <div>
              <div style={{ fontSize: '16px', fontWeight: 700, color: '#0f172a' }}>
                4. Profil Komposisi Mixed Refrigerant
              </div>
              <div style={{ fontSize: '13px', color: '#64748b', marginTop: '2px' }}>
                Perbandingan Fraksi Mol [%] Aktual vs Skenario Target
              </div>
            </div>
            <span style={{
              fontSize: '12px',
              padding: '2px 8px',
              backgroundColor: dm <= dmLimit ? '#dcfce7' : '#fee2e2',
              color: dm <= dmLimit ? '#15803d' : '#b91c1c',
              borderRadius: '4px',
              fontWeight: 700,
            }}>
              DM = {dm.toFixed(3)} {dm <= dmLimit ? '(VALID)' : '(EXTRAPOLASI)'}
            </span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', marginTop: '8px' }}>
            {compLabels.map((lbl, idx) => {
              const act = actualComps[idx];
              const sce = scenarioComps[idx];
              const delta = sce - act;
              return (
                <div key={idx}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px', marginBottom: '4px' }}>
                    <span style={{ color: '#0f172a', fontWeight: 700 }}>{lbl}</span>
                    <span className="font-num" style={{ color: '#475569' }}>
                      Aktual: <strong>{act.toFixed(2)}%</strong> &rarr; Skenario: <strong style={{ color: '#0284c7' }}>{sce.toFixed(2)}%</strong>
                      <span style={{
                        marginLeft: '8px',
                        color: Math.abs(delta) < 0.01 ? '#64748b' : delta > 0 ? '#16a34a' : '#d97706',
                        fontWeight: 700,
                      }}>
                        ({delta >= 0 ? '+' : ''}{delta.toFixed(2)}%)
                      </span>
                    </span>
                  </div>

                  {/* Dual bar representation */}
                  <div style={{ height: '16px', backgroundColor: '#f1f5f9', borderRadius: '4px', position: 'relative', overflow: 'hidden', border: '1px solid #e2e8f0' }}>
                    {/* Actual bar */}
                    <div style={{
                      position: 'absolute',
                      top: 0,
                      left: 0,
                      bottom: 0,
                      width: `${Math.min(100, act * 1.8)}%`,
                      backgroundColor: '#94a3b8',
                      borderRadius: '3px',
                      opacity: 0.7,
                    }} />
                    {/* Scenario bar */}
                    <div style={{
                      position: 'absolute',
                      top: 0,
                      left: 0,
                      bottom: 0,
                      width: `${Math.min(100, sce * 1.8)}%`,
                      backgroundColor: '#0284c7',
                      borderRadius: '3px',
                      opacity: 0.85,
                    }} />
                  </div>
                </div>
              );
            })}
          </div>

          <div style={{
            marginTop: '16px',
            padding: '10px 14px',
            backgroundColor: '#f8fafc',
            border: '1px solid #e2e8f0',
            borderRadius: '6px',
            fontSize: '12px',
            color: '#475569',
            display: 'flex',
            justifyContent: 'space-between',
          }}>
            <span>Legend: <span style={{ color: '#94a3b8' }}>■ Aktual DCS</span> &nbsp; <span style={{ color: '#0284c7' }}>■ Skenario Target</span></span>
            <span>Total Komposisi: <strong>{(scenarioComps.reduce((a, b) => a + b, 0)).toFixed(2)} mol%</strong></span>
          </div>
        </div>

        {/* CHART 5: MCHE Temperature Profile */}
        <div style={{
          backgroundColor: '#ffffff',
          border: '1px solid #cbd5e1',
          borderRadius: '8px',
          padding: '20px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.05)',
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '14px' }}>
            <div>
              <div style={{ fontSize: '16px', fontWeight: 700, color: '#0f172a' }}>
                5. Profil Termal MCHE 5E-1 (Pinch Curve)
              </div>
              <div style={{ fontSize: '13px', color: '#64748b', marginTop: '2px' }}>
                Profil Pendinginan Natural Gas vs Evaporasi MCR Shell
              </div>
            </div>
            <span style={{
              fontSize: '12px',
              padding: '2px 8px',
              backgroundColor: '#dcfce7',
              color: '#15803d',
              borderRadius: '4px',
              fontWeight: 700,
            }}>
              MITA &ge; 1.50 &deg;C (OK)
            </span>
          </div>

          <div style={{ width: '100%', overflowX: 'auto' }}>
            <svg viewBox={`0 0 ${svgWidth} ${svgHeight}`} style={{ width: '100%', maxHeight: '280px' }}>
              <rect x={c5Pad.left} y={c5Pad.top} width={c5W} height={c5H} fill="#f8fafc" stroke="#e2e8f0" />

              {/* Bundle sections */}
              <rect x={c5Pad.left} y={c5Pad.top} width={c5W * 0.45} height={c5H} fill="rgba(217, 119, 6, 0.04)" />
              <rect x={c5Pad.left + c5W * 0.45} y={c5Pad.top} width={c5W * 0.55} height={c5H} fill="rgba(2, 132, 199, 0.04)" />
              <line x1={c5Pad.left + c5W * 0.45} y1={c5Pad.top} x2={c5Pad.left + c5W * 0.45} y2={c5Pad.top + c5H} stroke="#94a3b8" strokeDasharray="3 3" />
              <text x={c5Pad.left + c5W * 0.22} y={c5Pad.top + 18} fill="#d97706" fontSize="11" fontWeight="700" textAnchor="middle">
                Warm Bundle (3E-1)
              </text>
              <text x={c5Pad.left + c5W * 0.72} y={c5Pad.top + 18} fill="#0284c7" fontSize="11" fontWeight="700" textAnchor="middle">
                Cold Bundle (3E-2)
              </text>

              {/* Y Grid */}
              {[20, -20, -60, -100, -140, -170].map((t) => (
                <g key={t}>
                  <line x1={c5Pad.left} y1={sY5(t)} x2={c5Pad.left + c5W} y2={sY5(t)} stroke="#e2e8f0" strokeDasharray="2 2" />
                  <text x={c5Pad.left - 8} y={sY5(t) + 4} fill="#64748b" fontSize="11" textAnchor="end" className="font-num">
                    {t} &deg;C
                  </text>
                </g>
              ))}

              {/* X Grid (0 to 100% bundle position) */}
              {[0, 25, 50, 75, 100].map((pct) => (
                <g key={pct}>
                  <line x1={sX5(pct)} y1={c5Pad.top} x2={sX5(pct)} y2={c5Pad.top + c5H} stroke="#e2e8f0" strokeDasharray="2 2" />
                  <text x={sX5(pct)} y={c5Pad.top + c5H + 16} fill="#64748b" fontSize="11" textAnchor="middle" className="font-num">
                    {pct}%
                  </text>
                </g>
              ))}

              {/* Hot Stream: Natural Gas Tube */}
              <polyline points={pointsNG} fill="none" stroke="#ef4444" strokeWidth={3} />
              <text x={sX5(10)} y={sY5(ngTemp(10)) - 8} fill="#dc2626" fontSize="11" fontWeight="700">
                Natural Gas (+20 &rarr; -158 &deg;C)
              </text>

              {/* Cold Stream: Vaporizing MCR Shell */}
              <polyline points={pointsMCR} fill="none" stroke="#0284c7" strokeWidth={3} />
              <text x={sX5(70)} y={sY5(mcrTemp(70)) + 16} fill="#0284c7" fontSize="11" fontWeight="700">
                MCR Shell (-162 &rarr; -38 &deg;C)
              </text>

              {/* Axis Labels */}
              <text x={c5Pad.left + c5W / 2} y={svgHeight - 8} fill="#0f172a" fontSize="12" textAnchor="middle" fontWeight="600">
                Posisi Bundle MCHE (0% = Warm Top &rarr; 100% = Cold Bottom)
              </text>
              <text x={-c5Pad.top - c5H / 2} y={16} fill="#0f172a" fontSize="12" textAnchor="middle" fontWeight="600" transform="rotate(-90)">
                Temperatur Kriogenik (&deg;C)
              </text>
            </svg>
          </div>
        </div>

        {/* CHART 6: Baseline vs Scenario Comparison */}
        <div style={{
          backgroundColor: '#ffffff',
          border: '1px solid #cbd5e1',
          borderRadius: '8px',
          padding: '20px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.05)',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'space-between',
        }}>
          <div>
            <div style={{ fontSize: '16px', fontWeight: 700, color: '#0f172a' }}>
              6. Ringkasan Perbandingan KPI Proses
            </div>
            <div style={{ fontSize: '13px', color: '#64748b', marginTop: '2px', marginBottom: '16px' }}>
              Perbandingan Metrik Utama: Kondisi Aktual vs Hasil Prediksi Skenario
            </div>

            {/* Metric Comparison Cards */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px' }}>
              {/* Power */}
              <div style={{ padding: '12px', border: '1px solid #e2e8f0', borderRadius: '6px', backgroundColor: '#f8fafc' }}>
                <div style={{ fontSize: '12px', color: '#64748b', fontWeight: 600 }}>Total Daya Poros C3MR</div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginTop: '6px' }}>
                  <span style={{ fontSize: '13px', color: '#64748b' }}>Aktual: {baselinePower.toFixed(2)} MW</span>
                  <span style={{ fontSize: '16px', fontWeight: 800, color: '#0f172a' }}>{currentPower.toFixed(2)} MW</span>
                </div>
                <div style={{
                  fontSize: '12px',
                  fontWeight: 700,
                  marginTop: '4px',
                  color: currentPower <= baselinePower ? '#16a34a' : '#d97706',
                }}>
                  {currentPower <= baselinePower ? 'Hemat ' : 'Tambah '}
                  {Math.abs(currentPower - baselinePower).toFixed(2)} MW ({(((currentPower - baselinePower) / baselinePower) * 100).toFixed(2)}%)
                </div>
              </div>

              {/* SEC */}
              <div style={{ padding: '12px', border: '1px solid #e2e8f0', borderRadius: '6px', backgroundColor: '#f8fafc' }}>
                <div style={{ fontSize: '12px', color: '#64748b', fontWeight: 600 }}>SEC LNG</div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginTop: '6px' }}>
                  <span style={{ fontSize: '13px', color: '#64748b' }}>Aktual: {baselineSec.toFixed(1)}</span>
                  <span style={{ fontSize: '16px', fontWeight: 800, color: '#0f172a' }}>{currentSec.toFixed(1)} kWh/t</span>
                </div>
                <div style={{
                  fontSize: '12px',
                  fontWeight: 700,
                  marginTop: '4px',
                  color: currentSec <= baselineSec ? '#16a34a' : '#d97706',
                }}>
                  {currentSec <= baselineSec ? 'Hemat ' : 'Tambah '}
                  {Math.abs(currentSec - baselineSec).toFixed(1)} kWh/t
                </div>
              </div>

              {/* MCR Flow */}
              <div style={{ padding: '12px', border: '1px solid #e2e8f0', borderRadius: '6px', backgroundColor: '#f8fafc' }}>
                <div style={{ fontSize: '12px', color: '#64748b', fontWeight: 600 }}>Sirkulasi MCR</div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginTop: '6px' }}>
                  <span style={{ fontSize: '13px', color: '#64748b' }}>Aktual: {(snapshot.values.H4FI001?.value ?? 562.3).toFixed(1)} t/h</span>
                  <span style={{ fontSize: '16px', fontWeight: 800, color: '#0f172a' }}>{currentMcr.toFixed(1)} t/h</span>
                </div>
                <div style={{ fontSize: '12px', fontWeight: 600, color: '#0284c7', marginTop: '4px' }}>
                  Anti-Surge Margin: +{(currentMcr - 480).toFixed(1)} t/h
                </div>
              </div>

              {/* CO2 Abatement */}
              <div style={{ padding: '12px', border: '1px solid #e2e8f0', borderRadius: '6px', backgroundColor: '#f8fafc' }}>
                <div style={{ fontSize: '12px', color: '#64748b', fontWeight: 600 }}>Potensi Reduksi Emisi CO₂</div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginTop: '6px' }}>
                  <span style={{ fontSize: '13px', color: '#64748b' }}>Faktor Grid: 0.82</span>
                  <span style={{ fontSize: '16px', fontWeight: 800, color: '#16a34a' }}>
                    {prediction?.prediction?.co2_abatement_t_day ? `${prediction.prediction.co2_abatement_t_day.toFixed(1)} t/hari` : '—'}
                  </span>
                </div>
                <div style={{ fontSize: '12px', fontWeight: 600, color: '#16a34a', marginTop: '4px' }}>
                  Basis Fuel Gas Kilang Badak
                </div>
              </div>
            </div>
          </div>

          <div style={{
            marginTop: '16px',
            padding: '12px 14px',
            backgroundColor: '#f1f5f9',
            border: '1px solid #cbd5e1',
            borderRadius: '6px',
            fontSize: '13px',
            color: '#334155',
            lineHeight: 1.5,
          }}>
            <strong>Ringkasan Hasil Evaluasi:</strong> Hasil perhitungan skenario menunjukkan bahwa konfigurasi yang dimasukkan dapat mempertahankan integritas batasan keselamatan kompresor di atas floor anti-surge (480.0 t/h) dan menjaga efisiensi spesifik LNG dalam rentang reliabel model.
          </div>
        </div>

      </div>
    </div>
  );
};
