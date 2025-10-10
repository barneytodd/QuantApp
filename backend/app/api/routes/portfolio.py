# app/api/portfolio.py
from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.orm import Session
from collections import defaultdict
import uuid
import json
import time
import asyncio


from app.database import get_db
from app.schemas import PreScreenPayload
from app import crud
from app.services.portfolio.stages.prescreen.run_prescreen import run_tests
from app.tasks import tasks_store


router = APIRouter()

# 1 Start pre-screening
@router.post("/runPreScreen/")
def run_prescreen_tests(payload: PreScreenPayload, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    task_id = str(uuid.uuid4())
    tasks_store[task_id] = {"progress": {"testing": 0, "completed": 0, "total": len(payload.symbols)}, "results": {}, "fails": {"global": {}, "momentum": {}, "mean_reversion":{}, "breakout": {}}}

    # Minimal data capture for background task
    symbols = payload.symbols
    start = payload.start
    end = payload.end
    filters = payload.filters

    def background_task():

        def progress_cb(progress):
            tasks_store[task_id]["progress"] = {
                "testing": progress.get("testing", 0),
                "completed": progress.get("completed", 0),
                "total": progress.get("total", 0)
            }
            print(f"[TASK {task_id}] Progress: "
              f"testing {tasks_store[task_id]['progress']['testing']}, "
              f"completed {tasks_store[task_id]['progress']['completed']}/{tasks_store[task_id]['progress']['total']}")

        print("submitting for tests")
        # Run tests using ProcessPoolExecutor
        results, fails = run_tests(symbols, start, end, filters, max_workers=5, progress_callback=progress_cb, task_id=task_id)

    # Schedule background task
    background_tasks.add_task(background_task)

    return {"task_id": task_id}  # returns immediately


# 2 Stream progress via SSE
@router.get("/streamProgress/{task_id}")
async def stream_progress(task_id: str):
    async def event_generator():
        last_progress = {"testing": -1, "completed": -1}
        while True:
            progress = tasks_store.get(task_id, {}).get(
                "progress", {"testing": 0, "completed": 0, "total": 0}
            )
            if (progress["completed"] != last_progress["completed"] or
                progress["testing"] != last_progress["testing"]):
                last_progress = progress.copy()
                yield f"data: {json.dumps(progress)}\n\n"

            if progress["completed"] >= progress["total"]:
                # Send a final JSON object indicating completion
                final_event = last_progress.copy()
                final_event["done"] = True
                yield f"data: {json.dumps(final_event)}\n\n"
                break

            await asyncio.sleep(0.1)

    return StreamingResponse(event_generator(), media_type="text/event-stream")



# 3 Get final results
@router.get("/getPreScreenResults/{task_id}")
def get_prescreen_results(task_id: str):
    task = tasks_store[task_id]
    if not task:
        return JSONResponse({"detail": "Task not found or not completed"}, status_code=404)

    results = task.get("results", {})
    fails = task.get("fails", {})  # make sure you store fails in tasks_store

    # Return a consistent object
    return {"symbols": results, "failed_count": fails}