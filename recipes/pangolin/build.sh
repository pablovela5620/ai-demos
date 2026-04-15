#!/bin/bash
set -euxo pipefail

# Pangolin uses pybind11 from a git submodule. Point it at conda's pybind11 instead.
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
cmake --build build --target pypangolin_pip_install
