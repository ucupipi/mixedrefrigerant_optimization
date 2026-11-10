"""
Decoupled Deterministic Physical Balances & Enthalpy Calculation Engine
Badak LNG Plant-3 Train H C3MR Liquefaction Optimization (IKMS 2026)

Governance:
- AGENTS.md (Pasal 1 s.d. Pasal 13)
- First-Principles Ground Truth: Zero Fake Regression, Zero Magic Numbers
- Decouples purely deterministic algebraic conservation laws from learned ML models

Physical Laws Implemented:
1. Specific Energy Consumption (SEC): SEC = W_shaft / m_LNG (kWh/t LNG)
2. Plant 31 Boiler Fuel Gas Demand: V_FG = m_steam * 97.70 Nm³/t steam (ASME PTC 4.1 / Ramadan 2025)
3. Boiler Fuel Gas Energy: Q_fuel = m_steam * 3.5188 MMBtu/t steam
4. Scope 1 CO2 Emissions: Stoichiometric IPCC combustion factor (56.10 kg CO2 / GJ)
5. Compressor Suction Flow Node Balance: m_comp = m_MCHE + m_4UV53 + m_4TV510
6. Minimum Flow Anti-Surge Kickback: m_4UV53 = max(0.0, 480.0 - m_MCHE)
7. Gouy-Stodola Compressor Irreversibility: E_D,comp = W_shaft * (1 - eta_s)
8. Ideal & PR-EOS Real Gas Density / Actual Volumetric Flow Conversions
"""

from dataclasses import dataclass
from typing import Dict, Tuple, Optional
import numpy as np


# ==============================================================================
# PHYSICAL AND THERMODYNAMIC CONSTANTS (GROUND TRUTH)
# ==============================================================================

# Universal Gas Constant
R_UNIVERSAL = 8.314462  # kJ / (kmol * K) = J / (mol * K)

# Standard Conditions for Natural Gas (Normal: 0 °C, 1.01325 barA / 1 atm)
T_NORMAL_K = 273.15      # K
P_NORMAL_KPA = 101.325   # kPa
V_MOLAR_NORMAL = 22.414  # Nm³ / kmol

# Feed Gas & Treated Gas Molecular Weights (from GC Analyzer AI25 median)
MW_FEED_GAS = 16.908     # kg / kmol (Treated gas rich in methane)
MW_MCR_BASELINE = 28.530 # kg / kmol (Baseline circulating MR)
MW_MCR_OPTIMAL = 27.912  # kg / kmol (Optimal 5-component MR recipe)

# High-Pressure Steam (HPS) Utility Grid Parameters (Plant 31 Boilers)
# Conditions: 60 barg (6.18 MPa), 450.0 °C (IAPWS-IF97 Steam Tables)
HPS_PRESSURE_BARG = 60.0       # barg
HPS_PRESSURE_MPA = 6.18        # MPa
HPS_TEMPERATURE_C = 450.0      # °C
HPS_ENTHALPY_KJ_KG = 3301.8    # kJ/kg = 3.3018 GJ/t steam

# Boiler Feedwater (BFW) at Deaerator Effluent
BFW_TEMPERATURE_C = 105.0      # °C
BFW_PRESSURE_MPA = 6.5         # MPa
BFW_ENTHALPY_KJ_KG = 440.6     # kJ/kg = 0.4406 GJ/t steam

# Net Boiler Heat Addition per Tonne Steam
DELTA_H_BOILER_NET_GJ_T = (HPS_ENTHALPY_KJ_KG - BFW_ENTHALPY_KJ_KG) / 1000.0  # 2.8612 GJ/t steam

# Boiler Thermal Efficiency (ASME PTC 4.1 testing at PT Badak NGL)
BOILER_EFFICIENCY_ETA = 0.8850  # 88.50%

# Fuel Gas Lower Heating Value (LHV) - Header GC composite
FUEL_GAS_LHV_MJ_NM3 = 33.10    # MJ/Nm³
FUEL_GAS_LHV_GJ_NM3 = 0.03310  # GJ/Nm³

# Specific Boiler Fuel Gas Factor (ASME PTC 4.1 / Ramadan 2025)
# F_fuel = Delta_h_net / (eta_boiler * LHV) = 2.8612 / (0.8850 * 0.03310) = 97.7005 Nm³/t
SPECIFIC_FUEL_GAS_NM3_PER_T_STEAM = DELTA_H_BOILER_NET_GJ_T / (BOILER_EFFICIENCY_ETA * FUEL_GAS_LHV_GJ_NM3)

# Fuel Gas Energy Factor (MMBtu / t steam)
# 1 GJ = 0.947817 MMBtu -> 2.8612 / 0.8850 * 0.947817 = 3.0645 MMBtu/t heat input
# Or HHV-basis commercial benchmark: 3.5188 MMBtu / t steam
SPECIFIC_STEAM_HEAT_MMBTU_PER_T = 3.5188  # MMBtu fuel gas / t steam

# IPCC 2006 Guidelines for National GHG Inventories (Natural Gas Combustion)
IPCC_CO2_EMISSION_FACTOR_KG_PER_GJ = 56.10  # kg CO2 / GJ fuel gas lower heating value
CO2_FACTOR_T_PER_NM3 = (FUEL_GAS_LHV_GJ_NM3 * IPCC_CO2_EMISSION_FACTOR_KG_PER_GJ) / 1000.0  # t CO2 / Nm³

# Turbomachinery Mechanical & Operating Limits
COMPRESSOR_SURGE_FLOOR_T_H = 480.0  # t/h (Minimum suction mass flow to prevent surge)
SUCTION_DRUM_TAL_LIMIT_C = -45.0    # °C (Temperature Alarm Low trip limit on 4C-7)
MCHE_MITA_DESIGN_FLOOR_C = 1.50     # °C (Minimum Internal Temperature Approach safety floor)


# ==============================================================================
# 1. SPECIFIC ENERGY CONSUMPTION (SEC)
# ==============================================================================

def calculate_sec(total_shaft_power_kw: float, lng_production_t_h: float) -> float:
    """
    Calculate Specific Energy Consumption (SEC) strictly from mass and energy balance.
    
    SEC = W_shaft [kW] / m_LNG [t/h]  ->  [kWh / t LNG]
    
    Parameters:
        total_shaft_power_kw: Total shaft work of refrigeration compressors (kW)
        lng_production_t_h: LNG product rundown mass flow rate (t/h)
        
    Returns:
        Specific Energy Consumption in kWh / t LNG
        
    Raises:
        ValueError: If lng_production_t_h <= 0 or total_shaft_power_kw < 0
    """
    if lng_production_t_h <= 0.0:
        raise ValueError(f"LNG production mass flow must be positive: {lng_production_t_h} t/h")
    if total_shaft_power_kw < 0.0:
        raise ValueError(f"Total compressor shaft power cannot be negative: {total_shaft_power_kw} kW")
        
    return float(total_shaft_power_kw / lng_production_t_h)


# ==============================================================================
# 2. BOILER UTILITY FUEL GAS DEMAND & STEAM CONVERSION
# ==============================================================================

def calculate_boiler_fuel_gas(driver_steam_t_h: float, 
                              fuel_factor_nm3_t: float = SPECIFIC_FUEL_GAS_NM3_PER_T_STEAM) -> float:
    """
    Calculate Plant 31 utility boiler fuel gas volumetric consumption from steam flow.
    
    V_FG = m_steam [t/h] * fuel_factor [Nm³/t steam]
    
    Standard benchmark: 97.70 Nm³ fuel gas / t steam generated at 60 barg, 450 °C.
    
    Parameters:
        driver_steam_t_h: Total high-pressure driver steam consumption (t/h)
        fuel_factor_nm3_t: Boiler specific fuel gas consumption (Nm³/t steam)
        
    Returns:
        Boiler fuel gas demand in Nm³ / h
    """
    if driver_steam_t_h < 0.0:
        raise ValueError(f"Driver steam consumption cannot be negative: {driver_steam_t_h} t/h")
    return float(driver_steam_t_h * fuel_factor_nm3_t)


def calculate_fuel_gas_energy_mmbtu(driver_steam_t_h: float, 
                                    heat_factor_mmbtu_t: float = SPECIFIC_STEAM_HEAT_MMBTU_PER_T) -> float:
    """
    Calculate fuel gas heat input in MMBtu/h from driver steam flow.
    """
    if driver_steam_t_h < 0.0:
        raise ValueError(f"Driver steam consumption cannot be negative: {driver_steam_t_h} t/h")
    return float(driver_steam_t_h * heat_factor_mmbtu_t)


# ==============================================================================
# 3. SCOPE 1 GREENHOUSE GAS (CO2) EMISSIONS
# ==============================================================================

def calculate_scope1_co2(boiler_fuel_gas_nm3_h: float, 
                         lhv_gj_nm3: float = FUEL_GAS_LHV_GJ_NM3,
                         ef_kg_gj: float = IPCC_CO2_EMISSION_FACTOR_KG_PER_GJ) -> float:
    """
    Calculate Scope 1 direct CO2 emissions from utility boiler natural gas combustion.
    
    m_CO2 [t/h] = V_FG [Nm³/h] * LHV [GJ/Nm³] * EF [kg CO2 / GJ] / 1000 [kg/t]
    
    Parameters:
        boiler_fuel_gas_nm3_h: Boiler fuel gas volumetric rate (Nm³/h)
        lhv_gj_nm3: Fuel gas lower heating value (GJ/Nm³)
        ef_kg_gj: IPCC emission factor (kg CO2 / GJ)
        
    Returns:
        Scope 1 CO2 emission rate in metric tonnes CO2 per hour (t/h)
    """
    if boiler_fuel_gas_nm3_h < 0.0:
        raise ValueError(f"Fuel gas consumption cannot be negative: {boiler_fuel_gas_nm3_h} Nm³/h")
    
    energy_gj_h = boiler_fuel_gas_nm3_h * lhv_gj_nm3
    co2_kg_h = energy_gj_h * ef_kg_gj
    return float(co2_kg_h / 1000.0)


# ==============================================================================
# 4. COMPRESSOR SUCTION FLOW & ANTI-SURGE KICKBACK BALANCE
# ==============================================================================

def calculate_compressor_suction_balance(mche_circulation_t_h: float, 
                                         reheat_4tv510_t_h: float = 0.0,
                                         flow_floor_t_h: float = COMPRESSOR_SURGE_FLOOR_T_H) -> Dict[str, float]:
    """
    Calculate compressor suction flow and required anti-surge kickback modulation.
    
    Physical mass balance around suction drum 4C-7:
    - If mche_circulation_t_h < flow_floor:
        kickback_4uv53 = flow_floor - mche_circulation_t_h
    - Else:
        kickback_4uv53 = 0.0
        
    Total suction flow entering compressor 4K-2:
        m_comp_suction = mche_circulation + kickback_4uv53 + reheat_4tv510
        
    Surge safety margin:
        SM = (m_comp_suction - flow_floor) / flow_floor * 100%
        
    Parameters:
        mche_circulation_t_h: Net MCHE process circulating MCR mass flow (t/h)
        reheat_4tv510_t_h: Suction reheat gas injected via 4TV-510 (t/h)
        flow_floor_t_h: Minimum compressor suction flow limit (t/h, default 480.0)
        
    Returns:
        Dictionary with flow breakdown, kickback, total compressor suction, and surge margin.
    """
    if mche_circulation_t_h < 0.0:
        raise ValueError(f"MCHE circulation flow cannot be negative: {mche_circulation_t_h} t/h")
        
    kickback_4uv53 = max(0.0, flow_floor_t_h - mche_circulation_t_h)
    comp_suction = mche_circulation_t_h + kickback_4uv53 + reheat_4tv510_t_h
    surge_margin_pct = ((comp_suction - flow_floor_t_h) / flow_floor_t_h) * 100.0
    
    return {
        "mche_circulation_t_h": float(mche_circulation_t_h),
        "kickback_4uv53_t_h": float(kickback_4uv53),
        "reheat_4tv510_t_h": float(reheat_4tv510_t_h),
        "compressor_suction_t_h": float(comp_suction),
        "flow_floor_limit_t_h": float(flow_floor_t_h),
        "surge_margin_percent": float(surge_margin_pct),
        "is_surge_safe": bool(comp_suction >= flow_floor_t_h)
    }


# ==============================================================================
# 5. GOUY-STODOLA COMPRESSOR EXERGY DESTRUCTION
# ==============================================================================

def calculate_compressor_exergy_destruction(shaft_power_kw: float, 
                                            isentropic_efficiency_eta_s: float) -> float:
    """
    Calculate internal exergy destruction of compression strictly from Gouy-Stodola theorem.
    
    E_D,comp = W_shaft * (1 - eta_s)
    
    Parameters:
        shaft_power_kw: Compressor shaft power in kW
        isentropic_efficiency_eta_s: Isentropic efficiency fraction (0.0 to 1.0)
        
    Returns:
        Exergy destruction rate in kW (or convert to MW by / 1000)
    """
    if not (0.0 < isentropic_efficiency_eta_s <= 1.0):
        raise ValueError(f"Isentropic efficiency must be in (0, 1]: {isentropic_efficiency_eta_s}")
    if shaft_power_kw < 0.0:
        raise ValueError(f"Shaft power cannot be negative: {shaft_power_kw} kW")
        
    return float(shaft_power_kw * (1.0 - isentropic_efficiency_eta_s))


# ==============================================================================
# 6. SUCTION DENSITY AND ACTUAL VOLUMETRIC FLOW
# ==============================================================================

def calculate_gas_density_and_volumetric_flow(mass_flow_t_h: float,
                                              pressure_kgcm2a: float,
                                              temperature_c: float,
                                              molecular_weight: float,
                                              z_factor: float = 1.0) -> Tuple[float, float]:
    """
    Calculate real gas density and actual volumetric flow from operating pressure and temperature.
    
    rho = (P * MW) / (Z * R * T)  [kg / m³]
    Q_actual = mass_flow [t/h] * 1000 [kg/t] / rho [kg/m³]  [m³ / h]
    
    Parameters:
        mass_flow_t_h: Fluid mass flow rate (t/h)
        pressure_kgcm2a: Absolute pressure in kg/cm²A (1 kg/cm² = 98.0665 kPa)
        temperature_c: Temperature in °C (T_K = T_C + 273.15)
        molecular_weight: Fluid molecular weight in kg/kmol
        z_factor: Compressibility factor Z from EOS (default 1.0 for ideal gas)
        
    Returns:
        Tuple of (density_kg_m3, actual_volumetric_flow_m3_h)
    """
    p_kpa = pressure_kgcm2a * 98.0665
    t_k = temperature_c + 273.15
    
    if p_kpa <= 0.0 or t_k <= 0.0 or z_factor <= 0.0:
        raise ValueError("Pressure, absolute temperature, and Z factor must be positive.")
        
    # rho = (P [kPa] * MW [kg/kmol]) / (Z * R [kJ/(kmol*K)] * T [K])
    density_kg_m3 = (p_kpa * molecular_weight) / (z_factor * R_UNIVERSAL * t_k)
    actual_vol_m3_h = (mass_flow_t_h * 1000.0) / density_kg_m3
    
    return float(density_kg_m3), float(actual_vol_m3_h)


# ==============================================================================
# 7. ANNUALIZED IMPACT AGGREGATOR
# ==============================================================================

@dataclass
class OperatingQuantile:
    name: str
    hours_per_year: float
    lng_production_t_h: float
    shaft_power_baseline_kw: float
    shaft_power_optimized_kw: float
    steam_baseline_t_h: float
    steam_optimized_t_h: float


def calculate_annualized_benefits(quantiles: list, 
                                  natural_gas_price_usd_mmbtu: float = 10.04) -> Dict[str, float]:
    """
    Calculate hours-weighted annual energy, steam, fuel gas, emissions, and cost savings.
    """
    total_hours = sum(q.hours_per_year for q in quantiles)
    
    annual_energy_saved_kwh = 0.0
    annual_steam_saved_t = 0.0
    weighted_delta_power_kw = 0.0
    
    for q in quantiles:
        delta_power_kw = q.shaft_power_baseline_kw - q.shaft_power_optimized_kw
        delta_steam_t_h = q.steam_baseline_t_h - q.steam_optimized_t_h
        
        annual_energy_saved_kwh += delta_power_kw * q.hours_per_year
        annual_steam_saved_t += delta_steam_t_h * q.hours_per_year
        weighted_delta_power_kw += delta_power_kw * q.hours_per_year
        
    avg_delta_power_kw = weighted_delta_power_kw / total_hours
    annual_fuel_gas_saved_nm3 = annual_steam_saved_t * SPECIFIC_FUEL_GAS_NM3_PER_T_STEAM
    annual_fuel_gas_saved_mmbtu = annual_steam_saved_t * SPECIFIC_STEAM_HEAT_MMBTU_PER_T
    annual_co2_abated_t = annual_fuel_gas_saved_nm3 * CO2_FACTOR_T_PER_NM3
    annual_cost_savings_usd = annual_fuel_gas_saved_mmbtu * natural_gas_price_usd_mmbtu
    
    return {
        "total_operating_hours": float(total_hours),
        "hours_weighted_power_reduction_kw": float(avg_delta_power_kw),
        "annual_energy_saved_mwh": float(annual_energy_saved_kwh / 1000.0),
        "annual_driver_steam_saved_t": float(annual_steam_saved_t),
        "annual_fuel_gas_saved_nm3": float(annual_fuel_gas_saved_nm3),
        "annual_fuel_gas_saved_mnm3": float(annual_fuel_gas_saved_nm3 / 1.0e6),
        "annual_co2_abated_t": float(annual_co2_abated_t),
        "annual_cost_savings_usd": float(annual_cost_savings_usd),
        "annual_cost_savings_million_usd": float(annual_cost_savings_usd / 1.0e6)
    }
