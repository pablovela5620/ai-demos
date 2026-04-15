#!/bin/bash
set -euxo pipefail

export TORCH_CUDA_ARCH_LIST="8.6;8.9;9.0;12.0"
export CONDA_PREFIX="$PREFIX"

pip install thirdparty/mast3r/asmk --no-deps --no-build-isolation
pip install -e thirdparty/mast3r --no-build-isolation
cd ./thirdparty/in3d/thirdparty/pyimgui
python setup.py build_ext --inplace
cd ../../../../
pip install ./thirdparty/in3d/thirdparty/pyimgui --no-deps --no-build-isolation
pip install -e thirdparty/in3d --no-build-isolation

pip install . --no-build-isolation
