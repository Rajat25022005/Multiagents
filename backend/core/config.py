from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=("../.env", ".env"), extra="ignore")

    # App
    app_env: str = "development"
    secret_key: str = "dev-secret-key-change-in-prod"
    access_token_expire_minutes: int = 1440

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/multiagent"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Neo4j
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "password123"

    # LLM
    llm_provider: str = "openai"
    openai_api_key: str = ""
    groq_api_key: str = ""
    gemini_api_key: str = ""
    ollama_base_url: str = "http://localhost:11434"
    default_model: str = "gpt-4o-mini"

    # Observability
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_host: str = "https://cloud.langfuse.com"

    # Storage
    vector_db_path: str = "./vector_db"
    output_dir: str = "./outputs"
    max_file_size_mb: int = 50


@lru_cache
def get_settings() -> Settings:
    return Settings()
