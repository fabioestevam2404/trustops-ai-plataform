from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.routers import assessments, auth, health, projects
from app.core.config import settings
from app.core.logging import configure_logging

configure_logging()

app = FastAPI(title="TrustOps AI Platform API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(assessments.router)

Instrumentator().instrument(app).expose(app)


@app.get("/")
def root() -> dict[str, str]:
    return {"service": "trustops-api", "env": settings.app_env}
