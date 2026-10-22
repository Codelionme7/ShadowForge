from shadowforge import calculate_resilience_plan, compare_all_shocks, list_shocks, run_simulation


def test_list_shocks():
    shocks = list_shocks()
    assert len(shocks) == 5


def test_run_simulation():
    res = run_simulation(100000, 70000, 200000, shock_id="kenya_inflation_spike")
    assert 0.0 <= res["survival_probability"] <= 1.0
    assert res["currency"] == "KES"


def test_resilience_plan_and_comparison():
    plan = calculate_resilience_plan(80000, 75000, 50000, shock_id="nigeria_naira_devaluation")
    assert "status" in plan
    comp = compare_all_shocks(100000, 80000, 150000)
    assert len(comp["scenario_ranking"]) == 5
