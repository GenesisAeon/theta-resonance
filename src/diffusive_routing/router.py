"""Diffusive routing engine — Dijkstra on entropic resistance field."""

from __future__ import annotations

import heapq
import math

from .network_graph import NetworkGraph
from .packet import Packet


class DiffusiveRouter:
    """
    Routes packets along minimum entropic resistance paths.

    Uses a modified Dijkstra with ρ_ij as the edge weight.
    Packets "evaporate" from high-resistance regions into low-resistance
    regions — Turing diffusion applied to network traffic (see
    reaction_diffusion.py for the field evolution).

    A shortest-path (hop-count) baseline is also computed for benchmark
    comparison.
    """

    def route(self, graph: NetworkGraph, packet: Packet) -> Packet:
        """
        Find the minimum-resistance path from packet.src to packet.dst.

        Returns the packet with .path, .latency, .delivered populated.
        """
        path, latency = self._dijkstra_resistance(graph, packet.src, packet.dst)
        packet.path = path
        packet.latency = latency
        packet.delivered = len(path) > 0

        if packet.delivered:
            for i in range(len(path) - 1):
                graph.add_load(path[i], path[i + 1])

        return packet

    def shortest_hop_path_length(self, graph: NetworkGraph, src: int, dst: int) -> int:
        """BFS hop count for the baseline comparison."""
        if src == dst:
            return 0
        visited = {src}
        queue = [(src, 0)]
        while queue:
            node, hops = queue.pop(0)
            for nb in graph.neighbors(node):
                if nb == dst:
                    return hops + 1
                if nb not in visited:
                    visited.add(nb)
                    queue.append((nb, hops + 1))
        return -1   # unreachable

    # ── private ───────────────────────────────────────────────────────────────

    def _dijkstra_resistance(
        self, graph: NetworkGraph, src: int, dst: int
    ) -> tuple[list[int], float]:
        dist: dict[int, float] = {src: 0.0}
        prev: dict[int, int | None] = {src: None}
        heap: list[tuple[float, int]] = [(0.0, src)]

        while heap:
            d, u = heapq.heappop(heap)
            if d > dist.get(u, math.inf):
                continue
            if u == dst:
                break
            for v in graph.neighbors(u):
                rho = graph.resistance(u, v)
                nd = d + rho
                if nd < dist.get(v, math.inf):
                    dist[v] = nd
                    prev[v] = u
                    heapq.heappush(heap, (nd, v))

        if dst not in dist:
            return [], math.inf

        # Reconstruct path
        path: list[int] = []
        node: int | None = dst
        while node is not None:
            path.append(node)
            node = prev.get(node)
        path.reverse()
        return path, dist[dst]
