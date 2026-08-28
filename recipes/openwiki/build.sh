#!/bin/bash
set -euxo pipefail

cd "${SRC_DIR}"

# Pack the extracted npm source first so a global install copies the package
# into the conda prefix instead of linking back to the temporary build tree.
TARBALL=$(npm pack --ignore-scripts 2>/dev/null)
npm install --global --prefix "${PREFIX}" "${SRC_DIR}/${TARBALL}"
