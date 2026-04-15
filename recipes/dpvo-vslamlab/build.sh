#!/bin/bash
set -euxo pipefail

export TORCH_CUDA_ARCH_LIST="8.6;8.9;9.0;12.0"
export CONDA_PREFIX="$PREFIX"

# conda-forge's pytorch-gpu doesn't ship libkineto.a but TorchConfig.cmake
# tries to find it via append_torchlib_if_found(kineto). When not found it
# adds "kineto_LIBRARY-NOTFOUND" to TORCH_LIBRARIES, causing link errors.
# Create a no-op static library so the find_library succeeds.
TORCH_LIB="$PREFIX/lib/python3.11/site-packages/torch/lib"
if [ ! -f "$TORCH_LIB/libkineto.a" ]; then
  echo "Creating stub libkineto.a"
  echo 'void _kineto_stub(void) {}' | "$CXX" -x c - -c -o /tmp/kineto_stub.o
  "$AR" rcs "$TORCH_LIB/libkineto.a" /tmp/kineto_stub.o
fi

pip install ./DPViewer --no-deps --no-build-isolation --use-pep517
pip install . --no-deps --no-build-isolation
