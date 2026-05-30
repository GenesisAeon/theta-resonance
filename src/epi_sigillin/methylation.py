"""Methylation/demethylation engine for CREP components."""

from __future__ import annotations

import math
from typing import Any

from .constants import ALPHA_DEFAULT, BETA_DEFAULT, CREP_COMPONENTS, DELTA_DEFAULT


class CREPMethylationEngine:
    """
    Epigenetic modification of CREP components via methylation state M_i ∈ [0, 1].

    dM_i/dt = α_i · max(H - H*, 0) - δ_i · M_i   (high entropy → methylation)
    dM_i/dt += -β_i · max(H* - H, 0) · M_i         (low entropy → demethylation)

    Effective CREP:
      Γ_eff = (C·(1-M_C) · R·(1-M_R) · E·(1-M_E) · P·(1-M_P))^(1/4)
    """

    def __init__(
        self,
        alpha: float = ALPHA_DEFAULT,
        delta: float = DELTA_DEFAULT,
        beta: float = BETA_DEFAULT,
    ) -> None:
        self._alpha = alpha
        self._delta = delta
        self._beta = beta
        self._M: dict[str, float] = {c: 0.0 for c in CREP_COMPONENTS}

    def step(
        self,
        crep_state: dict[str, Any],
        h: float,
        h_star: float,
        dt: float = 1.0,
    ) -> dict[str, float]:
        excess = max(h - h_star, 0.0)
        deficit = max(h_star - h, 0.0)
        for comp in CREP_COMPONENTS:
            m = self._M[comp]
            dm = self._alpha * excess - self._delta * m - self._beta * deficit * m
            self._M[comp] = max(0.0, min(1.0, m + dm * dt))
        return dict(self._M)

    def effective_crep(self, crep_state: dict[str, Any]) -> dict[str, float]:
        eff: dict[str, float] = {}
        product = 1.0
        for comp in CREP_COMPONENTS:
            raw = float(crep_state.get(comp, 0.0))
            e = raw * (1.0 - self._M[comp])
            eff[comp] = round(e, 6)
            product *= max(e, 0.0)
        gamma_eff = product ** (1.0 / 4.0)
        eff["Gamma"] = round(math.atanh(min(gamma_eff, 0.9999)) / 2.2, 6)
        return eff

    def methylation_state(self) -> dict[str, float]:
        return {f"M_{c}": round(v, 6) for c, v in self._M.items()}

    def set_state(self, state: dict[str, float]) -> None:
        for comp in CREP_COMPONENTS:
            key = f"M_{comp}"
            if key in state:
                self._M[comp] = float(state[key])

    def reset(self) -> None:
        self._M = {c: 0.0 for c in CREP_COMPONENTS}
