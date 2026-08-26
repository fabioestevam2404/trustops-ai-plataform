import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory


@dataclass
class GitleaksSecret:
    rule_id: str
    description: str
    filename: str
    line: int


@dataclass
class GitleaksResult:
    raw_report: str
    secrets: list[GitleaksSecret]


def run(repo_path: Path) -> GitleaksResult:
    with TemporaryDirectory(prefix="trustops-gitleaks-out-") as tmp:
        report_path = Path(tmp) / "report.json"

        # Gitleaks exits non-zero when secrets are found — expected, not caught here.
        subprocess.run(
            [
                "gitleaks",
                "detect",
                "--source",
                ".",
                "--no-git",
                "--report-format",
                "json",
                "--report-path",
                str(report_path),
            ],
            cwd=repo_path,
            capture_output=True,
            timeout=30,
            text=True,
        )

        raw_report = report_path.read_text(encoding="utf-8") if report_path.exists() else "[]"

    data = json.loads(raw_report) or []
    secrets = [
        GitleaksSecret(
            rule_id=item.get("RuleID", "UNKNOWN"),
            description=item.get("Description", ""),
            filename=item.get("File", ""),
            line=item.get("StartLine", 0),
        )
        for item in data
    ]
    return GitleaksResult(raw_report=raw_report, secrets=secrets)
