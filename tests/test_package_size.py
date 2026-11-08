"""Tests for the prefix.dev package-size check."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path
from types import ModuleType
from typing import Any

import yaml

ROOT: Path = Path(__file__).parent.parent
SCRIPT_PATH: Path = ROOT / ".github" / "scripts" / "check-package-size.py"
WORKFLOW_PATH: Path = ROOT / ".github" / "workflows" / "build.yml"


def load_script() -> ModuleType:
    """Import the check script (its file name has dashes)."""
    spec = importlib.util.spec_from_file_location("check_package_size", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module: ModuleType = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sparse_file(path: Path, size: int) -> None:
    """Create a file of ``size`` bytes without writing them (sparse on Linux and macOS)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as handle:
        handle.truncate(size)


class PackageSizeTest(unittest.TestCase):
    """prefix.dev rejects package files over 1 GiB; the build must catch them first."""

    def test_limit_is_one_gib(self) -> None:
        """The limit matches prefix.dev's 413 message."""
        self.assertEqual(load_script().MAX_PACKAGE_BYTES, 1024**3)

    def test_flags_only_packages_over_the_limit(self) -> None:
        """A file just over 1 GiB fails; one at exactly 1 GiB and non-package files pass."""
        script: ModuleType = load_script()
        with tempfile.TemporaryDirectory() as tmp:
            out: Path = Path(tmp)
            sparse_file(out / "linux-64" / "big-1.0-h0_0.conda", 1024**3 + 1)
            sparse_file(out / "linux-64" / "edge-1.0-h0_0.conda", 1024**3)
            sparse_file(out / "noarch" / "old-1.0-0.tar.bz2", 1024**3 + 2)
            sparse_file(out / "linux-64" / "notes.txt", 1024**3 + 3)
            names: list[str] = [path.name for path, _ in script.oversized_packages(out)]
            self.assertEqual(names, ["old-1.0-0.tar.bz2", "big-1.0-h0_0.conda"])
            self.assertEqual(script.main(["check", str(out)]), 1)

    def test_passes_without_output(self) -> None:
        """A build that produced nothing has nothing to check."""
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(load_script().main(["check", str(Path(tmp) / "missing")]), 0)

    def test_build_job_checks_sizes_before_artifacts(self) -> None:
        """The check runs after the build steps and before artifacts are kept, on PRs too."""
        workflow: dict[str, Any] = yaml.safe_load(WORKFLOW_PATH.read_text(encoding="utf-8"))
        names: list[str] = [step.get("name", "") for step in workflow["jobs"]["build"]["steps"]]
        check: int = names.index("Check package sizes")
        self.assertGreater(check, names.index("Build packages"))
        self.assertLess(check, names.index("Upload build artifacts"))
        step: dict[str, Any] = workflow["jobs"]["build"]["steps"][check]
        self.assertNotIn("if", step)
        self.assertEqual(step["run"], "pixi run check-package-size")


if __name__ == "__main__":
    unittest.main()
