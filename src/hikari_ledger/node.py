"""PoR validator node — holds a CREP state and signing identity."""

from __future__ import annotations

import hashlib
import math
import random
from dataclasses import dataclass, field
from typing import Any

from .constants import MIN_CREP_TO_VALIDATE, SIGMA


@dataclass
class NodeCREP:
    C: float  # coherence
    R: float  # resonance
    E: float  # emergence
    P: float  # poetics
    Gamma: float  # combined CREP score

    def as_dict(self) -> dict[str, float]:
        return {"C": self.C, "R": self.R, "E": self.E, "P": self.P, "Gamma": self.Gamma}


def _crep_gamma(c: float, r: float, e: float, p: float) -> float:
    eta = (c * r * e * p) ** 0.25
    eta = max(0.0, min(1.0 - 1e-9, eta))
    return math.atanh(eta) / SIGMA


@dataclass
class ValidatorNode:
    """
    A single PoR validator node with a CREP state and lightweight identity.

    The node_id is derived from a seed so that CREP states are reproducible
    (no real cryptographic keys needed for simulation).
    """

    node_id: str
    crep: NodeCREP
    hikari_balance: float = 0.0
    cycles_run: int = 0
    _rng: random.Random = field(repr=False, default_factory=random.Random)

    # ── Factory ────────────────────────────────────────────────────────────────

    @classmethod
    def from_seed(cls, seed: int, node_id: str | None = None) -> "ValidatorNode":
        rng = random.Random(seed)
        c = 0.3 + 0.5 * rng.random()
        r = 0.3 + 0.5 * rng.random()
        e = 0.3 + 0.5 * rng.random()
        p = 0.3 + 0.5 * rng.random()
        gamma = _crep_gamma(c, r, e, p)
        nid = node_id or hashlib.sha256(str(seed).encode()).hexdigest()[:12]
        obj = cls(node_id=nid, crep=NodeCREP(C=c, R=r, E=e, P=p, Gamma=gamma))
        obj._rng = rng
        return obj

    # ── State ──────────────────────────────────────────────────────────────────

    def run_utac_cycle(self) -> None:
        """Slightly drift CREP each cycle — simulates ongoing UTAC evaluation."""
        noise = 0.02
        self.crep.C = max(0.1, min(0.99, self.crep.C + self._rng.gauss(0, noise)))
        self.crep.R = max(0.1, min(0.99, self.crep.R + self._rng.gauss(0, noise)))
        self.crep.E = max(0.1, min(0.99, self.crep.E + self._rng.gauss(0, noise)))
        self.crep.P = max(0.1, min(0.99, self.crep.P + self._rng.gauss(0, noise)))
        self.crep.Gamma = _crep_gamma(
            self.crep.C, self.crep.R, self.crep.E, self.crep.P
        )
        self.cycles_run += 1

    def is_eligible(self) -> bool:
        return self.crep.Gamma >= MIN_CREP_TO_VALIDATE and self.cycles_run >= 1

    def sign_crep(self) -> str:
        """Deterministic 'signature' — hex of (node_id + Gamma)."""
        payload = f"{self.node_id}:{self.crep.Gamma:.6f}"
        return hashlib.sha256(payload.encode()).hexdigest()[:16]

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_id": self.node_id,
            "crep": self.crep.as_dict(),
            "hikari_balance": round(self.hikari_balance, 6),
            "cycles_run": self.cycles_run,
            "eligible": self.is_eligible(),
            "signature": self.sign_crep(),
        }
