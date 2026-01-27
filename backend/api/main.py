from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes.task_routes import router as task_router
from backend.api.routes.system_routes import router as system_router
from backend.api.routes.auth_routes import router as auth_router
from backend.config.database import engine, Base
from backend.api.models import User  # Import models to register them

app = FastAPI(
    title="Multi-Agent Orchestration API",
    version="1.0.0"
)

# Create database tables on startup
@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)

# Add CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:8000",  # Backend
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)  # Auth routes don't need prefix, already in router
app.include_router(task_router, prefix="/tasks", tags=["Tasks"])
app.include_router(system_router, prefix="/system", tags=["System"])

@app.get("/")
def root():
    return {
        "message": "Welcome to Multi-Agent Orchestrator API",
        "docs": "/docs",
        "health": "/system/health"
    }
