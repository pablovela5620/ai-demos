#!/usr/bin/env bash
# Mirrors conda-forge/tensorrt-feedstock's recipe/build.sh, trimmed to the
# outputs in recipe.yaml (builder resources split out of libnvinfer) and without
# cf-nvidia-tools' check-cuda-arch/check-glibc.

set -euxo pipefail

case "${PKG_NAME}" in
  libnvinfer)
    files=('*/lib/libnvinfer.so.*')
    ;;
  libnvinfer-builder-resource-*)
    files=("*/lib/libnvinfer_builder_resource_${PKG_NAME#libnvinfer-builder-resource-}.so.*")
    ;;
  libnvinfer-plugin)
    files=('*/lib/libnvinfer_plugin.so.*')
    ;;
  libnvonnxparser)
    files=('*/lib/libnvonnxparser.so.*')
    ;;
  *)
    echo "Unknown TensorRT output: ${PKG_NAME}" >&2
    exit 1
    ;;
esac

tar --zstd -xf tensorrt.tar.zst --strip-components=1 --wildcards \
  "${files[@]}" \
  '*/doc/README.txt' \
  '*/doc/Acknowledgements.txt'
rm -f tensorrt.tar.zst

mkdir -p "${PREFIX}/lib"
mv -v lib/*.so.* "${PREFIX}/lib/"
