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

# The conda sysroot contains GNU ld linker scripts (libm.so, libc.so, etc.)
# with absolute paths like GROUP ( /lib64/libm.so.6 ). These paths don't
# exist in the build sandbox (read-only /lib64). Fix by rewriting ALL linker
# scripts in the sysroot to use the actual sysroot-prefixed paths.
for sysroot in "$BUILD_PREFIX/x86_64-conda-linux-gnu/sysroot" \
               "$PREFIX/x86_64-conda-linux-gnu/sysroot"; do
  if [ -d "$sysroot" ]; then
    find "$sysroot" -name "*.so" -o -name "*.a" | while read -r f; do
      if head -1 "$f" 2>/dev/null | grep -q "GNU ld script"; then
        echo "Fixing linker script: $f"
        # Replace absolute /lib64/ and /usr/lib64/ with sysroot-relative paths
        sed -i \
          -e "s| /lib64/| $sysroot/lib64/|g" \
          -e "s| /usr/lib64/| $sysroot/usr/lib64/|g" \
          -e "s| /lib/| $sysroot/lib/|g" \
          -e "s| /usr/lib/| $sysroot/usr/lib/|g" \
          "$f"
      fi
    done
  fi
done

pip install ./DPViewer --no-deps --no-build-isolation --use-pep517
pip install . --no-deps --no-build-isolation
