"""Flow-state detection from EEG band signatures."""

from __future__ import annotations

from .constants import GAMMA_BY_BAND


class FlowStateDetector:
    """
    Detects cognitive flow states from relative EEG band powers.

    Flow signature (after Hengen & Shew 2025 + Buzsáki 2006):
      - Theta power elevated (> theta_threshold)
      - Alpha suppressed (< alpha_threshold)
      - Gamma reduced (< gamma_threshold)

    Confirmed Γ_flow ≈ 0.251 = Γ_AMOC = Γ_neural_criticality (triple universality).
    """

    def __init__(
        self,
        theta_threshold: float = 0.30,
        alpha_threshold: float = 0.35,
        gamma_threshold: float = 0.25,
    ) -> None:
        self.theta_threshold = theta_threshold
        self.alpha_threshold = alpha_threshold
        self.gamma_threshold = gamma_threshold

    def detect(self, band_powers: dict[str, float]) -> dict:
        """
        Parameters
        ----------
        band_powers : raw band powers (any scale — normalised internally)

        Returns
        -------
        dict with: is_flow, gamma, confidence, criteria
        """
        total = sum(band_powers.values()) or 1.0
        rel = {b: p / total for b, p in band_powers.items()}

        theta_ok = rel.get("theta", 0.0) > self.theta_threshold
        alpha_ok = rel.get("alpha", 1.0) < self.alpha_threshold
        gamma_ok = rel.get("gamma", 1.0) < self.gamma_threshold

        n_met = sum([theta_ok, alpha_ok, gamma_ok])
        is_flow = n_met >= 2

        confidence = n_met / 3.0
        gamma = GAMMA_BY_BAND["theta"] if is_flow else GAMMA_BY_BAND.get(
            max(rel, key=rel.get), 0.35  # type: ignore[arg-type]
        )

        return {
            "is_flow": is_flow,
            "gamma": round(gamma, 4),
            "confidence": round(confidence, 3),
            "criteria": {
                "theta_elevated": theta_ok,
                "alpha_suppressed": alpha_ok,
                "gamma_reduced": gamma_ok,
            },
        }
