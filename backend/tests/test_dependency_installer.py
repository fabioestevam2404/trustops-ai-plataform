from pathlib import Path

from app.infrastructure.scanners.dependency_installer import install


def test_install_with_uv_lock(uv_repo_path: Path) -> None:
    result = install(uv_repo_path)
    assert result.manager == "uv"
    assert result.installed is True
    assert result.python_executable is not None
    assert result.python_executable.exists()


def test_install_with_requirements_txt(pip_requirements_repo_path: Path) -> None:
    result = install(pip_requirements_repo_path)
    assert result.manager == "pip"
    assert result.installed is True
    assert result.python_executable is not None
    assert result.python_executable.exists()


def test_install_with_no_manifest_is_a_noop(clean_repo_path: Path) -> None:
    result = install(clean_repo_path)
    assert result.manager is None
    assert result.installed is False
    assert result.python_executable is None
