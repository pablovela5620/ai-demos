#!/bin/bash
set -euxo pipefail

# Build for multiple GPU architectures including Blackwell (sm_120).
export TORCH_CUDA_ARCH_LIST="8.6;8.9;9.0;12.0"
export CONDA_PREFIX="$PREFIX"

# DROID-SLAM's setup.py hardcodes -gencode flags up to sm_86.
# Add Blackwell (sm_120), Hopper (sm_90), and Ada Lovelace (sm_89).
sed -i "s|'-gencode=arch=compute_86,code=sm_86',|'-gencode=arch=compute_86,code=sm_86',\n                    '-gencode=arch=compute_89,code=sm_89',\n                    '-gencode=arch=compute_90,code=sm_90',\n                    '-gencode=arch=compute_120,code=sm_120',|" setup.py

python -m pip install . --no-deps --no-build-isolation
