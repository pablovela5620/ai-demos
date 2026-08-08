#!/usr/bin/env python3
"""Bump npm-backed rattler-build recipes without parsing YAML."""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import NoReturn


REGISTRY_HOST: str = "registry.npmjs.org"
RECIPE_ROOT: Path = Path("recipes")
CHUNK_SIZE: int = 1024 * 1024


@dataclass(frozen=True, slots=True)
class VersionLine:
    """Location and formatting for the recipe context version."""

    line_index: int
    """Line index containing context.version."""
    prefix: str
    """Text before the version value."""
    quote: str
    """Quote character used around the version, if any."""
    value: str
    """Parsed version value."""
    suffix: str
    """Text after the version value, excluding the line ending."""
    newline: str
    """Original line ending."""


@dataclass(frozen=True, slots=True)
class SourceUrlLine:
    """Location and formatting for a registry source URL."""

    line_index: int
    """Line index containing source.url."""
    prefix: str
    """Text before the URL value."""
    quote: str
    """Quote character used around the URL, if any."""
    value: str
    """Parsed URL value."""
    suffix: str
    """Text after the URL value, excluding the line ending."""
    newline: str
    """Original line ending."""
    sha256_line_index: int
    """Line index of the adjacent sha256 entry."""


@dataclass(frozen=True, slots=True)
class Sha256Line:
    """Location and formatting for a sha256 line."""

    prefix: str
    """Text before the sha256 value."""
    value: str
    """Parsed sha256 value."""
    suffix: str
    """Text after the sha256 value, excluding the line ending."""
    newline: str
    """Original line ending."""


@dataclass(frozen=True, slots=True)
class BuildNumberLine:
    """Location and formatting for build.number."""

    line_index: int
    """Line index containing build.number."""
    prefix: str
    """Text before the build number value."""
    value: str
    """Parsed build number value."""
    suffix: str
    """Text after the build number value, excluding the line ending."""
    newline: str
    """Original line ending."""


def usage() -> NoReturn:
    """Print command usage and exit."""
    print("Usage: update-npm.py <recipe-name> <npm-package>", file=sys.stderr)
    raise SystemExit(2)


def split_line_ending(line: str) -> tuple[str, str]:
    """Split a text line into body and original line ending."""
    if line.endswith("\r\n"):
        return line[:-2], "\r\n"
    if line.endswith("\n"):
        return line[:-1], "\n"
    return line, ""


def top_level_key(line: str) -> str | None:
    """Return the top-level YAML-like key for a line, if present."""
    body: str
    body, _newline = split_line_ending(line)
    match: re.Match[str] | None = re.match(r"^([A-Za-z0-9_-]+):(?:\s|$)", body)
    if match is None:
        return None
    return match.group(1)


def find_context_version(lines: list[str]) -> VersionLine:
    """Find context.version in recipe text."""
    in_context: bool = False
    line_index: int
    line: str
    for line_index, line in enumerate(lines):
        key: str | None = top_level_key(line)
        if key == "context":
            in_context = True
            continue
        if in_context and key is not None:
            break
        if not in_context:
            continue

        body: str
        newline: str
        body, newline = split_line_ending(line)
        match: re.Match[str] | None = re.match(
            r"^(\s+version:\s*)(?:(['\"])(.*?)\2|([^#\s]+))(\s*(?:#.*)?)$",
            body,
        )
        if match is None:
            continue

        quote: str = match.group(2) or ""
        value: str = match.group(3) if quote else match.group(4)
        suffix: str = match.group(5)
        return VersionLine(
            line_index=line_index,
            prefix=match.group(1),
            quote=quote,
            value=value,
            suffix=suffix,
            newline=newline,
        )

    raise ValueError("Could not find context.version in recipe")


def parse_url_line(line: str) -> tuple[str, str, str, str, str] | None:
    """Parse a URL line while preserving formatting."""
    body: str
    newline: str
    body, newline = split_line_ending(line)
    match: re.Match[str] | None = re.match(r"^(\s*url:\s*)(.+?)(\s*)$", body)
    if match is None:
        return None

    raw_value: str = match.group(2).strip()
    suffix: str = match.group(3)
    quote: str = ""
    value: str = raw_value
    if len(raw_value) >= 2 and raw_value[0] in {"'", '"'} and raw_value[-1] == raw_value[0]:
        quote = raw_value[0]
        value = raw_value[1:-1]

    return match.group(1), quote, value, suffix, newline


def parse_sha256_line(line: str) -> Sha256Line | None:
    """Parse a sha256 line while preserving formatting."""
    body: str
    newline: str
    body, newline = split_line_ending(line)
    match: re.Match[str] | None = re.match(r"^(\s*sha256:\s*)([0-9a-fA-F]+)(\s*(?:#.*)?)$", body)
    if match is None:
        return None
    return Sha256Line(
        prefix=match.group(1),
        value=match.group(2),
        suffix=match.group(3),
        newline=newline,
    )


def find_adjacent_sha256_line(lines: list[str], url_line_index: int) -> int:
    """Find the sha256 line following a source URL before another URL appears."""
    next_index: int
    for next_index in range(url_line_index + 1, len(lines)):
        next_line: str = lines[next_index]
        if parse_url_line(next_line) is not None:
            break
        if top_level_key(next_line) is not None:
            break
        if parse_sha256_line(next_line) is not None:
            return next_index

    line_number: int = url_line_index + 1
    raise ValueError(f"Could not find adjacent sha256 line after source URL on line {line_number}")


def find_source_urls(lines: list[str]) -> list[SourceUrlLine]:
    """Find source URLs with adjacent sha256 entries."""
    source_lines: list[SourceUrlLine] = []
    line_index: int
    line: str
    for line_index, line in enumerate(lines):
        parsed_url: tuple[str, str, str, str, str] | None = parse_url_line(line)
        if parsed_url is None:
            continue

        prefix: str
        quote: str
        value: str
        suffix: str
        newline: str
        prefix, quote, value, suffix, newline = parsed_url
        sha256_line_index: int = find_adjacent_sha256_line(lines, line_index)
        source_lines.append(
            SourceUrlLine(
                line_index=line_index,
                prefix=prefix,
                quote=quote,
                value=value,
                suffix=suffix,
                newline=newline,
                sha256_line_index=sha256_line_index,
            )
        )

    return source_lines


def find_build_number(lines: list[str]) -> BuildNumberLine:
    """Find build.number in recipe text."""
    in_build: bool = False
    line_index: int
    line: str
    for line_index, line in enumerate(lines):
        key: str | None = top_level_key(line)
        if key == "build":
            in_build = True
            continue
        if in_build and key is not None:
            break
        if not in_build:
            continue

        body: str
        newline: str
        body, newline = split_line_ending(line)
        match: re.Match[str] | None = re.match(r"^(\s+number:\s*)([0-9]+)(\s*(?:#.*)?)$", body)
        if match is None:
            continue
        return BuildNumberLine(
            line_index=line_index,
            prefix=match.group(1),
            value=match.group(2),
            suffix=match.group(3),
            newline=newline,
        )

    raise ValueError("Could not find build.number in recipe")


def npm_registry_url(npm_package: str) -> str:
    """Build the npm registry metadata URL for a package."""
    package_path: str = urllib.parse.quote(npm_package, safe="")
    return f"https://registry.npmjs.org/{package_path}/latest"


def read_url_bytes(url: str) -> bytes:
    """Read a URL as bytes with a deterministic user agent."""
    request: urllib.request.Request = urllib.request.Request(
        url,
        headers={"User-Agent": "ai-demos-autobump/1.0"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


def fetch_latest_version(npm_package: str) -> str:
    """Fetch the latest version for an npm package."""
    metadata_url: str = npm_registry_url(npm_package)
    metadata_bytes: bytes = read_url_bytes(metadata_url)
    metadata: object = json.loads(metadata_bytes.decode("utf-8"))
    if not isinstance(metadata, dict):
        raise ValueError(f"Unexpected npm metadata for {npm_package}: expected JSON object")

    version: object = metadata.get("version")
    if not isinstance(version, str) or not version:
        raise ValueError(f"Unexpected npm metadata for {npm_package}: missing version")

    return version


def parsed_semver(version: str) -> tuple[tuple[int, int, int], list[str] | None]:
    """Parse the semver fields needed for npm latest comparisons."""
    normalized: str = version.removeprefix("v")
    without_build: str = normalized.split("+", 1)[0]
    core_text: str
    prerelease_text: str
    core_text, separator, prerelease_text = without_build.partition("-")

    core_parts: list[str] = core_text.split(".")
    if len(core_parts) > 3 or any(not part.isdigit() for part in core_parts):
        raise ValueError(f"Cannot compare non-semver version: {version}")

    core_numbers: list[int] = [int(part) for part in core_parts]
    while len(core_numbers) < 3:
        core_numbers.append(0)

    prerelease: list[str] | None = prerelease_text.split(".") if separator else None
    return (core_numbers[0], core_numbers[1], core_numbers[2]), prerelease


def compare_prerelease(left: list[str] | None, right: list[str] | None) -> int:
    """Compare semver prerelease identifiers."""
    if left is None and right is None:
        return 0
    if left is None:
        return 1
    if right is None:
        return -1

    index: int
    for index in range(min(len(left), len(right))):
        left_identifier: str = left[index]
        right_identifier: str = right[index]
        if left_identifier == right_identifier:
            continue

        left_is_number: bool = left_identifier.isdigit()
        right_is_number: bool = right_identifier.isdigit()
        if left_is_number and right_is_number:
            left_number: int = int(left_identifier)
            right_number: int = int(right_identifier)
            return (left_number > right_number) - (left_number < right_number)
        if left_is_number:
            return -1
        if right_is_number:
            return 1
        return (left_identifier > right_identifier) - (left_identifier < right_identifier)

    return (len(left) > len(right)) - (len(left) < len(right))


def compare_versions(left: str, right: str) -> int:
    """Compare two npm semver strings."""
    if left == right:
        return 0

    left_core: tuple[int, int, int]
    right_core: tuple[int, int, int]
    left_prerelease: list[str] | None
    right_prerelease: list[str] | None
    left_core, left_prerelease = parsed_semver(left)
    right_core, right_prerelease = parsed_semver(right)
    if left_core != right_core:
        return (left_core > right_core) - (left_core < right_core)
    return compare_prerelease(left_prerelease, right_prerelease)


def url_for_version(source_url: str, current_version: str, latest_version: str) -> str:
    """Resolve a recipe source URL to a concrete tarball URL for a version."""
    versioned_url: str = source_url
    versioned_url = versioned_url.replace("${{ version }}", latest_version)
    versioned_url = versioned_url.replace("${{version}}", latest_version)
    if versioned_url != source_url:
        return versioned_url
    if current_version in versioned_url:
        return versioned_url.replace(current_version, latest_version)
    return versioned_url


def recipe_url_for_version(source_url: str, current_version: str, latest_version: str) -> str:
    """Return the source URL that should remain in the recipe after a bump."""
    if "${{ version }}" in source_url or "${{version}}" in source_url:
        return source_url
    if current_version in source_url:
        return source_url.replace(current_version, latest_version)
    return source_url


def sha256_url(url: str) -> str:
    """Download a URL and return its sha256 digest."""
    digest = hashlib.sha256()
    request: urllib.request.Request = urllib.request.Request(
        url,
        headers={"User-Agent": "ai-demos-autobump/1.0"},
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        while True:
            chunk: bytes = response.read(CHUNK_SIZE)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def render_version_line(version_line: VersionLine, value: str) -> str:
    """Render an updated context.version line."""
    return (
        f"{version_line.prefix}{version_line.quote}{value}{version_line.quote}"
        f"{version_line.suffix}{version_line.newline}"
    )


def render_source_url_line(source_line: SourceUrlLine, value: str) -> str:
    """Render an updated source.url line."""
    return (
        f"{source_line.prefix}{source_line.quote}{value}{source_line.quote}"
        f"{source_line.suffix}{source_line.newline}"
    )


def render_sha256_line(sha_line: Sha256Line, value: str) -> str:
    """Render an updated sha256 line."""
    return f"{sha_line.prefix}{value}{sha_line.suffix}{sha_line.newline}"


def render_build_number_line(build_number_line: BuildNumberLine) -> str:
    """Render build.number reset to zero."""
    return f"{build_number_line.prefix}0{build_number_line.suffix}{build_number_line.newline}"


def write_github_outputs(old_version: str, new_version: str, changed: bool) -> None:
    """Write GitHub Actions outputs when running in a workflow."""
    output_path_value: str | None = os.environ.get("GITHUB_OUTPUT")
    if output_path_value is None:
        return

    output_path: Path = Path(output_path_value)
    status: str = "true" if changed else "false"
    with output_path.open("a", encoding="utf-8") as output_file:
        output_file.write(f"old-version={old_version}\n")
        output_file.write(f"new-version={new_version}\n")
        output_file.write(f"changed={status}\n")


def update_recipe(recipe_name: str, npm_package: str) -> bool:
    """Update a recipe to the latest npm version if the registry has a newer release."""
    recipe_path: Path = RECIPE_ROOT / recipe_name / "recipe.yaml"
    if not recipe_path.is_file():
        raise FileNotFoundError(f"Recipe file not found: {recipe_path}")

    lines: list[str] = recipe_path.read_text(encoding="utf-8").splitlines(keepends=True)
    version_line: VersionLine = find_context_version(lines)
    current_version: str = version_line.value
    latest_version: str = fetch_latest_version(npm_package)
    is_newer: bool = compare_versions(latest_version, current_version) > 0
    target_version: str = latest_version if is_newer else current_version

    print(f"old-version={current_version}")
    print(f"new-version={target_version}")
    print(f"{recipe_name}: {current_version} -> {target_version}")

    if not is_newer:
        if latest_version != current_version:
            print(f"latest-registry-version={latest_version}")
        write_github_outputs(current_version, target_version, changed=False)
        print("unchanged")
        return False

    source_lines: list[SourceUrlLine] = [
        source_line
        for source_line in find_source_urls(lines)
        if url_for_version(source_line.value, current_version, latest_version)
        != source_line.value
    ]
    if not source_lines:
        raise ValueError(f"No versioned source URLs found in {recipe_path}")

    build_number_line: BuildNumberLine = find_build_number(lines)
    sha256_by_url: dict[str, str] = {}
    source_line: SourceUrlLine
    for source_line in source_lines:
        download_url: str = url_for_version(source_line.value, current_version, latest_version)
        if download_url not in sha256_by_url:
            print(f"hashing {download_url}")
            sha256_by_url[download_url] = sha256_url(download_url)

        sha_line: Sha256Line | None = parse_sha256_line(lines[source_line.sha256_line_index])
        if sha_line is None:
            line_number: int = source_line.sha256_line_index + 1
            raise ValueError(f"Expected sha256 on line {line_number}")

        recipe_url: str = recipe_url_for_version(source_line.value, current_version, latest_version)
        lines[source_line.line_index] = render_source_url_line(source_line, recipe_url)
        lines[source_line.sha256_line_index] = render_sha256_line(sha_line, sha256_by_url[download_url])
        print(f"sha256 {download_url} -> {sha256_by_url[download_url]}")

    lines[version_line.line_index] = render_version_line(version_line, latest_version)
    lines[build_number_line.line_index] = render_build_number_line(build_number_line)
    recipe_path.write_text("".join(lines), encoding="utf-8")

    write_github_outputs(current_version, latest_version, changed=True)
    print("changed")
    return True


def main() -> int:
    """Run the npm recipe updater."""
    if len(sys.argv) != 3:
        usage()

    recipe_name: str = sys.argv[1]
    npm_package: str = sys.argv[2]
    update_recipe(recipe_name, npm_package)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1) from error
