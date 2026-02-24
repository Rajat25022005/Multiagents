"""
Multi-Agent Orchestration System – FastAPI Application Entry Point
"""
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from api.routes.auth_routes import router as auth_router
from api.routes.system_routes import router as system_router
from api.routes.task_routes import router as task_router
from core.config import get_settings
from core.database import init_db

logger = structlog.get_logger()
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Multi-Agent System", env=settings.app_env)
    await init_db()

    # Warm up vector memory
    try:
        from agents.vector_memory import VectorMemory
        VectorMemory.get()
        logger.info("Vector memory initialized")
    except Exception as e:
        logger.warning("Vector memory unavailable", error=str(e))

    # Connect Neo4j
    try:
        from core.neo4j_client import Neo4jClient
        Neo4jClient.get().connect()
        logger.info("Neo4j connected")
    except Exception as e:
        logger.warning("Neo4j unavailable", error=str(e))

    yield

    logger.info("Shutting down")


app = FastAPI(
    title="Multi-Agent Orchestration System",
    description="Advanced AI agent system with parallel execution, vector memory, and ReAct tools",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ─── Middleware ───────────────────────────────────────────────────────────────

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routers ──────────────────────────────────────────────────────────────────

app.include_router(auth_router)
app.include_router(task_router)
app.include_router(system_router)


@app.get("/")
async def root():
    return {
        "name": "Multi-Agent Orchestration System",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/system/health",
    }
