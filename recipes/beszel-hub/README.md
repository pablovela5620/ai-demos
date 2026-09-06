# Beszel Hub GPU overview patch

This Linux x86-64 package builds upstream Beszel 0.19.0 at commit
`ffcdb041670a501611727848649d28d886beb231` with the adjacent
`patches/gpu-overview.patch`. Build number 1 distinguishes the fleet patch from
the unmodified upstream release. The executable remains `beszel` and reports
upstream version 0.19.0.

The patch separates GPU presence from current utilization so an idle GPU is
shown as zero usage rather than a missing GPU. The patch includes its focused
frontend and backend regression tests. Both run from `build.sh` even when the
channel CI passes `--no-test`; package tests also check `bin/beszel` and its
version command.

The frontend uses upstream `bun.lock` with frozen installation, followed by
upstream Lingui extraction/compilation and Vite build. Go embeds those built
assets into a static `CGO_ENABLED=0` Linux binary. Go 1.27.1 and Bun 1.3.11 are
pinned; Node follows the reviewed 24.x major. No daemon or Docker configuration
is installed by this package.

From the `ai-demos` workspace on Linux x86-64:

```sh
pixi run rattler-build build --recipe recipes/beszel-hub/recipe.yaml --keep-build -c conda-forge
```

The adjacent standalone workspace exposes the same recipe through the pinned
stable build backend:

```sh
pixi build --path recipes/beszel-hub/pixi.toml
```

The existing main-branch package CI builds and publishes this recipe to
`https://prefix.dev/ai-demos`. Other target platforms are deliberately skipped;
only the conductor's Linux x86-64 Hub is in scope. To update, review the upstream
revision, rebase the patch, run the regressions and raise the build number for
another patch at the same version.
