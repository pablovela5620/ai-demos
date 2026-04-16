#!/bin/bash
set -euxo pipefail

# Gaussian splatting submodules don't hardcode gencode flags —
# they rely on TORCH_CUDA_ARCH_LIST (needed for CI builds without a GPU).
export TORCH_CUDA_ARCH_LIST="8.6;8.9;9.0;12.0"

pip install submodules/simple-knn submodules/diff-gaussian-rasterization --no-deps --no-build-isolation
pip install . --no-deps --no-build-isolation
