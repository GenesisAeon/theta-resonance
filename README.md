# theta-resonance

[![Package 27](https://img.shields.io/badge/GenesisAeon-Package%2027-blueviolet)](https://github.com/GenesisAeon/theta-resonance)
[![Whitepaper](https://img.shields.io/badge/Whitepaper-10.5281%2Fzenodo.19645351-blue)](https://doi.org/10.5281/zenodo.19645351)
[![Reference](https://img.shields.io/badge/Neuron%202025-Hengen%20%26%20Shew-green)](https://doi.org/10.1016/j.neuron.2025.05.020)
[![PyPI](https://img.shields.io/pypi/v/theta-resonance)](https://pypi.org/project/theta-resonance/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI](https://github.com/GenesisAeon/theta-resonance/actions/workflows/ci.yml/badge.svg)](https://github.com/GenesisAeon/theta-resonance/actions/workflows/ci.yml)

**Brain Oscillation Bands as CREP Modulators — GenesisAeon Entropy Atlas Package 27**

Models EEG frequency bands (δ/θ/α/β/γ) as channels of the CREP tensor within the
Unified Threshold Activation Criticality (UTAC) framework.

> **Triple Universality:** Γ_theta ≈ 0.251 = Γ_AMOC = Γ_neural_criticality  
> The brain's flow state (theta band) converges to the same CREP setpoint as ocean
> circulation (AMOC) and cortical criticality — all homeostatic systems at 50 % efficiency.

---

## CREP Criticality Spectrum (context)

| Domain | Package | Γ | Regime |
|---|---|---|---|
| Qubit decoherence | P24 | 0.050 | Quantum fragile |
| Apoptosis ATP threshold | P25 | 0.090 | Cellular critical |
| **Theta band (flow state)** | **P27** | **0.251** | **Cognitive resonance ← YOU ARE HERE** |
| AMOC / Neural criticality | P18/20 | 0.251 | Homeostatic universal |
| BTW Sandpile | P22 | 0.296 | Classical SOC |
| ERA5 Arctic Ice | Core | 0.920 | Near-saturated |

---

## Install

```bash
pip install theta-resonance
# with MNE-Python for real EDF data:
pip install "theta-resonance[mne]"
```

## Quickstart

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

With a real EDF file (requires `mne` extra):

```python
sys = ThetaResonance(edf_path="sub-01_eeg.edf")
result = sys.run_cycle(duration_seconds=300.0)
```

## Diamond-Template Contract

All GenesisAeon packages implement this interface:

```python
sys = ThetaResonance()
sys.run_cycle()        # → dict  (drives simulation, returns summary)
sys.get_crep_state()   # → dict  {C, R, E, P, Gamma}
sys.get_utac_state()   # → dict  {H, dH_dt, H_star, K_eff}
sys.get_phase_events() # → list  (cognitive state transitions)
sys.to_zenodo_record() # → dict  (Zenodo-ready metadata)

# Extras
sys.detect_flow_state()       # → bool
sys.current_band()            # → str  "delta"/"theta"/"alpha"/"beta"/"gamma"
sys.gamma_for_band("theta")   # → 0.25
```

## Frequency Band → CREP Mapping

| Band | Range | Cognitive State | Γ |
|---|---|---|---|
| Delta δ | 0.5–4 Hz | Deep sleep | 0.05 |
| **Theta θ** | **4–8 Hz** | **Flow / meditation** | **0.25** |
| Alpha α | 8–13 Hz | Relaxed attention | 0.35 |
| Beta β | 13–30 Hz | Active cognition | 0.55 |
| Gamma γ | 30–80 Hz | Error correction / arousal | 0.75 |

## Repository Structure

```
theta-resonance/
├── src/theta_resonance/
│   ├── system.py          # ThetaResonance — Diamond interface
│   ├── band_filter.py     # Per-band power estimation
│   ├── pac_analysis.py    # Phase-Amplitude Coupling (Tort 2010 MI)
│   ├── cognitive_state.py # Cognitive state classifier
│   ├── crep_bands.py      # Band → CREP tensor
│   ├── flow_detector.py   # Flow-state detection
│   ├── frequency_utac.py  # UTAC ODE for frequency dynamics
│   ├── mne_interface.py   # MNE-Python / OpenNeuro loader
│   ├── benchmark.py       # vs. Hengen & Shew 2025 targets
│   └── constants.py
├── data/
│   ├── band_definitions.yaml
│   └── cognitive_states_literature.yaml
├── tests/
├── .zenodo.json
└── AGENT.md               # GenesisAeon release & metadata rules
```

## Reference

Hengen, K.B. & Shew, W.L. (2025). Is criticality a unified setpoint of brain function?
*Neuron* 113(16), 2582–2598. [DOI: 10.1016/j.neuron.2025.05.020](https://doi.org/10.1016/j.neuron.2025.05.020)

Frontiers Comp. Neurosci. (2026). E-I balance, avalanches, and criticality.
[DOI: 10.3389/fncom.2026.1744991](https://doi.org/10.3389/fncom.2026.1744991)

Buzsáki, G. (2006). *Rhythms of the Brain*. Oxford University Press.

---

## Citation

```bibtex
@software{Roemer2026_theta_resonance,
  author    = {Römer, Johann},
  title     = {{theta-resonance: Brain Oscillation Bands as CREP Modulators}},
  year      = {2026},
  version   = {0.1.0},
  publisher = {Zenodo},
  doi       = {10.5281/zenodo.19645351},
  url       = {https://doi.org/10.5281/zenodo.19645351}
}
```

---

Built with [uv](https://docs.astral.sh/uv/) · Part of the [GenesisAeon Entropy Atlas](https://github.com/GenesisAeon)
