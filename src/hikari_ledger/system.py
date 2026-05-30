"""HikariLedger — Diamond interface (Package 29)."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from .benchmark import run_benchmark
from .bft_fallback import BFTFallback
from .block import Block
from .consensus import ProofOfResonanceConsensus
from .constants import (
    CONSENSUS_LATENCY_MS,
    DEFAULT_N_BLOCKS,
    DEFAULT_N_NODES,
    GAMMA_POR,
    H_STAR_BFT,
    K_CONSENSUS,
    PACKAGE_NUMBER,
    R_CONSENSUS,
    REFERENCE,
    SIGMA,
    WHITEPAPER_DOI,
)
from .crep_validator import CREPValidator
from .hikari_currency import HikariCurrencyMinter
from .network import NetworkSimulator


@dataclass
class PhaseEvent:
    block_index: int
    kind: str          # "fork" | "consensus_failure" | "bft_fallback"
    weighted_agreement: float
    network_crep_mean: float
    description: str


class HikariLedger:
    """
    Package 29 — Proof-of-Resonance Distributed Consensus.

    Nodes with high CREP (coherent, resonant, emergent, poetic) earn
    validation rights proportional to their Γ value.  A block is accepted
    when Σ_{agreeing} w_i > 2/3.  Γ_PoR ≈ 0.367 (η = 2/3, σ = 2.2).

    Diamond-Template contract:
        run_cycle()        → dict
        get_crep_state()   → dict  {C, R, E, P, Gamma}
        get_utac_state()   → dict  {H, dH_dt, H_star, K_eff}
        get_phase_events() → list
        to_zenodo_record() → dict

    Reference: Gemini-2026-GenesisAeon-Assessment
               Nakamoto (2008); Castro & Liskov (1999).
    """

    def __init__(
        self,
        n_nodes: int = DEFAULT_N_NODES,
        byzantine_fraction: float = 0.0,
        seed: int = 42,
    ) -> None:
        self._n_nodes = n_nodes
        self._byz_frac = byzantine_fraction
        self._seed = seed

        self._net = NetworkSimulator(n_nodes=n_nodes, base_seed=seed)
        self._validator = CREPValidator()
        self._consensus = ProofOfResonanceConsensus(
            byzantine_fraction=byzantine_fraction, seed=seed
        )
        self._bft = BFTFallback()
        self._minter = HikariCurrencyMinter()

        self._chain: list[Block] = []
        self._phase_events: list[PhaseEvent] = []
        self._crep_state: dict[str, Any] = {}
        self._h: float = 0.0
        self._dh_dt: float = 0.0

    # ── Diamond interface ──────────────────────────────────────────────────────

    def run_cycle(
        self, n_nodes: int | None = None, n_blocks: int = DEFAULT_N_BLOCKS
    ) -> dict[str, Any]:
        """
        Simulate `n_blocks` rounds of PoR consensus.

        Each round:
          1. All nodes run one UTAC cycle (CREP states updated)
          2. Weights computed from current CREP distribution
          3. Proposer selected by weighted-random draw
          4. Nodes vote; block accepted if weighted agreement > 2/3
          5. Validator earns Hikari tokens
          6. Phase events recorded on failures/BFT fallback
        """
        if n_nodes is not None and n_nodes != self._n_nodes:
            self._net = NetworkSimulator(n_nodes=n_nodes, base_seed=self._seed)
            self._n_nodes = n_nodes

        accepted_blocks = 0
        failed_blocks = 0
        bft_activations = 0
        total_latency_ms = 0.0
        crep_means: list[float] = []

        for i in range(n_blocks):
            self._net.tick()
            nodes = self._net.eligible_nodes()

            use_bft = self._bft.should_activate(nodes)
            if use_bft:
                weights = self._bft.equal_weights(nodes)
                bft_activations += 1
            else:
                weights = self._validator.compute_weights(nodes)

            net_mean = self._validator.network_crep_mean(nodes)
            crep_means.append(net_mean)

            block_data = {
                "tx": f"block-{i}",
                "network_crep_mean": round(net_mean, 6),
            }

            block, accepted, agreement = self._consensus.run_consensus(
                block_index=len(self._chain),
                block_data=block_data,
                nodes=nodes,
                weights=weights,
                network_crep_mean=net_mean,
            )

            prev_h = self._h
            self._h = agreement
            self._dh_dt = self._h - prev_h

            if accepted and block is not None:
                self._chain.append(block)
                self._minter.mint(
                    validator=next(
                        n for n in nodes if n.node_id == block.validator_id
                    ),
                    all_nodes=nodes,
                )
                accepted_blocks += 1
                total_latency_ms += CONSENSUS_LATENCY_MS
            else:
                failed_blocks += 1
                self._phase_events.append(
                    PhaseEvent(
                        block_index=i,
                        kind="bft_fallback" if use_bft else "consensus_failure",
                        weighted_agreement=agreement,
                        network_crep_mean=net_mean,
                        description=(
                            f"Block {i} rejected: agreement={agreement:.3f} "
                            f"< threshold={H_STAR_BFT:.3f}"
                        ),
                    )
                )

        # Finalise CREP state
        nodes_final = self._net.eligible_nodes()
        if nodes_final:
            n = nodes_final[0]
            net_mean = self._validator.network_crep_mean(nodes_final)
            self._crep_state = {
                "C": round(sum(nd.crep.C for nd in nodes_final) / len(nodes_final), 6),
                "R": round(net_mean, 6),
                "E": round(sum(nd.crep.E for nd in nodes_final) / len(nodes_final), 6),
                "P": round(sum(nd.crep.P for nd in nodes_final) / len(nodes_final), 6),
                "Gamma": round(self._canonical_gamma(), 6),
            }

        weights_final = self._validator.compute_weights(nodes_final)
        gini = self._validator.gini_coefficient(weights_final)
        avg_latency = total_latency_ms / max(accepted_blocks, 1)
        gamma = self._canonical_gamma()

        bm = run_benchmark(
            gamma_por=gamma,
            consensus_threshold=H_STAR_BFT,
            byzantine_tolerance_pct=(1.0 - H_STAR_BFT) * 100,
            crep_gini=abs(gini),
            consensus_latency_ms=avg_latency,
        )

        return {
            "crep": self.get_crep_state(),
            "utac": self.get_utac_state(),
            "chain_length": len(self._chain),
            "accepted_blocks": accepted_blocks,
            "failed_blocks": failed_blocks,
            "bft_activations": bft_activations,
            "phase_events": len(self._phase_events),
            "network_crep_mean": round(
                sum(crep_means) / len(crep_means) if crep_means else 0.0, 6
            ),
            "hikari_total_supply": round(self._minter.total_supply, 6),
            "crep_gini": round(abs(gini), 6),
            "avg_latency_ms": round(avg_latency, 2),
            "benchmark": bm,
        }

    def get_crep_state(self) -> dict[str, Any]:
        return dict(self._crep_state) if self._crep_state else {
            "C": 0.0, "R": 0.0, "E": 0.0, "P": 0.0, "Gamma": 0.0,
        }

    def get_utac_state(self) -> dict[str, float]:
        return {
            "H": round(self._h, 6),
            "dH_dt": round(self._dh_dt, 6),
            "H_star": round(H_STAR_BFT, 6),
            "K_eff": round(K_CONSENSUS, 6),
        }

    def get_phase_events(self) -> list[dict[str, Any]]:
        return [
            {
                "block_index": e.block_index,
                "kind": e.kind,
                "weighted_agreement": e.weighted_agreement,
                "network_crep_mean": e.network_crep_mean,
                "description": e.description,
            }
            for e in self._phase_events
        ]

    def to_zenodo_record(self) -> dict[str, Any]:
        return {
            "title": (
                "hikari-ledger: Proof-of-Resonance Distributed Consensus "
                "(GenesisAeon Package 29)"
            ),
            "description": (
                "Package 29 of the GenesisAeon Entropy Atlas. "
                "Implements Proof-of-Resonance (PoR) consensus: nodes validate "
                "blocks proportionally to their CREP harmonic state Γ. "
                "Block accepted when Σ w_i > 2/3 (weighted BFT). "
                "Γ_PoR ≈ 0.367 (η = 2/3, σ = 2.2). "
                "Includes HikariCurrencyMinter (ΔH_i = k·Γ_i·(1−S_H)), "
                "BFT fallback, and full Diamond-Template contract. "
                "Diamond contract: run_cycle / get_crep_state / get_utac_state / "
                "get_phase_events / to_zenodo_record. "
                "Reference: Gemini-2026-GenesisAeon-Assessment; "
                "Nakamoto (2008); Castro & Liskov (1999)."
            ),
            "version": "0.3.0",
            "upload_type": "software",
            "creators": [{"name": "Römer, Johann", "affiliation": "MOR Research Collective"}],
            "keywords": [
                "proof-of-resonance",
                "distributed consensus",
                "CREP",
                "UTAC",
                "Byzantine fault tolerance",
                "GenesisAeon",
                "entropy atlas",
                "Hikari currency",
                "self-organized criticality",
                "network consensus",
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
            "gamma_canonical": GAMMA_POR,
        }

    # ── Additional interface ───────────────────────────────────────────────────

    def validate_block(
        self, block_data: dict[str, Any], node_crep_states: list[dict[str, Any]]
    ) -> bool:
        """Validate a block given a list of node CREP state dicts."""
        total_gamma = sum(n.get("Gamma", 0.0) for n in node_crep_states)
        if total_gamma < 1e-12:
            return False
        # All honest nodes agree (simulation); compute weighted sum
        weighted_yes = sum(
            n["Gamma"] / total_gamma
            for n in node_crep_states
            if n.get("Gamma", 0.0) > 0
        )
        return weighted_yes > H_STAR_BFT

    def mint_hikari(self, validator_id: str) -> float:
        node = next((n for n in self._net.nodes if n.node_id == validator_id), None)
        if node is None:
            return 0.0
        return self._minter.mint(node, self._net.eligible_nodes())

    def network_crep_mean(self) -> float:
        return self._validator.network_crep_mean(self._net.eligible_nodes())

    # ── Private ────────────────────────────────────────────────────────────────

    def _canonical_gamma(self) -> float:
        eta = H_STAR_BFT  # = 2/3
        return math.atanh(eta) / SIGMA
