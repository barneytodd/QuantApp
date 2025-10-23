import asyncio
import nest_asyncio
import optuna

from app.services.backtesting.helpers.optimisation import make_single_strategy_objective
from app.stores.task_stores import param_optimisation_tasks_store as tasks_store


def _run_single_study(db, strategy_name, cfg, global_params, scoring_params, metric_ranges, window_length, n_trials):
    """
    Run a single Optuna study for one strategy.

    Args:
        strategy_name (str): Name of the strategy
        cfg (dict): Strategy-specific configuration
        global_params (dict): Global parameters shared across strategies
        scoring_params (dict): Metrics for scoring trials
        window_length (int): Lookback window for evaluation
        n_trials (int): Number of Optuna trials

    Returns:
        dict: Best params, best score, and aggregated results
    """

    # Needed to allow nested event loops (e.g., when running in Jupyter / FastAPI background task)
    nest_asyncio.apply()

    # Create Optuna study (maximize the objective)
    study = optuna.create_study(direction="maximize")

    # Wrap the trial function with your custom objective
    objective = make_single_strategy_objective(db, strategy_name, cfg, global_params, scoring_params, metric_ranges, window_length)
    
    def trial_callback(study, trial):
        """
        Called after each trial completes.
        Updates tasks_store with progress and best results.
        """
        store_entry = tasks_store[strategy_name]
        completed_trials = len([t for t in study.trials if t.state == optuna.trial.TrialState.COMPLETE])
        store_entry["completed_trials"] = completed_trials

        if completed_trials > 0:
            store_entry["best_score"] = study.best_value
            store_entry["best_params"] = study.best_params

    def wrapped_objective(trial):
        """
        Wrap the original objective to store aggregated results in user_attrs.
        """
        score, aggregated_results = objective(trial)
        trial.set_user_attr("aggregated_results", aggregated_results)
        return score
    
    # Run the optimisation
    study.optimize(wrapped_objective, n_trials=n_trials, n_jobs=1, callbacks=[trial_callback])

    # Mark strategy as done in task store
    tasks_store[strategy_name]["status"] = "done"

    best_trial = study.best_trial
    best_aggregated_results = best_trial.user_attrs.get("aggregated_results")

    return {
        "strategy": strategy_name,
        "best_params": study.best_params,
        "best_score": study.best_value,
        "aggregated_results": best_aggregated_results
    }


async def optimise_multiple_strategies_async(db, strategies_config, global_params, scoring_params, metric_ranges, n_trials=50, window_length=3):
    """
    Run multiple strategies sequentially using asyncio.

    Args:
        strategies_config (dict): {strategy_name: config}
        global_params (dict): Global strategy parameters
        scoring_params (dict): Metrics to score trials
        n_trials (int): Number of trials per strategy
        window_length (int): Lookback window for evaluation

    Returns:
        dict: {strategy_name: {best_params, aggregated_results}}
    """

    results = {}
    for strategy_name, cfg in strategies_config.items():
        result = _run_single_study(
            db,
            strategy_name,
            cfg,
            global_params,
            scoring_params,
            metric_ranges, 
            window_length,
            n_trials
        )
        results[result["strategy"]] = {
            "best_params": result["best_params"],
            "aggregated_results": result["aggregated_results"]
        }
    
    return results


def optimise_parameters(db, strategies_config, global_params, optimisation_params, scoring_params, metric_ranges):
    """
    FastAPI synchronous entrypoint for parameter optimisation.

    Sets up tasks_store and runs async optimisation using asyncio.run.

    Args:
        strategies_config (dict): {strategy_name: config}
        global_params (dict)
        optimisation_params (dict): e.g., {"iterations": 50, "window_length": 3}
        scoring_params (dict)

    Returns:
        dict: results per strategy
    """
    n_trials = optimisation_params.get("iterations", 50)
    window_length = optimisation_params.get("window_length", 3)

    # Initialize task store entries for tracking progress
    for strategy_name in strategies_config.keys():
        tasks_store[strategy_name] = {
            "strategy": strategy_name,
            "total_trials": n_trials,
            "completed_trials": 0,
            "status": "pending",
            "best_score": None,
            "best_params": None
        }

    # Run the async optimisation loop synchronously
    return asyncio.run(
        optimise_multiple_strategies_async(db, strategies_config, global_params, scoring_params, metric_ranges, n_trials, window_length)
    )
