#!/bin/bash
set -euxo pipefail

# The binary resolves its setting presets at ../share/xcodegen relative to
# itself, matching the layout in the upstream release archive.
mkdir -p "${PREFIX}/bin" "${PREFIX}/share"
cp "${SRC_DIR}/bin/xcodegen" "${PREFIX}/bin/xcodegen"
cp -R "${SRC_DIR}/share/xcodegen" "${PREFIX}/share/xcodegen"
chmod +x "${PREFIX}/bin/xcodegen"
