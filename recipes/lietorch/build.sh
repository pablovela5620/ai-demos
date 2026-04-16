#!/bin/bash
set -euxo pipefail

# PyTorch 2.8 doesn't support SM 12.0 (Blackwell) natively.
# Build for 8.6/8.9/9.0 — Blackwell runs via PTX forward compatibility.
export TORCH_CUDA_ARCH_LIST="8.6;8.9;9.0;12.0"
export CONDA_PREFIX="$PREFIX"

python setup.py install
