import React from 'react';

interface TopNavbarProps {
  loading: boolean;
  onExportCsv: () => void;
  modelReady?: boolean;
}

export const TopNavbar: React.FC<TopNavbarProps> = ({
  loading,
  onExportCsv,
  modelReady = true,
}) => {
  return (
    <header style={{
      backgroundColor: 'rgba(15, 23, 42, 0.82)',
      backdropFilter: 'blur(16px)',
      WebkitBackdropFilter: 'blur(16px)',
      borderBottom: '1px solid rgba(255, 255, 255, 0.12)',
      padding: '10px 16px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      gap: '12px',
      boxShadow: '0 8px 32px 0 rgba(0, 0, 0, 0.25)',
      position: 'sticky',
      top: 0,
      zIndex: 200,
      fontFamily: "var(--font-sans, 'Plus Jakarta Sans', 'Inter', sans-serif)",
    }}>
      {/* Brand & Project Identification */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', minWidth: 0, flex: 1 }}>
        <div style={{
          width: '34px',
          height: '34px',
          flexShrink: 0,
          background: 'linear-gradient(135deg, #0284c7 0%, #38bdf8 100%)',
          borderRadius: '10px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#ffffff',
          fontWeight: 800,
          fontSize: '15px',
          fontFamily: "'Plus Jakarta Sans', sans-serif",
          letterSpacing: '0.5px',
          border: '1px solid rgba(255, 255, 255, 0.3)',
          boxShadow: '0 4px 12px rgba(2, 132, 199, 0.35)',
        }}>
          ML
        </div>
        <div style={{ minWidth: 0 }}>
          <div style={{
            fontSize: 'clamp(11px, 2.8vw, 16px)',
            fontWeight: 800,
            fontFamily: "'Plus Jakarta Sans', sans-serif",
            color: '#f8fafc',
            letterSpacing: '0.2px',
            lineHeight: 1.25,
            whiteSpace: 'nowrap',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
          }}>
            MACHINE LEARNING BASED MIXED REFRIGERANT EFFICIENCY
          </div>
          <div style={{
            fontSize: '11px',
            fontFamily: "'Inter', sans-serif",
            color: '#94a3b8',
            fontWeight: 500,
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            marginTop: '2px',
          }}>
            <span>C3MR Optimization Advisory</span>
            <span style={{ color: '#475569' }}>•</span>
            <span style={{ color: '#38bdf8', fontWeight: 600 }}>Yokogawa DCS</span>
          </div>
        </div>
      </div>

      {/* Operational Indicators & Compact Action Buttons */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexShrink: 0 }}>
        {/* Status Pills Container (Glassmorphic) */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          background: 'rgba(30, 41, 59, 0.65)',
          backdropFilter: 'blur(10px)',
          WebkitBackdropFilter: 'blur(10px)',
          border: '1px solid rgba(255, 255, 255, 0.08)',
          borderRadius: '20px',
          padding: '4px 10px',
          fontSize: '11px',
          fontFamily: "'Inter', sans-serif",
          color: '#cbd5e1',
          fontWeight: 700,
        }}>
          <span style={{
            width: '7px',
            height: '7px',
            borderRadius: '50%',
            backgroundColor: modelReady ? '#10b981' : '#ef4444',
            boxShadow: modelReady ? '0 0 8px #10b981' : '0 0 8px #ef4444',
            display: 'inline-block',
          }} />
          <span>{modelReady ? 'ONLINE' : 'OFFLINE'}</span>
          <span className="mobile-hide" style={{ color: '#475569' }}>|</span>
          <span className="mobile-hide" style={{ color: '#38bdf8' }}>ADVISORY</span>
        </div>

        {/* CSV Export Button (Glassmorphic) */}
        <button
          onClick={onExportCsv}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.9) 0%, rgba(5, 150, 105, 0.9) 100%)',
            backdropFilter: 'blur(8px)',
            WebkitBackdropFilter: 'blur(8px)',
            color: '#ffffff',
            border: '1px solid rgba(255, 255, 255, 0.3)',
            padding: '6px 12px',
            borderRadius: '8px',
            fontSize: '12px',
            fontWeight: 700,
            fontFamily: "'Plus Jakarta Sans', 'Inter', sans-serif",
            cursor: 'pointer',
            boxShadow: '0 4px 14px rgba(16, 185, 129, 0.3)',
            transition: 'all 0.2s ease',
          }}
          title="Unduh seluruh data skenario ke CSV"
        >
          <span>⬇</span>
          <span>CSV</span>
        </button>

        {loading && (
          <span style={{
            fontSize: '11px',
            color: '#38bdf8',
            fontWeight: 700,
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
          }}>
            <span style={{ display: 'inline-block', animation: 'spin 1s linear infinite' }}>⏳</span>
          </span>
        )}
      </div>
    </header>
  );
};

