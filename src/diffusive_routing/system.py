"""DiffusiveRouting — Diamond interface (Package 30)."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Any

from .benchmark import run_benchmark
from .constants import (
    DEFAULT_DURATION_S,
    DEFAULT_N_NODES,
    DEFAULT_N_PACKETS,
    GAMMA_ROUTING,
    H_STAR_ROUTING,
    K_THROUGHPUT,
    PACKAGE_NUMBER,
    SIGMA,
    WHITEPAPER_DOI,
)
from .crep_network import CREPNetworkState, NetworkCREPEvaluator
from .entropy_field import EntropicResistanceField
from .network_graph import NetworkGraph
from .packet import Packet
from .reaction_diffusion import ReactionDiffusionField
from .router import DiffusiveRouter
from .sa_sv_duality import SAVDuality


@dataclass
class PhaseEvent:
    tick: int
    kind: str           # "congestion_collapse" | "reroute_cascade" | "field_reset"
    mean_resistance: float
    throughput: float
    description: str


class DiffusiveRouting:
    """
    Package 30 — Entropy-Minimizing Network Routing.

    Data packets flow along paths of minimum entropic resistance ρ_ij,
    analogous to gas molecules flowing into low-pressure regions.  The
    resistance field evolves via Turing reaction-diffusion; the S_A/S_V
    duality provides the variational routing objective.

    Γ_routing ≈ 0.443  (η = 0.75, σ = 2.2).

    Diamond-Template contract:
        run_cycle()        → dict
        get_crep_state()   → dict  {C, R, E, P, Gamma}
        get_utac_state()   → dict  {H, dH_dt, H_star, K_eff}
        get_phase_events() → list
        to_zenodo_record() → dict

    References:
        Turing (1952) DOI:10.1098/rstb.1952.0012
        Bianconi (2021) Higher-Order Networks, Cambridge UP
        Gemini-2026-GenesisAeon-Assessment
    """

    def __init__(
        self,
        n_nodes: int = DEFAULT_N_NODES,
        seed: int = 42,
    ) -> None:
        self._n_nodes = n_nodes
        self._seed = seed
        self._rng = random.Random(seed)

        self._graph = NetworkGraph(n_nodes=n_nodes, seed=seed)
        self._field = EntropicResistanceField()
        self._rd = ReactionDiffusionField()
        self._router = DiffusiveRouter()
        self._crep_eval = NetworkCREPEvaluator(seed=seed)
        self._sa_sv = SAVDuality()

        self._phase_events: list[PhaseEvent] = []
        self._crep_state: CREPNetworkState = CREPNetworkState()
        self._h: float = 0.0
        self._dh_dt: float = 0.0
        self._tick: int = 0

    # ── Diamond interface ──────────────────────────────────────────────────────

    def run_cycle(
        self,
        duration_seconds: float = DEFAULT_DURATION_S,
        n_packets: int = DEFAULT_N_PACKETS,
    ) -> dict[str, Any]:
        """
        Route *n_packets* through the network over *duration_seconds*.

        Each simulated second:
          1. Resistance field updated (entropy field + RD step)
          2. Batch of packets routed via minimum-resistance Dijkstra
          3. CREP state evaluated from routing metrics
          4. Phase events recorded when congestion/reroute occurs
        """
        ticks = max(1, int(duration_seconds))
        packets_per_tick = max(1, n_packets // ticks)

        all_packets: list[Packet] = []
        throughputs: list[float] = []
        hop_counts: list[int] = []
        sp_hop_counts: list[int] = []

        for t in range(ticks):
            self._tick = t
            self._graph.reset_loads()

            # Advance resistance field
            self._field.compute(self._graph)
            self._rd.step(self._graph)

            # Route packets
            tick_delivered = 0
            tick_packets = self._make_packets(packets_per_tick)
            for pkt in tick_packets:
                self._router.route(self._graph, pkt)
                if pkt.delivered:
                    tick_delivered += 1
                    hop_counts.append(pkt.hop_count)
                    sp = self._router.shortest_hop_path_length(
                        self._graph, pkt.src, pkt.dst
                    )
                    if sp > 0:
                        sp_hop_counts.append(sp)
                all_packets.append(pkt)

            throughput = tick_delivered / max(packets_per_tick, 1)
            throughputs.append(throughput)
            prev_h = self._h
            self._h = throughput
            self._dh_dt = self._h - prev_h

            # Detect congestion phase events
            mean_r = self._field.mean_resistance(self._graph)
            if throughput < 0.4:
                self._phase_events.append(
                    PhaseEvent(
                        tick=t,
                        kind="congestion_collapse",
                        mean_resistance=mean_r,
                        throughput=throughput,
                        description=(
                            f"Tick {t}: throughput={throughput:.3f} < 0.4 "
                            f"— congestion collapse detected"
                        ),
                    )
                )

        # Final CREP evaluation
        mean_throughput = sum(throughputs) / len(throughputs)
        path_ent = self._sa_sv.path_entropy(hop_counts) / math.log(10)  # normalise
        eff = self._efficiency(hop_counts, sp_hop_counts)

        self._crep_state = self._crep_eval.evaluate(
            graph=self._graph,
            throughput_ratio=mean_throughput,
            efficiency_vs_baseline=eff,
            path_entropy=min(path_ent, 1.0),
        )
        self._crep_eval.update_link_gammas(self._graph, self._crep_state)

        # Gini coefficient of load distribution
        gini = self._gini(self._graph.load_distribution())

        # Congestion event rate
        cong_rate = len(self._phase_events) / (duration_seconds / 3600)

        bm = run_benchmark(
            throughput_vs_ospf=min(mean_throughput / 0.85, 2.0),  # OSPF baseline ≈ 85%
            latency_vs_sp=self._latency_ratio(hop_counts, sp_hop_counts),
            gamma_routing=self._crep_state.Gamma,
            congestion_events_per_hour=cong_rate,
            load_balance_gini=gini,
            adaptation_time_ms=100.0,
        )

        return {
            "crep": self.get_crep_state(),
            "utac": self.get_utac_state(),
            "packets_routed": len(all_packets),
            "delivered": sum(1 for p in all_packets if p.delivered),
            "mean_throughput": round(mean_throughput, 6),
            "mean_hop_count": round(sum(hop_counts) / max(len(hop_counts), 1), 3),
            "path_entropy": round(path_ent, 6),
            "load_gini": round(gini, 6),
            "phase_events": len(self._phase_events),
            "network_lagrangian": round(
                self._sa_sv.network_lagrangian(
                    self._graph,
                    [p.path for p in all_packets if p.delivered],
                ),
                6,
            ),
            "benchmark": bm,
        }

    def get_crep_state(self) -> dict[str, Any]:
        s = self._crep_state
        return {
            "C": round(s.C, 6),
            "R": round(s.R, 6),
            "E": round(s.E, 6),
            "P": round(s.P, 6),
            "Gamma": round(s.Gamma, 6),
        }

    def get_utac_state(self) -> dict[str, float]:
        return {
            "H": round(self._h, 6),
            "dH_dt": round(self._dh_dt, 6),
            "H_star": round(H_STAR_ROUTING, 6),
            "K_eff": round(K_THROUGHPUT, 6),
        }

    def get_phase_events(self) -> list[dict[str, Any]]:
        return [
            {
                "tick": e.tick,
                "kind": e.kind,
                "mean_resistance": e.mean_resistance,
                "throughput": e.throughput,
                "description": e.description,
            }
            for e in self._phase_events
        ]

    def to_zenodo_record(self) -> dict[str, Any]:
        return {
            "title": (
                "diffusive-routing: Entropy-Minimizing Network Routing "
                "(GenesisAeon Package 30)"
            ),
            "description": (
                "Package 30 of the GenesisAeon Entropy Atlas. "
                "Implements entropy-minimizing network routing: packets flow along "
                "paths of minimum entropic resistance ρ_ij = baseline/(1+Γ_ij·coherence), "
                "analogous to gas molecules in a low-pressure field. "
                "The resistance field evolves via Turing reaction-diffusion. "
                "S_A/S_V entropy duality provides the variational routing objective. "
                "Γ_routing ≈ 0.443 (η = 0.75, σ = 2.2). "
                "Diamond contract: run_cycle / get_crep_state / get_utac_state / "
                "get_phase_events / to_zenodo_record. "
                "References: Turing (1952); Bianconi (2021); "
                "Gemini-2026-GenesisAeon-Assessment."
            ),
            "version": "0.4.0",
            "upload_type": "software",
            "creators": [{"name": "Römer, Johann", "affiliation": "MOR Research Collective"}],
            "keywords": [
                "diffusive routing",
                "entropy minimization",
                "entropic resistance",
                "network routing",
                "reaction-diffusion",
                "S_A/S_V duality",
                "CREP",
                "UTAC",
                "GenesisAeon",
                "entropy atlas",
                "information geometry",
                "self-organized criticality",
            ],
            "license": "MIT",
            "related_identifiers": [
                {
                    "relation": "isDocumentedBy",
                    "identifier": f"https://doi.org/{WHITEPAPER_DOI}",
                    "resource_type": "publication-report",
                },
                {
                    "relation": "isPartOf",
                    "identifier": "https://github.com/GenesisAeon",
                    "resource_type": "other",
                },
            ],
            "package_number": PACKAGE_NUMBER,
            "gamma_canonical": GAMMA_ROUTING,
        }

    # ── Additional interface ───────────────────────────────────────────────────

    def route_packet(self, src: int, dst: int, payload: bytes = b"") -> dict[str, Any]:
        """Route a single packet and return routing metadata."""
        self._field.compute(self._graph)
        pkt = Packet(src=src, dst=dst, payload_bytes=len(payload))
        self._router.route(self._graph, pkt)
        return {
            "src": src,
            "dst": dst,
            "path": pkt.path,
            "hop_count": pkt.hop_count,
            "latency": round(pkt.latency, 6),
            "delivered": pkt.delivered,
        }

    def visualise_resistance_field(self, save_path: str | None = None) -> None:
        """Print a text summary of the resistance field (no matplotlib required)."""
        edges = self._graph.edges()
        header = f"{'Edge':>12}  {'ρ_ij':>8}  {'Γ_ij':>8}  {'load':>6}"
        print(header)
        print("-" * len(header))
        for u, v in sorted(edges)[:20]:  # show first 20
            print(
                f"  ({u:3d},{v:3d})  "
                f"{self._graph.resistance(u, v):8.4f}  "
                f"{self._graph.gamma_ij(u, v):8.4f}  "
                f"{self._graph.load(u, v):6.1f}"
            )

    # ── Private ────────────────────────────────────────────────────────────────

    def _make_packets(self, n: int) -> list[Packet]:
        nodes = self._graph.nodes()
        packets = []
        for _ in range(n):
            src = self._rng.choice(nodes)
            dst = self._rng.choice([nd for nd in nodes if nd != src])
            packets.append(Packet(src=src, dst=dst))
        return packets

    @staticmethod
    def _gini(values: list[float]) -> float:
        if not values:
            return 0.0
        sv = sorted(values)
        n = len(sv)
        total = sum(sv)
        if total < 1e-12:
            return 0.0
        cum = 0.0
        for i, v in enumerate(sv):
            cum += (2 * (i + 1) - n - 1) * v
        return cum / (n * total)

    @staticmethod
    def _efficiency(hops: list[int], sp_hops: list[int]) -> float:
        """Fraction of packets with hop_count ≤ shortest_path + 1."""
        if not hops or not sp_hops:
            return 0.5
        n = min(len(hops), len(sp_hops))
        ok = sum(1 for h, sp in zip(hops[:n], sp_hops[:n], strict=False) if h <= sp + 1)
        return ok / n

    @staticmethod
    def _latency_ratio(hops: list[int], sp_hops: list[int]) -> float:
        if not hops or not sp_hops:
            return 1.05
        n = min(len(hops), len(sp_hops))
        if n == 0:
            return 1.05
        mean_h = sum(hops[:n]) / n
        mean_sp = sum(sp_hops[:n]) / n
        if mean_sp < 1e-9:
            return 1.05
        return mean_h / mean_sp

    def _canonical_gamma(self) -> float:
        return math.atanh(H_STAR_ROUTING) / SIGMA
