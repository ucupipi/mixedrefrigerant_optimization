"""Pydantic schemas for the Operator Decision-Support Website API.

Governance: AGENTS.md (Pasal 2, 8, 10, 13), Strict units, zero ambiguous metrics.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    """User scenario inputs for what-if simulation."""
    feed_flow_t_h: float = Field(default=245.8, ge=50.0, le=1000.0, description="Laju alir umpan gas (t/h)")
    lng_flow_t_h: Optional[float] = Field(default=None, description="Laju alir produksi LNG rundown (H5FI6A) [t/h]")
    mcr_flow_t_h: float = Field(default=562.3, ge=200.0, le=900.0, description="Laju alir sirkulasi MCR (t/h)")
    comp_N2_molpct: float = Field(default=3.38, ge=0.0, le=20.0, description="Nitrogen mol%")
    comp_C1_molpct: float = Field(default=44.37, ge=20.0, le=70.0, description="Metana mol%")
    comp_C2_molpct: float = Field(default=44.94, ge=20.0, le=70.0, description="Etana mol%")
    comp_C2H4_molpct: float = Field(default=0.85, ge=0.0, le=50.0, description="Etilena mol%")
    comp_C3_molpct: float = Field(default=6.28, ge=0.0, le=25.0, description="Propana mol%")
    transition_hours: float = Field(default=2.0, ge=0.5, le=12.0, description="Estimasi durasi transisi injeksi (jam)")

    # Optional actual DCS inputs (if provided, make-up injection is computed relative to them)
    actual_feed_flow_t_h: Optional[float] = Field(default=None, description="Laju alir umpan aktual DCS (t/h)")
    actual_lng_flow_t_h: Optional[float] = Field(default=None, description="Laju alir produksi LNG aktual DCS H5FI6A (t/h)")
    actual_mcr_flow_t_h: Optional[float] = Field(default=None, description="Laju alir MCR aktual DCS (t/h)")
    actual_comp_N2_molpct: Optional[float] = Field(default=None, description="Aktual N2 mol% dari GC")
    actual_comp_C1_molpct: Optional[float] = Field(default=None, description="Aktual CH4 mol% dari GC")
    actual_comp_C2_molpct: Optional[float] = Field(default=None, description="Aktual C2H6 mol% dari GC")
    actual_comp_C2H4_molpct: Optional[float] = Field(default=None, description="Aktual C2H4 mol% dari GC")
    actual_comp_C3_molpct: Optional[float] = Field(default=None, description="Aktual C3H8 mol% dari GC")

    # Optional process sensor overrides (defaults applied from baseline if omitted)
    H4TI004B: Optional[float] = Field(default=None, description="Suhu drum suction 4C-8 (°C)")
    p_4k2_suct_kgcm2a: Optional[float] = Field(default=None, description="Tekanan suction 4K-2 (kg/cm2A)")
    p_4k2_disch_kgcm2a: Optional[float] = Field(default=None, description="Tekanan discharge 4K-2 (kg/cm2A)")
    p_4k3_suct_kgcm2a: Optional[float] = Field(default=None, description="Tekanan suction 4K-3 (kg/cm2A)")
    p_4k3_disch_kgcm2a: Optional[float] = Field(default=None, description="Tekanan discharge 4K-3 (kg/cm2A)")
    p_c3_suct_kgcm2a: Optional[float] = Field(default=None, description="Tekanan suction 4K-1 (kg/cm2A)")
    p_c3_disch_kgcm2a: Optional[float] = Field(default=None, description="Tekanan discharge 4K-1 (kg/cm2A)")
    t_mche_warm_mrv_out_c: Optional[float] = Field(default=None, description="Suhu keluar MRV warm bundle (°C)")
    t_mche_shell_mid_c: Optional[float] = Field(default=None, description="Suhu shell tengah MCHE (°C)")
    t_mche_warm_mrv_in_c: Optional[float] = Field(default=None, description="Suhu masuk MRV warm end (°C)")
    t_mche_cold_mrv_out_c: Optional[float] = Field(default=None, description="Suhu keluar MRV cold bundle (°C)")
    t_lng_rundown_c: Optional[float] = Field(default=None, description="Suhu LNG rundown (°C)")
    t_fg_cb_in_c: Optional[float] = Field(default=None, description="Suhu masuk feed gas cold bundle (°C)")
    dp_mche_warm_kgcm2: Optional[float] = Field(default=None, description="Beda tekan warm bundle (kg/cm2)")
    dp_mche_cold_kgcm2: Optional[float] = Field(default=None, description="Beda tekan cold bundle (kg/cm2)")


class PredictionSummary(BaseModel):
    """Predicted power and derived thermodynamic metrics."""
    total_shaft_power_mw: float = Field(..., description="Prediksi daya poros total Train C3MR (MW)")
    power_mcr_mw: Optional[float] = Field(None, description="Dekomposisi daya kompresor MCR 4K-2/3 (MW)")
    power_c3_mw: Optional[float] = Field(None, description="Dekomposisi daya kompresor Propana 4K-1 (MW)")
    delta_power_mw: Optional[float] = Field(None, description="Selisih daya poros vs baseline DCS (MW)")
    delta_power_pct: Optional[float] = Field(None, description="Persentase selisih daya poros vs baseline DCS (%)")
    sec_kwh_per_t: Optional[float] = Field(None, description="SEC LNG (kWh/t LNG) per ton produksi LNG H5FI6A")
    sec_lng_kwh_per_t: Optional[float] = Field(None, description="SEC LNG (kWh/t LNG) berbasis meter fiskal H5FI6A")
    sec_lng_status: str = Field(default="VALID (Meter Fiskal H5FI6A)", description="Status kalkulasi SEC LNG")
    specific_shaft_power_feed_kwh_per_t: Optional[float] = Field(None, description="Daya poros spesifik umpan (kWh/t feed)")
    delta_sec_kwh_per_t: Optional[float] = Field(None, description="Selisih SEC LNG vs baseline DCS (kWh/t LNG)")
    co2_abatement_t_day: Optional[float] = Field(None, description="Estimasi pengurangan emisi CO2 boiler (t CO2/hari)")
    operating_regime: str = Field(..., description="Rezim operasi: underload / transition / baseload")
    data_label: str = Field(default="SKENARIO WHAT-IF", description="Label asal data")
    battery_limit_note: str = Field(
        default="Mencakup kompresor MCR 4K-2/3 dan kompresor Propana 4K-1",
        description="Catatan batas sistem dekomposisi daya",
    )


class DomainCheckSummary(BaseModel):
    """Operating domain and Mahalanobis distance validation."""
    in_domain: bool = Field(..., description="Apakah titik operasi berada dalam domain data pelatihan")
    mahalanobis_distance: float = Field(..., description="Jarak Mahalanobis pada ruang ILR 4-dimensi")
    mahalanobis_limit: float = Field(..., description="Batas kritis Chi-kuadrat 95% (3.0802)")
    composition_closure_ok: bool = Field(..., description="Apakah total komposisi mendekati 100 mol%")
    composition_sum_molpct: float = Field(..., description="Jumlah fraksi mol sebelum normalisasi")


class SafetyCheckSummary(BaseModel):
    """Process safety and mechanical boundary audit results."""
    all_safe: bool = Field(..., description="Apakah semua batasan keselamatan yang dievaluasi terpenuhi")
    status_label: str = Field(
        default="Semua kendala yang diperiksa terpenuhi",
        description="Label status kepatuhan terverifikasi (bebas klaim berlebihan SEMUA AMAN)",
    )
    violations: List[str] = Field(default_factory=list, description="Daftar pelanggaran keselamatan (interlock/trip/alarm)")
    warnings: List[str] = Field(default_factory=list, description="Daftar peringatan batas operasi")
    unverified_checks: List[str] = Field(
        default_factory=lambda: ["Peta anti-surge dinamis kompresor sentrifugal (memerlukan kurva head/dp lengkap)"],
        description="Daftar kendala yang belum dapat dievaluasi",
    )


class ConfidenceSummary(BaseModel):
    """Statistical model uncertainty and test set validation metrics."""
    mae_mw: float = Field(default=0.802, description="Mean Absolute Error pada test set (MW)")
    bootstrap_ci_lower_mw: float = Field(default=0.640, description="Batas bawah CI 95% (MW)")
    bootstrap_ci_upper_mw: float = Field(default=1.023, description="Batas atas CI 95% (MW)")
    regime_r2: Optional[float] = Field(default=None, description="Koefisien determinasi R² pada rezim terkait")
    regime_warning: Optional[str] = Field(default=None, description="Peringatan jika akurasi rezim rendah")


class MakeupInjectionItem(BaseModel):
    """Make-up flow injection advisory for a single component."""
    component: str
    tag_dcs: str
    description: str
    unit: str = "Nm3/h"
    actual_molpct: float
    target_molpct: float
    delta_molpct: float
    recommended_flow_nm3_h: float
    recommended_flow_kg_h: float
    action: str
    instruction: str


class MakeupAdvisorySummary(BaseModel):
    """Consolidated make-up advisory for all components."""
    transition_hours: float = 2.0
    estimated_inventory_kg: float = 24000.0
    total_makeup_flow_nm3_h: float
    total_makeup_flow_kg_h: float
    items: List[MakeupInjectionItem]
    operational_notes: List[str]


class PredictResponse(BaseModel):
    """Consolidated prediction response for operator dashboard."""
    prediction: PredictionSummary
    domain_check: DomainCheckSummary
    safety_check: SafetyCheckSummary
    confidence: ConfidenceSummary
    makeup_advisory: MakeupAdvisorySummary
    features_computed: Dict[str, float]
    actual_power_mw: Optional[float] = Field(None, description="Prediksi model pada kondisi Aktual DCS (MW)")


class OptimizeRequest(BaseModel):
    """Actual DCS state entered by operator; optimum is searched for this feed rate."""
    feed_flow_t_h: float = Field(..., ge=50.0, le=1000.0, description="Treated gas aktual (t/h)")


class OptimizeResponse(BaseModel):
    """Recommended MCR flow and composition (SLSQP optimum, ILR-interpolated)."""
    feed_t_h: float
    mcr_flow_t_h: float
    comp_N2_molpct: float
    comp_C1_molpct: float
    comp_C2_molpct: float
    comp_C2H4_molpct: float
    comp_C3_molpct: float
    mahalanobis_distance: float
    expected_suction_temp_c: float
    suction_tal_ok: bool
    antisurge_floor_applied: bool
    envelope_shrink_applied: bool
    extrapolated: bool
    feed_span_t_h: List[float]
    source: str
    solver_converged: bool = True
    constraint_residuals: Optional[Dict[str, float]] = None

