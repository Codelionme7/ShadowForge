"""Quick CLI smoke test for ShadowForge."""
from shadowforge import run_simulation, generate_bedrock_cfo_memo

if __name__ == "__main__":
    result = run_simulation(120000, 85000, 150000, shock_id="kenya_inflation_spike")
    memo = generate_bedrock_cfo_memo(result)
    print(memo["cfo_memo"])
