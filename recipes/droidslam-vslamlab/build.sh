#!/bin/bash
set -euxo pipefail

# Build for multiple GPU architectures including Blackwell (sm_120).
export TORCH_CUDA_ARCH_LIST="8.6;8.9;9.0;12.0"
export CONDA_PREFIX="$PREFIX"

python -m pip install . --no-deps --no-build-isolation
