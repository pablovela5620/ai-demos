#!/bin/bash
set -euxo pipefail

cd "${SRC_DIR}"

# npm install --global from a local directory creates symlinks instead of
# copying files. Pack first to get a tarball, then install from it so npm
# copies everything into the prefix.
TARBALL=$(npm pack --ignore-scripts 2>/dev/null)
npm install --global --prefix "${PREFIX}" --ignore-scripts "${SRC_DIR}/${TARBALL}"
