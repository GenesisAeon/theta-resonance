"""UTAC ODE for cortical frequency dynamics."""

from __future__ import annotations

import math
import random

from .constants import H_STAR_THETA, K_HZ, R_DRIFT, SIGMA


class FrequencyUTAC:
    """
    UTAC for dominant oscillation frequency.

    dH/dt = r·(K - H) - K·tanh(σ·Γ)·δ(H - H*)·ε + η(t)

    Simplified integration: Euler steps with additive noise.
    H(t) ∈ [0, K_HZ]; H* set by cognitive state / band target.
    """

    def __init__(
        self,
        h_init: float = 6.0,
        h_star: float = H_STAR_THETA,
        k: float = K_HZ,
        r: float = R_DRIFT,
        sigma: float = SIGMA,
        noise_amp: float = 1.0,
        seed: int = 42,
    ) -> None:
        self.H = h_init
        self.H_star = h_star
        self.K = k
        self.r = r
        self.sigma = sigma
        self.noise_amp = noise_amp
        self._rng = random.Random(seed)
        self._t = 0.0
        self._dH_dt = 0.0

    def step(self, gamma: float, dt: float = 0.1) -> float:
        """Advance one Euler step; return new H."""
        # Loading term (drift toward K)
        load = self.r * (self.K - self.H)
        # Resonance attraction toward H_star modulated by CREP
        attraction = self.K * math.tanh(self.sigma * gamma) * (self.H_star - self.H) / self.K
        # White noise
        noise = self.noise_amp * (self._rng.gauss(0, 1)) * math.sqrt(dt)
        self._dH_dt = load + attraction
        self.H = max(0.0, min(self.K, self.H + self._dH_dt * dt + noise))
        self._t += dt
        return self.H

    def utac_state(self) -> dict:
        return {
            "H": round(self.H, 4),
            "dH_dt": round(self._dH_dt, 6),
            "H_star": self.H_star,
            "K_eff": self.K,
            "t": round(self._t, 3),
        }
