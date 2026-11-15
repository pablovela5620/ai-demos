#!/bin/bash
set -euxo pipefail

platform_args=()
if [[ "${target_platform}" == linux-* ]]; then
  platform_args+=(-DGLFW_BUILD_WAYLAND=OFF)
  # GLFW's C sources need CLOCK_MONOTONIC and O_CLOEXEC, which the glibc 2.17
  # sysroot hides without a feature macro (g++ defines it for the C++ files).
  export CFLAGS="${CFLAGS} -D_GNU_SOURCE"
else
  platform_args+=(-DSS_MOLTENVK_DIR="${SRC_DIR}/.deps/moltenvk" -DOpenMP_ROOT="${PREFIX}")
fi

# The source lints check uncommitted changes, which a release tarball has none
# of. Without Git, --version reports the release alone, not the commit of
# whatever repository holds the build directory.
cmake -S . -B build -G Ninja ${CMAKE_ARGS} \
  -DCMAKE_DISABLE_FIND_PACKAGE_Git=ON \
  -DSS_BACKEND=vulkan \
  -DSS_BUILD_GUI=ON \
  -DSS_SLANGC="${SRC_DIR}/.deps/slang/bin/slangc" \
  -DFETCHCONTENT_FULLY_DISCONNECTED=ON \
  -DFETCHCONTENT_SOURCE_DIR_GLFW="${SRC_DIR}/.deps/glfw" \
  -DFETCHCONTENT_SOURCE_DIR_IMGUI="${SRC_DIR}/.deps/imgui" \
  -DSS_CHECK_COMMENTS=OFF \
  -DSS_CHECK_UI_TEXT=OFF \
  "${platform_args[@]}"

# The project has no install rules; spirula is the one executable it ships.
cmake --build build --target spirula -j"${CPU_COUNT}"
mkdir -p "${PREFIX}/bin"
install -m 755 build/spirula "${PREFIX}/bin/spirula"
