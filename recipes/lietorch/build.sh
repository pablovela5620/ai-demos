#!/bin/bash
set -euxo pipefail

export CONDA_PREFIX="$PREFIX"

# The pinned VSLAM-LAB rev's setup.py stops at -gencode sm_86 (Ampere): no Ada
# (sm_89), Hopper (sm_90), or Blackwell (sm_120), and no PTX fallback — so on
# an RTX 4090/5090 every kernel dies with cudaErrorNoKernelImageForDevice.
# Append the missing targets after each sm_86 entry (both extensions), plus
# compute_120 PTX so future architectures can JIT.
sed -i "/code=sm_86'/a\\                    '-gencode=arch=compute_89,code=sm_89', '-gencode=arch=compute_90,code=sm_90', '-gencode=arch=compute_120,code=sm_120', '-gencode=arch=compute_120,code=compute_120'," setup.py
grep -c 'compute_120,code=sm_120' setup.py | grep -qx 2  # both ext blocks patched

# CUDA 13 removed offline compilation for Maxwell/Pascal/Volta — nvcc 13 fatals
# on `compute_60`. Strip the now-unsupported targets (sm_60/61/70) for the
# cuda13 build; Turing (sm_75) and newer stay. The cuda12.9 build keeps them.
CUDA_MAJOR="$(nvcc --version | sed -n 's/.*release \([0-9]\+\).*/\1/p' | head -1)"
if [ "${CUDA_MAJOR:-0}" -ge 13 ]; then
  sed -i "/code=sm_60'/d; /code=sm_61'/d; /code=sm_70'/d" setup.py
fi

python setup.py install
