"""Benchmark runner for hikari-ledger vs. HIKARI_TARGETS."""

from __future__ import annotations

from typing import Any

from .constants import HIKARI_TARGETS


def run_benchmark(
    gamma_por: float,
    consensus_threshold: float,
    byzantine_tolerance_pct: float,
    crep_gini: float,
    consensus_latency_ms: float,
) -> dict[str, Any]:
    results: dict[str, Any] = {}
    checks = {
        "gamma_por": gamma_por,
        "consensus_threshold": consensus_threshold,
        "byzantine_tolerance_pct": byzantine_tolerance_pct,
        "crep_gini_coefficient": crep_gini,
        "consensus_latency_ms": consensus_latency_ms,
    }
    all_pass = True
    for key, measured in checks.items():
        if key not in HIKARI_TARGETS:
            continue
        target, tol = HIKARI_TARGETS[key]
        if tol is None:
            pass_ = True
        else:
            pass_ = abs(float(measured) - float(target)) <= float(tol)  # type: ignore[arg-type]
        if not pass_:
            all_pass = False
        results[key] = {
            "measured": round(float(measured), 6),
            "target": target,
            "tolerance": tol,
            "pass": pass_,
        }
    results["all_pass"] = all_pass
    return results
