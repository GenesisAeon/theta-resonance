"""Phase-Amplitude Coupling (PAC) analysis — theta-gamma coupling."""

from __future__ import annotations

import math


def modulation_index(
    phase_signal: list[float],
    amplitude_signal: list[float],
    n_bins: int = 18,
) -> float:
    """
    Compute PAC Modulation Index (Tort et al. 2010).

    MI = KL-divergence between amplitude distribution across phase bins
    and the uniform distribution, normalised by log(n_bins).

    Parameters
    ----------
    phase_signal:     instantaneous phase of low-frequency (theta) signal [radians]
    amplitude_signal: amplitude envelope of high-frequency (gamma) signal
    n_bins:           number of phase bins (default 18 × 20°)

    Returns
    -------
    MI ∈ [0, 1]  (0 = no coupling, > 0.05 = significant coupling)
    """
    if len(phase_signal) != len(amplitude_signal) or len(phase_signal) == 0:
        return 0.0

    bin_size = 2 * math.pi / n_bins
    amplitude_sum = [0.0] * n_bins
    counts = [0] * n_bins

    for ph, amp in zip(phase_signal, amplitude_signal):
        idx = int((ph % (2 * math.pi)) / bin_size) % n_bins
        amplitude_sum[idx] += amp
        counts[idx] += 1

    total_amp = sum(amplitude_sum)
    if total_amp == 0:
        return 0.0

    # Normalised amplitude distribution
    p = [a / total_amp for a in amplitude_sum]
    q = 1.0 / n_bins  # uniform

    # KL divergence D_KL(P || Q)
    kl = sum(pi * math.log(pi / q) for pi in p if pi > 0)
    mi = kl / math.log(n_bins)
    return float(min(1.0, max(0.0, mi)))


def synthetic_theta_gamma(
    duration_s: float = 5.0,
    fs: float = 1000.0,
    theta_hz: float = 6.0,
    gamma_hz: float = 40.0,
    pac_strength: float = 0.05,
    seed: int = 42,
) -> tuple[list[float], list[float]]:
    """Generate synthetic theta-phase / gamma-amplitude signals for testing."""
    import random
    rng = random.Random(seed)
    n = int(duration_s * fs)
    dt = 1.0 / fs
    phase = [2 * math.pi * theta_hz * i * dt for i in range(n)]
    amplitude = [
        (1.0 + pac_strength * math.cos(ph)) + rng.gauss(0, 0.1)
        for ph in phase
    ]
    return phase, amplitude
