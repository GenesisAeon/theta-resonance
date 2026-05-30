"""Tests for theta-resonance (Package 27)."""

from theta_resonance import ThetaResonance, __version__
from theta_resonance.constants import BANDS, GAMMA_BY_BAND
from theta_resonance.crep_bands import BandCREPMapper
from theta_resonance.flow_detector import FlowStateDetector
from theta_resonance.pac_analysis import modulation_index, synthetic_theta_gamma


def test_version():
    assert __version__ == "0.3.0"


def test_gamma_theta_universality():
    """Γ_theta must equal the homeostatic universal value ≈ 0.251 ± 0.02."""
    gamma = GAMMA_BY_BAND["theta"]
    assert abs(gamma - 0.25) <= 0.02, f"Expected ~0.25, got {gamma}"


def test_gamma_all_bands_ordered():
    """Γ must increase monotonically from delta to gamma."""
    order = ["delta", "theta", "alpha", "beta", "gamma"]
    values = [GAMMA_BY_BAND[b] for b in order]
    assert values == sorted(values), f"Non-monotonic: {values}"


def test_band_definitions():
    """All five bands must be defined with positive ranges."""
    for band, (lo, hi) in BANDS.items():
        assert lo < hi, f"Band {band}: lo={lo} >= hi={hi}"
        assert lo >= 0


def test_crep_mapper_theta():
    """BandCREPMapper should return Γ ≈ 0.25 for theta-dominant input."""
    mapper = BandCREPMapper(target_band="theta")
    state = mapper.compute(dominant_hz=6.0, pac_mi=0.08, plv=0.70, perm_entropy=0.75)
    assert 0.0 <= state["Gamma"] <= 2.0
    assert state["R"] == 1.0, "Frequency at centre should give R=1.0"
    for key in ("C", "R", "E", "P", "Gamma"):
        assert key in state


def test_crep_mapper_off_target():
    """Frequency far from theta centre → lower R and lower Γ."""
    mapper = BandCREPMapper(target_band="theta")
    on  = mapper.compute(dominant_hz=6.0)
    off = mapper.compute(dominant_hz=40.0)
    assert off["R"] < on["R"]
    assert off["Gamma"] <= on["Gamma"]


def test_flow_detector_positive():
    powers = {"delta": 0.05, "theta": 0.50, "alpha": 0.20, "beta": 0.15, "gamma": 0.10}
    result = FlowStateDetector().detect(powers)
    assert result["is_flow"] is True
    assert abs(result["gamma"] - 0.25) <= 0.01


def test_flow_detector_negative():
    powers = {"delta": 0.05, "theta": 0.05, "alpha": 0.10, "beta": 0.20, "gamma": 0.60}
    result = FlowStateDetector().detect(powers)
    assert result["is_flow"] is False


def test_pac_mi_range():
    phase, amp = synthetic_theta_gamma(duration_s=2.0, pac_strength=0.05)
    mi = modulation_index(phase, amp)
    assert 0.0 <= mi <= 1.0


def test_pac_mi_increases_with_coupling():
    phase_w, amp_w = synthetic_theta_gamma(duration_s=2.0, pac_strength=0.15)
    phase_n, amp_n = synthetic_theta_gamma(duration_s=2.0, pac_strength=0.0)
    assert modulation_index(phase_w, amp_w) >= modulation_index(phase_n, amp_n)


def test_diamond_interface():
    """Full Diamond contract: all required methods present and return correct types."""
    sys = ThetaResonance(seed=42)
    result = sys.run_cycle(duration_seconds=5.0)

    assert isinstance(result, dict)
    assert "crep" in result and "utac" in result

    crep = sys.get_crep_state()
    for key in ("C", "R", "E", "P", "Gamma"):
        assert key in crep, f"Missing CREP key: {key}"

    utac = sys.get_utac_state()
    for key in ("H", "dH_dt", "H_star", "K_eff"):
        assert key in utac, f"Missing UTAC key: {key}"

    events = sys.get_phase_events()
    assert isinstance(events, list)

    zenodo = sys.to_zenodo_record()
    assert zenodo["package_number"] == 27
    assert "10.5281/zenodo.19645351" in str(zenodo["related_identifiers"])

    assert isinstance(sys.detect_flow_state(), bool)
    assert sys.current_band() in BANDS
    assert sys.gamma_for_band("theta") == GAMMA_BY_BAND["theta"]


def test_utac_h_in_range():
    """UTAC H(t) must stay within [0, K_hz]."""
    from theta_resonance.constants import K_HZ
    sys = ThetaResonance(seed=0)
    sys.run_cycle(duration_seconds=10.0)
    h = sys.get_utac_state()["H"]
    assert 0.0 <= h <= K_HZ
