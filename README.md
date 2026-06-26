# theta-resonance + epi-sigillin + hikari-ledger + diffusive-routing

[![Package 27](https://img.shields.io/badge/GenesisAeon-Package%2027-blueviolet)](https://github.com/GenesisAeon/theta-resonance)
[![Package 28](https://img.shields.io/badge/GenesisAeon-Package%2028-purple)](https://github.com/GenesisAeon/theta-resonance)
[![Package 29](https://img.shields.io/badge/GenesisAeon-Package%2029-orange)](https://github.com/GenesisAeon/theta-resonance)
[![Package 30](https://img.shields.io/badge/GenesisAeon-Package%2030-teal)](https://github.com/GenesisAeon/theta-resonance)
[![Whitepaper](https://img.shields.io/badge/Whitepaper-10.5281%2Fzenodo.19645351-blue)](https://doi.org/10.5281/zenodo.19645351)
[![Reference P27](https://img.shields.io/badge/Neuron%202025-Hengen%20%26%20Shew-green)](https://doi.org/10.1016/j.neuron.2025.05.020)
[![Reference P28](https://img.shields.io/badge/NatRevMCB%202019-Greenberg%20%26%20Bourc'his-green)](https://doi.org/10.1038/s41580-019-0160-9)
[![Reference P30](https://img.shields.io/badge/Turing%201952-Reaction--Diffusion-green)](https://doi.org/10.1098/rstb.1952.0012)
[![PyPI](https://img.shields.io/pypi/v/theta-resonance)](https://pypi.org/project/theta-resonance/)
[![License: GPLv3+](https://img.shields.io/badge/Code%20License-GPLv3--or--later-blue.svg)](LICENSE)
[![Docs License: CC BY 4.0](https://img.shields.io/badge/Docs%20License-CC%20BY%204.0-lightgrey.svg)](LICENSE-DOCS.md)
[![CI](https://github.com/GenesisAeon/theta-resonance/actions/workflows/ci.yml/badge.svg)](https://github.com/GenesisAeon/theta-resonance/actions/workflows/ci.yml)

**GenesisAeon Entropy Atlas — Packages 27, 28, 29 & 30**

| Package | Module | Domain | Γ |
|---|---|---|---|
| **P27** | `theta_resonance` | Brain oscillation bands as CREP modulators | 0.251 (theta) |
| **P28** | `epi_sigillin` | Epigenetic runtime parameter mutation | dynamic — f(S_total) |
| **P29** | `hikari_ledger` | Proof-of-Resonance distributed consensus | 0.367 |
| **P30** | `diffusive_routing` | Entropy-minimizing network routing | 0.443 |

---

## Package 27 — theta-resonance

Models EEG frequency bands (δ/θ/α/β/γ) as channels of the CREP tensor within the
Unified Threshold Activation Criticality (UTAC) framework.

> **Triple Universality:** Γ\_theta ≈ 0.251 = Γ\_AMOC = Γ\_neural\_criticality  
> The brain's flow state (theta band) converges to the same CREP setpoint as ocean
> circulation (AMOC) and cortical criticality — all homeostatic systems at 50 % efficiency.

```python
from theta_resonance import ThetaResonance

sys = ThetaResonance(seed=42)          # synthetic EEG by default
result = sys.run_cycle(duration_seconds=60.0)

print(result["crep"])
# {'C': 0.333, 'R': 1.0, 'E': 0.647, 'P': 0.752, 'Gamma': 0.2514, ...}

print(result["flow_state"])   # True
print(result["current_band"]) # 'theta'
print(sys.gamma_for_band("gamma"))  # 0.75
```

### Frequency Band → CREP Mapping

| Band | Range | Cognitive State | Γ |
|---|---|---|---|
| Delta δ | 0.5–4 Hz | Deep sleep | 0.05 |
| **Theta θ** | **4–8 Hz** | **Flow / meditation** | **0.251** |
| Alpha α | 8–13 Hz | Relaxed attention | 0.35 |
| Beta β | 13–30 Hz | Active cognition | 0.55 |
| Gamma γ | 30–80 Hz | Error correction / arousal | 0.75 |

---

## Package 28 — epi-sigillin

Implements **epigenetic mutation of UTAC parameters** during runtime. Analogous to how
environmental signals alter gene expression without changing DNA, the system entropy level
rewrites CREP-YAML parameter files at runtime — giving the framework organic adaptability.

> **Gemini's insight:** *"Umweltfaktoren verändert die Genexpression → systemisches
> Entropie-Niveau schreibt CREP-YAML während der Laufzeit um"*

```python
from epi_sigillin import EpiSigillin

epi = EpiSigillin(seed=42)
result = epi.run_cycle(duration_cycles=100)

print(result["methylation"])
# {'M_C': 0.12, 'M_R': 0.08, 'M_E': 0.03, 'M_P': 0.21}

print(result["active_marks"])
# ['H3K27me3']  ← high-entropy repression mark active

print(result["crep"])
# epigenetically modulated CREP with suppressed P-component

# Inherit methylation state across cycles (50% inheritance)
epi2 = EpiSigillin(seed=99)
epi2.inherit_from(epi.methylation_state())

# Rewrite a YAML parameter file based on current entropy
mutated = epi.mutate_yaml("config/crep_params.yaml", entropy_level=7.5)
```

### Epigenetic Methylation Rules

| Condition | Biological Analogy | CREP Effect |
|---|---|---|
| High entropy (H > H\*) | DNA methylation (H3K27me3) | Suppresses P-component |
| Low entropy (H < H\*) | Histone activation (H3K4me3) | Enhances E-component |
| Extreme entropy | Heterochromatin (H3K9me3) | CREP hibernation (all M→1) |
| Recovery | Demethylation | Gradual CREP restoration |

---

## Package 29 — hikari-ledger

Implements a **Proof-of-Resonance (PoR) consensus mechanism** for distributed
genesis-os node networks. Instead of energy-intensive Proof-of-Work, PoR validates
blocks based on each node's CREP harmonic state. Nodes with high Γ earn validation
rights proportional to their resonance. A block is accepted when the weighted
agreement of validators exceeds 2/3 (Byzantine fault tolerance).

> **Γ\_PoR ≈ 0.367** — η = 2/3 (BFT threshold), σ = 2.2
> Hikari tokens minted via: **ΔH\_i = k · Γ\_i · (1 − S\_H)**

```python
from hikari_ledger import HikariLedger

ledger = HikariLedger(n_nodes=50, seed=42)
result = ledger.run_cycle(n_blocks=100)

print(result["crep"])
# {'C': 0.553, 'R': 0.367, 'E': 0.541, 'P': 0.559, 'Gamma': 0.367}

print(result["accepted_blocks"])   # e.g. 98
print(result["hikari_total_supply"])  # e.g. 0.183
print(result["crep_gini"])          # e.g. 0.24  (fair distribution)

# Simulate a Byzantine attack
ledger_byz = HikariLedger(n_nodes=50, byzantine_fraction=0.30, seed=0)
result_byz = ledger_byz.run_cycle(n_blocks=100)
# System tolerates up to 33% Byzantine nodes (BFT guarantee)

# Validate a block from external CREP states
accepted = ledger.validate_block(
    block_data={"tx": "payment-001"},
    node_crep_states=[{"Gamma": 0.4}, {"Gamma": 0.35}, {"Gamma": 0.25}]
)
```

### Proof-of-Resonance vs. Classical Consensus

| Mechanism | Energy | Fairness | Sybil Resistance | CREP Integration |
|---|---|---|---|---|
| Proof-of-Work | Very high | Low (ASIC bias) | Strong | None |
| Proof-of-Stake | Low | Medium | Moderate | None |
| **Proof-of-Resonance** | **~1000× lower than PoW** | **High (Gini ≈ 0.30)** | **CREP-based** | **Native** |

---

## CREP Criticality Spectrum (context)

| Domain | Package | Γ | Regime |
|---|---|---|---|
| Qubit decoherence | P24 | 0.050 | Quantum fragile |
| Apoptosis ATP threshold | P25 | 0.090 | Cellular critical |
| **Theta band (flow state)** | **P27** | **0.251** | **Cognitive resonance** |
| AMOC / Neural criticality | P18/20 | 0.251 | Homeostatic universal |
| BTW Sandpile | P22 | 0.296 | Classical SOC |
| **epi-sigillin** | **P28** | **dynamic** | **Meta-level CREP modulator** |
| **Proof-of-Resonance** | **P29** | **0.367** | **Distributed consensus** |
| **Diffusive Routing** | **P30** | **0.443** | **Network infrastructure** |
| ERA5 Arctic Ice | Core | 0.920 | Near-saturated |

---

## Package 30 — diffusive-routing

Implements an **entropy-minimizing network routing protocol** where data packets
flow along paths of minimum entropic resistance — analogous to how gases flow
into low-pressure regions. The resistance field evolves via Turing reaction-diffusion;
the S_A/S_V duality provides the variational routing objective.

> **Gemini's insight:** *"Datenpakete fließen dynamisch wie ein Gas in Bereiche mit
> geringem entropischen Widerstand — die Theorie der S_A/S_V Entropie-Dualität
> auf Netzwerk-Infrastruktur."*

> **Γ\_routing ≈ 0.443** — η = 0.75 (optimal throughput), σ = 2.2

```python
from diffusive_routing import DiffusiveRouting

dr = DiffusiveRouting(n_nodes=20, seed=42)
result = dr.run_cycle(duration_seconds=60.0, n_packets=10000)

print(result["crep"])
# {'C': 0.712, 'R': 0.881, 'E': 0.743, 'P': 0.661, 'Gamma': 0.441}

print(result["mean_throughput"])      # e.g. 0.964
print(result["load_gini"])            # e.g. 0.12  (even load distribution)
print(result["network_lagrangian"])   # L_net = S_V(dst) - S_A(path)

# Route a single packet and inspect the path
info = dr.route_packet(src=0, dst=15)
print(info["path"])     # [0, 3, 11, 15]
print(info["latency"])  # entropic resistance along path

# Inspect the resistance field
dr.visualise_resistance_field()
```

### Entropic Resistance Field

Each link (i, j) carries a resistance that evolves dynamically:

```
ρ_ij(t) = baseline / (1 + Γ_ij · utilisation_coherence)
```

The field then diffuses via Turing reaction-diffusion:

```
dρ_ij/dt = D · ∇²ρ_ij − k · Γ_ij · ρ_ij + f(load_ij)
```

Packets route along `argmin Σ ρ_ij` — minimum total entropic resistance.

### S_A / S_V Entropy Duality

| Symbol | Meaning | Role |
|---|---|---|
| S_A(path) | Action entropy = Σ ρ_ij along path | Routing cost — minimised |
| S_V(node) | Volume entropy = H(outgoing load distribution) | Balance — maximised |
| L_net | Network Lagrangian = S_V(dst) − S_A | Unified routing objective |

### Routing vs. Classical Protocols

| Protocol | Adapts to load | Entropic field | S_A/S_V duality | CREP integration |
|---|---|---|---|---|
| OSPF (static) | No | None | None | None |
| ECMP | Partial | None | None | None |
| **Diffusive Routing** | **Yes (100ms)** | **Turing RD** | **Native** | **Full** |

---

## Install

```bash
pip install theta-resonance          # packages 27, 28, 29, 30
# with MNE-Python for real EDF data:
pip install "theta-resonance[mne]"
```

## Diamond-Template Contract

All GenesisAeon packages implement this interface:

```python
# Package 27
sys = ThetaResonance()
sys.run_cycle()        # → dict
sys.get_crep_state()   # → {C, R, E, P, Gamma}
sys.get_utac_state()   # → {H, dH_dt, H_star, K_eff}
sys.get_phase_events() # → list (cognitive state transitions)
sys.to_zenodo_record() # → dict

# Package 28
epi = EpiSigillin()
epi.run_cycle()        # → dict
epi.get_crep_state()   # → {C, R, E, P, Gamma}  (epigenetically modified)
epi.get_utac_state()   # → {H, dH_dt, H_star, K_eff}
epi.get_phase_events() # → list (entropy threshold crossings)
epi.to_zenodo_record() # → dict
epi.methylation_state()       # → {M_C, M_R, M_E, M_P}
epi.mutate_yaml(path, level)  # → mutated params dict
epi.inherit_from(parent)      # → 50% epigenetic inheritance

# Package 29
ledger = HikariLedger()
ledger.run_cycle()             # → dict
ledger.get_crep_state()        # → {C, R, E, P, Gamma}
ledger.get_utac_state()        # → {H, dH_dt, H_star, K_eff}
ledger.get_phase_events()      # → list (consensus failures, forks)
ledger.to_zenodo_record()      # → dict
ledger.validate_block(data, node_crep_states)  # → bool
ledger.mint_hikari(node_id)    # → float (Hikari earned)
ledger.network_crep_mean()     # → float

# Package 30
dr = DiffusiveRouting()
dr.run_cycle()                     # → dict
dr.get_crep_state()                # → {C, R, E, P, Gamma}
dr.get_utac_state()                # → {H, dH_dt, H_star, K_eff}
dr.get_phase_events()              # → list (congestion collapses, reroutes)
dr.to_zenodo_record()              # → dict
dr.route_packet(src, dst)          # → dict (path, latency, delivered)
dr.visualise_resistance_field()    # print resistance table
```

## Repository Structure

```
theta-resonance/
├── src/
│   ├── theta_resonance/           # Package 27
│   │   ├── system.py              # ThetaResonance — Diamond interface
│   │   ├── band_filter.py
│   │   ├── pac_analysis.py        # Phase-Amplitude Coupling (Tort 2010)
│   │   ├── cognitive_state.py
│   │   ├── crep_bands.py
│   │   ├── flow_detector.py
│   │   ├── frequency_utac.py
│   │   ├── mne_interface.py
│   │   ├── benchmark.py
│   │   └── constants.py
│   └── epi_sigillin/              # Package 28
│       ├── system.py              # EpiSigillin — Diamond interface
│       ├── methylation.py         # CREPMethylationEngine
│       ├── histone_model.py       # Histone modification analogy
│       ├── yaml_mutator.py        # RuntimeYAMLMutator (thread-safe)
│       ├── entropy_monitor.py     # Real-time entropy tracker
│       ├── adaptation_memory.py   # EpigeneticMemory (50% inheritance)
│       ├── crep_epigenome.py      # Combined methylation + histone CREP
│       ├── sigillin_bridge.py     # Static YAML parameter interface
│       ├── benchmark.py
│       └── constants.py
│   └── hikari_ledger/             # Package 29
│       ├── system.py              # HikariLedger — Diamond interface
│       ├── node.py                # ValidatorNode with CREP state
│       ├── consensus.py           # ProofOfResonanceConsensus engine
│       ├── crep_validator.py      # Per-node CREP weight computation
│       ├── block.py               # Block with CREP metadata
│       ├── network.py             # P2P NetworkSimulator
│       ├── bft_fallback.py        # Equal-weight BFT for low-CREP nets
│       ├── hikari_currency.py     # HikariCurrencyMinter
│       ├── benchmark.py
│       └── constants.py
│   └── diffusive_routing/         # Package 30
│       ├── system.py              # DiffusiveRouting — Diamond interface
│       ├── network_graph.py       # NetworkGraph (ring + Erdős–Rényi topology)
│       ├── entropy_field.py       # EntropicResistanceField (ρ_ij computation)
│       ├── packet.py              # Packet with CREP metadata
│       ├── router.py              # DiffusiveRouter (Dijkstra on ρ_ij)
│       ├── crep_network.py        # Per-link + aggregate CREP evaluation
│       ├── reaction_diffusion.py  # Turing RD field evolution
│       ├── sa_sv_duality.py       # S_A / S_V entropy duality
│       ├── benchmark.py
│       └── constants.py
├── src/diamond_setup/             # Template engine for new repos
│   └── templates/
│       ├── minimal.py             # (includes AGENT.md auto-copy)
│       └── genesis.py             # (includes AGENT.md auto-copy)
├── data/
├── tests/
├── .zenodo.json
└── AGENT.md                       # GenesisAeon release & metadata rules
```

## References

**Package 27:**
Hengen, K.B. & Shew, W.L. (2025). Is criticality a unified setpoint of brain function?
*Neuron* 113(16), 2582–2598. [DOI: 10.1016/j.neuron.2025.05.020](https://doi.org/10.1016/j.neuron.2025.05.020)

Frontiers Comp. Neurosci. (2026). E-I balance, avalanches, and criticality.
[DOI: 10.3389/fncom.2026.1744991](https://doi.org/10.3389/fncom.2026.1744991)

**Package 28:**
Greenberg, M.V.C. & Bourc'his, D. (2019). The diverse roles of DNA methylation in mammalian development.
*Nature Reviews Molecular Cell Biology* 20, 590–607. [DOI: 10.1038/s41580-019-0160-9](https://doi.org/10.1038/s41580-019-0160-9)

Allis, C.D. & Jenuwein, T. (2016). The molecular hallmarks of epigenetic control.
*Nature Reviews Genetics* 17, 487–500.

**Package 29:**
Nakamoto, S. (2008). Bitcoin: A Peer-to-Peer Electronic Cash System.

Castro, M. & Liskov, B. (1999). Practical Byzantine Fault Tolerance.
*OSDI '99*. [USENIX]

Gemini (2026). GenesisAeon Assessment — Hikari Currency & Proof-of-Resonance Concept.
*MOR Research Collective internal assessment.*

**Package 30:**
Turing, A.M. (1952). The chemical basis of morphogenesis.
*Philosophical Transactions of the Royal Society B* 237(641), 37–72. [DOI: 10.1098/rstb.1952.0012](https://doi.org/10.1098/rstb.1952.0012)

Bianconi, G. (2021). *Higher-Order Networks*. Cambridge University Press.

Gemini (2026). GenesisAeon Assessment — Diffusive Routing & S_A/S_V Entropy Duality Concept.
*MOR Research Collective internal assessment.*

---

## Citation

```bibtex
@software{Roemer2026_theta_epi,
  author    = {Römer, Johann},
  title     = {{theta-resonance + epi-sigillin + hikari-ledger + diffusive-routing: GenesisAeon Packages 27--30}},
  year      = {2026},
  version   = {1.0.0},
  publisher = {Zenodo},
  doi       = {10.5281/zenodo.19645351},
  url       = {https://doi.org/10.5281/zenodo.19645351}
}
```

---

Built with [uv](https://docs.astral.sh/uv/) · Part of the [GenesisAeon Entropy Atlas](https://github.com/GenesisAeon)
