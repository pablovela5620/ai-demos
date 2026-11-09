"""Contract tests for the package build workflow."""

from __future__ import annotations

import tomllib
from typing import Any

from conftest import ROOT, load_yaml

WORKFLOW: dict[str, Any] = load_yaml(".github/workflows/build.yml")
JOBS: dict[str, Any] = WORKFLOW["jobs"]


def step(job: str, name: str) -> dict[str, Any]:
    """Return the named step of a job."""
    return next(candidate for candidate in JOBS[job]["steps"] if candidate.get("name") == name)


def test_github_builds_use_linux_runners() -> None:
    """Use the fleet Mac mini for macOS instead of a hosted runner."""
    assert JOBS["build"]["strategy"]["matrix"]["include"] == [
        {"target": "linux-64", "os": "ubuntu-latest"},
        {"target": "linux-aarch64", "os": "ubuntu-24.04-arm"},
    ]


def test_main_publishes_on_push_and_on_dispatch() -> None:
    """Artifacts and the upload job follow main, so autobump's dispatch publishes like a push."""
    artifacts: dict[str, Any] = step("build", "Upload build artifacts")
    assert artifacts["if"] == "github.ref == 'refs/heads/main'"
    assert artifacts["with"]["retention-days"] == 1
    assert "github.ref == 'refs/heads/main' && needs.build.result == 'success'" in JOBS["upload"]["if"]


def test_prebuilt_macos_uses_the_existing_publisher() -> None:
    """Publish verified fleet builds with CI credentials, without a local login."""
    stage: dict[str, Any] = JOBS["stage-macos"]
    assert stage["runs-on"] == "ubuntu-latest"
    assert stage["permissions"] == {"contents": "read"}
    assert "stage-macos" in JOBS["upload"]["needs"]
    assert "needs.stage-macos.result == 'success'" in JOBS["upload"]["if"]
    verify: str = step("stage-macos", "Verify prebuilt macOS packages")["run"]
    assert "sha256sum --check" in verify
    assert "paseo claude-code codex opencode ruler" in verify
    stage_upload: dict[str, Any] = next(s for s in stage["steps"] if s.get("uses", "").startswith("actions/upload-artifact@"))
    assert stage_upload["with"]["path"] == "output/**/*.conda"


def test_build_logic_lives_in_pixi_task() -> None:
    """Keep the provider workflow as a thin wrapper around a local task."""
    with (ROOT / "pixi.toml").open("rb") as pixi_file:
        command: str = tomllib.load(pixi_file)["tasks"]["ci-build"]
    assert step("build", "Build packages")["run"] == "pixi run ci-build"
    assert "--target-platform=$TARGET_PLATFORM" in command
    assert "--noarch-build-platform=linux-64" in command


def test_upload_job_accepts_an_empty_build() -> None:
    """A run with no new package artifacts is successful, not an error."""
    for name in ("Upload packages to ai-demos channel", "Verify packages via pixi search"):
        assert "shopt -s globstar nullglob" in step("upload", name)["run"]
