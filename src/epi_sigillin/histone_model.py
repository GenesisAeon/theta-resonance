"""Histone modification analogy for CREP components."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class HistoneMark:
    name: str        # e.g. "H3K4me3"
    effect: str      # "activation" or "repression"
    target: str      # CREP component: "C", "R", "E", "P"
    strength: float  # 0.0–1.0


HISTONE_MARKS = [
    HistoneMark("H3K4me3",  "activation",  "E", 1.0),   # active enhancer → Emergence
    HistoneMark("H3K27me3", "repression",  "P", 1.0),   # polycomb → suppress Poetics
    HistoneMark("H3K9me3",  "repression",  "C", 1.0),   # heterochromatin → freeze Coherence
    HistoneMark("H3K36me3", "activation",  "R", 0.8),   # transcribed gene body → Resonance
    HistoneMark("H3K27ac",  "activation",  "C", 0.9),   # active enhancer → Coherence
]


class HistoneModificationModel:
    """
    Maps entropy levels to histone-mark-like CREP modifiers.

    Low entropy (productive phase):   H3K4me3 / H3K27ac set → E and C activated
    High entropy (crisis phase):      H3K27me3 / H3K9me3 set → P and C repressed
    Extreme entropy (shutdown):       all repression marks → CREP hibernation
    """

    def __init__(self) -> None:
        self._active_marks: set[str] = set()

    def evaluate(self, h: float, h_star: float, k: float) -> list[str]:
        ratio = h / max(k, 1e-9)
        self._active_marks.clear()
        if ratio < 0.3:
            self._active_marks.update(["H3K4me3", "H3K27ac", "H3K36me3"])
        elif ratio < 0.6:
            self._active_marks.update(["H3K36me3", "H3K4me3"])
        elif ratio < 0.85:
            self._active_marks.update(["H3K27me3"])
        else:
            self._active_marks.update(["H3K27me3", "H3K9me3"])
        return list(self._active_marks)

    def modifiers(self) -> dict[str, float]:
        """Returns per-CREP-component multiplier (<1 = repressed, >1 = activated)."""
        result = {"C": 1.0, "R": 1.0, "E": 1.0, "P": 1.0}
        for mark in HISTONE_MARKS:
            if mark.name in self._active_marks:
                if mark.effect == "activation":
                    # Allow multipliers above 1.0 so low-entropy activation enhances E/C/R.
                    result[mark.target] = min(2.0, result[mark.target] * (1 + mark.strength * 0.2))
                else:
                    result[mark.target] = max(0.0, result[mark.target] * (1 - mark.strength * 0.5))
        return result

    def active_marks(self) -> list[str]:
        return list(self._active_marks)

    def apply(self, crep_state: dict[str, Any]) -> dict[str, float]:
        mods = self.modifiers()
        return {
            comp: round(float(crep_state.get(comp, 0.0)) * mods.get(comp, 1.0), 6)
            for comp in ("C", "R", "E", "P")
        }
