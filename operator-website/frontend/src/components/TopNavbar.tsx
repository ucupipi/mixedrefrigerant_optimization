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
      backgroundColor: '#0f172a',
      borderBottom: '2px solid #0284c7',
      padding: '10px 20px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      gap: '12px',
      position: 'sticky',
      top: 0,
      zIndex: 200,
      fontFamily: "'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif",
    }}>
      {/* Brand & Project Identification */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', minWidth: 0, flex: 1 }}>
        <div style={{
          width: '38px',
          height: '38px',
          flexShrink: 0,
          backgroundColor: '#0284c7',
          borderRadius: '8px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#ffffff',
          fontWeight: 800,
          fontSize: '13px',
          letterSpacing: '0.5px',
        }}>
          C3MR
        </div>
        <div style={{ minWidth: 0 }}>
          <div style={{
            fontSize: 'clamp(11px, 2.8vw, 16px)',
            fontWeight: 800,
            color: '#f8fafc',
            lineHeight: 1.25,
            whiteSpace: 'nowrap',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
          }}>
            Optimasi Mixed Refrigerant (C3MR)
          </div>
        </div>
      </div>

      {/* Operational Indicators & Action Buttons */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexShrink: 0 }}>
        {/* Status Pill */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          backgroundColor: '#1e293b',
          border: '1px solid #334155',
          borderRadius: '6px',
          padding: '4px 10px',
          fontSize: '12px',
          color: '#cbd5e1',
          fontWeight: 600,
        }}>
          <span style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            backgroundColor: modelReady ? '#10b981' : '#ef4444',
            display: 'inline-block',
          }} />
          <span>{modelReady ? 'Sistem Aktif' : 'Offline'}</span>
          <span className="mobile-hide" style={{ color: '#475569' }}>|</span>
          <span className="mobile-hide" style={{ color: '#38bdf8' }}>ADVISORY</span>
        </div>

        {/* CSV Export Button */}
        <button
          onClick={onExportCsv}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            backgroundColor: '#059669',
            color: '#ffffff',
            border: 'none',
            padding: '6px 14px',
            borderRadius: '6px',
            fontSize: '12px',
            fontWeight: 700,
            cursor: 'pointer',
            transition: 'background-color 0.15s ease',
          }}
          title="Unduh seluruh data skenario ke format CSV"
        >
          <span>Unduh CSV</span>
        </button>

        {loading && (
          <span style={{
            fontSize: '12px',
            color: '#38bdf8',
            fontWeight: 600,
          }}>
            Memproses...
          </span>
        )}
      </div>
    </header>
  );
};

