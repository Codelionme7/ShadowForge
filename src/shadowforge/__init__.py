"""ShadowForge - Adversarial Shadow CFO for African financial decisions."""

__version__ = "0.2.0"

from .aws_bedrock import generate_bedrock_cfo_memo
from .engine import calculate_resilience_plan, compare_all_shocks, run_simulation
from .scenarios import SHOCKS, get_shock, list_shocks

__all__ = [
    "__version__",
    "SHOCKS",
    "list_shocks",
    "get_shock",
    "run_simulation",
    "calculate_resilience_plan",
    "compare_all_shocks",
    "generate_bedrock_cfo_memo",
]
