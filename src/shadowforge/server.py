"""ShadowForge MCP server - Alexa+ facing tools."""

from __future__ import annotations
import json
from mcp.server.fastmcp import FastMCP
from .aws_bedrock import generate_bedrock_cfo_memo
from .engine import calculate_resilience_plan, compare_all_shocks, run_simulation
from .scenarios import list_shocks

mcp = FastMCP("ShadowForge")


@mcp.tool()
def list_economic_shocks() -> str:
    """List available African economic shock scenarios."""
    return json.dumps(list_shocks(), indent=2)


@mcp.tool()
def run_shadow_cfo(
    monthly_income: float,
    monthly_expenses: float,
    savings: float,
    months: int = 12,
    n_paths: int = 500,
    shock_id: str | None = None,
    currency: str = "KES",
) -> str:
    """Run adversarial Monte-Carlo simulation and return JSON telemetry + Bedrock CFO memo."""
    sim = run_simulation(
        monthly_income=monthly_income,
        monthly_expenses=monthly_expenses,
        savings=savings,
        months=months,
        n_paths=n_paths,
        shock_id=shock_id,
        currency=currency,
    )
    sim["bedrock_executive_memo"] = generate_bedrock_cfo_memo(sim)
    return json.dumps(sim, indent=2)


@mcp.tool()
def get_resilience_plan(
    monthly_income: float,
    monthly_expenses: float,
    savings: float,
    target_survival: float = 0.85,
    months: int = 12,
    shock_id: str | None = None,
    currency: str = "KES",
) -> str:
    """Compute exact monthly expense cut or savings buffer needed to reach target survival."""
    plan = calculate_resilience_plan(
        monthly_income=monthly_income,
        monthly_expenses=monthly_expenses,
        savings=savings,
        target_survival=target_survival,
        months=months,
        shock_id=shock_id,
        currency=currency,
    )
    return json.dumps(plan, indent=2)


@mcp.tool()
def compare_shock_vulnerabilities(
    monthly_income: float,
    monthly_expenses: float,
    savings: float,
    months: int = 12,
    currency: str = "KES",
) -> str:
    """Compare financial survival across all 5 calibrated African macroeconomic shocks."""
    comp = compare_all_shocks(
        monthly_income=monthly_income,
        monthly_expenses=monthly_expenses,
        savings=savings,
        months=months,
        currency=currency,
    )
    return json.dumps(comp, indent=2)


def main() -> None:
    """Entry point for the ShadowForge MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
