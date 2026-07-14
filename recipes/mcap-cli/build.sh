#!/bin/bash
set -euxo pipefail

mkdir -p "${PREFIX}/bin"
install -m 755 "${SRC_DIR}/mcap" "${PREFIX}/bin/mcap"
