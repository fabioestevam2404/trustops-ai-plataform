from fastapi import FastAPI

from app.api.routers import health, projects
from app.core.config import settings

app = FastAPI(title="TrustOps AI Platform API")
app.include_router(health.router)
app.include_router(projects.router)


@app.get("/")
def root() -> dict[str, str]:
    return {"service": "trustops-api", "env": settings.app_env}
