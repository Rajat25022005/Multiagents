"""
Celery tasks – run in separate worker process, can use sync SQLAlchemy.
"""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from celery import states
from sqlalchemy import create_engine, update
from sqlalchemy.orm import Session

from core.config import get_settings
from workers.celery_app import celery_app

settings = get_settings()

# Sync engine for Celery workers (asyncpg → psycopg2 compatible)
_sync_db_url = settings.database_url.replace("+asyncpg", "+psycopg2")
_engine = None


def _get_sync_engine():
    global _engine
    if _engine is None:
        _engine = create_engine(_sync_db_url)
    return _engine


@celery_app.task(bind=True, name="workers.tasks.execute_task_celery")
def execute_task_celery(
    self,
    task_id: int,
    task_description: str,
    user_id: int,
    provider: str | None = None,
    model: str | None = None,
):
    from api.models.task import TaskRecord
    from orchestrator.engine import OrchestratorEngine

    engine_db = _get_sync_engine()

    def update_status(status: str, **kwargs):
        with Session(engine_db) as session:
            stmt = update(TaskRecord).where(TaskRecord.id == task_id).values(
                status=status, **kwargs
            )
            session.execute(stmt)
            session.commit()
        self.update_state(state="PROGRESS", meta={"stage": status, "task_id": task_id})

    try:
        update_status("planning")

        orchestrator = OrchestratorEngine(provider=provider, model=model)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                orchestrator.execute(
                    task=task_description,
                    user_id=user_id,
                    task_db_id=task_id,
                    on_stage=lambda stage: update_status(stage),
                )
            )
        finally:
            try:
                pending = asyncio.all_tasks(loop)
                for task in pending:
                    task.cancel()
                if pending:
                    loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
            finally:
                loop.close()
                asyncio.set_event_loop(None)

        update_status(
            "done",
            result=result,
            completed_at=datetime.now(timezone.utc),
        )
        return {"status": "done", "task_id": task_id}

    except Exception as exc:
        update_status("failed", error=str(exc))
        self.update_state(state=states.FAILURE, meta={"error": str(exc)})
        raise
