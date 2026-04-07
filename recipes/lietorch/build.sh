#!/bin/bash
set -euxo pipefail

# Build for multiple GPU architectures. nvcc compilation does not need a
# physical GPU — the CUDA toolkit packages provide everything.
#   8.6 = Ampere  (RTX 30xx)
#   8.9 = Ada Lovelace (RTX 40xx)
#   9.0 = Hopper  (H100)
#  12.0 = Blackwell (RTX 50xx)
export TORCH_CUDA_ARCH_LIST="8.6;8.9;9.0;12.0"

# rattler-build uses $PREFIX for the host env (where eigen/torch live).
# The patched setup.py reads CONDA_PREFIX for eigen header paths.
export CONDA_PREFIX="$PREFIX"

python setup.py build_ext install --prefix="$PREFIX"
