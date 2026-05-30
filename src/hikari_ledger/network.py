"""P2P network simulation for hikari-ledger."""

from __future__ import annotations

from typing import Any

from .node import ValidatorNode


class NetworkSimulator:
    """
    Simulates a P2P network of PoR validator nodes.

    Nodes are created from sequential seeds so that the network is
    reproducible.  Each call to `tick()` runs one UTAC cycle on every
    node, updating CREP states.
    """

    def __init__(self, n_nodes: int = 50, base_seed: int = 42) -> None:
        self.nodes: list[ValidatorNode] = [
            ValidatorNode.from_seed(base_seed + i, node_id=f"node-{i:04d}")
            for i in range(n_nodes)
        ]

    def tick(self) -> None:
        """Advance all nodes by one UTAC cycle."""
        for node in self.nodes:
            node.run_utac_cycle()

    def eligible_nodes(self) -> list[ValidatorNode]:
        return [n for n in self.nodes if n.is_eligible()]

    def crep_distribution(self) -> dict[str, Any]:
        gammas = [n.crep.Gamma for n in self.eligible_nodes()]
        if not gammas:
            return {"mean": 0.0, "min": 0.0, "max": 0.0, "count": 0}
        return {
            "mean": sum(gammas) / len(gammas),
            "min": min(gammas),
            "max": max(gammas),
            "count": len(gammas),
        }
