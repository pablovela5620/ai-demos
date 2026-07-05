#!/bin/bash
set -euxo pipefail

cd "${SRC_DIR}"

# Pack first, then install from the tarball so npm copies files into the
# prefix instead of symlinking (same pattern as splat-transform).
TARBALL=$(npm pack --ignore-scripts 2>/dev/null)

# NO --ignore-scripts here: node-pty (via @getpaseo/server) must compile its
# native addon with node-gyp, and sherpa-onnx-node fetches its platform
# binary in a postinstall step.
npm install --global --prefix "${PREFIX}" "${SRC_DIR}/${TARBALL}"

# Trim node-gyp build intermediates to keep the package lean.
find "${PREFIX}/lib/node_modules/@getpaseo" -type d -name "obj.target" -prune -exec rm -rf {} + 2>/dev/null || true
find "${PREFIX}/lib/node_modules/@getpaseo" -type f -name "*.o" -delete 2>/dev/null || true
