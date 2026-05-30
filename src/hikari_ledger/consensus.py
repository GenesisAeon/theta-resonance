"""Proof-of-Resonance consensus engine."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING, Any

from .block import Block
from .constants import H_STAR_BFT

if TYPE_CHECKING:
    from .node import ValidatorNode


class ProofOfResonanceConsensus:
    """
    PoR consensus: a block is accepted when the sum of CREP weights of
    agreeing nodes exceeds the BFT threshold (2/3).

    Byzantine nodes are simulated by flipping their vote with probability
    equal to their byzantine fraction.
    """

    def __init__(self, byzantine_fraction: float = 0.0, seed: int = 42) -> None:
        self._byz_frac = min(byzantine_fraction, 0.49)
        self._rng = random.Random(seed)
        self._bft_threshold = H_STAR_BFT

    def select_validator(
        self, nodes: list["ValidatorNode"], weights: dict[str, float]
    ) -> "ValidatorNode":
        """Weighted-random selection of the block proposer."""
        eligible = [n for n in nodes if n.node_id in weights]
        if not eligible:
            return nodes[0]
        wvals = [weights[n.node_id] for n in eligible]
        return self._rng.choices(eligible, weights=wvals, k=1)[0]

    def run_consensus(
        self,
        block_index: int,
        block_data: dict[str, Any],
        nodes: list["ValidatorNode"],
        weights: dict[str, float],
        network_crep_mean: float,
    ) -> tuple[Block | None, bool, float]:
        """
        Propose and vote on a block.

        Returns (block_or_None, accepted, weighted_agreement).
        """
        if not nodes:
            return None, False, 0.0

        proposer = self.select_validator(nodes, weights)
        prev_hash = ""

        weighted_yes = 0.0
        for node in nodes:
            if node.node_id not in weights:
                continue
            w = weights[node.node_id]
            is_byzantine = self._rng.random() < self._byz_frac
            vote_yes = not is_byzantine  # honest nodes always agree (simulation)
            if vote_yes:
                weighted_yes += w

        accepted = weighted_yes > self._bft_threshold

        block = Block(
            index=block_index,
            data=block_data,
            validator_id=proposer.node_id,
            validator_gamma=proposer.crep.Gamma,
            network_crep_mean=network_crep_mean,
            weighted_agreement=weighted_yes,
            prev_hash=prev_hash,
        )
        return block, accepted, weighted_yes
