#!/bin/bash
set -euxo pipefail

# Source is the extracted per-platform npm package: the rust binary plus its
# vendored helpers (bundled rg, zsh resources, code-mode host) live under
# vendor/<target-triple>/. Ship the whole tree so the binary's sibling
# lookups keep working; expose bin/codex via symlink (the symlink resolves,
# so relative sibling paths land in lib/codex/).
vendor_dir="$(echo "${SRC_DIR}"/vendor/*/)"
mkdir -p "${PREFIX}/lib/codex" "${PREFIX}/bin"
cp -R "${vendor_dir}." "${PREFIX}/lib/codex/"
chmod +x "${PREFIX}/lib/codex/bin/"*
ln -sf ../lib/codex/bin/codex "${PREFIX}/bin/codex"

# Opt out of pixi exporting CONDA_PREFIX when running the exposed binary
# (same convention as the conda-forge codex package and our claude-code):
# codex spawns shells, and an inherited CONDA_PREFIX pointing at this env
# confuses project tooling.
mkdir -p "${PREFIX}/etc/pixi/codex"
touch "${PREFIX}/etc/pixi/codex/global-ignore-conda-prefix"
