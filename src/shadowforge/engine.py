"""Monte-Carlo personal finance simulator with African macroeconomic stress."""

from __future__ import annotations
import time
from typing import Any
import numpy as np
from .scenarios import SHOCKS, get_shock


def _verdict(survival: float, ruin: float) -> str:
    """Return tier verdict matching the ShadowForge specification."""
    if survival >= 0.85:
        return "RESILIENT - high chance of staying solvent under stress"
    if survival >= 0.60:
        return "CONDITIONAL - buffer is thin; adjust discretionary spending"
    return "HIGH RISK - high probability of financial depletion; immediate action required"


def run_simulation(
    monthly_income: float,
    monthly_expenses: float,
    savings: float,
    months: int = 12,
    n_paths: int = 500,
    shock_id: str | None = None,
    currency: str = "KES",
    seed: int = 42,
) -> dict[str, Any]:
    """
    Run adversarial Monte-Carlo paths using Argon Compute vectorized NumPy operations.
    Returns survival probability, ruin risk, and distribution percentiles.
    """
    if monthly_income < 0:
        raise ValueError("monthly_income must be >= 0")
    if monthly_expenses < 0:
        raise ValueError("monthly_expenses must be >= 0")
    if savings < 0:
        raise ValueError("savings must be >= 0")
    if months < 1 or months > 120:
        raise ValueError("months must be between 1 and 120")
    if n_paths < 1 or n_paths > 100_000:
        raise ValueError("n_paths must be between 1 and 100,000")

    t0 = time.perf_counter()
    rng = np.random.default_rng(seed)

    if shock_id and shock_id.strip():
        shock = get_shock(shock_id)
        shock_used_name = shock["name"]
        mitigation_tip = shock["mitigation_tip"]
        infl_means = np.full(n_paths, float(shock["inflation_mean"]))
        infl_stds = np.full(n_paths, float(shock["inflation_std"]))
        fx_shocks = np.full(n_paths, float(shock["fx_shock"]))
        inc_hits = np.full(n_paths, float(shock["income_hit"]))
    else:
        ids = list(SHOCKS.keys())
        probs = np.array([SHOCKS[i]["probability"] for i in ids], dtype=np.float64)
        probs = probs / np.sum(probs)
        chosen_indices = rng.choice(len(ids), size=n_paths, p=probs)
        infl_means = np.array([SHOCKS[ids[i]]["inflation_mean"] for i in chosen_indices])
        infl_stds = np.array([SHOCKS[ids[i]]["inflation_std"] for i in chosen_indices])
        fx_shocks = np.array([SHOCKS[ids[i]]["fx_shock"] for i in chosen_indices])
        inc_hits = np.array([SHOCKS[ids[i]]["income_hit"] for i in chosen_indices])
        shock_used_name = "Probabilistic African Macro Mix"
        mitigation_tip = "Maintain a 4-month liquid reserve buffer and cap fixed costs at 70% of net income."

    bal = np.full(n_paths, float(savings), dtype=np.float64)
    income = np.full(n_paths, float(monthly_income), dtype=np.float64)
    expenses = np.full(n_paths, float(monthly_expenses), dtype=np.float64)

    first_ruin_month = np.full(n_paths, np.nan, dtype=np.float64)
    ever_ruined = np.zeros(n_paths, dtype=bool)

    for m in range(1, months + 1):
        infl = rng.normal(infl_means, infl_stds)
        infl = np.maximum(0.0, infl)
        expenses = expenses * (1.0 + infl / 12.0)
        income = income * (1.0 - inc_hits / 12.0)
        expenses = expenses * (1.0 + fx_shocks / 12.0)

        bal = bal + (income - expenses)

        newly_ruined = (bal <= 0.0) & (~ever_ruined)
        first_ruin_month[newly_ruined] = float(m)
        ever_ruined |= bal <= 0.0

        bal = np.maximum(0.0, bal)

    paths = bal
    ruin_rate = float(np.mean(paths <= 0.0))
    survival = 1.0 - ruin_rate
    p10, p50, p90 = np.percentile(paths, [10, 50, 90])
    var_95 = float(np.percentile(paths, 5))
    tail = paths[paths <= var_95]
    cvar_95 = float(np.mean(tail)) if len(tail) > 0 else var_95

    ruined_months = first_ruin_month[~np.isnan(first_ruin_month)]
    median_ruin_month = round(float(np.median(ruined_months)), 1) if len(ruined_months) > 0 else None
    latency_ms = round((time.perf_counter() - t0) * 1000.0, 3)

    verdict_text = _verdict(survival, ruin_rate)
    surv_pct = round(survival * 100)

    return {
        "currency": currency,
        "months": months,
        "n_paths": n_paths,
        "shock_used": shock_used_name,
        "survival_probability": round(survival, 3),
        "ruin_risk": round(ruin_rate, 3),
        "ending_balance": {
            "p10": round(float(p10), 2),
            "median": round(float(p50), 2),
            "p90": round(float(p90), 2),
            "mean": round(float(np.mean(paths)), 2),
            "var_95": round(var_95, 2),
            "cvar_95": round(cvar_95, 2),
        },
        "telemetry": {
            "median_month_of_ruin": median_ruin_month,
            "compute_latency_ms": latency_ms,
        },
        "verdict": verdict_text,
        "mitigation_tip": mitigation_tip,
        "voice_briefing": (
            f"Under {shock_used_name}, your 12-month survival rate is {surv_pct}% "
            f"with a median ending balance of {float(p50):,.0f} {currency}. "
            f"Recommendation: {mitigation_tip}"
        ),
    }


def calculate_resilience_plan(
    monthly_income: float,
    monthly_expenses: float,
    savings: float,
    target_survival: float = 0.85,
    months: int = 12,
    shock_id: str | None = None,
    currency: str = "KES",
) -> dict[str, Any]:
    """
    Reverse stress-testing solver using Bisection Search.
    Finds the exact monthly expense reduction or emergency savings boost needed to reach target_survival.
    """
    if not (0.0 < target_survival <= 1.0):
        raise ValueError("target_survival must be between 0.0 and 1.0")

    base = run_simulation(
        monthly_income=monthly_income,
        monthly_expenses=monthly_expenses,
        savings=savings,
        months=months,
        n_paths=500,
        shock_id=shock_id,
        currency=currency,
    )

    if base["survival_probability"] >= target_survival:
        return {
            "status": "ALREADY_RESILIENT",
            "target_survival": target_survival,
            "current_survival": base["survival_probability"],
            "recommended_monthly_expense_cut": 0.0,
            "recommended_additional_savings": 0.0,
            "currency": currency,
        }

    low_e, high_e = 0.0, float(monthly_expenses)
    best_e = 0.0
    for _ in range(18):
        mid_e = (low_e + high_e) / 2.0
        sim = run_simulation(
            monthly_income=monthly_income,
            monthly_expenses=mid_e,
            savings=savings,
            months=months,
            n_paths=300,
            shock_id=shock_id,
            currency=currency,
        )
        if sim["survival_probability"] >= target_survival:
            best_e = mid_e
            low_e = mid_e
        else:
            high_e = mid_e

    expense_cut = round(max(0.0, monthly_expenses - best_e), 2)

    low_s, high_s = float(savings), float(savings) + max(monthly_expenses * months * 2.0, 100_000.0)
    best_s = high_s
    for _ in range(18):
        mid_s = (low_s + high_s) / 2.0
        sim = run_simulation(
            monthly_income=monthly_income,
            monthly_expenses=monthly_expenses,
            savings=mid_s,
            months=months,
            n_paths=300,
            shock_id=shock_id,
            currency=currency,
        )
        if sim["survival_probability"] >= target_survival:
            best_s = mid_s
            high_s = mid_s
        else:
            low_s = mid_s

    savings_boost = round(max(0.0, best_s - savings), 2)

    return {
        "status": "ACTION_REQUIRED",
        "target_survival": target_survival,
        "current_survival": base["survival_probability"],
        "recommended_monthly_expense_cut": expense_cut,
        "safe_monthly_expense_limit": round(best_e, 2),
        "recommended_additional_savings": savings_boost,
        "safe_starting_savings_target": round(best_s, 2),
        "currency": currency,
    }


def compare_all_shocks(
    monthly_income: float,
    monthly_expenses: float,
    savings: float,
    months: int = 12,
    currency: str = "KES",
) -> dict[str, Any]:
    """Evaluate user finances across all 5 African shock scenarios and rank vulnerabilities."""
    ranking = []
    for sid in SHOCKS:
        res = run_simulation(
            monthly_income=monthly_income,
            monthly_expenses=monthly_expenses,
            savings=savings,
            months=months,
            n_paths=400,
            shock_id=sid,
            currency=currency,
        )
        ranking.append(
            {
                "shock_id": sid,
                "shock_name": res["shock_used"],
                "survival_probability": res["survival_probability"],
                "ruin_risk": res["ruin_risk"],
                "median_ending_balance": res["ending_balance"]["median"],
                "verdict": res["verdict"],
            }
        )

    ranking.sort(key=lambda x: x["survival_probability"])
    return {
        "currency": currency,
        "months": months,
        "most_vulnerable_shock": ranking[0],
        "most_resilient_shock": ranking[-1],
        "scenario_ranking": ranking,
    }
