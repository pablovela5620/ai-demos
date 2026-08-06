#!/bin/bash
set -euxo pipefail

mkdir -p "${PREFIX}/bin"
install -m 755 "${SRC_DIR}/bin/opencode" "${PREFIX}/bin/opencode"
