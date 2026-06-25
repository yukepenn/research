"""Typed claim-evidence dependency graph + deterministic impact propagation.

A report is modelled as a graph of atomic claims. Claims are supported by
evidence items (DIRECT_SUPPORT / ALTERNATIVE_SUPPORT) and related to one another
by TYPED edges:

    DIRECT_SUPPORT       claim <- evidence   (primary citation)
    ALTERNATIVE_SUPPORT  claim <- evidence   (independent redundant support)
    DERIVED_FROM         claim <- claim      (logical/textual derivation)
    NUMERIC_DEPENDENCY   claim <- claim      (value computed from upstream values)
    TEMPORAL_DEPENDENCY  claim <- claim      (validity/currency depends on upstream)
    QUALIFIED_BY         claim <- claim      (caveat / scoping qualifier)
    CONTRADICTED_BY      claim <- claim      (an upstream claim contradicts this one)

The :class:`ImpactPropagator` is the typed-graph analyzer (this paper's METHOD).
Given an :class:`EvidenceDelta` (a change in the evidence WORLD, not an author
edit) it deterministically predicts:

    affected   claims that MUST change (value/support changed + full downstream
               closure through propagating typed edges)
    contested  claims that become contested (a supporting source now conflicts)
    new        claims newly supported by the delta

Key semantics required by the research contract:
  * ALTERNATIVE_SUPPORT => a claim whose primary source is retracted is NOT
    necessarily affected (a redundant source still supports it).
  * a conflicting source => the directly-supported claim is *contested*, while
    its downstream dependents are *affected* (their basis is now uncertain).
  * temporal-validity changes propagate through TEMPORAL_DEPENDENCY even when no
    DIRECT_SUPPORT citation points at the changed evidence item.

Everything here is pure, deterministic and LLM-free.
"""
from __future__ import annotations

from dataclasses import dataclass, field


class EdgeType:
    DIRECT_SUPPORT = "DIRECT_SUPPORT"
    ALTERNATIVE_SUPPORT = "ALTERNATIVE_SUPPORT"
    DERIVED_FROM = "DERIVED_FROM"
    NUMERIC_DEPENDENCY = "NUMERIC_DEPENDENCY"
    TEMPORAL_DEPENDENCY = "TEMPORAL_DEPENDENCY"
    QUALIFIED_BY = "QUALIFIED_BY"
    CONTRADICTED_BY = "CONTRADICTED_BY"


ALL_EDGE_TYPES = frozenset({
    EdgeType.DIRECT_SUPPORT, EdgeType.ALTERNATIVE_SUPPORT, EdgeType.DERIVED_FROM,
    EdgeType.NUMERIC_DEPENDENCY, EdgeType.TEMPORAL_DEPENDENCY, EdgeType.QUALIFIED_BY,
    EdgeType.CONTRADICTED_BY,
})

# Claim->claim edges along which an upstream change PROPAGATES (must re-derive).
PROPAGATING_EDGES = frozenset({
    EdgeType.DERIVED_FROM, EdgeType.NUMERIC_DEPENDENCY,
    EdgeType.TEMPORAL_DEPENDENCY, EdgeType.QUALIFIED_BY,
})


@dataclass
class Claim:
    """An atomic claim asserted in a report.

    `supports` / `alt_supports` are evidence ids (DIRECT_SUPPORT /
    ALTERNATIVE_SUPPORT). Claim->claim relations live as edges on the
    :class:`ClaimGraph`; the value/formula/temporal_group fields carry the
    world physics used by the gold-set generator.
    """
    cid: str
    ctype: str                       # fact | numeric | comparison | derived | temporal
    text: str
    value: object = None             # float for numeric/comparison, str for fact, None=unsupported
    supports: tuple = ()             # DIRECT_SUPPORT evidence ids
    alt_supports: tuple = ()         # ALTERNATIVE_SUPPORT evidence ids
    citation: str | None = None      # evidence id shown in the report
    temporal_group: str | None = None
    formula: str | None = None       # human-readable derivation, e.g. "cA + cB"


@dataclass
class EvidenceDelta:
    """A change in the evidence WORLD (W_t -> W_{t+1}).

    Each field names which evidence items / temporal groups / claims changed.
    Both the flat-ledger baseline and the typed-graph analyzer read this same
    object; they differ only in how much of the graph they exploit.
    """
    dtype: str
    changed_value_evidence: frozenset = frozenset()    # numeric value revised
    retracted_evidence: frozenset = frozenset()        # source retracted
    superseded_evidence: frozenset = frozenset()       # replaced by new authoritative source
    conflicted_evidence: frozenset = frozenset()       # now in two-source conflict
    validity_changed_evidence: frozenset = frozenset() # temporal validity interval moved
    temporal_changed_groups: frozenset = frozenset()   # temporal group(s) whose currency shifted
    added_claim_ids: frozenset = frozenset()           # claims newly supported (N)

    def touched_evidence(self) -> frozenset:
        """Every evidence id a *flat* citation ledger would notice changed."""
        return (self.changed_value_evidence | self.retracted_evidence
                | self.superseded_evidence | self.conflicted_evidence
                | self.validity_changed_evidence)


@dataclass
class ClaimGraph:
    claims: dict[str, Claim]
    edges: list[tuple[str, str, str]] = field(default_factory=list)  # (upstream, downstream, etype)

    def __post_init__(self):
        # dependents[upstream] = [(downstream, etype), ...]
        self._dependents: dict[str, list[tuple[str, str]]] = {}
        for up, down, et in self.edges:
            self._dependents.setdefault(up, []).append((down, et))

    def dependents(self, cid: str) -> list[tuple[str, str]]:
        return self._dependents.get(cid, [])

    def edges_of_type(self, etype: str) -> list[tuple[str, str]]:
        return [(u, d) for (u, d, et) in self.edges if et == etype]


def downstream_closure(graph: ClaimGraph, seeds, edge_types) -> set[str]:
    """All claims reachable from `seeds` by following dependent edges whose type
    is in `edge_types` (inclusive of the seeds themselves)."""
    edge_types = frozenset(edge_types)
    seen = set(seeds)
    stack = list(seeds)
    while stack:
        u = stack.pop()
        for (down, et) in graph.dependents(u):
            if et in edge_types and down not in seen:
                seen.add(down)
                stack.append(down)
    return seen


@dataclass
class ImpactResult:
    affected: set[str]      # must-change (A-style prediction)
    contested: set[str]     # now-contested (C-style prediction)
    new: set[str]           # newly-supported (N-style prediction)

    @property
    def impacted(self) -> set[str]:
        return self.affected | self.contested


class ImpactPropagator:
    """The typed-graph analyzer: full deterministic propagation."""

    name = "typed_graph"

    def analyze(self, graph: ClaimGraph, delta: EvidenceDelta) -> ImpactResult:
        claims = graph.claims
        value_changed = delta.changed_value_evidence | delta.superseded_evidence

        value_seeds: set[str] = set()
        retraction_seeds: set[str] = set()
        temporal_seeds: set[str] = set()
        conflict_seeds: set[str] = set()

        for cid, c in claims.items():
            sup = set(c.supports)
            alt = set(c.alt_supports)
            # numeric value of a directly-supported claim changed
            if sup & value_changed:
                value_seeds.add(cid)
            # source retraction: affected ONLY if no support survives (respect
            # ALTERNATIVE_SUPPORT -> not necessarily affected)
            if sup & delta.retracted_evidence:
                remaining = (sup | alt) - delta.retracted_evidence
                if not remaining:
                    retraction_seeds.add(cid)
            # temporal validity / currency shift
            if c.temporal_group is not None and c.temporal_group in delta.temporal_changed_groups:
                temporal_seeds.add(cid)
            # conflicting source -> this claim is contested
            if sup & delta.conflicted_evidence:
                conflict_seeds.add(cid)

        # contested claims propagate the *uncertainty* downstream too, but the
        # contested node itself is reported as contested, not as affected.
        contested = set(conflict_seeds)
        # CONTRADICTED_BY: anything contradicted by a contested/changed claim
        impacted_basis = value_seeds | retraction_seeds | temporal_seeds | contested
        for up, down in graph.edges_of_type(EdgeType.CONTRADICTED_BY):
            if up in impacted_basis:
                contested.add(down)

        seeds = value_seeds | retraction_seeds | temporal_seeds | contested
        impacted = downstream_closure(graph, seeds, PROPAGATING_EDGES)

        new = set(delta.added_claim_ids)
        affected = impacted - contested - new
        return ImpactResult(affected=affected, contested=contested, new=new)


def build_graph(claims: dict[str, Claim], edges: list[tuple[str, str, str]]) -> ClaimGraph:
    return ClaimGraph(claims=claims, edges=list(edges))
