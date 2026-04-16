set -e
pip install submodules/simple-knn submodules/diff-gaussian-rasterization --no-deps --no-build-isolation
pip install . --no-deps --no-build-isolation
