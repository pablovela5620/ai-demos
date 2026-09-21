# Rebuild the temporary Linux ARM64 AV1 wheels

The normal `recipes/rerun-sdk` recipe packages checksum-pinned wheels from
the `rerun-sdk-0.38.1-av1arm64-wheels` GitHub release. It does not compile Rerun.

This directory preserves the upstream 0.38.1 source recipe, four-file AV1 patch,
and toolchain used to produce those wheels. To rebuild on Linux aarch64:

```sh
pixi run rattler-build build -r .github/rerun-source-build/recipe.yaml \
  -m conda_build_config.yaml -c conda-forge --keep-build
```

The retained work directory contains `sdk-wheels/` and `notebook-wheels/`.
Verify SDK imports on supported Python versions and capture changing AV1 frames
with the native viewer before publishing replacement build inputs. Use a new
release tag and checksums; do not replace existing assets.

The initial release wheels were built on DGX Spark using Rust 1.96.0, conda GCC
13, and the glibc 2.17 sysroot. Both wheels passed imports on Python 3.10 and 3.14;
the bundled viewer decoded AV1 at two distinct timestamps, checked in screenshots.
The original source build stopped at notebook dependency installation; that stage
was completed separately in the retained environment. The preserved build script
includes the corrected Yarn invocation and CI setting.

Remove this stopgap, the release-input recipe, and consumer pins when an upstream
release fixes rerun-io/rerun#7755.
