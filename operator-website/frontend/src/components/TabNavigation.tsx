import React from 'react';
import type { ActiveTabId } from '../types';

interface TabNavigationProps {
  activeTab: ActiveTabId;
  onTabChange: (tabId: ActiveTabId) => void;
  hasConstraintViolations: boolean;
}

export const TabNavigation: React.FC<TabNavigationProps> = ({
  activeTab,
  onTabChange,
  hasConstraintViolations,
}) => {
  const tabs = [
    {
      id: 'input-results' as ActiveTabId,
      number: '1',
      title: 'Input & Results',
      subtitle: 'Workspace Skenario, KPI & Injeksi Make-Up',
      alert: hasConstraintViolations,
    },
    {
      id: 'process-graphics' as ActiveTabId,
      number: '2',
      title: 'Process Graphics',
      subtitle: '6 Grafik Proses & Profil Termal MCHE',
      alert: false,
    },
    {
      id: 'operator-guide' as ActiveTabId,
      number: '3',
      title: 'Operator Guide',
      subtitle: 'Alur 7 Langkah, Batasan SOP & Kamus Parameter',
      alert: false,
    },
  ];

  return (
    <nav style={{
      position: 'sticky',
      top: 0,
      zIndex: 100,
      backgroundColor: '#1e293b',
      borderBottom: '3px solid #0284c7',
      display: 'flex',
      alignItems: 'center',
      padding: '0 24px',
      gap: '8px',
      boxShadow: '0 2px 6px rgba(0,0,0,0.15)',
      userSelect: 'none',
      fontFamily: "'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif",
    }}>
      {tabs.map((tab) => {
        const isActive = activeTab === tab.id;
        return (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
              padding: '12px 20px',
              backgroundColor: isActive ? '#f8fafc' : 'transparent',
              color: isActive ? '#0f172a' : '#94a3b8',
              border: 'none',
              borderTopLeftRadius: '6px',
              borderTopRightRadius: '6px',
              cursor: 'pointer',
              transition: 'all 0.15s ease',
              outline: 'none',
              position: 'relative',
              boxShadow: isActive ? '0 -2px 8px rgba(0,0,0,0.12)' : 'none',
            }}
          >
            <span style={{
              width: '24px',
              height: '24px',
              borderRadius: '50%',
              backgroundColor: isActive ? '#0284c7' : '#334155',
              color: '#ffffff',
              fontSize: '13px',
              fontWeight: 800,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}>
              {tab.number}
            </span>
            <div style={{ textAlign: 'left' }}>
              <div style={{
                fontSize: '16px',
                fontWeight: 700,
                lineHeight: 1.2,
                color: isActive ? '#0f172a' : '#cbd5e1',
              }}>
                {tab.title}
              </div>
              <div style={{
                fontSize: '12px',
                fontWeight: 500,
                color: isActive ? '#64748b' : '#64748b',
                marginTop: '2px',
              }}>
                {tab.subtitle}
              </div>
            </div>
            {tab.alert && (
              <span
                style={{
                  width: '9px',
                  height: '9px',
                  borderRadius: '50%',
                  backgroundColor: '#ef4444',
                  boxShadow: '0 0 6px #ef4444',
                  marginLeft: '4px',
                }}
                title="Peringatan batasan terdeteksi"
              />
            )}
          </button>
        );
      })}
    </nav>
  );
};
