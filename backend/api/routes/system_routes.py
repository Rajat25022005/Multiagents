from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from api.deps import get_current_user, require_admin
from api.models.schemas import HealthOut
from api.models.user import User
from core.config import get_settings
from core.database import get_db

router = APIRouter(prefix="/system", tags=["system"])
settings = get_settings()

APP_VERSION = "2.0.0"


@router.get("/health", response_model=HealthOut)
async def health(db: AsyncSession = Depends(get_db)):
    services: dict[str, str] = {}

    # PostgreSQL
    try:
        await db.execute(text("SELECT 1"))
        services["postgres"] = "ok"
    except Exception as e:
        services["postgres"] = f"error: {e}"

    # Redis
    try:
        import redis
        r = redis.from_url(settings.redis_url, socket_connect_timeout=2)
        r.ping()
        services["redis"] = "ok"
    except Exception as e:
        services["redis"] = f"error: {e}"

    # Neo4j
    try:
        from core.neo4j_client import Neo4jClient
        client = Neo4jClient.get()
        with client.session() as s:
            s.run("RETURN 1")
        services["neo4j"] = "ok"
    except Exception as e:
        services["neo4j"] = f"error: {e}"

    # Vector DB
    try:
        import chromadb
        chromadb.PersistentClient(path=settings.vector_db_path)
        services["chromadb"] = "ok"
    except Exception as e:
        services["chromadb"] = f"error: {e}"

    overall = "ok" if all(v == "ok" for v in services.values()) else "degraded"
    return HealthOut(status=overall, version=APP_VERSION, services=services)


@router.get("/info")
async def info(current_user: User = Depends(get_current_user)):
    return {
        "provider": settings.llm_provider,
        "model": settings.default_model,
        "env": settings.app_env,
        "version": APP_VERSION,
    }


@router.get("/admin/users")
async def list_users(
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    from sqlalchemy import select
    result = await db.execute(select(User))
    users = result.scalars().all()
    return [{"id": u.id, "email": u.email, "username": u.username, "created_at": u.created_at} for u in users]
