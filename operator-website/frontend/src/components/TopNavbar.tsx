import React, { useState } from 'react';

interface TopNavbarProps {
  loading: boolean;
  onExportCsv: () => void;
  modelReady?: boolean;
}

const AUTHORS = [
  {
    name: 'Mukhammad Yusuf Iqbal',
    role: 'Process & Optimization Engineer / Lead Author',
    linkedin: 'https://www.linkedin.com/in/mukhyusufiqbal/',
    initials: 'MYI',
  },
  {
    name: 'Afdal Elang Arifin',
    role: 'Process & Simulation Engineer / Co-Author',
    linkedin: 'https://www.linkedin.com/in/afdal-elang-arifin-623418371/',
    initials: 'AEA',
  },
  {
    name: 'Dewi Putri Rahmawati',
    role: 'Process & Safety Engineer / Co-Author',
    linkedin: 'https://www.linkedin.com/in/dewi-putri-rahmawati-1430792b4/',
    initials: 'DPR',
  },
  {
    name: 'Hizkia Dhiego Gurning',
    role: 'Instrumentation & Process Control / Co-Author',
    linkedin: 'https://www.linkedin.com/in/hizkia-dhiego-gurning-a583b01ab/',
    initials: 'HDG',
  },
  {
    name: 'Bilqiis Dara Ramadhan Sasongko',
    role: 'Energy & Decarbonization Specialist / Co-Author',
    linkedin: 'https://www.linkedin.com/in/bilqiis-sasongko-673a5a349/',
    initials: 'BDS',
  },
];

export const TopNavbar: React.FC<TopNavbarProps> = ({
  loading,
  onExportCsv,
  modelReady = true,
}) => {
  const [showContactModal, setShowContactModal] = useState<boolean>(false);

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

        {/* Contact Us Button */}
        <button
          onClick={() => setShowContactModal(true)}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            backgroundColor: '#1e293b',
            color: '#38bdf8',
            border: '1px solid #0284c7',
            padding: '6px 12px',
            borderRadius: '6px',
            fontSize: '12px',
            fontWeight: 700,
            cursor: 'pointer',
            transition: 'all 0.15s ease',
          }}
          title="Kontak Tim Peneliti & Pengembang (LinkedIn)"
        >
          <span>👥 Contact Us</span>
        </button>

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

      {/* Contact Us Modal Dialog */}
      {showContactModal && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(15, 23, 42, 0.75)',
            backdropFilter: 'blur(8px)',
            WebkitBackdropFilter: 'blur(8px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
            padding: '16px',
          }}
          onClick={() => setShowContactModal(false)}
        >
          <div
            style={{
              backgroundColor: '#0f172a',
              border: '1px solid #334155',
              borderRadius: '16px',
              width: '100%',
              maxWidth: '540px',
              maxHeight: '90vh',
              overflowY: 'auto',
              boxShadow: '0 20px 40px -15px rgba(0, 0, 0, 0.6), 0 0 0 1px rgba(2, 132, 199, 0.35)',
              color: '#f8fafc',
              padding: '24px',
              fontFamily: "'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif",
            }}
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '18px', borderBottom: '1px solid #1e293b', paddingBottom: '14px' }}>
              <div>
                <div style={{ fontSize: '18px', fontWeight: 800, color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span>👥 Contact Us</span>
                  <span style={{ fontSize: '11px', backgroundColor: '#0284c7', color: '#ffffff', padding: '2px 8px', borderRadius: '12px', fontWeight: 700 }}>
                    Plant-3 Suite
                  </span>
                </div>
                <div style={{ fontSize: '12.5px', color: '#94a3b8', marginTop: '4px' }}>
                  Tim Peneliti & Pengembang AI C3MR Optimization Suite
                </div>
              </div>
              <button
                onClick={() => setShowContactModal(false)}
                style={{
                  background: '#1e293b',
                  border: '1px solid #334155',
                  color: '#94a3b8',
                  borderRadius: '8px',
                  width: '32px',
                  height: '32px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  cursor: 'pointer',
                  fontSize: '16px',
                  fontWeight: 'bold',
                  lineHeight: 1,
                }}
                aria-label="Tutup"
              >
                ✕
              </button>
            </div>

            {/* Authors List */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {AUTHORS.map((author) => (
                <div
                  key={author.name}
                  style={{
                    backgroundColor: '#1e293b',
                    border: '1px solid #334155',
                    borderRadius: '12px',
                    padding: '12px 14px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    gap: '12px',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px', minWidth: 0 }}>
                    <div style={{
                      width: '40px',
                      height: '40px',
                      borderRadius: '10px',
                      background: 'linear-gradient(135deg, #0284c7 0%, #0369a1 100%)',
                      color: '#ffffff',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontWeight: 800,
                      fontSize: '13px',
                      flexShrink: 0,
                    }}>
                      {author.initials}
                    </div>
                    <div style={{ minWidth: 0 }}>
                      <div style={{ fontWeight: 700, fontSize: '14px', color: '#f8fafc', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                        {author.name}
                      </div>
                      <div style={{ fontSize: '11.5px', color: '#38bdf8', marginTop: '2px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                        {author.role}
                      </div>
                    </div>
                  </div>

                  <a
                    href={author.linkedin}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '6px',
                      backgroundColor: '#0a66c2',
                      color: '#ffffff',
                      textDecoration: 'none',
                      padding: '7px 12px',
                      borderRadius: '8px',
                      fontSize: '12px',
                      fontWeight: 700,
                      flexShrink: 0,
                      transition: 'background-color 0.15s ease',
                    }}
                  >
                    <span>LinkedIn ↗</span>
                  </a>
                </div>
              ))}
            </div>

            {/* Footer */}
            <div style={{ marginTop: '20px', paddingTop: '14px', borderTop: '1px solid #1e293b', display: 'flex', justifyContent: 'flex-end' }}>
              <button
                onClick={() => setShowContactModal(false)}
                style={{
                  backgroundColor: '#334155',
                  color: '#f8fafc',
                  border: 'none',
                  padding: '8px 18px',
                  borderRadius: '8px',
                  fontSize: '12.5px',
                  fontWeight: 600,
                  cursor: 'pointer',
                }}
              >
                Tutup
              </button>
            </div>
          </div>
        </div>
      )}
    </header>
  );
};

