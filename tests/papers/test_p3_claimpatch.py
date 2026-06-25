"""Validate the deterministic core of the no-gold ClaimPatch (no LLM)."""
from papers.p3_deltaresearch.claimpatch import (
    oracle_full_patch, oracle_graph_recompute_patch, recompute_patch)
from papers.p3_deltaresearch.evaluator.metrics import acr, ucp
from papers.p3_deltaresearch.worlds_v2 import generate_worlds_v2


def test_worlds_have_downstream_cascades_and_no_gold_in_view():
    worlds = generate_worlds_v2(n=12, seed0=0)
    assert len(worlds) == 12
    for w in worlds:
        # at least one DERIVED claim must change (a real cascade)
        assert any(w.claims[c].kind not in ("base", "fact") for c in w.gold_A), w.world_id
        assert w.gold_A and w.gold_U
        # the method view must NOT leak parents / gold / post-values
        view = w.r0_view()
        blob = str(view)
        assert "parents" not in blob and "gold" not in blob and "post_value" not in blob


def test_oracle_graph_recompute_recovers_gold_with_correct_values():
    """Using the GOLD structure + the deterministic calculator must reproduce the
    gold affected set AND the correct post-values (proves the calculator is right;
    the no-gold method differs only by inferring the structure instead)."""
    worlds = generate_worlds_v2(n=16, seed0=0)
    for w in worlds:
        patch = oracle_graph_recompute_patch(w)
        assert acr(patch, w.gold_A) == 1.0, (w.world_id, "missed affected")
        assert ucp(patch, w.gold_U) == 1.0, (w.world_id, "touched unaffected")
        # numeric values are the correct recomputed gold values
        for c in w.gold_A:
            if isinstance(w.post_values.get(c), (int, float)) and not isinstance(w.post_values[c], bool):
                assert c in patch.new_values
                assert abs(patch.new_values[c] - w.post_values[c]) < 1e-6


def test_oracle_full_is_perfect_and_empty_structure_underperforms():
    worlds = generate_worlds_v2(n=8, seed0=3)
    for w in worlds:
        assert acr(oracle_full_patch(w), w.gold_A) == 1.0
        # a method that infers NO structure (no derived edges, no directly_changed)
        # recovers little -> proves the task is non-trivial
        empty = recompute_patch(w, {"derived": {}, "directly_changed": []})
        assert acr(empty, w.gold_A) < 1.0
