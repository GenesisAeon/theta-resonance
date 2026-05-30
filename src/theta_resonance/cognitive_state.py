"""Cognitive state classifier from EEG band powers."""

from __future__ import annotations

from .constants import BANDS, GAMMA_BY_BAND


_STATE_RULES: list[tuple[str, dict]] = [
    # (state_name, {dominant_band, optional constraints})
    ("deep_sleep",  {"dominant": "delta"}),
    ("flow",        {"dominant": "theta", "alpha_relative": (0.0, 0.4)}),
    ("relaxed",     {"dominant": "alpha"}),
    ("active",      {"dominant": "beta"}),
    ("arousal",     {"dominant": "gamma"}),
]


class CognitiveStateClassifier:
    """
    Rule-based cognitive state detector from relative band powers.

    States: deep_sleep · flow · relaxed · active · arousal
    Each maps to a CREP Γ value (canonical from Hengen & Shew 2025).
    """

    def classify(self, band_powers: dict[str, float]) -> dict:
        """
        Parameters
        ----------
        band_powers : dict {band_name: power}  (raw or relative)

        Returns
        -------
        dict with keys: state, gamma, dominant_band
        """
        total = sum(band_powers.values()) or 1.0
        rel = {b: p / total for b, p in band_powers.items()}
        dominant = max(rel, key=rel.get)  # type: ignore[arg-type]

        state = self._apply_rules(dominant, rel)
        gamma = GAMMA_BY_BAND.get(dominant, 0.25)
        return {
            "state": state,
            "dominant_band": dominant,
            "gamma": round(gamma, 4),
            "relative_powers": {b: round(v, 4) for b, v in rel.items()},
        }

    def _apply_rules(self, dominant: str, rel: dict[str, float]) -> str:
        if dominant == "theta":
            alpha_rel = rel.get("alpha", 0.0)
            if alpha_rel < 0.40:
                return "flow"
            return "meditation"
        state_map = {
            "delta": "deep_sleep",
            "alpha": "relaxed",
            "beta":  "active",
            "gamma": "arousal",
        }
        return state_map.get(dominant, "unknown")
