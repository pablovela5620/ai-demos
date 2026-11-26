#!/bin/bash
set -euxo pipefail

cd "${SRC_DIR}"

# npm install --global from a local directory creates symlinks instead of
# copying files. Pack first to get a tarball, then install from it so npm
# copies everything into the prefix.
TARBALL=$(npm pack --ignore-scripts 2>/dev/null)
npm install --global --prefix "${PREFIX}" --ignore-scripts "${SRC_DIR}/${TARBALL}"

# noarch packages cannot contain symlinks. Replace the npm bin symlink with a
# wrapper that runs the CLI with this environment's node, and drop npm's nested
# .bin shortcuts (nothing calls them).
target=$(readlink "${PREFIX}/bin/playwright-cli")
rm "${PREFIX}/bin/playwright-cli"
cat > "${PREFIX}/bin/playwright-cli" <<WRAPPER
#!/bin/sh
here=\$(cd "\$(dirname "\$0")" && pwd)
exec "\$here/node" "\$here/${target}" "\$@"
WRAPPER
chmod 755 "${PREFIX}/bin/playwright-cli"
rm -f "${PREFIX}"/lib/node_modules/@playwright/cli/node_modules/.bin/playwright \
      "${PREFIX}"/lib/node_modules/@playwright/cli/node_modules/.bin/playwright-core
