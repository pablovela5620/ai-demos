#!/usr/bin/env python3
"""Bump a recipe to the newest upstream release: context.version, source sha256s, build.number.

Usage: autobump.py <recipe> <npm:PACKAGE | github:OWNER/REPO>

``rattler-build bump-recipe`` cannot do this: it fails with "No source URL found" on the
per-platform ``if/then`` sources (claude-code, codex, opencode) and does not detect npm releases.
"""

from __future__ import annotations

import hashlib
import os
import re
import sys
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from packaging.version import Version
from serde import serde
from serde.json import from_json

RECIPE_ROOT: Path = Path("recipes")
PRESERVE_MARKER: str = "autobump: preserve-build-number"
"""A build.number line with this comment keeps its value across version bumps."""

VERSION_LINE: re.Pattern[str] = re.compile(r'^(context:\n  version: )"([^"]+)"', re.MULTILINE)
VERSIONED_SOURCE: re.Pattern[str] = re.compile(
    r"^(\s*(?:- )?url: )(\S*\$\{\{ version \}\}\S*)(\n\s+sha256: )[0-9a-f]{64}", re.MULTILINE
)
BUILD_NUMBER_LINE: re.Pattern[str] = re.compile(r"^(build:\n  number: )\d+(.*)$", re.MULTILINE)
RELEASE_TAG: re.Pattern[str] = re.compile(r"^v\d+\.\d+\.\d+$")


@serde
@dataclass(frozen=True, slots=True)
class NpmLatest:
    """The fields we read from ``registry.npmjs.org/<package>/latest``."""

    version: str
    """Version behind the npm ``latest`` dist-tag."""


@serde
@dataclass(frozen=True, slots=True)
class GitHubRelease:
    """The fields we read from one entry of ``GET /repos/{repo}/releases``."""

    tag_name: str
    """Release tag, e.g. ``v2.2.6``."""
    draft: bool
    """Unpublished draft release."""
    prerelease: bool
    """Release marked as a prerelease."""


@dataclass(frozen=True, slots=True)
class Bump:
    """Result of one autobump check."""

    old_version: str
    """Version in the recipe before the check."""
    new_version: str
    """Version in the recipe after the check."""

    @property
    def changed(self) -> bool:
        """Whether the recipe was rewritten."""
        return self.new_version != self.old_version


def fetch(url: str) -> bytes:
    """Read a URL, sending a GitHub token for api.github.com when one is set."""
    headers: dict[str, str] = {"User-Agent": "ai-demos-autobump"}
    token: str | None = os.environ.get("GH_TOKEN")
    if token and url.startswith("https://api.github.com/"):
        headers["Authorization"] = f"Bearer {token}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=120) as response:
        return response.read()


def sha256_url(url: str) -> str:
    """Download a URL and return its sha256 hex digest."""
    return hashlib.sha256(fetch(url)).hexdigest()


def newest_release(releases: list[GitHubRelease]) -> str:
    """Return the highest published ``vX.Y.Z`` release version.

    GitHub's "latest" flag is not used: opencode keeps it on v1 while publishing v2, and the
    repository also tags other components (``process-daemon-v0.5.0``).
    """
    versions: list[Version] = [
        Version(release.tag_name)
        for release in releases
        if not release.draft and not release.prerelease and RELEASE_TAG.match(release.tag_name)
    ]
    if not versions:
        raise ValueError("no published vX.Y.Z release")
    return str(max(versions))


def latest_version(source: str) -> str:
    """Return the newest upstream version for ``npm:PACKAGE`` or ``github:OWNER/REPO``."""
    kind: str
    name: str
    kind, _, name = source.partition(":")
    if kind == "npm":
        package: str = urllib.parse.quote(name, safe="")
        return from_json(NpmLatest, fetch(f"https://registry.npmjs.org/{package}/latest")).version
    if kind == "github":
        body: bytes = fetch(f"https://api.github.com/repos/{name}/releases?per_page=100")
        return newest_release(from_json(list[GitHubRelease], body))
    raise ValueError(f"unknown version source {source!r}; expected npm:PACKAGE or github:OWNER/REPO")


def reset_build_number(match: re.Match[str]) -> str:
    """Reset build.number to 0 unless the line carries the preserve marker."""
    return match.group(0) if PRESERVE_MARKER in match.group(2) else f"{match.group(1)}0{match.group(2)}"


def bump_recipe(recipe: str, source: str) -> Bump:
    """Rewrite ``recipes/<recipe>/recipe.yaml`` to the newest upstream version, if it is newer.

    Every source URL that contains ``${{ version }}`` is rehashed for the new version.

    Args:
        recipe: Recipe directory name under ``recipes/``.
        source: Where to look up releases: ``npm:PACKAGE`` or ``github:OWNER/REPO``.

    Returns:
        The old and new versions; they are equal when the recipe is already current.
    """
    recipe_path: Path = RECIPE_ROOT / recipe / "recipe.yaml"
    text: str = recipe_path.read_text(encoding="utf-8")
    version_match: re.Match[str] | None = VERSION_LINE.search(text)
    if version_match is None:
        raise ValueError(f'{recipe_path}: expected the recipe to start with context:\\n  version: "..."')
    current: str = version_match.group(2)
    latest: str = latest_version(source)
    if Version(latest) <= Version(current):
        return Bump(old_version=current, new_version=current)

    def rehash(match: re.Match[str]) -> str:
        url: str = match.group(2).replace("${{ version }}", latest)
        print(f"hashing {url}")
        return f"{match.group(1)}{match.group(2)}{match.group(3)}{sha256_url(url)}"

    rehashed: tuple[str, int] = VERSIONED_SOURCE.subn(rehash, text)
    if rehashed[1] == 0:
        raise ValueError(f"{recipe_path}: no url with ${{{{ version }}}} followed by a sha256 line")
    renumbered: tuple[str, int] = BUILD_NUMBER_LINE.subn(reset_build_number, rehashed[0], count=1)
    if renumbered[1] == 0:
        raise ValueError(f"{recipe_path}: expected build:\\n  number: N")
    text = VERSION_LINE.sub(rf'\g<1>"{latest}"', renumbered[0], count=1)
    recipe_path.write_text(text, encoding="utf-8")
    return Bump(old_version=current, new_version=latest)


def main(argv: list[str]) -> int:
    """Bump one recipe and report the result to stdout and ``$GITHUB_OUTPUT``."""
    if len(argv) != 3:
        print(__doc__, file=sys.stderr)
        return 2
    bump: Bump = bump_recipe(argv[1], argv[2])
    print(f"{argv[1]}: {bump.old_version} -> {bump.new_version}")
    output_path: str | None = os.environ.get("GITHUB_OUTPUT")
    if output_path:
        with Path(output_path).open("a", encoding="utf-8") as output:
            output.write(f"old-version={bump.old_version}\nnew-version={bump.new_version}\nchanged={str(bump.changed).lower()}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
