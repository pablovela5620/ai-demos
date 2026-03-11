#!/bin/bash
set -euxo pipefail

cd "${SRC_DIR}"
"${BUILD_PREFIX}/bin/cargo" install --locked --root "${PREFIX}" --path . --bin gsplat-rerun-minimal

mv "${PREFIX}/bin/gsplat-rerun-minimal" "${PREFIX}/bin/rerun-gs-viewer"
