"""Per-link CREP tensor for diffusive-routing."""

from __future__ import annotations

import math
import random

from .constants import SIGMA
from .network_graph import NetworkGraph


class CREPNetworkState:
    """Holds CREP components {C, R, E, P, Gamma} aggregated across all links."""

    __slots__ = ("C", "R", "E", "P", "Gamma")

    def __init__(
        self, C: float = 0.0, R: float = 0.0, E: float = 0.0, P: float = 0.0
    ) -> None:
        self.C = C
        self.R = R
        self.E = E
        self.P = P
        self.Gamma = math.atanh(min(max((C * R * E * P) ** 0.25, 1e-9), 1 - 1e-9)) / SIGMA


class NetworkCREPEvaluator:
    """
    Evaluates the per-link CREP components and aggregates to a network state.

    C = path coherence — stability of resistance field over time
    R = resonance between packet demand and available capacity
    E = emergent routing efficiency (vs. shortest-path baseline)
    P = entropy of path-length distribution
    """

    def __init__(self, seed: int = 42) -> None:
        self._rng = random.Random(seed)
        self._prev_resistances: dict[tuple[int, int], float] = {}

    def evaluate(
        self,
        graph: NetworkGraph,
        throughput_ratio: float,
        efficiency_vs_baseline: float,
        path_entropy: float,
    ) -> CREPNetworkState:
        edges = graph.edges()

        # C: coherence — 1 - mean relative change in resistance
        if self._prev_resistances:
            deltas = []
            for e in edges:
                prev = self._prev_resistances.get(e, graph.resistance(*e))
                curr = graph.resistance(*e)
                rel = abs(curr - prev) / (prev + 1e-9)
                deltas.append(rel)
            C = max(0.0, 1.0 - (sum(deltas) / len(deltas) if deltas else 0.0))
        else:
            C = 0.5

        self._prev_resistances = {e: graph.resistance(*e) for e in edges}

        # R: resonance — how close throughput is to H* = 0.75
        R = max(0.0, 1.0 - abs(throughput_ratio - 0.75) / 0.75)

        # E: emergence — routing efficiency gain over shortest-path
        E = min(1.0, max(0.0, efficiency_vs_baseline))

        # P: entropy of path-length distribution (normalised to [0,1])
        P = min(1.0, max(0.0, path_entropy))

        return CREPNetworkState(C=C, R=R, E=E, P=P)

    def update_link_gammas(self, graph: NetworkGraph, global_state: CREPNetworkState) -> None:
        """Modulate per-link Γ_ij based on load and global CREP."""
        for u, v in graph.edges():
            load_norm = min(graph.load(u, v) / 10.0, 1.0)
            gamma_ij = global_state.Gamma * (1.0 - 0.5 * load_norm)
            graph.set_gamma_ij(u, v, max(gamma_ij, 0.05))
