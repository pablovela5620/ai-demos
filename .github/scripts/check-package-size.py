"""Fail when a built package is larger than prefix.dev accepts.

prefix.dev rejects any single package file over 1 GiB with ``413 Payload Too Large``
("Package size (1.8 GiB) exceeds the maximum allowed size (1 GiB)"). The upload job
only finds that out after the build has finished, and its loop stops at the first
rejected file, so one oversized package blocks every other package in the same run.
This check runs right after the build, on pull requests too, so an oversized package
fails before it is merged. Split such a package into several outputs instead (see
recipes/tensorrt: one builder-resource package per GPU architecture).

Usage: python .github/scripts/check-package-size.py [OUTPUT_DIR]
"""

from __future__ import annotations

import sys
from pathlib import Path

MAX_PACKAGE_BYTES: int = 1024**3
"""prefix.dev's per-file upload limit (1 GiB)."""


def oversized_packages(output_dir: Path, max_bytes: int = MAX_PACKAGE_BYTES) -> list[tuple[Path, int]]:
    """Return every ``.conda`` / ``.tar.bz2`` package under ``output_dir`` larger than ``max_bytes``.

    Args:
        output_dir: The rattler-build output directory.
        max_bytes: The largest allowed file size.

    Returns:
        ``(path, size_bytes)`` pairs, largest first.
    """
    packages: list[Path] = [*output_dir.rglob("*.conda"), *output_dir.rglob("*.tar.bz2")]
    sized: list[tuple[Path, int]] = [(path, path.stat().st_size) for path in packages]
    return sorted((item for item in sized if item[1] > max_bytes), key=lambda item: item[1], reverse=True)


def main(argv: list[str]) -> int:
    """Print the oversized packages and return 1 if there are any."""
    output_dir: Path = Path(argv[1]) if len(argv) > 1 else Path("output")
    if not output_dir.is_dir():
        print(f"No {output_dir}/ directory: nothing to check")
        return 0
    too_big: list[tuple[Path, int]] = oversized_packages(output_dir)
    for path, size in too_big:
        print(f"::error file={path}::{path.name} is {size / 1024**3:.2f} GiB; prefix.dev rejects packages over 1 GiB. Split it into smaller outputs.")
    if too_big:
        return 1
    print(f"All packages under {output_dir}/ are within prefix.dev's 1 GiB limit")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
