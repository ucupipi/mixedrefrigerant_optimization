import React from 'react';
import type { DemoSnapshot, PredictResponse, ScenarioInput } from '../types';

interface SpreadsheetTableProps {
  snapshot: DemoSnapshot;
  scenario: ScenarioInput;
  prediction: PredictResponse | null;
  onScenarioChange: (key: keyof ScenarioInput, value: number) => void;
  onReset: () => void;
  onCalculate: () => void;
  loading: boolean;
  onExportCsv: () => void;
}

export const SpreadsheetTable: React.FC<SpreadsheetTableProps> = ({
  snapshot,
  scenario,
  prediction,
  onScenarioChange,
  onReset,
  onCalculate,
  loading,
  onExportCsv,
}) => {
  const v = snapshot.values;

  // Group definitions
  const rows = [
    // Group 1: Feed Gas
    {
      group: 'Umpan Gas Alam',
      name: 'Laju Alir Umpan Gas (Scrub Column Overhead)',
      tag: 'H1FI012',
      actual: v.H1FI012?.value ?? 245.8,
      scenarioKey: 'feed_flow_t_h' as keyof ScenarioInput,
      scenarioVal: scenario.feed_flow_t_h,
      unit: 't/h',
      editable: true,
      status: 'DEMO (DCS)',
      note: 'Variabel utama kapasitas produksi. Rentang data valid: 130 – 340 t/h.',
    },
    // Group 2: MCR Compressor
    {
      group: 'Kompresor MCR',
      name: 'Laju Alir Sirkulasi MCR ke MCHE',
      tag: 'H4FI001',
      actual: v.H4FI001?.value ?? 562.3,
      scenarioKey: 'mcr_flow_t_h' as keyof ScenarioInput,
      scenarioVal: scenario.mcr_flow_t_h,
      unit: 't/h',
      editable: true,
      status: 'DEMO (DCS)',
      note: 'Batas anti-surge minimum: ≥ 480.0 t/h. Katup 4UV-53 membuka jika di bawah ini.',
    },
    {
      group: 'Kompresor MCR',
      name: 'Suhu Gas Keluar Suction Drum 4C-8',
      tag: 'H4TI004B',
      actual: v.H4TI004B?.value ?? -40.5,
      scenarioKey: null,
      scenarioVal: v.H4TI004B?.value ?? -40.5,
      unit: '°C',
      editable: false,
      status: 'DEMO (DCS)',
      note: 'Interlock keselamatan TAL: ≥ -45.0 °C (TALL trip: -51.0 °C).',
    },
    {
      group: 'Kompresor MCR',
      name: 'Tekanan Suction 4K-2 (LP MCR)',
      tag: 'H4PI014B',
      actual: v.p_4k2_suct_kgcm2a?.value ?? 3.235,
      scenarioKey: null,
      scenarioVal: v.p_4k2_suct_kgcm2a?.value ?? 3.235,
      unit: 'kg/cm2A',
      editable: false,
      status: 'DEMO (DCS)',
      note: 'Kalibrasi pemancar tekanan absolut.',
    },
    {
      group: 'Kompresor MCR',
      name: 'Tekanan Discharge 4K-3 (HP MCR)',
      tag: 'H4PI017B',
      actual: v.p_4k3_disch_kgcm2a?.value ?? 43.881,
      scenarioKey: null,
      scenarioVal: v.p_4k3_disch_kgcm2a?.value ?? 43.881,
      unit: 'kg/cm2A',
      editable: false,
      status: 'DEMO (DCS)',
      note: 'Batas alarm tekanan tinggi PAH: 54.0 kg/cm2A.',
    },
    // Group 3: MCR Composition
    {
      group: 'Komposisi MCR',
      name: 'Nitrogen (N2) Mole Fraction',
      tag: 'comp_4C-8_N2',
      actual: v.comp_N2?.value ?? 3.38,
      scenarioKey: 'comp_N2_molpct' as keyof ScenarioInput,
      scenarioVal: scenario.comp_N2_molpct,
      unit: 'mol%',
      editable: true,
      status: 'DEMO (Lab GC)',
      note: 'Komponen volatil; mengontrol suhu ujung dingin MCHE & TAL suction.',
    },
    {
      group: 'Komposisi MCR',
      name: 'Metana (CH4) Mole Fraction',
      tag: 'comp_4C-8_C1',
      actual: v.comp_C1?.value ?? 44.37,
      scenarioKey: 'comp_C1_molpct' as keyof ScenarioInput,
      scenarioVal: scenario.comp_C1_molpct,
      unit: 'mol%',
      editable: true,
      status: 'DEMO (Lab GC)',
      note: 'Komponen utama pendinginan subcooling MCHE. Rentang nominal: 35 – 55 mol%.',
    },
    {
      group: 'Komposisi MCR',
      name: 'Etana (C2H6) Mole Fraction',
      tag: 'comp_4C-8_C2',
      actual: v.comp_C2?.value ?? 44.94,
      scenarioKey: 'comp_C2_molpct' as keyof ScenarioInput,
      scenarioVal: scenario.comp_C2_molpct,
      unit: 'mol%',
      editable: true,
      status: 'DEMO (Lab GC)',
      note: 'Komponen pendinginan bundle tengah MCHE. Rentang nominal: 30 – 55 mol%.',
    },
    {
      group: 'Komposisi MCR',
      name: 'Etilena (C2H4) Mole Fraction',
      tag: 'comp_4C-8_C2H4',
      actual: v.comp_C2H4?.value ?? 0.85,
      scenarioKey: 'comp_C2H4_molpct' as keyof ScenarioInput,
      scenarioVal: scenario.comp_C2H4_molpct,
      unit: 'mol%',
      editable: true,
      status: 'DEMO (Lab GC)',
      note: 'Komponen modifikasi kurva pendinginan transisi.',
    },
    {
      group: 'Komposisi MCR',
      name: 'Propana (C3H8) Mole Fraction',
      tag: 'comp_4C-8_C3',
      actual: v.comp_C3?.value ?? 6.28,
      scenarioKey: 'comp_C3_molpct' as keyof ScenarioInput,
      scenarioVal: scenario.comp_C3_molpct,
      unit: 'mol%',
      editable: true,
      status: 'DEMO (Lab GC)',
      note: 'Komponen fraksi berat; menurunkan suhu suction drum jika dinaikkan.',
    },
    // Group 4: MCHE
    {
      group: 'MCHE (Penukar Panas)',
      name: 'Beda Tekan Warm Bundle MCHE',
      tag: 'H5PDI003',
      actual: v.dp_mche_warm_kgcm2?.value ?? 0.213,
      scenarioKey: null,
      scenarioVal: v.dp_mche_warm_kgcm2?.value ?? 0.213,
      unit: 'kg/cm2',
      editable: false,
      status: 'DEMO (DCS)',
      note: 'Batas alarm: 0.42 kg/cm2, batas trip darurat: 0.54 kg/cm2.',
    },
    {
      group: 'MCHE (Penukar Panas)',
      name: 'Beda Tekan Cold Bundle MCHE',
      tag: 'H5PDI004',
      actual: v.dp_mche_cold_kgcm2?.value ?? 0.079,
      scenarioKey: null,
      scenarioVal: v.dp_mche_cold_kgcm2?.value ?? 0.079,
      unit: 'kg/cm2',
      editable: false,
      status: 'DEMO (DCS)',
      note: 'Batas normal maksimum: 0.17 kg/cm2.',
    },
    {
      group: 'MCHE (Penukar Panas)',
      name: 'Suhu LNG Rundown ke Tangki',
      tag: 'H5TI0029',
      actual: v.t_lng_rundown_c?.value ?? -148.0,
      scenarioKey: null,
      scenarioVal: v.t_lng_rundown_c?.value ?? -148.0,
      unit: '°C',
      editable: false,
      status: 'DEMO (DCS)',
      note: 'Suhu spesifikasi produk LNG cair sebelum dikirim ke tangki penyimpanan.',
    },
  ];

  return (
    <div style={{
      backgroundColor: '#131d2e',
      border: '1px solid #1f2e46',
      borderRadius: '8px',
      overflow: 'hidden'
    }}>
      {/* Action Toolbar */}
      <div style={{
        padding: '14px 20px',
        backgroundColor: '#162235',
        borderBottom: '1px solid #203047',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '12px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#f8fafc' }}>
            Lembar Kerja Operasi & Simulasi Skenario
          </span>
          <span style={{ fontSize: '0.75rem', color: '#64748b' }}>
            (Sel berlatar biru muda pada kolom Skenario dapat disunting)
          </span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <button
            onClick={onCalculate}
            disabled={loading}
            style={{
              backgroundColor: '#0284c7',
              color: '#ffffff',
              border: 'none',
              padding: '8px 16px',
              borderRadius: '6px',
              fontWeight: 700,
              fontSize: '0.85rem',
              cursor: loading ? 'not-allowed' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              opacity: loading ? 0.7 : 1,
            }}
          >
            {loading ? 'Menghitung...' : '⚡ Hitung Prediksi (Model ML)'}
          </button>

          <button
            onClick={onReset}
            style={{
              backgroundColor: '#1e293b',
              color: '#94a3b8',
              border: '1px solid #334155',
              padding: '8px 14px',
              borderRadius: '6px',
              fontWeight: 600,
              fontSize: '0.85rem',
              cursor: 'pointer'
            }}
          >
            ↺ Reset ke Aktual
          </button>

          <button
            onClick={onExportCsv}
            style={{
              backgroundColor: '#1e293b',
              color: '#38bdf8',
              border: '1px solid #0284c7',
              padding: '8px 14px',
              borderRadius: '6px',
              fontWeight: 600,
              fontSize: '0.85rem',
              cursor: 'pointer'
            }}
          >
            📥 Ekspor CSV
          </button>
        </div>
      </div>

      {/* Warning/Alert banners if any */}
      {prediction?.safety_check.violations && prediction.safety_check.violations.length > 0 && (
        <div style={{
          backgroundColor: 'rgba(239, 68, 68, 0.12)',
          borderBottom: '1px solid #ef4444',
          padding: '12px 20px',
          color: '#fca5a5',
          fontSize: '0.8rem'
        }}>
          <div style={{ fontWeight: 700, marginBottom: '4px', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span>⛔ PELANGGARAN KESELAMATAN PROSES:</span>
          </div>
          <ul style={{ margin: 0, paddingLeft: '20px' }}>
            {prediction.safety_check.violations.map((violation, i) => (
              <li key={i}>{violation}</li>
            ))}
          </ul>
        </div>
      )}

      {prediction?.safety_check.warnings && prediction.safety_check.warnings.length > 0 && (
        <div style={{
          backgroundColor: 'rgba(245, 158, 11, 0.12)',
          borderBottom: '1px solid #f59e0b',
          padding: '10px 20px',
          color: '#fcd34d',
          fontSize: '0.8rem'
        }}>
          <div style={{ fontWeight: 700, marginBottom: '2px' }}>
            ⚠️ Peringatan Operasional & Validitas Domain:
          </div>
          <ul style={{ margin: 0, paddingLeft: '20px' }}>
            {prediction.safety_check.warnings.map((warn, i) => (
              <li key={i}>{warn}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Spreadsheet Table */}
      <div style={{ overflowX: 'auto' }}>
        <table className="spreadsheet-table">
          <thead>
            <tr>
              <th style={{ width: '150px' }}>Kelompok</th>
              <th>Variabel Proses</th>
              <th style={{ width: '100px' }}>Tag DCS</th>
              <th style={{ width: '130px', textAlign: 'right' }}>Kondisi Aktual</th>
              <th style={{ width: '150px', textAlign: 'right' }}>Nilai Skenario</th>
              <th style={{ width: '90px' }}>Satuan</th>
              <th style={{ width: '120px' }}>Status Data</th>
              <th style={{ minWidth: '220px' }}>Keterangan & Limitasi</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row, idx) => {
              const isEdited = row.editable && row.scenarioVal !== row.actual;
              return (
                <tr key={idx} style={{
                  backgroundColor: isEdited ? 'rgba(2, 132, 199, 0.08)' : 'transparent'
                }}>
                  <td style={{ color: '#94a3b8', fontSize: '0.8rem', fontWeight: 600 }}>
                    {row.group}
                  </td>
                  <td style={{ fontWeight: 600, color: '#f1f5f9' }}>
                    {row.name}
                  </td>
                  <td>
                    <span className="font-num" style={{
                      fontSize: '0.75rem',
                      color: '#38bdf8',
                      backgroundColor: '#0f172a',
                      padding: '2px 6px',
                      borderRadius: '4px',
                      border: '1px solid #1e293b'
                    }}>
                      {row.tag}
                    </span>
                  </td>
                  <td className="font-num" style={{ textAlign: 'right', fontWeight: 600, color: '#cbd5e1' }}>
                    {typeof row.actual === 'number' ? row.actual.toFixed(typeof row.actual === 'number' && row.actual % 1 !== 0 ? (row.unit === 'mol%' ? 2 : (row.unit.includes('kg/cm2') ? 3 : 1)) : 0) : row.actual}
                  </td>
                  <td style={{ textAlign: 'right' }}>
                    {row.editable && row.scenarioKey ? (
                      <input
                        type="number"
                        step={row.unit === 'mol%' ? '0.01' : '1.0'}
                        value={row.scenarioVal}
                        onChange={(e) => onScenarioChange(row.scenarioKey!, parseFloat(e.target.value) || 0)}
                        className="input-scenario font-num"
                      />
                    ) : (
                      <span className="font-num" style={{ color: '#64748b', fontSize: '0.85rem' }}>
                        {typeof row.scenarioVal === 'number' ? row.scenarioVal.toFixed(row.unit.includes('kg/cm2') ? 3 : 1) : row.scenarioVal}
                      </span>
                    )}
                  </td>
                  <td style={{ color: '#94a3b8', fontSize: '0.8rem' }}>
                    {row.unit}
                  </td>
                  <td>
                    <span style={{
                      fontSize: '0.7rem',
                      padding: '2px 6px',
                      borderRadius: '4px',
                      backgroundColor: '#1e293b',
                      color: row.status.includes('DCS') ? '#38bdf8' : (row.status.includes('Lab') ? '#a78bfa' : '#94a3b8')
                    }}>
                      {row.status}
                    </span>
                  </td>
                  <td style={{ color: '#64748b', fontSize: '0.78rem', lineHeight: 1.3 }}>
                    {row.note}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};
