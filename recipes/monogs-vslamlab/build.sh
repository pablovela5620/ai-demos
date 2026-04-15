#!/bin/bash
set -euxo pipefail

export TORCH_CUDA_ARCH_LIST="8.6;8.9;9.0;12.0"
export CONDA_PREFIX="$PREFIX"

pip install submodules/simple-knn submodules/diff-gaussian-rasterization --no-deps --no-build-isolation
pip install . --no-deps --no-build-isolation
