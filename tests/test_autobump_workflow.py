"""Contract tests for the autobump workflows: test on both Linux targets, merge, then publish."""

from __future__ import annotations

from typing import Any

from conftest import load_yaml

RECIPE_WORKFLOW: dict[str, Any] = load_yaml(".github/workflows/autobump-recipe.yml")
JOBS: dict[str, Any] = RECIPE_WORKFLOW["jobs"]


def run_scripts(job: dict[str, Any]) -> str:
    """Concatenate every ``run`` script of a job."""
    return "\n".join(step.get("run", "") for step in job["steps"])


def test_every_matrix_row_calls_the_recipe_workflow() -> None:
    """The scheduled workflow fans out one reusable-workflow call per recipe."""
    bump: dict[str, Any] = load_yaml(".github/workflows/autobump.yml")["jobs"]["bump"]
    assert bump["uses"] == "./.github/workflows/autobump-recipe.yml"
    assert {"recipe": "opencode", "source": "github:anomalyco/opencode"} in bump["strategy"]["matrix"]["include"]
    assert bump["permissions"] == {"actions": "write", "contents": "write", "pull-requests": "write"}


def test_one_pull_request_per_recipe_updated_in_place() -> None:
    """A rerun or a newer upstream release reuses autobump/<recipe> and closes older bump PRs."""
    script: str = run_scripts(JOBS["bump"])
    assert 'branch="autobump/$RECIPE"' in script
    assert 'gh pr edit "$pr"' in script
    assert "gh pr close" in script


def test_recipe_tests_run_natively_on_both_linux_targets() -> None:
    """The bump commit is built with its recipe tests on an x64 and an arm64 runner."""
    test: dict[str, Any] = JOBS["test"]
    assert test["strategy"]["matrix"]["include"] == [
        {"target": "linux-64", "os": "ubuntu-latest"},
        {"target": "linux-aarch64", "os": "ubuntu-24.04-arm"},
    ]
    assert test["steps"][0]["with"]["ref"] == "${{ needs.bump.outputs.sha }}"
    assert 'pixi run test-recipe "$RECIPE"' in run_scripts(test)


def test_merge_needs_the_tests_and_then_dispatches_the_publisher() -> None:
    """Merge exactly the tested commit, then start build.yml on main (a GITHUB_TOKEN merge starts no push run)."""
    merge: dict[str, Any] = JOBS["merge"]
    script: str = run_scripts(merge)
    assert merge["needs"] == ["bump", "test"]
    assert "if" not in merge, "merge must keep the default success() gate on the test matrix"
    assert '--match-head-commit "$SHA"' in script
    assert script.index("gh pr merge") < script.index("gh workflow run build.yml")
    assert "--ref main" in script
