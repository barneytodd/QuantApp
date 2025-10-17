from .scoring import composite_score
import copy, asyncio
from .backtest import run_strategy_backtest
from app.tasks import param_optimisation_tasks_store as tasks_store

def make_single_strategy_objective(strategy_name, cfg, global_params, scoring_params, window_length=3):
    async def async_objective(trial):
        # build per-strategy trial params
        param_space = cfg["param_space"]
        trial_params = {}

        for p_name, p_def in param_space.items():
            if p_def["type"] == "int":
                val = trial.suggest_int(p_name, p_def["min"], p_def["max"])
            elif p_def["type"] == "float":
                val = trial.suggest_float(p_name, p_def["min"], p_def["max"])
            elif p_def["type"] == "categorical":
                val = trial.suggest_categorical(p_name, p_def["choices"])
            else:
                continue
            trial_params[p_name] = {"value": val, "lookback": p_def.get("lookback", False)}

        # assign to shared config
        backtest_cfg = {
            **cfg,  # other static cfg values
            "trial_params": trial_params
        }
        # run combined backtest for all strategies with current params
        backtest_result = await run_strategy_backtest(backtest_cfg, global_params, window_length)

        score = composite_score(backtest_result, scoring_params)

        if strategy_name in tasks_store:
            store_entry = tasks_store[strategy_name]
            store_entry["completed_trials"] += 1
            store_entry["best_params"] = trial_params
            store_entry["best_score"] = score

        return score

    def objective(trial):
        # This runs in separate process, so it's safe
        return asyncio.run(async_objective(trial))

    return objective
