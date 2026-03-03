#!/bin/bash
set -euxo pipefail

# Use $PREFIX-relative path directly (avoids calling cross-compiled python on x86_64 CI)
DEST="${PREFIX}/lib/python3.10/site-packages/cuvslam"
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
# $ORIGIN/../../.. → resolves to $PREFIX/lib from lib/python3.10/site-packages/cuvslam/
patchelf --set-rpath '$ORIGIN:$ORIGIN/../../..' "${DEST}/pycuvslam.so"
patchelf --set-rpath '$ORIGIN:$ORIGIN/../../..' "${DEST}/libcuvslam.so"

chmod +x "${DEST}/pycuvslam.so" "${DEST}/libcuvslam.so"
