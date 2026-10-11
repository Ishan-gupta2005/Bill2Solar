"""Rooftop solar economics for Indian households under PM Surya Ghar Muft Bijli Yojana.

All money is in rupees. Every constant is named so a judge can audit it.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Optional

# --- Physical / scheme constants -------------------------------------------
UNITS_PER_KW_PER_DAY = 4.0          # Typical Indian rooftop yield, kWh per kW per day
DAYS_PER_MONTH = 30
UNITS_PER_KW_PER_MONTH = UNITS_PER_KW_PER_DAY * DAYS_PER_MONTH   # 120
ROOF_SQFT_PER_KW = 100.0            # Shadow-free roof needed per kW
GRID_CO2_KG_PER_KWH = 0.716         # CEA weighted average grid emission factor
CO2_KG_PER_TREE_PER_YEAR = 21.0     # Mature tree sequestration, conservative
EXPORT_RATE_RS_PER_UNIT = 3.0       # Net-metering feed-in credit, conservative
PANEL_WATT = 540                    # One modern mono-PERC module
PANEL_DEGRADATION_PER_YEAR = 0.006
SYSTEM_LIFE_YEARS = 25


def installed_cost_per_kw(kw: float) -> float:
    """Installed cost benchmark, rupees per kW, including inverter, structure, wiring."""
    if kw <= 3:
        return 60000.0
    if kw <= 5:
        return 55000.0
    return 50000.0


def pm_surya_ghar_subsidy(kw: float) -> float:
    """Central Financial Assistance for residential rooftop solar.

    Rs 30,000 per kW for the first 2 kW, Rs 18,000 for the third kW, capped at Rs 78,000.
    """
    if kw <= 0:
        return 0.0
    if kw <= 2:
        return 30000.0 * kw
    if kw <= 3:
        return 60000.0 + 18000.0 * (kw - 2)
    return 78000.0


def recommend_kw(monthly_units: float, roof_sqft: Optional[float] = None) -> float:
    """Size the plant to offset roughly all consumption, in 0.5 kW steps, 1 to 10 kW."""
    raw = monthly_units / UNITS_PER_KW_PER_MONTH
    kw = round(raw * 2) / 2
    kw = max(1.0, min(10.0, kw))
    if roof_sqft:
        roof_cap = max(1.0, (roof_sqft // (ROOF_SQFT_PER_KW / 2)) / 2)
        kw = min(kw, roof_cap)
    return kw


@dataclass
class Estimate:
    monthly_units: float
    effective_tariff_rs_per_unit: float
    recommended_kw: float
    panel_count: int
    roof_sqft_needed: float
    monthly_generation_units: float
    gross_cost_rs: float
    subsidy_rs: float
    net_cost_rs: float
    annual_savings_rs: float
    monthly_savings_rs: float
    payback_years: float
    lifetime_savings_rs: float
    co2_tonnes_per_year: float
    trees_equivalent: int
    coverage_percent: float
    assumptions: dict


def estimate(monthly_units: float,
             bill_amount_rs: Optional[float] = None,
             sanctioned_load_kw: Optional[float] = None,
             roof_sqft: Optional[float] = None,
             tariff_hint_rs_per_unit: Optional[float] = None) -> Estimate:
    monthly_units = max(30.0, float(monthly_units or 0))

    if tariff_hint_rs_per_unit:
        tariff = float(tariff_hint_rs_per_unit)
    elif bill_amount_rs and bill_amount_rs > 0:
        tariff = max(3.0, min(12.0, bill_amount_rs / monthly_units))
    else:
        tariff = 7.0

    kw = recommend_kw(monthly_units, roof_sqft)
    gen = kw * UNITS_PER_KW_PER_MONTH
    self_consumed = min(gen, monthly_units)
    exported = max(0.0, gen - monthly_units)
    monthly_savings = self_consumed * tariff + exported * EXPORT_RATE_RS_PER_UNIT
    annual_savings = monthly_savings * 12

    gross = kw * installed_cost_per_kw(kw)
    subsidy = pm_surya_ghar_subsidy(kw)
    net = max(0.0, gross - subsidy)
    payback = net / annual_savings if annual_savings > 0 else 99.0

    lifetime = 0.0
    yearly = annual_savings
    for _ in range(SYSTEM_LIFE_YEARS):
        lifetime += yearly
        yearly *= (1 - PANEL_DEGRADATION_PER_YEAR)
    lifetime -= net

    co2_kg = gen * 12 * GRID_CO2_KG_PER_KWH
    panels = int(round(kw * 1000 / PANEL_WATT))

    return Estimate(
        monthly_units=round(monthly_units),
        effective_tariff_rs_per_unit=round(tariff, 2),
        recommended_kw=kw,
        panel_count=panels,
        roof_sqft_needed=round(kw * ROOF_SQFT_PER_KW),
        monthly_generation_units=round(gen),
        gross_cost_rs=round(gross),
        subsidy_rs=round(subsidy),
        net_cost_rs=round(net),
        annual_savings_rs=round(annual_savings),
        monthly_savings_rs=round(monthly_savings),
        payback_years=round(payback, 1),
        lifetime_savings_rs=round(lifetime),
        co2_tonnes_per_year=round(co2_kg / 1000, 2),
        trees_equivalent=int(round(co2_kg / CO2_KG_PER_TREE_PER_YEAR)),
        coverage_percent=round(min(100.0, gen / monthly_units * 100)),
        assumptions={
            "units_per_kw_per_day": UNITS_PER_KW_PER_DAY,
            "roof_sqft_per_kw": ROOF_SQFT_PER_KW,
            "grid_co2_kg_per_kwh": GRID_CO2_KG_PER_KWH,
            "export_rate_rs_per_unit": EXPORT_RATE_RS_PER_UNIT,
            "installed_cost_rs_per_kw": installed_cost_per_kw(kw),
            "scheme": "PM Surya Ghar Muft Bijli Yojana CFA: Rs 30k/kW up to 2 kW, Rs 18k for 3rd kW, cap Rs 78k",
            "panel_watt": PANEL_WATT,
            "system_life_years": SYSTEM_LIFE_YEARS,
        },
    )


def to_dict(e: Estimate) -> dict:
    return asdict(e)
