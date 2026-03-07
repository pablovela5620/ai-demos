#!/bin/bash
set -euxo pipefail

mkdir -p "${PREFIX}/bin"
cp "${SRC_DIR}/brush_app" "${PREFIX}/bin/brush_app"
chmod +x "${PREFIX}/bin/brush_app"
