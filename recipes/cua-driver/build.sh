#!/usr/bin/env bash
set -euo pipefail
mkdir -p "$PREFIX/bin" "$PREFIX/libexec/cua-driver" "$PREFIX/share/cua-driver"
if [[ "$target_platform" == osx-* ]]; then
    cp -R CuaDriver.app "$PREFIX/share/cua-driver/"
else
    install -m755 cua-driver cua-cursor-theme "$PREFIX/libexec/cua-driver/"
    cp -R wayland-helper "$PREFIX/libexec/cua-driver/"
fi
install -m755 "$RECIPE_DIR/cua-driver" "$PREFIX/bin/cua-driver"
