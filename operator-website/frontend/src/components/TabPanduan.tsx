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
            PERNYATAAN KESELAMATAN & STATUS READ-ONLY (SAFETY NOTICE)
          </h3>
        </div>
        <p style={{ margin: 0, fontSize: '15px', lineHeight: 1.6, color: '#7f1d1d' }}>
          Aplikasi ini adalah <strong>perangkat pendukung keputusan (decision-support tool)</strong> dan kalkulator simulasi skenario what-if semata.
          Aplikasi ini secara fisik dan arsitektural <strong>TIDAK BISA dan DILARANG</strong> mengubah setpoint DCS secara otomatis, menggerakkan katup kontrol,
          mengatur kecepatan turbin, atau mengubah komposisi refrigeran di lapangan. Seluruh hasil yang ditampilkan adalah estimasi numerik
          dan wajib diverifikasi melalui prosedur operasi standar serta persetujuan pengawas operasi sebelum tindakan lapangan diambil.
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
          Alur Kerja 7 Langkah Operator (Standard Operator Workflow)
        </h2>
        <div style={{ fontSize: '15px', color: '#64748b', marginBottom: '20px' }}>
          Ikuti urutan langkah berikut saat melakukan pengujian skenario operasi C3MR Train H:
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
          {[
            {
              step: '1',
              title: 'Tinjau Data Proses',
              desc: 'Periksa laju alir treated gas aktual (H3FI0004), produksi LNG rundown (H5FI6A), dan temperatur suction drum.',
              color: '#0284c7',
            },
            {
              step: '2',
              title: 'Verifikasi Validitas Sensor',
              desc: 'Pastikan status sensor bertanda VALID, tidak ada indikasi instrumen beku atau di luar rentang wajar.',
              color: '#0284c7',
            },
            {
              step: '3',
              title: 'Masukkan Nilai Skenario',
              desc: 'Isi nilai skenario yang diizinkan (sirkulasi MCR atau target komposisi mol%), atau klik "Gunakan Rekomendasi Optimum".',
              color: '#2563eb',
            },
            {
              step: '4',
              title: 'Pilih "Hitung Skenario"',
              desc: 'Klik tombol utama "Hitung Skenario" untuk menjalankan simulasi model prediksi surrogate secara langsung.',
              color: '#0284c7',
            },
            {
              step: '5',
              title: 'Tinjau Hasil Simulasi (KPI)',
              desc: 'Amati total daya poros C3MR, SEC LNG (kWh/t LNG), delta penghematan, dan tabel injeksi make-up refrigeran.',
              color: '#16a34a',
            },
            {
              step: '6',
              title: 'Evaluasi Batasan Keselamatan',
              desc: 'Periksa 5 kartu batasan: Anti-Surge, TAL Suction Drum, Superheat, DP MCHE, dan Batas Elipsoid Operasi.',
              color: '#d97706',
            },
            {
              step: '7',
              title: 'Pahami Penjelasan Hasil',
              desc: 'Baca catatan operasional di bawah tabel KPI sebelum berkonsultasi dengan Shift Supervisor untuk eksekusi lapangan.',
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
          Tabel Variabel yang Boleh Diubah vs Terkunci (Variable Dictionary)
        </h2>
        <div style={{ fontSize: '15px', color: '#64748b', marginBottom: '16px' }}>
          Pembedaan tegas antara variabel yang boleh diubah operator pada skenario what-if dan variabel terproteksi yang hanya dibaca dari DCS:
        </div>

        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '15px' }}>
            <thead>
              <tr style={{ backgroundColor: '#0f172a', color: '#ffffff' }}>
                <th style={{ padding: '12px 14px', textAlign: 'left', fontWeight: 600 }}>Parameter</th>
                {userMode === 'ENGINEERING' && (
                  <th style={{ padding: '12px 14px', textAlign: 'left', fontWeight: 600 }}>Tag DCS</th>
                )}
                <th style={{ padding: '12px 14px', textAlign: 'left', fontWeight: 600 }}>Satuan</th>
                <th style={{ padding: '12px 14px', textAlign: 'center', fontWeight: 600 }}>Status Input</th>
                <th style={{ padding: '12px 14px', textAlign: 'left', fontWeight: 600 }}>Rentang & Aturan Rekayasa</th>
              </tr>
            </thead>
            <tbody>
              {[
                {
                  param: 'Laju Alir Treated Gas Masuk MCHE',
                  tag: 'H3FI0004 × 0.760',
                  unit: 't/h',
                  type: 'GANGGUAN (Read-Only)',
                  typeColor: '#64748b',
                  rule: 'Variabel gangguan (beban kilang). Diisi sesuai pembacaan riil DCS atau rencana produksi feed gas.',
                },
                {
                  param: 'Laju Alir Produksi LNG Rundown',
                  tag: 'H5FI6A',
                  unit: 't/h LNG',
                  type: 'TERKOPEL (Read-Only)',
                  typeColor: '#64748b',
                  rule: 'Otomatis dihitung = 0.9450 × Feed Gas (yield 94.5% setelah end-flash letdown). Denominator resmi SEC LNG.',
                },
                {
                  param: 'Laju Alir Sirkulasi MCR',
                  tag: 'H4FI011B × 36.8',
                  unit: 't/h',
                  type: 'EDITABLE (Skenario)',
                  typeColor: '#0284c7',
                  rule: 'Dapat diubah. Rentang wajar 480 – 620 t/h. Wajib ≥ 480.0 t/h untuk mencegah trip batas surge kompresor.',
                },
                {
                  param: 'Komposisi MCR: N₂ (Nitrogen)',
                  tag: 'comp_4C-8_N2',
                  unit: 'mol%',
                  type: 'EDITABLE (Skenario)',
                  typeColor: '#0284c7',
                  rule: 'Rentang 2.0 – 5.5 mol%. Mempengaruhi pendinginan subcooling kriogenik ujung dingin MCHE.',
                },
                {
                  param: 'Komposisi MCR: CH₄ (Metana, C₁)',
                  tag: 'comp_4C-8_C1',
                  unit: 'mol%',
                  type: 'EDITABLE (Skenario)',
                  typeColor: '#0284c7',
                  rule: 'Rentang 40.0 – 48.0 mol%. Komponen refrigeran pendingin suhu rendah (cold bundle).',
                },
                {
                  param: 'Komposisi MCR: C₂H₆ (Etana, C₂)',
                  tag: 'comp_4C-8_C2',
                  unit: 'mol%',
                  type: 'EDITABLE (Skenario)',
                  typeColor: '#0284c7',
                  rule: 'Rentang 40.0 – 48.0 mol%. Komponen pendingin suhu menengah (mid-bundle).',
                },
                {
                  param: 'Komposisi MCR: C₂H₄ (Etilena)',
                  tag: 'comp_4C-8_C2H4',
                  unit: 'mol%',
                  type: 'EDITABLE (Skenario)',
                  typeColor: '#0284c7',
                  rule: 'Rentang 0.0 – 3.0 mol%. Komponen transisi untuk penyetelan kurva VLE pendinginan cepat.',
                },
                {
                  param: 'Komposisi MCR: C₃H₈ (Propana, C₃)',
                  tag: 'comp_4C-8_C3',
                  unit: 'mol%',
                  type: 'EDITABLE (Skenario)',
                  typeColor: '#0284c7',
                  rule: 'Rentang 4.0 – 8.5 mol%. Komponen berat pendingin warm bundle. Penentu utama suhu suction drum.',
                },
                {
                  param: 'Batas Alarm Suhu Rendah Suction Drum (TAL)',
                  tag: 'H4TI004B',
                  unit: '°C',
                  type: 'SAFETY LIMIT (Terkunci)',
                  typeColor: '#dc2626',
                  rule: 'Interlock keselamatan pabrik: TAL ≥ -45.0 °C. Tidak dapat diedit oleh siapapun pada aplikasi ini.',
                },
                {
                  param: 'Beda Tekan Bundle MCHE 5E-1',
                  tag: 'H5PDI003',
                  unit: 'kg/cm²',
                  type: 'SAFETY LIMIT (Terkunci)',
                  typeColor: '#dc2626',
                  rule: 'Batas hidraulik: Alarm 0.42 kg/cm², Trip darurat 0.54 kg/cm² (5PDAHH-25).',
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
          Kamus Status Evaluasi Batasan (Constraint Status Dictionary)
        </h2>
        <div style={{ fontSize: '15px', color: '#64748b', marginBottom: '16px' }}>
          Arti dari setiap kategori badge status yang ditampilkan pada kartu evaluasi batasan proses:
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
              Batasan Terpenuhi
            </div>
            <div style={{ fontSize: '14px', color: '#166534', lineHeight: 1.5 }}>
              Parameter operasi berada aman di dalam batas spesifikasi teknis dan memiliki margin keselamatan yang memadai.
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
              Mendekati Batas / Perhatian
            </div>
            <div style={{ fontSize: '14px', color: '#854d0e', lineHeight: 1.5 }}>
              Parameter masih memenuhi batas batas minimum/maksimum tetapi margin keselamatan menyempit, atau variasi komposisi mendekati tepi domain teruji.
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
              Pelanggaran Batasan Terverifikasi
            </div>
            <div style={{ fontSize: '14px', color: '#991b1b', lineHeight: 1.5 }}>
              Skenario melanggar batas keselamatan pabrik (misal: sirkulasi &lt; 480 t/h tanpa modulasi kickback valve, atau suhu suction &lt; -45 °C). DILARANG DIGUNAKAN.
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
              Belum Dievaluasi
            </div>
            <div style={{ fontSize: '14px', color: '#475569', lineHeight: 1.5 }}>
              Pemeriksaan instrumen dinamis tertentu belum memiliki koneksi sensor live pada snapshot saat ini (misal: kurva peta head dinamis anti-surge kompresor).
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
          Kapan Hasil Skenario TIDAK BOLEH Digunakan (When NOT to Use)
        </h2>
        <div style={{ fontSize: '15px', color: '#64748b', marginBottom: '16px' }}>
          Skenario prediksi dilarang keras diimplementasikan sebagai acuan pengaturan kilang jika salah satu kondisi berikut terjadi:
        </div>

        <ul style={{ margin: 0, paddingLeft: '24px', fontSize: '15px', color: '#334155', lineHeight: 1.7 }}>
          <li>
            <strong>Ada indikator FAILED pada salah satu batasan keselamatan:</strong> Terjadi pelanggaran flow anti-surge, suhu suction drum, superheat, atau beda tekan MCHE.
          </li>
          <li>
            <strong>Jarak Mahalanobis DM &gt; 3.0802:</strong> Rekomendasi komposisi berada di luar batas elipsoid data latih terverifikasi (indikasi ekstrapolasi tidak aman).
          </li>
          <li>
            <strong>Kompresor sedang mengalami transient berat:</strong> Unit sedang dalam proses start-up, shutdown darurat, trip sebagian turbin, atau hunting surge.
          </li>
          <li>
            <strong>Data sensor aktual DCS tidak valid:</strong> Terjadi kegagalan kromatografi gas online (AI25A-H) atau sensor transmitter flow/pressure menunjukkan bad quality.
          </li>
          <li>
            <strong>Tanpa persetujuan tertulis pengawas operasi:</strong> Segala penyesuaian resep refrigeran wajib melalui verifikasi teknis dan persetujuan pengawas operasi.
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
            Train H LNG Liquefaction Unit (Versi Demo & Evaluasi Rekayasa)
          </div>
        </div>
        <div style={{ fontSize: '13px', color: '#94a3b8', textAlign: 'right' }}>
          <div>Versi Aplikasi: 2.0.0 (Operator Decision-Support System)</div>
          <div>Batas Sistem: Total Train C3MR Shaft Power (MCR 4KT-2/3 + C3 4KT-1)</div>
        </div>
      </div>
    </div>
  );
};
