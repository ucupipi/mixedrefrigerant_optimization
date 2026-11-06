import React, { useState } from 'react';

interface TopNavbarProps {
  loading: boolean;
  onExportCsv: () => void;
  modelReady?: boolean;
}

interface Author {
  name: string;
  role: string;
  institution: string;
  linkedin: string;
  photo: string;
  initials: string;
}

const AUTHORS: Author[] = [
  {
    name: 'Mukhammad Yusuf Iqbal',
    role: 'Process Simulation & Optimization (Lead)',
    institution: 'LNG Academy / PT Badak NGL',
    linkedin: 'https://www.linkedin.com/in/mukhyusufiqbal/',
    photo: '/authors/yusuf.jpg',
    initials: 'MYI',
  },
  {
    name: 'Afdal Elang Arifin',
    role: 'Process Simulation & Thermodynamic Modeling',
    institution: 'LNG Academy / PT Badak NGL',
    linkedin: 'https://www.linkedin.com/in/afdal-elang-arifin-623418371/',
    photo: '/authors/afdal.jpg',
    initials: 'AEA',
  },
  {
    name: 'Dewi Putri Rahmawati',
    role: 'Process Safety & Operational Interlocks',
    institution: 'LNG Academy / PT Badak NGL',
    linkedin: 'https://www.linkedin.com/in/dewi-putri-rahmawati-1430792b4/',
    photo: '/authors/dewi.jpeg',
    initials: 'DPR',
  },
  {
    name: 'Hizkia Dhiego Gurning',
    role: 'Instrumentation & Advanced Process Control',
    institution: 'LNG Academy / PT Badak NGL',
    linkedin: 'https://www.linkedin.com/in/hizkia-dhiego-gurning-a583b01ab/',
    photo: '/authors/gurning.jpg',
    initials: 'HDG',
  },
  {
    name: 'Bilqiis Dara Ramadhan Sasongko',
    role: 'Energy Efficiency & Decarbonization Analysis',
    institution: 'LNG Academy / PT Badak NGL',
    linkedin: 'https://www.linkedin.com/in/bilqiis-sasongko-673a5a349/',
    photo: '/authors/bilqiis.jpeg',
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
      backgroundColor: 'rgba(255, 255, 255, 0.82)',
      backdropFilter: 'blur(16px)',
      WebkitBackdropFilter: 'blur(16px)',
      borderBottom: '1px solid rgba(226, 232, 240, 0.8)',
      padding: '10px 20px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      gap: '12px',
      position: 'sticky',
      top: 0,
      zIndex: 200,
      boxShadow: '0 4px 20px -2px rgba(15, 23, 42, 0.03)',
      fontFamily: "'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif",
    }}>
      {/* Brand & Project Identification */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', minWidth: 0, flex: 1 }}>
        <div style={{
          width: '38px',
          height: '38px',
          flexShrink: 0,
          background: 'linear-gradient(135deg, #0284c7 0%, #0369a1 100%)',
          borderRadius: '8px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#ffffff',
          fontWeight: 800,
          fontSize: '13px',
          letterSpacing: '0.5px',
          boxShadow: '0 2px 8px rgba(2, 132, 199, 0.3)',
        }}>
          C3MR
        </div>
        <div style={{ minWidth: 0 }}>
          <div style={{
            fontSize: 'clamp(11px, 2.8vw, 16px)',
            fontWeight: 800,
            color: '#0f172a',
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
          backgroundColor: 'rgba(241, 245, 249, 0.85)',
          border: '1px solid rgba(203, 213, 225, 0.8)',
          borderRadius: '6px',
          padding: '4px 10px',
          fontSize: '12px',
          color: '#334155',
          fontWeight: 600,
          boxShadow: '0 1px 2px rgba(0, 0, 0, 0.04)',
        }}>
          <span style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            backgroundColor: modelReady ? '#10b981' : '#ef4444',
            display: 'inline-block',
          }} />
          <span>{modelReady ? 'Sistem Aktif' : 'Offline'}</span>
          <span className="mobile-hide" style={{ color: '#cbd5e1' }}>|</span>
          <span className="mobile-hide" style={{ color: '#0284c7', fontWeight: 700 }}>ADVISORY</span>
        </div>

        {/* Contact Us Button */}
        <button
          onClick={() => setShowContactModal(true)}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            backgroundColor: 'rgba(255, 255, 255, 0.85)',
            color: '#0369a1',
            border: '1px solid rgba(203, 213, 225, 0.9)',
            padding: '6px 12px',
            borderRadius: '6px',
            fontSize: '12px',
            fontWeight: 700,
            cursor: 'pointer',
            boxShadow: '0 2px 6px rgba(0, 0, 0, 0.04), inset 0 1px 0 #ffffff',
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
            background: 'linear-gradient(135deg, #059669 0%, #047857 100%)',
            color: '#ffffff',
            border: 'none',
            padding: '6px 14px',
            borderRadius: '6px',
            fontSize: '12px',
            fontWeight: 700,
            cursor: 'pointer',
            boxShadow: '0 2px 6px rgba(5, 150, 105, 0.25)',
            transition: 'background-color 0.15s ease',
          }}
          title="Unduh seluruh data skenario ke format CSV"
        >
          <span>Unduh CSV</span>
        </button>

        {loading && (
          <span style={{
            fontSize: '12px',
            color: '#0284c7',
            fontWeight: 600,
          }}>
            Memproses...
          </span>
        )}
      </div>

      {/* Contact Us Modal Dialog (Light Frosted Glassmorphism) */}
      {showContactModal && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(15, 23, 42, 0.35)',
            backdropFilter: 'blur(16px)',
            WebkitBackdropFilter: 'blur(16px)',
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
              background: 'rgba(255, 255, 255, 0.92)',
              backdropFilter: 'blur(24px) saturate(180%)',
              WebkitBackdropFilter: 'blur(24px) saturate(180%)',
              border: '1px solid rgba(255, 255, 255, 0.95)',
              borderRadius: '20px',
              width: '100%',
              maxWidth: '580px',
              maxHeight: '90vh',
              overflowY: 'auto',
              boxShadow: '0 25px 60px -15px rgba(15, 23, 42, 0.15), 0 0 0 1px rgba(226, 232, 240, 0.6), inset 0 1px 1px #ffffff',
              color: '#0f172a',
              padding: '24px 26px',
              fontFamily: "'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif",
            }}
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'flex-start',
              marginBottom: '18px',
              borderBottom: '1px solid rgba(226, 232, 240, 0.8)',
              paddingBottom: '14px',
            }}>
              <div>
                <div style={{ fontSize: '18px', fontWeight: 800, color: '#0f172a', display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <span>Kontak Tim Peneliti</span>
                  <span style={{
                    fontSize: '11px',
                    background: '#e0f2fe',
                    border: '1px solid #bae6fd',
                    color: '#0369a1',
                    padding: '2px 10px',
                    borderRadius: '12px',
                    fontWeight: 700,
                    letterSpacing: '0.3px',
                  }}>
                    Plant-5 Liquefaction
                  </span>
                </div>
                <div style={{ fontSize: '12.5px', color: '#64748b', marginTop: '4px' }}>
                  Badak LNG C3MR Plant-5 Process Optimization & Decision-Support System
                </div>
              </div>
              <button
                onClick={() => setShowContactModal(false)}
                style={{
                  background: 'rgba(241, 245, 249, 0.8)',
                  border: '1px solid rgba(203, 213, 225, 0.8)',
                  color: '#64748b',
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
                  transition: 'all 0.15s ease',
                }}
                aria-label="Tutup"
              >
                ✕
              </button>
            </div>

            {/* Authors List with Light Tactile Glass Cards */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {AUTHORS.map((author) => (
                <div
                  key={author.name}
                  style={{
                    background: 'rgba(255, 255, 255, 0.75)',
                    backdropFilter: 'blur(12px)',
                    WebkitBackdropFilter: 'blur(12px)',
                    border: '1px solid rgba(226, 232, 240, 0.85)',
                    borderRadius: '14px',
                    padding: '12px 16px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    gap: '14px',
                    boxShadow: '0 4px 16px rgba(15, 23, 42, 0.03), inset 0 1px 0 #ffffff',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '14px', minWidth: 0, flex: 1 }}>
                    <div style={{ position: 'relative', width: '48px', height: '48px', flexShrink: 0 }}>
                      <img
                        src={author.photo}
                        alt={author.name}
                        style={{
                          width: '48px',
                          height: '48px',
                          borderRadius: '50%',
                          objectFit: 'cover',
                          border: '2px solid rgba(2, 132, 199, 0.4)',
                          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
                          display: 'block',
                        }}
                        onError={(e) => {
                          e.currentTarget.style.display = 'none';
                          const fallback = e.currentTarget.parentElement?.querySelector('.fallback-avatar') as HTMLElement | null;
                          if (fallback) fallback.style.display = 'flex';
                        }}
                      />
                      <div
                        className="fallback-avatar"
                        style={{
                          display: 'none',
                          width: '48px',
                          height: '48px',
                          borderRadius: '50%',
                          background: 'linear-gradient(135deg, #0284c7 0%, #0369a1 100%)',
                          color: '#ffffff',
                          alignItems: 'center',
                          justifyContent: 'center',
                          fontWeight: 800,
                          fontSize: '13px',
                          border: '2px solid rgba(2, 132, 199, 0.4)',
                        }}
                      >
                        {author.initials}
                      </div>
                    </div>
                    <div style={{ minWidth: 0, flex: 1 }}>
                      <div style={{
                        fontWeight: 700,
                        fontSize: '14px',
                        color: '#0f172a',
                        whiteSpace: 'nowrap',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                      }}>
                        {author.name}
                      </div>
                      <div style={{
                        fontSize: '12px',
                        color: '#0284c7',
                        marginTop: '2px',
                        fontWeight: 600,
                        whiteSpace: 'nowrap',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                      }}>
                        {author.role}
                      </div>
                      <div style={{
                        fontSize: '11px',
                        color: '#64748b',
                        marginTop: '1px',
                        whiteSpace: 'nowrap',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                      }}>
                        {author.institution}
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
                      background: '#0a66c2',
                      color: '#ffffff',
                      textDecoration: 'none',
                      padding: '7px 13px',
                      borderRadius: '8px',
                      fontSize: '12px',
                      fontWeight: 700,
                      border: '1px solid rgba(10, 102, 194, 0.3)',
                      boxShadow: '0 2px 6px rgba(10, 102, 194, 0.25)',
                      flexShrink: 0,
                      transition: 'all 0.15s ease',
                    }}
                    title={`Profil LinkedIn ${author.name}`}
                  >
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/>
                    </svg>
                    <span>LinkedIn</span>
                    <span style={{ fontSize: '10px', opacity: 0.85 }}>↗</span>
                  </a>
                </div>
              ))}
            </div>

            {/* Footer */}
            <div style={{
              marginTop: '20px',
              paddingTop: '14px',
              borderTop: '1px solid rgba(226, 232, 240, 0.8)',
              display: 'flex',
              justifyContent: 'flex-end',
            }}>
              <button
                onClick={() => setShowContactModal(false)}
                style={{
                  background: 'rgba(241, 245, 249, 0.9)',
                  border: '1px solid rgba(203, 213, 225, 0.8)',
                  color: '#334155',
                  padding: '8px 20px',
                  borderRadius: '8px',
                  fontSize: '12.5px',
                  fontWeight: 600,
                  cursor: 'pointer',
                  transition: 'all 0.15s ease',
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

