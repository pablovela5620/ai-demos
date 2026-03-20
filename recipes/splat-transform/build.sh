#!/bin/bash
set -euxo pipefail

cd "${SRC_DIR}"

# npm install --global from a local directory creates symlinks instead of
# copying files. Pack first to get a tarball, then install from it so npm
# copies everything into the prefix.
TARBALL=$(npm pack --ignore-scripts 2>/dev/null)
npm install --global --prefix "${PREFIX}" --ignore-scripts "${SRC_DIR}/${TARBALL}"

# Remove native Dawn binaries for other platforms to reduce package size.
# The webgpu npm package bundles all platforms (~52 MiB); only keep the
# one matching the current build target.
WEBGPU_DIST="${PREFIX}/lib/node_modules/@playcanvas/splat-transform/node_modules/webgpu/dist"
if [[ "$(uname)" == "Darwin" ]]; then
    rm -f "${WEBGPU_DIST}/linux-x64.dawn.node" \
          "${WEBGPU_DIST}/win32-x64.dawn.node" \
          "${WEBGPU_DIST}/d3dcompiler_47.dll"
else
    rm -f "${WEBGPU_DIST}/darwin-universal.dawn.node" \
          "${WEBGPU_DIST}/win32-x64.dawn.node" \
          "${WEBGPU_DIST}/d3dcompiler_47.dll"
fi
