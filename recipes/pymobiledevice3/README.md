# pymobiledevice3

The initial package targets `osx-arm64` and Python 3.13. This keeps the
platform/Python markers aligned with the dependency set tested on the Mac mini.
Do not remove the platform restriction without adding the non-macOS dependencies
(including the appropriate video and compression libraries) and testing them.

The accompanying recipes provide dependencies missing from conda-forge, a newer
`construct-typing`, and a noarch `enum-compat` usable with Python 3.13. Recheck
conda-forge before adding or updating a dependency recipe.

Packaging corrections found by the CLI tests:

- Apple TSS signing requests use HTTPS with certificate verification. The upstream
  HTTP endpoint was redirected to an ISP page on the test host and could not sign
  the developer image.
- `asgiwebdav` needs `python-dotenv`, `backports.zstd`, and `uvicorn` at runtime.
- `remotezip2` imports `requests`; `srptools` needs `click` for its CLI.
- `developer-disk-image` and `opack2` declare entry points whose modules are absent
  from the source release. Patches remove those entry points; their library APIs
  remain available to pymobiledevice3.
- Some upstream archives omit a license file despite declaring a license in
  package metadata. The recipes preserve that declaration without inventing a file.

Build with tests enabled, using a local output channel so sibling dependencies
resolve. The repository-wide CI build skips tests; local package tests and a clean
conda-only installation are required for this dependency set before publishing.

The hardware smoke test must use the packaged CLI: discover and identify the USB
device, capture its screen, open Calculator, perform a known calculation with touch
input, inspect the result, and return Home. Save before/after screenshots outside
the repository. Report a blocked action as blocked. CLI exit status alone is
insufficient: some device errors exit zero.

On the tested iPhone 12 Pro / iOS 26.2.1, direct HID touch fails with CoreDevice
error 9021 (requires iOS 27), even with the `27A5228h` DDI. Screenshots, app launch,
and Home-button input work. Touch on this OS needs a separately signed and
installed WebDriverAgent. The agent skill records this boundary and the macOS
system-root export needed when Python cannot validate Apple's TSS certificate.

Pairing, Developer Mode, and developer-image mounting are runtime setup steps,
not package installation side effects. No device identifier or pairing record
belongs in a recipe or fleet manifest.
