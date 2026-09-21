#!/usr/bin/env bash
set -euo pipefail

# Adapted from conda-forge/rerun-sdk-feedstock's 0.38.1 build.
export CARGO_NET_GIT_FETCH_WITH_CLI=true
export IS_IN_RERUN_WORKSPACE=no
export CARGO_BUILD_JOBS="${CPU_COUNT:-8}"
if (( CARGO_BUILD_JOBS > 8 )); then
    export CARGO_BUILD_JOBS=8
fi
unset CI

export CC_wasm32_unknown_unknown=clang
export CXX_wasm32_unknown_unknown=clang++
export AR_wasm32_unknown_unknown=llvm-ar
export PKG_CONFIG_ALLOW_CROSS=1
export PIXI_PROJECT_ROOT="$PWD"
export PYTHONPATH="$PWD/rerun_pixi_env/src${PYTHONPATH:+:$PYTHONPATH}"
"$PYTHON" -c 'from rerun_pixi_env import ensure_pyo3_build_cfg; ensure_pyo3_build_cfg()'

cargo-bundle-licenses --format yaml --output THIRDPARTY.yml

run_wasm_build() {
    (
        unset CFLAGS CXXFLAGS CPPFLAGS TARGET_CFLAGS TARGET_CXXFLAGS TARGET_CPPFLAGS
        "$@"
    )
}

run_wasm_build cargo run --locked -p re_dev_tools -- build-web-viewer --no-default-features --features analytics,map_view --release -g
cargo build --locked --package rerun-cli --target aarch64-unknown-linux-gnu --no-default-features --features release_full --release
cp target/aarch64-unknown-linux-gnu/release/rerun rerun_py/rerun_sdk/rerun_cli/rerun
maturin build --locked --release --manifest-path rerun_py/Cargo.toml --target aarch64-unknown-linux-gnu --features pypi --interpreter "$PYTHON" --out sdk-wheels
"$PYTHON" -m installer --prefix "$PREFIX" sdk-wheels/*.whl

yarn --cwd rerun_js install
run_wasm_build yarn --cwd rerun_js/web-viewer run build
"$PYTHON" -m build --wheel --no-isolation --outdir notebook-wheels rerun_notebook
"$PYTHON" -m installer --prefix "$PREFIX" notebook-wheels/*.whl
