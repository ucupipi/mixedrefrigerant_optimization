import React from 'react';

interface HeaderProps {
  timestamp?: string;
  modelReady: boolean;
  shiftInfo?: string;
}

export const Header: React.FC<HeaderProps> = ({ timestamp, modelReady, shiftInfo }) => {
  return (
    <header style={{
      backgroundColor: '#111927',
      borderBottom: '1px solid #1f2d44',
      padding: '14px 24px',
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      flexWrap: 'wrap',
      gap: '12px'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <div style={{
          backgroundColor: '#0284c7',
          color: '#ffffff',
          fontWeight: 800,
          padding: '6px 12px',
          borderRadius: '6px',
          letterSpacing: '0.05em',
          fontSize: '0.9rem'
        }}>
          BADAK LNG
        </div>
        <div>
          <h1 style={{
            margin: 0,
            fontSize: '1.25rem',
            fontWeight: 700,
            color: '#f8fafc',
            display: 'flex',
            alignItems: 'center',
            gap: '10px'
          }}>
            Plant-5 Train H — C3MR Liquefaction & Refrigeration Cycle
            <span style={{
              fontSize: '0.75rem',
              fontWeight: 600,
              padding: '3px 8px',
              backgroundColor: '#1e293b',
              color: '#38bdf8',
              borderRadius: '4px',
              border: '1px solid #334155'
            }}>
              OTS & AI DECISION-SUPPORT
            </span>
          </h1>
          <p style={{ margin: '2px 0 0 0', fontSize: '0.8rem', color: '#94a3b8' }}>
            Alat bantu evaluasi efisiensi energi & what-if kompresor C3MR (Hanya-Baca / Read-Only)
          </p>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <span className="badge-demo">
          DEMO — BUKAN DATA PLANT
        </span>

        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          padding: '6px 12px',
          backgroundColor: '#162235',
          border: '1px solid #223249',
          borderRadius: '6px',
          fontSize: '0.8rem'
        }}>
          <span style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            backgroundColor: modelReady ? '#10b981' : '#f59e0b',
            boxShadow: modelReady ? '0 0 8px #10b981' : 'none'
          }} />
          <span style={{ color: '#cbd5e1', fontWeight: 500 }}>
            {modelReady ? 'Model ML Siap (R² = 0.836)' : 'Memuat Model...'}
          </span>
        </div>

        <div style={{
          fontSize: '0.75rem',
          color: '#64748b',
          textAlign: 'right',
          lineHeight: 1.3
        }}>
          <div style={{ color: '#94a3b8', fontWeight: 600 }}>{shiftInfo || 'Shift Operasi'}</div>
          <div>{timestamp || new Date().toLocaleString('id-ID')}</div>
        </div>
      </div>
    </header>
  );
};

