#!/bin/bash
set -euxo pipefail

# Pangolin uses pybind11 from a git submodule. Since we use a tarball source,
# the submodule isn't present. Pangolin's CMakeLists.txt falls back to
# find_package(pybind11) which finds conda's pybind11 via -Dpybind11_DIR.

cmake -B build -S . -G Ninja \
  -DCMAKE_INSTALL_PREFIX="$PREFIX" \
  -DCMAKE_PREFIX_PATH="$PREFIX" \
  -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_EXAMPLES=OFF \
  -DBUILD_TESTS=OFF \
  -DBUILD_TOOLS=OFF \
  -DPython3_EXECUTABLE="$PYTHON" \
  -Dpybind11_DIR="$PREFIX/share/cmake/pybind11"

cmake --build build -j"${CPU_COUNT:-$(nproc)}"
cmake --install build

# Install the Python wheel that CMake generates
cmake --build build --target pypangolin_pip_install || \
  cmake --build build --target pypangolin_wheel
