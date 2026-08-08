"""Contract tests for the package build workflow."""

from __future__ import annotations

import unittest
from pathlib import Path
from typing import Any
import tomllib

import yaml

WORKFLOW_PATH: Path = (
    Path(__file__).parent.parent / ".github" / "workflows" / "build.yml"
)
PIXI_PATH: Path = Path(__file__).parent.parent / "pixi.toml"


def load_workflow() -> dict[str, Any]:
    """Load the package build workflow."""
    workflow_text: str = WORKFLOW_PATH.read_text(encoding="utf-8")
    workflow: object = yaml.safe_load(workflow_text)
    if not isinstance(workflow, dict):
        raise TypeError("build workflow must be a mapping")
    return workflow


class BuildWorkflowTest(unittest.TestCase):
    """Verify package builds use free runners without retaining duplicate artifacts."""

    def test_standard_macos_builds_use_short_lived_push_artifacts(self) -> None:
        """Build macOS packages but retain artifacts only long enough to publish them."""
        workflow: dict[str, Any] = load_workflow()
        build_job: dict[str, Any] = workflow["jobs"]["build"]
        matrix_rows: list[dict[str, str]] = build_job["strategy"]["matrix"]["include"]
        upload_step: dict[str, Any] = next(
            step
            for step in build_job["steps"]
            if step.get("name") == "Upload build artifacts"
        )

        self.assertIn({"target": "osx-arm64", "os": "macos-latest"}, matrix_rows)
        self.assertEqual(
            upload_step["if"],
            "github.event_name == 'push' && steps.check.outputs.has-packages == 'true'",
        )
        self.assertEqual(upload_step["with"]["retention-days"], 1)

    def test_build_logic_lives_in_pixi_task(self) -> None:
        """Keep the provider workflow as a thin wrapper around a local task."""
        workflow: dict[str, Any] = load_workflow()
        build_steps: list[dict[str, Any]] = workflow["jobs"]["build"]["steps"]
        build_step: dict[str, Any] = next(
            step for step in build_steps if step.get("name") == "Build packages"
        )
        with PIXI_PATH.open("rb") as pixi_file:
            pixi: dict[str, Any] = tomllib.load(pixi_file)
        command: str = pixi["tasks"]["ci-build"]

        self.assertEqual(build_step["run"], "pixi run ci-build")
        self.assertIn("--target-platform=$TARGET_PLATFORM", command)
        self.assertIn("--noarch-build-platform=linux-64", command)


if __name__ == "__main__":
    unittest.main()
