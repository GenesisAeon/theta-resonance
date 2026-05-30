"""Epigenetic memory — methylation inheritance across cycles."""

from __future__ import annotations

import copy
from typing import Any

from .constants import CREP_COMPONENTS, INHERITANCE_FRACTION


class EpigeneticMemory:
    """
    Stores methylation patterns across cycles (epigenetic inheritance).

    When a new cycle begins, inherits INHERITANCE_FRACTION (50%) of
    the parent cycle's methylation state. Allows learned adaptations to
    persist across genesis-os restarts — a simple non-genetic inheritance model.
    """

    def __init__(self, max_generations: int = 100) -> None:
        self._generations: list[dict[str, Any]] = []
        self._max_generations = max_generations

    def record(
        self, methylation_state: dict[str, float], metadata: dict[str, Any] | None = None
    ) -> int:
        entry = {
            "methylation": copy.deepcopy(methylation_state),
            "generation": len(self._generations),
            "metadata": metadata or {},
        }
        self._generations.append(entry)
        if len(self._generations) > self._max_generations:
            self._generations.pop(0)
        return entry["generation"]

    def inherit(self, parent_methylation: dict[str, float] | None = None) -> dict[str, float]:
        """
        Returns a methylation state for a new cycle — 50% inherited from parent.
        If parent_methylation is None, uses the most recent recorded generation.
        """
        if parent_methylation is None:
            if not self._generations:
                return {f"M_{c}": 0.0 for c in CREP_COMPONENTS}
            parent_methylation = self._generations[-1]["methylation"]

        inherited: dict[str, float] = {}
        for key, val in parent_methylation.items():
            inherited[key] = round(float(val) * INHERITANCE_FRACTION, 6)
        return inherited

    def generations(self) -> int:
        return len(self._generations)

    def last(self) -> dict[str, Any] | None:
        return copy.deepcopy(self._generations[-1]) if self._generations else None

    def mean_methylation(self) -> dict[str, float]:
        if not self._generations:
            return {f"M_{c}": 0.0 for c in CREP_COMPONENTS}
        keys = [f"M_{c}" for c in CREP_COMPONENTS]
        totals = dict.fromkeys(keys, 0.0)
        for gen in self._generations:
            m = gen["methylation"]
            for k in keys:
                totals[k] += m.get(k, 0.0)
        n = len(self._generations)
        return {k: round(v / n, 6) for k, v in totals.items()}
