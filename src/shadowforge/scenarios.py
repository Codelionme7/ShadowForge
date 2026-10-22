"""African economic shock scenarios for Monte-Carlo simulation."""

from __future__ import annotations
from typing import Any

SHOCKS: dict[str, dict[str, Any]] = {
    "kenya_inflation_spike": {
        "name": "Kenya Inflation Spike",
        "description": "Sudden 8-15% inflation surge with KES depreciation and fuel/food price pressure.",
        "inflation_mean": 0.12,
        "inflation_std": 0.04,
        "fx_shock": 0.08,
        "income_hit": 0.05,
        "probability": 0.18,
        "mitigation_tip": "Lock in fixed-rate Sacco or mobile money savings and bulk-purchase non-perishable staples.",
    },
    "nigeria_naira_devaluation": {
        "name": "Nigeria Naira Devaluation",
        "description": "Sharp Naira move against USD causing imported inflation and purchasing power erosion.",
        "inflation_mean": 0.18,
        "inflation_std": 0.06,
        "fx_shock": 0.25,
        "income_hit": 0.10,
        "probability": 0.22,
        "mitigation_tip": "Pre-pay recurring USD/imported costs early and diversify liquid reserves into hedged instruments.",
    },
    "south_africa_load_shedding": {
        "name": "South Africa Load Shedding Impact",
        "description": "Business disruption + higher backup energy costs and SME revenue compression.",
        "inflation_mean": 0.07,
        "inflation_std": 0.03,
        "fx_shock": 0.05,
        "income_hit": 0.12,
        "probability": 0.15,
        "mitigation_tip": "Ring-fence a dedicated inverter/fuel buffer and shift high-load operations to off-peak hours.",
    },
    "regional_drought": {
        "name": "East/West Africa Drought",
        "description": "Agricultural income and food price shock across urban and rural supply chains.",
        "inflation_mean": 0.14,
        "inflation_std": 0.05,
        "fx_shock": 0.04,
        "income_hit": 0.18,
        "probability": 0.12,
        "mitigation_tip": "Build a 3-month staple food & utility reserve buffer and diversify household income streams.",
    },
    "stable_baseline": {
        "name": "Stable Baseline",
        "description": "No major shock - normal volatility and baseline CPI progression.",
        "inflation_mean": 0.05,
        "inflation_std": 0.02,
        "fx_shock": 0.02,
        "income_hit": 0.0,
        "probability": 0.33,
        "mitigation_tip": "Automate monthly transfers of 15% of net surplus into high-yield money market funds.",
    },
}


def list_shocks() -> list[dict[str, Any]]:
    """Return metadata for all calibrated African macroeconomic shock scenarios."""
    return [
        {
            "id": k,
            "name": v["name"],
            "description": v["description"],
            "probability": v["probability"],
            "inflation_mean": v["inflation_mean"],
            "fx_shock": v["fx_shock"],
            "income_hit": v["income_hit"],
        }
        for k, v in SHOCKS.items()
    ]


def get_shock(shock_id: str) -> dict[str, Any]:
    """Retrieve a shock scenario by ID (case-insensitive) or raise ValueError."""
    if not isinstance(shock_id, str) or not shock_id.strip():
        raise ValueError("shock_id must be a non-empty string.")
    cleaned = shock_id.strip().lower()
    if cleaned not in SHOCKS:
        valid = ", ".join(SHOCKS.keys())
        raise ValueError(f"Unknown shock: {shock_id}. Valid IDs: {valid}")
    return SHOCKS[cleaned]
