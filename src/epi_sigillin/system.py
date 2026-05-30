"""EpiSigillin — Diamond interface for Package 28."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Any

from .adaptation_memory import EpigeneticMemory
from .benchmark import run_benchmark
from .constants import (
    CREP_COUPLING,
    ENTROPY_RATE,
    PACKAGE_NUMBER,
    REFERENCE_DOI,
    S_MAX,
    S_OPTIMAL,
    WHITEPAPER_DOI,
)
from .crep_epigenome import CREPEpigenome
from .entropy_monitor import EntropyMonitor
from .sigillin_bridge import SigillinBridge
from .yaml_mutator import RuntimeYAMLMutator


@dataclass
class PhaseEvent:
    cycle: int
    h_before: float
    h_after: float
    entropy_level: float
    methylation_state: dict[str, float]
    description: str


class EpiSigillin:
    """
    Package 28 — Epigenetic Runtime Parameter Mutation.

    The system entropy level H(t) acts as the environmental signal that
    epigenetically modifies CREP parameters during runtime — analogous to
    how methylation and histone modifications alter gene expression without
    changing the underlying DNA sequence.

    Diamond-Template contract:
        run_cycle()         → dict
        get_crep_state()    → dict  {C, R, E, P, Gamma}
        get_utac_state()    → dict  {H, dH_dt, H_star, K_eff}
        get_phase_events()  → list
        to_zenodo_record()  → dict

    References:
        Greenberg & Bourc'his (2019). Nat. Rev. Mol. Cell Biol. 20, 590-607.
        DOI: 10.1038/s41580-019-0160-9
        Allis & Jenuwein (2016). Nat. Rev. Genetics 17, 487-500.
    """

    def __init__(
        self,
        sigillin_yaml: str | None = None,
        s_optimal: float = S_OPTIMAL,
        s_max: float = S_MAX,
        seed: int = 42,
    ) -> None:
        self._rng = random.Random(seed)
        self._s_optimal = s_optimal
        self._s_max = s_max

        self._bridge = SigillinBridge(sigillin_yaml)
        self._epigenome = CREPEpigenome()
        self._monitor = EntropyMonitor()
        self._memory = EpigeneticMemory()
        self._mutator = RuntimeYAMLMutator()

        self._base_crep: dict[str, Any] = self._bridge.base_crep()
        self._crep_state: dict[str, Any] = dict(self._base_crep)
        self._h = float(s_optimal)
        self._dh_dt = 0.0
        self._cycle = 0
        self._phase_events: list[PhaseEvent] = []

    # ── Diamond interface ──────────────────────────────────────────────────────

    def run_cycle(self, duration_cycles: int = 100) -> dict[str, Any]:
        """
        Simulate `duration_cycles` of epigenetic adaptation.

        Each step:
          1. Entropy monitor tracks system entropy H(t)
          2. CREPEpigenome applies methylation/histone modifications
          3. RuntimeYAMLMutator rewrites parameter state
          4. EpigeneticMemory records methylation pattern
          5. Phase events logged when H crosses H* threshold
        """
        adaptation_cycles_needed = 0
        initial_entropy = self._monitor.current() or self._h
        h_crossed = False

        for step in range(duration_cycles):
            noise = self._rng.gauss(0, 0.15)
            dh = ENTROPY_RATE * (self._s_optimal - self._h) + noise
            h_prev = self._h
            self._h = max(0.0, min(self._s_max, self._h + dh))
            self._dh_dt = self._h - h_prev

            entropy = self._monitor.update(self._crep_state)

            epi_state = self._epigenome.step(
                self._base_crep,
                h=self._h,
                h_star=self._s_optimal,
                k=self._s_max,
                dt=1.0,
            )
            self._crep_state = {k: v for k, v in epi_state.items() if k != "active_marks" and k != "methylation"}

            mutated_params = self._mutator.mutate(
                params={"crep": dict(self._crep_state), "utac": self._bridge.base_utac()},
                entropy_level=entropy,
                s_optimal=self._s_optimal,
                s_max=self._s_max,
            )

            if not h_crossed and abs(self._h - self._s_optimal) < 0.5:
                adaptation_cycles_needed = step + 1
                h_crossed = True

            if abs(self._h - self._s_optimal) < 0.3 and step > 0:
                self._phase_events.append(
                    PhaseEvent(
                        cycle=self._cycle + step,
                        h_before=h_prev,
                        h_after=self._h,
                        entropy_level=entropy,
                        methylation_state=self._epigenome.methylation_state(),
                        description=(
                            f"Entropy crossed H* ≈ {self._s_optimal:.2f} "
                            f"(H: {h_prev:.2f} → {self._h:.2f})"
                        ),
                    )
                )

        self._memory.record(
            self._epigenome.methylation_state(),
            metadata={"cycle_block": self._cycle, "duration": duration_cycles},
        )
        self._cycle += duration_cycles

        final_entropy = self._monitor.current()
        entropy_reduction = max(0.0, (initial_entropy - final_entropy) / max(initial_entropy, 1e-9))

        bm = run_benchmark(
            methylation_state=self._epigenome.methylation_state(),
            crep_state=self._crep_state,
            entropy_reduction=entropy_reduction,
            yaml_valid=self._mutator.history_len() > 0,
            adaptation_cycles=adaptation_cycles_needed or duration_cycles,
        )

        return {
            "crep": self.get_crep_state(),
            "utac": self.get_utac_state(),
            "methylation": self._epigenome.methylation_state(),
            "active_marks": self._epigenome.active_marks(),
            "phase_events": len(self._phase_events),
            "memory_generations": self._memory.generations(),
            "entropy_level": round(final_entropy, 4),
            "entropy_reduction": round(entropy_reduction, 4),
            "benchmark": bm,
            "yaml_mutations": self._mutator.history_len(),
        }

    def get_crep_state(self) -> dict[str, Any]:
        return dict(self._crep_state) if self._crep_state else {
            "C": 0.0, "R": 0.0, "E": 0.0, "P": 0.0, "Gamma": 0.0,
        }

    def get_utac_state(self) -> dict[str, float]:
        return {
            "H": round(self._h, 6),
            "dH_dt": round(self._dh_dt, 6),
            "H_star": round(self._s_optimal, 6),
            "K_eff": round(self._s_max, 6),
        }

    def get_phase_events(self) -> list[dict[str, Any]]:
        return [
            {
                "cycle": e.cycle,
                "h_before": e.h_before,
                "h_after": e.h_after,
                "entropy_level": e.entropy_level,
                "methylation": e.methylation_state,
                "description": e.description,
            }
            for e in self._phase_events
        ]

    def to_zenodo_record(self) -> dict[str, Any]:
        return {
            "title": "epi-sigillin: Epigenetic Runtime Parameter Mutation (GenesisAeon Package 28)",
            "description": (
                "Package 28 of the GenesisAeon Entropy Atlas. "
                "Implements epigenetic mutation of UTAC/CREP parameters during runtime: "
                "high entropy epochs methylate (suppress) CREP-P, low entropy epochs "
                "de-methylate (activate) CREP-E. Includes histone modification analogy, "
                "runtime YAML rewriting, and epigenetic inheritance across cycles. "
                "Diamond-Template contract: run_cycle / get_crep_state / get_utac_state / "
                "get_phase_events / to_zenodo_record. "
                "Reference: Greenberg & Bourc'his (2019). Nat. Rev. Mol. Cell Biol. 20, 590-607. "
                "DOI: 10.1038/s41580-019-0160-9"
            ),
            "version": "0.2.0",
            "upload_type": "software",
            "creators": [{"name": "Römer, Johann", "affiliation": "MOR Research Collective"}],
            "keywords": [
                "epigenetics",
                "DNA methylation",
                "histone modification",
                "CREP",
                "UTAC",
                "runtime parameter mutation",
                "GenesisAeon",
                "entropy atlas",
                "adaptive systems",
                "self-organization",
            ],
            "license": "MIT",
            "related_identifiers": [
                {
                    "relation": "isDocumentedBy",
                    "identifier": f"https://doi.org/{WHITEPAPER_DOI}",
                    "resource_type": "publication-report",
                },
                {
                    "relation": "isSupplementTo",
                    "identifier": f"https://doi.org/{REFERENCE_DOI}",
                    "resource_type": "publication-article",
                },
                {
                    "relation": "isPartOf",
                    "identifier": "https://doi.org/10.1038/s41576-016-0028-x",
                    "resource_type": "publication-article",
                },
            ],
            "package_number": PACKAGE_NUMBER,
            "gamma_canonical": "dynamic — f(S_total)",
        }

    # ── Additional interface ───────────────────────────────────────────────────

    def methylation_state(self) -> dict[str, float]:
        return self._epigenome.methylation_state()

    def mutate_yaml(self, target_file: str, entropy_level: float) -> dict[str, Any]:
        base = self._bridge.all_params()
        return self._mutator.mutate(
            params=base,
            entropy_level=entropy_level,
            s_optimal=self._s_optimal,
            s_max=self._s_max,
            target_path=target_file,
        )

    def inherit_from(self, parent_state: dict[str, float]) -> None:
        inherited = self._memory.inherit(parent_state)
        self._epigenome.set_methylation(inherited)
