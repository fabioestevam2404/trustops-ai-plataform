from pathlib import Path

from app.core.config import settings


def _path_for(assessment_id: str, tool: str) -> Path:
    return Path(settings.evidence_store_path) / assessment_id / f"{tool}.json"


def save(assessment_id: str, tool: str, content: str) -> Path:
    path = _path_for(assessment_id, tool)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def read(assessment_id: str, tool: str) -> str | None:
    path = _path_for(assessment_id, tool)
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")
