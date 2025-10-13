from multiprocessing import Queue
from app.services.backtesting.engines.backtest_engine import run_backtest

def run_segment(segment_data, segment_id, strategy_symbols, params, lookback, progress_queue=None):
    # In child process, define a callback that puts progress into the queue
    def progress_callback(current_idx, total):
        pct = round(current_idx / total * 100, 2)
        progress_queue.put({
            "segment_id": segment_id,
            "progress_pct": pct,
            "done": False
        })

    result = run_backtest(segment_data, strategy_symbols, params, lookback, progress_callback)

    progress_queue.put({
        "segment_id": segment_id,
        "progress_pct": 100.0,
        "done": True,
        "result": result
    })

