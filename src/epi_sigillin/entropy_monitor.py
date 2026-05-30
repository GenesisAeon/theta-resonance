"""Real-time system entropy tracker for epi-sigillin."""

from __future__ import annotations

import math
from collections import deque
from typing import Any


class EntropyMonitor:
    """
    Tracks Shannon entropy of the combined CREP state distribution
    across recent cycles. H(t) = -Σ p_i · log(p_i) over CREP components.
    """

    def __init__(self, window_size: int = 20) -> None:
        self._window: deque[dict[str, float]] = deque(maxlen=window_size)
        self._current_entropy: float = 0.0

    def update(self, crep_state: dict[str, Any]) -> float:
        components = ("C", "R", "E", "P")
        vals = [max(float(crep_state.get(k, 0.0)), 1e-9) for k in components]
        total = sum(vals)
        probs = [v / total for v in vals]
        h = -sum(p * math.log(p) for p in probs if p > 0)
        self._window.append({k: float(crep_state.get(k, 0.0)) for k in components})
        self._current_entropy = h
        return h

    def current(self) -> float:
        return self._current_entropy

    def mean(self) -> float:
        if not self._window:
            return 0.0
        entropies: list[float] = []
        for state in self._window:
            vals = [max(v, 1e-9) for v in state.values()]
            total = sum(vals)
            probs = [v / total for v in vals]
            entropies.append(-sum(p * math.log(p) for p in probs if p > 0))
        return sum(entropies) / len(entropies)

    def trend(self) -> float:
        """Positive = entropy rising, negative = falling."""
        if len(self._window) < 4:
            return 0.0
        history = list(self._window)
        n = len(history)
        mid = n // 2
        early: list[float] = []
        late: list[float] = []
        for state in history[:mid]:
            vals = [max(v, 1e-9) for v in state.values()]
            total = sum(vals)
            probs = [v / total for v in vals]
            early.append(-sum(p * math.log(p) for p in probs if p > 0))
        for state in history[mid:]:
            vals = [max(v, 1e-9) for v in state.values()]
            total = sum(vals)
            probs = [v / total for v in vals]
            late.append(-sum(p * math.log(p) for p in probs if p > 0))
        return (sum(late) / len(late)) - (sum(early) / len(early))
