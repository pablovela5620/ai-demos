# ai-demos

Conda recipes for AI and robotics tools, built with [rattler-build](https://rattler-build.readthedocs.io/) and published to the [prefix.dev/ai-demos](https://prefix.dev/channels/ai-demos) channel.
The channel is the package catalog and `recipes/<name>/recipe.yaml` is the source of truth for each package.
agent-fleet pins exact versions from this channel, so publishing here changes nothing on machines until a pin moves.

## Working on recipes

Tasks live in `pixi.toml`. The everyday ones:

- `pixi run test-recipe <name>` builds one recipe and runs its tests on this machine's platform.
- `pixi run build-new` builds every recipe whose version is not on the channel yet, into `output/`.
- `pixi run check` runs the repository tests.

A new recipe is a new `recipes/<name>/` directory (`recipe.yaml`, plus `build.sh` if needed); CI picks it up.
Merge to `main` and CI builds and publishes whatever the channel is missing.

**Versions and build numbers.** For a new upstream release, change `context.version`, update every `sha256`, and reset `build.number` to 0.
For a packaging-only change (build script, `run` dependencies, metadata), bump `build.number` and keep the version and hashes.
A `# autobump: preserve-build-number` comment on the `build.number` line keeps the number across automatic version bumps (opencode carries a corrected build lane this way).

**Package size limit.** prefix.dev rejects any single package file over **1 GiB** (`413 Payload Too Large`).
The build job runs `pixi run check-package-size` after the build, so an oversized package fails on its pull
request, not in the upload job after merge (where it would also block every other package in that run).
Split a large package into several outputs instead; `recipes/tensorrt` ships one
`libnvinfer-builder-resource-<arch>` package per GPU architecture for this reason.

## Autobump

`.github/workflows/autobump.yml` checks the recipes in its matrix every Monday: the npm `latest` tag, or for
opencode the highest `vX.Y.Z` GitHub release (its 2.x releases are not on npm). For each newer release,
`autobump-recipe.yml`:

1. rewrites the recipe on the branch `autobump/<recipe>`, opens or updates that recipe's one PR, and closes its older bump PRs;
2. builds the recipe and runs its tests natively on linux-64 and linux-aarch64;
3. merges the tested commit and dispatches `build.yml` on `main` to publish.

A bump whose tests fail stays open as a PR for a human. The merge needs no review because agent-fleet's pins gate
what machines install. The publish is a dispatch because a merge made with `GITHUB_TOKEN` starts no push workflow.

The updater is `pixi run autobump <recipe> npm:<package>` (or `github:<owner>/<repo>`). A recipe in the matrix
needs `context.version` as its first key, a `sha256` line right below each `${{ version }}` URL, and
`build.number` as the first `build` key; `pixi run check` enforces this.

## CI/CD

`.github/workflows/build.yml` runs on pushes to `main`, on pull requests, and on dispatch:

1. **Build** builds all recipes for `linux-64` and `linux-aarch64`, skipping versions that already exist on the channel,
   then checks that no package file is over prefix.dev's 1 GiB limit.
2. **Upload** runs for `main` only. It authenticates to prefix.dev via OIDC trusted publisher and uploads the new
   `.conda` packages. Build artifacts are kept for one day, long enough for this job.

Validate macOS changes on the fleet Mac mini. Hosted macOS runners are excluded
to avoid private-repository usage costs. In a checkout on that machine, run
`pixi run check`, `pixi run test-blender-package`, then
`TARGET_PLATFORM=osx-arm64 pixi run ci-build`.

Publish the five tested agent packages (`paseo`, `claude-code`, `codex`,
`opencode`, and `ruler`) through the same CI publisher as Linux. This does
not need a personal Prefix login or a hosted Mac runner. Stage the packages
in a temporary prerelease named `macos-staging-<full recipe commit SHA>`
(marked as a prerelease, not the latest release),
with a `SHA256SUMS` file containing only those five filenames and hashes.
Dispatch `build.yml` on `main` with `prebuilt_release` set to that release
name and `prebuilt_manifest_sha256` set to the hash of `SHA256SUMS`.
CI checks every hash and each recipe version before using the existing
OIDC publisher. After it succeeds, verify channel availability, remove
the temporary prerelease, then merge the fleet pins and converge.
