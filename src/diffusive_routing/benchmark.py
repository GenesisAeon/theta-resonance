"""Benchmark runner for diffusive-routing (Package 30)."""

from __future__ import annotations

from .constants import ROUTING_TARGETS


def _check(
    value: float, target: object, tolerance: object, label: str
) -> dict[str, object]:
    if not isinstance(target, (int, float)) or not isinstance(tolerance, (int, float)):
        return {"value": value, "target": target, "tolerance": tolerance, "pass": None, "label": label}
    lo = float(target) - float(tolerance)
    hi = float(target) + float(tolerance)
    return {
        "value": round(value, 6),
        "target": target,
        "tolerance": tolerance,
        "pass": lo <= value <= hi,
        "label": label,
    }


def run_benchmark(
    throughput_vs_ospf: float,
    latency_vs_sp: float,
    gamma_routing: float,
    congestion_events_per_hour: float,
    load_balance_gini: float,
    adaptation_time_ms: float,
) -> dict[str, object]:
    results: dict[str, object] = {}

    t = ROUTING_TARGETS
    results["throughput_vs_ospf_ratio"]  = _check(throughput_vs_ospf,           *t["throughput_vs_ospf_ratio"],  "throughput_vs_ospf_ratio")
    results["latency_vs_shortest_path"]  = _check(latency_vs_sp,                *t["latency_vs_shortest_path"],  "latency_vs_shortest_path")
    results["gamma_routing"]             = _check(gamma_routing,                 *t["gamma_routing"],             "gamma_routing")
    results["congestion_events_per_hour"]= _check(congestion_events_per_hour,    *t["congestion_events_per_hour"],"congestion_events_per_hour")
    results["load_balance_gini"]         = _check(load_balance_gini,             *t["load_balance_gini"],         "load_balance_gini")
    results["adaptation_time_ms"]        = _check(adaptation_time_ms,            *t["adaptation_time_ms"],        "adaptation_time_ms")

    passes = [v["pass"] for v in results.values() if isinstance(v, dict) and v["pass"] is not None]  # type: ignore[index]
    results["all_pass"] = all(passes) if passes else False
    results["n_pass"]   = sum(1 for p in passes if p)
    results["n_total"]  = len(passes)
    return results
