#!/usr/bin/env python3
"""Bump an npm-sourced recipe to the latest version on the npm registry.

Usage: update-npm.py <recipe-name> <npm-package>
       update-npm.py claude-code @anthropic-ai/claude-code

Edits recipes/<recipe-name>/recipe.yaml as TEXT (rattler-build jinja like
${{ version }} breaks YAML parsers): updates context.version, recomputes the
sha256 of every registry.npmjs.org source (claude-code has one per platform),
and resets the build number. Writes old-version/new-version to GITHUB_OUTPUT
when available. Last stdout line is "changed" or "unchanged".
"""

import hashlib
import json
import os
import re
import sys
import urllib.request

USER_AGENT = {"User-Agent": "ai-demos-autobump"}


def fetch_latest(npm_package: str) -> str:
    url = f"https://registry.npmjs.org/{npm_package}/latest"
    with urllib.request.urlopen(urllib.request.Request(url, headers=USER_AGENT)) as r:
        return json.load(r)["version"]


def sha256_of(url: str) -> str:
    digest = hashlib.sha256()
    with urllib.request.urlopen(urllib.request.Request(url, headers=USER_AGENT)) as r:
        for chunk in iter(lambda: r.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def github_output(old: str, new: str) -> None:
    path = os.environ.get("GITHUB_OUTPUT")
    if path:
        with open(path, "a") as f:
            f.write(f"old-version={old}\nnew-version={new}\n")


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__)
        return 1
    recipe_name, npm_package = sys.argv[1], sys.argv[2]
    recipe_path = f"recipes/{recipe_name}/recipe.yaml"
    text = open(recipe_path).read()

    m = re.search(r'(context:\s*\n\s*version:\s*")([^"]+)(")', text)
    if not m:
        print(f"ERROR: no context.version in {recipe_path}")
        return 1
    current = m.group(2)
    latest = fetch_latest(npm_package)
    print(f"{recipe_name}: current {current}, npm latest {latest}")

    if latest == current:
        github_output(current, current)
        print("unchanged")
        return 0

    text = text[: m.start(2)] + latest + text[m.end(2):]

    # Recompute sha256 for every npm source; the sha256 line follows its url.
    lines = text.splitlines(keepends=True)
    pending_url = None
    for i, line in enumerate(lines):
        # NB: recipe URLs contain jinja like ${{ version }} — spaces included,
        # so match to the trailing .tgz rather than using \S+
        url_m = re.search(r"url:\s*(https://registry\.npmjs\.org/.+\.tgz)", line)
        if url_m:
            pending_url = url_m.group(1).replace("${{ version }}", latest)
            continue
        if pending_url and re.search(r"^\s*sha256:", line):
            digest = sha256_of(pending_url)
            lines[i] = re.sub(r"(sha256:\s*)\S+", rf"\g<1>{digest}", line)
            print(f"  {pending_url.rsplit('/', 1)[-1]}: {digest}")
            pending_url = None

    text = "".join(lines)
    text = re.sub(r"(build:\s*\n\s*number:\s*)\d+", r"\g<1>0", text, count=1)

    open(recipe_path, "w").write(text)
    github_output(current, latest)
    print("changed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
