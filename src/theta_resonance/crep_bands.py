"""Band-to-CREP tensor mapping for theta-resonance."""

from __future__ import annotations

import math

from .constants import BANDS, BAND_CENTERS, GAMMA_BY_BAND, SIGMA


class BandCREPMapper:
    """
    Maps EEG frequency band powers to CREP components {C, R, E, P, Γ}.

    C = theta-gamma PAC strength (Modulation Index, Tort 2010)
    R = proximity of dominant band to target band centre [0, 1]
    E = inter-regional phase synchrony (PLV-like measure)
    P = permutation entropy of bandpass signal [0, 1]
    Γ = arctanh(η) / σ  where η = (C·R·E·P)^(1/4)
    """

    def __init__(self, target_band: str = "theta", sigma: float = SIGMA) -> None:
        if target_band not in BANDS:
            raise ValueError(f"Unknown band '{target_band}'. Choose from {list(BANDS)}")
        self.target_band = target_band
        self.target_hz = BAND_CENTERS[target_band]
        self.sigma = sigma

    def compute(
        self,
        dominant_hz: float,
        pac_mi: float = 0.05,
        plv: float = 0.70,
        perm_entropy: float = 0.75,
    ) -> dict:
        """Return CREP state dict for given EEG features."""
        C = float(min(1.0, max(0.0, pac_mi / 0.15)))          # MI → [0,1]
        R = self._resonance(dominant_hz)
        E = float(min(1.0, max(0.0, plv)))
        P = float(min(1.0, max(0.0, perm_entropy)))
        eta = (C * R * E * P) ** 0.25 if (C * R * E * P) > 0 else 0.0
        eta = min(eta, 0.9999)
        gamma = math.atanh(eta) / self.sigma
        return {
            "C": round(C, 4),
            "R": round(R, 4),
            "E": round(E, 4),
            "P": round(P, 4),
            "eta": round(eta, 4),
            "Gamma": round(gamma, 4),
            "dominant_hz": round(dominant_hz, 2),
            "target_band": self.target_band,
        }

    def gamma_for_band(self, band: str) -> float:
        """Canonical Γ for a named frequency band."""
        return GAMMA_BY_BAND.get(band, 0.0)

    def _resonance(self, hz: float) -> float:
        lo, hi = BANDS[self.target_band]
        centre = self.target_hz
        width = (hi - lo) / 2
        distance = abs(hz - centre)
        return float(max(0.0, 1.0 - distance / (width + 1e-9)))
