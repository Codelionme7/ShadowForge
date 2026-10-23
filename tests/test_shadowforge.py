"""Unit and integration tests for ShadowForge."""

from __future__ import annotations
import json
import pytest

from shadowforge import (
    SHOCKS,
    calculate_resilience_plan,
    compare_all_shocks,
    generate_bedrock_cfo_memo,
    get_shock,
    list_shocks,
    run_simulation,
)
from shadowforge.server import (
    compare_shock_vulnerabilities,
    get_resilience_plan,
    list_economic_shocks,
    run_shadow_cfo,
)


def test_list_and_get_shocks() -> None:
    shocks = list_shocks()
    assert len(shocks) == 5
    kenya = get_shock("KENYA_INFLATION_SPIKE")
    assert kenya["name"] == "Kenya Inflation Spike"
    with pytest.raises(ValueError):
        get_shock("invalid_shock_id")
    with pytest.raises(ValueError):
        get_shock("   ")


def test_run_simulation_resilient() -> None:
    res = run_simulation(
        monthly_income=150_000,
        monthly_expenses=80_000,
        savings=500_000,
        months=12,
        n_paths=200,
        shock_id="stable_baseline",
        currency="KES",
    )
    assert res["survival_probability"] >= 0.85
    assert "RESILIENT" in res["verdict"]
    assert res["ending_balance"]["median"] > 500_000


def test_run_simulation_high_risk_and_probabilistic_mix() -> None:
    res = run_simulation(
        monthly_income=50_000,
        monthly_expenses=95_000,
        savings=40_000,
        months=12,
        n_paths=200,
        shock_id=None,
        currency="NGN",
    )
    assert res["survival_probability"] < 0.60
    assert "HIGH RISK" in res["verdict"]
    assert res["telemetry"]["median_month_of_ruin"] is not None


def test_simulation_validation_errors() -> None:
    with pytest.raises(ValueError):
        run_simulation(-1, 1000, 1000)
    with pytest.raises(ValueError):
        run_simulation(1000, -1, 1000)
    with pytest.raises(ValueError):
        run_simulation(1000, 1000, -1)
    with pytest.raises(ValueError):
        run_simulation(1000, 1000, 1000, months=0)
    with pytest.raises(ValueError):
        run_simulation(1000, 1000, 1000, n_paths=0)


def test_calculate_resilience_plan() -> None:
    already_ok = calculate_resilience_plan(
        monthly_income=200_000,
        monthly_expenses=80_000,
        savings=600_000,
        target_survival=0.85,
        shock_id="stable_baseline",
    )
    assert already_ok["status"] == "ALREADY_RESILIENT"

    needs_action = calculate_resilience_plan(
        monthly_income=80_000,
        monthly_expenses=100_000,
        savings=50_000,
        target_survival=0.85,
        shock_id="nigeria_naira_devaluation",
    )
    assert needs_action["status"] == "ACTION_REQUIRED"
    assert needs_action["recommended_monthly_expense_cut"] > 0
    assert needs_action["recommended_additional_savings"] > 0


def test_compare_all_shocks() -> None:
    comp = compare_all_shocks(
        monthly_income=100_000,
        monthly_expenses=85_000,
        savings=150_000,
    )
    assert len(comp["scenario_ranking"]) == len(SHOCKS)
    assert (
        comp["most_vulnerable_shock"]["survival_probability"]
        <= comp["most_resilient_shock"]["survival_probability"]
    )


def test_bedrock_fallback_memo(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("AWS_ACCESS_KEY_ID", raising=False)
    monkeypatch.delenv("AWS_SECRET_ACCESS_KEY", raising=False)
    sim = run_simulation(100_000, 70_000, 200_000, shock_id="kenya_inflation_spike")
    memo = generate_bedrock_cfo_memo(sim)
    assert memo["engine"] == "shadowforge_local_deterministic_fallback"
    assert "Kenya Inflation Spike" in memo["cfo_memo"]


def test_mcp_server_tools() -> None:
    shocks_json = json.loads(list_economic_shocks())
    assert len(shocks_json) == 5

    cfo_json = json.loads(run_shadow_cfo(120_000, 80_000, 300_000, shock_id="kenya_inflation_spike"))
    assert "bedrock_executive_memo" in cfo_json

    plan_json = json.loads(get_resilience_plan(120_000, 80_000, 300_000))
    assert "status" in plan_json

    comp_json = json.loads(compare_shock_vulnerabilities(120_000, 80_000, 300_000))
    assert "scenario_ranking" in comp_json
