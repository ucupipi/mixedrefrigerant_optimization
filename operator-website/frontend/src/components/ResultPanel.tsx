import React from 'react';
import type { PredictResponse } from '../types';

interface ResultPanelProps {
  prediction: PredictResponse | null;
  baselinePower?: number;
  loading: boolean;
}

export const ResultPanel: React.FC<ResultPanelProps> = ({
  prediction,
  baselinePower,
  loading,
}) => {
  if (loading) {
    return (
      <div style={{
        backgroundColor: '#131d2e',
        border: '1px solid #1f2e46',
        borderRadius: '8px',
        padding: '24px',
        textAlign: 'center',
        color: '#94a3b8'
      }}>
        <div style={{ fontSize: '1rem', fontWeight: 600, color: '#38bdf8' }}>
          Menghitung Rekomendasi MCR...
        </div>
        <div style={{ fontSize: '0.8rem', marginTop: '6px' }}>
          Transformasi simpleks ILR 5-komponen & inferensi termodinamika C3MR
        </div>
      </div>
    );
  }

  if (!prediction) {
    return (
      <div style={{
        backgroundColor: '#131d2e',
        border: '1px solid #1f2e46',
        borderRadius: '8px',
        padding: '20px',
        color: '#64748b',
        textAlign: 'center'
      }}>
        Silakan klik tombol <strong>Hitung Prediksi</strong> untuk mengevaluasi skenario.
      </div>
    );
  }

  const { prediction: pred, domain_check, safety_check, confidence } = prediction;
  const power = pred.total_shaft_power_mw;
  const deltaPower = baselinePower ? power - baselinePower : null;
  const deltaPct = baselinePower ? ((power - baselinePower) / baselinePower) * 100 : null;

  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
      gap: '14px',
      marginBottom: '20px'
    }}>
      {/* Card 1: Total Power Prediction */}
      <div style={{
        backgroundColor: '#142033',
        border: '1px solid #23344d',
        borderRadius: '8px',
        padding: '16px',
        position: 'relative',
        overflow: 'hidden'
      }}>
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: '3px',
          backgroundColor: '#0284c7'
        }} />
        <div style={{ fontSize: '0.75rem', fontWeight: 600, color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          Prediksi Daya Poros Total (C3MR)
        </div>
        <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px', marginTop: '6px' }}>
          <span className="font-num" style={{ fontSize: '2.1rem', fontWeight: 800, color: '#f8fafc' }}>
            {power.toFixed(2)}
          </span>
          <span style={{ fontSize: '1.1rem', fontWeight: 700, color: '#38bdf8' }}>MW</span>
        </div>
        <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '2px' }}>
          Ketidakpastian (CI 95%): ±{confidence.mae_mw.toFixed(2)} MW [{confidence.bootstrap_ci_lower_mw.toFixed(2)} – {confidence.bootstrap_ci_upper_mw.toFixed(2)} MW]
        </div>
        {deltaPower !== null && (
          <div style={{
            marginTop: '8px',
            paddingTop: '8px',
            borderTop: '1px solid #1e2c40',
            fontSize: '0.75rem',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
          }}>
            <span style={{ color: '#94a3b8' }}>Selisih vs Aktual:</span>
            <span className="font-num" style={{
              fontWeight: 700,
              color: deltaPower <= 0 ? '#10b981' : '#f59e0b'
            }}>
              {deltaPower > 0 ? '+' : ''}{deltaPower.toFixed(2)} MW ({deltaPct !== null ? (deltaPct > 0 ? '+' : '') + deltaPct.toFixed(2) + '%' : ''})
            </span>
          </div>
        )}
      </div>

      {/* Card 2: Specific Energy Consumption (SEC) */}
      <div style={{
        backgroundColor: '#142033',
        border: '1px solid #23344d',
        borderRadius: '8px',
        padding: '16px',
        position: 'relative'
      }}>
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: '3px',
          backgroundColor: '#06b6d4'
        }} />
        <div style={{ fontSize: '0.75rem', fontWeight: 600, color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          Konsumsi Energi Spesifik (SEC)
        </div>
        <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px', marginTop: '6px' }}>
          <span className="font-num" style={{ fontSize: '2.1rem', fontWeight: 800, color: '#f8fafc' }}>
            {pred.sec_kwh_per_t ? pred.sec_kwh_per_t.toFixed(1) : '—'}
          </span>
          <span style={{ fontSize: '1rem', fontWeight: 700, color: '#06b6d4' }}>kWh/t umpan</span>
        </div>
        <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '2px' }}>
          Basis: Total daya poros / laju alir massa umpan gas
        </div>
        <div style={{
          marginTop: '8px',
          paddingTop: '8px',
          borderTop: '1px solid #1e2c40',
          fontSize: '0.75rem',
          display: 'flex',
          justifyContent: 'space-between'
        }}>
          <span style={{ color: '#94a3b8' }}>Rezim Beban:</span>
          <span style={{
            fontWeight: 700,
            textTransform: 'capitalize',
            color: pred.operating_regime === 'underload' ? '#38bdf8' : (pred.operating_regime === 'baseload' ? '#10b981' : '#f59e0b')
          }}>
            {pred.operating_regime} ({confidence.regime_r2 ? `R² = ${confidence.regime_r2.toFixed(3)}` : 'R² ≈ 0.836'})
          </span>
        </div>
      </div>

      {/* Card 3: Operating Domain & Mahalanobis */}
      <div style={{
        backgroundColor: '#142033',
        border: '1px solid #23344d',
        borderRadius: '8px',
        padding: '16px',
        position: 'relative'
      }}>
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: '3px',
          backgroundColor: domain_check.in_domain ? '#10b981' : '#f59e0b'
        }} />
        <div style={{ fontSize: '0.75rem', fontWeight: 600, color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          Validitas Domain Data (Mahalanobis)
        </div>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: '8px' }}>
          <span className={domain_check.in_domain ? 'badge-safe' : 'badge-warn'}>
            {domain_check.in_domain ? 'DALAM DOMAIN DATA' : 'DI LUAR DOMAIN DATA'}
          </span>
          <span className="font-num" style={{ fontSize: '1rem', fontWeight: 700, color: '#cbd5e1' }}>
            D_M = {domain_check.mahalanobis_distance.toFixed(3)}
          </span>
        </div>
        <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '6px' }}>
          Batas kritis χ²(0.95, 4): {domain_check.mahalanobis_limit.toFixed(4)}
        </div>
        <div style={{
          marginTop: '8px',
          paddingTop: '8px',
          borderTop: '1px solid #1e2c40',
          fontSize: '0.75rem',
          display: 'flex',
          justifyContent: 'space-between'
        }}>
          <span style={{ color: '#94a3b8' }}>Penjumlahan Komposisi:</span>
          <span className="font-num" style={{
            fontWeight: 700,
            color: domain_check.composition_closure_ok ? '#10b981' : '#f59e0b'
          }}>
            {domain_check.composition_sum_molpct.toFixed(2)} mol%
          </span>
        </div>
      </div>

      {/* Card 4: Process Safety Audit */}
      <div style={{
        backgroundColor: '#142033',
        border: '1px solid #23344d',
        borderRadius: '8px',
        padding: '16px',
        position: 'relative'
      }}>
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: '3px',
          backgroundColor: safety_check.all_safe ? '#10b981' : '#ef4444'
        }} />
        <div style={{ fontSize: '0.75rem', fontWeight: 600, color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          Audit Batas Keselamatan Kilang
        </div>
        <div style={{ marginTop: '8px' }}>
          <span className={safety_check.all_safe ? 'badge-safe' : 'badge-alert'}>
            {safety_check.all_safe ? 'SELURUH BATASAN AMAN' : `${safety_check.violations.length} PELANGGARAN KESELAMATAN`}
          </span>
        </div>
        <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '6px' }}>
          Anti-Surge (≥480 t/h), TAL (≥-45°C), dP MCHE (&lt;0.42)
        </div>
        {safety_check.warnings.length > 0 && (
          <div style={{
            marginTop: '8px',
            paddingTop: '8px',
            borderTop: '1px solid #1e2c40',
            fontSize: '0.72rem',
            color: '#f59e0b'
          }}>
            ⚠️ {safety_check.warnings.length} peringatan operasional
          </div>
        )}
      </div>
    </div>
  );
};
