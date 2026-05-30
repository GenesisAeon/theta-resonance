# theta-resonance

**Brain Oscillation Bands as CREP Modulators — GenesisAeon Package 27**

## Triple Universality

> Γ_theta ≈ 0.251 = Γ_AMOC = Γ_neural_criticality

The theta band (4–8 Hz, flow state) shares its CREP setpoint with ocean circulation
(AMOC) and cortical criticality — all homeostatic systems converge at 50 % efficiency.

## Quickstart

```python
from theta_resonance import ThetaResonance

sys = ThetaResonance(seed=42)
result = sys.run_cycle(duration_seconds=60.0)
print(result["crep"]["Gamma"])  # ≈ 0.25
print(result["flow_state"])     # True
print(result["current_band"])   # 'theta'
```

## Diamond-Template Contract

| Method | Returns | Description |
|--------|---------|-------------|
| `run_cycle(duration_seconds)` | dict | Run full simulation cycle |
| `get_crep_state()` | dict | Current {C, R, E, P, Gamma} |
| `get_utac_state()` | dict | Current {H, dH_dt, H_star, K_eff} |
| `get_phase_events()` | list | Cognitive state transitions |
| `to_zenodo_record()` | dict | Zenodo-ready metadata |
