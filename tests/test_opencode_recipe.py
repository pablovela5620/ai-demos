"""Contract tests for the OpenCode package recipe."""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT: Path = Path(__file__).parent.parent


class OpenCodeRecipeTest(unittest.TestCase):
    """Verify Linux ARM64 uses the runnable glibc release binary."""

    def test_linux_arm64_uses_glibc_release_asset(self) -> None:
        """Reject the npm ARM64 binary, which requires a system musl loader."""
        recipe: str = (ROOT / "recipes/opencode/recipe.yaml").read_text()
        build_script: str = (ROOT / "recipes/opencode/build.sh").read_text()

        self.assertIn("opencode-linux-arm64.tar.gz", recipe)
        self.assertNotIn("registry.npmjs.org/opencode-linux-arm64", recipe)
        self.assertIn('file "${source_binary}"', build_script)
        self.assertIn("/lib/ld-linux-aarch64.so.1", build_script)


if __name__ == "__main__":
    unittest.main()
