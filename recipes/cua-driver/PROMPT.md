Repackage official prebuilt releases. Keep cua-driver and my-skill-forge's
agent-skill-cua-driver on the same release; update both fleet pins together.
Stable tags match cua-driver-rs-vX.Y.Z even when GitHub marks them prerelease.
Preserve the signed macOS app without binary relocation or re-signing. Fleet
sync deploys it as a real app at /Applications/CuaDriver.app. Do not run the
upstream installer or self-updater from the package build or install hooks.
Validate CLI smoke tests on all platforms and codesign on macOS before upload.
