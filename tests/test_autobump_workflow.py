"""Contract tests for the npm autobump workflow."""

from __future__ import annotations

import unittest
from pathlib import Path
from typing import Any

import yaml

WORKFLOW_PATH: Path = Path(__file__).parent.parent / ".github" / "workflows" / "autobump.yml"


def load_workflow() -> dict[str, Any]:
    """Load the autobump workflow."""
    workflow_text: str = WORKFLOW_PATH.read_text(encoding="utf-8")
    workflow: object = yaml.safe_load(workflow_text)
    if not isinstance(workflow, dict):
        raise TypeError("autobump workflow must be a mapping")
    return workflow


class AutobumpWorkflowTest(unittest.TestCase):
    """Verify a failed PR creation can be retried safely."""

    def test_pr_step_reuses_branch_and_existing_pull_request(self) -> None:
        """A rerun must update its deterministic branch instead of failing to push."""
        workflow: dict[str, Any] = load_workflow()
        steps: list[dict[str, Any]] = workflow["jobs"]["bump"]["steps"]
        pr_step: dict[str, Any] = next(
            step for step in steps if step.get("name") == "Create Pull Request"
        )
        script: str = pr_step["run"]

        self.assertIn('git switch -C "$branch"', script)
        self.assertIn(
            'git push --force-with-lease --set-upstream origin "$branch"', script
        )
        self.assertIn('gh pr list --head "$branch" --state open', script)
        self.assertIn('gh pr edit "$existing_pr"', script)


if __name__ == "__main__":
    unittest.main()
