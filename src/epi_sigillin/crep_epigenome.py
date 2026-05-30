"""Epigenetically modified CREP tensor — integrates methylation + histone marks."""

from __future__ import annotations

import math
from typing import Any

from .constants import CREP_COUPLING
from .histone_model import HistoneModificationModel
from .methylation import CREPMethylationEngine


class CREPEpigenome:
    """
    Combines methylation state and histone modifications to produce
    an epigenetically modulated effective CREP tensor.

    Γ_eff = arctanh(η_eff) / σ  where
    η_eff = geometric mean of (C_eff, R_eff, E_eff, P_eff)
    """

    def __init__(self) -> None:
        self._methylation = CREPMethylationEngine()
        self._histones = HistoneModificationModel()

    def step(
        self,
        crep_state: dict[str, Any],
        h: float,
        h_star: float,
        k: float,
        dt: float = 1.0,
    ) -> dict[str, Any]:
        self._methylation.step(crep_state, h, h_star, dt)
        active_marks = self._histones.evaluate(h, h_star, k)
        meth_eff = self._methylation.effective_crep(crep_state)
        histone_mods = self._histones.modifiers()

        combined: dict[str, float] = {}
        for comp in ("C", "R", "E", "P"):
            combined[comp] = round(
                float(meth_eff.get(comp, 0.0)) * histone_mods.get(comp, 1.0), 6
            )

        product = 1.0
        for comp in ("C", "R", "E", "P"):
            product *= max(combined[comp], 0.0)
        eta = product ** 0.25
        gamma_eff = math.atanh(min(eta, 0.9999)) / CREP_COUPLING if eta > 0 else 0.0

        return {
            **combined,
            "Gamma": round(gamma_eff, 6),
            "active_marks": active_marks,
            "methylation": self._methylation.methylation_state(),
        }

    def methylation_state(self) -> dict[str, float]:
        return self._methylation.methylation_state()

    def active_marks(self) -> list[str]:
        return self._histones.active_marks()

    def reset(self) -> None:
        self._methylation.reset()

    def set_methylation(self, state: dict[str, float]) -> None:
        self._methylation.set_state(state)
