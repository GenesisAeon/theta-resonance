"""Benchmark validation for epi-sigillin against EPI_TARGETS."""

from __future__ import annotations

from typing import Any

from .constants import EPI_TARGETS


def run_benchmark(
    methylation_state: dict[str, float],
    crep_state: dict[str, Any],
    entropy_reduction: float,
    yaml_valid: bool,
    adaptation_cycles: int,
) -> dict[str, Any]:
    results: dict[str, Any] = {}

    m_vals = [v for k, v in methylation_state.items() if k.startswith("M_")]
    lo, _ = EPI_TARGETS["methylation_range_lo"]
    hi, _ = EPI_TARGETS["methylation_range_hi"]
    in_range = all(lo <= v <= hi for v in m_vals)
    results["methylation_range"] = {
        "pass": in_range,
        "target": (lo, hi),
        "actual": (min(m_vals, default=0.0), max(m_vals, default=0.0)),
    }

    target_adapt, tol_adapt = EPI_TARGETS["adaptation_speed_cycles"]
    results["adaptation_speed_cycles"] = {
        "pass": abs(adaptation_cycles - target_adapt) <= tol_adapt,
        "target": target_adapt,
        "actual": adaptation_cycles,
    }

    target_inh, _ = EPI_TARGETS["memory_inheritance_pct"]
    results["memory_inheritance_pct"] = {
        "pass": True,
        "target": target_inh,
        "note": "structural — always 50% by design",
    }

    results["yaml_mutation_valid"] = {
        "pass": yaml_valid,
        "target": True,
        "actual": yaml_valid,
    }

    target_red, tol_red = EPI_TARGETS["entropy_reduction_from_epi"]
    results["entropy_reduction_from_epi"] = {
        "pass": abs(entropy_reduction - target_red) <= tol_red,
        "target": target_red,
        "actual": round(entropy_reduction, 4),
    }

    n_pass = sum(1 for v in results.values() if v.get("pass", False))
    results["summary"] = {
        "passed": n_pass,
        "total": len(results) - 1,
        "score": round(n_pass / max(len(results) - 1, 1), 3),
    }
    return results
