from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    database_url: str = "postgresql+psycopg2://trustops:trustops@postgres:5432/trustops"
    redis_url: str = "redis://redis:6379/0"
    evidence_store_path: str = "/app/evidence/store"
    cors_origins: list[str] = ["http://localhost:5173"]
    # Dev-only default — every real deployment must override this via the
    # JWT_SECRET_KEY env var, or anyone can forge an admin token.
    jwt_secret_key: str = "dev-insecure-change-me"


settings = Settings()
