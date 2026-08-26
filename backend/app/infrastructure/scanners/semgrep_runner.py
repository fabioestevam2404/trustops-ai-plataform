import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

_RULES_PATH = Path(__file__).parent / "semgrep_rules.yml"


@dataclass
class SemgrepFinding:
    check_id: str
    severity: str
    message: str
    filename: str
    line: int


@dataclass
class SemgrepResult:
    raw_report: str
    findings: list[SemgrepFinding]


def run(repo_path: Path) -> SemgrepResult:
    # Semgrep exits non-zero when findings are reported — expected, not caught here.
    result = subprocess.run(
        ["semgrep", "scan", "--config", str(_RULES_PATH), "--json", "--quiet", "."],
        cwd=repo_path,
        capture_output=True,
        timeout=45,
        text=True,
    )
    raw_report = result.stdout or "{}"
    data = json.loads(raw_report)
    findings = [
        SemgrepFinding(
            check_id=item.get("check_id", "UNKNOWN"),
            severity=(item.get("extra") or {}).get("severity", "INFO"),
            message=(item.get("extra") or {}).get("message", ""),
            filename=item.get("path", ""),
            line=(item.get("start") or {}).get("line", 0),
        )
        for item in data.get("results", [])
    ]
    return SemgrepResult(raw_report=raw_report, findings=findings)
