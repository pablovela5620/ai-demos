#!/bin/bash
set -euo pipefail

# Build for common GPU architectures. +PTX on the highest arch enables
# forward compatibility with future GPUs via JIT compilation.
#   8.0  = A100        8.6 = RTX 30xx      8.9 = RTX 40xx
#   9.0  = H100       12.0 = RTX 50xx (Blackwell, requires CUDA >=12.8)
export TORCH_CUDA_ARCH_LIST="${TORCH_CUDA_ARCH_LIST:-8.0;8.6;8.9;9.0;12.0+PTX}"

# rattler-build uses $PREFIX for the host env where eigen/torch live.
# The patched setup.py reads CONDA_PREFIX for eigen header paths.
export CONDA_PREFIX="$PREFIX"

echo "Building lietorch for CUDA architectures: $TORCH_CUDA_ARCH_LIST"
python setup.py build_ext install --prefix="$PREFIX"
