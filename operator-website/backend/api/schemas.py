"""Pydantic schemas for the Operator Decision-Support Website API.

Governance: AGENTS.md (Pasal 2, 8, 10, 13), Strict units, zero ambiguous metrics.
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


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
    data_label: str = Field(default="SIMULASI SKENARIO WHAT-IF", description="Label asal data")
    battery_limit_note: str = Field(
        default="Mencakup kompresor MCR 4K-2/3 dan kompresor Propana 4K-1",
        description="Catatan batas sistem dekomposisi daya",
    )
    capacity_warning: Optional[str] = Field(None, description="Peringatan jika beban melebihi kapasitas desain Train H (350 t/h)")
    capacity_exceeded: bool = Field(default=False, description="Apakah beban melebihi batas desain Train H")


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


class MakeupComponentRecommendation(BaseModel):
    """Component-specific make-up flow recommendation with dual mass and volumetric units.

    Governance: AGENTS.md (Pasal 1-13), ORIGINAL_REQUEST.md (§R3, §R4).
    """
    component: str = Field(..., description="Simbol komponen (N2, C1, C2, C3)")
    tag_dcs: str = Field(..., description="Tag DCS resmi pengontrol make-up (H4FIC006, H4FIC005, H4FI00C8, H4FIC007)")
    alternate_tag_dcs: Optional[str] = Field(None, description="Tag alternatif DCS (misal H4FIC009 untuk C1)")
    description: str = Field(..., description="Deskripsi nama komponen")
    unit: str = Field(default="Nm3/h", description="Satuan standar laju alir (Nm3/h)")
    actual_molpct: Optional[float] = Field(None, description="Fraksi mol aktual (%)")
    target_molpct: Optional[float] = Field(None, description="Fraksi mol target skenario (%)")
    delta_molpct: Optional[float] = Field(None, description="Selisih fraksi mol target - aktual (%)")
    needed_kmol: Optional[float] = Field(None, description="Kebutuhan mol injeksi (kmol)")
    needed_kg: Optional[float] = Field(None, description="Kebutuhan massa injeksi (kg)")
    recommended_flow_nm3_h: Optional[float] = Field(None, description="Rekomendasi laju alir volumetrik normal (Nm3/h)")
    recommended_flow_kg_h: Optional[float] = Field(None, description="Rekomendasi laju alir massa (kg/h)")
    recommended_flow_t_h: Optional[float] = Field(None, description="Rekomendasi laju alir massa (t/h)")
    recommended_flow_scfd: Optional[float] = Field(None, description="Rekomendasi laju alir gas standar (scfd)")
    action: str = Field(..., description="Aksi operasional: INJEKSI, TAHAN / STOP, STABIL / SEIMBANG, TIDAK DAPAT DIEVALUASI")
    instruction: str = Field(..., description="Instruksi advisory untuk operator")


# Backward-compatible alias for existing tests and components
MakeupInjectionItem = MakeupComponentRecommendation


class MakeupAdvisoryRequest(BaseModel):
    """Request payload for dedicated MCR component make-up advisory endpoint.

    Advisory only: does not write setpoints to DCS, SIS, PLC, or field controllers.
    """
    actual_comp: Optional[Dict[str, float]] = Field(
        default=None,
        description="Komposisi kromatografi gas aktual DCS {'N2': 3.38, 'C1': 44.37, ...} (mol%)",
    )
    target_comp: Optional[Dict[str, float]] = Field(
        default=None,
        description="Komposisi target optimasi/skenario {'N2': 3.50, 'C1': 45.00, ...} (mol%)",
    )
    transition_hours: Optional[float] = Field(
        default=2.0,
        ge=0.5,
        le=24.0,
        description="Estimasi durasi transisi injeksi (jam, default 2.0)",
    )
    inventory_kg: Optional[float] = Field(
        default=24000.0,
        gt=0.0,
        description="Estimasi massa inventory aktif loop MCR (kg, nominal 24,000 kg)",
    )
    use_stream_purity: Optional[bool] = Field(
        default=True,
        description="Apakah memperhitungkan matriks kemurnian header riil kilang",
    )
    c1_tag: Optional[str] = Field(
        default="H4FIC005",
        description="Tag DCS pilihan untuk C1 make-up ('H4FIC005' atau 'H4FIC009')",
    )


class MakeupAdvisoryResponse(BaseModel):
    """Component-resolved make-up inventory balance advisory response.

    Governance: AGENTS.md (Pasal 1-13), ORIGINAL_REQUEST.md (§R3, §R4).
    """
    status: str = Field(
        default="EVALUATED",
        description="Status evaluasi make-up: 'EVALUATED' atau 'NOT EVALUATED'",
    )
    transition_hours: Optional[float] = Field(
        default=2.0,
        description="Durasi transisi injeksi make-up (jam)",
    )
    estimated_inventory_kg: Optional[float] = Field(
        default=24000.0,
        description="Estimasi active loop inventory MCR (kg)",
    )
    initial_moles_kmol: Optional[float] = Field(
        default=None,
        description="Total mol awal dalam loop refrigerasi MCR (kmol)",
    )
    final_moles_kmol: Optional[float] = Field(
        default=None,
        description="Total mol akhir pasca injeksi/dilusi tertutup (kmol)",
    )
    expansion_ratio: Optional[float] = Field(
        default=None,
        description="Rasio ekspansi mol loop n_final / n0 untuk mencegah purging",
    )
    total_makeup_flow_nm3_h: Optional[float] = Field(
        default=None,
        description="Total laju alir make-up seluruh komponen (Nm3/h)",
    )
    total_makeup_flow_kg_h: Optional[float] = Field(
        default=None,
        description="Total laju alir massa make-up seluruh komponen (kg/h)",
    )
    total_makeup_flow_t_h: Optional[float] = Field(
        default=None,
        description="Total laju alir massa make-up seluruh komponen (t/h)",
    )
    total_makeup_flow_scfd: Optional[float] = Field(
        default=None,
        description="Total laju alir gas make-up standar (scfd)",
    )
    recommendations: List[MakeupComponentRecommendation] = Field(
        default_factory=list,
        description="Daftar rekomendasi per komponen MCR",
    )
    items: List[MakeupComponentRecommendation] = Field(
        default_factory=list,
        description="Alias recommendations untuk kompatibilitas frontend dan backward-compatibility",
    )
    explanation: str = Field(
        default="",
        description="Penjelasan teknis operasional status make-up advisory",
    )
    operational_notes: List[str] = Field(
        default_factory=list,
        description="Catatan operasional dan batasan keselamatan",
    )
    calculation_timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Timestamp kalkulasi dalam format ISO 8601 UTC",
    )


# Backward-compatible alias for existing services
MakeupAdvisorySummary = MakeupAdvisoryResponse


class FlashDrumSummary(BaseModel):
    """Thermodynamic state of Flash Drum 5C-1 from PR-EOS flash engine."""
    feed_flow_t_h: float = Field(..., description="Laju umpan gas masuk (t/h)")
    lng_liquid_flow_t_h: float = Field(..., description="Laju alir produksi LNG rundown (t/h)")
    efg_gas_flow_t_h: float = Field(..., description="Laju alir end-flash gas ke fuel gas header (t/h)")
    mass_liquid_yield: float = Field(..., description="Yield massa cair LNG (wt fraction)")
    vapor_fraction_mol: float = Field(..., description="Fraksi uap molar beta (mol/mol)")
    t_flash_c: float = Field(..., description="Suhu kesetimbangan flash drum 5C-1 (°C)")
    t_bubble_c: float = Field(..., description="Suhu bubble point pada tekanan bejana (°C)")
    p_flash_kgcm2g: float = Field(default=0.30, description="Tekanan operasi flash drum 5C-1 (kg/cm2G)")
    status: str = Field(..., description="Status evaluasi termodinamika PR-EOS")


class PredictResponse(BaseModel):
    """Consolidated prediction response for operator dashboard."""
    prediction: PredictionSummary
    domain_check: DomainCheckSummary
    safety_check: SafetyCheckSummary
    confidence: ConfidenceSummary
    makeup_advisory: MakeupAdvisorySummary
    features_computed: Dict[str, float]
    actual_power_mw: Optional[float] = Field(None, description="Prediksi model pada kondisi Aktual DCS (MW)")
    baseline_power_mw: Optional[float] = Field(None, description="Daya poros baseline (komposisi DCS) pada feed skenario (MW)")
    baseline_sec_lng: Optional[float] = Field(None, description="SEC baseline (komposisi DCS) pada feed skenario (kWh/t LNG)")
    flash_drum_5c1: Optional[FlashDrumSummary] = Field(None, description="Detail termodinamika PR-EOS Flash Drum 5C-1")


class OptimizationStrategy(str, Enum):
    """C3MR Mixed Refrigerant optimization strategy options.

    Governance: AGENTS.md (Pasal 1-13), ORIGINAL_REQUEST.md (Requirements R2, R4).
    """
    CONDITION_DEPENDENT = "CONDITION_DEPENDENT"
    FIXED_RECIPE = "FIXED_RECIPE"
    MINIMUM_INTERVENTION = "MINIMUM_INTERVENTION"


class OptimizeRequest(BaseModel):
    """Actual DCS state entered by operator; optimum is searched for this feed rate and strategy.

    Governance: AGENTS.md (Pasal 1-13), ORIGINAL_REQUEST.md (Requirements R2, R4).
    """
    feed_flow_t_h: float = Field(..., ge=50.0, le=1000.0, description="Treated gas aktual (t/h)")
    strategy: Optional[OptimizationStrategy] = Field(
        default=None,
        description="Strategi optimasi C3MR: CONDITION_DEPENDENT, FIXED_RECIPE, MINIMUM_INTERVENTION",
    )
    selected_recipe: Optional[Dict[str, float]] = Field(
        default=None,
        description="Resep acuan tetap untuk strategi FIXED_RECIPE (mol%)",
    )
    actual_mcr_flow_t_h: Optional[float] = Field(default=None, description="Laju alir MCR aktual DCS (t/h)")
    actual_comp_N2_molpct: Optional[float] = Field(default=None, description="Aktual N2 mol% dari GC")
    actual_comp_C1_molpct: Optional[float] = Field(default=None, description="Aktual CH4 mol% dari GC")
    actual_comp_C2_molpct: Optional[float] = Field(default=None, description="Aktual C2H6 mol% dari GC")
    actual_comp_C2H4_molpct: Optional[float] = Field(default=None, description="Aktual C2H4 mol% dari GC")
    actual_comp_C3_molpct: Optional[float] = Field(default=None, description="Aktual C3H8 mol% dari GC")
    alpha_trim: Optional[float] = Field(default=0.30, ge=0.05, le=1.0, description="Faktor langkah transisi mendekati komposisi aktual")
    intervention_weight: Optional[float] = Field(default=None, ge=0.0, description="Penalty weight for MINIMUM_INTERVENTION trade-off")
    fixed_recipe_preset: Optional[str] = Field(default="CERTIFIED_INVARIANT_MASTER", description="Recipe preset name for FIXED_RECIPE")

    @field_validator("strategy", mode="before")
    @classmethod
    def parse_strategy(cls, v: Any) -> Any:
        if v is None:
            return None
        if isinstance(v, str):
            v_norm = v.strip().upper()
            if v_norm in OptimizationStrategy.__members__:
                return OptimizationStrategy[v_norm]
        return v


class OptimizeResponse(BaseModel):
    """Recommended MCR flow and composition with full constraint residuals, effective inputs, and explanations.

    Governance: AGENTS.md (Pasal 1-13), ORIGINAL_REQUEST.md (Requirements R2, R4).
    """
    feed_t_h: float = Field(..., description="Laju alir umpan gas skenario (t/h)")
    mcr_flow_t_h: float = Field(..., description="Target laju alir sirkulasi MCR optimal (t/h)")
    comp_N2_molpct: float = Field(..., description="Target fraksi mol N2 (%)")
    comp_C1_molpct: float = Field(..., description="Target fraksi mol C1 (%)")
    comp_C2_molpct: float = Field(..., description="Target fraksi mol C2 (%)")
    comp_C2H4_molpct: float = Field(..., description="Target fraksi mol C2H4 (%)")
    comp_C3_molpct: float = Field(..., description="Target fraksi mol C3 (%)")
    mahalanobis_distance: float = Field(..., description="Jarak Mahalanobis pada ruang ILR Simpleks S^5")
    expected_suction_temp_c: float = Field(..., description="Estimasi suhu suction drum 4C-8 (°C)")
    suction_tal_ok: bool = Field(..., description="Apakah suhu suction drum >= -45.0 °C")
    antisurge_floor_applied: bool = Field(..., description="Apakah batas bawah anti-surge 480.0 t/h aktif")
    envelope_shrink_applied: bool = Field(default=False, description="Apakah penyusutan batas amplop diterapkan")
    extrapolated: bool = Field(default=False, description="Apakah titik operasi berada di luar rentang kuantil")
    feed_span_t_h: List[float] = Field(..., description="Rentang batas umpan [min, max] (t/h)")
    source: str = Field(..., description="Sumber kalkulasi / algoritma optimasi")
    solver_converged: bool = Field(default=True, description="Status konvergensi solver")

    # Milestone 1 Extended Fields (Requirements R2 & R4):
    strategy: str = Field(
        default=OptimizationStrategy.CONDITION_DEPENDENT.value,
        description="Strategi optimasi yang dieksekusi (CONDITION_DEPENDENT / FIXED_RECIPE / MINIMUM_INTERVENTION)",
    )
    effective_inputs: Dict[str, Any] = Field(
        default_factory=dict,
        description="Echo input efektif yang diterima dan digunakan dalam kalkulasi optimasi",
    )
    calculation_timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Timestamp kalkulasi dalam format ISO 8601 UTC",
    )
    constraint_residuals: Dict[str, float] = Field(
        default_factory=dict,
        description="Residual kendala operasional (antisurge_margin_t_h, suction_tal_margin_c, superheat_margin_c, mahalanobis_margin)",
    )
    explanation: str = Field(
        default="",
        description="Penjelasan teknis operasional mengapa target berubah atau tetap konstan",
    )

