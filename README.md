# ai-demos

Conda package forge for AI/robotics demos, built with [rattler-build](https://rattler-build.readthedocs.io/) and published to the [prefix.dev/ai-demos](https://prefix.dev/channels/ai-demos) channel.

## Packages

| Package | Description | Platforms |
|---------|-------------|-----------|
| [cuvslam](https://prefix.dev/channels/ai-demos/packages/cuvslam) | Python bindings for NVIDIA cuVSLAM visual SLAM | linux-64, linux-aarch64 |
| [simplecv](https://prefix.dev/channels/ai-demos/packages/simplecv) | Simple computer-vision utilities | noarch |

## Prerequisites

- [pixi](https://pixi.sh) package manager

## Quick start

```bash
git clone https://github.com/pablovela5620/ai-demos.git
cd ai-demos
pixi install
```

Build only packages whose latest version is not yet on the channel:

```bash
pixi run build-new
```

Rebuild all packages regardless of what already exists:

```bash
pixi run build-all
```

Built `.conda` packages are written to `output/`.

## Updating an existing package

**Version number** — bump when the upstream source changes (new release, new source archive). Reset `build.number` to 0 and update the `sha256` hash(es).

**Build number** — bump (without changing `version`) when only the packaging changes: patching the build script, updating `run` dependencies, or fixing recipe metadata like `description`. The source archive stays the same so the hash doesn't change.

1. Edit `recipes/<pkg>/recipe.yaml` with the appropriate bump.
2. If `version` changed, update the `sha256` hash for each source archive.
3. Push to `main` — CI will build and upload the new version automatically.

## Adding a new recipe

1. Create `recipes/<name>/recipe.yaml` following the [rattler-build recipe format](https://rattler-build.readthedocs.io/en/latest/reference/recipe_file/).
2. If the package needs a build script, add `recipes/<name>/build.sh`.
3. Test locally:
   ```bash
   pixi run rattler-build build -c https://prefix.dev/ai-demos -c conda-forge \
     --recipe recipes/<name>/ --no-test
   ```
4. Push to `main` — the existing CI workflow picks up any new recipe directory automatically.

## CI/CD

GitHub Actions (`.github/workflows/build.yml`) runs on every push to `main`:

1. **Build** — builds all recipes for `linux-64` and `linux-aarch64`, skipping versions that already exist on the channel.
2. **Upload** — authenticates to prefix.dev via OIDC trusted publisher and uploads new `.conda` packages to the `ai-demos` channel.

Pull requests trigger builds (no upload) so you can verify the recipe compiles before merging.
