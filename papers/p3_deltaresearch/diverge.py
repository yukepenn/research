"""H_DIVERGE harness: evidence-WORLD delta vs equivalent author-style edit.

The gating hypothesis: one intended change, framed two ways, must produce
DIFFERENT downstream impact sets -- otherwise the "evidence-world delta" framing
is cosmetic and the project should not proceed.

  (a) author-edit framing: "edit claim X". An author-style edit only reasons
      about manuscript-visible relations -- it follows DERIVED_FROM / QUALIFIED_BY
      edges out of the named claim. It cannot see that a value/currency in the
      evidence world moved, so it misses NUMERIC_DEPENDENCY / TEMPORAL_DEPENDENCY
      propagation.

  (b) evidence-world delta framing: "evidence e changed". The typed-graph
      analyzer seeds from the affected evidence (incl. temporal currency) and
      propagates through ALL typed edges.

The divergence is the Jaccard distance between the two predicted impact sets.
divergence > 0 exactly when there are NUMERIC/TEMPORAL dependents the author
framing misses; divergence == 0 when the changed claim has no such downstream.

Pure / deterministic / LLM-free.
"""
from __future__ import annotations

from dataclasses import dataclass

from papers.p3_deltaresearch.claim_graph import (
    ClaimGraph, EdgeType, EvidenceDelta, ImpactPropagator, downstream_closure,
)
from papers.p3_deltaresearch.controlled_worlds.generator import (
    CCUR, CZ, E_S5, World, generate_world,
)

# An author-style manuscript edit only traverses manuscript-visible relations.
AUTHOR_EDIT_EDGES = frozenset({EdgeType.DERIVED_FROM, EdgeType.QUALIFIED_BY})


def author_edit_impact(graph: ClaimGraph, claim_id: str) -> set[str]:
    """Downstream set an author-edit framing of 'edit claim X' would touch."""
    return downstream_closure(graph, {claim_id}, AUTHOR_EDIT_EDGES)


def evidence_delta_impact(graph: ClaimGraph, delta: EvidenceDelta) -> set[str]:
    """Downstream set the evidence-world-aware typed analyzer would touch."""
    res = ImpactPropagator().analyze(graph, delta)
    return res.impacted


def jaccard_distance(a: set, b: set) -> float:
    a, b = set(a), set(b)
    union = a | b
    if not union:
        return 0.0
    return len(a ^ b) / len(union)


@dataclass(frozen=True)
class DivergenceResult:
    author_set: frozenset
    evidence_set: frozenset
    divergence: float                 # Jaccard distance in [0, 1]
    missed_by_author: frozenset       # claims the author framing fails to flag

    @property
    def diverges(self) -> bool:
        return self.divergence > 0.0


def diverge(graph: ClaimGraph, author_claim_id: str,
            evidence_delta: EvidenceDelta) -> DivergenceResult:
    """Measure behavioral divergence between the two framings of one change."""
    author = author_edit_impact(graph, author_claim_id)
    evidence = evidence_delta_impact(graph, evidence_delta)
    return DivergenceResult(
        author_set=frozenset(author),
        evidence_set=frozenset(evidence),
        divergence=jaccard_distance(author, evidence),
        missed_by_author=frozenset(evidence - author),
    )


# --------------------------------------------------------------------------
# Constructed cases for the gate test
# --------------------------------------------------------------------------
def build_divergence_case(seed: int = 0) -> tuple[World, DivergenceResult]:
    """A world WITH numeric/temporal downstream: updating the rate's evidence
    forces re-derivation of the projection (NUMERIC + TEMPORAL_DEPENDENCY) that an
    'edit claim cCur' author framing (DERIVED_FROM only) misses -> divergence > 0."""
    world = generate_world(seed, "temporal_validity_change")
    res = diverge(world.graph, CCUR, world.delta)
    return world, res


def build_null_case(seed: int = 0) -> tuple[World, DivergenceResult]:
    """A world with NO downstream dependents for the changed claim: the
    unrelated leaf cZ. Both framings flag exactly {cZ} -> divergence == 0."""
    world = generate_world(seed, "irrelevant_update_negative_control")
    leaf_delta = EvidenceDelta(dtype="numeric_revision",
                               changed_value_evidence=frozenset({E_S5}))
    res = diverge(world.graph, CZ, leaf_delta)
    return world, res
