from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import assessments, health, projects
from app.core.config import settings

app = FastAPI(title="TrustOps AI Platform API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(health.router)
app.include_router(projects.router)
app.include_router(assessments.router)


@app.get("/")
def root() -> dict[str, str]:
    return {"service": "trustops-api", "env": settings.app_env}
