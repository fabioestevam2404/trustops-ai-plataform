import json
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class TrivyFinding:
    kind: str  # "secret" | "misconfig"
    rule_id: str
    severity: str
    message: str
    filename: str


@dataclass
class TrivyResult:
    raw_report: str
    findings: list[TrivyFinding]


def run(repo_path: Path) -> TrivyResult:
    # Trivy exits non-zero when findings are reported — expected, not caught here.
    result = subprocess.run(
        ["trivy", "fs", "--scanners", "secret,misconfig", "--format", "json", "--quiet", "."],
        cwd=repo_path,
        capture_output=True,
        timeout=60,
        text=True,
    )
    raw_report = result.stdout or "{}"
    data = json.loads(raw_report)

    findings: list[TrivyFinding] = []
    for target in data.get("Results", []) or []:
        filename = target.get("Target", "")
        for secret in target.get("Secrets", []) or []:
            findings.append(
                TrivyFinding(
                    kind="secret",
                    rule_id=secret.get("RuleID", "UNKNOWN"),
                    severity=secret.get("Severity", "CRITICAL"),
                    message=secret.get("Title", ""),
                    filename=filename,
                )
            )
        for misconfig in target.get("Misconfigurations", []) or []:
            findings.append(
                TrivyFinding(
                    kind="misconfig",
                    rule_id=misconfig.get("ID", "UNKNOWN"),
                    severity=misconfig.get("Severity", "MEDIUM"),
                    message=misconfig.get("Title", ""),
                    filename=filename,
                )
            )
    return TrivyResult(raw_report=raw_report, findings=findings)
