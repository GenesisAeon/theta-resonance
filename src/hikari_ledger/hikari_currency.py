"""Hikari token minting from CREP resonance contribution."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

from .constants import HIKARI_EMISSION_RATE

if TYPE_CHECKING:
    from .node import ValidatorNode


class HikariCurrencyMinter:
    """
    Mints Hikari tokens proportional to CREP resonance.

    ΔH_i = k · Γ_i · (1 - S_H)
    where S_H = supply entropy = -Σ (b_i/B) · log(b_i/B + ε)
    and B = total supply.

    High-CREP validators earn more Hikari; supply entropy dampens
    emission as the distribution becomes saturated.
    """

    def __init__(self, emission_rate: float = HIKARI_EMISSION_RATE) -> None:
        self._k = emission_rate
        self._total_supply: float = 0.0

    def _supply_entropy(self, nodes: list[ValidatorNode]) -> float:
        total = max(sum(n.hikari_balance for n in nodes), 1e-9)
        s = 0.0
        for n in nodes:
            p = n.hikari_balance / total
            if p > 0:
                s -= p * math.log(p + 1e-12)
        # Normalise to [0, 1] via max possible entropy = log(n_nodes)
        n_nodes = max(len(nodes), 1)
        max_s = math.log(n_nodes + 1e-12)
        return s / max_s if max_s > 0 else 0.0

    def mint(self, validator: ValidatorNode, all_nodes: list[ValidatorNode]) -> float:
        s_h = self._supply_entropy(all_nodes)
        emission = self._k * validator.crep.Gamma * (1.0 - s_h)
        emission = max(0.0, emission)
        validator.hikari_balance += emission
        self._total_supply += emission
        return emission

    @property
    def total_supply(self) -> float:
        return self._total_supply
