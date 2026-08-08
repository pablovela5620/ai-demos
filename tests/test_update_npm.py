"""Regression tests for versioned source updates."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from types import ModuleType
from unittest.mock import patch

ROOT: Path = Path(__file__).parent.parent
SCRIPT_PATH: Path = ROOT / ".github" / "scripts" / "update-npm.py"


def load_updater() -> ModuleType:
    """Load the updater whose filename is not a valid Python module name."""
    spec = importlib.util.spec_from_file_location("update_npm", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class UpdateNpmTest(unittest.TestCase):
    """Verify every source that changes with the package version is rehashed."""

    def test_update_rehashes_npm_and_github_sources(self) -> None:
        """A mixed-source recipe must not keep a stale GitHub release hash."""
        updater: ModuleType = load_updater()
        recipe_text: str = """context:
  version: "1.0.0"
source:
  - if: target_platform == "linux-64"
    then:
      url: https://registry.npmjs.org/tool/-/tool-${{ version }}.tgz
      sha256: aaaa
  - if: target_platform == "linux-aarch64"
    then:
      url: https://github.com/example/tool/releases/download/v${{ version }}/tool.tar.gz
      sha256: bbbb
build:
  number: 2
"""
        with tempfile.TemporaryDirectory() as temporary_directory:
            recipe_root = Path(temporary_directory)
            recipe_path = recipe_root / "tool" / "recipe.yaml"
            recipe_path.parent.mkdir()
            recipe_path.write_text(recipe_text, encoding="utf-8")
            hashes: dict[str, str] = {
                "https://registry.npmjs.org/tool/-/tool-1.1.0.tgz": "1" * 64,
                "https://github.com/example/tool/releases/download/v1.1.0/tool.tar.gz": "2" * 64,
            }

            with (
                patch.object(updater, "RECIPE_ROOT", recipe_root),
                patch.object(updater, "fetch_latest_version", return_value="1.1.0"),
                patch.object(updater, "sha256_url", side_effect=hashes.__getitem__) as sha,
            ):
                changed: bool = updater.update_recipe("tool", "tool")

            updated: str = recipe_path.read_text(encoding="utf-8")
            self.assertTrue(changed)
            self.assertEqual({call.args[0] for call in sha.call_args_list}, set(hashes))
            self.assertIn('version: "1.1.0"', updated)
            self.assertIn("sha256: " + "1" * 64, updated)
            self.assertIn("sha256: " + "2" * 64, updated)
            self.assertIn("number: 0", updated)


if __name__ == "__main__":
    unittest.main()
