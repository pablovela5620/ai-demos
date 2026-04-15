#!/bin/bash
set -euxo pipefail

export TORCH_CUDA_ARCH_LIST="8.6;8.9;9.0;12.0"
export CONDA_PREFIX="$PREFIX"

# 1. Clone and install Salad
echo "Cloning and installing Salad..."
git clone https://github.com/Dominic101/salad.git
pip install ./salad --no-deps --no-build-isolation

# 2. Clone and install VGGT
echo "Cloning and installing VGGT..."
git clone https://github.com/VSLAM-LAB/vggt-VSLAM-LAB.git vggt
pip install ./vggt --no-deps --no-build-isolation

# 3. Install current repo
echo "Installing current repo..."
pip install . --no-deps --no-build-isolation

echo "Installation Complete"
