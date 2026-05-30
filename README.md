# theta-resonance + epi-sigillin

[![Package 27](https://img.shields.io/badge/GenesisAeon-Package%2027-blueviolet)](https://github.com/GenesisAeon/theta-resonance)
[![Package 28](https://img.shields.io/badge/GenesisAeon-Package%2028-purple)](https://github.com/GenesisAeon/theta-resonance)
[![Whitepaper](https://img.shields.io/badge/Whitepaper-10.5281%2Fzenodo.19645351-blue)](https://doi.org/10.5281/zenodo.19645351)
[![Reference P27](https://img.shields.io/badge/Neuron%202025-Hengen%20%26%20Shew-green)](https://doi.org/10.1016/j.neuron.2025.05.020)
[![Reference P28](https://img.shields.io/badge/NatRevMCB%202019-Greenberg%20%26%20Bourc'his-green)](https://doi.org/10.1038/s41580-019-0160-9)
[![PyPI](https://img.shields.io/pypi/v/theta-resonance)](https://pypi.org/project/theta-resonance/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI](https://github.com/GenesisAeon/theta-resonance/actions/workflows/ci.yml/badge.svg)](https://github.com/GenesisAeon/theta-resonance/actions/workflows/ci.yml)

**GenesisAeon Entropy Atlas — Packages 27 & 28**

| Package | Module | Domain | Γ |
|---|---|---|---|
| **P27** | `theta_resonance` | Brain oscillation bands as CREP modulators | 0.251 (theta) |
| **P28** | `epi_sigillin` | Epigenetic runtime parameter mutation | dynamic — f(S_total) |

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

## CREP Criticality Spectrum (context)

| Domain | Package | Γ | Regime |
|---|---|---|---|
| Qubit decoherence | P24 | 0.050 | Quantum fragile |
| Apoptosis ATP threshold | P25 | 0.090 | Cellular critical |
| **Theta band (flow state)** | **P27** | **0.251** | **Cognitive resonance** |
| AMOC / Neural criticality | P18/20 | 0.251 | Homeostatic universal |
| BTW Sandpile | P22 | 0.296 | Classical SOC |
| **epi-sigillin** | **P28** | **dynamic** | **Meta-level CREP modulator** |
| ERA5 Arctic Ice | Core | 0.920 | Near-saturated |

---

## Install

```bash
pip install theta-resonance
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

---

## Citation

```bibtex
@software{Roemer2026_theta_epi,
  author    = {Römer, Johann},
  title     = {{theta-resonance + epi-sigillin: GenesisAeon Packages 27 \& 28}},
  year      = {2026},
  version   = {0.2.0},
  publisher = {Zenodo},
  doi       = {10.5281/zenodo.19645351},
  url       = {https://doi.org/10.5281/zenodo.19645351}
}
```

---

Built with [uv](https://docs.astral.sh/uv/) · Part of the [GenesisAeon Entropy Atlas](https://github.com/GenesisAeon)
