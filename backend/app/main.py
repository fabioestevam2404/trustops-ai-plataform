from fastapi import FastAPI

from app.core.config import settings

app = FastAPI(title="TrustOps AI Platform API")


@app.get("/")
def root() -> dict[str, str]:
    return {"service": "trustops-api", "env": settings.app_env}
