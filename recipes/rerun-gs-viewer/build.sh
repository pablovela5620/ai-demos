#!/bin/bash
set -euxo pipefail

cargo build --release --locked --bin gsplat-rerun-minimal

mkdir -p "${PREFIX}/bin"
cp "${SRC_DIR}/target/release/gsplat-rerun-minimal" "${PREFIX}/bin/rerun-gs-viewer"
chmod +x "${PREFIX}/bin/rerun-gs-viewer"
