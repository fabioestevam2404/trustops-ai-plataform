import json
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class BanditIssue:
    severity: str
    test_id: str
    message: str
    filename: str
    line: int


@dataclass
class BanditResult:
    raw_report: str
    issues: list[BanditIssue]


def run(repo_path: Path) -> BanditResult:
    # Bandit exits non-zero when issues are found — expected outcome, not caught here.
    result = subprocess.run(
        ["bandit", "-r", ".", "-f", "json", "-q"],
        cwd=repo_path,
        capture_output=True,
        timeout=30,
        text=True,
    )
    raw_report = result.stdout or "{}"
    data = json.loads(raw_report)
    issues = [
        BanditIssue(
            severity=item.get("issue_severity", "LOW"),
            test_id=item.get("test_id", "UNKNOWN"),
            message=item.get("issue_text", ""),
            filename=item.get("filename", ""),
            line=item.get("line_number", 0),
        )
        for item in data.get("results", [])
    ]
    return BanditResult(raw_report=raw_report, issues=issues)
