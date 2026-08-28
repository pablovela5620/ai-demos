"""Contract tests for the OpenWiki conda package."""

from __future__ import annotations

import unittest
from pathlib import Path
from typing import Any

import yaml

ROOT: Path = Path(__file__).parent.parent
RECIPE_PATH: Path = ROOT / "recipes" / "openwiki" / "recipe.yaml"
BUILD_SCRIPT_PATH: Path = ROOT / "recipes" / "openwiki" / "build.sh"


class OpenWikiRecipeTest(unittest.TestCase):
    """Verify fleet users get a tested CLI without running npm themselves."""

    def test_recipe_exposes_openwiki_with_only_node_as_a_runtime_dependency(self) -> None:
        """Install the public CLI seam and keep npm confined to package build time."""
        recipe_object: object = yaml.safe_load(RECIPE_PATH.read_text(encoding="utf-8"))
        if not isinstance(recipe_object, dict):
            self.fail("OpenWiki recipe must be a mapping")
        recipe: dict[str, Any] = recipe_object

        self.assertEqual(recipe["package"]["name"], "openwiki")
        self.assertEqual(recipe["requirements"]["host"], ["nodejs >=22"])
        self.assertEqual(recipe["requirements"]["run"], ["nodejs >=22"])
        self.assertEqual(
            recipe["requirements"]["build"][0],
            {
                "if": "linux",
                "then": ["${{ compiler('c') }}", "${{ compiler('cxx') }}"],
            },
        )
        self.assertIn("openwiki", recipe["tests"][0]["package_contents"]["bin"])
        script_tests: list[str] = recipe["tests"][1]["script"]
        self.assertIn("openwiki integrations list", script_tests)
        self.assertTrue(
            any("better-sqlite3" in command for command in script_tests),
            "recipe must prove OpenWiki's native SQLite binding loads",
        )

        build_script: str = BUILD_SCRIPT_PATH.read_text(encoding="utf-8")
        self.assertIn('npm install --global --prefix "${PREFIX}"', build_script)


if __name__ == "__main__":
    unittest.main()
