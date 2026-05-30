"""Benchmark theta-resonance against literature targets."""

from __future__ import annotations

from typing import Any

from .constants import BANDS, GAMMA_BY_BAND, THETA_TARGETS


def run_benchmark(crep_state: dict[str, Any], utac_state: dict[str, Any]) -> dict[str, Any]:
    """
    Compare a ThetaResonance result dict against THETA_TARGETS.

    Returns per-target pass/fail and an overall pass boolean.
    """
    results: dict[str, dict[str, Any]] = {}

    # theta_band_hz: check dominant_hz is within theta range
    lo, hi = BANDS["theta"]
    dom_hz = utac_state.get("H", 6.0)
    results["theta_band_hz"] = {
        "target": f"{lo}–{hi} Hz",
        "value": round(dom_hz, 2),
        "pass": lo <= dom_hz <= hi,
    }

    # gamma_theta_utac: Γ when in theta should be ~0.25
    gamma_val = crep_state.get("Gamma", 0.0)
    target_g, tol_g = THETA_TARGETS["gamma_theta_utac"]
    results["gamma_theta_utac"] = {
        "target": target_g,
        "tolerance": tol_g,
        "value": round(gamma_val, 4),
        "pass": abs(gamma_val - target_g) <= tol_g,
    }

    # gamma_gamma_band: canonical gamma-band Γ
    g_gamma = GAMMA_BY_BAND["gamma"]
    tg_raw, tol_raw = THETA_TARGETS["gamma_gamma_band"]
    tg2, tol2 = float(tg_raw), float(tol_raw)  # type: ignore[arg-type]
    results["gamma_gamma_band"] = {
        "target": tg2,
        "tolerance": tol2,
        "value": g_gamma,
        "pass": abs(g_gamma - tg2) <= tol2,
    }

    passed = sum(1 for v in results.values() if v["pass"])
    results["summary"] = {
        "passed": passed,
        "total": len(results) - 1,
        "all_pass": passed == len(results) - 1,
    }
    return results
