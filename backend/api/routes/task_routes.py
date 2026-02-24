"""
Task routes:
  POST /tasks/execute        → queue async Celery job, return job_id
  POST /tasks/execute/stream → SSE streaming execution
  GET  /tasks/status/{job_id}→ poll Celery job status
  GET  /tasks/               → list user's task history
  GET  /tasks/{id}           → get single task
  DELETE /tasks/{id}         → delete task record
"""
from __future__ import annotations

import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_current_user
from api.models.schemas import TaskListOut, TaskOut, TaskRequest
from api.models.task import TaskRecord
from api.models.user import User
from core.database import get_db
from workers.tasks import execute_task_celery

router = APIRouter(prefix="/tasks", tags=["tasks"])


# ─── Queue async task ─────────────────────────────────────────────────────────

@router.post("/execute", response_model=TaskOut, status_code=status.HTTP_202_ACCEPTED)
async def execute_task(
    payload: TaskRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    record = TaskRecord(
        user_id=current_user.id,
        description=payload.task,
        status="queued",
    )
    db.add(record)
    await db.flush()
    await db.refresh(record)

    job = execute_task_celery.delay(
        task_id=record.id,
        task_description=payload.task,
        user_id=current_user.id,
        provider=payload.provider,
        model=payload.model,
    )
    record.job_id = job.id
    await db.flush()

    return TaskOut.model_validate(record)


# ─── SSE streaming ────────────────────────────────────────────────────────────

@router.post("/execute/stream")
async def execute_task_stream(
    payload: TaskRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from orchestrator.engine import OrchestratorEngine

    record = TaskRecord(
        user_id=current_user.id,
        description=payload.task,
        status="planning",
    )
    db.add(record)
    await db.flush()
    await db.refresh(record)
    task_db_id = record.id
    await db.commit()

    async def event_stream():
        engine = OrchestratorEngine(
            provider=payload.provider,
            model=payload.model,
        )
        async for event in engine.execute_streaming(
            task=payload.task,
            task_db_id=task_db_id,
            user_id=current_user.id,
        ):
            yield f"data: {json.dumps(event)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


# ─── Job status ───────────────────────────────────────────────────────────────

@router.get("/status/{job_id}")
async def job_status(job_id: str, current_user: User = Depends(get_current_user)):
    from workers.celery_app import celery_app
    job = celery_app.AsyncResult(job_id)
    return {
        "job_id": job_id,
        "status": job.status,
        "result": job.result if job.ready() else None,
        "info": job.info if job.status == "PROGRESS" else None,
    }


# ─── List tasks ───────────────────────────────────────────────────────────────

@router.get("/", response_model=TaskListOut)
async def list_tasks(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(TaskRecord)
        .where(TaskRecord.user_id == current_user.id)
        .order_by(TaskRecord.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    tasks = result.scalars().all()
    total_r = await db.execute(
        select(TaskRecord).where(TaskRecord.user_id == current_user.id)
    )
    total = len(total_r.scalars().all())
    return TaskListOut(tasks=[TaskOut.model_validate(t) for t in tasks], total=total)


# ─── Get single task ──────────────────────────────────────────────────────────

@router.get("/{task_id}", response_model=TaskOut)
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(TaskRecord).where(
            TaskRecord.id == task_id,
            TaskRecord.user_id == current_user.id,
        )
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskOut.model_validate(task)


# ─── Delete task ──────────────────────────────────────────────────────────────

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(TaskRecord).where(
            TaskRecord.id == task_id,
            TaskRecord.user_id == current_user.id,
        )
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    await db.delete(task)
