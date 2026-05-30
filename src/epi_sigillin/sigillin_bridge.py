"""Interface to static Sigillin YAML parameter files."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

DEFAULT_CREP_PARAMS: dict[str, Any] = {
    "crep": {"C": 0.5, "R": 0.5, "E": 0.5, "P": 0.5},
    "utac": {
        "H_init": 5.0,
        "H_star": 5.0,
        "K": 10.0,
        "r": 0.05,
        "sigma": 2.2,
    },
    "meta": {
        "package": 28,
        "name": "epi-sigillin",
        "version": "0.2.0",
    },
}


class SigillinBridge:
    """
    Reads static Sigillin YAML files and provides base CREP parameters.
    Falls back to DEFAULT_CREP_PARAMS when no file is found.
    """

    def __init__(self, yaml_path: str | Path | None = None) -> None:
        self._path = Path(yaml_path) if yaml_path else None
        self._params: dict[str, Any] = self._load()

    def _load(self) -> dict[str, Any]:
        if self._path is not None and self._path.exists():
            with self._path.open() as f:
                loaded = yaml.safe_load(f)
            if isinstance(loaded, dict):
                return loaded
        return dict(DEFAULT_CREP_PARAMS)

    def base_crep(self) -> dict[str, Any]:
        return dict(self._params.get("crep", DEFAULT_CREP_PARAMS["crep"]))

    def base_utac(self) -> dict[str, Any]:
        return dict(self._params.get("utac", DEFAULT_CREP_PARAMS["utac"]))

    def all_params(self) -> dict[str, Any]:
        return dict(self._params)

    def save(self, params: dict[str, Any], path: str | Path | None = None) -> Path:
        target = Path(path or self._path or "sigillin_params.yaml")
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("w") as f:
            yaml.dump(params, f, allow_unicode=True, sort_keys=False)
        return target
