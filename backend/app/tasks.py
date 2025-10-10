from collections import defaultdict

# key: task_id -> value: dict with 'progress' and 'results'
tasks_store = defaultdict(lambda: {"progress": {"testing": 0, "completed": 0, "total": 0}, "results": {}, "fails": {"global": {}, "momentum": {}, "mean_reversion": {}, "breakout": {}}})
