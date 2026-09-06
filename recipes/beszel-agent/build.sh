#!/usr/bin/env bash
set -euo pipefail

if [[ -f beszel-agent.exe ]]; then
  mkdir -p "$PREFIX/Library/bin"
  cp beszel-agent.exe "$PREFIX/Library/bin/beszel-agent.exe"
else
  mkdir -p "$PREFIX/bin"
  install -m 755 beszel-agent "$PREFIX/bin/beszel-agent"
fi
