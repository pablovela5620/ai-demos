#!/bin/bash
set -euxo pipefail

# === DPViewer CMakeLists.txt patches ===

# 1. Fix ABI: DPViewer hardcodes old ABI, conda-forge PyTorch uses new ABI
sed -i 's/-D_GLIBCXX_USE_CXX11_ABI=0/-D_GLIBCXX_USE_CXX11_ABI=1/' DPViewer/CMakeLists.txt

# 2. Disable GPU auto-detection in DPViewer (it detects SM 12.0 which
#    PyTorch's cmake module doesn't recognize). Use fixed architectures.
sed -i 's/include(FindCUDA\/select_compute_arch)/# include(FindCUDA\/select_compute_arch)/' DPViewer/CMakeLists.txt
sed -i 's/CUDA_DETECT_INSTALLED_GPUS/# CUDA_DETECT_INSTALLED_GPUS/' DPViewer/CMakeLists.txt
sed -i '/INSTALLED_GPU_CCS/s/^/# /' DPViewer/CMakeLists.txt
sed -i '/CUDA_ARCH_LIST/s/^/# /' DPViewer/CMakeLists.txt
sed -i 's/SET(CMAKE_CUDA_ARCHITECTURES ${CUDA_ARCH_LIST})/SET(CMAKE_CUDA_ARCHITECTURES 86 89 90 120)/' DPViewer/CMakeLists.txt

# === PyTorch cmake module patches ===

# 3. Create stub libkineto.a — conda-forge PyTorch doesn't ship it but
#    TorchConfig.cmake references it via append_torchlib_if_found(kineto).
TORCH_LIB="$PREFIX/lib/python3.11/site-packages/torch/lib"
if [ ! -f "$TORCH_LIB/libkineto.a" ]; then
  echo "Creating stub libkineto.a"
  echo 'void _kineto_stub(void) {}' | "$CXX" -x c - -c -o /tmp/kineto_stub.o
  "$AR" rcs "$TORCH_LIB/libkineto.a" /tmp/kineto_stub.o
fi

# === Build ===

# DPViewer uses cmake find_package(Torch) which calls cuda_select_nvcc_arch_flags
# with TORCH_CUDA_ARCH_LIST. SM 12.0 isn't recognized by PyTorch's cmake module.
# Use only known archs for the DPViewer cmake build.
export TORCH_CUDA_ARCH_LIST="8.6;8.9;9.0;12.0"
pip install ./DPViewer --no-deps --no-build-isolation --use-pep517

# DPVO uses torch.utils.cpp_extension. PyTorch 2.8 doesn't support SM 12.0,
# but 9.0+PTX provides forward compatibility for Blackwell via JIT.
export TORCH_CUDA_ARCH_LIST="8.6;8.9;9.0;12.0"
pip install . --no-deps --no-build-isolation
