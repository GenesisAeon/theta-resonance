"""Constants for epi-sigillin (Package 28)."""

PACKAGE_NUMBER = 28
PACKAGE_NAME = "epi-sigillin"
DOMAIN = "epigenetics"
SCALE = "systemic"

WHITEPAPER_DOI = "10.5281/zenodo.19645351"
REFERENCE_DOI = "10.1038/s41580-019-0160-9"  # Greenberg & Bourc'his 2019

CREP_COUPLING = 2.2  # σ — shared across all GenesisAeon packages

# UTAC parameters for entropy-as-H mapping
S_MAX = 10.0        # K — maximum sustainable system entropy (nats)
S_OPTIMAL = 5.0     # H* — target entropy for stable self-organisation
ENTROPY_RATE = 0.05  # r — base entropy production rate per cycle

# Methylation kinetics
ALPHA_DEFAULT = 0.10   # methylation rate (suppression per unit excess entropy)
DELTA_DEFAULT = 0.05   # spontaneous demethylation rate
BETA_DEFAULT = 0.08    # de-methylation enhancement rate (low entropy)

# Epigenetic inheritance fraction (50% from parent state)
INHERITANCE_FRACTION = 0.50

# Benchmark targets — all tolerances are numeric to keep mypy happy.
# yaml_mutation_valid is handled separately (boolean check, no numeric tolerance).
EPI_TARGETS: dict[str, tuple[float, float]] = {
    "methylation_range_lo":        (0.0,  0.0),
    "methylation_range_hi":        (1.0,  0.0),
    "adaptation_speed_cycles":     (10.0, 3.0),
    "memory_inheritance_pct":      (50.0, 5.0),
    "entropy_reduction_from_epi":  (0.20, 0.05),
}

# CREP components
CREP_COMPONENTS = ("C", "R", "E", "P")
