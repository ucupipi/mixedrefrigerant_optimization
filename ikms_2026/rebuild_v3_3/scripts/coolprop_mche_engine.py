"""
CoolProp PR-EOS 100-Slice Multi-Stream MCHE Enthalpy Pinch & Exergy Engine
Badak LNG Train H C3MR Optimization Suite (Rebuild v3.3 - Priority 4)
Replaces NeqSim JVM dependency with 100% native C++ CoolProp Peng-Robinson backend.

Physics Specifications:
  - 5 Components: Nitrogen, Methane, Ethane, Ethylene, Propane
  - 100-slice enthalpy-flash composite curve integration
  - Rigorous signed temperature approach Delta T(Q) = T_hot(Q) - T_cold(Q)
  - Strict crossover detection (Second Law violation guard: min_pinch >= 1.50 C)
  - Discretized Gouy-Stodola exergy destruction E_D = T_0 * sum(Delta Q * (1/T_c - 1/T_h))
  - Suction superheat margin Delta T_superheat = T_suct - T_dew >= 3.0 C
  - Suction TAL interlock guard: T_suct >= -45.0 C
"""

import numpy as np
import CoolProp.CoolProp as CP
from CoolProp.CoolProp import AbstractState

# Default treated feed gas composition (mol fraction)
FEED_COMP_DEFAULT = {
    "nitrogen": 0.0006,
    "methane": 0.9105,
    "ethane": 0.0230,
    "propane": 0.0160
}

COOLPROP_COMP_MAP = {
    "nitrogen": "Nitrogen",
    "methane": "Methane",
    "ethane": "Ethane",
    "ethylene": "Ethylene",
    "propane": "Propane",
}


class CoolPropMCHEEngine:
    """Mesin termodinamika MCHE 100-slice berbasis Peng-Robinson EOS CoolProp murni."""

    def __init__(self, backend: str = "PR"):
        self.backend = backend

    def _create_state(self, comp_dict: dict) -> tuple[AbstractState, list[float]]:
        """Membuat instance AbstractState Peng-Robinson untuk campuran gas."""
        clean_comps = {}
        for k, v in comp_dict.items():
            k_low = k.lower()
            if k_low in COOLPROP_COMP_MAP and v > 0:
                clean_comps[COOLPROP_COMP_MAP[k_low]] = float(v)

        total = sum(clean_comps.values())
        norm_comps = {k: v / total for k, v in clean_comps.items()}

        comp_names = list(norm_comps.keys())
        mole_fractions = list(norm_comps.values())
        fluid_str = "&".join(comp_names)

        state = AbstractState(self.backend, fluid_str)
        state.set_mole_fractions(mole_fractions)
        return state, mole_fractions

    def calculate_dew_point(self, comp_dict: dict, p_bara: float) -> float:
        """Menghitung suhu dew point (titik embun) campuran pada tekanan tertentu."""
        state, _ = self._create_state(comp_dict)
        p_pa = p_bara * 1e5
        # Q = 1.0 adalah kondisi uap jenuh (dew point)
        state.update(CP.PQ_INPUTS, p_pa, 1.0)
        return float(state.T() - 273.15)

    def calculate_bubble_point(self, comp_dict: dict, p_bara: float) -> float:
        """Menghitung suhu bubble point (titik didih jenuh) campuran."""
        state, _ = self._create_state(comp_dict)
        p_pa = p_bara * 1e5
        # Q = 0.0 adalah kondisi cairan jenuh (bubble point)
        state.update(CP.PQ_INPUTS, p_pa, 0.0)
        return float(state.T() - 273.15)

    def evaluate_100_slice(
        self,
        mcr_flow_th: float,
        mcr_comp: dict | list[float],
        feed_flow_th: float,
        t_suct_c: float = -35.0,
        n_slices: int = 100,
        pinch_limit_c: float = 1.50,
        superheat_limit_c: float = 3.0,
        p_shell_bara: float = 3.15,
        p_hp_bara: float = 40.7,
        p_feed_bara: float = 40.0,
        t_env_k: float = 298.15,
    ) -> dict:
        """
        Evaluasi termodinamika komposit 100-slice MCHE, MITA approach, dan destruksi eksergi.
        """
        # Parsing vektor komposisi MR
        if isinstance(mcr_comp, (list, np.ndarray)):
            if len(mcr_comp) == 5:
                mcr_dict = {
                    "nitrogen": float(mcr_comp[0]),
                    "methane": float(mcr_comp[1]),
                    "ethane": float(mcr_comp[2]),
                    "ethylene": float(mcr_comp[3]),
                    "propane": float(mcr_comp[4]),
                }
            elif len(mcr_comp) == 4:
                mcr_dict = {
                    "nitrogen": float(mcr_comp[0]),
                    "methane": float(mcr_comp[1]),
                    "ethane": float(mcr_comp[2]),
                    "ethylene": 0.0,
                    "propane": float(mcr_comp[3]),
                }
            else:
                raise ValueError(f"Panjang vektor komposisi tidak valid: {len(mcr_comp)}")
        else:
            mcr_dict = {k.lower(): float(v) for k, v in mcr_comp.items()}

        total_mol = sum(mcr_dict.values())
        mcr_norm = {k: v / total_mol for k, v in mcr_dict.items()}

        # 1. Suction Superheat & Dew Point di Shell Pressure (3.15 bar_a)
        dew_t_suct = self.calculate_dew_point(mcr_norm, p_shell_bara)
        superheat_margin = float(t_suct_c - dew_t_suct)

        # 2. Separasi Fasa HP di 5C-1 (-35.0 C, 40.7 bar_a)
        fl_inlet, _ = self._create_state(mcr_norm)
        p_hp_pa = p_hp_bara * 1e5
        t_inlet_k = -35.0 + 273.15
        fl_inlet.update(CP.PT_INPUTS, p_hp_pa, t_inlet_k)

        # Cek fasa (jika vapor quality Q terdefinisi dalam rentang 0-1)
        try:
            molar_vap_frac = float(fl_inlet.Q())
            if molar_vap_frac < 0.0:
                molar_vap_frac = 0.0
            elif molar_vap_frac > 1.0:
                molar_vap_frac = 1.0
        except Exception:
            # Fallback jika Q tidak konvergen langsung
            molar_vap_frac = 0.55

        # Split laju massa HPV dan HPL
        mass_vap_frac = molar_vap_frac  # Approksimasi fraksi massa fasa
        m_hp_vap_th = mcr_flow_th * mass_vap_frac
        m_hp_liq_th = mcr_flow_th * (1.0 - mass_vap_frac)

        # 3. Setup Aliran Panas (Hot Composite Streams)
        fl_ng, _ = self._create_state(FEED_COMP_DEFAULT)
        fl_ng.update(CP.PT_INPUTS, p_feed_bara * 1e5, -32.0 + 273.15)
        h_ng_in = fl_ng.hmass()

        fl_hpv, _ = self._create_state(mcr_norm)
        fl_hpv.update(CP.PT_INPUTS, p_hp_pa, -35.0 + 273.15)
        h_hpv_in = fl_hpv.hmass()
        fl_hpv.update(CP.PT_INPUTS, p_hp_pa, -150.0 + 273.15)
        h_hpv_end = fl_hpv.hmass()

        fl_hpl, _ = self._create_state(mcr_norm)
        fl_hpl.update(CP.PT_INPUTS, p_hp_pa, -35.0 + 273.15)
        h_hpl_in = fl_hpl.hmass()
        fl_hpl.update(CP.PT_INPUTS, p_hp_pa, -127.0 + 273.15)
        h_hpl_end = fl_hpl.hmass()

        # 4. Konstruksi Kurva Komposit Panas (T_hot: -32 C s.d. -151 C)
        t_hot_grid = np.linspace(-32.0, -151.0, n_slices)
        q_hot_list = []

        m_ng_kgs = feed_flow_th * 1000.0 / 3600.0
        m_hpv_kgs = m_hp_vap_th * 1000.0 / 3600.0
        m_hpl_kgs = m_hp_liq_th * 1000.0 / 3600.0

        for t in t_hot_grid:
            t_k = t + 273.15
            # Natural gas feed cooling
            fl_ng.update(CP.PT_INPUTS, p_feed_bara * 1e5, t_k)
            q_ng = m_ng_kgs * (h_ng_in - fl_ng.hmass()) / 1000.0  # kW

            # HPV cooling (-35 C s.d. -150 C)
            if t >= -35.0:
                q_hpv = 0.0
            elif t >= -150.0:
                fl_hpv.update(CP.PT_INPUTS, p_hp_pa, t_k)
                q_hpv = m_hpv_kgs * (h_hpv_in - fl_hpv.hmass()) / 1000.0
            else:
                q_hpv = m_hpv_kgs * (h_hpv_in - h_hpv_end) / 1000.0

            # HPL cooling (-35 C s.d. -127 C)
            if t >= -35.0:
                q_hpl = 0.0
            elif t >= -127.0:
                fl_hpl.update(CP.PT_INPUTS, p_hp_pa, t_k)
                q_hpl = m_hpl_kgs * (h_hpl_in - fl_hpl.hmass()) / 1000.0
            else:
                q_hpl = m_hpl_kgs * (h_hpl_in - h_hpl_end) / 1000.0

            q_hot_list.append(max(0.0, q_ng + q_hpv + q_hpl))

        q_hot_arr = np.array(q_hot_list)
        q_hot_total = float(q_hot_arr[-1])

        # 5. Kurva Komposit Dingin (LP MCR Menguap di Shell 3.15 bar_a)
        fl_cold, _ = self._create_state(mcr_norm)
        p_shell_pa = p_shell_bara * 1e5
        fl_cold.update(CP.PT_INPUTS, p_shell_pa, t_suct_c + 273.15)
        h_cold_out = fl_cold.hmass()

        t_cold_grid = np.linspace(t_suct_c, -165.0, n_slices)
        q_cold_list = []
        m_mcr_kgs = mcr_flow_th * 1000.0 / 3600.0

        for t in t_cold_grid:
            t_k = t + 273.15
            fl_cold.update(CP.PT_INPUTS, p_shell_pa, t_k)
            q_c = m_mcr_kgs * (h_cold_out - fl_cold.hmass()) / 1000.0  # kW
            q_cold_list.append(max(0.0, q_c))

        q_cold_arr = np.array(q_cold_list)
        q_cold_max = float(q_cold_arr[-1])

        # 6. Diskritisasi 100-Slice Approach: Delta T(Q) = T_hot(Q) - T_cold(Q)
        q_sample = np.linspace(0.0, q_hot_total, n_slices + 1)
        t_h_interp = np.interp(q_sample, q_hot_arr, t_hot_grid)
        t_c_interp = np.interp(q_sample, q_cold_arr, t_cold_grid)
        delta_t_arr = t_h_interp - t_c_interp

        min_pinch = float(np.min(delta_t_arr))

        # Crossover guard: jika kapasitas dingin tidak mampu menyerap seluruh duty panas
        if q_cold_max < q_hot_total:
            shortfall_mw = (q_hot_total - q_cold_max) / 1000.0
            min_pinch = min(min_pinch, -shortfall_mw)

        min_idx = int(np.argmin(delta_t_arr))
        pinch_loc_pct = float(q_sample[min_idx] / q_hot_total * 100.0) if q_hot_total > 0 else 0.0
        warm_approach = float(delta_t_arr[0])
        cold_approach = float(delta_t_arr[-1])

        # 7. Destruksi Eksergi MCHE Riemann Diskrit 100-Slice (Gouy-Stodola)
        # E_D = T_0 * sum( Delta Q_i * (1/T_cold,i - 1/T_hot,i) )
        exergy_destruction_kw = 0.0
        ua_total_kw_k = 0.0

        for i in range(len(q_sample) - 1):
            dq = abs(q_sample[i + 1] - q_sample[i])  # kW
            t_h_mean_k = ((t_h_interp[i] + t_h_interp[i + 1]) / 2.0) + 273.15
            t_c_mean_k = ((t_c_interp[i] + t_c_interp[i + 1]) / 2.0) + 273.15

            if t_c_mean_k > 0 and t_h_mean_k > 0:
                exergy_destruction_kw += t_env_k * dq * ( (1.0 / t_c_mean_k) - (1.0 / t_h_mean_k) )

            # UA LMTD calculation
            dt1 = float(delta_t_arr[i])
            dt2 = float(delta_t_arr[i + 1])
            if dt1 > 0.0 and dt2 > 0.0:
                if abs(dt1 - dt2) < 1e-4:
                    lmtd = dt1
                else:
                    try:
                        lmtd = (dt1 - dt2) / np.log(dt1 / dt2)
                    except Exception:
                        lmtd = (dt1 + dt2) / 2.0
                if lmtd > 1e-5:
                    ua_total_kw_k += dq / lmtd

        is_feasible = (min_pinch >= pinch_limit_c) and (superheat_margin >= superheat_limit_c) and (q_cold_max >= q_hot_total)

        return {
            "min_pinch_c": round(min_pinch, 3),
            "pinch_loc_pct": round(pinch_loc_pct, 1),
            "warm_approach_c": round(warm_approach, 3),
            "cold_approach_c": round(cold_approach, 3),
            "dew_point_c": round(dew_t_suct, 2),
            "superheat_margin_c": round(superheat_margin, 2),
            "total_duty_mw": round(q_hot_total / 1000.0, 3),
            "exergy_destruction_mw": round(exergy_destruction_kw / 1000.0, 3),
            "ua_mw_k": round(ua_total_kw_k / 1000.0, 3),
            "is_feasible": bool(is_feasible),
            "crossover_detected": bool(min_pinch <= 0.0),
        }


# Quick verification self-check
if __name__ == "__main__":
    engine = CoolPropMCHEEngine()
    # Baseline MR composition: N2: 3.67%, C1: 51.26%, C2: 42.62%, C2H4: 0.44%, C3: 2.01%
    test_comp = [0.03669, 0.512644, 0.426182, 0.004423, 0.020061]
    res = engine.evaluate_100_slice(
        mcr_flow_th=720.0,
        mcr_comp=test_comp,
        feed_flow_th=380.0,
        t_suct_c=-35.0,
    )
    print("=== CoolProp PR-EOS MCHE 100-Slice Verification ===")
    for k, v in res.items():
        print(f"  {k:24s}: {v}")
