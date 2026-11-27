# Rebuild the temporary Linux ARM64 AV1 wheels

The normal `recipes/rerun-sdk` recipe packages checksum-pinned wheels from
a GitHub release. It does not compile Rerun.

This directory preserves the upstream 0.44.0 source recipe, the AV1 patch, the
slow-reader patch, and toolchain used to produce those wheels. To rebuild on
Linux aarch64:

```sh
pixi run rattler-build build -r .github/rerun-source-build/recipe.yaml \
  -m conda_build_config.yaml -c conda-forge --keep-build
```

The retained work directory contains `sdk-wheels/` and `notebook-wheels/`.
Verify SDK imports on supported Python versions and capture changing AV1 frames
with the native viewer before publishing replacement build inputs. Use a new
release tag and checksums; do not replace existing assets.

The 0.44 build uses Rust 1.98.1, conda GCC 13, and the glibc 2.17 sysroot.
Rerun 0.44 requires Python 3.11 or newer. The web build uses
`scripts/build_web_viewer.py` and wasm-bindgen 0.2.129. Rerun 0.44 moved
`rerun_js` from Yarn to npm (`npm ci`; its postinstall generates the protobuf
bindings). The notebook build requires hatchling 1.30.1 and
hatch-jupyter-builder 0.9.1 exactly.

The AV1 patch, `rerun-0.44.0-av1-arm64.patch`, enables `re_rav1d` on Linux
aarch64 and takes `re_rav1d` 0.1.4 from the git revision
`pablo-rerun/re_rav1d@dd03865f` (branch `pablo/arm64-archext-and-hidden-symbols`;
0.1.4 is not on crates.io yet). That release marks the Rust-defined tables its
AArch64 assembly reads as hidden, so the `cdylib` links without the 0.42 build's
`-Wl,--exclude-libs,ALL` workaround in `re_viewer/build.rs`. Cargo fetches the
revision with the git CLI during the build. This is the same change as the
upstream fix for rerun-io/rerun#7755. When 0.1.4 is on crates.io, use the
registry version.

The released 0.44.0 wheels passed imports on Python 3.11, 3.14 and 3.15. The
native viewer rendered the correct, different AV1 frames at 0.2 and 1.6 seconds
(frames 6 and 48 of a synthetic test pattern); stock conda-forge 0.44.0 shows
"Rerun does not yet support native AV1 decoding on Linux ARM64" for the same
recording. The channel test passed with `--features tokio`; without that feature
the test is not compiled. In the end-to-end check (proxy with a 200 MB memory
limit, 600 MB logged, one `rerun --save` client stopped with SIGSTOP), the
producer exited after 2.0 s and the producer file and the live client both held
601 MB; a fresh client received 201 MB. Stock 0.44.0 blocked the producer's
flush and the live client for about 27 s. Each `rerun --save` client needs its
own `--port`: the default viewer port may belong to a catalog.

The second patch, `rerun-0.44.0-proxy-slow-reader.patch`, fixes a stalled live-proxy
reader blocking the logger and all viewers: Rerun's broadcast channel waits forever
by design. It allows overflow after one second so the stalled reader skips ahead.
Verify it with `test_stalled_receiver_does_not_block_sender` and the end-to-end
frozen-reader check: fresh clients receive bytes, the producer file keeps growing,
and port 19879 is free at the end. Drop this patch when upstream Rerun stops
blocking on a stalled broadcast receiver.

Remove this stopgap, the release-input recipe, and consumer pins when an upstream
release fixes rerun-io/rerun#7755.
