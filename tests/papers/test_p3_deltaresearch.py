"""P3 DeltaResearch Tier-0 tests: controlled worlds, typed-graph impact
propagation vs flat ledger, patchers, dual metric, and the H_DIVERGE gate.

Everything here is deterministic and LLM-free: the gold A/U/N/C sets are computed
by the world generator's physics, and the typed-graph analyzer is a separate code
path, so these tests genuinely verify the method rather than restating it.
"""
import pytest

from papers.p3_deltaresearch.baselines import (
    Patch, flat_ledger_predict, full_regeneration_patch, naive_revise_patch,
    oracle_predict, oracle_patcher, oracle_upper_bound_patch, typed_graph_patch,
    typed_graph_predict,
)
from papers.p3_deltaresearch.controlled_worlds.generator import (
    ASSERTED, CPROJ, DELTA_TYPES, EFFECTFUL_DELTAS, generate_world, generate_worlds,
    world_is_consistent,
)
from papers.p3_deltaresearch.diverge import build_divergence_case, build_null_case
from papers.p3_deltaresearch.evaluator import metrics as M

SEEDS = range(6)


# ---- 1. generator: internally consistent worlds, non-empty A & U ----------
def test_worlds_internally_consistent_and_nonempty_gold():
    for s in SEEDS:
        for dt in DELTA_TYPES:
            w = generate_world(s, dt)
            assert world_is_consistent(w), f"{dt} seed={s} inconsistent"
            # gold sets partition the asserted claims
            assert set(w.gold_A) | set(w.gold_U) | set(w.gold_C) == set(ASSERTED)
            if dt == "irrelevant_update_negative_control":
                # negative control: nothing must change, everything preserved
                assert w.gold_A == frozenset()
                assert w.gold_U == frozenset(ASSERTED)
                assert w.gold_C == frozenset()
            else:
                assert w.gold_A, f"{dt} seed={s} has empty gold A"
                assert w.gold_U, f"{dt} seed={s} has empty gold U"
            # every world carries derived + temporal claims by construction
            assert {"cTotal", "cShare", "cIndex"} <= set(ASSERTED)


def test_delta_type_specific_gold():
    w = generate_world(0, "source_conflict")
    assert "cA" in w.gold_C and "cA" not in w.gold_A          # contested, not affected
    assert {"cTotal", "cShare", "cIndex", "cMargin"} <= set(w.gold_A)

    w = generate_world(0, "source_retraction")
    assert "cR" in w.gold_U                                   # alternative support preserves it
    assert "cA" in w.gold_A                                   # sole support lost

    w = generate_world(0, "new_authoritative_source")
    assert w.gold_N == frozenset({"cW"})                      # newly supported claim

    w = generate_world(0, "temporal_validity_change")
    assert set(w.gold_A) == {"cCur", "cProj"}


def test_generation_is_deterministic():
    a = generate_world(3, "numeric_revision")
    b = generate_world(3, "numeric_revision")
    assert a.gold_A == b.gold_A and a.gold_U == b.gold_U
    assert a.world_id == b.world_id
    assert a.pre_values == b.pre_values and a.post_values == b.post_values


# ---- 2. typed-graph analyzer matches gold & beats the flat ledger ----------
def test_typed_analyzer_equals_gold():
    for w in generate_worlds(n=6, dtypes=DELTA_TYPES):
        pred = typed_graph_predict(w)
        assert pred.affected == set(w.gold_A), f"{w.dtype}: {pred.affected} != {w.gold_A}"
        assert pred.contested == set(w.gold_C)
        assert pred.new == set(w.gold_N)


def test_typed_graph_strictly_beats_flat_ledger_acr():
    """On worlds with derived/temporal claims the typed analyzer recovers ALL
    must-change claims (ACR=1) while the flat citation ledger misses downstream
    propagation -> strictly lower ACR."""
    n_compared = 0
    for w in generate_worlds(n=6, dtypes=EFFECTFUL_DELTAS):
        typed = typed_graph_predict(w)
        flat = flat_ledger_predict(w)
        typed_acr = M.acr(Patch(edited=typed.affected), w.gold_A)
        flat_acr = M.acr(Patch(edited=flat.affected), w.gold_A)
        assert typed_acr == 1.0, f"{w.dtype}: typed ACR={typed_acr}"
        assert typed_acr > flat_acr, (
            f"{w.dtype} seed={w.seed}: typed {typed_acr} !> flat {flat_acr}")
        n_compared += 1
    assert n_compared == 6 * len(EFFECTFUL_DELTAS)


def test_flat_ledger_overflags_alternative_support():
    """The flat ledger flags an alternatively-supported claim whose primary was
    retracted (false positive); the typed analyzer correctly preserves it."""
    w = generate_world(0, "source_retraction")
    assert "cR" in flat_ledger_predict(w).affected
    assert "cR" not in typed_graph_predict(w).affected


# ---- 3. oracle upper bound ------------------------------------------------
def test_oracle_upper_bound_acr_is_one():
    for w in generate_worlds(n=6, dtypes=DELTA_TYPES):
        patch = oracle_upper_bound_patch(w)
        assert M.acr(patch, w.gold_A) == 1.0
        assert oracle_predict(w).affected == set(w.gold_A)


# ---- 4. patchers: preservation vs stale residual --------------------------
def test_full_regeneration_spurious_oracle_preserves():
    for w in generate_worlds(n=6, dtypes=EFFECTFUL_DELTAS):
        regen = full_regeneration_patch(w)
        oracle = oracle_upper_bound_patch(w)
        # full regen rewrites everything: high spurious revision, low preservation
        assert M.spurious_revision_rate(regen, w.gold_U) == 1.0
        assert M.ucp(regen, w.gold_U) == 0.0
        # ...yet it does change everything that must change
        assert M.acr(regen, w.gold_A) == 1.0
        # the oracle patch preserves every unaffected claim
        assert M.ucp(oracle, w.gold_U) == 1.0
        assert M.spurious_revision_rate(oracle, w.gold_U) == 0.0


def test_naive_revise_leaves_stale_residual_but_preserves():
    """Naive 'revise the cited claims' edits only directly-cited claims: it
    preserves U but leaves stale downstream residual (low ACR)."""
    w = generate_world(0, "numeric_revision")
    naive = naive_revise_patch(w)
    assert M.ucp(naive, w.gold_U) == 1.0
    assert M.stale_residual_rate(naive, w.gold_A) > 0.0
    assert M.acr(naive, w.gold_A) < 1.0


def test_typed_patch_is_pareto_optimal_vs_baselines():
    """The typed-graph patch dominates both failure modes on the (ACR, UCP)
    pair: it matches full-regen recall without its collateral damage, and beats
    naive-revise recall without sacrificing preservation."""
    w = generate_world(0, "upstream_recompute")
    typed = M.combined_score(typed_graph_patch(w), w)
    regen = M.combined_score(full_regeneration_patch(w), w)
    naive = M.combined_score(naive_revise_patch(w), w)
    assert typed.acr == 1.0 and typed.ucp == 1.0
    assert typed.dominates(regen)      # same recall, better preservation
    assert typed.dominates(naive)      # same preservation, better recall


def test_typed_patch_quality_metrics():
    """The typed-graph patch is calculation-correct, citation-fresh and
    conflict-honest across all delta types."""
    for w in generate_worlds(n=4, dtypes=DELTA_TYPES):
        rep = M.full_report(typed_graph_patch(w), w)
        assert rep["calculation_correctness"] == 1.0, w.dtype
        assert rep["citation_freshness"] == 1.0, w.dtype
        assert rep["conflict_honesty"] == 1.0, w.dtype
        assert rep["unsupported_new_rate"] == 0.0, w.dtype


# ---- 5. metrics correctness on hand-built cases ---------------------------
def test_metrics_on_hand_built_sets():
    gold_A = {"c1", "c2", "c3"}
    gold_U = {"c4", "c5"}
    gold_C = {"c6"}
    patch = Patch(edited={"c1", "c2", "c4"}, flagged_contested=set(),
                  added={"c7", "c8"})
    assert M.acr(patch, gold_A) == pytest.approx(2 / 3)
    assert M.stale_residual_rate(patch, gold_A) == pytest.approx(1 / 3)
    assert M.ucp(patch, gold_U) == pytest.approx(0.5)         # c5 preserved, c4 touched
    assert M.spurious_revision_rate(patch, gold_U) == pytest.approx(0.5)
    assert M.unsupported_new_rate(patch, {"c7"}) == pytest.approx(0.5)  # c8 unsupported
    assert M.conflict_honesty(patch, gold_C) == 0.0          # c6 not flagged
    assert M.conflict_honesty(Patch(flagged_contested={"c6"}), gold_C) == 1.0


def test_metrics_vacuous_denominators():
    empty = Patch()
    assert M.acr(empty, set()) == 1.0                        # nothing to recall
    assert M.ucp(empty, set()) == 1.0                        # nothing to preserve
    assert M.stale_residual_rate(empty, set()) == 0.0
    assert M.spurious_revision_rate(empty, set()) == 0.0
    assert M.conflict_honesty(empty, set()) == 1.0


def test_calculation_and_citation_metrics_catch_errors():
    w = generate_world(0, "numeric_revision")
    # a patch that edits the right claims but writes WRONG numbers
    bad_values = oracle_patcher(w, w.gold_A)
    bad_values.new_values = {c: 0.0 for c in bad_values.new_values}
    assert M.calculation_correctness(bad_values, w) < 1.0
    assert M.calculation_correctness(oracle_upper_bound_patch(w), w) == 1.0

    # retraction requires a citation refresh on cA (sole source retracted)
    wr = generate_world(0, "source_retraction")
    stale_cite = oracle_patcher(wr, wr.gold_A)
    stale_cite.new_citations = {}                            # forgot to refresh
    assert M.citation_freshness(stale_cite, wr) < 1.0
    assert M.citation_freshness(oracle_upper_bound_patch(wr), wr) == 1.0


# ---- 6. H_DIVERGE gate ----------------------------------------------------
def test_h_diverge_positive_on_numeric_temporal_downstream():
    for s in SEEDS:
        _, res = build_divergence_case(s)
        assert res.diverges, f"seed={s} expected divergence>0"
        assert res.divergence > 0.0
        assert CPROJ in res.missed_by_author       # author framing misses the projection


def test_h_diverge_zero_without_downstream():
    for s in SEEDS:
        _, res = build_null_case(s)
        assert res.divergence == 0.0
        assert res.author_set == res.evidence_set
