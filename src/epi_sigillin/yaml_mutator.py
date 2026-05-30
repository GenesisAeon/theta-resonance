"""Runtime YAML parameter file rewriter — thread-safe with version history."""

from __future__ import annotations

import copy
import threading
from pathlib import Path
from typing import Any

import yaml


class RuntimeYAMLMutator:
    """
    Safely rewrites CREP YAML parameter files at runtime based on entropy level.

    Maintains an in-memory version history (up to max_history snapshots).
    The system literally rewrites its own config, implementing Gemini's insight:
    "das systemische Entropie-Niveau schreibt CREP-YAML während der Laufzeit um".

    File I/O is optional — operates in-memory when no path is provided.
    """

    def __init__(self, max_history: int = 50) -> None:
        self._lock = threading.Lock()
        self._history: list[dict[str, Any]] = []
        self._max_history = max_history

    def mutate(
        self,
        params: dict[str, Any],
        entropy_level: float,
        s_optimal: float,
        s_max: float,
        target_path: str | None = None,
    ) -> dict[str, Any]:
        """
        Rewrite params according to entropy_level relative to s_optimal / s_max.

        High entropy → suppress P-component strength, reduce learning rates.
        Low entropy  → enhance E-component multiplier, increase exploration.
        """
        mutated = copy.deepcopy(params)
        ratio = min(entropy_level / max(s_max, 1e-9), 1.0)
        excess = max(entropy_level - s_optimal, 0.0) / max(s_max, 1e-9)
        deficit = max(s_optimal - entropy_level, 0.0) / max(s_max, 1e-9)

        crep = mutated.get("crep", {})
        if "P" in crep:
            crep["P"] = round(float(crep["P"]) * (1.0 - 0.5 * excess), 6)
        if "E" in crep:
            crep["E"] = round(float(crep["E"]) * (1.0 + 0.3 * deficit), 6)
        mutated["crep"] = crep
        mutated["_entropy_ratio"] = round(ratio, 4)
        mutated["_mutated_by"] = "epi-sigillin"

        with self._lock:
            self._history.append(copy.deepcopy(mutated))
            if len(self._history) > self._max_history:
                self._history.pop(0)

        if target_path is not None:
            self._write(mutated, Path(target_path))

        return mutated

    def restore(self, version: int = -1) -> dict[str, Any]:
        with self._lock:
            if not self._history:
                return {}
            return copy.deepcopy(self._history[version])

    def history_len(self) -> int:
        return len(self._history)

    @staticmethod
    def _write(data: dict[str, Any], path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w") as f:
            yaml.dump(data, f, allow_unicode=True, sort_keys=False)

    @staticmethod
    def load(path: str | Path) -> dict[str, Any]:
        with Path(path).open() as f:
            return dict(yaml.safe_load(f) or {})
