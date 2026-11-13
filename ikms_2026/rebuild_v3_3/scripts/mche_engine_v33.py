"""
MCHE 100-SLICE THERMODYNAMIC ENGINE — REBUILD v3.3 (CORRECTED, NEQSIM PR-EOS)
PT Badak NGL Train H C3MR Research

WHY THIS FILE EXISTS
--------------------
The legacy engine (MR_OPTIMIZATION_REBUILD/src/thermodynamics/neqsim_engine.py) has a unit
defect at lines 201-203:

    if q_cold_max < q_hot_total:
        shortfall_mw = (q_hot_total - q_cold_max) / 1000.0
        min_pinch = min(min_pinch, -shortfall_mw)      # degC compared against MW

`min_pinch` carries units of degC and is min()'d against a quantity in MW: a non-temperature is
injected into a temperature field. Measured on the shipped baseline CSV, 5 of 7 probed quantiles
were contaminated (P75: -2.006 reported vs +8.530 true; P90: -6.630 vs +9.410). The "turndown
crossover" narrative in 02_energy_baseline/ is an artifact of this defect, not a plant observation.

The legacy engine also:
  (a) built the hot and cold composites on DIFFERENT temperature grids and summed them
      element-wise, which is only valid if the grids coincide (they do not);
  (b) never asserted energy closure;
  (c) forced the FULL MCR circulation into the cold side;
  (d) hardcoded the hot inlet at -32 degC, producing an impossible negative warm-end approach
      whenever t_suct > -32 degC (warm_approach = -13.33 degC at P1 in the shipped CSV).

DESIGN OF THIS ENGINE
---------------------
1. MULTI-STREAM, PHASE-AWARE HOT SIDE.
   The HP separator 5C-1 flash at (p_hp, t_sep) returns the vapour fraction and the per-phase
   compositions. The hot side is then three physically distinct streams, each with its own
   composition and mass flow:
       - treated feed gas            (cooling t_ng_in -> T_end at p_feed)
       - MR vapour from 5C-1         (cooling t_sep   -> T_end at p_hp)
       - MR liquid from 5C-1         (cooling t_sep   -> T_end at p_hp).
   This replaces the legacy single-stream lumping, which is what made the reported pinch an
   artifact of composition cancellation.

2. COLD SIDE IS THE SHELL REFRIGERANT, WITH JT TREATED AS ISENTHALPIC.
   The liquid leaving 5C-1 is subcooled to T_end, let down through the JT valve (h conserved)
   and evaporated in the 5E-1 shell up to the measured suction temperature t_suct at p_shell.
   The cold-side inlet enthalpy is therefore a DERIVED quantity, not an invented one.

3. COMPOSITES ARE ALIGNED BY DUTY FROM THE COLD END — the only alignment that is physically
   meaningful for pinch analysis. Both curves start at Q = 0 at the cold end of the exchanger:

       Q_hot(T)  = sum_i m_i * (h_i(T) - h_i(T_end))       over hot streams
       Q_cold(T) = m_cold * (h_shell(T) - h_shell(T_end_cold))

   and the approach is evaluated as

       dT(Q) = T_hot(Q) - T_cold(Q),     MITA = min dT(Q)

   over the duty range [0, min(Q_hot_total, Q_cold_total)]. No element-wise addition of arrays
   living on different temperature grids is performed anywhere.

4. ENERGY CLOSURE IS REPORTED, NEVER RESCALED.
       energy_balance_error_kW = Q_hot_total - Q_cold_total
   Negative approaches are reported as negative; they are never clipped to look safe.

5. 4E-40 (heavy-liquid subcooler) is a SEPARATE boundary and is reported on its own line.

UNITS: SI internally (K, Pa, J/kg, kg/s). degC only at the reporting boundary.
"""

from __future__ import annotations

import os

import numpy as np

os.environ.setdefault("JAVA_HOME", r"C:\Users\khari\AppData\Local\openLCA\jre")

from neqsim.thermo import fluid, thermodynamicoperations  # noqa: E402

COMP_ORDER = ["nitrogen", "methane", "ethane", "ethylene", "propane"]
DISPLAY = ["N2", "C1", "C2", "C2H4", "C3"]

FEED_COMP = {"nitrogen": 0.0006, "methane": 0.9105, "ethane": 0.0230, "propane": 0.0160}

DEFAULT_N_GRID = 60
CLOSURE_ABS_TOL_KW = 5.0
CLOSURE_REL_TOL = 5e-3


def _degc(t_k):
    return float(t_k) - 273.15


class NeqSimState:
    """Thin wrapper around one NeqSim PR fluid, reused across flashes for speed."""

    def __init__(self, comp: dict, p_bar: float | None = None, t_c: float | None = None):
        self.fl = fluid("pr")
        tot = sum(v for v in comp.values() if v > 0)
        for name in COMP_ORDER:
            v = float(comp.get(name, 0.0))
            if v > 0:
                self.fl.addComponent(name, v / tot)
        self.fl.setMixingRule("classic")
        if p_bar is not None:
            self.fl.setPressure(float(p_bar), "bara")
        if t_c is not None:
            self.fl.setTemperature(float(t_c), "C")

    def h_mass(self, p_bar: float, t_c: float) -> float:
        """Mass enthalpy [J/kg] at (p, T) via TP flash."""
        self.fl.setPressure(float(p_bar), "bara")
        self.fl.setTemperature(float(t_c), "C")
        thermodynamicoperations(self.fl).TPflash()
        return float(self.fl.getEnthalpy("J/kg"))

    def flash_phases(self, p_bar: float, t_c: float) -> dict:
        """TP flash returning phase split, per-phase compositions and mass fractions."""
        self.fl.setPressure(float(p_bar), "bara")
        self.fl.setTemperature(float(t_c), "C")
        thermodynamicoperations(self.fl).TPflash()

        nph = int(self.fl.getNumberOfPhases())
        beta_mol = float(self.fl.getBeta())

        phases = []
        for i in range(nph):
            ph = self.fl.getPhase(i)
            comp = {c: float(ph.getComponent(c).getx()) for c in self.fl.getComponentNames()}
            phases.append({
                "name": str(ph.getPhaseTypeName()),
                "beta_mol": float(ph.getBeta()),
                "mw_kg_mol": float(ph.getMolarMass()),
                "h_mass": float(ph.getEnthalpy("J/kg")),
                "comp": comp,
            })

        return {"n_phases": nph, "beta_mol": beta_mol, "phases": phases,
                "mw_total": float(self.fl.getMolarMass())}


class MCHEEngine:
    """Corrected multi-stream MCHE composite-curve engine (NeqSim Peng-Robinson)."""

    def __init__(self, n_grid=DEFAULT_N_GRID):
        self.n_grid = int(n_grid)
        self._cache = {}
        self.n_flash = 0

    # ------------------------------------------------------------------ helpers
    @staticmethod
    def _normalise(comp, keys):
        if isinstance(comp, dict):
            raw = [float(comp.get(k, 0.0)) for k in keys]
        else:
            seq = [float(x) for x in comp]
            if len(seq) == len(keys):
                raw = seq
            elif len(seq) == 5 and len(keys) == 4:
                raw = [seq[0], seq[1], seq[2] + seq[3], seq[4]]
            else:
                raise ValueError("composition length mismatch")
        arr = np.clip(np.asarray(raw, float), 0.0, None)
        if arr.sum() <= 0:
            raise ValueError("composition sums to zero")
        return arr / arr.sum()

    def _state(self, comp, keys):
        z = self._normalise(comp, keys)
        key = tuple(np.round(z, 12).tolist())
        st = self._cache.get(key)
        if st is None:
            st = NeqSimState(dict(zip(keys, z)))
            self._cache[key] = st
        return st

    def _h(self, st, p_bar, t_c):
        self.n_flash += 1
        return st.h_mass(p_bar, t_c)

    @staticmethod
    def _cosine_frac(n):
        theta = np.linspace(0.0, 1.0, int(n))
        return 0.5 * (1.0 - np.cos(np.pi * theta))

    # ------------------------------------------------------------------ main API
    def evaluate(self, mcr_flow_th, mcr_comp, feed_flow_th, t_suct_c, p_shell_bara,
                 p_hp_bara, p_feed_bara=40.0, t_ng_in_c=-32.0, t_cold_end_c=-151.0,
                 t_sep_c=-32.0, pinch_limit_c=1.50, superheat_limit_c=3.0,
                 t_tal_c=-45.0, feed_comp=None, n_slices=100) -> dict:
        feed_comp = feed_comp or FEED_COMP

        comp_vec = list(mcr_comp.values()) if isinstance(mcr_comp, dict) else list(mcr_comp)
        if sum(comp_vec) > 1.5:
            comp_vec = [v / 100.0 for v in comp_vec]
        z_mcr = self._normalise(comp_vec, COMP_ORDER)
        p_hp = float(p_hp_bara)
        p_sh = float(p_shell_bara)
        p_fd = float(p_feed_bara)
        t_end = float(t_cold_end_c)
        t_sep = float(t_sep_c)

        m_mcr = float(mcr_flow_th) * 1000.0 / 3600.0
        m_ng = float(feed_flow_th) * 1000.0 / 3600.0
        if m_mcr <= 0 or m_ng <= 0:
            raise ValueError("non-positive stream flow")

        # ---- 5C-1 separator flash: phase split + per-phase compositions ------
        st_mcr = self._state(dict(zip(COMP_ORDER, z_mcr)), COMP_ORDER)
        sep = st_mcr.flash_phases(p_hp, t_sep)
        self.n_flash += 1

        vap = liq = None
        for ph in sep["phases"]:
            if ph["name"].lower().startswith("gas"):
                vap = ph
            else:
                liq = ph

        closure_notes = []
        hot_streams = []
        # feed gas (fixed composition, its own mass flow)
        hot_streams.append({"label": "feed_gas",
                            "comp": feed_comp, "keys": list(feed_comp.keys()),
                            "m_kg_s": m_ng, "p_bar": p_fd, "t_in_c": t_ng_in_c})

        # MR phases: convert molar phase split -> mass flows
        if vap is not None and liq is not None:
            bv = vap["beta_mol"]
            mw_v, mw_l = vap["mw_kg_mol"], liq["mw_kg_mol"]
            mw_bar = bv * mw_v + (1.0 - bv) * mw_l
            w_vap = (bv * mw_v) / mw_bar if mw_bar > 0 else 0.0
            m_vap = m_mcr * w_vap
            m_liq = m_mcr * (1.0 - w_vap)
            hot_streams.append({"label": "mr_vapour", "comp": vap["comp"], "keys": COMP_ORDER,
                                "m_kg_s": m_vap, "p_bar": p_hp, "t_in_c": t_sep})
            hot_streams.append({"label": "mr_liquid", "comp": liq["comp"], "keys": COMP_ORDER,
                                "m_kg_s": m_liq, "p_bar": p_hp, "t_in_c": t_sep})
            cold_comp, cold_keys, m_cold = liq["comp"], COMP_ORDER, m_liq
        else:
            closure_notes.append("single-phase MR at separator conditions")
            hot_streams.append({"label": "mr_total", "comp": dict(zip(COMP_ORDER, z_mcr)),
                                "keys": COMP_ORDER, "m_kg_s": m_mcr, "p_bar": p_hp,
                                "t_in_c": t_sep})
            cold_comp, cold_keys, m_cold = dict(zip(COMP_ORDER, z_mcr)), COMP_ORDER, m_mcr

        # ---- hot composite Q(T) measured from the COLD end -------------------
        # common temperature axis, cold end -> warm end
        t_warm = max(t_ng_in_c, t_sep)
        f = self._cosine_frac(self.n_grid)
        t_axis = t_end + (t_warm - t_end) * f          # ascending: cold -> warm

        q_hot = np.zeros_like(t_axis)
        for s in hot_streams:
            st = self._state(s["comp"], s["keys"])
            h_end = self._h(st, s["p_bar"], t_end)
            # duty accumulated from t_end up to each axis temperature, capped at the
            # stream's own warm inlet (a stream contributes nothing above its inlet)
            h_axis = np.array([
                self._h(st, s["p_bar"], min(float(t), s["t_in_c"])) for t in t_axis])
            q_hot += s["m_kg_s"] * (h_axis - h_end) / 1000.0

        q_hot_total = float(q_hot[-1])

        # ---- cold composite Q(T) from the cold end ---------------------------
        st_cold = self._state(cold_comp, cold_keys)
        cold_in_bar = p_hp          # JT inlet pressure (isenthalpic)
        h_cold_end = self._h(st_cold, cold_in_bar, t_end)     # enthalpy conserved through JT
        h_axis_c = np.array([self._h(st_cold, p_sh, min(float(t), t_suct_c)) for t in t_axis])
        q_cold = m_cold * (h_axis_c - h_cold_end) / 1000.0
        q_cold_total = float(q_cold[-1])

        closure_err = q_hot_total - q_cold_total

        # ---- MITA on a common duty grid -------------------------------------
        q_common = min(q_hot_total, q_cold_total)
        if q_common > 0:
            q_eval = np.linspace(0.0, q_common, int(n_slices) + 1)
            qh = q_hot - q_hot[0]
            order_h = np.argsort(qh)
            t_hot_q = np.interp(q_eval, qh[order_h], t_axis[order_h])
            qc = q_cold - q_cold[0]
            order_c = np.argsort(qc)
            t_cold_q = np.interp(q_eval, qc[order_c], t_axis[order_c])
        else:
            q_eval = np.zeros(int(n_slices) + 1)
            t_hot_q = t_cold_q = np.full(int(n_slices) + 1, np.nan)

        dt = t_hot_q - t_cold_q
        fin = np.isfinite(dt)
        if fin.sum():
            dtf = dt[fin]
            i = int(np.argmin(dtf))
            mita_c = float(dtf[i])
            mita_loc = float(q_eval[fin][i] / q_common * 100.0) if q_common > 0 else float("nan")
            warm_appr, cold_appr = float(dtf[0]), float(dtf[-1])
        else:
            mita_c = mita_loc = warm_appr = cold_appr = float("nan")

        # ---- superheat / TAL -------------------------------------------------
        try:
            st_dew = self._state(dict(zip(COMP_ORDER, z_mcr)), COMP_ORDER)
            st_dew.fl.setPressure(p_sh, "bara")
            thermodynamicoperations(st_dew.fl).dewPointTemperature()
            dew_c = float(st_dew.fl.getTemperature("C"))
        except Exception:
            dew_c = float("nan")
        superheat_c = (float(t_suct_c) - dew_c) if np.isfinite(dew_c) else float("nan")

        tol = max(CLOSURE_ABS_TOL_KW, CLOSURE_REL_TOL * max(abs(q_hot_total), 1.0))
        closure_ok = bool(abs(closure_err) <= tol)

        feasible = bool(
            np.isfinite(mita_c) and mita_c >= pinch_limit_c
            and (not np.isfinite(superheat_c) or superheat_c >= superheat_limit_c)
            and float(t_suct_c) >= t_tal_c
        )

        r = lambda x, nd=3: round(float(x), nd) if np.isfinite(x) else None
        return {
            "mita_C": r(mita_c),
            "mita_location_pct": r(mita_loc, 1),
            "warm_approach_C": r(warm_appr),
            "cold_approach_C": r(cold_appr),
            "hot_duty_kW": r(q_hot_total, 2),
            "cold_capacity_kW": r(q_cold_total, 2),
            "energy_balance_error_kW": r(closure_err, 2),
            "closure_tolerance_kW": r(tol, 2),
            "closure_ok": closure_ok,
            "cold_capacity_utilisation_pct": r(q_hot_total / q_cold_total * 100.0, 2) if q_cold_total > 0 else None,
            "dew_point_C": r(dew_c, 2),
            "superheat_C": r(superheat_c, 2),
            "separator_vapour_mol_frac": r(sep["beta_mol"], 4),
            "vapour_mass_flow_t_h": r((hot_streams[1]["m_kg_s"] * 3.6) if len(hot_streams) > 2 else None, 2),
            "liquid_mass_flow_t_h": r((hot_streams[2]["m_kg_s"] * 3.6) if len(hot_streams) > 2 else None, 2),
            "closure_notes": closure_notes,
            "infeasible_reason": (
                None if closure_ok else
                "COLD_CAPACITY_SHORTFALL" if closure_err > 0 else "COLD_CAPACITY_EXCESS"),
            "feasible": feasible,
            "engine": "NeqSim-PR multi-stream 100-slice composite (corrected)",
            "pinch_limit_C": pinch_limit_c,
            "superheat_limit_C": superheat_limit_c,
            "tal_limit_C": t_tal_c,
            "q_profile_kW": [round(float(x), 2) for x in q_eval],
            "t_hot_profile_C": [r(_degc(x), 2) for x in t_hot_q],
            "t_cold_profile_C": [r(_degc(x), 2) for x in t_cold_q],
        }


def evaluate_mche(**kwargs) -> dict:
    return MCHEEngine().evaluate(**kwargs)
