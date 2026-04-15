#!/bin/bash
set -euxo pipefail

export TORCH_CUDA_ARCH_LIST="8.6;8.9;9.0;12.0"
export CONDA_PREFIX="$PREFIX"

# MASt3R-SLAM's setup.py hardcodes -gencode flags up to sm_86.
# Add Blackwell (sm_120), Hopper (sm_90), and Ada Lovelace (sm_89).
find . -name "setup.py" | while read f; do
  if grep -q "compute_86,code=sm_86" "$f"; then
    sed -i "s|'-gencode=arch=compute_86,code=sm_86',|'-gencode=arch=compute_86,code=sm_86',\n                    '-gencode=arch=compute_89,code=sm_89',\n                    '-gencode=arch=compute_90,code=sm_90',\n                    '-gencode=arch=compute_120,code=sm_120',|" "$f"
    echo "Patched $f with sm_89/sm_90/sm_120"
  fi
done

pip install thirdparty/mast3r/asmk --no-deps --no-build-isolation
pip install -e thirdparty/mast3r --no-build-isolation
cd ./thirdparty/in3d/thirdparty/pyimgui
python setup.py build_ext --inplace
cd ../../../../
pip install ./thirdparty/in3d/thirdparty/pyimgui --no-deps --no-build-isolation
pip install -e thirdparty/in3d --no-build-isolation

pip install . --no-build-isolation
