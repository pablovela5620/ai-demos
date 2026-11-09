"""Contract tests for recipes whose packaging choices are easy to undo by accident."""

from __future__ import annotations

from typing import Any

from conftest import ROOT, load_yaml


def test_openwiki_needs_only_node_at_runtime() -> None:
    """Install the public CLI and keep npm confined to package build time."""
    recipe: dict[str, Any] = load_yaml("recipes/openwiki/recipe.yaml")
    assert recipe["package"]["name"] == "openwiki"
    assert recipe["requirements"]["host"] == ["nodejs >=22"]
    assert recipe["requirements"]["run"] == ["nodejs >=22"]
    assert recipe["requirements"]["build"][0] == {"if": "linux", "then": ["${{ compiler('c') }}", "${{ compiler('cxx') }}"]}
    assert "openwiki" in recipe["tests"][0]["package_contents"]["bin"]
    script_tests: list[str] = recipe["tests"][1]["script"]
    assert "openwiki integrations list" in script_tests
    assert any("better-sqlite3" in command for command in script_tests), "prove the native SQLite binding loads"
    assert 'npm install --global --prefix "${PREFIX}"' in (ROOT / "recipes/openwiki/build.sh").read_text(encoding="utf-8")


def test_opencode_linux_arm64_uses_the_glibc_release_asset() -> None:
    """Reject the npm ARM64 binary, which requires a system musl loader."""
    recipe: str = (ROOT / "recipes/opencode/recipe.yaml").read_text(encoding="utf-8")
    build_script: str = (ROOT / "recipes/opencode/build.sh").read_text(encoding="utf-8")
    assert "opencode-linux-arm64.tar.gz" in recipe
    assert "registry.npmjs.org/opencode-linux-arm64" not in recipe
    assert 'file "${source_binary}"' in build_script
    assert "/lib/ld-linux-aarch64.so.1" in build_script
