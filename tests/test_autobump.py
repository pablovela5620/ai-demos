"""Tests for the recipe updater (.github/scripts/autobump.py)."""

from __future__ import annotations

from pathlib import Path
from types import ModuleType

import pytest
from conftest import ROOT, load_script, load_yaml

autobump: ModuleType = load_script("autobump")


def mixed_sources(build_number: str) -> str:
    """A recipe with a per-platform npm source, a GitHub source, and an unversioned source."""
    return f"""context:
  version: "1.0.0"
source:
  - if: target_platform == "linux-64"
    then:
      url: https://registry.npmjs.org/tool/-/tool-${{{{ version }}}}.tgz
      sha256: {"a" * 64}
  - url: https://github.com/example/tool/releases/download/v${{{{ version }}}}/tool.tar.gz
    sha256: {"b" * 64}
  - url: https://example.com/unversioned/LICENSE
    sha256: {"c" * 64}
build:
  number: {build_number}
"""


def write_recipe(root: Path, text: str) -> Path:
    """Write ``root/tool/recipe.yaml`` and return its path."""
    path: Path = root / "tool" / "recipe.yaml"
    path.parent.mkdir()
    path.write_text(text, encoding="utf-8")
    return path


@pytest.fixture
def recipe_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point the updater at a temporary recipes/ directory and fake every download."""
    monkeypatch.setattr(autobump, "RECIPE_ROOT", tmp_path)
    monkeypatch.setattr(autobump, "sha256_url", lambda url: "1" * 64 if "registry" in url else "2" * 64)
    return tmp_path


def test_bump_rehashes_every_versioned_source(recipe_root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Every ${{ version }} URL gets a new hash; unversioned sources and their hashes stay."""
    path: Path = write_recipe(recipe_root, mixed_sources("2"))
    monkeypatch.setattr(autobump, "latest_version", lambda source: "1.1.0")

    bump = autobump.bump_recipe("tool", "npm:tool")

    updated: str = path.read_text(encoding="utf-8")
    assert (bump.old_version, bump.new_version, bump.changed) == ("1.0.0", "1.1.0", True)
    assert 'version: "1.1.0"' in updated
    assert "sha256: " + "1" * 64 in updated
    assert "sha256: " + "2" * 64 in updated
    assert "sha256: " + "c" * 64 in updated
    assert "number: 0" in updated


def test_bump_keeps_a_marked_build_number(recipe_root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A recipe whose build lane was corrected keeps its build number across versions."""
    path: Path = write_recipe(recipe_root, mixed_sources("1  # autobump: preserve-build-number"))
    monkeypatch.setattr(autobump, "latest_version", lambda source: "1.1.0")

    autobump.bump_recipe("tool", "npm:tool")

    assert "number: 1  # autobump: preserve-build-number" in path.read_text(encoding="utf-8")


@pytest.mark.parametrize("upstream", ["1.0.0", "0.9.9"])
def test_bump_never_rewrites_to_an_equal_or_older_version(
    recipe_root: Path, monkeypatch: pytest.MonkeyPatch, upstream: str
) -> None:
    """A registry that lags the recipe (opencode-ai on npm stayed at v1) must not downgrade it."""
    original: str = mixed_sources("2")
    path: Path = write_recipe(recipe_root, original)
    monkeypatch.setattr(autobump, "latest_version", lambda source: upstream)

    bump = autobump.bump_recipe("tool", "npm:tool")

    assert not bump.changed
    assert path.read_text(encoding="utf-8") == original


def test_newest_release_ignores_latest_flag_prereleases_and_other_components() -> None:
    """Pick the highest published vX.Y.Z tag, as opencode tags other components in the same repo."""
    release = autobump.GitHubRelease
    releases: list[autobump.GitHubRelease] = [
        release(tag_name="v2.3.0", draft=False, prerelease=True),
        release(tag_name="process-daemon-v0.5.0", draft=False, prerelease=False),
        release(tag_name="v2.2.6", draft=False, prerelease=False),
        release(tag_name="v2.10.0", draft=True, prerelease=False),
        release(tag_name="v1.19.5", draft=False, prerelease=False),
    ]
    assert autobump.newest_release(releases) == "2.2.6"


def test_every_autobump_recipe_matches_the_updater_patterns() -> None:
    """Each recipe in the autobump matrix has the layout the updater rewrites."""
    matrix: list[dict[str, str]] = load_yaml(".github/workflows/autobump.yml")["jobs"]["bump"]["strategy"]["matrix"]["include"]
    for row in matrix:
        text: str = (ROOT / "recipes" / row["recipe"] / "recipe.yaml").read_text(encoding="utf-8")
        assert autobump.VERSION_LINE.search(text), row["recipe"]
        assert autobump.VERSIONED_SOURCE.search(text), row["recipe"]
        assert autobump.BUILD_NUMBER_LINE.search(text), row["recipe"]
        assert row["source"].partition(":")[0] in {"npm", "github"}, row["recipe"]
