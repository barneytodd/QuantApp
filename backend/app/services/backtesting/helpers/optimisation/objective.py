import asyncio

from .backtest import run_strategy_backtest
from .scoring import composite_score
from app.stores.task_stores import param_optimisation_tasks_store as tasks_store


def make_single_strategy_objective(strategy_name, cfg, global_params, scoring_params, metric_ranges, window_length=3):
    """
    Create an Optuna-compatible objective function for a single strategy.

    This function generates trial parameters, runs a walk-forward backtest asynchronously,
    computes a composite score, and updates the task store.

    Args:
        strategy_name (str): Name of the strategy being optimized.
        cfg (dict): Strategy configuration, including param_space and symbolItems.
        global_params (dict): Global parameters for the backtest (capital, slippage, etc.).
        scoring_params (dict): Weights and metrics for composite scoring.
        window_length (int): Number of years per walk-forward segment.
    
    Returns:
        objective (callable): Function that takes a trial and returns a score for Optuna.
    """

    async def async_objective(trial):
        """
        Asynchronous objective function to generate trial parameters and run backtest.
        """
        # --- Build per-trial parameter set ---
        param_space = cfg["param_space"]
        trial_params = {}

        for p_name, p_def in param_space.items():
            # Suggest value according to parameter type
            if p_def["type"] == "int":
                val = trial.suggest_int(p_name, p_def["min"], p_def["max"])
            elif p_def["type"] == "float":
                val = trial.suggest_float(p_name, p_def["min"], p_def["max"])
            elif p_def["type"] == "categorical":
                val = trial.suggest_categorical(p_name, p_def["choices"])
            else:
                continue  # skip unknown types

            # Store value with optional lookback info
            trial_params[p_name] = {"value": val, "lookback": p_def.get("lookback", False)}

        # --- Combine trial params with static strategy config ---
        backtest_cfg = {
            **cfg,  # other static config values like symbolItems
            "trial_params": trial_params
        }

        # --- Run walk-forward backtest asynchronously ---
        backtest_result = await run_strategy_backtest(backtest_cfg, global_params, window_length)

        # Separate overall portfolio results vs individual symbol-strategy results
        overall_results = [r for r in backtest_result if r["symbol"] == "overall"]
        symbol_results = [r for r in backtest_result if r["symbol"] != "overall"]

        # --- Compute composite score for the trial ---
        score = composite_score(overall_results, scoring_params, metric_ranges)

        # --- Update shared task store for progress tracking ---
        if strategy_name in tasks_store:
            store_entry = tasks_store[strategy_name]
            store_entry["completed_trials"] += 1
            store_entry["best_params"] = trial_params
            store_entry["best_score"] = score

        return score, symbol_results

    def objective(trial):
        """
        Synchronous wrapper to run the async objective inside Optuna.
        This allows Optuna to execute the async backtest in a blocking context.
        """
        return asyncio.run(async_objective(trial))

    return objective
