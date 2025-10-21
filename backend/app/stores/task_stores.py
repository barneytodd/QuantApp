from collections import defaultdict

# =============================================
# Prescreen Tasks Store
# =============================================
# Tracks progress and results of stock prescreening tasks.
# Each task_id maps to a dict containing:
#   - progress: dict with testing, completed, and total counts
#   - results: dict mapping symbol -> test results
#   - fails: dict of fail counts per test group
prescreen_tasks_store = defaultdict(
    lambda: {
        "progress": {"testing": 0, "completed": 0, "total": 0},
        "results": {},
        "fails": {
            "global": {},
            "momentum": {},
            "mean_reversion": {},
            "breakout": {}
        }
    }
)


# =============================================
# Walkforward Tasks Store
# =============================================
# Tracks walkforward backtesting tasks.
# Key: task_id -> value: dict with backtest progress, results, window info, etc.
walkforward_tasks_store = {}


# =============================================
# Pairs Trading Tasks Store
# =============================================
# Stores progress and results for pairs trading strategy tasks.
pairs_tasks_store = {}


# =============================================
# Parameter Optimisation Tasks Store
# =============================================
# Tracks parameter optimisation tasks for strategies.
param_optimisation_tasks_store = {}
