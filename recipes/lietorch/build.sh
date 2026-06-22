#!/bin/bash
set -euxo pipefail

export CONDA_PREFIX="$PREFIX"

# The VSLAM-LAB fork's setup.py already lists -gencode targets sm_60..sm_120
# (Pascal through Blackwell) plus compute_90 PTX, so nothing needs adding.
#
# CUDA 13 removed offline compilation for Maxwell/Pascal/Volta — nvcc 13 fatals
# on `compute_60`. Strip the now-unsupported targets (sm_60/61/70) for the
# cuda13 build; Turing (sm_75) and newer stay. The cuda12.9 build keeps them.
CUDA_MAJOR="$(nvcc --version | sed -n 's/.*release \([0-9]\+\).*/\1/p' | head -1)"
if [ "${CUDA_MAJOR:-0}" -ge 13 ]; then
  sed -i "/code=sm_60'/d; /code=sm_61'/d; /code=sm_70'/d" setup.py
fi

python setup.py install
