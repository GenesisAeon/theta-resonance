"""Physical and model constants for theta-resonance (Package 27)."""

from __future__ import annotations

# ── Frequency band definitions (Hz) ──────────────────────────────────────────
BANDS: dict[str, tuple[float, float]] = {
    "delta": (0.5, 4.0),
    "theta": (4.0, 8.0),
    "alpha": (8.0, 13.0),
    "beta": (13.0, 30.0),
    "gamma": (30.0, 80.0),
}

BAND_CENTERS: dict[str, float] = {
    band: (lo + hi) / 2 for band, (lo, hi) in BANDS.items()
}

# ── UTAC parameters ───────────────────────────────────────────────────────────
K_HZ: float = 80.0          # ceiling frequency [Hz]
H_STAR_THETA: float = 6.0   # theta-band centre [Hz] — flow-state fixed point
SIGMA: float = 2.2           # CREP coupling constant (universal)
R_DRIFT: float = 0.05        # frequency drift rate (normalised / s)

# ── Band → Γ mapping (canonical values) ──────────────────────────────────────
GAMMA_BY_BAND: dict[str, float] = {
    "delta": 0.05,
    "theta": 0.25,   # Homeostatic universality: Γ_theta = Γ_AMOC = 0.251
    "alpha": 0.35,
    "beta":  0.55,
    "gamma": 0.75,
}

# ── Benchmark targets ─────────────────────────────────────────────────────────
THETA_TARGETS: dict[str, tuple[object, ...]] = {
    "theta_band_hz":      ((4.0, 8.0), 0.5),
    "gamma_theta_utac":   (0.25,       0.02),
    "gamma_gamma_band":   (0.75,       0.05),
    "pac_mi_flow_state":  (0.05,       0.02),
    "flow_detection_acc": (0.80,       0.05),
}

# ── Package metadata ──────────────────────────────────────────────────────────
PACKAGE_NUMBER: int = 27
WHITEPAPER_DOI: str = "10.5281/zenodo.19645351"
REFERENCE_DOI: str = "10.1016/j.neuron.2025.05.020"
