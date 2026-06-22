#!/bin/bash
set -euxo pipefail

mkdir -p build
cd build

cmake -G Ninja \
    ${CMAKE_ARGS} \
    -DBUILD_SHARED_LIBS=ON \
    -DBUILD_TESTING=OFF \
    -DFAISS_ENABLE_PYTHON=OFF \
    -DFAISS_ENABLE_GPU=OFF \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_LIBDIR=lib \
    -DCMAKE_INSTALL_DATAROOTDIR="${PREFIX}/lib/cmake" \
    ..

cmake --build . --target faiss -j "${CPU_COUNT:-4}"
cmake --install . --prefix "${PREFIX}"
