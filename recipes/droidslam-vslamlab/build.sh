#!/bin/bash
set -euxo pipefail

# PyTorch 2.8 doesn't support SM 12.0 (Blackwell) natively.
# Build for 8.6/8.9/9.0 — Blackwell runs via PTX forward compatibility.
export TORCH_CUDA_ARCH_LIST="8.6;8.9;9.0;12.0"
export CONDA_PREFIX="$PREFIX"

# DROID-SLAM's setup.py hardcodes -gencode flags up to sm_86.
# Add Ada Lovelace (sm_89) and Hopper (sm_90).
sed -i "s|'-gencode=arch=compute_86,code=sm_86',|'-gencode=arch=compute_86,code=sm_86',\n                    '-gencode=arch=compute_89,code=sm_89',\n                    '-gencode=arch=compute_90,code=sm_90',|" setup.py

python -m pip install . --no-deps --no-build-isolation
