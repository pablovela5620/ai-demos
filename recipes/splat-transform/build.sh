#!/bin/bash
set -euxo pipefail

cd "${SRC_DIR}"

# npm install --global from a local directory creates symlinks instead of
# copying files. Pack first to get a tarball, then install from it so npm
# copies everything into the prefix.
TARBALL=$(npm pack --ignore-scripts 2>/dev/null)
npm install --global --prefix "${PREFIX}" --ignore-scripts "${SRC_DIR}/${TARBALL}"

# The webgpu npm package bundles Dawn for every supported platform. Keep only
# the native binary so each Conda package stays platform-specific and small.
WEBGPU_DIST="${PREFIX}/lib/node_modules/@playcanvas/splat-transform/node_modules/webgpu/dist"
case "$(uname -s)-$(uname -m)" in
    Darwin-*)
        NATIVE_BINARY="darwin-universal.dawn.node"
        ;;
    Linux-x86_64)
        NATIVE_BINARY="linux-x64.dawn.node"
        ;;
    Linux-aarch64 | Linux-arm64)
        NATIVE_BINARY="linux-arm64.dawn.node"
        ;;
    *)
        echo "Unsupported build platform: $(uname -s)-$(uname -m)" >&2
        exit 1
        ;;
esac

for binary in "${WEBGPU_DIST}"/*.dawn.node "${WEBGPU_DIST}/d3dcompiler_47.dll"; do
    if [[ -e "${binary}" && "$(basename "${binary}")" != "${NATIVE_BINARY}" ]]; then
        rm -f "${binary}"
    fi
done

test -f "${WEBGPU_DIST}/${NATIVE_BINARY}"
