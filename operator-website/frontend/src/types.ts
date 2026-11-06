// TypeScript interface definitions for C3MR Operator Decision-Support UI

export interface VariableItem {
  id: string;
  name: string;
  tag: string;
  value: number;
  unit: string;
  editable: boolean;
  category: string;
  description?: string;
  safety_limit?: string;
}

export interface DemoSnapshot {
  source_mode: string;
  disclaimer: string;
  timestamp: string;
  shift_info: string;
  operating_regime: string;
  values: Record<string, VariableItem>;
  baseline_model_output: {
    total_shaft_power_mw: number;
    sec_kwh_per_t: number;
    mcr_shaft_power_mw: string;
    c3_shaft_power_mw: string;
  };
}

export interface ScenarioInput {
  feed_flow_t_h: number;
  lng_flow_t_h?: number;
  mcr_flow_t_h: number;
  comp_N2_molpct: number;
  comp_C1_molpct: number;
  comp_C2_molpct: number;
  comp_C2H4_molpct: number;
  comp_C3_molpct: number;
  transition_hours?: number;
  /* Actual DCS state entered by operator (column "Aktual DCS") */
  actual_feed_flow_t_h?: number;
  actual_lng_flow_t_h?: number;
  actual_mcr_flow_t_h?: number;
  actual_comp_N2_molpct?: number;
  actual_comp_C1_molpct?: number;
  actual_comp_C2_molpct?: number;
  actual_comp_C2H4_molpct?: number;
  actual_comp_C3_molpct?: number;
}

/* Operator-editable actual DCS state */
export interface ActualDcsState {
  feed_flow_t_h: number;
  lng_flow_t_h?: number;
  mcr_flow_t_h: number;
  comp_N2_molpct: number;
  comp_C1_molpct: number;
  comp_C2_molpct: number;
  comp_C2H4_molpct: number;
  comp_C3_molpct: number;
}

export interface OptimizeResponse {
  feed_t_h: number;
  mcr_flow_t_h: number;
  comp_N2_molpct: number;
  comp_C1_molpct: number;
  comp_C2_molpct: number;
  comp_C2H4_molpct: number;
  comp_C3_molpct: number;
  mahalanobis_distance: number;
  expected_suction_temp_c: number;
  suction_tal_ok: boolean;
  antisurge_floor_applied: boolean;
  envelope_shrink_applied: boolean;
  extrapolated: boolean;
  feed_span_t_h: number[];
  source: string;
  solver_converged?: boolean;
  constraint_residuals?: Record<string, number>;
}

export interface PredictionSummary {
  total_shaft_power_mw: number;
  power_mcr_mw: number | null;
  power_c3_mw: number | null;
  delta_power_mw: number | null;
  delta_power_pct: number | null;
  sec_kwh_per_t: number | null;
  specific_shaft_power_feed_kwh_per_t?: number | null;
  sec_lng_kwh_per_t?: number | null;
  sec_lng_status?: string;
  delta_sec_kwh_per_t: number | null;
  co2_abatement_t_day: number | null;
  operating_regime: 'underload' | 'transition' | 'baseload' | string;
  data_label: string;
  battery_limit_note: string;
  capacity_warning?: string | null;
  capacity_exceeded?: boolean;
}

export interface DomainCheck {
  in_domain: boolean;
  mahalanobis_distance: number;
  mahalanobis_limit: number;
  composition_closure_ok: boolean;
  composition_sum_molpct: number;
}

export interface SafetyCheck {
  all_safe: boolean;
  status_label?: string;
  violations: string[];
  warnings: string[];
  unverified_checks?: string[];
}

export interface ConfidenceData {
  mae_mw: number;
  bootstrap_ci_lower_mw: number;
  bootstrap_ci_upper_mw: number;
  regime_r2: number | null;
  regime_warning: string | null;
}

export interface MakeupInjectionItem {
  component: string;
  tag_dcs: string;
  description: string;
  unit: string;
  actual_molpct: number;
  target_molpct: number;
  delta_molpct: number;
  recommended_flow_nm3_h: number;
  recommended_flow_kg_h: number;
  action: string;
  instruction: string;
}

export interface MakeupAdvisory {
  transition_hours: number;
  estimated_inventory_kg: number;
  total_makeup_flow_nm3_h: number;
  total_makeup_flow_kg_h: number;
  items: MakeupInjectionItem[];
  operational_notes: string[];
}

export interface FlashDrumSummary {
  feed_flow_t_h: number;
  lng_liquid_flow_t_h: number;
  efg_gas_flow_t_h: number;
  mass_liquid_yield: number;
  vapor_fraction_mol: number;
  t_flash_c: number;
  t_bubble_c: number;
  p_flash_kgcm2g: number;
  status: string;
}

export interface PredictResponse {
  prediction: PredictionSummary;
  domain_check: DomainCheck;
  safety_check: SafetyCheck;
  confidence: ConfidenceData;
  makeup_advisory: MakeupAdvisory;
  features_computed: Record<string, number>;
  actual_power_mw?: number | null;
  baseline_power_mw?: number | null;
  baseline_sec_lng?: number | null;
  flash_drum_5c1?: FlashDrumSummary | null;
}

export interface HistoricalPoint {
  feed_flow: number;
  power_mw: number;
  regime: string;
}

export interface HistoricalSummary {
  source: string;
  n_points?: number;
  points: HistoricalPoint[];
}

export type UserMode = 'OPERATOR' | 'ENGINEERING';
export type ActiveTabId = 'input-results' | 'process-graphics' | 'operator-guide';

export type ConstraintStatusType = 'PASSED' | 'WARNING' | 'FAILED' | 'NOT_EVALUATED';

export interface EvaluatedConstraint {
  id: string;
  name: string;
  tag?: string;
  threshold: string;
  actual_value: string;
  status: ConstraintStatusType;
  message: string;
  engineering_notes?: string;
}
