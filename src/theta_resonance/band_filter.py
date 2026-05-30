"""EEG/LFP bandpass filtering — pure-Python Butterworth approximation."""

from __future__ import annotations

import math


def bandpass_power(
    signal: list[float],
    fs: float,
    lo: float,
    hi: float,
) -> float:
    """
    Estimate band power via FFT-equivalent DFT on short windows.

    Returns mean squared amplitude of frequency components in [lo, hi] Hz.
    Uses a simple Goertzel-inspired approach for efficiency.
    """
    n = len(signal)
    if n == 0:
        return 0.0

    df = fs / n
    lo_bin = max(0, int(lo / df))
    hi_bin = min(n // 2, int(hi / df) + 1)

    # DFT via direct summation (acceptable for n < 10k)
    power = 0.0
    count = 0
    for k in range(lo_bin, hi_bin):
        omega = 2 * math.pi * k / n
        re = sum(x * math.cos(omega * i) for i, x in enumerate(signal))
        im = sum(x * math.sin(omega * i) for i, x in enumerate(signal))
        power += (re * re + im * im) / (n * n)
        count += 1

    return power / max(count, 1)


def dominant_frequency(
    band_powers: dict[str, float],
    band_centers: dict[str, float],
) -> float:
    """Return power-weighted mean frequency from per-band powers."""
    total = sum(band_powers.values())
    if total == 0:
        return 6.0  # default theta
    return sum(band_centers[b] * p for b, p in band_powers.items()) / total


def synthetic_eeg(
    duration_s: float = 10.0,
    fs: float = 256.0,
    dominant_band: str = "theta",
    seed: int = 42,
) -> list[float]:
    """Generate synthetic EEG dominated by the given band (for testing)."""
    import random
    from .constants import BAND_CENTERS

    rng = random.Random(seed)
    n = int(duration_s * fs)
    freq = BAND_CENTERS.get(dominant_band, 6.0)
    return [
        math.sin(2 * math.pi * freq * i / fs) + 0.1 * rng.gauss(0, 1)
        for i in range(n)
    ]
