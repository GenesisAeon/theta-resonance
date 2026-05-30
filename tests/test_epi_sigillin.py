"""Tests for epi-sigillin (Package 28)."""

from __future__ import annotations

from epi_sigillin import EpiSigillin
from epi_sigillin.adaptation_memory import EpigeneticMemory
from epi_sigillin.methylation import CREPMethylationEngine
from epi_sigillin.yaml_mutator import RuntimeYAMLMutator


def test_version():
    import epi_sigillin
    assert epi_sigillin.__version__ == "0.4.0"


def test_diamond_contract():
    sys = EpiSigillin(seed=42)
    sys.run_cycle(duration_cycles=20)

    crep = sys.get_crep_state()
    utac = sys.get_utac_state()
    events = sys.get_phase_events()
    zenodo = sys.to_zenodo_record()

    assert set(crep.keys()) >= {"C", "R", "E", "P", "Gamma"}
    assert set(utac.keys()) == {"H", "dH_dt", "H_star", "K_eff"}
    assert isinstance(events, list)
    assert zenodo["package_number"] == 28


def test_crep_gamma_in_range():
    sys = EpiSigillin(seed=42)
    sys.run_cycle(duration_cycles=50)
    crep = sys.get_crep_state()
    assert -1.0 <= crep["Gamma"] <= 1.0


def test_methylation_range():
    engine = CREPMethylationEngine()
    fake_crep = {"C": 0.5, "R": 0.5, "E": 0.5, "P": 0.5}
    for _ in range(30):
        state = engine.step(fake_crep, h=8.0, h_star=5.0, dt=1.0)
    for key, val in state.items():
        assert 0.0 <= val <= 1.0, f"{key} = {val} out of range"


def test_methylation_suppresses_with_high_entropy():
    engine = CREPMethylationEngine()
    fake_crep = {"C": 0.5, "R": 0.5, "E": 0.5, "P": 0.5}
    for _ in range(50):
        engine.step(fake_crep, h=9.5, h_star=5.0, dt=1.0)
    state = engine.methylation_state()
    assert any(v > 0.05 for v in state.values()), "Expected some methylation under high entropy"


def test_demethylation_under_low_entropy():
    engine = CREPMethylationEngine()
    fake_crep = {"C": 0.5, "R": 0.5, "E": 0.5, "P": 0.5}
    for _ in range(20):
        engine.step(fake_crep, h=9.0, h_star=5.0, dt=1.0)
    for _ in range(40):
        engine.step(fake_crep, h=1.0, h_star=5.0, dt=1.0)
    state = engine.methylation_state()
    total = sum(state.values())
    assert total < 4.0 * 0.9, "Demethylation should reduce total methylation"


def test_yaml_mutator_history():
    mutator = RuntimeYAMLMutator()
    params = {"crep": {"C": 0.5, "R": 0.5, "E": 0.5, "P": 0.5}}
    mutator.mutate(params, entropy_level=7.0, s_optimal=5.0, s_max=10.0)
    mutator.mutate(params, entropy_level=3.0, s_optimal=5.0, s_max=10.0)
    assert mutator.history_len() == 2
    restored = mutator.restore(-1)
    assert "crep" in restored


def test_epigenetic_memory_inheritance():
    mem = EpigeneticMemory()
    parent = {"M_C": 0.4, "M_R": 0.2, "M_E": 0.6, "M_P": 0.8}
    mem.record(parent)
    child = mem.inherit(parent)
    for key, val in parent.items():
        assert abs(child[key] - val * 0.5) < 1e-5


def test_run_cycle_returns_benchmark():
    sys = EpiSigillin(seed=42)
    result = sys.run_cycle(duration_cycles=30)
    assert "benchmark" in result
    assert "summary" in result["benchmark"]
    assert result["benchmark"]["summary"]["total"] > 0


def test_zenodo_record_has_doi():
    sys = EpiSigillin(seed=42)
    record = sys.to_zenodo_record()
    identifiers = [r["identifier"] for r in record["related_identifiers"]]
    assert any("10.5281/zenodo.19645351" in i for i in identifiers)


def test_inherit_from():
    sys = EpiSigillin(seed=42)
    sys.run_cycle(duration_cycles=10)
    parent_state = sys.methylation_state()
    sys2 = EpiSigillin(seed=99)
    sys2.inherit_from(parent_state)
    m = sys2.methylation_state()
    assert isinstance(m, dict)
    assert all(0.0 <= v <= 1.0 for v in m.values())
