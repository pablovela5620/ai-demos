#!/bin/bash
set -euxo pipefail

# Build CUDA kernels for Ampere, Ada, Hopper, and Blackwell.
export TORCH_CUDA_ARCH_LIST="8.6;8.9;9.0;12.0"
export CONDA_PREFIX="$PREFIX"

# lietorch's setup.py hardcodes -gencode flags up to sm_86.
# Add sm_89, sm_90, sm_120, and compute_90 PTX.
sed -i "s|'-gencode=arch=compute_86,code=sm_86',|'-gencode=arch=compute_86,code=sm_86',\n                    '-gencode=arch=compute_89,code=sm_89',\n                    '-gencode=arch=compute_90,code=sm_90',\n                    '-gencode=arch=compute_90,code=compute_90',\n                    '-gencode=arch=compute_120,code=sm_120',|g" setup.py

python setup.py install
