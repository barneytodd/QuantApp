from app.database import SessionLocal
import asyncio, uuid
from app.schemas import StrategyRequest

from app.api.routes.backtest import run_walkforward_async
from app.tasks import walkforward_tasks_store as tasks_store
from .scoring import composite_score
from app.services.backtesting.helpers.data.data_preparation import prepare_backtest_inputs, create_walkforward_windows
from app.services.backtesting.helpers.data.data_aggregation import compute_walkforward_results, aggregate_walkforward_results


def make_single_strategy_objective(strategy_name, cfg, global_params, window_length=3):
    async def async_objective(trial):
        # Generate trial params
        db = SessionLocal()
        param_space = cfg["param_space"]

        trial_params = {}
        for p_name, p_def in param_space.items():
            full_name = f"{strategy_name}_{p_name}"

            if p_def["type"] == "int":
                val = trial.suggest_int(full_name, p_def["min"], p_def["max"])
            elif p_def["type"] == "float":
                val = trial.suggest_float(full_name, p_def["min"], p_def["max"])
            elif p_def["type"] == "categorical":
                val = trial.suggest_categorical(full_name, p_def["choices"])
            else:
                continue  # skip unknown param types

            trial_params[p_name] = {
                "value": val,
                "lookback": p_def.get("lookback", False)
            }

        params = {**global_params, **trial_params}

        # Prepare and run walkforward directly
        all_symbols, strategy_symbols, params, lookback = prepare_backtest_inputs(StrategyRequest(
            symbolItems = cfg["symbolItems"],
            params = params
        ))

        windows = create_walkforward_windows(params["startDate"], params["endDate"], window_length=window_length)
        task_id = str(uuid.uuid4())
        print(f"[TASK {task_id}] Starting walk-forward with: ", windows, all_symbols, strategy_symbols, params, lookback)
        # Instead of create_task -> await directly
        await run_walkforward_async(
            task_id, windows, all_symbols, strategy_symbols, params, lookback, db
        )

        task = tasks_store[task_id]
        segments = [r for r in task["results"].values()]
        aggregated = aggregate_walkforward_results(segments)
        overall_results = [r for r in aggregated if r["symbol"] == "overall"]
        return composite_score(overall_results)

    def objective(trial):
        # This runs in separate process, so it's safe
        return asyncio.run(async_objective(trial))

    return objective
