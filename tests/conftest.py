"""Shared helpers: repository paths and loaders for the dashed-name CI scripts and workflows."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import yaml

ROOT: Path = Path(__file__).parent.parent


def load_script(name: str) -> ModuleType:
    """Import ``.github/scripts/<name>.py`` (file names with dashes are not importable)."""
    path: Path = ROOT / ".github" / "scripts" / f"{name}.py"
    module_name: str = name.replace("-", "_")
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None and spec.loader is not None
    module: ModuleType = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def load_yaml(relative_path: str) -> dict[str, Any]:
    """Load a YAML mapping (workflow or recipe) relative to the repository root."""
    data: object = yaml.safe_load((ROOT / relative_path).read_text(encoding="utf-8"))
    assert isinstance(data, dict), f"{relative_path} must be a mapping"
    return data
