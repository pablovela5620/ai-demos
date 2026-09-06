#!/usr/bin/env bash
set -euo pipefail

export CGO_ENABLED=0
export GOTOOLCHAIN=local

cd internal/site
bun install --frozen-lockfile
bun test src/components/systems-table/gpu-usage.test.ts
bun run build
cd ../..

# Regression checks are part of the build, including CI builds using --no-test.
go test -tags testing ./internal/hub/systems -run TestOverviewReportsCurrentGPUCount -count=1
mkdir -p "$PREFIX/bin"
GOOS=linux GOARCH=amd64 go build -trimpath -ldflags='-w -s' -o "$PREFIX/bin/beszel" ./internal/cmd/hub
