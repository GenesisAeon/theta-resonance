"""Benchmark runner for diffusive-routing (Package 30)."""

from __future__ import annotations

from .constants import ROUTING_TARGETS


def _check(
    value: float,
    target: object,
    tolerance: object,
    label: str,
) -> dict[str, object]:
    if not isinstance(target, (int, float)) or not isinstance(tolerance, (int, float)):
        return {
            "value": value,
            "target": target,
            "tolerance": tolerance,
            "pass": None,
            "label": label,
        }
    lo = float(target) - float(tolerance)
    hi = float(target) + float(tolerance)
    return {
        "value": round(value, 6),
        "target": target,
        "tolerance": tolerance,
        "pass": lo <= value <= hi,
        "label": label,
    }


def _t(key: str) -> tuple[object, object]:
    """Return (target, tolerance) pair for a benchmark key."""
    entry = ROUTING_TARGETS[key]
    return entry[0], entry[1]


def run_benchmark(
    throughput_vs_ospf: float,
    latency_vs_sp: float,
    gamma_routing: float,
    congestion_events_per_hour: float,
    load_balance_gini: float,
    adaptation_time_ms: float,
) -> dict[str, object]:
    tgt, tol = _t("throughput_vs_ospf_ratio")
    ltgt, ltol = _t("latency_vs_shortest_path")
    gtgt, gtol = _t("gamma_routing")
    ctgt, ctol = _t("congestion_events_per_hour")
    gitgt, gitol = _t("load_balance_gini")
    atgt, atol = _t("adaptation_time_ms")

    results: dict[str, object] = {
        "throughput_vs_ospf_ratio": _check(
            throughput_vs_ospf, tgt, tol, "throughput_vs_ospf_ratio"
        ),
        "latency_vs_shortest_path": _check(
            latency_vs_sp, ltgt, ltol, "latency_vs_shortest_path"
        ),
        "gamma_routing": _check(gamma_routing, gtgt, gtol, "gamma_routing"),
        "congestion_events_per_hour": _check(
            congestion_events_per_hour, ctgt, ctol, "congestion_events_per_hour"
        ),
        "load_balance_gini": _check(load_balance_gini, gitgt, gitol, "load_balance_gini"),
        "adaptation_time_ms": _check(adaptation_time_ms, atgt, atol, "adaptation_time_ms"),
    }

    passes = [
        v["pass"]
        for v in results.values()
        if isinstance(v, dict) and isinstance(v["pass"], bool)
    ]
    results["all_pass"] = all(passes) if passes else False
    results["n_pass"] = sum(1 for p in passes if p)
    results["n_total"] = len(passes)
    return results
