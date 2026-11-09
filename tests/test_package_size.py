"""Tests for the prefix.dev package-size check."""

from __future__ import annotations

from pathlib import Path
from types import ModuleType
from typing import Any

from conftest import load_script, load_yaml

check: ModuleType = load_script("check-package-size")


def sparse_file(path: Path, size: int) -> None:
    """Create a file of ``size`` bytes without writing them (sparse on Linux and macOS)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as handle:
        handle.truncate(size)


def test_limit_is_one_gib() -> None:
    """The limit matches prefix.dev's 413 message."""
    assert check.MAX_PACKAGE_BYTES == 1024**3


def test_flags_only_packages_over_the_limit(tmp_path: Path) -> None:
    """A file just over 1 GiB fails; one at exactly 1 GiB and non-package files pass."""
    sparse_file(tmp_path / "linux-64" / "big-1.0-h0_0.conda", 1024**3 + 1)
    sparse_file(tmp_path / "linux-64" / "edge-1.0-h0_0.conda", 1024**3)
    sparse_file(tmp_path / "noarch" / "old-1.0-0.tar.bz2", 1024**3 + 2)
    sparse_file(tmp_path / "linux-64" / "notes.txt", 1024**3 + 3)
    assert [path.name for path, _ in check.oversized_packages(tmp_path)] == ["old-1.0-0.tar.bz2", "big-1.0-h0_0.conda"]
    assert check.main(["check", str(tmp_path)]) == 1


def test_passes_without_output(tmp_path: Path) -> None:
    """A build that produced nothing has nothing to check."""
    assert check.main(["check", str(tmp_path / "missing")]) == 0


def test_build_job_checks_sizes_before_artifacts() -> None:
    """The check runs after the build steps and before artifacts are kept, on PRs too."""
    steps: list[dict[str, Any]] = load_yaml(".github/workflows/build.yml")["jobs"]["build"]["steps"]
    names: list[str] = [step.get("name", "") for step in steps]
    position: int = names.index("Check package sizes")
    assert names.index("Build packages") < position < names.index("Upload build artifacts")
    assert "if" not in steps[position]
    assert steps[position]["run"] == "pixi run check-package-size"
