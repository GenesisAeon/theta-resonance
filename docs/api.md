# API Reference

## ThetaResonance

Main class implementing the Diamond-Template contract.

```python
from theta_resonance import ThetaResonance

sys = ThetaResonance(
    edf_path=None,      # optional path to EDF file (requires mne extra)
    target_band="theta",
    seed=42,
)
```

### Methods

**`run_cycle(duration_seconds=300.0) → dict`**  
Drive the UTAC simulation. Returns summary dict with `crep`, `utac`, `cognitive_state`,
`flow_state`, `current_band`, `benchmark`, and `phase_events` count.

**`get_crep_state() → dict`**  
Returns `{C, R, E, P, Gamma, dominant_hz, target_band}`.

**`get_utac_state() → dict`**  
Returns `{H, dH_dt, H_star, K_eff, t}`.

**`get_phase_events() → list`**  
List of cognitive state transition dicts: `{t, from, to, gamma_before, gamma_after, description}`.

**`to_zenodo_record() → dict`**  
Zenodo-ready metadata for this package version.

**`detect_flow_state() → bool`**  
True when theta-dominant, alpha-suppressed, gamma-reduced.

**`current_band() → str`**  
Current dominant EEG band: `"delta"` / `"theta"` / `"alpha"` / `"beta"` / `"gamma"`.

**`gamma_for_band(band: str) → float`**  
Canonical CREP Γ for the named band.
