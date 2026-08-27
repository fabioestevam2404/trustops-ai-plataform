from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProjectCreate(BaseModel):
    name: str
    repository_url: str


class ProjectUpdate(BaseModel):
    name: str | None = None
    repository_url: str | None = None


class ProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    repository_url: str
    created_at: datetime
    latest_trust_score: int | None = None
    latest_certification_level: str | None = None
