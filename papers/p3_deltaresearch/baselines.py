"""Impact predictors and report patchers (deterministic baselines + method).

Predictors (claims -> predicted impact set), all returning an ImpactResult:
  * flat_ledger_predict   : (a) flat claim-citation ledger -- only DIRECT_SUPPORT
                            edges, NO downstream propagation, NO alt-support /
                            temporal reasoning. The AAR-style weak baseline.
  * typed_graph_predict   : (b) the typed-graph analyzer (this paper's METHOD),
                            full deterministic propagation.
  * oracle_predict        : (c) oracle upper bound -- reads the gold sets.

Patchers (world + impact -> Patch), simulating editing strategies:
  * oracle_patcher        : edits EXACTLY a given predicted affected set (with the
                            correct post values / citations). With the gold set it
                            is the upper bound; with the typed prediction it is the
                            typed-graph patcher.
  * full_regeneration_patch : rewrites ALL claims -> spurious revision of U.
  * naive_revise_patch    : edits only directly-cited claims -> stale residual.

No LLM, no wall-clock; everything is a pure function of the World.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from papers.p3_deltaresearch.claim_graph import ImpactPropagator, ImpactResult
from papers.p3_deltaresearch.controlled_worlds.generator import ASSERTED, World


# --------------------------------------------------------------------------
# Predictors
# --------------------------------------------------------------------------
def flat_ledger_predict(world: World) -> ImpactResult:
    """(a) Flat claim-citation ledger: a claim is 'affected' iff it directly
    cites a changed evidence item. No propagation, no alternative-support or
    temporal reasoning -> misses derived/temporal downstream claims and
    over-flags alternatively-supported ones."""
    touched = world.delta.touched_evidence()
    affected = {cid for cid, c in world.claims.items() if set(c.supports) & touched}
    return ImpactResult(affected=affected, contested=set(), new=set())


def typed_graph_predict(world: World) -> ImpactResult:
    """(b) Typed dependency-graph analyzer with full propagation."""
    return ImpactPropagator().analyze(world.graph, world.delta)


def oracle_predict(world: World) -> ImpactResult:
    """(c) Oracle upper bound: returns the programmatic gold sets directly."""
    return ImpactResult(affected=set(world.gold_A), contested=set(world.gold_C),
                        new=set(world.gold_N))


# --------------------------------------------------------------------------
# Patch
# --------------------------------------------------------------------------
@dataclass
class Patch:
    """A claim-level edit: which claims were touched + their new content."""
    edited: set = field(default_factory=set)          # claim ids the patch rewrote
    new_values: dict = field(default_factory=dict)    # cid -> new value
    new_citations: dict = field(default_factory=dict) # cid -> updated citation
    flagged_contested: set = field(default_factory=set)
    added: set = field(default_factory=set)           # newly added claim ids


def _fill_values(world: World, cids, values: dict, citations: dict) -> None:
    for c in cids:
        if world.is_numeric(c):
            values[c] = world.post_values[c]
        citations[c] = world.post_citations[c]


def oracle_patcher(world: World, predicted_affected, *, contested=frozenset(),
                   new=frozenset()) -> Patch:
    """Edit EXACTLY the given predicted affected set, writing the correct post
    values/citations; flag the given contested set; add the given new claims.

    With (gold_A, gold_C, gold_N) this is the oracle upper bound; with a
    predictor's output it is that predictor's patcher (e.g. typed-graph)."""
    edited = set(predicted_affected)
    values: dict = {}
    citations: dict = {}
    _fill_values(world, edited, values, citations)
    added = set(new)
    _fill_values(world, added, values, citations)
    return Patch(edited=edited, new_values=values, new_citations=citations,
                 flagged_contested=set(contested), added=added)


def oracle_upper_bound_patch(world: World) -> Patch:
    return oracle_patcher(world, world.gold_A, contested=world.gold_C, new=world.gold_N)


def typed_graph_patch(world: World) -> Patch:
    pred = typed_graph_predict(world)
    return oracle_patcher(world, pred.affected, contested=pred.contested, new=pred.new)


def naive_revise_patch(world: World) -> Patch:
    """Edits only the directly-cited claims (flat-ledger scope) with correct
    values -> preserves unaffected claims but leaves STALE downstream residual."""
    pred = flat_ledger_predict(world)
    return oracle_patcher(world, pred.affected, contested=set(), new=set())


def full_regeneration_patch(world: World) -> Patch:
    """Simulated full regeneration: rewrites EVERY claim. Values are correct, but
    every unaffected claim is touched -> spurious revision / low preservation
    (the Mr.DRE / EditPropBench failure mode)."""
    edited = set(ASSERTED)
    values: dict = {}
    citations: dict = {}
    _fill_values(world, edited, values, citations)
    added = set(world.gold_N)
    _fill_values(world, added, values, citations)
    return Patch(edited=edited, new_values=values, new_citations=citations,
                 flagged_contested=set(world.gold_C), added=added)
