#!/bin/bash
set -euxo pipefail

# CUDA 13 dropped Maxwell/Pascal/Volta; target Hopper (90), Blackwell datacenter
# (100) and consumer Blackwell (120, e.g. RTX 50xx) + 120 PTX for forward compat.
export CMAKE_CUDA_ARCHS="90-real;100-real;120-real;120-virtual"

mkdir -p build
cd build

cmake -G Ninja \
    ${CMAKE_ARGS} \
    -DBUILD_SHARED_LIBS=ON \
    -DBUILD_TESTING=OFF \
    -DFAISS_ENABLE_PYTHON=OFF \
    -DFAISS_ENABLE_GPU=ON \
    -DFAISS_ENABLE_RAFT=OFF \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_LIBDIR=lib \
    -DCMAKE_INSTALL_DATAROOTDIR="${PREFIX}/lib/cmake" \
    -DCMAKE_CUDA_ARCHITECTURES="${CMAKE_CUDA_ARCHS}" \
    ..

cmake --build . --target faiss -j "${CPU_COUNT:-4}"
cmake --install . --prefix "${PREFIX}"
