#!/bin/bash
set -euxo pipefail

# Upstream setup.py files hardcode -gencode flags up to sm_86.
# Extend with Ada (sm_89), Hopper (sm_90), Blackwell (sm_120),
# plus compute_90 PTX for forward compatibility.
find . -name "setup.py" | while read f; do
  if grep -q "compute_86,code=sm_86" "$f"; then
    sed -i "s|'-gencode=arch=compute_86,code=sm_86',|'-gencode=arch=compute_86,code=sm_86',\n                    '-gencode=arch=compute_89,code=sm_89',\n                    '-gencode=arch=compute_90,code=sm_90',\n                    '-gencode=arch=compute_90,code=compute_90',\n                    '-gencode=arch=compute_120,code=sm_120',|" "$f"
    echo "Patched $f with sm_89/sm_90/sm_120 + PTX"
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
