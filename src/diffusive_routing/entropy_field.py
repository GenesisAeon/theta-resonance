"""Entropic resistance field over the network (Package 30)."""

from __future__ import annotations

from .constants import BASELINE_RESISTANCE
from .network_graph import NetworkGraph


class EntropicResistanceField:
    """
    Computes and updates the entropic resistance ρ_ij for each link.

    ρ_ij = baseline / (1 + Γ_ij · utilisation_coherence)

    Low ρ  → high-throughput, stable, high-CREP link → packets prefer it.
    High ρ → congested, unstable, low-CREP link → packets avoid it.

    The AFET entropy-production equation (3) is applied at link level:
    each link's entropic resistance evolves via reaction-diffusion (see
    reaction_diffusion.py); this class computes the instantaneous value.
    """

    def __init__(self, baseline: float = BASELINE_RESISTANCE) -> None:
        self._baseline = baseline

    def compute(self, graph: NetworkGraph) -> None:
        """Update ρ_ij for every edge in *graph* in-place."""
        for u, v in graph.edges():
            gamma_ij = graph.gamma_ij(u, v)
            load = graph.load(u, v)
            utilisation = min(load / 10.0, 1.0)   # normalise load to [0,1]
            coherence = 1.0 - 0.5 * utilisation    # high load → lower coherence
            rho = self._baseline / (1.0 + gamma_ij * coherence)
            graph.set_resistance(u, v, rho)

    def total_entropy(self, graph: NetworkGraph) -> float:
        """S_A = sum of entropic resistances (action entropy of the field)."""
        return sum(graph.resistance(*e) for e in graph.edges())

    def mean_resistance(self, graph: NetworkGraph) -> float:
        edges = graph.edges()
        if not edges:
            return 0.0
        return self.total_entropy(graph) / len(edges)
