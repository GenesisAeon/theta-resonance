"""Turing reaction-diffusion evolution of the entropic resistance field."""

from __future__ import annotations

from .constants import DIFFUSION_COEFF, RD_DECAY_RATE
from .network_graph import NetworkGraph


class ReactionDiffusionField:
    """
    Evolves the resistance field via Turing reaction-diffusion:

        dρ_ij/dt = D · ∇²ρ_ij − k · Γ_ij · ρ_ij + f(load_ij)

    ∇²ρ_ij ≈ mean(ρ of adjacent edges) − ρ_ij  (graph Laplacian)
    f(load)  = load / 10  (load-driven resistance production)

    One call to `step()` advances the field by time increment dt.
    """

    def __init__(
        self, D: float = DIFFUSION_COEFF, k: float = RD_DECAY_RATE, dt: float = 0.1
    ) -> None:
        self._D = D
        self._k = k
        self._dt = dt

    def step(self, graph: NetworkGraph) -> None:
        """Advance resistance field by one time step dt."""
        edges = graph.edges()
        if not edges:
            return

        # Build adjacency map: edge → list of incident edges (sharing a node)
        deltas: dict[tuple[int, int], float] = {}
        for u, v in edges:
            rho_uv = graph.resistance(u, v)
            # Laplacian term: mean of adjacent-edge resistances
            adj_rhos = self._adjacent_resistances(graph, u, v)
            laplacian = (sum(adj_rhos) / len(adj_rhos) - rho_uv) if adj_rhos else 0.0
            # Reaction term
            gamma_ij = graph.gamma_ij(u, v)
            reaction = -self._k * gamma_ij * rho_uv
            # Source term from traffic load
            source = graph.load(u, v) / 10.0
            deltas[(u, v)] = self._dt * (self._D * laplacian + reaction + source)

        for (u, v), d in deltas.items():
            new_rho = max(0.05, graph.resistance(u, v) + d)
            graph.set_resistance(u, v, new_rho)

    def _adjacent_resistances(
        self, graph: NetworkGraph, u: int, v: int
    ) -> list[float]:
        """Resistances of all edges incident to u or v, excluding (u,v) itself."""
        result = []
        for node in (u, v):
            for nb in graph.neighbors(node):
                if not (nb == u and node == v) and not (nb == v and node == u):
                    result.append(graph.resistance(node, nb))
        return result
