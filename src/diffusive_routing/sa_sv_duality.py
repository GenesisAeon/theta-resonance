"""S_A / S_V entropy duality for diffusive-routing (Package 30)."""

from __future__ import annotations

import math

from .network_graph import NetworkGraph


class SAVDuality:
    """
    Implements the S_A / S_V entropy duality.

    S_A(path) = action entropy  = Σ ρ_ij along path (routing cost)
    S_V(node) = volume entropy  = H(traffic distribution at node)
                                = -Σ p_k · log p_k  over outgoing flows

    Routing objective: minimise S_A while maximising S_V at destinations.
    This is a variational principle dual to the Unified Lagrangian:
    just as L = T - V + Φ + Γ governs physical dynamics,
    L_net = -S_A + S_V governs network routing dynamics.
    """

    def action_entropy(self, graph: NetworkGraph, path: list[int]) -> float:
        """S_A = total entropic resistance along path."""
        total = 0.0
        for i in range(len(path) - 1):
            total += graph.resistance(path[i], path[i + 1])
        return total

    def volume_entropy(self, graph: NetworkGraph, node: int) -> float:
        """
        S_V(node) = Shannon entropy of normalised outgoing load distribution.

        Higher S_V means more evenly distributed outgoing traffic (better balance).
        """
        nbs = graph.neighbors(node)
        if not nbs:
            return 0.0
        loads = [max(graph.load(node, nb), 1e-12) for nb in nbs]
        total = sum(loads)
        probs = [load / total for load in loads]
        return -sum(p * math.log(p) for p in probs if p > 0)

    def network_lagrangian(
        self, graph: NetworkGraph, paths: list[list[int]]
    ) -> float:
        """
        L_net = mean(S_V at destination nodes) - mean(S_A of all paths).

        Higher L_net → better routing (low action cost, high destination diversity).
        """
        if not paths:
            return 0.0
        mean_sa = sum(self.action_entropy(graph, p) for p in paths) / len(paths)
        dst_sv = sum(self.volume_entropy(graph, p[-1]) for p in paths if p) / len(paths)
        return dst_sv - mean_sa

    def path_entropy(self, hop_counts: list[int]) -> float:
        """
        Shannon entropy of the hop-count distribution across all routed packets.

        Used as the CREP P-component (routing diversity measure).
        """
        if not hop_counts:
            return 0.0
        counts: dict[int, int] = {}
        for h in hop_counts:
            counts[h] = counts.get(h, 0) + 1
        n = len(hop_counts)
        return -sum((c / n) * math.log(c / n) for c in counts.values())
