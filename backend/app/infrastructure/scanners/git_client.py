import subprocess
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path


class GitCloneError(Exception):
    pass


@dataclass
class ClonedRepository:
    path: Path
    resolved_ref: str


@contextmanager
def clone_repository(url: str, ref: str | None) -> Iterator[ClonedRepository]:
    with tempfile.TemporaryDirectory(prefix="trustops-scan-") as tmp:
        repo_path = Path(tmp)
        try:
            subprocess.run(
                ["git", "clone", "--quiet", url, str(repo_path)],
                check=True,
                capture_output=True,
                timeout=30,
                text=True,
            )
            if ref:
                subprocess.run(
                    ["git", "-C", str(repo_path), "checkout", "--quiet", ref],
                    check=True,
                    capture_output=True,
                    timeout=30,
                    text=True,
                )
            sha = subprocess.run(
                ["git", "-C", str(repo_path), "rev-parse", "--short", "HEAD"],
                check=True,
                capture_output=True,
                timeout=10,
                text=True,
            ).stdout.strip()
        except subprocess.CalledProcessError as exc:
            raise GitCloneError(exc.stderr or str(exc)) from exc
        except subprocess.TimeoutExpired as exc:
            raise GitCloneError(f"git operation timed out: {exc}") from exc

        yield ClonedRepository(path=repo_path, resolved_ref=sha)
