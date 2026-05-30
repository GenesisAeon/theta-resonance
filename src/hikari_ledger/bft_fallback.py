"""BFT fallback for low-CREP networks."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .constants import H_STAR_BFT, MIN_CREP_TO_VALIDATE

if TYPE_CHECKING:
    from .node import ValidatorNode


class BFTFallback:
    """
    Equal-weight BFT consensus used when average network CREP falls
    below MIN_CREP_TO_VALIDATE — reverts to classical PBFT majority vote.
    """

    def should_activate(self, nodes: list["ValidatorNode"]) -> bool:
        eligible = [n for n in nodes if n.is_eligible()]
        if not eligible:
            return True
        mean_gamma = sum(n.crep.Gamma for n in eligible) / len(eligible)
        return mean_gamma < MIN_CREP_TO_VALIDATE

    def equal_weights(self, nodes: list["ValidatorNode"]) -> dict[str, float]:
        eligible = [n for n in nodes if n.is_eligible()]
        if not eligible:
            return {}
        w = 1.0 / len(eligible)
        return {n.node_id: w for n in eligible}

    def consensus_result(
        self,
        nodes: list["ValidatorNode"],
        block_data: dict[str, Any],
        byzantine_fraction: float = 0.0,
    ) -> tuple[bool, float]:
        weights = self.equal_weights(nodes)
        weighted_yes = sum(w for w in weights.values()) * (1.0 - byzantine_fraction)
        accepted = weighted_yes > H_STAR_BFT
        return accepted, weighted_yes
