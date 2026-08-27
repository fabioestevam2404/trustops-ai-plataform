import os
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

_INSTALL_TIMEOUT = 300


@dataclass
class DependencyInstallResult:
    installed: bool
    manager: str | None
    python_executable: Path | None
    venv_dir: Path | None
    raw_log: str


def _venv_python(venv_dir: Path) -> Path:
    candidate = venv_dir / "bin" / "python"
    return candidate if candidate.exists() else venv_dir / "Scripts" / "python.exe"


def _run(
    command: list[str], cwd: Path, env: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        capture_output=True,
        timeout=_INSTALL_TIMEOUT,
        text=True,
        env=env,
    )


def _new_venv_dir() -> Path:
    """Deliberately outside repo_path: bandit/semgrep/trivy/gitleaks all walk
    repo_path recursively, and a venv nested inside it would put every
    installed third-party package's source (torch, transformers, ...) in
    front of those scanners as if it were the target's own code — wrong
    attribution, and large enough to blow their timeouts outright (observed:
    bandit/trivy silently timing out and truncating their own findings)."""
    return Path(tempfile.mkdtemp(prefix="trustops-venv-"))


def _uv_venv(repo_path: Path) -> tuple[Path, Path]:
    """`uv venv` (unlike stdlib venv.create(with_pip=True)) doesn't bootstrap
    pip via ensurepip — it's a bare, near-instant venv creation. Every install
    path below uses `uv pip install --python <exe>` afterward, which works
    against any venv without needing pip physically present in it."""
    venv_dir = _new_venv_dir()
    _run(["uv", "venv", str(venv_dir)], repo_path)
    return venv_dir, _venv_python(venv_dir)


def _install_with_uv(repo_path: Path) -> DependencyInstallResult:
    venv_dir = _new_venv_dir()
    # `uv sync` creates/looks for `.venv` next to pyproject.toml by default;
    # this env var is the supported way to redirect it elsewhere.
    env = os.environ | {"UV_PROJECT_ENVIRONMENT": str(venv_dir)}
    result = _run(["uv", "sync", "--all-groups"], repo_path, env=env)
    python_executable = _venv_python(venv_dir)
    installed = result.returncode == 0 and python_executable.exists()
    return DependencyInstallResult(
        installed=installed,
        manager="uv",
        python_executable=python_executable if installed else None,
        venv_dir=venv_dir,
        raw_log=f"$ uv sync --all-groups\n{result.stdout}\n{result.stderr}",
    )


def _install_with_pip_requirements(
    repo_path: Path, requirement_files: list[Path]
) -> DependencyInstallResult:
    venv_dir, python_executable = _uv_venv(repo_path)

    logs = []
    ok = True
    for req_file in requirement_files:
        result = _run(
            ["uv", "pip", "install", "--python", str(python_executable), "-r", req_file.name],
            repo_path,
        )
        logs.append(f"$ uv pip install -r {req_file.name}\n{result.stdout}\n{result.stderr}")
        if result.returncode != 0:
            ok = False
            break

    return DependencyInstallResult(
        installed=ok,
        manager="pip",
        python_executable=python_executable if ok else None,
        venv_dir=venv_dir,
        raw_log="\n".join(logs),
    )


def _install_with_pip_pyproject(repo_path: Path) -> DependencyInstallResult:
    venv_dir, python_executable = _uv_venv(repo_path)

    result = _run(
        ["uv", "pip", "install", "--python", str(python_executable), "."], repo_path
    )
    ok = result.returncode == 0
    return DependencyInstallResult(
        installed=ok,
        manager="pip",
        python_executable=python_executable if ok else None,
        venv_dir=venv_dir,
        raw_log=f"$ uv pip install .\n{result.stdout}\n{result.stderr}",
    )


def _ensure_reporting_plugins(
    repo_path: Path, result: DependencyInstallResult
) -> DependencyInstallResult:
    """The target repo's own deps may not include the plugins we need to get a
    machine-readable pytest report (pytest-cov, pytest-json-report) — install
    them into the same venv regardless of what the target declared."""
    if not (result.installed and result.python_executable):
        return result
    plugins = _run(
        [
            "uv",
            "pip",
            "install",
            "--python",
            str(result.python_executable),
            "pytest-cov",
            "pytest-json-report",
        ],
        repo_path,
    )
    if plugins.returncode != 0:
        return DependencyInstallResult(
            installed=False,
            manager=result.manager,
            python_executable=None,
            venv_dir=result.venv_dir,
            raw_log=(
                result.raw_log
                + f"\n$ uv pip install pytest-cov pytest-json-report\n{plugins.stderr}"
            ),
        )
    return result


def install(repo_path: Path) -> DependencyInstallResult:
    """Best-effort install of the target repo's own dependencies, isolated in a
    venv created outside repo_path (see _new_venv_dir). Never raises — a
    failure or timeout here just means the caller falls back to running
    pytest without the target's dependencies, same as before this existed.
    Callers own cleanup of the returned venv_dir once they're done with it."""
    try:
        if (repo_path / "uv.lock").exists():
            return _ensure_reporting_plugins(repo_path, _install_with_uv(repo_path))

        requirement_files = [
            f
            for f in (repo_path / "requirements.txt", repo_path / "requirements-dev.txt")
            if f.exists()
        ]
        if requirement_files:
            return _ensure_reporting_plugins(
                repo_path, _install_with_pip_requirements(repo_path, requirement_files)
            )

        if (repo_path / "pyproject.toml").exists():
            return _ensure_reporting_plugins(repo_path, _install_with_pip_pyproject(repo_path))

    except Exception as exc:  # noqa: BLE001 - isolate from the rest of the assessment
        return DependencyInstallResult(
            installed=False,
            manager=None,
            python_executable=None,
            venv_dir=None,
            raw_log=f"error: {exc}",
        )

    return DependencyInstallResult(
        installed=False,
        manager=None,
        python_executable=None,
        venv_dir=None,
        raw_log="no uv.lock, requirements.txt, or pyproject.toml found — nothing to install",
    )
