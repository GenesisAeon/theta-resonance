"""Tests for diffusive-routing (Package 30)."""

from __future__ import annotations

import math

import pytest

from diffusive_routing import DiffusiveRouting
from diffusive_routing.constants import GAMMA_ROUTING, H_STAR_ROUTING, SIGMA
from diffusive_routing.entropy_field import EntropicResistanceField
from diffusive_routing.network_graph import NetworkGraph
from diffusive_routing.packet import Packet
from diffusive_routing.reaction_diffusion import ReactionDiffusionField
from diffusive_routing.router import DiffusiveRouter
from diffusive_routing.sa_sv_duality import SAVDuality

# ── Diamond contract ──────────────────────────────────────────────────────────

class TestDiamondContract:
    def setup_method(self) -> None:
        self.dr = DiffusiveRouting(n_nodes=10, seed=42)
        self.result = self.dr.run_cycle(duration_seconds=5.0, n_packets=100)

    def test_run_cycle_returns_dict(self) -> None:
        assert isinstance(self.result, dict)

    def test_get_crep_state_keys(self) -> None:
        crep = self.dr.get_crep_state()
        assert set(crep) >= {"C", "R", "E", "P", "Gamma"}

    def test_get_utac_state_keys(self) -> None:
        utac = self.dr.get_utac_state()
        assert set(utac) >= {"H", "dH_dt", "H_star", "K_eff"}

    def test_utac_h_star(self) -> None:
        utac = self.dr.get_utac_state()
        assert abs(utac["H_star"] - H_STAR_ROUTING) < 1e-9

    def test_get_phase_events_is_list(self) -> None:
        assert isinstance(self.dr.get_phase_events(), list)

    def test_to_zenodo_record_keys(self) -> None:
        rec = self.dr.to_zenodo_record()
        assert rec["package_number"] == 30
        assert "gamma_canonical" in rec
        assert rec["gamma_canonical"] == pytest.approx(GAMMA_ROUTING, abs=0.001)

    def test_zenodo_whitepaper_doi(self) -> None:
        rec = self.dr.to_zenodo_record()
        ids = rec["related_identifiers"]
        dois = [r["identifier"] for r in ids]
        assert any("10.5281/zenodo.19645351" in d for d in dois)


# ── Γ formula ─────────────────────────────────────────────────────────────────

class TestGammaRouting:
    def test_canonical_gamma_formula(self) -> None:
        expected = math.atanh(H_STAR_ROUTING) / SIGMA
        assert abs(expected - GAMMA_ROUTING) < 0.005

    def test_gamma_positive_after_cycle(self) -> None:
        dr = DiffusiveRouting(n_nodes=8, seed=0)
        dr.run_cycle(duration_seconds=3.0, n_packets=50)
        crep = dr.get_crep_state()
        assert crep["Gamma"] > 0.0

    def test_crep_components_in_unit_interval(self) -> None:
        dr = DiffusiveRouting(n_nodes=10, seed=7)
        dr.run_cycle(duration_seconds=5.0, n_packets=100)
        crep = dr.get_crep_state()
        for key in ("C", "R", "E", "P"):
            assert 0.0 <= crep[key] <= 1.0, f"{key} = {crep[key]} out of [0,1]"


# ── Network graph ──────────────────────────────────────────────────────────────

class TestNetworkGraph:
    def test_graph_has_nodes(self) -> None:
        g = NetworkGraph(n_nodes=15, seed=42)
        assert len(g.nodes()) == 15

    def test_graph_is_connected_via_ring(self) -> None:
        g = NetworkGraph(n_nodes=8, seed=1)
        for i in range(8):
            assert g.has_edge(i, (i + 1) % 8)

    def test_resistance_positive(self) -> None:
        g = NetworkGraph(n_nodes=10, seed=42)
        for e in g.edges():
            assert g.resistance(*e) > 0.0

    def test_load_reset(self) -> None:
        g = NetworkGraph(n_nodes=5, seed=0)
        for e in g.edges():
            g.add_load(*e, 3.0)
        g.reset_loads()
        for e in g.edges():
            assert g.load(*e) == 0.0


# ── Entropy field ──────────────────────────────────────────────────────────────

class TestEntropicResistanceField:
    def test_compute_lowers_resistance_for_high_crep(self) -> None:
        g = NetworkGraph(n_nodes=6, seed=42)
        # Set high Γ on all links
        for e in g.edges():
            g.set_gamma_ij(*e, 0.9)
        field = EntropicResistanceField()
        field.compute(g)
        for e in g.edges():
            assert g.resistance(*e) < 1.0

    def test_total_entropy_positive(self) -> None:
        g = NetworkGraph(n_nodes=8, seed=5)
        field = EntropicResistanceField()
        field.compute(g)
        assert field.total_entropy(g) > 0.0


# ── Router ─────────────────────────────────────────────────────────────────────

class TestDiffusiveRouter:
    def test_route_delivers_packet(self) -> None:
        g = NetworkGraph(n_nodes=10, seed=42)
        router = DiffusiveRouter()
        pkt = Packet(src=0, dst=5)
        router.route(g, pkt)
        assert pkt.delivered
        assert pkt.path[0] == 0
        assert pkt.path[-1] == 5

    def test_route_same_node(self) -> None:
        g = NetworkGraph(n_nodes=5, seed=0)
        router = DiffusiveRouter()
        pkt = Packet(src=2, dst=2)
        router.route(g, pkt)
        # Dijkstra returns trivial path [2] with dist=0
        assert pkt.latency == pytest.approx(0.0)

    def test_shortest_hop_path_length(self) -> None:
        g = NetworkGraph(n_nodes=5, seed=0)
        router = DiffusiveRouter()
        # Ring backbone ensures all nodes reachable in ≤ n/2 hops
        sp = router.shortest_hop_path_length(g, 0, 2)
        assert sp >= 1

    def test_latency_positive_for_different_nodes(self) -> None:
        g = NetworkGraph(n_nodes=10, seed=42)
        EntropicResistanceField().compute(g)
        router = DiffusiveRouter()
        pkt = Packet(src=0, dst=9)
        router.route(g, pkt)
        if pkt.delivered:
            assert pkt.latency > 0.0


# ── Reaction diffusion ─────────────────────────────────────────────────────────

class TestReactionDiffusion:
    def test_step_changes_resistances(self) -> None:
        g = NetworkGraph(n_nodes=8, seed=42)
        rd = ReactionDiffusionField()
        initial = {e: g.resistance(*e) for e in g.edges()}
        g.add_load(*g.edges()[0], 5.0)   # inject load on one edge
        rd.step(g)
        changed = any(g.resistance(*e) != initial[e] for e in g.edges())
        assert changed

    def test_resistance_stays_positive(self) -> None:
        g = NetworkGraph(n_nodes=10, seed=3)
        rd = ReactionDiffusionField()
        for _ in range(10):
            rd.step(g)
        for e in g.edges():
            assert g.resistance(*e) > 0.0


# ── S_A / S_V duality ─────────────────────────────────────────────────────────

class TestSAVDuality:
    def test_action_entropy_positive(self) -> None:
        g = NetworkGraph(n_nodes=6, seed=42)
        duality = SAVDuality()
        path = [0, 1, 2]
        if g.has_edge(0, 1) and g.has_edge(1, 2):
            assert duality.action_entropy(g, path) > 0.0

    def test_volume_entropy_non_negative(self) -> None:
        g = NetworkGraph(n_nodes=6, seed=42)
        g.add_load(0, 1, 3.0)
        duality = SAVDuality()
        assert duality.volume_entropy(g, 0) >= 0.0

    def test_path_entropy_zero_for_constant_hops(self) -> None:
        duality = SAVDuality()
        assert duality.path_entropy([3, 3, 3, 3]) == pytest.approx(0.0)

    def test_path_entropy_positive_for_mixed_hops(self) -> None:
        duality = SAVDuality()
        assert duality.path_entropy([1, 2, 3, 4, 5]) > 0.0


# ── Full cycle integration ─────────────────────────────────────────────────────

class TestFullCycle:
    def test_delivered_positive(self) -> None:
        dr = DiffusiveRouting(n_nodes=12, seed=42)
        result = dr.run_cycle(duration_seconds=10.0, n_packets=200)
        assert result["delivered"] > 0

    def test_benchmark_keys_present(self) -> None:
        dr = DiffusiveRouting(n_nodes=10, seed=42)
        result = dr.run_cycle(duration_seconds=5.0, n_packets=100)
        bm = result["benchmark"]
        assert "gamma_routing" in bm
        assert "all_pass" in bm

    def test_route_packet_api(self) -> None:
        dr = DiffusiveRouting(n_nodes=10, seed=42)
        info = dr.route_packet(0, 5)
        assert "path" in info
        assert "delivered" in info

    def test_network_lagrangian_finite(self) -> None:
        dr = DiffusiveRouting(n_nodes=10, seed=42)
        result = dr.run_cycle(duration_seconds=5.0, n_packets=100)
        assert math.isfinite(result["network_lagrangian"])
