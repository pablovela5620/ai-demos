#!/bin/bash
set -euxo pipefail

# Source is the extracted platform npm package: the native binary at ./claude
# (SRC_DIR is the extracted package/ directory contents).
mkdir -p "${PREFIX}/bin"
install -m 755 "${SRC_DIR}/claude" "${PREFIX}/bin/claude"

# Opt out of pixi exporting CONDA_PREFIX when running the exposed binary
# (same convention as the conda-forge codex package): claude spawns shells,
# and an inherited CONDA_PREFIX pointing at this env confuses project tooling.
mkdir -p "${PREFIX}/etc/pixi/claude"
touch "${PREFIX}/etc/pixi/claude/global-ignore-conda-prefix"
