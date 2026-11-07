import React, { useState, useRef } from 'react';
import {
  calculateFeedGasMW,
  DEFAULT_FEED_GAS,
  getEstimatedLngFlow,
} from '../utils/thermoFlash';
import type { FeedGasComposition } from '../utils/thermoFlash';
import type {
  ActualDcsState,
  DemoSnapshot,
  OptimizeResponse,
  PredictResponse,
  ScenarioInput,
  UserMode,
} from '../types';

interface TabInputResultsProps {
  snapshot: DemoSnapshot;
  scenario: ScenarioInput;
  actualDcs: ActualDcsState;
  optimum: OptimizeResponse | null;
  prediction: PredictResponse | null;
  userMode: UserMode;
  loading: boolean;
  strategy?: 'CONDITION_DEPENDENT' | 'FIXED_RECIPE' | 'MINIMUM_INTERVENTION';
  onStrategyChange?: (strategy: 'CONDITION_DEPENDENT' | 'FIXED_RECIPE' | 'MINIMUM_INTERVENTION') => void;
  feedGasComp?: FeedGasComposition;
  onFeedGasCompChange?: (comp: FeedGasComposition) => void;
  onActualChange: (key: keyof ActualDcsState, val: number) => void;
  onScenarioChange: (key: keyof ScenarioInput, val: number) => void;
  onCalculate: () => void;
  onOptimize: () => void;
  onNormalizeScenario: () => void;
  onReset: () => void;
}

export const TabInputResults: React.FC<TabInputResultsProps> = ({
  snapshot: _snapshot,
  scenario,
  actualDcs,
  optimum,
  prediction,
  userMode: _userMode,
  loading,
  strategy = 'CONDITION_DEPENDENT',
  onStrategyChange,
  feedGasComp,
  onFeedGasCompChange,
  onActualChange: _onActualChange,
  onScenarioChange,
  onCalculate: _onCalculate,
  onOptimize,
  onNormalizeScenario,
  onReset,
}) => {
  // Feed Gas Composition Modal State
  const [showFeedGasModal, setShowFeedGasModal] = useState<boolean>(false);
  const [localFeedGas, setLocalFeedGas] = useState<Required<FeedGasComposition>>({
    ...DEFAULT_FEED_GAS,
    ...(feedGasComp || {}),
  });

  // Mobile View Switcher: 'card' vs 'table'
  const [mobileMode, setMobileMode] = useState<'card' | 'table'>('card');

  // DOM Refs for responsive horizontal scrolling
  const table1Ref = useRef<HTMLDivElement>(null);
  const table2Ref = useRef<HTMLDivElement>(null);

  const scrollTable = (ref: React.RefObject<HTMLDivElement | null>, direction: 'left' | 'right') => {
    if (ref.current) {
      const scrollAmount = direction === 'right' ? 320 : -320;
      ref.current.scrollBy({ left: scrollAmount, behavior: 'smooth' });
    }
  };

  // Coupling: LNG Rundown follows feed gas rate via PR-EOS 5C-1 Flash Drum phase equilibrium
  const scenarioLngFlow = prediction?.flash_drum_5c1?.lng_liquid_flow_t_h
    ?? scenario.lng_flow_t_h
    ?? getEstimatedLngFlow(scenario.feed_flow_t_h, -152.5, feedGasComp);

  // Power and SEC calculations (Evaluated ceteris-paribus at the active feed & LNG flow)
  const baselinePower = prediction?.baseline_power_mw ?? prediction?.actual_power_mw ?? 84.48;
  const scenarioPower = prediction?.prediction?.total_shaft_power_mw ?? baselinePower;
  const deltaPower = prediction?.prediction?.delta_power_mw ?? (scenarioPower - baselinePower);
  const deltaPowerPct = prediction?.prediction?.delta_power_pct ?? (baselinePower > 0 ? (deltaPower / baselinePower) * 100 : 0);

  const activeLngFlow = Math.max(scenarioLngFlow, 10.0);
  const baselineSecLng = prediction?.baseline_sec_lng ?? ((baselinePower * 1000) / activeLngFlow);
  const scenarioSecLng = prediction?.prediction?.sec_lng_kwh_per_t ?? ((scenarioPower * 1000) / activeLngFlow);
  const deltaSecLng = prediction?.prediction?.delta_sec_kwh_per_t ?? (scenarioSecLng - baselineSecLng);
  const deltaSecLngPct = baselineSecLng > 0 ? (deltaSecLng / baselineSecLng) * 100 : 0;

  // Plant-5 Train H (Liquefaction) Economic & Decarbonization Constants (Manual Book Modul 8 & Stage 08)
  const STEAM_RATE_T_PER_MWH = 4.04; // Verified condensate-meter anchor (R2 = 0.9989, Stage 08)
  const FUEL_GAS_NM3_PER_T_STEAM = 97.7; // Boiler fuel gas consumption (Nm³ fuel gas / t steam, Modul 8)
  const FG_DENSITY_KG_NM3 = 0.75; // Standard fuel gas density (kg/Nm³)
  const FUEL_GAS_MMBTU_PER_NM3 = 0.03535; // Heat content conversion: 35.3147 scf/Nm³ * 1001 BTU/scf / 1e6 MMBTU/BTU
  const FUEL_GAS_PRICE_USD_PER_MMBTU = 6.0; // Plant-5 Train H (Liquefaction) internal fuel gas transfer valuation ($/MMBTU)
  const ANNUAL_OPERATING_HOURS = 8000; // Baseline annual plant operating hours (~91.3% availability)

  const deltaPowerSavingMw = Math.max(0, -deltaPower);
  const steamSaved_t_h = deltaPowerSavingMw * STEAM_RATE_T_PER_MWH;
  const fuelGasSaved_nm3_h = steamSaved_t_h * FUEL_GAS_NM3_PER_T_STEAM;
  const fuelGasSaved_t_h = (fuelGasSaved_nm3_h * FG_DENSITY_KG_NM3) / 1000;
  const fuelGasSaved_usd_yr = (fuelGasSaved_nm3_h * FUEL_GAS_MMBTU_PER_NM3 * FUEL_GAS_PRICE_USD_PER_MMBTU * ANNUAL_OPERATING_HOURS) / 1_000_000;

  // Potential savings if AI Recommendation (Target MCR) is applied vs DCS baseline
  // Physical derivation: MCR reduction (recMcrFlow vs current MCR) saves ~0.093 MW / (t/h)
  const recMcrFlow = optimum?.mcr_flow_t_h ?? 480.0;
  const recN2 = optimum?.comp_N2_molpct ?? 3.31;
  const recC1 = optimum?.comp_C1_molpct ?? 46.08;
  const recC2 = optimum?.comp_C2_molpct ?? 45.15;
  const recC2H4 = optimum?.comp_C2H4_molpct ?? 0.05;
  const recC3 = optimum?.comp_C3_molpct ?? 5.41;

  const potentialAiPowerSavingMw = Math.max(
    0.5,
    deltaPower > 0
      ? deltaPower + Math.max(0, (scenario.mcr_flow_t_h - recMcrFlow) * 0.093)
      : Math.max(0, -deltaPower)
  );
  const potentialAiSecSavingKwh = activeLngFlow > 0 ? (potentialAiPowerSavingMw * 1000) / activeLngFlow : 0;

  // Make-Up MCR Schedule items (from backend makeup_advisory or computed dynamically)
  const makeupTransitionHours = prediction?.makeup_advisory?.transition_hours ?? scenario.transition_hours ?? 2.0;
  const makeupInventoryKg = prediction?.makeup_advisory?.estimated_inventory_kg ?? 85000;

  const actualCompMap = {
    N2: actualDcs.comp_N2_molpct,
    C1: actualDcs.comp_C1_molpct,
    C2: actualDcs.comp_C2_molpct,
    C2H4: actualDcs.comp_C2H4_molpct,
    C3: actualDcs.comp_C3_molpct,
  };
  const targetCompMap = {
    N2: scenario.comp_N2_molpct,
    C1: scenario.comp_C1_molpct,
    C2: scenario.comp_C2_molpct,
    C2H4: scenario.comp_C2H4_molpct,
    C3: scenario.comp_C3_molpct,
  };
  const compMeta = [
    { key: 'N2', name: 'Nitrogen (N₂)', tag: 'H4FIC008', mw: 28.0134, line: 'Line N₂ Make-up (3E-10 Inlet)' },
    { key: 'C1', name: 'Methane (C₁)', tag: '4PV-021', mw: 16.0425, line: 'Feed Gas In-Line Blend' },
    { key: 'C2', name: 'Ethane (C₂)', tag: '3FV-014', mw: 30.0690, line: 'De-ethanizer Overhead' },
    { key: 'C2H4', name: 'Ethylene (C₂H₄)', tag: '3FV-018', mw: 28.0532, line: 'Pure Ethylene Sphere Make-up' },
    { key: 'C3', name: 'Propane (C₃)', tag: '3FV-022', mw: 44.0956, line: 'De-propanizer Distillate Make-up' },
  ];

  const makeupItems = (prediction?.makeup_advisory?.items && prediction.makeup_advisory.items.length > 0)
    ? prediction.makeup_advisory.items
    : compMeta.map((c) => {
      const act = (actualCompMap as any)[c.key] ?? 0;
      const tgt = (targetCompMap as any)[c.key] ?? 0;
      const delta = tgt - act;
      const isInject = delta > 0.02;
      const deltaFrac = Math.max(0, delta) / 100.0;
      const kgTotal = deltaFrac * makeupInventoryKg;
      const kgPerHour = kgTotal / makeupTransitionHours;
      const nm3PerHour = (kgPerHour / c.mw) * 22.414;
      return {
        component: c.key,
        tag_dcs: c.tag,
        description: c.name,
        unit: 'Nm³/h',
        actual_molpct: act,
        target_molpct: tgt,
        delta_molpct: delta,
        recommended_flow_nm3_h: nm3PerHour,
        recommended_flow_kg_h: kgPerHour,
        action: isInject ? 'INJECT' : 'HOLD',
        instruction: isInject
          ? `Gradually open control valve ${c.tag}, rate ${nm3PerHour.toFixed(1)} Nm³/h (${kgPerHour.toFixed(1)} kg/h) over ${makeupTransitionHours} hours.`
          : `Maintain minimum valve position (0 Nm³/h); component fraction meets target.`,
      };
    });

  const totalMakeupFlowNm3 = prediction?.makeup_advisory?.total_makeup_flow_nm3_h
    ?? makeupItems.reduce((acc, it) => acc + (it.recommended_flow_nm3_h || 0), 0);
  const totalMakeupFlowKg = prediction?.makeup_advisory?.total_makeup_flow_kg_h
    ?? makeupItems.reduce((acc, it) => acc + (it.recommended_flow_kg_h || 0), 0);

  // Composition sum
  const compSum =
    scenario.comp_N2_molpct +
    scenario.comp_C1_molpct +
    scenario.comp_C2_molpct +
    scenario.comp_C2H4_molpct +
    scenario.comp_C3_molpct;
  const isCompositionClosed = Math.abs(compSum - 100.0) < 0.05;

  const handleApplyRecommended = () => {
    onScenarioChange('mcr_flow_t_h', recMcrFlow);
    onScenarioChange('comp_N2_molpct', recN2);
    onScenarioChange('comp_C1_molpct', recC1);
    onScenarioChange('comp_C2_molpct', recC2);
    onScenarioChange('comp_C2H4_molpct', recC2H4);
    onScenarioChange('comp_C3_molpct', recC3);
    if (onOptimize) {
      onOptimize();
    }
  };

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      gap: '24px',
      paddingBottom: '36px',
      fontFamily: "'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif",
      color: '#0f172a',
    }}>

      {/* =================================================================== */}
      {/* SECTION 1: INPUT VARIABEL PROSES & REKOMENDASI AI                  */}
      {/* =================================================================== */}
      <section style={{
        backgroundColor: 'rgba(255, 255, 255, 0.85)',
        backdropFilter: 'blur(16px)',
        WebkitBackdropFilter: 'blur(16px)',
        borderRadius: '16px',
        border: '1px solid rgba(226, 232, 240, 0.85)',
        boxShadow: '0 4px 20px -2px rgba(15, 23, 42, 0.04), inset 0 1px 0 #ffffff',
        overflow: 'hidden',
      }}>
        {/* Section Header */}
        <div className="section1-header" style={{
          backgroundColor: 'rgba(248, 250, 252, 0.9)',
          backdropFilter: 'blur(10px)',
          color: '#0f172a',
          padding: '14px 20px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          borderBottom: '1px solid rgba(226, 232, 240, 0.9)',
          flexWrap: 'wrap',
          gap: '12px',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span style={{
              width: '24px',
              height: '24px',
              borderRadius: '6px',
              background: 'linear-gradient(135deg, #0284c7 0%, #0369a1 100%)',
              color: '#ffffff',
              fontSize: '12px',
              fontWeight: 800,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 2px 6px rgba(2, 132, 199, 0.3)',
            }}>
              1
            </span>
            <span style={{ fontSize: '15px', fontWeight: 800, color: '#0f172a', letterSpacing: '-0.2px' }}>
              Operating Conditions & MCR Targets
            </span>
          </div>

          <div className="section1-buttons" style={{ display: 'flex', gap: '8px', alignItems: 'center', flexWrap: 'wrap' }}>
            <button
              onClick={() => {
                setLocalFeedGas({ ...DEFAULT_FEED_GAS, ...(feedGasComp || {}) });
                setShowFeedGasModal(true);
              }}
              disabled={loading}
              style={{
                backgroundColor: 'rgba(255, 255, 255, 0.9)',
                color: '#0369a1',
                border: '1px solid rgba(203, 213, 225, 0.9)',
                borderRadius: '8px',
                padding: '7px 14px',
                fontWeight: 600,
                fontSize: '13px',
                cursor: loading ? 'not-allowed' : 'pointer',
                boxShadow: '0 1px 3px rgba(0, 0, 0, 0.04)',
                transition: 'all 0.15s ease',
              }}
              title="Configure 3C-1 overhead feed gas composition to MCHE"
            >
              Feed Gas Composition
            </button>
            <button
              onClick={handleApplyRecommended}
              disabled={loading}
              style={{
                background: 'linear-gradient(135deg, #059669 0%, #047857 100%)',
                color: '#ffffff',
                border: 'none',
                borderRadius: '8px',
                padding: '7px 16px',
                fontWeight: 700,
                fontSize: '13px',
                cursor: loading ? 'not-allowed' : 'pointer',
                boxShadow: '0 2px 6px rgba(5, 150, 105, 0.25)',
                transition: 'all 0.15s ease',
              }}
            >
              Apply AI Target
            </button>
            <button
              onClick={onReset}
              disabled={loading}
              style={{
                backgroundColor: 'rgba(241, 245, 249, 0.9)',
                color: '#475569',
                border: '1px solid rgba(203, 213, 225, 0.9)',
                borderRadius: '8px',
                padding: '7px 14px',
                fontWeight: 600,
                fontSize: '13px',
                cursor: loading ? 'not-allowed' : 'pointer',
                transition: 'all 0.15s ease',
              }}
            >
              Reset to DCS
            </button>
          </div>
        </div>

        {/* Section Content: Comparison Table */}
        <div style={{ padding: '16px 20px', minWidth: 0, maxWidth: '100%', boxSizing: 'border-box' }}>
          {/* OPERATING STRATEGY SELECTOR (Master Prompt Strategy A / B / C) */}
          <div style={{
            marginBottom: '16px',
            padding: '14px 16px',
            backgroundColor: '#f8fafc',
            border: '1px solid #e2e8f0',
            borderRadius: '12px',
            boxShadow: '0 1px 3px rgba(0, 0, 0, 0.02)',
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px', flexWrap: 'wrap', gap: '8px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ fontSize: '13px', fontWeight: 800, color: '#1e293b', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                  Optimization Strategy Policy
                </span>
                <span style={{ fontSize: '11px', backgroundColor: '#e0f2fe', color: '#0369a1', padding: '2px 8px', borderRadius: '4px', fontWeight: 700 }}>
                  Advisory Decision Support (Zero Direct DCS Write)
                </span>
              </div>
              {optimum?.strategy && (
                <span style={{ fontSize: '11px', color: '#64748b', fontWeight: 600 }}>
                  Active Engine: <strong style={{ color: '#0f172a' }}>{optimum.strategy}</strong>
                </span>
              )}
            </div>

            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
              gap: '10px',
            }}>
              {/* Strategy B: Condition-Dependent */}
              <button
                type="button"
                onClick={() => onStrategyChange?.('CONDITION_DEPENDENT')}
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'flex-start',
                  padding: '10px 14px',
                  backgroundColor: strategy === 'CONDITION_DEPENDENT' ? '#eff6ff' : '#ffffff',
                  border: strategy === 'CONDITION_DEPENDENT' ? '2px solid #2563eb' : '1px solid #cbd5e1',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  textAlign: 'left',
                  transition: 'all 0.15s ease',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', width: '100%', marginBottom: '4px' }}>
                  <input
                    type="radio"
                    name="opt_strategy"
                    checked={strategy === 'CONDITION_DEPENDENT'}
                    onChange={() => onStrategyChange?.('CONDITION_DEPENDENT')}
                    style={{ accentColor: '#2563eb', cursor: 'pointer' }}
                  />
                  <strong style={{ fontSize: '12px', color: strategy === 'CONDITION_DEPENDENT' ? '#1d4ed8' : '#334155' }}>
                    Strategy B: Condition-Dependent
                  </strong>
                </div>
                <span style={{ fontSize: '11px', color: '#64748b', lineHeight: 1.35 }}>
                  Full 5D dynamic MR composition and circulation optimization per operating condition across the load curve.
                </span>
              </button>

              {/* Strategy A: Fixed Recipe */}
              <button
                type="button"
                onClick={() => onStrategyChange?.('FIXED_RECIPE')}
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'flex-start',
                  padding: '10px 14px',
                  backgroundColor: strategy === 'FIXED_RECIPE' ? '#eff6ff' : '#ffffff',
                  border: strategy === 'FIXED_RECIPE' ? '2px solid #2563eb' : '1px solid #cbd5e1',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  textAlign: 'left',
                  transition: 'all 0.15s ease',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', width: '100%', marginBottom: '4px' }}>
                  <input
                    type="radio"
                    name="opt_strategy"
                    checked={strategy === 'FIXED_RECIPE'}
                    onChange={() => onStrategyChange?.('FIXED_RECIPE')}
                    style={{ accentColor: '#2563eb', cursor: 'pointer' }}
                  />
                  <strong style={{ fontSize: '12px', color: strategy === 'FIXED_RECIPE' ? '#1d4ed8' : '#334155' }}>
                    Strategy A: Fixed Recipe Across Loads
                  </strong>
                </div>
                <span style={{ fontSize: '11px', color: '#64748b', lineHeight: 1.35 }}>
                  Maintain certified constant baseline recipe; circulation scales with feed flow to minimize make-up transitions.
                </span>
              </button>

              {/* Strategy C: Minimum Intervention */}
              <button
                type="button"
                onClick={() => onStrategyChange?.('MINIMUM_INTERVENTION')}
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'flex-start',
                  padding: '10px 14px',
                  backgroundColor: strategy === 'MINIMUM_INTERVENTION' ? '#eff6ff' : '#ffffff',
                  border: strategy === 'MINIMUM_INTERVENTION' ? '2px solid #2563eb' : '1px solid #cbd5e1',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  textAlign: 'left',
                  transition: 'all 0.15s ease',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', width: '100%', marginBottom: '4px' }}>
                  <input
                    type="radio"
                    name="opt_strategy"
                    checked={strategy === 'MINIMUM_INTERVENTION'}
                    onChange={() => onStrategyChange?.('MINIMUM_INTERVENTION')}
                    style={{ accentColor: '#2563eb', cursor: 'pointer' }}
                  />
                  <strong style={{ fontSize: '12px', color: strategy === 'MINIMUM_INTERVENTION' ? '#1d4ed8' : '#334155' }}>
                    Strategy C: Minimum-Intervention
                  </strong>
                </div>
                <span style={{ fontSize: '11px', color: '#64748b', lineHeight: 1.35 }}>
                  Penalize composition movement from current loop inventory; balances thermodynamic gain against make-up costs.
                </span>
              </button>
            </div>

            {/* Strategy Explanation Banner */}
            {optimum?.explanation && (
              <div style={{
                marginTop: '10px',
                padding: '8px 12px',
                backgroundColor: '#f1f5f9',
                borderLeft: '3px solid #0284c7',
                borderRadius: '4px',
                fontSize: '11px',
                color: '#334155',
                lineHeight: 1.4,
              }}>
                <strong>Strategy Explanation:</strong> {optimum.explanation}
              </div>
            )}

            {/* Thermodynamic Constraint Residuals */}
            {optimum?.constraint_residuals && (
              <div style={{
                marginTop: '8px',
                display: 'flex',
                gap: '12px',
                flexWrap: 'wrap',
                fontSize: '11px',
                color: '#475569',
              }}>
                <span>Suction TAL Margin: <strong style={{ color: optimum.constraint_residuals.suction_tal_margin_c >= 0 ? '#16a34a' : '#dc2626' }}>+{optimum.constraint_residuals.suction_tal_margin_c.toFixed(2)} °C</strong></span>
                <span>Anti-Surge Margin: <strong style={{ color: optimum.constraint_residuals.antisurge_margin_t_h >= 0 ? '#16a34a' : '#dc2626' }}>+{optimum.constraint_residuals.antisurge_margin_t_h.toFixed(1)} t/h</strong></span>
                <span>Superheat Margin: <strong style={{ color: optimum.constraint_residuals.superheat_margin_c >= 0 ? '#16a34a' : '#dc2626' }}>+{optimum.constraint_residuals.superheat_margin_c.toFixed(2)} °C</strong></span>
                <span>Mahalanobis Margin: <strong style={{ color: optimum.constraint_residuals.mahalanobis_margin >= 0 ? '#16a34a' : '#dc2626' }}>+{optimum.constraint_residuals.mahalanobis_margin.toFixed(3)}</strong></span>
              </div>
            )}
          </div>

          {/* Capacity Boundary Warning Card */}
          {prediction?.prediction?.capacity_warning && (
            <div style={{
              backgroundColor: '#fffbeb',
              border: '1px solid #fde68a',
              borderRadius: '8px',
              padding: '12px 16px',
              marginBottom: '14px',
              display: 'flex',
              alignItems: 'flex-start',
              gap: '12px',
              color: '#92400e',
              fontSize: '13px',
              fontWeight: 600,
              boxShadow: '0 1px 3px rgba(0,0,0,0.04)',
            }}>
              <span style={{ fontSize: '20px', lineHeight: 1 }}>⚠️</span>
              <div>
                <div style={{ fontWeight: 800, color: '#78350f', marginBottom: '2px' }}>
                  TRAIN H DESIGN CAPACITY WARNING
                </div>
                <div style={{ color: '#92400e', fontWeight: 500, lineHeight: 1.4 }}>
                  {prediction.prediction.capacity_warning}
                </div>
              </div>
            </div>
          )}

          {/* Mobile View Toggle: Cards vs Table */}
          <div className="mobile-view-toggle-bar">
            <button
              type="button"
              onClick={() => setMobileMode('card')}
              className={`view-toggle-btn ${mobileMode === 'card' ? 'view-toggle-active' : ''}`}
            >
              📱 Mobile Card View (Compact)
            </button>
            <button
              type="button"
              onClick={() => setMobileMode('table')}
              className={`view-toggle-btn ${mobileMode === 'table' ? 'view-toggle-active' : ''}`}
            >
              📊 Full Table View (Scroll ↔)
            </button>
          </div>

          {/* Mobile Card Deck for Section 1 (Rendered on mobile screens when mobileMode === 'card') */}
          {mobileMode === 'card' && (
            <div className="mobile-card-deck">
              {/* Card 1: Feed Gas Flow */}
              <div className="mobile-param-card">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                  <span style={{ fontWeight: 700, fontSize: '13.5px', color: '#0f172a' }}>MCHE Feed Gas Flow (5E-1)</span>
                  <span style={{ fontFamily: 'monospace', fontSize: '11px', color: '#0284c7', backgroundColor: '#e0f2fe', padding: '2px 6px', borderRadius: '4px', fontWeight: 600 }}>H3FI0004</span>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', alignItems: 'center' }}>
                  <div style={{ backgroundColor: '#f8fafc', padding: '8px 10px', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                    <div style={{ fontSize: '11px', color: '#64748b', fontWeight: 600, marginBottom: '4px' }}>Input DCS (t/h)</div>
                    <input
                      type="number"
                      step="0.5"
                      min="100"
                      max="500"
                      value={scenario.feed_flow_t_h}
                      onChange={(e) => onScenarioChange('feed_flow_t_h', parseFloat(e.target.value) || 0)}
                      style={{ width: '80px', padding: '5px 8px', border: '1px solid #cbd5e1', borderRadius: '6px', fontWeight: 700, fontSize: '13px' }}
                    />
                    <div style={{ fontSize: '10.5px', color: '#475569', marginTop: '4px' }}>LNG: {scenarioLngFlow.toFixed(1)} t/h</div>
                  </div>
                  <div style={{ backgroundColor: '#ecfdf5', padding: '8px 10px', borderRadius: '8px', border: '1px solid #a7f3d0' }}>
                    <div style={{ fontSize: '11px', color: '#065f46', fontWeight: 600, marginBottom: '4px' }}>AI Target</div>
                    <div style={{ fontSize: '15px', fontWeight: 800, color: '#047857' }}>{scenario.feed_flow_t_h.toFixed(1)} <span style={{ fontSize: '11px', fontWeight: 600 }}>t/h</span></div>
                    <div style={{ fontSize: '10px', color: '#0369a1', fontWeight: 700, marginTop: '2px' }}>Fixed Load</div>
                  </div>
                </div>
              </div>

              {/* Card 2: MCR Circulation Flow */}
              <div className="mobile-param-card">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                  <span style={{ fontWeight: 700, fontSize: '13.5px', color: '#0f172a' }}>MCR Circulation Flow</span>
                  <span style={{ fontFamily: 'monospace', fontSize: '11px', color: '#0284c7', backgroundColor: '#e0f2fe', padding: '2px 6px', borderRadius: '4px', fontWeight: 600 }}>H4FI001</span>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', alignItems: 'center' }}>
                  <div style={{ backgroundColor: '#f8fafc', padding: '8px 10px', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                    <div style={{ fontSize: '11px', color: '#64748b', fontWeight: 600, marginBottom: '4px' }}>Input DCS (t/h)</div>
                    <input
                      type="number"
                      step="0.5"
                      min="400"
                      max="1200"
                      value={scenario.mcr_flow_t_h}
                      onChange={(e) => onScenarioChange('mcr_flow_t_h', parseFloat(e.target.value) || 0)}
                      style={{ width: '80px', padding: '5px 8px', border: '1px solid #cbd5e1', borderRadius: '6px', fontWeight: 700, fontSize: '13px' }}
                    />
                  </div>
                  <div style={{ backgroundColor: '#ecfdf5', padding: '8px 10px', borderRadius: '8px', border: '1px solid #a7f3d0' }}>
                    <div style={{ fontSize: '11px', color: '#065f46', fontWeight: 600, marginBottom: '4px' }}>AI Target</div>
                    <div style={{ fontSize: '15px', fontWeight: 800, color: '#047857' }}>{recMcrFlow.toFixed(1)} <span style={{ fontSize: '11px', fontWeight: 600 }}>t/h</span></div>
                    <div style={{ fontSize: '10px', color: scenario.mcr_flow_t_h > recMcrFlow ? '#15803d' : '#475569', fontWeight: 700, marginTop: '2px' }}>
                      {scenario.mcr_flow_t_h > recMcrFlow ? `Save ${(scenario.mcr_flow_t_h - recMcrFlow).toFixed(1)} t/h` : 'Optimal'}
                    </div>
                  </div>
                </div>
              </div>

              {/* Cards 3-7: 5 MCR Compositions */}
              {[
                { name: 'Nitrogen (N₂)', key: 'comp_N2_molpct' as const, rec: recN2, tag: 'comp_N2' },
                { name: 'Methane (CH₄ / C₁)', key: 'comp_C1_molpct' as const, rec: recC1, tag: 'comp_C1' },
                { name: 'Ethane (C₂H₆ / C₂)', key: 'comp_C2_molpct' as const, rec: recC2, tag: 'comp_C2' },
                { name: 'Ethylene (C₂H₄)', key: 'comp_C2H4_molpct' as const, rec: recC2H4, tag: 'comp_C2H4' },
                { name: 'Propane (C₃H₈ / C₃)', key: 'comp_C3_molpct' as const, rec: recC3, tag: 'comp_C3' },
              ].map((comp) => {
                const diff = comp.rec - scenario[comp.key];
                const diffSign = diff > 0 ? '+' : '';
                return (
                  <div key={comp.key} className="mobile-param-card">
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                      <span style={{ fontWeight: 600, fontSize: '13px', color: '#1e293b' }}>{comp.name}</span>
                      <span style={{ fontFamily: 'monospace', fontSize: '10.5px', color: '#64748b' }}>{comp.tag}</span>
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', alignItems: 'center' }}>
                      <div style={{ backgroundColor: '#f8fafc', padding: '6px 10px', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                        <div style={{ fontSize: '10.5px', color: '#64748b', fontWeight: 600, marginBottom: '2px' }}>Input DCS</div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                          <input
                            type="number"
                            step="0.05"
                            min="0"
                            max="100"
                            value={scenario[comp.key]}
                            onChange={(e) => onScenarioChange(comp.key, parseFloat(e.target.value) || 0)}
                            style={{ width: '70px', padding: '4px 6px', border: '1px solid #cbd5e1', borderRadius: '6px', fontWeight: 600, fontSize: '12.5px' }}
                          />
                          <span style={{ fontSize: '11px', color: '#64748b' }}>mol%</span>
                        </div>
                      </div>
                      <div style={{ backgroundColor: '#ecfdf5', padding: '6px 10px', borderRadius: '8px', border: '1px solid #a7f3d0' }}>
                        <div style={{ fontSize: '10.5px', color: '#065f46', fontWeight: 600, marginBottom: '2px' }}>AI Target</div>
                        <div style={{ fontSize: '14px', fontWeight: 800, color: '#047857' }}>
                          {comp.rec.toFixed(2)} <span style={{ fontSize: '11px', fontWeight: 600 }}>mol%</span>
                        </div>
                        <div style={{ fontSize: '10px', color: Math.abs(diff) > 0.01 ? (diff > 0 ? '#15803d' : '#b45309') : '#64748b', fontWeight: 700 }}>
                          Δ {diffSign}{diff.toFixed(2)} mol%
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}

              {/* Card 8: Total Composition Summary */}
              <div className="mobile-param-card" style={{ backgroundColor: isCompositionClosed ? '#f0fdf4' : '#fef2f2', border: isCompositionClosed ? '1px solid #86efac' : '1px solid #fca5a5' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontWeight: 800, fontSize: '13px', color: isCompositionClosed ? '#166534' : '#991b1b' }}>Total MCR Composition</span>
                  <span style={{ backgroundColor: isCompositionClosed ? '#dcfce7' : '#fee2e2', color: isCompositionClosed ? '#15803d' : '#b91c1c', padding: '2px 8px', borderRadius: '6px', fontWeight: 800, fontSize: '12px' }}>
                    {compSum.toFixed(2)} mol%
                  </span>
                </div>
                {!isCompositionClosed && (
                  <button
                    onClick={onNormalizeScenario}
                    style={{ marginTop: '8px', width: '100%', backgroundColor: '#ef4444', color: '#ffffff', border: 'none', borderRadius: '6px', padding: '6px 12px', fontSize: '12px', fontWeight: 700, cursor: 'pointer' }}
                  >
                    Normalize to 100%
                  </button>
                )}
              </div>
            </div>
          )}

          {/* Mobile Swipe & Scroll Control Bar */}
          <div className={`mobile-swipe-hint mobile-swipe-control ${mobileMode === 'card' ? 'mobile-hide' : ''}`}>
            <div className="mobile-swipe-info">
              <span>👉 Swipe for AI Target & Units ↔</span>
            </div>
            <div className="mobile-scroll-btns">
              <button
                type="button"
                onClick={() => scrollTable(table1Ref, 'left')}
                className="scroll-btn"
                aria-label="Scroll left"
              >
                ◀ Left
              </button>
              <button
                type="button"
                onClick={() => scrollTable(table1Ref, 'right')}
                className="scroll-btn scroll-btn-primary"
                aria-label="Scroll right"
              >
                Right ▶
              </button>
            </div>
          </div>

          <div
            ref={table1Ref}
            className={`table-scroll-container ${mobileMode === 'card' ? 'mobile-hide' : ''}`}
            style={{
              width: '100%',
              maxWidth: '100%',
              minWidth: 0,
              overflowX: 'auto',
              WebkitOverflowScrolling: 'touch',
              borderRadius: '8px',
              border: '1px solid #e2e8f0',
              boxShadow: 'inset 0 1px 2px rgba(0,0,0,0.02)',
            }}
          >
            <table style={{
              width: '100%',
              minWidth: '720px',
              borderCollapse: 'separate',
              borderSpacing: 0,
              fontSize: '14px',
              textAlign: 'left',
            }}>
            <thead>
              <tr style={{ backgroundColor: '#f1f5f9', color: '#475569' }}>
                <th className="sticky-col-header" style={{ padding: '10px 14px', fontWeight: 700, fontSize: '13px', width: '26%', minWidth: '150px', borderBottom: '2px solid #cbd5e1' }}>
                  Operating Parameter
                </th>
                <th style={{ padding: '10px 14px', fontWeight: 700, fontSize: '13px', width: '12%', minWidth: '85px', borderBottom: '2px solid #cbd5e1' }}>DCS Tag</th>
                <th style={{ padding: '10px 14px', fontWeight: 700, fontSize: '13px', width: '26%', minWidth: '160px', backgroundColor: '#f8fafc', borderBottom: '2px solid #cbd5e1' }}>
                  Current Input
                </th>
                <th style={{ padding: '10px 14px', fontWeight: 700, fontSize: '13px', width: '24%', minWidth: '150px', backgroundColor: '#ecfdf5', color: '#065f46', borderBottom: '2px solid #a7f3d0' }}>
                  AI Target
                </th>
                <th style={{ padding: '10px 14px', fontWeight: 700, fontSize: '13px', width: '12%', minWidth: '60px', borderBottom: '2px solid #cbd5e1' }}>Unit</th>
              </tr>
            </thead>
            <tbody>
              {/* Row 1: Feed Gas Flow */}
              <tr style={{ borderBottom: '1px solid #e2e8f0' }}>
                <td className="sticky-col-cell" style={{ padding: '10px 14px', fontWeight: 600, borderBottom: '1px solid #e2e8f0' }}>
                  MCHE Feed Gas Flow (5E-1)
                </td>
                <td style={{ padding: '10px 14px', fontFamily: 'monospace', color: '#0284c7', fontSize: '13px', borderBottom: '1px solid #e2e8f0' }}>
                  H3FI0004
                </td>
                <td style={{ padding: '8px 14px', backgroundColor: '#f8fafc', borderBottom: '1px solid #e2e8f0' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <input
                      type="number"
                      step="0.5"
                      min="100"
                      max="500"
                      value={scenario.feed_flow_t_h}
                      onChange={(e) => onScenarioChange('feed_flow_t_h', parseFloat(e.target.value) || 0)}
                      style={{
                        width: '100px',
                        padding: '6px 10px',
                        border: '1px solid #cbd5e1',
                        borderRadius: '6px',
                        fontWeight: 700,
                        fontSize: '13px',
                        color: '#0f172a',
                      }}
                    />
                    <span style={{
                      backgroundColor: '#e2e8f0',
                      color: '#475569',
                      padding: '2px 8px',
                      borderRadius: '10px',
                      fontSize: '11px',
                      fontWeight: 600,
                    }}>
                      LNG: {scenarioLngFlow.toFixed(1)} t/h
                    </span>
                  </div>
                </td>
                <td style={{ padding: '10px 14px', backgroundColor: '#ecfdf5', fontWeight: 700, color: '#047857', borderBottom: '1px solid #e2e8f0' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span>{scenario.feed_flow_t_h.toFixed(1)}</span>
                    <span style={{
                      backgroundColor: '#e0f2fe',
                      color: '#0369a1',
                      padding: '2px 8px',
                      borderRadius: '12px',
                      fontSize: '11px',
                      fontWeight: 700,
                    }} title="Fixed Load (Plant Disturbance)">
                      Scenario Input / Fixed Load
                    </span>
                  </div>
                </td>
                <td style={{ padding: '10px 14px', color: '#64748b', fontWeight: 600, borderBottom: '1px solid #e2e8f0' }}>
                  t/h
                </td>
              </tr>

              {/* Row 2: MCR Flow */}
              <tr style={{ borderBottom: '1px solid #e2e8f0', backgroundColor: '#fbfcfd' }}>
                <td className="sticky-col-cell" style={{ padding: '10px 14px', fontWeight: 600, borderBottom: '1px solid #e2e8f0' }}>
                  MCR Circulation Flow
                </td>
                <td style={{ padding: '10px 14px', fontFamily: 'monospace', color: '#0284c7', fontSize: '13px', borderBottom: '1px solid #e2e8f0' }}>
                  H4FI001
                </td>
                <td style={{ padding: '8px 14px', backgroundColor: '#f8fafc', borderBottom: '1px solid #e2e8f0' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <input
                      type="number"
                      step="1.0"
                      min="450"
                      max="650"
                      value={scenario.mcr_flow_t_h}
                      onChange={(e) => onScenarioChange('mcr_flow_t_h', parseFloat(e.target.value) || 0)}
                      style={{
                        width: '100px',
                        padding: '6px 10px',
                        border: scenario.mcr_flow_t_h < 480 ? '2px solid #ef4444' : '1px solid #cbd5e1',
                        borderRadius: '6px',
                        fontWeight: 700,
                        fontSize: '13px',
                        color: scenario.mcr_flow_t_h < 480 ? '#b91c1c' : '#0f172a',
                      }}
                    />
                    {scenario.mcr_flow_t_h < 480 && (
                      <span style={{
                        backgroundColor: '#fee2e2',
                        color: '#b91c1c',
                        padding: '2px 6px',
                        borderRadius: '4px',
                        fontSize: '11px',
                        fontWeight: 700,
                      }}>
                        Minimum Floor 480
                      </span>
                    )}
                  </div>
                </td>
                <td style={{ padding: '10px 14px', backgroundColor: '#ecfdf5', fontWeight: 700, color: '#047857', borderBottom: '1px solid #e2e8f0' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span>{recMcrFlow.toFixed(1)}</span>
                    {recMcrFlow < scenario.mcr_flow_t_h ? (
                      <span style={{
                        backgroundColor: '#dcfce7',
                        color: '#15803d',
                        padding: '2px 8px',
                        borderRadius: '12px',
                        fontSize: '11px',
                        fontWeight: 700,
                      }}>
                        Save {(scenario.mcr_flow_t_h - recMcrFlow).toFixed(1)} t/h
                      </span>
                    ) : (
                      <span style={{
                        backgroundColor: '#e2e8f0',
                        color: '#475569',
                        padding: '2px 8px',
                        borderRadius: '12px',
                        fontSize: '11px',
                        fontWeight: 700,
                      }}>
                        Optimal
                      </span>
                    )}
                  </div>
                </td>
                <td style={{ padding: '10px 14px', color: '#64748b', fontWeight: 600, borderBottom: '1px solid #e2e8f0' }}>
                  t/h
                </td>
              </tr>

              {/* Rows 3-7: MCR Compositions */}
              {[
                { name: 'Nitrogen (N₂)', key: 'comp_N2_molpct' as const, rec: recN2, tag: 'comp_N2' },
                { name: 'Methane (CH₄ / C₁)', key: 'comp_C1_molpct' as const, rec: recC1, tag: 'comp_C1' },
                { name: 'Ethane (C₂H₆ / C₂)', key: 'comp_C2_molpct' as const, rec: recC2, tag: 'comp_C2' },
                { name: 'Ethylene (C₂H₄)', key: 'comp_C2H4_molpct' as const, rec: recC2H4, tag: 'comp_C2H4' },
                { name: 'Propane (C₃H₈ / C₃)', key: 'comp_C3_molpct' as const, rec: recC3, tag: 'comp_C3' },
              ].map((comp, idx) => (
                <tr key={comp.key} style={{ borderBottom: '1px solid #e2e8f0', backgroundColor: idx % 2 === 0 ? '#ffffff' : '#fbfcfd' }}>
                  <td className="sticky-col-cell" style={{ padding: '10px 14px', fontWeight: 500, paddingLeft: '24px', borderBottom: '1px solid #e2e8f0' }}>
                    {comp.name}
                  </td>
                  <td style={{ padding: '10px 14px', fontFamily: 'monospace', color: '#64748b', fontSize: '13px', borderBottom: '1px solid #e2e8f0' }}>
                    {comp.tag}
                  </td>
                  <td style={{ padding: '8px 14px', backgroundColor: '#f8fafc', borderBottom: '1px solid #e2e8f0' }}>
                    <input
                      type="number"
                      step="0.05"
                      min="0"
                      max="100"
                      value={scenario[comp.key]}
                      onChange={(e) => onScenarioChange(comp.key, parseFloat(e.target.value) || 0)}
                      style={{
                        width: '100px',
                        padding: '6px 10px',
                        border: '1px solid #cbd5e1',
                        borderRadius: '6px',
                        fontWeight: 600,
                        fontSize: '13px',
                      }}
                    />
                  </td>
                  <td style={{ padding: '10px 14px', backgroundColor: '#ecfdf5', fontWeight: 700, color: '#047857', borderBottom: '1px solid #e2e8f0' }}>
                    {comp.rec.toFixed(2)}
                  </td>
                  <td style={{ padding: '10px 14px', color: '#64748b', fontSize: '13px', borderBottom: '1px solid #e2e8f0' }}>
                    mol%
                  </td>
                </tr>
              ))}

              {/* Total Composition Row */}
              <tr style={{ backgroundColor: isCompositionClosed ? '#f0fdf4' : '#fef2f2', borderTop: '2px solid #cbd5e1' }}>
                <td className="sticky-col-cell" style={{ padding: '10px 14px', fontWeight: 700, backgroundColor: isCompositionClosed ? '#f0fdf4' : '#fee2e2', borderTop: '2px solid #cbd5e1' }}>
                  Total MCR Composition
                </td>
                <td style={{ padding: '10px 14px', fontSize: '12px', color: '#64748b', borderTop: '2px solid #cbd5e1' }}>
                  Σ 5 Fractions
                </td>
                <td style={{ padding: '10px 14px', borderTop: '2px solid #cbd5e1' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <span style={{
                      backgroundColor: isCompositionClosed ? '#dcfce7' : '#fee2e2',
                      color: isCompositionClosed ? '#15803d' : '#b91c1c',
                      padding: '3px 8px',
                      borderRadius: '6px',
                      fontWeight: 800,
                    }}>
                      {compSum.toFixed(2)} mol%
                    </span>
                    {!isCompositionClosed && (
                      <button
                        onClick={onNormalizeScenario}
                        style={{
                          backgroundColor: '#ef4444',
                          color: '#ffffff',
                          border: 'none',
                          borderRadius: '4px',
                          padding: '3px 8px',
                          fontSize: '11px',
                          fontWeight: 700,
                          cursor: 'pointer',
                        }}
                      >
                        Normalize 100%
                      </button>
                    )}
                  </div>
                </td>
                <td style={{ padding: '10px 14px', fontWeight: 800, color: '#15803d', borderTop: '2px solid #cbd5e1' }}>
                  <span style={{ backgroundColor: '#dcfce7', color: '#15803d', padding: '3px 8px', borderRadius: '6px' }}>
                    100.00 mol%
                  </span>
                </td>
                <td style={{ padding: '10px 14px', fontWeight: 700, borderTop: '2px solid #cbd5e1' }}>
                  mol%
                </td>
              </tr>
            </tbody>
          </table>
          </div>

          {/* Sub-Panel: Rekomendasi Injeksi Make-Up MCR */}
          <div style={{
            marginTop: '28px',
            paddingTop: '20px',
            borderTop: '2px solid #e2e8f0',
          }}>
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: '14px',
              flexWrap: 'wrap',
              gap: '10px',
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ fontSize: '16px', fontWeight: 700, color: '#0f172a' }}>
                  Refrigerant Make-Up Schedule (MCR)
                </span>
              </div>

              <div style={{ display: 'flex', gap: '8px', fontSize: '12px', flexWrap: 'wrap' }}>
                <span style={{ backgroundColor: '#f1f5f9', color: '#334155', padding: '4px 10px', borderRadius: '6px', fontWeight: 600, border: '1px solid #cbd5e1' }}>
                  Transition Time: <strong>{makeupTransitionHours} Hours</strong>
                </span>
                <span style={{ backgroundColor: '#f0fdf4', color: '#166534', padding: '4px 10px', borderRadius: '6px', fontWeight: 600, border: '1px solid #bbf7d0' }}>
                  Total Make-Up: <strong>{totalMakeupFlowNm3.toFixed(1)} Nm³/h</strong> ({totalMakeupFlowKg.toFixed(1)} kg/h)
                </span>
                <span style={{ backgroundColor: '#e0f2fe', color: '#0369a1', padding: '4px 10px', borderRadius: '6px', fontWeight: 600, border: '1px solid #bae6fd' }}>
                  Loop Inventory: <strong>{makeupInventoryKg.toLocaleString()} kg</strong>
                </span>
              </div>
            </div>

            {/* Mobile Card Deck for Make-Up Schedule */}
            {mobileMode === 'card' && (
              <div className="mobile-card-deck">
                {makeupItems.map((item, idx) => {
                  const isInject = item.action === 'INJEKSI' || item.action === 'INJECT';
                  const isStop = item.action === 'TAHAN / STOP' || item.action === 'Tutup';
                  const actionLabel = isInject ? 'Inject' : isStop ? 'Close' : 'Standby';
                  const actionBg = isInject ? '#dcfce7' : isStop ? '#fef3c7' : '#f1f5f9';
                  const actionColor = isInject ? '#15803d' : isStop ? '#92400e' : '#475569';
                  const actionBorder = isInject ? '1px solid #86efac' : isStop ? '1px solid #fde68a' : '1px solid #e2e8f0';

                  const compName =
                    item.description.includes('N2') ? 'Nitrogen (N₂)' :
                      item.description.includes('C1') ? 'Methane (C₁)' :
                        item.description.includes('C2H4') ? 'Ethylene (C₂H₄)' :
                          item.description.includes('C2') ? 'Ethane (C₂)' :
                            item.description.includes('C3') ? 'Propane (C₃)' :
                              item.description;

                  const cleanInstruction = isInject
                    ? `Open valve ${item.tag_dcs} to ${item.recommended_flow_nm3_h.toFixed(1)} Nm³/h.`
                    : isStop
                      ? `Close valve ${item.tag_dcs} (concentration exceeds target).`
                      : `Valve on standby (concentration on target).`;

                  const diff = item.target_molpct - item.actual_molpct;
                  const diffSign = diff > 0 ? '+' : '';

                  return (
                    <div key={item.component || idx} className="mobile-param-card">
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                        <div>
                          <div style={{ fontWeight: 700, fontSize: '13.5px', color: '#0f172a' }}>{compName}</div>
                          <div style={{ fontFamily: 'monospace', fontSize: '11px', color: '#0284c7' }}>{item.tag_dcs}</div>
                        </div>
                        <span style={{ backgroundColor: actionBg, color: actionColor, border: actionBorder, padding: '3px 10px', borderRadius: '12px', fontSize: '11px', fontWeight: 800 }}>
                          {actionLabel}
                        </span>
                      </div>
                      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', marginBottom: '8px' }}>
                        <div style={{ backgroundColor: '#f8fafc', padding: '6px 8px', borderRadius: '6px', border: '1px solid #e2e8f0' }}>
                          <div style={{ fontSize: '10px', color: '#64748b', fontWeight: 600 }}>DCS (mol%)</div>
                          <div style={{ fontSize: '13px', fontWeight: 700, color: '#334155' }}>{item.actual_molpct.toFixed(2)}</div>
                        </div>
                        <div style={{ backgroundColor: '#ecfdf5', padding: '6px 8px', borderRadius: '6px', border: '1px solid #a7f3d0' }}>
                          <div style={{ fontSize: '10px', color: '#065f46', fontWeight: 600 }}>AI Target (Δ)</div>
                          <div style={{ fontSize: '13px', fontWeight: 800, color: '#047857' }}>
                            {item.target_molpct.toFixed(2)} <span style={{ fontSize: '10px', color: diff >= 0 ? '#15803d' : '#b45309' }}>({diffSign}{diff.toFixed(2)})</span>
                          </div>
                        </div>
                      </div>
                      <div style={{ fontSize: '11.5px', color: '#1e293b', backgroundColor: '#f1f5f9', padding: '6px 10px', borderRadius: '6px', marginBottom: '6px' }}>
                        <strong>Injection Rate:</strong> {item.recommended_flow_nm3_h.toFixed(1)} Nm³/h ({item.recommended_flow_kg_h.toFixed(1)} kg/h)
                      </div>
                      <div style={{ fontSize: '11px', color: '#475569', fontStyle: 'italic' }}>
                        💡 {cleanInstruction}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}

            {/* Mobile Swipe & Scroll Control Bar */}
            <div className={`mobile-swipe-hint mobile-swipe-control ${mobileMode === 'card' ? 'mobile-hide' : ''}`}>
              <div className="mobile-swipe-info">
                <span>👉 Swipe for Injection Rate & Guidance ↔</span>
              </div>
              <div className="mobile-scroll-btns">
                <button
                  type="button"
                  onClick={() => scrollTable(table2Ref, 'left')}
                  className="scroll-btn"
                  aria-label="Scroll left"
                >
                  ◀ Left
                </button>
                <button
                  type="button"
                  onClick={() => scrollTable(table2Ref, 'right')}
                  className="scroll-btn scroll-btn-primary"
                  aria-label="Scroll right"
                >
                  Right ▶
                </button>
              </div>
            </div>

            <div
              ref={table2Ref}
              className={`table-scroll-container ${mobileMode === 'card' ? 'mobile-hide' : ''}`}
              style={{
                width: '100%',
                maxWidth: '100%',
                minWidth: 0,
                overflowX: 'auto',
                WebkitOverflowScrolling: 'touch',
                borderRadius: '8px',
                border: '1px solid #e2e8f0',
                boxShadow: 'inset 0 1px 2px rgba(0,0,0,0.02)',
              }}
            >
              <table style={{
                width: '100%',
                minWidth: '840px',
                borderCollapse: 'separate',
                borderSpacing: 0,
                fontSize: '14px',
                textAlign: 'left',
              }}>
              <thead>
                <tr style={{ backgroundColor: '#f1f5f9', color: '#475569' }}>
                  <th className="sticky-col-header" style={{ padding: '10px 14px', fontWeight: 700, width: '18%', minWidth: '140px', borderBottom: '2px solid #cbd5e1' }}>
                    Component
                  </th>
                  <th style={{ padding: '10px 14px', fontWeight: 700, width: '10%', minWidth: '85px', borderBottom: '2px solid #cbd5e1' }}>Valve Tag</th>
                  <th style={{ padding: '10px 14px', fontWeight: 700, width: '11%', minWidth: '85px', backgroundColor: '#f8fafc', borderBottom: '2px solid #cbd5e1' }}>DCS (mol%)</th>
                  <th style={{ padding: '10px 14px', fontWeight: 700, width: '11%', minWidth: '85px', backgroundColor: '#ecfdf5', color: '#065f46', borderBottom: '2px solid #a7f3d0' }}>AI Target</th>
                  <th style={{ padding: '10px 14px', fontWeight: 700, width: '10%', minWidth: '80px', borderBottom: '2px solid #cbd5e1' }}>Deviation (Δ)</th>
                  <th style={{ padding: '10px 14px', fontWeight: 700, width: '18%', minWidth: '140px', borderBottom: '2px solid #cbd5e1' }}>Injection Rate</th>
                  <th style={{ padding: '10px 14px', fontWeight: 700, width: '9%', minWidth: '75px', textAlign: 'center', borderBottom: '2px solid #cbd5e1' }}>Action</th>
                  <th style={{ padding: '10px 14px', fontWeight: 700, width: '18%', minWidth: '180px', borderBottom: '2px solid #cbd5e1' }}>Operator Guidance</th>
                </tr>
              </thead>
              <tbody>
                {makeupItems.map((item, idx) => {
                  const isInject = item.action === 'INJEKSI' || item.action === 'INJECT';
                  const isStop = item.action === 'TAHAN / STOP' || item.action === 'Tutup';
                  const actionLabel = isInject ? 'Inject' : isStop ? 'Close' : 'Standby';
                  const actionBg = isInject ? '#dcfce7' : isStop ? '#fef3c7' : '#f1f5f9';
                  const actionColor = isInject ? '#15803d' : isStop ? '#92400e' : '#475569';
                  const actionBorder = isInject ? '1px solid #86efac' : isStop ? '1px solid #fde68a' : '1px solid #e2e8f0';

                  const compName =
                    item.description.includes('N2') ? 'Nitrogen (N₂)' :
                      item.description.includes('C1') ? 'Methane (C₁)' :
                        item.description.includes('C2H4') ? 'Ethylene (C₂H₄)' :
                          item.description.includes('C2') ? 'Ethane (C₂)' :
                            item.description.includes('C3') ? 'Propane (C₃)' :
                              item.description;

                  const cleanInstruction = isInject
                    ? `Open valve ${item.tag_dcs} to ${item.recommended_flow_nm3_h.toFixed(1)} Nm³/h.`
                    : isStop
                      ? `Close valve ${item.tag_dcs} (concentration exceeds target).`
                      : `Valve on standby (concentration on target).`;

                  return (
                    <tr key={item.component || idx} style={{ borderBottom: '1px solid #e2e8f0', backgroundColor: idx % 2 === 0 ? '#ffffff' : '#fbfcfd' }}>
                      <td className="sticky-col-cell" style={{ padding: '10px 14px', fontWeight: 600, color: '#0f172a', borderBottom: '1px solid #e2e8f0' }}>
                        {compName}
                      </td>
                      <td style={{ padding: '10px 14px', fontFamily: 'monospace', color: '#0284c7', fontSize: '13px', borderBottom: '1px solid #e2e8f0' }}>
                        {item.tag_dcs}
                      </td>
                      <td style={{ padding: '10px 14px', backgroundColor: '#f8fafc', color: '#475569', fontWeight: 600, borderBottom: '1px solid #e2e8f0' }}>
                        {item.actual_molpct.toFixed(2)}
                      </td>
                      <td style={{ padding: '10px 14px', backgroundColor: '#ecfdf5', fontWeight: 700, color: '#047857', borderBottom: '1px solid #e2e8f0' }}>
                        {item.target_molpct.toFixed(2)}
                      </td>
                      <td style={{ padding: '10px 14px', fontWeight: 600, color: item.delta_molpct > 0 ? '#15803d' : '#64748b', borderBottom: '1px solid #e2e8f0' }}>
                        {item.delta_molpct > 0 ? `+${item.delta_molpct.toFixed(2)}` : item.delta_molpct.toFixed(2)}
                      </td>
                      <td style={{ padding: '10px 14px', fontFamily: 'monospace', fontWeight: 700, fontSize: '13px', color: isInject ? '#0f172a' : '#94a3b8', borderBottom: '1px solid #e2e8f0' }}>
                        {item.recommended_flow_nm3_h.toFixed(1)} Nm³/h
                        <span style={{ fontSize: '12px', color: '#64748b', marginLeft: '6px', fontWeight: 500 }}>
                          ({item.recommended_flow_kg_h.toFixed(1)} kg/h)
                        </span>
                      </td>
                      <td style={{ padding: '10px 14px', textAlign: 'center', borderBottom: '1px solid #e2e8f0' }}>
                        <span style={{
                          backgroundColor: actionBg,
                          color: actionColor,
                          padding: '3px 10px',
                          borderRadius: '12px',
                          fontSize: '12px',
                          fontWeight: 700,
                          display: 'inline-block',
                          border: actionBorder,
                        }}>
                          {actionLabel}
                        </span>
                      </td>
                      <td style={{ padding: '10px 14px', fontSize: '13px', color: '#334155', borderBottom: '1px solid #e2e8f0' }}>
                        {cleanInstruction}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
            </div>

          </div>
        </div>
      </section>

      {/* =================================================================== */}
      {/* SECTION 2: PENGAWASAN OPERASI & BATAS AMAN                         */}
      {/* =================================================================== */}
      <section style={{
        backgroundColor: 'rgba(255, 255, 255, 0.85)',
        backdropFilter: 'blur(16px)',
        WebkitBackdropFilter: 'blur(16px)',
        borderRadius: '16px',
        border: '1px solid rgba(226, 232, 240, 0.85)',
        boxShadow: '0 4px 20px -2px rgba(15, 23, 42, 0.04), inset 0 1px 0 #ffffff',
        overflow: 'hidden',
      }}>
        <div style={{
          backgroundColor: 'rgba(248, 250, 252, 0.9)',
          backdropFilter: 'blur(10px)',
          color: '#0f172a',
          padding: '14px 20px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          borderBottom: '1px solid rgba(226, 232, 240, 0.9)',
          flexWrap: 'wrap',
          gap: '10px',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span style={{
              width: '24px',
              height: '24px',
              borderRadius: '6px',
              background: 'linear-gradient(135deg, #0284c7 0%, #0369a1 100%)',
              color: '#ffffff',
              fontSize: '12px',
              fontWeight: 800,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 2px 6px rgba(2, 132, 199, 0.3)',
            }}>
              2
            </span>
            <span style={{ fontSize: '15px', fontWeight: 800, color: '#0f172a', letterSpacing: '-0.2px' }}>
              Operational Monitoring & Safety Limits
            </span>
          </div>

          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            backgroundColor: prediction?.safety_check?.all_safe ? '#dcfce7' : '#fee2e2',
            color: prediction?.safety_check?.all_safe ? '#166534' : '#991b1b',
            border: prediction?.safety_check?.all_safe ? '1px solid #bbf7d0' : '1px solid #fecaca',
            padding: '5px 14px',
            borderRadius: '20px',
            fontSize: '12px',
            fontWeight: 700,
          }}>
            <span>{prediction?.safety_check?.all_safe ? '✓ Normal & Safe' : '⚠ Constraint Check'}</span>
          </div>
        </div>

        <div style={{ padding: '16px 20px', minWidth: 0, maxWidth: '100%', boxSizing: 'border-box' }}>
          <div className="safe-boundaries-grid" style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
            gap: '16px',
          }}>
            {/* Panel 1: Kompresor MCR 4K-2 */}
            <div style={{
              backgroundColor: '#f8fafc',
              border: '1px solid #e2e8f0',
              borderRadius: '8px',
              padding: '16px',
            }}>
              <div style={{
                fontSize: '13px',
                fontWeight: 800,
                color: '#0369a1',
                textTransform: 'uppercase',
                letterSpacing: '0.5px',
                marginBottom: '12px',
                borderBottom: '1px solid #cbd5e1',
                paddingBottom: '6px',
              }}>
                1. MCR Compressor (4K-2)
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', fontSize: '13px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px dashed #e2e8f0', paddingBottom: '8px' }}>
                  <span style={{ color: '#475569', fontWeight: 500 }}>Suction Temperature (4TI-4B):</span>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <span style={{ backgroundColor: '#e2e8f0', color: '#475569', padding: '2px 6px', borderRadius: '4px', fontSize: '11px', fontWeight: 600 }}>
                      DCS -44.8°C
                    </span>
                    <span style={{ backgroundColor: '#dcfce7', color: '#15803d', padding: '2px 6px', borderRadius: '4px', fontSize: '12px', fontWeight: 800 }}>
                      AI {optimum?.expected_suction_temp_c ? `${optimum.expected_suction_temp_c.toFixed(1)}°C` : '-41.5°C'}
                    </span>
                    <span style={{ backgroundColor: '#10b981', color: '#ffffff', padding: '2px 6px', borderRadius: '4px', fontSize: '10px', fontWeight: 800 }}>
                      SAFE
                    </span>
                  </div>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px dashed #e2e8f0', paddingBottom: '8px' }}>
                  <span style={{ color: '#475569', fontWeight: 500 }}>Suction Pressure (4PI-13):</span>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <span style={{ backgroundColor: '#e2e8f0', color: '#475569', padding: '2px 6px', borderRadius: '4px', fontSize: '11px', fontWeight: 600 }}>
                      DCS 2.28
                    </span>
                    <span style={{ backgroundColor: '#dcfce7', color: '#15803d', padding: '2px 6px', borderRadius: '4px', fontSize: '12px', fontWeight: 800 }}>
                      AI 2.35 kg/cm²
                    </span>
                  </div>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px dashed #e2e8f0', paddingBottom: '8px' }}>
                  <span style={{ color: '#475569', fontWeight: 500 }}>Discharge Temperature (4TI-16):</span>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <span style={{ backgroundColor: '#e2e8f0', color: '#475569', padding: '2px 6px', borderRadius: '4px', fontSize: '11px', fontWeight: 600 }}>
                      DCS 62.4°C
                    </span>
                    <span style={{ backgroundColor: '#dcfce7', color: '#15803d', padding: '2px 6px', borderRadius: '4px', fontSize: '12px', fontWeight: 800 }}>
                      AI 58.1°C
                    </span>
                  </div>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ color: '#475569', fontWeight: 500 }}>Discharge Pressure (4PI-1):</span>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <span style={{ backgroundColor: '#e2e8f0', color: '#475569', padding: '2px 6px', borderRadius: '4px', fontSize: '11px', fontWeight: 600 }}>
                      DCS 36.90
                    </span>
                    <span style={{ backgroundColor: '#dcfce7', color: '#15803d', padding: '2px 6px', borderRadius: '4px', fontSize: '12px', fontWeight: 800 }}>
                      AI 35.15 kg/cm²
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Panel 2: PDI MCHE 5E-1 */}
            <div style={{
              backgroundColor: '#f8fafc',
              border: '1px solid #e2e8f0',
              borderRadius: '8px',
              padding: '16px',
            }}>
              <div style={{
                fontSize: '13px',
                fontWeight: 800,
                color: '#0369a1',
                textTransform: 'uppercase',
                letterSpacing: '0.5px',
                marginBottom: '12px',
                borderBottom: '1px solid #cbd5e1',
                paddingBottom: '6px',
              }}>
                2. MCHE 5E-1 Differential Pressure (PDI)
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', fontSize: '13px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px dashed #e2e8f0', paddingBottom: '8px' }}>
                  <span style={{ color: '#475569', fontWeight: 500 }}>Cold Bundle (PDI4):</span>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <span style={{ backgroundColor: '#e2e8f0', color: '#475569', padding: '2px 6px', borderRadius: '4px', fontSize: '11px', fontWeight: 600 }}>
                      DCS 0.067
                    </span>
                    <span style={{ backgroundColor: '#dcfce7', color: '#15803d', padding: '2px 6px', borderRadius: '4px', fontSize: '12px', fontWeight: 800 }}>
                      AI 0.062
                    </span>
                    <span style={{ backgroundColor: '#10b981', color: '#ffffff', padding: '2px 6px', borderRadius: '4px', fontSize: '10px', fontWeight: 800 }}>
                      NORMAL
                    </span>
                  </div>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px dashed #e2e8f0', paddingBottom: '8px' }}>
                  <span style={{ color: '#475569', fontWeight: 500 }}>Warm Bundle (PDI3):</span>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <span style={{ backgroundColor: '#e2e8f0', color: '#475569', padding: '2px 6px', borderRadius: '4px', fontSize: '11px', fontWeight: 600 }}>
                      DCS 0.240
                    </span>
                    <span style={{ backgroundColor: '#dcfce7', color: '#15803d', padding: '2px 6px', borderRadius: '4px', fontSize: '12px', fontWeight: 800 }}>
                      AI 0.215
                    </span>
                    <span style={{ backgroundColor: '#10b981', color: '#ffffff', padding: '2px 6px', borderRadius: '4px', fontSize: '10px', fontWeight: 800 }}>
                      NORMAL
                    </span>
                  </div>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px dashed #e2e8f0', paddingBottom: '8px' }}>
                  <span style={{ color: '#475569', fontWeight: 500 }}>Cold Separator Level (LI2):</span>
                  <span style={{ backgroundColor: '#e0f2fe', color: '#0369a1', padding: '3px 8px', borderRadius: '6px', fontSize: '12px', fontWeight: 800 }}>
                    39.0 %
                  </span>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ color: '#475569', fontWeight: 500 }}>Warm Separator Level (LI3):</span>
                  <span style={{ backgroundColor: '#e0f2fe', color: '#0369a1', padding: '3px 8px', borderRadius: '6px', fontSize: '12px', fontWeight: 800 }}>
                    48.5 %
                  </span>
                </div>
              </div>
            </div>

            {/* Panel 3: Outlet LNG & MCHE Cold End */}
            <div style={{
              backgroundColor: '#f8fafc',
              border: '1px solid #e2e8f0',
              borderRadius: '8px',
              padding: '16px',
            }}>
              <div style={{
                fontSize: '13px',
                fontWeight: 800,
                color: '#0369a1',
                textTransform: 'uppercase',
                letterSpacing: '0.5px',
                marginBottom: '12px',
                borderBottom: '1px solid #cbd5e1',
                paddingBottom: '6px',
              }}>
                3. LNG Outlet & Cryogenic Rundown
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', fontSize: '13px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px dashed #e2e8f0', paddingBottom: '8px' }}>
                  <span style={{ color: '#475569', fontWeight: 500 }}>LNG Outlet Temperature (TIC1):</span>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <span style={{ backgroundColor: '#e2e8f0', color: '#475569', padding: '2px 6px', borderRadius: '4px', fontSize: '11px', fontWeight: 600 }}>
                      DCS -151.2°C
                    </span>
                    <span style={{ backgroundColor: '#dcfce7', color: '#15803d', padding: '2px 6px', borderRadius: '4px', fontSize: '12px', fontWeight: 800 }}>
                      Scenario: -152.0°C
                    </span>
                    <span style={{ backgroundColor: '#10b981', color: '#ffffff', padding: '2px 6px', borderRadius: '4px', fontSize: '10px', fontWeight: 800 }}>
                      LIMIT: ≤ -150.0°C
                    </span>
                  </div>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px dashed #e2e8f0', paddingBottom: '8px' }}>
                  <span style={{ color: '#475569', fontWeight: 500 }}>Rundown Temperature (TI29):</span>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <span style={{ backgroundColor: '#e2e8f0', color: '#475569', padding: '2px 6px', borderRadius: '4px', fontSize: '11px', fontWeight: 600 }}>
                      DCS -153.6°C
                    </span>
                    <span style={{ backgroundColor: '#dcfce7', color: '#15803d', padding: '2px 6px', borderRadius: '4px', fontSize: '12px', fontWeight: 800 }}>
                      Scenario: -153.8°C
                    </span>
                  </div>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px dashed #e2e8f0', paddingBottom: '8px' }}>
                  <span style={{ color: '#475569', fontWeight: 500 }}>LNG Rundown Production (H5FI6A):</span>
                  <span style={{ backgroundColor: '#f1f5f9', color: '#0f172a', padding: '3px 8px', borderRadius: '6px', fontSize: '12px', fontWeight: 800 }}>
                    {scenarioLngFlow.toFixed(1)} t/h
                  </span>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ color: '#475569', fontWeight: 500 }}>MCHE Bottom Temperature (TI8):</span>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <span style={{ backgroundColor: '#e2e8f0', color: '#475569', padding: '2px 6px', borderRadius: '4px', fontSize: '11px', fontWeight: 600 }}>
                      DCS -44.8°C
                    </span>
                    <span style={{ backgroundColor: '#dcfce7', color: '#15803d', padding: '2px 6px', borderRadius: '4px', fontSize: '12px', fontWeight: 800 }}>
                      Scenario: -43.5°C
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>


      {/* =================================================================== */}
      {/* SEKSI 3: ESTIMASI PENGHEMATAN ENERGI                                */}
      {/* =================================================================== */}
      <section style={{
        backgroundColor: 'rgba(255, 255, 255, 0.85)',
        backdropFilter: 'blur(16px)',
        WebkitBackdropFilter: 'blur(16px)',
        borderRadius: '16px',
        border: '1px solid rgba(226, 232, 240, 0.85)',
        boxShadow: '0 4px 20px -2px rgba(15, 23, 42, 0.04), inset 0 1px 0 #ffffff',
        overflow: 'hidden',
      }}>
        <div style={{
          backgroundColor: 'rgba(248, 250, 252, 0.9)',
          backdropFilter: 'blur(10px)',
          color: '#0f172a',
          padding: '14px 24px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          borderBottom: '1px solid rgba(226, 232, 240, 0.9)',
          flexWrap: 'wrap',
          gap: '12px',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span style={{
              width: '24px',
              height: '24px',
              borderRadius: '6px',
              background: 'linear-gradient(135deg, #059669 0%, #047857 100%)',
              color: '#ffffff',
              fontSize: '12px',
              fontWeight: 800,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 2px 6px rgba(5, 150, 105, 0.3)',
            }}>
              3
            </span>
            <span style={{ fontSize: '15px', fontWeight: 800, color: '#0f172a', letterSpacing: '-0.2px' }}>
              Energy Conservation & Decarbonization Assessment
            </span>
          </div>
        </div>

        <div style={{ padding: '24px' }}>
          {/* Prominent AI Opportunity Alert Callout if current scenario is not saving */}
          {deltaPower > 0 && (
            <div style={{
              backgroundColor: '#ecfdf5',
              border: '1px solid #86efac',
              borderRadius: '8px',
              padding: '14px 18px',
              marginBottom: '20px',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              gap: '16px',
            }}>
              <div>
                <div style={{ fontSize: '14px', fontWeight: 700, color: '#065f46' }}>
                  AI Target can save {potentialAiPowerSavingMw.toFixed(2)} MW ({potentialAiSecSavingKwh.toFixed(1)} kWh/t SEC)
                </div>
                <div style={{ fontSize: '13px', color: '#047857', marginTop: '4px' }}>
                  Current input ({scenario.mcr_flow_t_h.toFixed(1)} t/h) demands higher shaft power. Target AI MCR flow: {recMcrFlow.toFixed(1)} t/h.
                </div>
              </div>
              <button
                onClick={handleApplyRecommended}
                disabled={loading}
                style={{
                  backgroundColor: '#10b981',
                  color: '#ffffff',
                  border: 'none',
                  borderRadius: '6px',
                  padding: '8px 16px',
                  fontWeight: 700,
                  fontSize: '13px',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  whiteSpace: 'nowrap',
                }}
              >
                Apply AI Target
              </button>
            </div>
          )}

          {/* 4 KPI Cards Grid */}
          {(() => {
            const isSaving = deltaPowerSavingMw > 0;

            const dispSecVal = deltaPowerSavingMw > 0
              ? Math.abs(deltaSecLng).toFixed(1)
              : `+${deltaSecLng.toFixed(1)}`;
            const dispSecBadge = deltaPowerSavingMw > 0
              ? `Save ${Math.abs(deltaSecLngPct).toFixed(1)}%`
              : `+${Math.abs(deltaSecLngPct).toFixed(1)}% above baseline`;

            const dispSteamVal = deltaPowerSavingMw > 0
              ? steamSaved_t_h.toFixed(1)
              : `+${(deltaPower * STEAM_RATE_T_PER_MWH).toFixed(1)}`;
            const dispSteamBadge = isSaving ? 'Load Reduced' : 'Load Increased';

            const dispFgVal = deltaPowerSavingMw > 0
              ? fuelGasSaved_t_h.toFixed(1)
              : `+${(((deltaPower * STEAM_RATE_T_PER_MWH * FUEL_GAS_NM3_PER_T_STEAM * FG_DENSITY_KG_NM3) / 1000)).toFixed(1)}`;
            const dispFgBadge = isSaving
              ? `Save USD ${fuelGasSaved_usd_yr.toFixed(2)} M/Yr`
              : 'Cost Increased';

            const dispPowerVal = deltaPowerSavingMw > 0
              ? deltaPowerSavingMw.toFixed(2)
              : `+${deltaPower.toFixed(2)}`;
            const dispPowerBadge = deltaPowerSavingMw > 0
              ? `Save ${Math.abs(deltaPowerPct).toFixed(1)}%`
              : `+${Math.abs(deltaPowerPct).toFixed(1)}% above baseline`;

            const cardBg = isSaving ? '#f0fdf4' : '#fffbeb';
            const cardBorder = isSaving ? '2px solid #86efac' : '2px solid #fcd34d';
            const cardValColor = isSaving ? '#15803d' : '#b45309';
            const cardUnitColor = isSaving ? '#166534' : '#92400e';
            const badgeBg = isSaving ? '#bbf7d0' : '#fef3c7';
            const badgeColor = isSaving ? '#166534' : '#b45309';

            return (
              <div className="kpi-cards-grid" style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(230px, 1fr))',
                gap: '16px',
              }}>
                {/* KPI Card 1: Penghematan SEC LNG */}
                <div style={{
                  backgroundColor: cardBg,
                  border: cardBorder,
                  borderRadius: '8px',
                  padding: '18px',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                }}>
                  <div>
                    <div style={{ fontSize: '12px', fontWeight: 700, color: cardUnitColor, textTransform: 'uppercase' }}>
                      1. Specific Energy Consumption (SEC)
                    </div>
                    <div style={{ fontSize: '30px', fontWeight: 800, color: cardValColor, margin: '8px 0 6px 0' }}>
                      {dispSecVal}
                      <span style={{ fontSize: '14px', fontWeight: 600, marginLeft: '6px', color: cardUnitColor }}>
                        kWh/t
                      </span>
                    </div>
                    <div>
                      <span style={{
                        backgroundColor: badgeBg,
                        color: badgeColor,
                        padding: '3px 8px',
                        borderRadius: '12px',
                        fontSize: '11px',
                        fontWeight: 800,
                      }}>
                        {dispSecBadge}
                      </span>
                    </div>
                  </div>
                  <div style={{
                    marginTop: '14px',
                    paddingTop: '10px',
                    borderTop: `1px solid ${isSaving ? '#bbf7d0' : '#fde68a'}`,
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    gap: '6px',
                  }}>
                    <span style={{ backgroundColor: '#e2e8f0', color: '#334155', padding: '3px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: 700 }}>
                      DCS: {baselineSecLng.toFixed(1)}
                    </span>
                    <span style={{ backgroundColor: isSaving ? '#dcfce7' : '#fef3c7', color: isSaving ? '#15803d' : '#b45309', padding: '3px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: 800 }}>
                      Scenario: {scenarioSecLng.toFixed(1)} kWh/t
                    </span>
                  </div>
                </div>

                {/* KPI Card 2: Penghematan Steam */}
                <div style={{
                  backgroundColor: cardBg,
                  border: cardBorder,
                  borderRadius: '8px',
                  padding: '18px',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                }}>
                  <div>
                    <div style={{ fontSize: '12px', fontWeight: 700, color: cardUnitColor, textTransform: 'uppercase' }}>
                      2. High-Pressure Steam Savings
                    </div>
                    <div style={{ fontSize: '30px', fontWeight: 800, color: cardValColor, margin: '8px 0 6px 0' }}>
                      {dispSteamVal}
                      <span style={{ fontSize: '14px', fontWeight: 600, marginLeft: '6px', color: cardUnitColor }}>
                        t/h
                      </span>
                    </div>
                    <div>
                      <span style={{
                        backgroundColor: badgeBg,
                        color: badgeColor,
                        padding: '3px 8px',
                        borderRadius: '12px',
                        fontSize: '11px',
                        fontWeight: 800,
                      }}>
                        {dispSteamBadge}
                      </span>
                    </div>
                  </div>
                  <div style={{
                    marginTop: '14px',
                    paddingTop: '10px',
                    borderTop: `1px solid ${isSaving ? '#bbf7d0' : '#fde68a'}`,
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                  }}>
                    <span style={{ backgroundColor: '#e2e8f0', color: '#334155', padding: '3px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: 700 }}>
                      Utility Steam
                    </span>
                    <span style={{ backgroundColor: isSaving ? '#dcfce7' : '#fef3c7', color: isSaving ? '#15803d' : '#b45309', padding: '3px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: 800 }}>
                      {isSaving ? 'More Efficient' : 'Load Increased'}
                    </span>
                  </div>
                </div>

                {/* KPI Card 3: Penghematan Fuel Gas */}
                <div style={{
                  backgroundColor: cardBg,
                  border: cardBorder,
                  borderRadius: '8px',
                  padding: '18px',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                }}>
                  <div>
                    <div style={{ fontSize: '12px', fontWeight: 700, color: cardUnitColor, textTransform: 'uppercase' }}>
                      3. Fuel Gas & Financial Savings
                    </div>
                    <div style={{ fontSize: '30px', fontWeight: 800, color: cardValColor, margin: '8px 0 6px 0' }}>
                      {dispFgVal}
                      <span style={{ fontSize: '14px', fontWeight: 600, marginLeft: '6px', color: cardUnitColor }}>
                        t/h
                      </span>
                    </div>
                    <div>
                      <span style={{
                        backgroundColor: isSaving ? '#fef3c7' : '#fee2e2',
                        color: isSaving ? '#92400e' : '#b91c1c',
                        padding: '3px 8px',
                        borderRadius: '12px',
                        fontSize: '11px',
                        fontWeight: 800,
                      }}>
                        {dispFgBadge}
                      </span>
                    </div>
                  </div>
                  <div style={{
                    marginTop: '14px',
                    paddingTop: '10px',
                    borderTop: `1px solid ${isSaving ? '#bbf7d0' : '#fde68a'}`,
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                  }}>
                    <span style={{ backgroundColor: '#e2e8f0', color: '#334155', padding: '3px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: 700 }}>
                      Turbine Fuel
                    </span>
                    <span style={{ backgroundColor: isSaving ? '#dcfce7' : '#fef3c7', color: isSaving ? '#15803d' : '#b45309', padding: '3px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: 800 }}>
                      {isSaving ? 'Emissions Reduced' : 'Emissions Increased'}
                    </span>
                  </div>
                </div>

                {/* KPI Card 4: Total Penghematan Daya Poros C3MR */}
                <div style={{
                  backgroundColor: cardBg,
                  border: cardBorder,
                  borderRadius: '8px',
                  padding: '18px',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                }}>
                  <div>
                    <div style={{ fontSize: '12px', fontWeight: 700, color: cardUnitColor, textTransform: 'uppercase' }}>
                      4. Total C3MR Shaft Power
                    </div>
                    <div style={{ fontSize: '30px', fontWeight: 800, color: cardValColor, margin: '8px 0 6px 0' }}>
                      {dispPowerVal}
                      <span style={{ fontSize: '14px', fontWeight: 600, marginLeft: '6px', color: cardUnitColor }}>
                        MW
                      </span>
                    </div>
                    <div>
                      <span style={{
                        backgroundColor: badgeBg,
                        color: badgeColor,
                        padding: '3px 8px',
                        borderRadius: '12px',
                        fontSize: '11px',
                        fontWeight: 800,
                      }}>
                        {dispPowerBadge}
                      </span>
                    </div>
                  </div>
                  <div style={{
                    marginTop: '14px',
                    paddingTop: '10px',
                    borderTop: `1px solid ${isSaving ? '#bbf7d0' : '#fde68a'}`,
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    gap: '6px',
                  }}>
                    <span style={{ backgroundColor: '#e2e8f0', color: '#334155', padding: '3px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: 700 }}>
                      DCS: {baselinePower.toFixed(1)} MW
                    </span>
                    <span style={{ backgroundColor: isSaving ? '#dcfce7' : '#fef3c7', color: isSaving ? '#15803d' : '#b45309', padding: '3px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: 800 }}>
                      Scenario: {scenarioPower.toFixed(1)} MW
                    </span>
                  </div>
                </div>
              </div>
            );
          })()}
        </div>
      </section>

      {/* =================================================================== */}
      {/* POPUP MODAL: KOMPOSISI & KONDISI FEED GAS 3C-1 KE MCHE 5E-1         */}
      {/* =================================================================== */}
      {showFeedGasModal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(15, 23, 42, 0.35)',
          backdropFilter: 'blur(16px)',
          WebkitBackdropFilter: 'blur(16px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 9999,
          padding: '20px',
        }}>
          <div style={{
            backgroundColor: 'rgba(255, 255, 255, 0.95)',
            backdropFilter: 'blur(24px) saturate(180%)',
            WebkitBackdropFilter: 'blur(24px) saturate(180%)',
            borderRadius: '20px',
            width: '100%',
            maxWidth: '780px',
            maxHeight: '92vh',
            overflowY: 'auto',
            boxShadow: '0 25px 60px -15px rgba(15, 23, 42, 0.15), 0 0 0 1px rgba(226, 232, 240, 0.8), inset 0 1px 1px #ffffff',
            border: '1px solid rgba(255, 255, 255, 0.95)',
            display: 'flex',
            flexDirection: 'column',
          }}>
            {/* Modal Header */}
            <div style={{
              backgroundColor: 'rgba(248, 250, 252, 0.9)',
              backdropFilter: 'blur(10px)',
              color: '#0f172a',
              padding: '16px 24px',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              borderBottom: '1px solid rgba(226, 232, 240, 0.9)',
            }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{
                    background: 'linear-gradient(135deg, #0284c7 0%, #0369a1 100%)',
                    color: '#ffffff',
                    padding: '2px 8px',
                    borderRadius: '4px',
                    fontSize: '11px',
                    fontWeight: 800,
                  }}>
                    GC 3C-1
                  </span>
                  <span style={{ fontSize: '16px', fontWeight: 800, color: '#0f172a' }}>
                    Feed Gas Composition (3C-1)
                  </span>
                </div>
                <div style={{ fontSize: '12px', color: '#64748b', marginTop: '4px' }}>
                  Gas chromatography telemetry of treated feed entering MCHE 5E-1
                </div>
              </div>
              <button
                type="button"
                onClick={() => setShowFeedGasModal(false)}
                style={{
                  background: 'rgba(241, 245, 249, 0.8)',
                  border: '1px solid rgba(203, 213, 225, 0.8)',
                  color: '#64748b',
                  fontSize: '16px',
                  borderRadius: '8px',
                  width: '32px',
                  height: '32px',
                  cursor: 'pointer',
                  fontWeight: 700,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  lineHeight: 1,
                  transition: 'all 0.15s ease',
                }}
              >
                ✕
              </button>
            </div>

            {/* Modal Body */}
            <div style={{ padding: '20px 24px', display: 'flex', flexDirection: 'column', gap: '18px' }}>
              {/* Presets Row */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
                <span style={{ fontSize: '12px', fontWeight: 700, color: '#475569' }}>
                  Shift Composition Presets:
                </span>
                <button
                  type="button"
                  onClick={() => setLocalFeedGas({ ...DEFAULT_FEED_GAS })}
                  style={{
                    backgroundColor: '#f1f5f9',
                    border: '1px solid #cbd5e1',
                    borderRadius: '6px',
                    padding: '4px 10px',
                    fontSize: '12px',
                    fontWeight: 600,
                    cursor: 'pointer',
                    color: '#0f172a',
                  }}
                >
                  Baseline DCS (94.51% C₁)
                </button>
                <button
                  type="button"
                  onClick={() => setLocalFeedGas({
                    N2: 0.1000,
                    C1: 96.2000,
                    C2: 2.2000,
                    C3: 1.1000,
                    iC4: 0.2000,
                    nC4: 0.2000,
                    iC5: 0.0000,
                    temp_inlet_c: -53.5,
                    press_inlet_kgcm2g: 43.15,
                  })}
                  style={{
                    backgroundColor: '#f1f5f9',
                    border: '1px solid #cbd5e1',
                    borderRadius: '6px',
                    padding: '4px 10px',
                    fontSize: '12px',
                    fontWeight: 600,
                    cursor: 'pointer',
                    color: '#0f172a',
                  }}
                >
                  Gas Lean (96.20% C₁)
                </button>
                <button
                  type="button"
                  onClick={() => setLocalFeedGas({
                    N2: 0.0400,
                    C1: 92.5000,
                    C2: 3.8000,
                    C3: 2.3000,
                    iC4: 0.6500,
                    nC4: 0.7100,
                    iC5: 0.0000,
                    temp_inlet_c: -53.5,
                    press_inlet_kgcm2g: 43.15,
                  })}
                  style={{
                    backgroundColor: '#f1f5f9',
                    border: '1px solid #cbd5e1',
                    borderRadius: '6px',
                    padding: '4px 10px',
                    fontSize: '12px',
                    fontWeight: 600,
                    cursor: 'pointer',
                    color: '#0f172a',
                  }}
                >
                  Gas Rich (92.50% C₁)
                </button>
              </div>

              {/* Composition Table */}
              <div
                className="table-scroll-container"
                style={{
                  width: '100%',
                  overflowX: 'auto',
                  WebkitOverflowScrolling: 'touch',
                  border: '1px solid #e2e8f0',
                  borderRadius: '6px',
                }}
              >
                <table style={{
                  width: '100%',
                  minWidth: '580px',
                  borderCollapse: 'collapse',
                  fontSize: '13px',
                }}>
                <thead>
                  <tr style={{ backgroundColor: '#f8fafc', color: '#475569', borderBottom: '2px solid #cbd5e1' }}>
                    <th style={{ padding: '8px 12px', fontWeight: 700, width: '32%' }}>Feed Gas Component</th>
                    <th style={{ padding: '8px 12px', fontWeight: 700, width: '18%' }}>Online GC Tag</th>
                    <th style={{ padding: '8px 12px', fontWeight: 700, width: '25%' }}>Mole Fraction (mol%)</th>
                    <th style={{ padding: '8px 12px', fontWeight: 700, width: '25%' }}>DCS Median Baseline</th>
                  </tr>
                </thead>
                <tbody>
                  {[
                    { key: 'N2', label: 'Nitrogen (N₂)', tag: 'AI25A', def: 0.0536, step: 0.005 },
                    { key: 'C1', label: 'Methane (CH₄ / C₁)', tag: 'AI25B', def: 94.5096, step: 0.05 },
                    { key: 'C2', label: 'Ethane (C₂H₆ / C₂)', tag: 'AI25C', def: 2.7181, step: 0.05 },
                    { key: 'C3', label: 'Propane (C₃H₈ / C₃)', tag: 'AI25D', def: 1.6738, step: 0.02 },
                    { key: 'iC4', label: 'i-Butane (i-C₄H₁₀)', tag: 'AI25E', def: 0.3913, step: 0.01 },
                    { key: 'nC4', label: 'n-Butane (n-C₄H₁₀)', tag: 'AI25F', def: 0.5426, step: 0.01 },
                    { key: 'iC5', label: 'i-Pentane+ (i-C₅+)', tag: 'AI25G', def: 0.0002, step: 0.0005 },
                  ].map((row, idx) => (
                    <tr key={row.key} style={{ borderBottom: '1px solid #f1f5f9', backgroundColor: idx % 2 === 0 ? '#ffffff' : '#fcfcfc' }}>
                      <td style={{ padding: '8px 12px', fontWeight: 600 }}>{row.label}</td>
                      <td style={{ padding: '8px 12px', fontFamily: 'monospace', color: '#0284c7' }}>{row.tag}</td>
                      <td style={{ padding: '6px 12px' }}>
                        <input
                          type="number"
                          step={row.step}
                          min="0"
                          max="100"
                          value={(localFeedGas as any)[row.key] ?? 0}
                          onChange={(e) => {
                            const val = parseFloat(e.target.value) || 0;
                            setLocalFeedGas((prev) => ({ ...prev, [row.key]: val }));
                          }}
                          style={{
                            width: '100px',
                            padding: '4px 8px',
                            border: '1px solid #cbd5e1',
                            borderRadius: '4px',
                            fontWeight: 700,
                            fontSize: '13px',
                          }}
                        />
                      </td>
                      <td style={{ padding: '8px 12px', color: '#64748b' }}>
                        {row.def.toFixed(4)} mol%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              </div>

              {/* Feed Gas Physical Properties Bar */}
              {(() => {
                const sum = (localFeedGas.N2 ?? 0) + (localFeedGas.C1 ?? 0) + (localFeedGas.C2 ?? 0) +
                  (localFeedGas.C3 ?? 0) + (localFeedGas.iC4 ?? 0) + (localFeedGas.nC4 ?? 0) + (localFeedGas.iC5 ?? 0);
                const isClosed = Math.abs(sum - 100.0) < 0.05;
                const mw = calculateFeedGasMW(localFeedGas);
                const c2Plus = (localFeedGas.C2 ?? 0) + (localFeedGas.C3 ?? 0) + (localFeedGas.iC4 ?? 0) + (localFeedGas.nC4 ?? 0) + (localFeedGas.iC5 ?? 0);

                const handleNormalizeFeed = () => {
                  const factor = sum > 0 ? 100.0 / sum : 1.0;
                  setLocalFeedGas((prev) => ({
                    ...prev,
                    N2: Number(((prev.N2 ?? 0) * factor).toFixed(4)),
                    C2: Number(((prev.C2 ?? 0) * factor).toFixed(4)),
                    C3: Number(((prev.C3 ?? 0) * factor).toFixed(4)),
                    iC4: Number(((prev.iC4 ?? 0) * factor).toFixed(4)),
                    nC4: Number(((prev.nC4 ?? 0) * factor).toFixed(4)),
                    iC5: Number(((prev.iC5 ?? 0) * factor).toFixed(4)),
                    C1: Number((100.0 - (
                      (prev.N2 ?? 0) * factor +
                      (prev.C2 ?? 0) * factor +
                      (prev.C3 ?? 0) * factor +
                      (prev.iC4 ?? 0) * factor +
                      (prev.nC4 ?? 0) * factor +
                      (prev.iC5 ?? 0) * factor
                    )).toFixed(4)),
                  }));
                };

                return (
                  <div style={{
                    backgroundColor: isClosed ? '#f0fdf4' : '#fef2f2',
                    border: `1px solid ${isClosed ? '#86efac' : '#fca5a5'}`,
                    borderRadius: '8px',
                    padding: '12px 16px',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    flexWrap: 'wrap',
                    gap: '12px',
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                      <span style={{ fontSize: '13px', fontWeight: 700, color: isClosed ? '#166534' : '#991b1b' }}>
                        Total Composition: {sum.toFixed(4)} mol%
                      </span>
                      {!isClosed && (
                        <button
                          type="button"
                          onClick={handleNormalizeFeed}
                          style={{
                            backgroundColor: '#ef4444',
                            color: '#ffffff',
                            border: 'none',
                            padding: '3px 8px',
                            borderRadius: '4px',
                            fontSize: '11px',
                            fontWeight: 700,
                            cursor: 'pointer',
                          }}
                        >
                          Normalize 100%
                        </button>
                      )}
                    </div>

                    <div style={{ display: 'flex', gap: '16px', fontSize: '12px', color: '#334155' }}>
                      <span>Molecular Weight (MW): <strong style={{ color: '#0284c7' }}>{mw.toFixed(3)}</strong> g/mol</span>
                      <span>C₂+ Fraction: <strong style={{ color: '#059669' }}>{c2Plus.toFixed(2)}%</strong></span>
                    </div>
                  </div>
                );
              })()}

              {/* Operating Conditions (Temperature & Pressure) */}
              <div style={{
                backgroundColor: '#f8fafc',
                border: '1px solid #e2e8f0',
                borderRadius: '8px',
                padding: '14px 16px',
                display: 'grid',
                gridTemplateColumns: 'repeat(2, 1fr)',
                gap: '16px',
              }}>
                <div>
                  <div style={{ fontSize: '12px', fontWeight: 700, color: '#475569', marginBottom: '4px' }}>
                    MCHE Tube Inlet Temperature (5E-1):
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <input
                      type="number"
                      step="0.1"
                      value={localFeedGas.temp_inlet_c ?? -53.5}
                      onChange={(e) => {
                        const val = parseFloat(e.target.value) || -53.5;
                        setLocalFeedGas((prev) => ({ ...prev, temp_inlet_c: val }));
                      }}
                      style={{
                        width: '100px',
                        padding: '4px 8px',
                        border: '1px solid #cbd5e1',
                        borderRadius: '4px',
                        fontWeight: 700,
                        fontSize: '13px',
                      }}
                    />
                    <span style={{ fontSize: '12px', color: '#64748b' }}>°C (Tag: H5TI0023, Baseline: -53.5°C)</span>
                  </div>
                </div>

                <div>
                  <div style={{ fontSize: '12px', fontWeight: 700, color: '#475569', marginBottom: '4px' }}>
                    MCHE Tube Inlet Pressure (5E-1):
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <input
                      type="number"
                      step="0.1"
                      value={localFeedGas.press_inlet_kgcm2g ?? 43.15}
                      onChange={(e) => {
                        const val = parseFloat(e.target.value) || 43.15;
                        setLocalFeedGas((prev) => ({ ...prev, press_inlet_kgcm2g: val }));
                      }}
                      style={{
                        width: '100px',
                        padding: '4px 8px',
                        border: '1px solid #cbd5e1',
                        borderRadius: '4px',
                        fontWeight: 700,
                        fontSize: '13px',
                      }}
                    />
                    <span style={{ fontSize: '12px', color: '#64748b' }}>kg/cm²G (Tag: H5PI0012, Baseline: 43.15)</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Modal Footer */}
            <div style={{
              backgroundColor: '#f8fafc',
              borderTop: '1px solid #cbd5e1',
              padding: '14px 24px',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
            }}>
              <button
                type="button"
                onClick={() => setLocalFeedGas({ ...DEFAULT_FEED_GAS })}
                style={{
                  backgroundColor: '#ffffff',
                  color: '#475569',
                  border: '1px solid #cbd5e1',
                  borderRadius: '6px',
                  padding: '6px 14px',
                  fontWeight: 600,
                  fontSize: '13px',
                  cursor: 'pointer',
                }}
              >
                Reset to DCS
              </button>

              <div style={{ display: 'flex', gap: '10px' }}>
                <button
                  type="button"
                  onClick={() => setShowFeedGasModal(false)}
                  style={{
                    backgroundColor: '#e2e8f0',
                    color: '#334155',
                    border: 'none',
                    borderRadius: '6px',
                    padding: '6px 14px',
                    fontWeight: 600,
                    fontSize: '13px',
                    cursor: 'pointer',
                  }}
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={() => {
                    onFeedGasCompChange?.(localFeedGas);
                    setShowFeedGasModal(false);
                  }}
                  style={{
                    backgroundColor: '#0284c7',
                    color: '#ffffff',
                    border: 'none',
                    borderRadius: '6px',
                    padding: '6px 18px',
                    fontWeight: 700,
                    fontSize: '13px',
                    cursor: 'pointer',
                    boxShadow: '0 1px 3px rgba(0,0,0,0.2)',
                  }}
                >
                  Save Changes
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

    </div>
  );
};
