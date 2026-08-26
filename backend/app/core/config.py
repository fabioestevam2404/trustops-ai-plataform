from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    database_url: str = "postgresql+psycopg2://trustops:trustops@postgres:5432/trustops"
    redis_url: str = "redis://redis:6379/0"
    evidence_store_path: str = "/app/evidence/store"


settings = Settings()
