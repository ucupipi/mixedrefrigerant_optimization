import React from 'react';
import type { UserMode } from '../types';

interface TopNavbarProps {
  userMode: UserMode;
  onToggleUserMode: (mode: UserMode) => void;
  loading: boolean;
  onReset: () => void;
  onExportCsv: () => void;
  modelReady?: boolean;
}

export const TopNavbar: React.FC<TopNavbarProps> = ({
  userMode,
  onToggleUserMode,
  loading,
  onReset,
  onExportCsv,
  modelReady = true,
}) => {
  return (
    <header style={{
      backgroundColor: '#0f172a',
      borderBottom: '2px solid #1e293b',
      padding: '12px 24px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      gap: '16px',
      flexWrap: 'wrap',
      boxShadow: '0 2px 8px rgba(0,0,0,0.25)',
      fontFamily: "'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif",
    }}>
      {/* Brand & Plant Identification */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
        <div style={{
          width: '38px',
          height: '38px',
          backgroundColor: '#0284c7',
          borderRadius: '6px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#ffffff',
          fontWeight: 800,
          fontSize: '18px',
          letterSpacing: '0.5px',
          boxShadow: '0 2px 4px rgba(0,0,0,0.3)',
        }}>
          3H
        </div>
        <div>
          <div style={{
            fontSize: '21px',
            fontWeight: 700,
            color: '#f8fafc',
            letterSpacing: '0.3px',
            lineHeight: 1.2,
          }}>
            BADAK LNG PLANT-3 TRAIN H
          </div>
          <div style={{
            fontSize: '13px',
            color: '#94a3b8',
            marginTop: '2px',
            fontWeight: 500,
          }}>
            Workspace Pendukung Keputusan Operasi C3MR (MCHE 5E-1 & Kompresor 4K)
          </div>
        </div>
      </div>

      {/* Operational Indicators & Mode Toggle */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '14px', flexWrap: 'wrap' }}>
        {/* Read-Only Safety Pill */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '7px',
          backgroundColor: '#1e293b',
          border: '1px solid #334155',
          borderRadius: '6px',
          padding: '6px 12px',
          fontSize: '13px',
          color: '#cbd5e1',
          fontWeight: 600,
        }}>
          <span style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            backgroundColor: '#22c55e',
            display: 'inline-block',
            boxShadow: '0 0 8px #22c55e',
          }} />
          READ-ONLY ADVISORY
        </div>

        {/* Model Ready Status Pill */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          backgroundColor: '#1e293b',
          border: '1px solid #334155',
          borderRadius: '6px',
          padding: '6px 12px',
          fontSize: '13px',
          color: modelReady ? '#86efac' : '#fca5a5',
          fontWeight: 600,
        }}>
          <span style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            backgroundColor: modelReady ? '#16a34a' : '#dc2626',
            display: 'inline-block',
          }} />
          {modelReady ? 'MODEL ONLINE' : 'MODEL OFFLINE'}
        </div>

        {/* User Mode Toggle: OPERATOR vs ENGINEERING */}
        <div style={{
          display: 'flex',
          backgroundColor: '#1e293b',
          padding: '3px',
          borderRadius: '8px',
          border: '1px solid #334155',
        }}>
          <button
            onClick={() => onToggleUserMode('OPERATOR')}
            style={{
              padding: '6px 14px',
              border: 'none',
              borderRadius: '6px',
              backgroundColor: userMode === 'OPERATOR' ? '#2563eb' : 'transparent',
              color: userMode === 'OPERATOR' ? '#ffffff' : '#94a3b8',
              fontSize: '14px',
              fontWeight: 700,
              cursor: 'pointer',
              transition: 'all 0.15s ease',
            }}
          >
            Operator Mode
          </button>
          <button
            onClick={() => onToggleUserMode('ENGINEERING')}
            style={{
              padding: '6px 14px',
              border: 'none',
              borderRadius: '6px',
              backgroundColor: userMode === 'ENGINEERING' ? '#0d9488' : 'transparent',
              color: userMode === 'ENGINEERING' ? '#ffffff' : '#94a3b8',
              fontSize: '14px',
              fontWeight: 700,
              cursor: 'pointer',
              transition: 'all 0.15s ease',
            }}
          >
            Engineering Mode
          </button>
        </div>

        {/* Action Buttons */}
        <button
          onClick={onReset}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            backgroundColor: '#334155',
            color: '#f8fafc',
            border: '1px solid #475569',
            padding: '7px 14px',
            borderRadius: '6px',
            fontSize: '14px',
            fontWeight: 600,
            cursor: 'pointer',
            transition: 'background-color 0.15s ease',
          }}
          title="Kembalikan semua nilai ke kondisi DCS awal"
        >
          ⟲ Reset DCS
        </button>

        <button
          onClick={onExportCsv}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            backgroundColor: '#15803d',
            color: '#ffffff',
            border: 'none',
            padding: '7px 14px',
            borderRadius: '6px',
            fontSize: '14px',
            fontWeight: 700,
            cursor: 'pointer',
            boxShadow: '0 1px 3px rgba(0,0,0,0.2)',
          }}
          title="Unduh seluruh data skenario & rekomendasi make-up ke file CSV"
        >
          ⬇ Unduh Data CSV
        </button>

        {loading && (
          <span style={{
            fontSize: '13px',
            color: '#38bdf8',
            fontWeight: 600,
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
          }}>
            <span style={{ display: 'inline-block', animation: 'spin 1s linear infinite' }}>⏳</span>
            Menghitung...
          </span>
        )}
      </div>
    </header>
  );
};

