"""Packet data structure with CREP metadata (Package 30)."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Packet:
    """
    A routed data packet carrying CREP-field metadata.

    path      — list of node IDs traversed (populated by DiffusiveRouter)
    latency   — total entropic resistance along the path (proxy for delay)
    delivered — True once the packet reaches its destination
    """

    src: int
    dst: int
    payload_bytes: int = 64
    path: list[int] = field(default_factory=list)
    latency: float = 0.0
    delivered: bool = False
    congestion_reroutes: int = 0

    @property
    def hop_count(self) -> int:
        return max(0, len(self.path) - 1)
