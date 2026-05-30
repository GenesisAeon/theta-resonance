"""Physical and consensus constants for hikari-ledger (Package 29)."""

from __future__ import annotations

# ── UTAC parameters ────────────────────────────────────────────────────────────
K_CONSENSUS: float = 1.0          # maximum consensus fraction (perfect agreement)
H_STAR_BFT: float = 2.0 / 3.0    # Byzantine fault tolerance threshold (≥ 2/3)
SIGMA: float = 2.2                 # CREP coupling constant (universal)
R_CONSENSUS: float = 0.10          # consensus propagation rate

# ── Proof-of-Resonance ─────────────────────────────────────────────────────────
GAMMA_POR: float = 0.367           # canonical Γ for PoR (η = 2/3)
MIN_CREP_TO_VALIDATE: float = 0.05 # minimum Γ for a node to participate
HIKARI_EMISSION_RATE: float = 0.01 # k in ΔH_i = k · Γ_i · (1 - S_H)

# ── Network defaults ───────────────────────────────────────────────────────────
DEFAULT_N_NODES: int = 50
DEFAULT_N_BLOCKS: int = 100
CONSENSUS_LATENCY_MS: float = 100.0

# ── Benchmark targets ──────────────────────────────────────────────────────────
HIKARI_TARGETS: dict[str, tuple[object, ...]] = {
    "consensus_threshold":     (0.667, 0.01),
    "gamma_por":               (0.367, 0.02),
    "energy_vs_pow_ratio":     (0.001, 0.002),
    "consensus_latency_ms":    (100,   50),
    "byzantine_tolerance_pct": (33.0,  2.0),
    "crep_gini_coefficient":   (0.30,  0.10),
}

# ── Package metadata ───────────────────────────────────────────────────────────
PACKAGE_NUMBER: int = 29
WHITEPAPER_DOI: str = "10.5281/zenodo.19645351"
REFERENCE: str = "Gemini-2026-GenesisAeon-Assessment"
