import optuna
import asyncio, nest_asyncio, uuid
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from app.services.backtesting.helpers.optimisation.objective import make_single_strategy_objective
from app.tasks import param_optimisation_tasks_store as tasks_store



def _run_single_study(strategy_name, cfg, global_params, scoring_params, window_length, n_trials):
    """Run one Optuna study in a separate process."""
    nest_asyncio.apply()

    study = optuna.create_study(direction="maximize")

    objective = make_single_strategy_objective(strategy_name, cfg, global_params, scoring_params, window_length)
    
    # Define callback for after each trial
    def trial_callback(study, trial):
        store_entry = tasks_store[strategy_name]
        store_entry["completed_trials"] = len([t for t in study.trials if t.state == optuna.trial.TrialState.COMPLETE])
        if len([t for t in study.trials if t.state == optuna.trial.TrialState.COMPLETE]) > 0:
            store_entry["best_score"] = study.best_value
            store_entry["best_params"] = study.best_params

    def wrapped_objective(trial):
        score, aggregated_results = objective(trial)
        trial.set_user_attr("aggregated_results", aggregated_results)
        return score
    
    study.optimize(wrapped_objective, n_trials=n_trials, n_jobs=1, callbacks=[trial_callback])

    tasks_store[strategy_name]["status"] = "done"

    best_trial = study.best_trial
    best_aggregated_results = best_trial.user_attrs.get("aggregated_results")

    return {
        "strategy": strategy_name,
        "best_params": study.best_params,
        "best_score": study.best_value,
        "aggregated_results": best_aggregated_results
    }


async def optimise_multiple_strategies_async(strategies_config, global_params, scoring_params, n_trials=50, window_length=3):
    """Run multiple strategies sequntially."""
    results = {}
    for strategy_name, cfg in strategies_config.items():
        result = _run_single_study(
            strategy_name,
            cfg,
            global_params,
            scoring_params,
            window_length,
            n_trials
        )
        results[result["strategy"]] = {
            "best_params": result["best_params"],
            "aggregated_results": result["aggregated_results"]
        }
    
    return results


def optimise_parameters(strategies_config, global_params, optimisation_params, scoring_params):
    """Sync FastAPI entrypoint."""
    n_trials = optimisation_params.get("iterations", 50)
    window_length = optimisation_params.get("window_length", 3)

    for strategy_name in strategies_config.keys():
        tasks_store[strategy_name] = {
            "strategy": strategy_name,
            "total_trials": n_trials,
            "completed_trials": 0,
            "status": "pending",
            "best_score": None,
            "best_params": None
        }


    return asyncio.run(optimise_multiple_strategies_async(strategies_config, global_params, scoring_params, n_trials, window_length))
