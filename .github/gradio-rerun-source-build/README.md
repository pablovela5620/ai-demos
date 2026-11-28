# Rebuild the temporary gradio-rerun 0.42.0.post1 wheel

The normal `recipes/gradio-rerun` recipe packages a checksum-pinned wheel from
a GitHub release. It does not build the frontend.

This directory keeps the one frontend patch that wheel adds to gradio-rerun
0.42.0: `frontend/Index.svelte` queues value loads, so the segments of a
streamed recording reach the Rerun viewer in the order the app sent them.

To rebuild:

```sh
git clone --branch 0.42.0 https://github.com/rerun-io/gradio-rerun-viewer.git
cd gradio-rerun-viewer
git apply ../gradio-rerun-0.42.0-ordered-loads.patch
sed -i 's/^version = "0.42.0"$/version = "0.42.0.post1"/' pyproject.toml
(cd frontend && pnpm install --frozen-lockfile)
gradio cc build --no-generate-docs   # gradio 6.31.0, Node 22, pnpm 10, this checkout installed editable
```

The wheel lands in `dist/`. Its Python files and viewer bundle must match PyPI
`gradio-rerun==0.42.0` byte for byte; only `templates/component/index.js`
differs. Use a new release tag and checksum for a replacement; do not replace
existing assets.
