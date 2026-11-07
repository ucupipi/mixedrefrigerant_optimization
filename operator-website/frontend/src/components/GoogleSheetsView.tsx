import React, { useState } from 'react';
import type { DemoSnapshot, PredictResponse, ScenarioInput } from '../types';

interface GoogleSheetsViewProps {
  snapshot: DemoSnapshot;
  scenario: ScenarioInput;
  prediction: PredictResponse | null;
  onScenarioChange: (key: keyof ScenarioInput, value: number) => void;
  onReset: () => void;
  onCalculate: () => void;
  loading: boolean;
  onExportCsv: () => void;
}

export const GoogleSheetsView: React.FC<GoogleSheetsViewProps> = ({
  snapshot,
  scenario,
  prediction,
  onScenarioChange,
  onReset,
  onCalculate,
  loading,
  onExportCsv,
}) => {
  const [selectedCell, setSelectedCell] = useState<{ row: number; col: string; name: string; formula: string }>({
    row: 5,
    col: 'D',
    name: 'D5',
    formula: '=INPUT_FEED_FLOW(H3FI0004)',
  });

  const [transitionHours, setTransitionHours] = useState<number>(2.0);

  const handleCellClick = (row: number, col: string, name: string, formula: string) => {
    setSelectedCell({ row, col, name, formula });
  };

  const currentPower = prediction ? prediction.prediction.total_shaft_power_mw : 84.15;
  const baselinePower = snapshot.baseline_model_output?.total_shaft_power_mw ?? 84.15;
  const deltaPower = currentPower - baselinePower;
  const deltaPct = (deltaPower / baselinePower) * 100;
  const sec = prediction?.prediction.sec_kwh_per_t ?? (currentPower * 1000 / scenario.feed_flow_t_h);

  const compSum = (
    scenario.comp_N2_molpct +
    scenario.comp_C1_molpct +
    scenario.comp_C2_molpct +
    scenario.comp_C2H4_molpct +
    scenario.comp_C3_molpct
  );

  const makeup = prediction?.makeup_advisory;

  return (
    <div style={{
      backgroundColor: '#ffffff',
      border: '1px solid #dadce0',
      borderRadius: '8px',
      overflow: 'hidden',
      boxShadow: '0 1px 3px rgba(60,64,67,0.15)',
      fontFamily: 'Roboto, Arial, sans-serif',
      color: '#202124'
    }}>
      {/* 1. Google Sheets App Header Bar */}
      <div style={{
        padding: '10px 16px',
        backgroundColor: '#ffffff',
        borderBottom: '1px solid #e8eaed',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '10px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          {/* Sheets Icon */}
          <div style={{
            width: '36px',
            height: '36px',
            backgroundColor: '#0f9d58',
            borderRadius: '4px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#ffffff',
            fontWeight: 900,
            fontSize: '1.2rem'
          }}>
            ⊞
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: '1.05rem', fontWeight: 600, color: '#202124' }}>
                Badak_LNG_Plant3_TrainH_C3MR_Optimization_Advisory.xlsx
              </span>
              <span style={{
                fontSize: '0.7rem',
                backgroundColor: '#e6f4ea',
                color: '#137333',
                padding: '2px 8px',
                borderRadius: '4px',
                fontWeight: 600
              }}>
                HANYA BACA (READ-ONLY)
              </span>
            </div>
            {/* Menu items */}
            <div style={{ display: 'flex', gap: '14px', fontSize: '0.8rem', color: '#5f6368', marginTop: '4px' }}>
              <span style={{ cursor: 'pointer' }}>File</span>
              <span style={{ cursor: 'pointer' }}>Edit</span>
              <span style={{ cursor: 'pointer' }}>Tampilan</span>
              <span style={{ cursor: 'pointer' }}>Sisipkan</span>
              <span style={{ cursor: 'pointer' }}>Format</span>
              <span style={{ cursor: 'pointer' }}>Data</span>
              <span style={{ cursor: 'pointer', color: '#0f9d58', fontWeight: 600 }}>Simulasi ML</span>
              <span style={{ cursor: 'pointer' }}>Bantuan</span>
            </div>
          </div>
        </div>

        {/* Action Buttons Toolbar */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.8rem', color: '#5f6368' }}>
            <span>Durasi Injeksi:</span>
            <select
              value={transitionHours}
              onChange={(e) => {
                const val = parseFloat(e.target.value);
                setTransitionHours(val);
                onScenarioChange('transition_hours', val);
              }}
              style={{
                padding: '5px 8px',
                borderRadius: '4px',
                border: '1px solid #dadce0',
                fontSize: '0.8rem',
                fontWeight: 600,
                backgroundColor: '#f8f9fa'
              }}
            >
              <option value={1.0}>1.0 Jam (Cepat)</option>
              <option value={2.0}>2.0 Jam (Standar SOP)</option>
              <option value={4.0}>4.0 Jam (Konservatif)</option>
            </select>
          </div>

          <button
            onClick={onCalculate}
            disabled={loading}
            style={{
              backgroundColor: '#0f9d58',
              color: '#ffffff',
              border: 'none',
              padding: '8px 16px',
              borderRadius: '4px',
              fontWeight: 600,
              fontSize: '0.85rem',
              cursor: loading ? 'not-allowed' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              boxShadow: '0 1px 2px rgba(0,0,0,0.1)'
            }}
          >
            {loading ? 'Menghitung...' : '⚡ Hitung Simulasi (ML)'}
          </button>

          <button
            onClick={onReset}
            style={{
              backgroundColor: '#ffffff',
              color: '#5f6368',
              border: '1px solid #dadce0',
              padding: '8px 12px',
              borderRadius: '4px',
              fontWeight: 600,
              fontSize: '0.85rem',
              cursor: 'pointer'
            }}
          >
            ↺ Reset ke DCS
          </button>

          <button
            onClick={onExportCsv}
            style={{
              backgroundColor: '#ffffff',
              color: '#1a73e8',
              border: '1px solid #dadce0',
              padding: '8px 12px',
              borderRadius: '4px',
              fontWeight: 600,
              fontSize: '0.85rem',
              cursor: 'pointer'
            }}
          >
            📥 Unduh Excel / CSV
          </button>
        </div>
      </div>

      {/* 2. Formula Bar */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        padding: '6px 14px',
        backgroundColor: '#f8f9fa',
        borderBottom: '1px solid #e8eaed',
        gap: '8px',
        fontSize: '0.85rem'
      }}>
        <div style={{
          minWidth: '55px',
          padding: '4px 8px',
          backgroundColor: '#ffffff',
          border: '1px solid #dadce0',
          borderRadius: '3px',
          textAlign: 'center',
          fontWeight: 700,
          color: '#202124',
          fontFamily: 'monospace'
        }}>
          {selectedCell.name}
        </div>
        <div style={{ color: '#80868b', fontWeight: 700, fontStyle: 'italic', padding: '0 4px' }}>
          fx
        </div>
        <div style={{
          flex: 1,
          padding: '4px 10px',
          backgroundColor: '#ffffff',
          border: '1px solid #dadce0',
          borderRadius: '3px',
          color: '#3c4043',
          fontFamily: 'monospace',
          fontSize: '0.82rem'
        }}>
          {selectedCell.formula}
        </div>
      </div>

      {/* 3. Authentic Spreadsheet Grid Table */}
      <div style={{ overflowX: 'auto', maxHeight: '720px' }}>
        <table style={{
          width: '100%',
          borderCollapse: 'collapse',
          fontSize: '0.85rem',
          userSelect: 'none'
        }}>
          <thead>
            <tr style={{ backgroundColor: '#f8f9fa', color: '#5f6368', textAlign: 'center' }}>
              <th style={{ width: '40px', border: '1px solid #e0e0e0', padding: '6px 0', fontSize: '0.75rem' }}></th>
              <th style={{ width: '130px', border: '1px solid #e0e0e0', padding: '6px 8px', fontSize: '0.75rem' }}>A (Tag DCS)</th>
              <th style={{ minWidth: '220px', border: '1px solid #e0e0e0', padding: '6px 8px', fontSize: '0.75rem', textAlign: 'left' }}>B (Nama Parameter)</th>
              <th style={{ width: '140px', border: '1px solid #e0e0e0', padding: '6px 8px', fontSize: '0.75rem', textAlign: 'right' }}>C (Kondisi Aktual DCS)</th>
              <th style={{ width: '170px', border: '1px solid #e0e0e0', padding: '6px 8px', fontSize: '0.75rem', textAlign: 'right', backgroundColor: '#e8f0fe', color: '#1a73e8', fontWeight: 700 }}>
                D (Nilai Skenario Target)
              </th>
              <th style={{ width: '85px', border: '1px solid #e0e0e0', padding: '6px 8px', fontSize: '0.75rem' }}>E (Satuan)</th>
              <th style={{ width: '190px', border: '1px solid #e0e0e0', padding: '6px 8px', fontSize: '0.75rem', textAlign: 'left' }}>F (Status / Rekomendasi)</th>
              <th style={{ minWidth: '240px', border: '1px solid #e0e0e0', padding: '6px 8px', fontSize: '0.75rem', textAlign: 'left' }}>G (Batas Operasi & Panduan)</th>
            </tr>
          </thead>
          <tbody>
            {/* ========================================================================= */}
            {/* SEKSI 1: INPUT SKENARIO OPERATOR */}
            {/* ========================================================================= */}
            <tr style={{ backgroundColor: '#1a73e8', color: '#ffffff', fontWeight: 700, fontSize: '0.8rem' }}>
              <td style={{ border: '1px solid #1557b0', textAlign: 'center', backgroundColor: '#1557b0' }}>4</td>
              <td colSpan={7} style={{ padding: '6px 12px', letterSpacing: '0.04em' }}>
                📁 SEKSI 1 - INPUT SKENARIO OPERATOR (WHAT-IF PARAMETERS - DAPAT DIEDIT)
              </td>
            </tr>

            {/* Row 5: Feed Flow */}
            <tr onClick={() => handleCellClick(5, 'D', 'D5', '=INPUT_FEED_FLOW(H3FI0004)')}>
              <td style={{ backgroundColor: '#f8f9fa', border: '1px solid #e0e0e0', textAlign: 'center', color: '#70757a', fontSize: '0.75rem' }}>5</td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', fontFamily: 'monospace', fontWeight: 600, color: '#1a73e8' }}>H3FI0004</td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', fontWeight: 600 }}>Laju Alir Umpan Gas Alam (Feed Gas)</td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', textAlign: 'right', fontFamily: 'monospace' }}>245.8</td>
              <td style={{ border: '1px solid #e0e0e0', padding: '4px 6px', textAlign: 'right', backgroundColor: '#e8f0fe' }}>
                <input
                  type="number"
                  step="1.0"
                  value={scenario.feed_flow_t_h}
                  onChange={(e) => onScenarioChange('feed_flow_t_h', parseFloat(e.target.value) || 0)}
                  style={{
                    width: '100%',
                    border: selectedCell.name === 'D5' ? '2px solid #1a73e8' : '1px solid #aecbfa',
                    backgroundColor: '#ffffff',
                    padding: '4px 6px',
                    borderRadius: '2px',
                    textAlign: 'right',
                    fontFamily: 'monospace',
                    fontWeight: 700,
                    color: '#1a73e8',
                    outline: 'none'
                  }}
                />
              </td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', textAlign: 'center', color: '#5f6368' }}>t/h</td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', color: '#137333', fontWeight: 600 }}>INPUT AKTIF</td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', color: '#5f6368', fontSize: '0.78rem' }}>Rentang pelatihan valid: 130 - 340 t/h</td>
            </tr>

            {/* Row 6: MCR Flow */}
            <tr onClick={() => handleCellClick(6, 'D', 'D6', '=INPUT_MCR_FLOW(H4FI001)')}>
              <td style={{ backgroundColor: '#f8f9fa', border: '1px solid #e0e0e0', textAlign: 'center', color: '#70757a', fontSize: '0.75rem' }}>6</td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', fontFamily: 'monospace', fontWeight: 600, color: '#1a73e8' }}>H4FI001</td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', fontWeight: 600 }}>Laju Alir Sirkulasi MCR ke MCHE</td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', textAlign: 'right', fontFamily: 'monospace' }}>562.3</td>
              <td style={{ border: '1px solid #e0e0e0', padding: '4px 6px', textAlign: 'right', backgroundColor: '#e8f0fe' }}>
                <input
                  type="number"
                  step="1.0"
                  value={scenario.mcr_flow_t_h}
                  onChange={(e) => onScenarioChange('mcr_flow_t_h', parseFloat(e.target.value) || 0)}
                  style={{
                    width: '100%',
                    border: selectedCell.name === 'D6' ? '2px solid #1a73e8' : '1px solid #aecbfa',
                    backgroundColor: '#ffffff',
                    padding: '4px 6px',
                    borderRadius: '2px',
                    textAlign: 'right',
                    fontFamily: 'monospace',
                    fontWeight: 700,
                    color: '#1a73e8',
                    outline: 'none'
                  }}
                />
              </td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', textAlign: 'center', color: '#5f6368' }}>t/h</td>
              <td style={{
                border: '1px solid #e0e0e0',
                padding: '5px 8px',
                fontWeight: 600,
                color: scenario.mcr_flow_t_h >= 480.0 ? '#137333' : '#c5221f'
              }}>
                {scenario.mcr_flow_t_h >= 480.0 ? '≥ 480.0 (AMAN)' : '⚠️ DI BAWAH SURGE'}
              </td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', color: '#5f6368', fontSize: '0.78rem' }}>Batas anti-surge: ≥ 480.0 t/h (4UV-53 modulasi jika &lt; 480)</td>
            </tr>

            {/* Row 7: N2 */}
            <tr onClick={() => handleCellClick(7, 'D', 'D7', '=INPUT_COMP_N2(comp_4C-8_N2)')}>
              <td style={{ backgroundColor: '#f8f9fa', border: '1px solid #e0e0e0', textAlign: 'center', color: '#70757a', fontSize: '0.75rem' }}>7</td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', fontFamily: 'monospace', color: '#5f6368' }}>comp_4C-8_N2</td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px' }}>MCR Nitrogen (N2) Fraction</td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', textAlign: 'right', fontFamily: 'monospace' }}>3.38</td>
              <td style={{ border: '1px solid #e0e0e0', padding: '4px 6px', textAlign: 'right', backgroundColor: '#e8f0fe' }}>
                <input
                  type="number"
                  step="0.01"
                  value={scenario.comp_N2_molpct}
                  onChange={(e) => onScenarioChange('comp_N2_molpct', parseFloat(e.target.value) || 0)}
                  style={{
                    width: '100%',
                    border: selectedCell.name === 'D7' ? '2px solid #1a73e8' : '1px solid #aecbfa',
                    backgroundColor: '#ffffff',
                    padding: '4px 6px',
                    borderRadius: '2px',
                    textAlign: 'right',
                    fontFamily: 'monospace',
                    fontWeight: 700,
                    color: '#1a73e8',
                    outline: 'none'
                  }}
                />
              </td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', textAlign: 'center', color: '#5f6368' }}>mol%</td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', color: '#137333', fontSize: '0.8rem' }}>Kromatografi Gas</td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', color: '#5f6368', fontSize: '0.78rem' }}>Mengontrol suhu cold bundle MCHE & TAL</td>
            </tr>

            {/* Row 8: C1 */}
            <tr onClick={() => handleCellClick(8, 'D', 'D8', '=INPUT_COMP_C1(comp_4C-8_C1)')}>
              <td style={{ backgroundColor: '#f8f9fa', border: '1px solid #e0e0e0', textAlign: 'center', color: '#70757a', fontSize: '0.75rem' }}>8</td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', fontFamily: 'monospace', color: '#5f6368' }}>comp_4C-8_C1</td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px' }}>MCR Metana (CH4) Fraction</td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', textAlign: 'right', fontFamily: 'monospace' }}>44.37</td>
              <td style={{ border: '1px solid #e0e0e0', padding: '4px 6px', textAlign: 'right', backgroundColor: '#e8f0fe' }}>
                <input
                  type="number"
                  step="0.01"
                  value={scenario.comp_C1_molpct}
                  onChange={(e) => onScenarioChange('comp_C1_molpct', parseFloat(e.target.value) || 0)}
                  style={{
                    width: '100%',
                    border: selectedCell.name === 'D8' ? '2px solid #1a73e8' : '1px solid #aecbfa',
                    backgroundColor: '#ffffff',
                    padding: '4px 6px',
                    borderRadius: '2px',
                    textAlign: 'right',
                    fontFamily: 'monospace',
                    fontWeight: 700,
                    color: '#1a73e8',
                    outline: 'none'
                  }}
                />
              </td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', textAlign: 'center', color: '#5f6368' }}>mol%</td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', color: '#137333', fontSize: '0.8rem' }}>Kromatografi Gas</td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', color: '#5f6368', fontSize: '0.78rem' }}>Subcooling LNG rundown; rentang: 35 - 55%</td>
            </tr>

            {/* Row 9: C2 */}
            <tr onClick={() => handleCellClick(9, 'D', 'D9', '=INPUT_COMP_C2(comp_4C-8_C2)')}>
              <td style={{ backgroundColor: '#f8f9fa', border: '1px solid #e0e0e0', textAlign: 'center', color: '#70757a', fontSize: '0.75rem' }}>9</td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', fontFamily: 'monospace', color: '#5f6368' }}>comp_4C-8_C2</td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px' }}>MCR Etana (C2H6) Fraction</td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', textAlign: 'right', fontFamily: 'monospace' }}>44.94</td>
              <td style={{ border: '1px solid #e0e0e0', padding: '4px 6px', textAlign: 'right', backgroundColor: '#e8f0fe' }}>
                <input
                  type="number"
                  step="0.01"
                  value={scenario.comp_C2_molpct}
                  onChange={(e) => onScenarioChange('comp_C2_molpct', parseFloat(e.target.value) || 0)}
                  style={{
                    width: '100%',
                    border: selectedCell.name === 'D9' ? '2px solid #1a73e8' : '1px solid #aecbfa',
                    backgroundColor: '#ffffff',
                    padding: '4px 6px',
                    borderRadius: '2px',
                    textAlign: 'right',
                    fontFamily: 'monospace',
                    fontWeight: 700,
                    color: '#1a73e8',
                    outline: 'none'
                  }}
                />
              </td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', textAlign: 'center', color: '#5f6368' }}>mol%</td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', color: '#137333', fontSize: '0.8rem' }}>Kromatografi Gas</td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', color: '#5f6368', fontSize: '0.78rem' }}>Pendinginan bundle tengah; rentang: 30 - 55%</td>
            </tr>

            {/* Row 10: C2H4 */}
            <tr onClick={() => handleCellClick(10, 'D', 'D10', '=INPUT_COMP_C2H4(comp_4C-8_C2H4)')}>
              <td style={{ backgroundColor: '#f8f9fa', border: '1px solid #e0e0e0', textAlign: 'center', color: '#70757a', fontSize: '0.75rem' }}>10</td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', fontFamily: 'monospace', color: '#5f6368' }}>comp_4C-8_C2H4</td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px' }}>MCR Etilena (C2H4) Fraction</td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', textAlign: 'right', fontFamily: 'monospace' }}>0.85</td>
              <td style={{ border: '1px solid #e0e0e0', padding: '4px 6px', textAlign: 'right', backgroundColor: '#e8f0fe' }}>
                <input
                  type="number"
                  step="0.01"
                  value={scenario.comp_C2H4_molpct}
                  onChange={(e) => onScenarioChange('comp_C2H4_molpct', parseFloat(e.target.value) || 0)}
                  style={{
                    width: '100%',
                    border: selectedCell.name === 'D10' ? '2px solid #1a73e8' : '1px solid #aecbfa',
                    backgroundColor: '#ffffff',
                    padding: '4px 6px',
                    borderRadius: '2px',
                    textAlign: 'right',
                    fontFamily: 'monospace',
                    fontWeight: 700,
                    color: '#1a73e8',
                    outline: 'none'
                  }}
                />
              </td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', textAlign: 'center', color: '#5f6368' }}>mol%</td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', color: '#137333', fontSize: '0.8rem' }}>Kromatografi Gas</td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', color: '#5f6368', fontSize: '0.78rem' }}>Modifikasi kurva transisi; rentang: 0 - 45%</td>
            </tr>

            {/* Row 11: C3 */}
            <tr onClick={() => handleCellClick(11, 'D', 'D11', '=INPUT_COMP_C3(comp_4C-8_C3)')}>
              <td style={{ backgroundColor: '#f8f9fa', border: '1px solid #e0e0e0', textAlign: 'center', color: '#70757a', fontSize: '0.75rem' }}>11</td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', fontFamily: 'monospace', color: '#5f6368' }}>comp_4C-8_C3</td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px' }}>MCR Propana (C3H8) Fraction</td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', textAlign: 'right', fontFamily: 'monospace' }}>6.28</td>
              <td style={{ border: '1px solid #e0e0e0', padding: '4px 6px', textAlign: 'right', backgroundColor: '#e8f0fe' }}>
                <input
                  type="number"
                  step="0.01"
                  value={scenario.comp_C3_molpct}
                  onChange={(e) => onScenarioChange('comp_C3_molpct', parseFloat(e.target.value) || 0)}
                  style={{
                    width: '100%',
                    border: selectedCell.name === 'D11' ? '2px solid #1a73e8' : '1px solid #aecbfa',
                    backgroundColor: '#ffffff',
                    padding: '4px 6px',
                    borderRadius: '2px',
                    textAlign: 'right',
                    fontFamily: 'monospace',
                    fontWeight: 700,
                    color: '#1a73e8',
                    outline: 'none'
                  }}
                />
              </td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', textAlign: 'center', color: '#5f6368' }}>mol%</td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', color: '#137333', fontSize: '0.8rem' }}>Kromatografi Gas</td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', color: '#5f6368', fontSize: '0.78rem' }}>Pendinginan warm end; rentang: 0 - 12%</td>
            </tr>

            {/* Row 12: Total MCR Sum */}
            <tr style={{ backgroundColor: '#f1f3f4', fontWeight: 700 }}>
              <td style={{ backgroundColor: '#f8f9fa', border: '1px solid #e0e0e0', textAlign: 'center', color: '#70757a', fontSize: '0.75rem' }}>12</td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', fontFamily: 'monospace' }}>TOTAL_COMP</td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px' }}>Total Penjumlahan Komposisi MCR</td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', textAlign: 'right', fontFamily: 'monospace' }}>99.82</td>
              <td style={{
                border: '1px solid #e0e0e0',
                padding: '5px 8px',
                textAlign: 'right',
                fontFamily: 'monospace',
                color: Math.abs(compSum - 100.0) < 0.5 ? '#137333' : '#b06000'
              }}>
                {compSum.toFixed(2)}
              </td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', textAlign: 'center' }}>mol%</td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', color: Math.abs(compSum - 100.0) < 0.5 ? '#137333' : '#b06000' }}>
                {Math.abs(compSum - 100.0) < 0.5 ? 'SEIMBANG (100%)' : 'NORMALISASI OTOMATIS'}
              </td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', color: '#5f6368', fontSize: '0.78rem' }}>Wajib mendekati 100.0 mol% (Simpleks S5)</td>
            </tr>

            {/* ========================================================================= */}
            {/* SEKSI 2: HASIL PREDIKSI DAYA & SEC (OUTPUT) */}
            {/* ========================================================================= */}
            <tr style={{ backgroundColor: '#0f9d58', color: '#ffffff', fontWeight: 700, fontSize: '0.8rem' }}>
              <td style={{ border: '1px solid #0b8043', textAlign: 'center', backgroundColor: '#0b8043' }}>14</td>
              <td colSpan={7} style={{ padding: '6px 12px', letterSpacing: '0.04em' }}>
                📊 SEKSI 2 - HASIL PREDIKSI DAYA & EFISIENSI MODEL ML (OUTPUT SISTEM)
              </td>
            </tr>

            {/* Row 15: Total Power */}
            <tr onClick={() => handleCellClick(15, 'D', 'D15', '=SURROGATE_PREDICT_POWER(D5:D11)')} style={{ backgroundColor: '#e6f4ea' }}>
              <td style={{ backgroundColor: '#f8f9fa', border: '1px solid #e0e0e0', textAlign: 'center', color: '#70757a', fontSize: '0.75rem' }}>15</td>
              <td style={{ border: '1px solid #e0e0e0', padding: '6px 8px', fontFamily: 'monospace', fontWeight: 700, color: '#0f9d58' }}>TOTAL_POWER</td>
              <td style={{ border: '1px solid #e0e0e0', padding: '6px 8px', fontWeight: 700, color: '#137333' }}>
                Total Daya Poros Kompresor C3MR (4KT-1 + 4KT-2/3)
              </td>
              <td style={{ border: '1px solid #e0e0e0', padding: '6px 8px', textAlign: 'right', fontFamily: 'monospace', fontWeight: 700 }}>
                {baselinePower.toFixed(2)}
              </td>
              <td style={{
                border: selectedCell.name === 'D15' ? '2px solid #0f9d58' : '1px solid #e0e0e0',
                padding: '6px 8px',
                textAlign: 'right',
                fontFamily: 'monospace',
                fontSize: '1rem',
                fontWeight: 800,
                color: '#137333',
                backgroundColor: '#ceead6'
              }}>
                {currentPower.toFixed(2)}
              </td>
              <td style={{ border: '1px solid #e0e0e0', padding: '6px 8px', textAlign: 'center', fontWeight: 700, color: '#137333' }}>MW</td>
              <td style={{
                border: '1px solid #e0e0e0',
                padding: '6px 8px',
                fontWeight: 700,
                color: deltaPower <= 0 ? '#137333' : '#b06000'
              }}>
                {deltaPower <= 0 ? `HEMAT ${Math.abs(deltaPower).toFixed(2)} MW` : `NAIK +${deltaPower.toFixed(2)} MW`}
              </td>
              <td style={{ border: '1px solid #e0e0e0', padding: '6px 8px', color: '#5f6368', fontSize: '0.78rem' }}>
                Batas sistem: Total Train C3MR (Propana + MCR LP/HP)
              </td>
            </tr>

            {/* Row 16: Delta Power */}
            <tr onClick={() => handleCellClick(16, 'D', 'D16', '=(D15 - C15) / C15 * 100')}>
              <td style={{ backgroundColor: '#f8f9fa', border: '1px solid #e0e0e0', textAlign: 'center', color: '#70757a', fontSize: '0.75rem' }}>16</td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', fontFamily: 'monospace', color: '#5f6368' }}>DELTA_POWER</td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px' }}>Selisih Daya vs Baseline Aktual</td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', textAlign: 'right', color: '#80868b' }}>0.00 MW</td>
              <td style={{
                border: selectedCell.name === 'D16' ? '2px solid #0f9d58' : '1px solid #e0e0e0',
                padding: '5px 8px',
                textAlign: 'right',
                fontFamily: 'monospace',
                fontWeight: 700,
                color: deltaPower <= 0 ? '#137333' : '#b06000'
              }}>
                {deltaPower > 0 ? '+' : ''}{deltaPower.toFixed(2)} MW ({deltaPct > 0 ? '+' : ''}{deltaPct.toFixed(2)}%)
              </td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', textAlign: 'center', color: '#5f6368' }}>MW / %</td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', color: deltaPower <= 0 ? '#137333' : '#b06000', fontWeight: 600 }}>
                {deltaPower <= 0 ? 'EFISIENSI MENINGKAT' : 'BEBAN BERTAMBAH'}
              </td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', color: '#5f6368', fontSize: '0.78rem' }}>Penurunan daya poros menurunkan konsumsi uap boiler</td>
            </tr>

            {/* Row 17: SEC */}
            <tr onClick={() => handleCellClick(17, 'D', 'D17', '=D15 * 1000 / D5')}>
              <td style={{ backgroundColor: '#f8f9fa', border: '1px solid #e0e0e0', textAlign: 'center', color: '#70757a', fontSize: '0.75rem' }}>17</td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', fontFamily: 'monospace', color: '#5f6368' }}>SEC_RATIO</td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', fontWeight: 600 }}>Specific Energy Consumption (SEC)</td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', textAlign: 'right', fontFamily: 'monospace' }}>
                {(baselinePower * 1000 / 245.8).toFixed(1)}
              </td>
              <td style={{
                border: selectedCell.name === 'D17' ? '2px solid #0f9d58' : '1px solid #e0e0e0',
                padding: '5px 8px',
                textAlign: 'right',
                fontFamily: 'monospace',
                fontWeight: 700,
                color: '#202124'
              }}>
                {sec.toFixed(1)}
              </td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', textAlign: 'center', color: '#5f6368' }}>kWh/t</td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', color: '#137333' }}>Konsumsi Spesifik</td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', color: '#5f6368', fontSize: '0.78rem' }}>Rasio energi poros per ton umpan gas cair</td>
            </tr>

            {/* Row 18: Regime & Model Accuracy */}
            <tr onClick={() => handleCellClick(18, 'D', 'D18', '=GET_MODEL_ACCURACY("underload")')}>
              <td style={{ backgroundColor: '#f8f9fa', border: '1px solid #e0e0e0', textAlign: 'center', color: '#70757a', fontSize: '0.75rem' }}>18</td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', fontFamily: 'monospace', color: '#5f6368' }}>MODEL_METRICS</td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px' }}>Akurasi Model & Ketidakpastian (CI 95%)</td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', textAlign: 'right', color: '#80868b' }}>R² = 0.8365</td>
              <td style={{
                border: selectedCell.name === 'D18' ? '2px solid #0f9d58' : '1px solid #e0e0e0',
                padding: '5px 8px',
                textAlign: 'right',
                fontFamily: 'monospace',
                fontWeight: 600,
                color: '#137333'
              }}>
                ± 0.80 MW (0.93%)
              </td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', textAlign: 'center', color: '#5f6368' }}>MW</td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', color: '#137333' }}>TERVALIDASI</td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', color: '#5f6368', fontSize: '0.78rem' }}>Diuji pada 295 shift independen (MAE &lt; 1.0 MW)</td>
            </tr>

            {/* ========================================================================= */}
            {/* SEKSI 3: REKOMENDASI INJEKSI HYDROCARBON MAKE-UP (BARU!) */}
            {/* ========================================================================= */}
            <tr style={{ backgroundColor: '#e37400', color: '#ffffff', fontWeight: 700, fontSize: '0.8rem' }}>
              <td style={{ border: '1px solid #b06000', textAlign: 'center', backgroundColor: '#b06000' }}>20</td>
              <td colSpan={7} style={{ padding: '6px 12px', letterSpacing: '0.04em' }}>
                🛢️ SEKSI 3 - REKOMENDASI LAJU INJEKSI HYDROCARBON MAKE-UP (H4FIC005 - H4FIC007)
              </td>
            </tr>

            {/* Make-up Items */}
            {makeup?.items ? (
              makeup.items.map((item, idx) => {
                const rowNum = 21 + idx;
                const isInj = item.action === 'INJEKSI';
                return (
                  <tr
                    key={idx}
                    onClick={() => handleCellClick(rowNum, 'D', `D${rowNum}`, `=CALC_MAKEUP_FLOW("${item.component}", Durasi=${transitionHours}h)`)}
                    style={{ backgroundColor: isInj ? '#fef7e0' : '#ffffff' }}
                  >
                    <td style={{ backgroundColor: '#f8f9fa', border: '1px solid #e0e0e0', textAlign: 'center', color: '#70757a', fontSize: '0.75rem' }}>{rowNum}</td>
                    <td style={{ border: '1px solid #e0e0e0', padding: '6px 8px', fontFamily: 'monospace', fontWeight: 700, color: '#e37400' }}>
                      {item.tag_dcs}
                    </td>
                    <td style={{ border: '1px solid #e0e0e0', padding: '6px 8px', fontWeight: 600 }}>
                      Injeksi {item.description}
                    </td>
                    <td style={{ border: '1px solid #e0e0e0', padding: '6px 8px', textAlign: 'right', fontFamily: 'monospace' }}>
                      {item.actual_molpct != null ? `${item.actual_molpct.toFixed(2)} mol%` : '-'}
                    </td>
                    <td style={{
                      border: selectedCell.name === `D${rowNum}` ? '2px solid #e37400' : '1px solid #e0e0e0',
                      padding: '6px 8px',
                      textAlign: 'right',
                      fontFamily: 'monospace',
                      fontWeight: 700,
                      color: isInj ? '#b06000' : '#80868b',
                      fontSize: '0.95rem'
                    }}>
                      {item.recommended_flow_nm3_h != null && item.recommended_flow_nm3_h > 0 ? `${item.recommended_flow_nm3_h.toFixed(1)} Nm³/h` : '0.0 Nm³/h'}
                    </td>
                    <td style={{ border: '1px solid #e0e0e0', padding: '6px 8px', textAlign: 'center', color: '#5f6368' }}>
                      {item.recommended_flow_kg_h != null && item.recommended_flow_kg_h > 0 ? `${item.recommended_flow_kg_h.toFixed(1)} kg/h` : '-'}
                    </td>
                    <td style={{
                      border: '1px solid #e0e0e0',
                      padding: '6px 8px',
                      fontWeight: 700,
                      color: isInj ? '#b06000' : '#137333'
                    }}>
                      {item.action === 'INJEKSI' ? `⚡ ${item.action}` : item.action}
                    </td>
                    <td style={{ border: '1px solid #e0e0e0', padding: '6px 8px', color: '#3c4043', fontSize: '0.78rem' }}>
                      {item.instruction}
                    </td>
                  </tr>
                );
              })
            ) : (
              <tr>
                <td colSpan={8} style={{ padding: '12px', textAlign: 'center', color: '#80868b' }}>
                  Klik tombol <strong>Hitung Simulasi</strong> untuk menghitung laju injeksi make-up refrigeran.
                </td>
              </tr>
            )}

            {/* Total Makeup summary row */}
            {makeup && (
              <tr style={{ backgroundColor: '#fef7e0', fontWeight: 700 }}>
                <td style={{ backgroundColor: '#f8f9fa', border: '1px solid #e0e0e0', textAlign: 'center', color: '#70757a', fontSize: '0.75rem' }}>25</td>
                <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', fontFamily: 'monospace', color: '#e37400' }}>TOTAL_MAKEUP</td>
                <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px' }}>Total Laju Alir Injeksi Hidrokarbon / N2</td>
                <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', textAlign: 'right', color: '#80868b' }}>-</td>
                <td style={{
                  border: '1px solid #e0e0e0',
                  padding: '5px 8px',
                  textAlign: 'right',
                  fontFamily: 'monospace',
                  color: '#b06000',
                  fontSize: '0.95rem'
                }}>
                  {makeup.total_makeup_flow_nm3_h != null ? `${makeup.total_makeup_flow_nm3_h.toFixed(1)} Nm³/h` : '-'}
                </td>
                <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', textAlign: 'center', color: '#b06000' }}>
                  {makeup.total_makeup_flow_kg_h != null ? `${makeup.total_makeup_flow_kg_h.toFixed(1)} kg/h` : '-'}
                </td>
                <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', color: '#b06000' }}>
                  DURASI {transitionHours.toFixed(1)} JAM
                </td>
                <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', color: '#5f6368', fontSize: '0.78rem' }}>
                  Total massa make-up yang ditambahkan ke active loop inventory (~24.000 kg)
                </td>
              </tr>
            )}

            {/* ========================================================================= */}
            {/* SEKSI 4: AUDIT KESELAMATAN & INTERLOCK OPERASI */}
            {/* ========================================================================= */}
            <tr style={{ backgroundColor: '#5f6368', color: '#ffffff', fontWeight: 700, fontSize: '0.8rem' }}>
              <td style={{ border: '1px solid #3c4043', textAlign: 'center', backgroundColor: '#3c4043' }}>27</td>
              <td colSpan={7} style={{ padding: '6px 12px', letterSpacing: '0.04em' }}>
                🛡️ SEKSI 4 - AUDIT BATAS KESELAMATAN KILANG & JARAK MAHALANOBIS (SAFETY INTERLOCKS)
              </td>
            </tr>

            {/* Row 28: Mahalanobis Distance */}
            <tr onClick={() => handleCellClick(28, 'D', 'D28', '=MAHALANOBIS_DISTANCE(D7:D11)')}>
              <td style={{ backgroundColor: '#f8f9fa', border: '1px solid #e0e0e0', textAlign: 'center', color: '#70757a', fontSize: '0.75rem' }}>28</td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', fontFamily: 'monospace', color: '#5f6368' }}>D_M_ENVELOPE</td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', fontWeight: 600 }}>Jarak Mahalanobis Komposisi MCR</td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', textAlign: 'right', color: '#80868b' }}>1.025</td>
              <td style={{
                border: selectedCell.name === 'D28' ? '2px solid #5f6368' : '1px solid #e0e0e0',
                padding: '5px 8px',
                textAlign: 'right',
                fontFamily: 'monospace',
                fontWeight: 700,
                color: (prediction?.domain_check.in_domain ?? true) ? '#137333' : '#c5221f'
              }}>
                {prediction ? prediction.domain_check.mahalanobis_distance.toFixed(3) : '1.025'}
              </td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', textAlign: 'center', color: '#5f6368' }}>-</td>
              <td style={{
                border: '1px solid #e0e0e0',
                padding: '5px 8px',
                fontWeight: 700,
                color: (prediction?.domain_check.in_domain ?? true) ? '#137333' : '#c5221f'
              }}>
                {(prediction?.domain_check.in_domain ?? true) ? '✅ DALAM DOMAIN' : '⚠️ DI LUAR DOMAIN'}
              </td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', color: '#5f6368', fontSize: '0.78rem' }}>
                Batas kritis χ²: ≤ 3.0802 (Elipsoid kepercayaan 95% kilang)
              </td>
            </tr>

            {/* Row 29: Anti-Surge */}
            <tr onClick={() => handleCellClick(29, 'D', 'D29', '=IF(D6>=480,"SAFE","SURGE_WARNING")')}>
              <td style={{ backgroundColor: '#f8f9fa', border: '1px solid #e0e0e0', textAlign: 'center', color: '#70757a', fontSize: '0.75rem' }}>29</td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', fontFamily: 'monospace', color: '#5f6368' }}>4UV-53_FLOOR</td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px' }}>Anti-Surge Safe Operating Floor</td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', textAlign: 'right', fontFamily: 'monospace' }}>562.3</td>
              <td style={{
                border: '1px solid #e0e0e0',
                padding: '5px 8px',
                textAlign: 'right',
                fontFamily: 'monospace',
                fontWeight: 700,
                color: scenario.mcr_flow_t_h >= 480.0 ? '#137333' : '#c5221f'
              }}>
                {scenario.mcr_flow_t_h.toFixed(1)}
              </td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', textAlign: 'center', color: '#5f6368' }}>t/h</td>
              <td style={{
                border: '1px solid #e0e0e0',
                padding: '5px 8px',
                fontWeight: 700,
                color: scenario.mcr_flow_t_h >= 480.0 ? '#137333' : '#c5221f'
              }}>
                {scenario.mcr_flow_t_h >= 480.0 ? '✅ MEMENUHI' : '⛔ PELANGGARAN'}
              </td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', color: '#5f6368', fontSize: '0.78rem' }}>
                Batas minimum: ≥ 480.0 t/h (Kickback valve 4UV-53 modulasi jika &lt; 480)
              </td>
            </tr>

            {/* Row 30: TAL Suction */}
            <tr onClick={() => handleCellClick(30, 'D', 'D30', '=IF(H4TI004B>=-45,"SAFE","TAL_TRIP")')}>
              <td style={{ backgroundColor: '#f8f9fa', border: '1px solid #e0e0e0', textAlign: 'center', color: '#70757a', fontSize: '0.75rem' }}>30</td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', fontFamily: 'monospace', color: '#5f6368' }}>H4TI004B_TAL</td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px' }}>Suction Drum 4C-8 Temperature Alarm Low</td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', textAlign: 'right', fontFamily: 'monospace' }}>-40.5</td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', textAlign: 'right', fontFamily: 'monospace', fontWeight: 700, color: '#137333' }}>
                -40.5
              </td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', textAlign: 'center', color: '#5f6368' }}>°C</td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', fontWeight: 700, color: '#137333' }}>
                ✅ AMAN (&gt; -45 °C)
              </td>
              <td style={{ border: '1px solid #e0e0e0', padding: '5px 8px', color: '#5f6368', fontSize: '0.78rem' }}>
                Batas TAL: ≥ -45.0 °C (Mencegah liquid carryover ke kompresor 4K-2)
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      {/* 4. Bottom Sheet Tabs (Google Sheets Style) */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        backgroundColor: '#f8f9fa',
        borderTop: '1px solid #dadce0',
        padding: '0 12px',
        gap: '4px'
      }}>
        <div style={{
          padding: '8px 16px',
          backgroundColor: '#ffffff',
          borderLeft: '1px solid #dadce0',
          borderRight: '1px solid #dadce0',
          borderTop: '2px solid #0f9d58',
          fontWeight: 700,
          color: '#0f9d58',
          fontSize: '0.8rem',
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          cursor: 'pointer'
        }}>
          <span>⊞</span> Sheet1: Skenario & Rekomendasi Injeksi
        </div>
      </div>
    </div>
  );
};

