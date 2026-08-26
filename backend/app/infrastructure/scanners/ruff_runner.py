import json
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class RuffViolation:
    code: str
    message: str
    filename: str
    line: int


@dataclass
class RuffResult:
    raw_report: str
    violations: list[RuffViolation]


def run(repo_path: Path) -> RuffResult:
    # Ruff exits 1 when violations are found — expected outcome, not caught here.
    result = subprocess.run(
        ["ruff", "check", "--output-format=json", "."],
        cwd=repo_path,
        capture_output=True,
        timeout=30,
        text=True,
    )
    raw_report = result.stdout or "[]"
    data = json.loads(raw_report)
    violations = [
        RuffViolation(
            code=item.get("code") or "UNKNOWN",
            message=item.get("message", ""),
            filename=item.get("filename", ""),
            line=(item.get("location") or {}).get("row", 0),
        )
        for item in data
    ]
    return RuffResult(raw_report=raw_report, violations=violations)
