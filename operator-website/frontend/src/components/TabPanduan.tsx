import React from 'react';
import type { UserMode } from '../types';

interface TabPanduanProps {
  userMode?: UserMode;
}

export const TabPanduan: React.FC<TabPanduanProps> = ({ userMode = 'OPERATOR' }) => {
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      gap: '24px',
      maxWidth: '1200px',
      margin: '0 auto',
      paddingBottom: '40px',
      fontFamily: "'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif",
    }}>
      {/* Safety Notice Banner */}
      <div style={{
        backgroundColor: '#fef2f2',
        border: '2px solid #ef4444',
        borderRadius: '8px',
        padding: '18px 24px',
        color: '#991b1b',
        boxShadow: '0 1px 3px rgba(0,0,0,0.05)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
          <span style={{ fontSize: '20px' }}>⚠️</span>
          <h3 style={{ margin: 0, fontSize: '18px', fontWeight: 700, color: '#b91c1c' }}>
            SAFETY NOTICE & READ-ONLY ADVISORY STATUS
          </h3>
        </div>
        <p style={{ margin: 0, fontSize: '15px', lineHeight: 1.6, color: '#7f1d1d' }}>
          This software suite is strictly a <strong>decision-support tool</strong> and what-if simulation calculator.
          It is architecturally and physically <strong>INCAPABLE of and PROHIBITED from</strong> writing setpoints directly to DCS, actuating control valves,
          adjusting turbine governor speeds, or modifying field refrigerant inventory. All displayed results are numerical estimates
          and must be verified against standard operating procedures (SOP) and approved by the Shift Supervisor before any field actions are executed.
        </p>
      </div>

      {/* SECTION 1: 7-STEP OPERATOR WORKFLOW */}
      <div style={{
        backgroundColor: '#ffffff',
        border: '1px solid #cbd5e1',
        borderRadius: '8px',
        padding: '24px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.05)',
      }}>
        <h2 style={{ margin: '0 0 8px 0', fontSize: '20px', fontWeight: 700, color: '#0f172a' }}>
          Standard Operator Workflow (7-Step Execution Model)
        </h2>
        <div style={{ fontSize: '15px', color: '#64748b', marginBottom: '20px' }}>
          Follow this structured sequence when performing C3MR Train H operational evaluations:
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
          {[
            {
              step: '1',
              title: 'Review Process Data',
              desc: 'Inspect actual treated feed gas flow (H3FI0004), LNG rundown production (H5FI6A), and suction drum temperature.',
              color: '#0284c7',
            },
            {
              step: '2',
              title: 'Verify Sensor Validity',
              desc: 'Ensure all instrument health flags indicate VALID, with no evidence of frozen transmitters or out-of-range tags.',
              color: '#0284c7',
            },
            {
              step: '3',
              title: 'Set Scenario Targets',
              desc: 'Enter permissible scenario values (MCR flow or target mole fractions), or click "Apply AI Target".',
              color: '#2563eb',
            },
            {
              step: '4',
              title: 'Evaluate Predictions',
              desc: 'Review real-time machine learning surrogate predictions automatically computed with rigorous PR-EOS closure.',
              color: '#0284c7',
            },
            {
              step: '5',
              title: 'Analyze KPI Benefits',
              desc: 'Inspect total C3MR shaft power savings, specific energy consumption (SEC LNG), and the make-up injection schedule.',
              color: '#16a34a',
            },
            {
              step: '6',
              title: 'Audit Safety Limits',
              desc: 'Verify the 5 critical safety constraints: Anti-Surge Floor, Suction Drum TAL, Superheat, MCHE DP, and Mahalanobis Boundary.',
              color: '#d97706',
            },
            {
              step: '7',
              title: 'Consult Supervisor',
              desc: 'Review operational guidance notes before consulting with the Shift Supervisor for phased field execution.',
              color: '#475569',
            },
          ].map((item) => (
            <div key={item.step} style={{
              border: '1px solid #e2e8f0',
              borderRadius: '8px',
              padding: '16px',
              backgroundColor: '#f8fafc',
              display: 'flex',
              flexDirection: 'column',
              gap: '8px',
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <div style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: '50%',
                  backgroundColor: item.color,
                  color: '#ffffff',
                  fontWeight: 800,
                  fontSize: '15px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0,
                }}>
                  {item.step}
                </div>
                <div style={{ fontSize: '16px', fontWeight: 700, color: '#0f172a' }}>
                  {item.title}
                </div>
              </div>
              <div style={{ fontSize: '14px', color: '#475569', lineHeight: 1.5, paddingLeft: '42px' }}>
                {item.desc}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* SECTION 2: EDITABLE vs LOCKED VARIABLES TABLE */}
      <div style={{
        backgroundColor: '#ffffff',
        border: '1px solid #cbd5e1',
        borderRadius: '8px',
        padding: '24px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.05)',
      }}>
        <h2 style={{ margin: '0 0 8px 0', fontSize: '20px', fontWeight: 700, color: '#0f172a' }}>
          Process Variables & Constraints Dictionary
        </h2>
        <div style={{ fontSize: '15px', color: '#64748b', marginBottom: '16px' }}>
          Explicit demarcation between operator-editable what-if scenario parameters and protected real-time DCS variables:
        </div>

        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '15px' }}>
            <thead>
              <tr style={{ backgroundColor: '#0f172a', color: '#ffffff' }}>
                <th style={{ padding: '12px 14px', textAlign: 'left', fontWeight: 600 }}>Parameter</th>
                {userMode === 'ENGINEERING' && (
                  <th style={{ padding: '12px 14px', textAlign: 'left', fontWeight: 600 }}>DCS Tag</th>
                )}
                <th style={{ padding: '12px 14px', textAlign: 'left', fontWeight: 600 }}>Unit</th>
                <th style={{ padding: '12px 14px', textAlign: 'center', fontWeight: 600 }}>Input Type</th>
                <th style={{ padding: '12px 14px', textAlign: 'left', fontWeight: 600 }}>Operating Range & Engineering Rules</th>
              </tr>
            </thead>
            <tbody>
              {[
                {
                  param: 'Treated Feed Gas Flow to MCHE (5E-1)',
                  tag: 'H3FI0004 × 0.760',
                  unit: 't/h',
                  type: 'DISTURBANCE (Read-Only)',
                  typeColor: '#64748b',
                  rule: 'Independent process disturbance (plant loading). Follows real-time DCS telemetry or planned production rate.',
                },
                {
                  param: 'LNG Rundown Production Flow',
                  tag: 'H5FI6A',
                  unit: 't/h LNG',
                  type: 'COUPLED (Read-Only)',
                  typeColor: '#64748b',
                  rule: 'Determined via 7-component PR-EOS flash equilibrium of drum 5C-1 (~94.53 wt% nominal yield at -152.5°C, 0.30 kg/cm²G). Official SEC LNG denominator.',
                },
                {
                  param: 'MCR Circulation Flow',
                  tag: 'H4FI011B × 36.8',
                  unit: 't/h',
                  type: 'EDITABLE (Scenario)',
                  typeColor: '#0284c7',
                  rule: 'Primary decision variable. Normal range 480 – 620 t/h. Must remain ≥ 480.0 t/h to prevent centrifugal compressor surge trip.',
                },
                {
                  param: 'MCR Composition: N₂ (Nitrogen)',
                  tag: 'comp_4C-8_N2',
                  unit: 'mol%',
                  type: 'EDITABLE (Scenario)',
                  typeColor: '#0284c7',
                  rule: 'Range 2.0 – 5.5 mol%. Sets deep cryogenic subcooling at the cold bundle overhead of MCHE 5E-1.',
                },
                {
                  param: 'MCR Composition: CH₄ (Methane, C₁)',
                  tag: 'comp_4C-8_C1',
                  unit: 'mol%',
                  type: 'EDITABLE (Scenario)',
                  typeColor: '#0284c7',
                  rule: 'Range 40.0 – 48.0 mol%. Primary low-temperature refrigerant component for cold bundle heat absorption.',
                },
                {
                  param: 'MCR Composition: C₂H₆ (Ethane, C₂)',
                  tag: 'comp_4C-8_C2',
                  unit: 'mol%',
                  type: 'EDITABLE (Scenario)',
                  typeColor: '#0284c7',
                  rule: 'Range 40.0 – 48.0 mol%. Mid-temperature refrigerant component matching intermediate condensation slope.',
                },
                {
                  param: 'MCR Composition: C₂H₄ (Ethylene)',
                  tag: 'comp_4C-8_C2H4',
                  unit: 'mol%',
                  type: 'EDITABLE (Scenario)',
                  typeColor: '#0284c7',
                  rule: 'Range 0.0 – 3.0 mol%. Dynamic transition component for fast cooling curve adjustment.',
                },
                {
                  param: 'MCR Composition: C₃H₈ (Propane, C₃)',
                  tag: 'comp_4C-8_C3',
                  unit: 'mol%',
                  type: 'EDITABLE (Scenario)',
                  typeColor: '#0284c7',
                  rule: 'Range 4.0 – 8.5 mol%. Heavy refrigerant component for warm bundle cooling. Primary driver of suction drum temperature.',
                },
                {
                  param: 'Suction Drum Temperature Alarm Low (TAL)',
                  tag: 'H4TI004B',
                  unit: '°C',
                  type: 'SAFETY LIMIT (Locked)',
                  typeColor: '#dc2626',
                  rule: 'Plant mechanical safety interlock: TAL ≥ -45.0 °C. Hardcoded safety boundary, strictly non-editable.',
                },
                {
                  param: 'MCHE 5E-1 Bundle Differential Pressure',
                  tag: 'H5PDI003',
                  unit: 'kg/cm²',
                  type: 'SAFETY LIMIT (Locked)',
                  typeColor: '#dc2626',
                  rule: 'Hydraulic limit: High Alarm at 0.42 kg/cm², Emergency Trip at 0.54 kg/cm² (5PDAHH-25).',
                },
              ].map((row, idx) => (
                <tr key={idx} style={{
                  backgroundColor: idx % 2 === 0 ? '#ffffff' : '#f8fafc',
                  borderBottom: '1px solid #e2e8f0',
                }}>
                  <td style={{ padding: '12px 14px', fontWeight: 600, color: '#0f172a' }}>{row.param}</td>
                  {userMode === 'ENGINEERING' && (
                    <td style={{ padding: '12px 14px', fontFamily: 'monospace', color: '#0284c7', fontSize: '13px' }}>{row.tag}</td>
                  )}
                  <td style={{ padding: '12px 14px', color: '#64748b' }}>{row.unit}</td>
                  <td style={{ padding: '12px 14px', textAlign: 'center' }}>
                    <span style={{
                      fontSize: '12px',
                      fontWeight: 700,
                      padding: '3px 8px',
                      borderRadius: '4px',
                      backgroundColor: row.typeColor === '#0284c7' ? '#e0f2fe' : row.typeColor === '#dc2626' ? '#fee2e2' : '#f1f5f9',
                      color: row.typeColor,
                    }}>
                      {row.type}
                    </span>
                  </td>
                  <td style={{ padding: '12px 14px', color: '#334155', fontSize: '14px', lineHeight: 1.4 }}>{row.rule}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* SECTION 3: CONSTRAINT STATUS DICTIONARY */}
      <div style={{
        backgroundColor: '#ffffff',
        border: '1px solid #cbd5e1',
        borderRadius: '8px',
        padding: '24px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.05)',
      }}>
        <h2 style={{ margin: '0 0 8px 0', fontSize: '20px', fontWeight: 700, color: '#0f172a' }}>
          Constraint Status & Badge Dictionary
        </h2>
        <div style={{ fontSize: '15px', color: '#64748b', marginBottom: '16px' }}>
          Definitions and engineering interpretations for each constraint evaluation badge:
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '16px' }}>
          <div style={{ padding: '16px', borderRadius: '8px', border: '1px solid #bbf7d0', backgroundColor: '#f0fdf4' }}>
            <span style={{
              fontSize: '13px',
              fontWeight: 800,
              padding: '3px 8px',
              backgroundColor: '#16a34a',
              color: '#ffffff',
              borderRadius: '4px',
            }}>
              PASSED
            </span>
            <div style={{ fontSize: '16px', fontWeight: 700, color: '#15803d', margin: '10px 0 6px 0' }}>
              Constraint Fully Satisfied
            </div>
            <div style={{ fontSize: '14px', color: '#166534', lineHeight: 1.5 }}>
              Operating parameters reside well within technical design limits and maintain adequate safety margins.
            </div>
          </div>

          <div style={{ padding: '16px', borderRadius: '8px', border: '1px solid #fef08a', backgroundColor: '#fefce8' }}>
            <span style={{
              fontSize: '13px',
              fontWeight: 800,
              padding: '3px 8px',
              backgroundColor: '#d97706',
              color: '#ffffff',
              borderRadius: '4px',
            }}>
              WARNING
            </span>
            <div style={{ fontSize: '16px', fontWeight: 700, color: '#b45309', margin: '10px 0 6px 0' }}>
              Approaching Safety Margin
            </div>
            <div style={{ fontSize: '14px', color: '#854d0e', lineHeight: 1.5 }}>
              Parameters satisfy minimum/maximum thresholds but safety margin is narrowing, or composition nears training boundary.
            </div>
          </div>

          <div style={{ padding: '16px', borderRadius: '8px', border: '1px solid #fecaca', backgroundColor: '#fef2f2' }}>
            <span style={{
              fontSize: '13px',
              fontWeight: 800,
              padding: '3px 8px',
              backgroundColor: '#dc2626',
              color: '#ffffff',
              borderRadius: '4px',
            }}>
              FAILED
            </span>
            <div style={{ fontSize: '16px', fontWeight: 700, color: '#b91c1c', margin: '10px 0 6px 0' }}>
              Verified Safety Limit Violation
            </div>
            <div style={{ fontSize: '14px', color: '#991b1b', lineHeight: 1.5 }}>
              Scenario breaches mechanical/process safety limits (e.g., circulation &lt; 480 t/h without kickback modulation, or suction temp &lt; -45 °C). STRICTLY PROHIBITED.
            </div>
          </div>

          <div style={{ padding: '16px', borderRadius: '8px', border: '1px solid #e2e8f0', backgroundColor: '#f8fafc' }}>
            <span style={{
              fontSize: '13px',
              fontWeight: 800,
              padding: '3px 8px',
              backgroundColor: '#64748b',
              color: '#ffffff',
              borderRadius: '4px',
            }}>
              NOT EVALUATED
            </span>
            <div style={{ fontSize: '16px', fontWeight: 700, color: '#334155', margin: '10px 0 6px 0' }}>
              Telemetry Not Wired
            </div>
            <div style={{ fontSize: '14px', color: '#475569', lineHeight: 1.5 }}>
              Specific dynamic instrument checks lack live telemetry in the active snapshot (e.g., dynamic anti-surge head map curves).
            </div>
          </div>
        </div>
      </div>

      {/* SECTION 4: WHEN NOT TO USE SCENARIO RESULTS */}
      <div style={{
        backgroundColor: '#ffffff',
        border: '1px solid #cbd5e1',
        borderRadius: '8px',
        padding: '24px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.05)',
      }}>
        <h2 style={{ margin: '0 0 8px 0', fontSize: '20px', fontWeight: 700, color: '#dc2626' }}>
          When NOT to Implement Scenario Recommendations
        </h2>
        <div style={{ fontSize: '15px', color: '#64748b', marginBottom: '16px' }}>
          Scenario recommendations must NEVER be implemented as plant operational setpoints if any of the following occur:
        </div>

        <ul style={{ margin: 0, paddingLeft: '24px', fontSize: '15px', color: '#334155', lineHeight: 1.7 }}>
          <li>
            <strong>Any FAILED indicator appears on safety interlock cards:</strong> Violation of compressor flow floor, suction drum TAL, superheat, or MCHE differential pressure.
          </li>
          <li>
            <strong>Mahalanobis Distance DM &gt; 3.0802:</strong> Target composition lies outside the 95% confidence operating ellipsoid (unsafe extrapolation alert).
          </li>
          <li>
            <strong>Severe compressor transient events:</strong> Train is undergoing startup, emergency shutdown (ESD), partial turbine trip, or aerodynamic surge hunting.
          </li>
          <li>
            <strong>DCS telemetry or online GC failure:</strong> Online chromatograph (AI25A-H) is offline or flow/pressure transmitters indicate bad quality status.
          </li>
          <li>
            <strong>Absence of Shift Supervisor approval:</strong> All refrigerant recipe adjustments require rigorous engineering verification and written operational authorization.
          </li>
        </ul>
      </div>

      {/* Footer Plant Identification (Demo Version) */}
      <div style={{
        backgroundColor: '#0f172a',
        borderRadius: '8px',
        padding: '18px 24px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '12px',
        color: '#f8fafc',
      }}>
        <div>
          <div style={{ fontSize: '16px', fontWeight: 700 }}>
            C3MR Liquefaction Optimization System | Decision-Support Workspace
          </div>
          <div style={{ fontSize: '14px', color: '#94a3b8', marginTop: '2px' }}>
            Train H LNG Liquefaction Unit (Engineering Demonstration Suite)
          </div>
        </div>
        <div style={{ fontSize: '13px', color: '#94a3b8', textAlign: 'right' }}>
          <div>Software Version: 2.0.0 (Operator Decision-Support System)</div>
          <div>Battery Limit: Total Train C3MR Shaft Power (MCR 4KT-2/3 + C3 4KT-1)</div>
        </div>
      </div>
    </div>
  );
};
