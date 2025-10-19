# app/api/portfolio.py
from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.orm import Session
from collections import defaultdict
import uuid
import json
import time
import asyncio
import os


from app.database import get_db
from app.schemas import PreScreenPayload
from app import crud
from app.services.portfolio.stages.prescreen.run_prescreen import run_tests
from app.tasks import prescreen_tasks_store as tasks_store


router = APIRouter()

# 1 Start pre-screening
@router.post("/runPreScreen/")
async def run_prescreen_tests(payload: PreScreenPayload, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    task_id = str(uuid.uuid4())
    tasks_store[task_id] = {
        "progress": {"testing": 0, "completed": 0, "total": len(payload.symbols)},
        "results": {},
        "fails": {"global": {}, "momentum": {}, "mean_reversion": {}, "breakout": {}}
    }

    symbols = payload.symbols
    start = payload.start
    end = payload.end
    filters = payload.filters

    def progress_cb(progress):
        tasks_store[task_id]["progress"] = progress

    async def background_task_async():
        print(f"[TASK {task_id}] starting pre-screen tests")
        try:
            max_workers = min(len(symbols), os.cpu_count() or 4)
            results, fails = await run_tests(
                symbols, start, end, filters,
                max_workers=max_workers,
                progress_callback=progress_cb,
                task_id=task_id
            )
            print(f"[TASK {task_id}] finished successfully")
        except Exception as e:
            print(f"[TASK {task_id}] failed: {e}")

    asyncio.create_task(background_task_async())

    return {"task_id": task_id}



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