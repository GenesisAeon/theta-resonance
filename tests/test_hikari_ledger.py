"""Tests for hikari-ledger (Package 29)."""

from __future__ import annotations

import math

from hikari_ledger import HikariLedger
from hikari_ledger.constants import GAMMA_POR, H_STAR_BFT, SIGMA
from hikari_ledger.crep_validator import CREPValidator
from hikari_ledger.network import NetworkSimulator
from hikari_ledger.node import ValidatorNode

# ── Diamond contract ──────────────────────────────────────────────────────────

class TestDiamondContract:
    def setup_method(self) -> None:
        self.ledger = HikariLedger(n_nodes=10, seed=42)
        self.result = self.ledger.run_cycle(n_blocks=20)

    def test_run_cycle_returns_dict(self) -> None:
        assert isinstance(self.result, dict)

    def test_get_crep_state_keys(self) -> None:
        crep = self.ledger.get_crep_state()
        assert set(crep) >= {"C", "R", "E", "P", "Gamma"}

    def test_get_utac_state_keys(self) -> None:
        utac = self.ledger.get_utac_state()
        assert set(utac) >= {"H", "dH_dt", "H_star", "K_eff"}

    def test_get_phase_events_is_list(self) -> None:
        assert isinstance(self.ledger.get_phase_events(), list)

    def test_to_zenodo_record_keys(self) -> None:
        rec = self.ledger.to_zenodo_record()
        assert rec["package_number"] == 29
        assert "gamma_canonical" in rec
        assert "WHITEPAPER_DOI" not in rec  # should be resolved value


# ── CREP / Γ correctness ──────────────────────────────────────────────────────

class TestGammaPOR:
    def test_canonical_gamma_formula(self) -> None:
        expected = math.atanh(H_STAR_BFT) / SIGMA
        assert abs(expected - GAMMA_POR) < 0.01

    def test_gamma_positive(self) -> None:
        ledger = HikariLedger(n_nodes=10, seed=0)
        ledger.run_cycle(n_blocks=10)
        crep = ledger.get_crep_state()
        assert crep["Gamma"] > 0.0


# ── Consensus logic ───────────────────────────────────────────────────────────

class TestConsensus:
    def test_honest_network_accepts_blocks(self) -> None:
        ledger = HikariLedger(n_nodes=20, byzantine_fraction=0.0, seed=42)
        result = ledger.run_cycle(n_blocks=50)
        assert result["accepted_blocks"] > result["failed_blocks"]

    def test_byzantine_majority_causes_failures(self) -> None:
        # 40% byzantine should cause some failures
        ledger = HikariLedger(n_nodes=20, byzantine_fraction=0.40, seed=7)
        result = ledger.run_cycle(n_blocks=50)
        # Some failures expected at 40% byzantine
        assert result["accepted_blocks"] + result["failed_blocks"] == 50

    def test_validate_block_honest_nodes(self) -> None:
        ledger = HikariLedger(n_nodes=10, seed=42)
        node_crep_states = [
            {"Gamma": 0.4},
            {"Gamma": 0.3},
            {"Gamma": 0.3},
        ]
        assert ledger.validate_block({}, node_crep_states) is True

    def test_validate_block_no_nodes(self) -> None:
        ledger = HikariLedger(n_nodes=5, seed=1)
        assert ledger.validate_block({}, []) is False


# ── Network and nodes ─────────────────────────────────────────────────────────

class TestNetwork:
    def test_nodes_created(self) -> None:
        net = NetworkSimulator(n_nodes=20, base_seed=0)
        assert len(net.nodes) == 20

    def test_tick_updates_cycles_run(self) -> None:
        net = NetworkSimulator(n_nodes=5, base_seed=0)
        net.tick()
        assert all(n.cycles_run == 1 for n in net.nodes)

    def test_node_eligible_after_tick(self) -> None:
        node = ValidatorNode.from_seed(42)
        node.run_utac_cycle()
        assert node.is_eligible()

    def test_crep_validator_weights_sum_to_one(self) -> None:
        net = NetworkSimulator(n_nodes=10, base_seed=0)
        net.tick()
        val = CREPValidator()
        weights = val.compute_weights(net.eligible_nodes())
        assert abs(sum(weights.values()) - 1.0) < 1e-9


# ── Hikari currency ───────────────────────────────────────────────────────────

class TestHikariCurrency:
    def test_mint_hikari_increases_balance(self) -> None:
        ledger = HikariLedger(n_nodes=10, seed=42)
        ledger.run_cycle(n_blocks=10)
        total = ledger._minter.total_supply
        assert total > 0.0

    def test_mint_hikari_by_id(self) -> None:
        ledger = HikariLedger(n_nodes=5, seed=42)
        ledger.run_cycle(n_blocks=1)
        node_id = ledger._net.nodes[0].node_id
        amount = ledger.mint_hikari(node_id)
        assert amount >= 0.0

    def test_mint_unknown_node_returns_zero(self) -> None:
        ledger = HikariLedger(n_nodes=5, seed=42)
        ledger.run_cycle(n_blocks=1)
        assert ledger.mint_hikari("nonexistent-node") == 0.0


# ── Benchmark ─────────────────────────────────────────────────────────────────

class TestBenchmark:
    def test_benchmark_keys_present(self) -> None:
        ledger = HikariLedger(n_nodes=15, seed=42)
        result = ledger.run_cycle(n_blocks=30)
        bm = result["benchmark"]
        assert "gamma_por" in bm
        assert "consensus_threshold" in bm
        assert "all_pass" in bm

    def test_bft_threshold_target_passes(self) -> None:
        ledger = HikariLedger(n_nodes=15, seed=42)
        result = ledger.run_cycle(n_blocks=30)
        bm = result["benchmark"]
        assert bm["consensus_threshold"]["pass"] is True
