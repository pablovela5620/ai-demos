# Rebuild the temporary Linux ARM64 AV1 wheels

The normal `recipes/rerun-sdk` recipe packages checksum-pinned wheels from
a GitHub release. It does not compile Rerun.

This directory preserves the upstream 0.42.0 source recipe, four-file AV1 patch,
the slow-reader patch, and toolchain used to produce those wheels. To rebuild on
Linux aarch64:

```sh
pixi run rattler-build build -r .github/rerun-source-build/recipe.yaml \
  -m conda_build_config.yaml -c conda-forge --keep-build
```

The retained work directory contains `sdk-wheels/` and `notebook-wheels/`.
Verify SDK imports on supported Python versions and capture changing AV1 frames
with the native viewer before publishing replacement build inputs. Use a new
release tag and checksums; do not replace existing assets.

The 0.42 build uses Rust 1.98.1, conda GCC 13, and the glibc 2.17 sysroot.
Rerun 0.42 requires Python 3.11 or newer. The web build uses
`scripts/build_web_viewer.py` and wasm-bindgen 0.2.129. The notebook build
requires hatchling 1.30.1 and hatch-jupyter-builder 0.9.1 exactly.

The released 0.42.0 wheels passed imports on Python 3.11, 3.14 and 3.15. The
native viewer rendered the correct, different AV1 frames at 0.2 and 1.6 seconds.
The channel test passed with `--features tokio`; without that feature the test is
not compiled. In the end-to-end check (proxy with a 200 MB memory limit, 600 MB
logged), a stopped gRPC client did not block the producer file or another client
(both received 601 MB), and a fresh client received 192 MB. Each `rerun --save`
client needs its own `--port`: the default viewer port may belong to a catalog.

The second patch, `rerun-0.42.0-proxy-slow-reader.patch`, fixes a stalled live-proxy
reader blocking the logger and all viewers: Rerun's broadcast channel waits forever
by design. It allows overflow after one second so the stalled reader skips ahead.
Verify it with `test_stalled_receiver_does_not_block_sender` and the end-to-end
frozen-reader check: fresh clients receive bytes, the producer file keeps growing,
and port 19879 is free at the end. Drop this patch when upstream Rerun stops
blocking on a stalled broadcast receiver.

Remove this stopgap, the release-input recipe, and consumer pins when an upstream
release fixes rerun-io/rerun#7755.
