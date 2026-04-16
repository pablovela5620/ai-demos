#!/bin/bash
set -euxo pipefail

export CONDA_PREFIX="$PREFIX"

# Upstream lietorch hardcodes -gencode flags up to sm_86.
# Extend with Ada (sm_89), Hopper (sm_90), Blackwell (sm_120),
# plus compute_90 PTX for forward compatibility.
sed -i "s|'-gencode=arch=compute_86,code=sm_86',|'-gencode=arch=compute_86,code=sm_86',\n                    '-gencode=arch=compute_89,code=sm_89',\n                    '-gencode=arch=compute_90,code=sm_90',\n                    '-gencode=arch=compute_90,code=compute_90',\n                    '-gencode=arch=compute_120,code=sm_120',|g" setup.py

python setup.py install
