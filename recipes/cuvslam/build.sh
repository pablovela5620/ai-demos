#!/bin/bash
set -euxo pipefail

# Derive site-packages path from Python (not hardcoded)
SITE_PACKAGES=$(python -c "import sysconfig; print(sysconfig.get_path('purelib'))")
DEST="${SITE_PACKAGES}/cuvslam"
mkdir -p "${DEST}"

# Copy all package files
cp "${SRC_DIR}/__init__.py" "${DEST}/"
cp "${SRC_DIR}/tracker.py" "${DEST}/"
cp "${SRC_DIR}/pycuvslam.so" "${DEST}/"
cp "${SRC_DIR}/libcuvslam.so" "${DEST}/"
cp "${SRC_DIR}/pycuvslam.pyi" "${DEST}/"
cp "${SRC_DIR}/py.typed" "${DEST}/"

# Patch RPATH so .so files find each other and CUDA libs from conda prefix
# $ORIGIN → pycuvslam.so finds libcuvslam.so in same directory
# relative path → both find libcublas, libcusolver in $PREFIX/lib
RPATH_TO_LIB=$(python -c "import os; print(os.path.relpath('${PREFIX}/lib', '${DEST}'))")
patchelf --set-rpath "\$ORIGIN:${RPATH_TO_LIB}" "${DEST}/pycuvslam.so"
patchelf --set-rpath "\$ORIGIN:${RPATH_TO_LIB}" "${DEST}/libcuvslam.so"

chmod +x "${DEST}/pycuvslam.so" "${DEST}/libcuvslam.so"
