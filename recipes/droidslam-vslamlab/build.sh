#!/bin/bash
set -euxo pipefail

# PyTorch 2.8 doesn't support SM 12.0 (Blackwell) natively.
# Build for 8.6/8.9/9.0 — Blackwell runs via PTX forward compatibility.
export TORCH_CUDA_ARCH_LIST="8.6;8.9;9.0;12.0"
export CONDA_PREFIX="$PREFIX"

# DROID-SLAM's setup.py hardcodes -gencode flags up to sm_86.
# Add Ada Lovelace (sm_89) and Hopper (sm_90).
sed -i "s|'-gencode=arch=compute_86,code=sm_86',|'-gencode=arch=compute_86,code=sm_86',\n                    '-gencode=arch=compute_89,code=sm_89',\n                    '-gencode=arch=compute_90,code=sm_90',|" setup.py

# === Remove pytorch_scatter: inject pure-PyTorch scatter_utils ===
cp "$RECIPE_DIR/scatter_utils.py" droid_slam/scatter_utils.py

# droid_slam/geom/ba.py: two-level relative import (geom/ → droid_slam/)
sed -i 's/^from torch_scatter import/from ..scatter_utils import/' droid_slam/geom/ba.py

# droid_slam/droid_net.py: single-level relative import
sed -i 's/^from torch_scatter import/from .scatter_utils import/' droid_slam/droid_net.py

python -m pip install . --no-deps --no-build-isolation
