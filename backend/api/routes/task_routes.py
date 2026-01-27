from fastapi import APIRouter, Depends
from backend.api.schemas.task_schema import TaskRequest
from backend.core.orchestrator_engine import OrchestratorEngine
from backend.api.auth_utils import get_current_user
from backend.api.models import User

router = APIRouter()
engine = OrchestratorEngine()


@router.post("/execute")
def execute_task(
    payload: TaskRequest,
    current_user: User = Depends(get_current_user)
):
    """Execute a task (requires authentication)."""
    # Add user context to the task
    context = payload.context or {}
    context["user"] = {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email
    }
    
    result = engine.execute(payload.task, context)
    return {
        "success": True,
        "data": result,
        "executed_by": current_user.username
    }
