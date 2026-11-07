import { useEffect, useState } from 'react';
import { fetchDemoSnapshot, fetchHistoricalSummary, fetchSystemStatus, optimizeForFeed, predictScenario } from './api';
import { calculateFlashDrum5C1, DEFAULT_FEED_GAS, getEstimatedLngFlow } from './utils/thermoFlash';
import type { FeedGasComposition } from './utils/thermoFlash';
import { TabGrafik } from './components/TabGrafik';
import { TabInputResults } from './components/TabInputResults';
import { TabNavigation } from './components/TabNavigation';
import { TabPanduan } from './components/TabPanduan';
import { TopNavbar } from './components/TopNavbar';
import type {
  ActiveTabId,
  ActualDcsState,
  DemoSnapshot,
  HistoricalPoint,
  OptimizationStrategy,
  OptimizeResponse,
  PredictResponse,
  ScenarioInput,
  UserMode,
} from './types';

/* Normalizes 5 refrigerant components to sum to exactly 100.00% */
const normalizeComposition = <T extends { comp_N2_molpct: number; comp_C1_molpct: number; comp_C2_molpct: number; comp_C2H4_molpct: number; comp_C3_molpct: number }>(c: T): T => {
  const sum = c.comp_N2_molpct + c.comp_C1_molpct + c.comp_C2_molpct + c.comp_C2H4_molpct + c.comp_C3_molpct;
  if (sum <= 0) return c;
  const factor = 100.0 / sum;
  const n2 = Math.round(c.comp_N2_molpct * factor * 100) / 100;
  const c2 = Math.round(c.comp_C2_molpct * factor * 100) / 100;
  const c2h4 = Math.round(c.comp_C2H4_molpct * factor * 100) / 100;
  const c3 = Math.round(c.comp_C3_molpct * factor * 100) / 100;
  const c1 = Math.round((100.0 - (n2 + c2 + c2h4 + c3)) * 100) / 100;
  return {
    ...c,
    comp_N2_molpct: n2,
    comp_C1_molpct: c1,
    comp_C2_molpct: c2,
    comp_C2H4_molpct: c2h4,
    comp_C3_molpct: c3,
  };
};

const DEFAULT_ACTUAL: ActualDcsState = {
  feed_flow_t_h: 245.8,
  lng_flow_t_h: 232.3,
  mcr_flow_t_h: 562.3,
  comp_N2_molpct: 3.39,
  comp_C1_molpct: 44.45,
  comp_C2_molpct: 45.02,
  comp_C2H4_molpct: 0.85,
  comp_C3_molpct: 6.29,
};

const actualFromSnapshot = (snap: DemoSnapshot): ActualDcsState => {
  const raw = {
    comp_N2_molpct: snap.values.comp_N2?.value ?? DEFAULT_ACTUAL.comp_N2_molpct,
    comp_C1_molpct: snap.values.comp_C1?.value ?? DEFAULT_ACTUAL.comp_C1_molpct,
    comp_C2_molpct: snap.values.comp_C2?.value ?? DEFAULT_ACTUAL.comp_C2_molpct,
    comp_C2H4_molpct: snap.values.comp_C2H4?.value ?? DEFAULT_ACTUAL.comp_C2H4_molpct,
    comp_C3_molpct: snap.values.comp_C3?.value ?? DEFAULT_ACTUAL.comp_C3_molpct,
  };
  const norm = normalizeComposition(raw);
  const feed = snap.values.H3FI0004?.value ?? snap.values.H1FI012?.value ?? DEFAULT_ACTUAL.feed_flow_t_h;
  const lng = snap.values.H5FI006A?.value ?? getEstimatedLngFlow(feed);
  return {
    feed_flow_t_h: feed,
    lng_flow_t_h: lng,
    mcr_flow_t_h: snap.values.H4FI001?.value ?? DEFAULT_ACTUAL.mcr_flow_t_h,
    ...norm,
  };
};

const scenarioFromActual = (a: ActualDcsState, hours: number): ScenarioInput => ({ ...a, transition_hours: hours });

const buildRequest = (s: ScenarioInput, a: ActualDcsState): ScenarioInput => ({
  ...s,
  lng_flow_t_h: s.lng_flow_t_h ?? getEstimatedLngFlow(s.feed_flow_t_h),
  actual_feed_flow_t_h: a.feed_flow_t_h,
  actual_lng_flow_t_h: a.lng_flow_t_h ?? getEstimatedLngFlow(a.feed_flow_t_h),
  actual_mcr_flow_t_h: a.mcr_flow_t_h,
  actual_comp_N2_molpct: a.comp_N2_molpct,
  actual_comp_C1_molpct: a.comp_C1_molpct,
  actual_comp_C2_molpct: a.comp_C2_molpct,
  actual_comp_C2H4_molpct: a.comp_C2H4_molpct,
  actual_comp_C3_molpct: a.comp_C3_molpct,
});

const DEFAULT_RECOMMENDED: OptimizeResponse = {
  feed_t_h: 245.8,
  mcr_flow_t_h: 480.0,
  comp_N2_molpct: 3.31,
  comp_C1_molpct: 46.08,
  comp_C2_molpct: 45.15,
  comp_C2H4_molpct: 0.05,
  comp_C3_molpct: 5.41,
  mahalanobis_distance: 0.858,
  expected_suction_temp_c: -38.7,
  suction_tal_ok: true,
  antisurge_floor_applied: true,
  envelope_shrink_applied: false,
  extrapolated: false,
  feed_span_t_h: [141.2, 296.4],
  source: 'Live SLSQP Solver (PR-EOS + GBRT Surrogate)',
  solver_converged: true,
  constraint_residuals: {
    suction_tal_margin_c: 6.31,
    mahalanobis_margin: 2.222,
    antisurge_margin_t_h: 0.0,
    superheat_margin_c: 20.76,
  },
};

const DEFAULT_PREDICTION: PredictResponse = {
  prediction: {
    total_shaft_power_mw: 79.09,
    power_mcr_mw: 48.24,
    power_c3_mw: 30.85,
    delta_power_mw: -5.39,
    delta_power_pct: -6.38,
    sec_kwh_per_t: 340.49,
    specific_shaft_power_feed_kwh_per_t: 321.77,
    sec_lng_kwh_per_t: 340.49,
    sec_lng_status: 'OK',
    delta_sec_kwh_per_t: -23.21,
    co2_abatement_t_day: 52.4,
    operating_regime: 'underload',
    data_label: 'WHAT-IF SCENARIO SIMULATION',
    battery_limit_note: 'Includes MCR compressors 4K-2/3 and Propane precooling compressor 4K-1',
  },
  domain_check: {
    in_domain: true,
    mahalanobis_distance: 0.858,
    mahalanobis_limit: 3.0802,
    composition_closure_ok: true,
    composition_sum_molpct: 100.0,
  },
  safety_check: {
    all_safe: true,
    status_label: 'All verified operational constraints satisfied',
    violations: [],
    warnings: [],
    unverified_checks: ['Centrifugal compressor dynamic anti-surge map (requires complete head/dp curves)'],
  },
  confidence: {
    mae_mw: 0.802,
    bootstrap_ci_lower_mw: 78.29,
    bootstrap_ci_upper_mw: 79.89,
    regime_r2: 0.985,
    regime_warning: null,
  },
  actual_power_mw: 84.48,
  baseline_power_mw: 84.48,
  baseline_sec_lng: 363.7,
  features_computed: {},
  makeup_advisory: {
    status: 'EVALUATED',
    transition_hours: 2.0,
    estimated_inventory_kg: 24000.0,
    total_makeup_flow_nm3_h: 0,
    total_makeup_flow_kg_h: 0,
    items: [],
    operational_notes: [],
  },
};

export function App() {
  const userMode: UserMode = 'OPERATOR';
  const [activeTab, setActiveTab] = useState<ActiveTabId>('input-results');
  const [modelReady, setModelReady] = useState<boolean>(false);
  const [snapshot, setSnapshot] = useState<DemoSnapshot | null>(null);
  const [actualDcs, setActualDcs] = useState<ActualDcsState>(DEFAULT_ACTUAL);
  const [optimum, setOptimum] = useState<OptimizeResponse | null>(DEFAULT_RECOMMENDED);
  const [strategy, setStrategy] = useState<OptimizationStrategy>('CONDITION_DEPENDENT');
  const [scenario, setScenario] = useState<ScenarioInput>({
    ...DEFAULT_ACTUAL,
    mcr_flow_t_h: DEFAULT_RECOMMENDED.mcr_flow_t_h,
    comp_N2_molpct: DEFAULT_RECOMMENDED.comp_N2_molpct,
    comp_C1_molpct: DEFAULT_RECOMMENDED.comp_C1_molpct,
    comp_C2_molpct: DEFAULT_RECOMMENDED.comp_C2_molpct,
    comp_C2H4_molpct: DEFAULT_RECOMMENDED.comp_C2H4_molpct,
    comp_C3_molpct: DEFAULT_RECOMMENDED.comp_C3_molpct,
    transition_hours: 2.0,
  });
  const [prediction, setPrediction] = useState<PredictResponse | null>(DEFAULT_PREDICTION);
  const [feedGasComp, setFeedGasComp] = useState<FeedGasComposition>(DEFAULT_FEED_GAS);
  const [historicalPoints, setHistoricalPoints] = useState<HistoricalPoint[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const autoCalculate = true;

  // Auto-recalculate whenever scenario or actual changes (debounced 250ms)
  useEffect(() => {
    if (!autoCalculate || !snapshot) return;
    const timer = setTimeout(async () => {
      try {
        setLoading(true);
        const res = await predictScenario(buildRequest(scenario, actualDcs));
        setPrediction(res);
        setErrorMsg(null);
      } catch (err: any) {
        if (err?.name !== 'AbortError') {
          console.error('Auto-calculation error:', err);
          setErrorMsg(err.message || 'Prediction calculation failed.');
        }
      } finally {
        setLoading(false);
      }
    }, 250);
    return () => clearTimeout(timer);
  }, [scenario, actualDcs, autoCalculate, Boolean(snapshot)]);

  // Initialize data on mount
  useEffect(() => {
    async function initApp() {
      try {
        setLoading(true);
        const status = await fetchSystemStatus().catch(() => ({ model_loaded: false }));
        setModelReady(Boolean(status?.model_loaded));

        const snap = await fetchDemoSnapshot();
        const act = actualFromSnapshot(snap);
        setActualDcs(act);

        // Fetch AI recommendation for actual feed with proximity trim
        const opt = await optimizeForFeed(act.feed_flow_t_h, act, 0.30, strategy);
        setOptimum(opt);

        // Synchronize scenario input with AI recommendation
        setScenario({
          ...act,
          feed_flow_t_h: act.feed_flow_t_h,
          lng_flow_t_h: act.lng_flow_t_h,
          mcr_flow_t_h: opt.mcr_flow_t_h,
          comp_N2_molpct: opt.comp_N2_molpct,
          comp_C1_molpct: opt.comp_C1_molpct,
          comp_C2_molpct: opt.comp_C2_molpct,
          comp_C2H4_molpct: opt.comp_C2H4_molpct,
          comp_C3_molpct: opt.comp_C3_molpct,
          transition_hours: 2.0,
        });
        setSnapshot(snap);

        const hist = await fetchHistoricalSummary().catch(() => ({ points: [] }));
        setHistoricalPoints(hist.points || []);
      } catch (err: any) {
        console.error('Initialization error:', err);
        setErrorMsg(err.message || 'Failed to connect to backend model.');
      } finally {
        setLoading(false);
      }
    }
    initApp();
  }, []);

  // Auto-optimize AI target recommendation whenever scenario feed flow, actual DCS, or strategy changes
  useEffect(() => {
    if (!scenario.feed_flow_t_h || scenario.feed_flow_t_h <= 0) return;
    const timer = setTimeout(async () => {
      try {
        const opt = await optimizeForFeed(scenario.feed_flow_t_h, actualDcs, 0.30, strategy);
        setOptimum(opt);
      } catch (err: any) {
        if (err?.name !== 'AbortError') {
          console.warn('Auto-optimize for feed failed:', err);
        }
      }
    }, 200);
    return () => clearTimeout(timer);
  }, [scenario.feed_flow_t_h, actualDcs, strategy]);

  const handleScenarioChange = (key: keyof ScenarioInput, value: number) => {
    if (key === 'feed_flow_t_h') {
      const lng = getEstimatedLngFlow(value);
      setScenario((prev) => ({
        ...prev,
        feed_flow_t_h: value,
        lng_flow_t_h: lng,
      }));
    } else {
      setScenario((prev) => ({ ...prev, [key]: value }));
    }
  };

  const handleActualChange = async (key: keyof ActualDcsState, value: number) => {
    setActualDcs((prev) => ({ ...prev, [key]: value }));
    // Feed is a disturbance: target feed follows actual feed
    if (key === 'feed_flow_t_h') {
      const lng = getEstimatedLngFlow(value);
      const updatedActual = { ...actualDcs, [key]: value, lng_flow_t_h: lng };
      setActualDcs(updatedActual);
      try {
        const opt = await optimizeForFeed(value, updatedActual, 0.30, strategy);
        setOptimum(opt);
        setScenario((prev) => ({
          ...prev,
          feed_flow_t_h: value,
          lng_flow_t_h: lng,
          mcr_flow_t_h: opt.mcr_flow_t_h,
          comp_N2_molpct: opt.comp_N2_molpct,
          comp_C1_molpct: opt.comp_C1_molpct,
          comp_C2_molpct: opt.comp_C2_molpct,
          comp_C2H4_molpct: opt.comp_C2H4_molpct,
          comp_C3_molpct: opt.comp_C3_molpct,
        }));
      } catch {
        setScenario((prev) => ({
          ...prev,
          feed_flow_t_h: value,
          lng_flow_t_h: lng,
        }));
      }
    }
  };

  const handleStrategyChange = (newStrategy: OptimizationStrategy) => {
    setStrategy(newStrategy);
  };

  const handleNormalizeScenario = () => {
    setScenario((prev) => normalizeComposition(prev));
  };

  const handleFeedGasCompChange = (newComp: FeedGasComposition) => {
    setFeedGasComp(newComp);
    const newLng = getEstimatedLngFlow(scenario.feed_flow_t_h, -152.5, newComp);
    setScenario((prev) => ({
      ...prev,
      lng_flow_t_h: newLng,
    }));
  };

  const handleOptimize = async () => {
    try {
      setLoading(true);
      setErrorMsg(null);
      const targetFeed = scenario.feed_flow_t_h;
      const opt = await optimizeForFeed(targetFeed, actualDcs, 0.30, strategy);
      setOptimum(opt);
      setScenario((prev) => ({
        ...prev,
        feed_flow_t_h: targetFeed,
        lng_flow_t_h: getEstimatedLngFlow(targetFeed),
        mcr_flow_t_h: opt.mcr_flow_t_h,
        comp_N2_molpct: opt.comp_N2_molpct,
        comp_C1_molpct: opt.comp_C1_molpct,
        comp_C2_molpct: opt.comp_C2_molpct,
        comp_C2H4_molpct: opt.comp_C2H4_molpct,
        comp_C3_molpct: opt.comp_C3_molpct,
      }));
    } catch (err: any) {
      setErrorMsg(err.message || 'Optimization solver failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleCalculate = async () => {
    try {
      setLoading(true);
      setErrorMsg(null);
      setPrediction(await predictScenario(buildRequest(scenario, actualDcs)));
    } catch (err: any) {
      setErrorMsg(err.message || 'Prediction calculation failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = async () => {
    if (!snapshot) return;
    const act = actualFromSnapshot(snapshot);
    setActualDcs(act);
    setFeedGasComp(DEFAULT_FEED_GAS);
    setScenario(scenarioFromActual(act, scenario.transition_hours ?? 2.0));
    try {
      const opt = await optimizeForFeed(act.feed_flow_t_h, act, 0.30, strategy);
      setOptimum(opt);
    } catch {
      setOptimum(null);
    }
  };

  const handleExportCsv = () => {
    if (!snapshot || !prediction) return;
    const actualLng = actualDcs.lng_flow_t_h ?? getEstimatedLngFlow(actualDcs.feed_flow_t_h);
    const scenarioFlash = calculateFlashDrum5C1(scenario.feed_flow_t_h);
    const scenarioLng = prediction.flash_drum_5c1?.lng_liquid_flow_t_h 
      ?? scenario.lng_flow_t_h 
      ?? scenarioFlash.lngLiquidFlowTH;
    const rows: (string | number | undefined | null)[][] = [
      ['Parameter', 'DCS Tag', 'DCS Actual', 'MCR Scenario / Recommendation', 'Unit', 'Variable Category'],
      ['Treated Feed Gas Flow to MCHE 5E-1 (mass)', 'H3FI0004 x 0.760', actualDcs.feed_flow_t_h, scenario.feed_flow_t_h, 't/h', 'INPUT_DISTURBANCE'],
      ['LNG Rundown Production Flow (H5FI6A)', 'H5FI6A', actualLng.toFixed(1), scenarioLng.toFixed(1), 't/h LNG', 'COUPLED_PRODUCT'],
      ['MCR Circulation Flow (mass)', 'H4FI011B x 36.8', actualDcs.mcr_flow_t_h, scenario.mcr_flow_t_h, 't/h', 'DECISION_VARIABLE'],
      ['MCR N2', 'comp_4C-8_N2', actualDcs.comp_N2_molpct, scenario.comp_N2_molpct, 'mol%', 'DECISION_VARIABLE'],
      ['MCR CH4 (C1)', 'comp_4C-8_C1', actualDcs.comp_C1_molpct, scenario.comp_C1_molpct, 'mol%', 'DECISION_VARIABLE'],
      ['MCR C2H6 (C2)', 'comp_4C-8_C2', actualDcs.comp_C2_molpct, scenario.comp_C2_molpct, 'mol%', 'DECISION_VARIABLE'],
      ['MCR C2H4', 'comp_4C-8_C2H4', actualDcs.comp_C2H4_molpct, scenario.comp_C2H4_molpct, 'mol%', 'DECISION_VARIABLE'],
      ['MCR C3H8 (C3)', 'comp_4C-8_C3', actualDcs.comp_C3_molpct, scenario.comp_C3_molpct, 'mol%', 'DECISION_VARIABLE'],
      ['Total C3MR Shaft Power', 'OUTPUT_MODEL', (prediction.baseline_power_mw ?? prediction.actual_power_mw), prediction.prediction.total_shaft_power_mw, 'MW', 'OUTPUT_PREDICTION'],
      ['SEC LNG (Denominator H5FI6A)', 'DERIVED_LNG', prediction.baseline_sec_lng ?? '-', prediction.prediction.sec_lng_kwh_per_t ?? prediction.prediction.sec_kwh_per_t, 'kWh/t LNG', 'OUTPUT_PREDICTION'],
      ['Mahalanobis Distance', 'ENVELOPE', '-', prediction.domain_check.mahalanobis_distance, 'dimensionless', prediction.domain_check.in_domain ? 'IN_DOMAIN' : 'OUT_OF_DOMAIN'],
      ['Safety Interlock Status', 'INTERLOCK', '-', prediction.safety_check.all_safe ? 'PASSED' : 'VIOLATION', 'status', 'SAFETY_AUDIT'],
    ];

    if (prediction.makeup_advisory?.items) {
      rows.push(['---', '---', '---', '---', '---', '---']);
      rows.push(['MAKE-UP INJECTION RECOMMENDATION', 'DCS TAG', 'ACTUAL', 'RECOMMENDED FLOW', 'UNIT', 'STATUS']);
      for (const item of prediction.makeup_advisory.items) {
        const actStr = item.actual_molpct != null ? `${item.actual_molpct.toFixed(2)} mol%` : 'N/A';
        const flowStr = item.recommended_flow_nm3_h != null
          ? `${item.recommended_flow_nm3_h.toFixed(1)} Nm3/h (${item.recommended_flow_kg_h != null ? item.recommended_flow_kg_h.toFixed(1) : '-'} kg/h)`
          : 'NOT EVALUATED';
        rows.push([
          `Injection ${item.description}`,
          item.tag_dcs,
          actStr,
          flowStr,
          'Nm3/h',
          item.action,
        ]);
      }
    }

    const csvContent = 'data:text/csv;charset=utf-8,' + rows.map((e) => e.join(',')).join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `Badak_C3MR_Scenario_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const hasConstraintViolations = Boolean(
    prediction && (!prediction.safety_check.all_safe || scenario.mcr_flow_t_h < 480)
  );

  // Clean industrial loading splash screen
  if (!snapshot) {
    return (
      <div style={{
        height: '100vh',
        width: '100vw',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: '#f8fafc',
        color: '#0f172a',
        fontFamily: "'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif",
      }}>
        <div style={{
          width: '54px',
          height: '54px',
          border: '4px solid #e2e8f0',
          borderTopColor: '#0284c7',
          borderRadius: '50%',
          animation: 'spin 0.8s linear infinite',
          marginBottom: '20px',
        }} />
        <div style={{ fontSize: '18px', fontWeight: 700, color: '#0f172a' }}>
          MACHINE LEARNING BASED C3MR OPTIMIZATION
        </div>
        <div style={{ fontSize: '14px', color: '#64748b', marginTop: '6px' }}>
          Loading DCS operational data & initializing C3MR surrogate model...
        </div>
      </div>
    );
  }

  return (
    <div style={{
      minHeight: '100vh',
      width: '100%',
      margin: 0,
      padding: 0,
      display: 'flex',
      flexDirection: 'column',
      backgroundColor: '#f8fafc',
      color: '#0f172a',
    }}>
      {/* Top Navbar */}
      <TopNavbar
        loading={loading}
        onExportCsv={handleExportCsv}
        modelReady={modelReady}
      />

      {/* Tab Navigation */}
      <TabNavigation
        activeTab={activeTab}
        onTabChange={setActiveTab}
        hasConstraintViolations={hasConstraintViolations}
      />

      {/* Error / Warning Alert Banner */}
      {errorMsg && (
        <div style={{
          backgroundColor: '#fffbeb',
          borderBottom: '2px solid #f59e0b',
          padding: '10px 24px',
          color: '#92400e',
          fontSize: '14px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          fontFamily: "'Segoe UI', sans-serif",
        }}>
          <span>⚠️ <strong>SYSTEM ALERT:</strong> {errorMsg}</span>
          <button
            onClick={() => setErrorMsg(null)}
            style={{
              background: 'none',
              border: 'none',
              color: '#92400e',
              cursor: 'pointer',
              fontWeight: 700,
              fontSize: '16px',
            }}
          >
            ✕
          </button>
        </div>
      )}

      {/* Main Tab Content Workspace */}
      <main className="app-main-container" style={{ flex: 1, padding: '24px', maxWidth: '1600px', width: '100%', margin: '0 auto' }}>
        {activeTab === 'input-results' && (
          <TabInputResults
            snapshot={snapshot}
            scenario={scenario}
            actualDcs={actualDcs}
            optimum={optimum}
            prediction={prediction}
            userMode={userMode}
            loading={loading}
            strategy={strategy}
            onStrategyChange={handleStrategyChange}
            feedGasComp={feedGasComp}
            onFeedGasCompChange={handleFeedGasCompChange}
            onActualChange={handleActualChange}
            onScenarioChange={handleScenarioChange}
            onCalculate={handleCalculate}
            onOptimize={handleOptimize}
            onNormalizeScenario={handleNormalizeScenario}
            onReset={handleReset}
          />
        )}

        {activeTab === 'process-graphics' && (
          <TabGrafik
            snapshot={snapshot}
            scenario={scenario}
            actualDcs={actualDcs}
            optimum={optimum}
            prediction={prediction}
            historicalPoints={historicalPoints}
            userMode={userMode}
          />
        )}

        {activeTab === 'operator-guide' && (
          <TabPanduan
            userMode={userMode}
          />
        )}
      </main>
    </div>
  );
}

export default App;
