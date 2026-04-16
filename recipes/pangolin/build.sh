#!/bin/bash
set -euxo pipefail

# Pangolin uses pybind11 from a git submodule. Since we use a tarball source,
# the submodule isn't present. Pangolin's CMakeLists.txt falls back to
# find_package(pybind11) which finds conda's pybind11 via -Dpybind11_DIR.

# Build with default (new) C++11 ABI to match conda-forge's PyTorch.
# DPViewer's CMakeLists.txt is patched during dpvo build to also use new ABI.
# Point CMake at conda's Python (not the system Python) to avoid
# picking up /usr/include/python3.x headers on CI runners.
PY_INC=$("$PYTHON" -c "import sysconfig; print(sysconfig.get_path('include'))")
PY_LIB=$("$PYTHON" -c "import sysconfig, os; print(os.path.join(sysconfig.get_config_var('LIBDIR'), sysconfig.get_config_var('LDLIBRARY')))")

cmake -B build -S . -G Ninja \
  -DCMAKE_INSTALL_PREFIX="$PREFIX" \
  -DCMAKE_PREFIX_PATH="$PREFIX" \
  -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_EXAMPLES=OFF \
  -DBUILD_TESTS=OFF \
  -DBUILD_TOOLS=OFF \
  -DPython_EXECUTABLE="$PYTHON" \
  -DPython_INCLUDE_DIR="$PY_INC" \
  -DPython_LIBRARY="$PY_LIB" \
  -DPython3_EXECUTABLE="$PYTHON" \
  -DPython3_INCLUDE_DIR="$PY_INC" \
  -DPython3_LIBRARY="$PY_LIB" \
  -Dpybind11_DIR="$PREFIX/share/cmake/pybind11"

cmake --build build -j"${CPU_COUNT:-$(nproc)}"
cmake --install build

# Install the Python wheel if cmake configured Python bindings.
# The targets may not exist if Python/pybind11 detection fails on CI.
# DPVO only uses Pangolin's C++ API, so Python bindings are optional.
cmake --build build --target pypangolin_pip_install 2>/dev/null || \
  cmake --build build --target pypangolin_wheel 2>/dev/null || \
  echo "Warning: pypangolin targets not available — skipping Python bindings"
