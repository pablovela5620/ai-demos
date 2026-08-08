#!/bin/bash
set -euxo pipefail

mkdir -p "${PREFIX}/bin"

source_binary="${SRC_DIR}/bin/opencode"
if [[ "${target_platform:-}" == "linux-aarch64" ]]; then
    source_binary="${SRC_DIR}/opencode"
    file "${source_binary}" | grep -Fq 'interpreter /lib/ld-linux-aarch64.so.1'
fi

install -m 755 "${source_binary}" "${PREFIX}/bin/opencode"
