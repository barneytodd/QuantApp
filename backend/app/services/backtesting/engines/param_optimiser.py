import optuna
import asyncio
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from app.services.backtesting.helpers.optimisation.objective import make_single_strategy_objective


def _run_single_study(strategy_name, cfg, global_params, n_trials, window_length):
    """Run one Optuna study in a separate process."""
    study = optuna.create_study(direction="maximize")
    objective = make_single_strategy_objective(strategy_name, cfg, global_params, window_length)
    study.optimize(objective, n_trials=n_trials)
    return {
        "strategy": strategy_name,
        "best_params": study.best_params,
        "best_score": study.best_value
    }


async def optimise_multiple_strategies_async(strategies_config, global_params, n_trials=50, window_length=3):
    """Run multiple strategies in parallel using ProcessPoolExecutor."""
    results = []
    with ProcessPoolExecutor() as pool:
        loop = asyncio.get_running_loop()
        tasks = []
        for strategy_name, cfg in strategies_config.items():
            task = loop.run_in_executor(
                pool,
                partial(_run_single_study, strategy_name, cfg, global_params, n_trials, window_length)
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks)

    return {r["strategy"]: r for r in results}


def optimise_parameters(strategies_config, global_params, optimisation_params):
    """Sync FastAPI entrypoint."""
    n_trials = optimisation_params.get("iterations", 50)
    window_length = optimisation_params.get("foldLength", 252)
    return asyncio.run(optimise_multiple_strategies_async(strategies_config, global_params, n_trials, window_length))
