#!/usr/bin/env bash
set -euo pipefail

"$PYTHON" -m installer --prefix "$PREFIX" ./*.whl
