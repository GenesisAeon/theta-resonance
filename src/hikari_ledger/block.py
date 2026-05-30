"""Block data structure with CREP metadata."""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Block:
    index: int
    data: dict[str, Any]
    validator_id: str
    validator_gamma: float
    network_crep_mean: float
    weighted_agreement: float   # Σ w_i for agreeing nodes
    timestamp: float = field(default_factory=time.time)
    prev_hash: str = ""
    block_hash: str = ""

    def __post_init__(self) -> None:
        if not self.block_hash:
            self.block_hash = self._compute_hash()

    def _compute_hash(self) -> str:
        payload = (
            f"{self.index}:{self.prev_hash}:"
            f"{self.validator_id}:{self.validator_gamma:.6f}:"
            f"{self.weighted_agreement:.6f}"
        )
        return hashlib.sha256(payload.encode()).hexdigest()[:24]

    def to_dict(self) -> dict[str, Any]:
        return {
            "index": self.index,
            "data": self.data,
            "validator_id": self.validator_id,
            "validator_gamma": round(self.validator_gamma, 6),
            "network_crep_mean": round(self.network_crep_mean, 6),
            "weighted_agreement": round(self.weighted_agreement, 6),
            "timestamp": self.timestamp,
            "prev_hash": self.prev_hash,
            "block_hash": self.block_hash,
        }
