import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory


@dataclass
class PytestResult:
    raw_report: str
    raw_coverage: str
    passed: int
    failed: int
    total: int
    coverage_percent: float
    failed_tests: list[str]


def run(repo_path: Path, python_executable: Path | None = None) -> PytestResult:
    # When the target repo's own dependencies were installed into an isolated
    # venv (see dependency_installer.py), run pytest through that venv's
    # Python so imports resolve against the target's real dependency tree
    # instead of this platform's own environment. That path gets a much
    # longer timeout: importing a real ML stack (torch/transformers/...) for
    # the first time, or a real test suite actually exercising it, is
    # legitimately slow — a plain scan with no target deps installed stays
    # fast-failing at the original budget.
    if python_executable:
        pytest_command = [str(python_executable), "-m", "pytest"]
        timeout = 300
    else:
        pytest_command = ["pytest"]
        timeout = 90

    with TemporaryDirectory(prefix="trustops-pytest-out-") as tmp:
        report_path = Path(tmp) / "report.json"
        coverage_path = Path(tmp) / "coverage.json"

        # Non-zero exit (test failures) is an expected outcome, not caught here.
        subprocess.run(
            [
                *pytest_command,
                "--json-report",
                f"--json-report-file={report_path}",
                "--cov=.",
                f"--cov-report=json:{coverage_path}",
                "-q",
            ],
            cwd=repo_path,
            capture_output=True,
            timeout=timeout,
            text=True,
        )

        raw_report = report_path.read_text(encoding="utf-8") if report_path.exists() else "{}"
        raw_coverage = (
            coverage_path.read_text(encoding="utf-8") if coverage_path.exists() else "{}"
        )

    report = json.loads(raw_report)
    summary = report.get("summary", {})
    passed = summary.get("passed", 0)
    failed = summary.get("failed", 0) + summary.get("error", 0)
    total = summary.get("total", passed + failed)
    failed_tests = [
        test["nodeid"]
        for test in report.get("tests", [])
        if test.get("outcome") in ("failed", "error")
    ]

    coverage_data = json.loads(raw_coverage)
    coverage_percent = coverage_data.get("totals", {}).get("percent_covered", 0.0)

    return PytestResult(
        raw_report=raw_report,
        raw_coverage=raw_coverage,
        passed=passed,
        failed=failed,
        total=total,
        coverage_percent=round(coverage_percent, 2),
        failed_tests=failed_tests,
    )
