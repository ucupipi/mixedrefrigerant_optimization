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
      title: 'Input & Rekomendasi',
      alert: hasConstraintViolations,
    },
    {
      id: 'process-graphics' as ActiveTabId,
      number: '2',
      title: 'Process Flow Diagram',
      alert: false,
    },
    {
      id: 'operator-guide' as ActiveTabId,
      number: '3',
      title: 'Operator Guidance',
      alert: false,
    },
  ];

  return (
    <nav
      className="no-scrollbar"
      style={{
        position: 'sticky',
        top: '55px',
        zIndex: 90,
        background: 'rgba(255, 255, 255, 0.78)',
        backdropFilter: 'blur(16px)',
        WebkitBackdropFilter: 'blur(16px)',
        borderBottom: '1px solid rgba(226, 232, 240, 0.8)',
        display: 'flex',
        alignItems: 'center',
        padding: '8px 16px',
        gap: '8px',
        boxShadow: '0 4px 20px -2px rgba(15, 23, 42, 0.03)',
        userSelect: 'none',
        flexWrap: 'nowrap',
        scrollbarWidth: 'none',
        msOverflowStyle: 'none',
        overflowX: 'auto',
        WebkitOverflowScrolling: 'touch',
      }}
    >
      {tabs.map((tab) => {
        const isActive = activeTab === tab.id;
        return (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '8px 14px',
              background: isActive
                ? 'rgba(255, 255, 255, 0.98)'
                : 'rgba(241, 245, 249, 0.65)',
              backdropFilter: 'blur(10px)',
              WebkitBackdropFilter: 'blur(10px)',
              color: isActive ? '#0f172a' : '#64748b',
              border: isActive
                ? '1px solid rgba(203, 213, 225, 0.9)'
                : '1px solid transparent',
              borderRadius: '10px',
              cursor: 'pointer',
              transition: 'all 0.2s cubic-bezier(0.16, 1, 0.3, 1)',
              outline: 'none',
              flexShrink: 0,
              boxShadow: isActive ? '0 4px 14px -2px rgba(15, 23, 42, 0.08), inset 0 1px 0 #ffffff' : 'none',
            }}
          >
            <span style={{
              width: '22px',
              height: '22px',
              borderRadius: '7px',
              background: isActive
                ? 'linear-gradient(135deg, #0284c7 0%, #0369a1 100%)'
                : 'rgba(203, 213, 225, 0.7)',
              color: isActive ? '#ffffff' : '#64748b',
              fontSize: '12px',
              fontWeight: 800,
              fontFamily: "'Plus Jakarta Sans', sans-serif",
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0,
            }}>
              {tab.number}
            </span>
            <div style={{ textAlign: 'left', minWidth: 0 }}>
              <div style={{
                fontSize: '13px',
                fontWeight: 700,
                fontFamily: "'Plus Jakarta Sans', 'Inter', sans-serif",
                lineHeight: 1.2,
                color: isActive ? '#0f172a' : '#64748b',
                whiteSpace: 'nowrap',
              }}>
                {tab.title}
              </div>
            </div>
            {tab.alert && (
              <span
                style={{
                  width: '8px',
                  height: '8px',
                  borderRadius: '50%',
                  backgroundColor: '#ef4444',
                  boxShadow: '0 0 6px #ef4444',
                  marginLeft: '2px',
                  flexShrink: 0,
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
