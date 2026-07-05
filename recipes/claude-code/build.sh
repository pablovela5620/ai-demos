#!/bin/bash
set -euxo pipefail

# Source is the extracted platform npm package: the native binary at ./claude
# (SRC_DIR is the extracted package/ directory contents).
mkdir -p "${PREFIX}/bin"
install -m 755 "${SRC_DIR}/claude" "${PREFIX}/bin/claude"
