#!/bin/bash
set -euxo pipefail

export CONDA_PREFIX="$PREFIX"

# Upstream setup.py hardcodes -gencode flags up to sm_86.
# Extend with Ada (sm_89), Hopper (sm_90), Blackwell (sm_120),
# plus compute_90 PTX for forward compatibility.
sed -i "s|'-gencode=arch=compute_86,code=sm_86',|'-gencode=arch=compute_86,code=sm_86',\n                    '-gencode=arch=compute_89,code=sm_89',\n                    '-gencode=arch=compute_90,code=sm_90',\n                    '-gencode=arch=compute_90,code=compute_90',\n                    '-gencode=arch=compute_120,code=sm_120',|" setup.py

# === Remove pytorch_scatter: inject pure-PyTorch scatter_utils ===
cp "$RECIPE_DIR/scatter_utils.py" droid_slam/scatter_utils.py

# droid_slam/geom/ba.py: two-level relative import (geom/ → droid_slam/)
sed -i 's/^from torch_scatter import/from ..scatter_utils import/' droid_slam/geom/ba.py

# droid_slam/droid_net.py: single-level relative import
sed -i 's/^from torch_scatter import/from .scatter_utils import/' droid_slam/droid_net.py

python -m pip install . --no-deps --no-build-isolation
