"""Network topology for diffusive-routing (NetworkX-based)."""

from __future__ import annotations

import random


class NetworkGraph:
    """
    Undirected weighted graph representing the network topology.

    Each edge carries a mutable resistance value ρ_ij and a CREP modulation
    factor Γ_ij.  Nodes carry a volume-entropy S_V value.
    """

    def __init__(self, n_nodes: int = 20, seed: int = 42) -> None:
        self._rng = random.Random(seed)
        self._n_nodes = n_nodes
        self._edges: dict[tuple[int, int], dict[str, float]] = {}
        self._node_sv: dict[int, float] = {}
        self._build_fat_tree_like(n_nodes)

    # ── construction ───────────────────────────────────────────────────────────

    def _build_fat_tree_like(self, n: int) -> None:
        """Erdős–Rényi graph with p chosen so average degree ≈ 5."""
        p = min(0.35, 5.0 / max(n - 1, 1))
        for i in range(n):
            self._node_sv[i] = self._rng.uniform(0.3, 0.9)
            for j in range(i + 1, n):
                if self._rng.random() < p:
                    self._set_edge(i, j, resistance=1.0, gamma=0.443)
        # Ensure the graph is connected via a ring backbone
        for i in range(n):
            j = (i + 1) % n
            if not self.has_edge(i, j):
                self._set_edge(i, j, resistance=1.0, gamma=0.443)

    def _set_edge(self, u: int, v: int, resistance: float, gamma: float) -> None:
        key = (min(u, v), max(u, v))
        self._edges[key] = {"resistance": resistance, "gamma": gamma, "load": 0.0}

    # ── queries ────────────────────────────────────────────────────────────────

    def nodes(self) -> list[int]:
        return list(range(self._n_nodes))

    def edges(self) -> list[tuple[int, int]]:
        return list(self._edges.keys())

    def has_edge(self, u: int, v: int) -> bool:
        return (min(u, v), max(u, v)) in self._edges

    def neighbors(self, u: int) -> list[int]:
        result = []
        for i, j in self._edges:
            if i == u:
                result.append(j)
            elif j == u:
                result.append(i)
        return result

    def resistance(self, u: int, v: int) -> float:
        key = (min(u, v), max(u, v))
        return self._edges[key]["resistance"]

    def gamma_ij(self, u: int, v: int) -> float:
        key = (min(u, v), max(u, v))
        return self._edges[key]["gamma"]

    def node_sv(self, node: int) -> float:
        return self._node_sv[node]

    # ── mutations ─────────────────────────────────────────────────────────────

    def set_resistance(self, u: int, v: int, rho: float) -> None:
        key = (min(u, v), max(u, v))
        if key in self._edges:
            self._edges[key]["resistance"] = max(rho, 1e-6)

    def set_gamma_ij(self, u: int, v: int, gamma: float) -> None:
        key = (min(u, v), max(u, v))
        if key in self._edges:
            self._edges[key]["gamma"] = max(gamma, 0.0)

    def add_load(self, u: int, v: int, amount: float = 1.0) -> None:
        key = (min(u, v), max(u, v))
        if key in self._edges:
            self._edges[key]["load"] += amount

    def load(self, u: int, v: int) -> float:
        key = (min(u, v), max(u, v))
        return self._edges[key]["load"]

    def reset_loads(self) -> None:
        for key in self._edges:
            self._edges[key]["load"] = 0.0

    def load_distribution(self) -> list[float]:
        return [e["load"] for e in self._edges.values()]
