"""Per-node CREP evaluation and validation weight assignment."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .constants import MIN_CREP_TO_VALIDATE

if TYPE_CHECKING:
    from .node import ValidatorNode


class CREPValidator:
    """
    Evaluates CREP states across the validator pool and computes
    normalised weights: w_i = Γ_i / Σ_j Γ_j
    """

    def compute_weights(self, nodes: list["ValidatorNode"]) -> dict[str, float]:
        eligible = [n for n in nodes if n.is_eligible()]
        total_gamma = sum(n.crep.Gamma for n in eligible)
        if total_gamma < 1e-12:
            # Fallback: equal weights for all eligible nodes
            n_elig = max(len(eligible), 1)
            return {n.node_id: 1.0 / n_elig for n in eligible}
        return {n.node_id: n.crep.Gamma / total_gamma for n in eligible}

    def validate_crep(self, node: "ValidatorNode", expected_gamma: float,
                      tolerance: float = 0.15) -> bool:
        """Check that a node's CREP state is self-consistent and above minimum."""
        if not node.is_eligible():
            return False
        if abs(node.crep.Gamma - expected_gamma) > tolerance:
            return False
        return True

    def gini_coefficient(self, weights: dict[str, float]) -> float:
        """Measure CREP weight distribution fairness (0 = perfect equality)."""
        vals = sorted(weights.values())
        n = len(vals)
        if n == 0:
            return 0.0
        cumsum = 0.0
        weighted_sum = 0.0
        for i, v in enumerate(vals, 1):
            cumsum += v
            weighted_sum += (2 * i - n - 1) * v
        denom = n * sum(vals)
        return weighted_sum / denom if denom > 1e-12 else 0.0

    def network_crep_mean(self, nodes: list["ValidatorNode"]) -> float:
        eligible = [n for n in nodes if n.crep.Gamma >= MIN_CREP_TO_VALIDATE]
        if not eligible:
            return 0.0
        return sum(n.crep.Gamma for n in eligible) / len(eligible)
