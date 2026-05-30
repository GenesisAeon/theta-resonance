"""Physical and routing constants for diffusive-routing (Package 30)."""

from __future__ import annotations

# ── UTAC parameters ────────────────────────────────────────────────────────────
K_THROUGHPUT: float = 1.0        # maximum normalised throughput (Shannon ceiling)
H_STAR_ROUTING: float = 0.75    # optimal operating point (75% of capacity)
SIGMA: float = 2.2               # CREP coupling constant (universal)
R_ADAPTATION: float = 0.10       # routing adaptation rate (paths updated per tick)

# ── Diffusive routing ──────────────────────────────────────────────────────────
GAMMA_ROUTING: float = 0.443     # canonical Γ for routing (η = 0.75, σ = 2.2)
BASELINE_RESISTANCE: float = 1.0 # ρ_ij baseline before CREP modulation
DIFFUSION_COEFF: float = 0.05    # D in reaction-diffusion ∂ρ/∂t = D·∇²ρ - k·Γ·ρ + f
RD_DECAY_RATE: float = 0.10      # k in reaction-diffusion decay term

# ── Network defaults ───────────────────────────────────────────────────────────
DEFAULT_N_NODES: int = 20
DEFAULT_N_EDGES_FACTOR: float = 2.5  # average degree ≈ 2 × n_edges_factor
DEFAULT_N_PACKETS: int = 1000
DEFAULT_DURATION_S: float = 60.0

# ── Benchmark targets ──────────────────────────────────────────────────────────
ROUTING_TARGETS: dict[str, tuple[object, ...]] = {
    "throughput_vs_ospf_ratio":  (1.20, 0.10),
    "latency_vs_shortest_path":  (1.05, 0.05),
    "gamma_routing":             (0.443, 0.030),
    "congestion_events_per_hour":(2.0,  1.0),
    "load_balance_gini":         (0.15, 0.05),
    "adaptation_time_ms":        (100,  50),
}

# ── Package metadata ───────────────────────────────────────────────────────────
PACKAGE_NUMBER: int = 30
WHITEPAPER_DOI: str = "10.5281/zenodo.19645351"
REFERENCE: str = "Gemini-2026-GenesisAeon-Assessment"
