"""Post-audit tests: no hidden-metadata leakage, independent calculator, public-input
recompute soundness, and the stricter Correct Update Recall metric."""
import random

import pytest

from papers.p3_deltaresearch import claimpatch_v2 as M
from papers.p3_deltaresearch.evaluator.metrics import acr, correct_update_recall
from papers.p3_deltaresearch.worlds_v2 import _compute, generate_worlds_v2


def _gold_structure(world):
    s = {"derived": {}}
    for cid in world.report_claims:
        c = world.claims[cid]
        if c.kind not in ("base", "fact"):
            s["derived"][cid] = {"parents": list(c.parents), "op": c.kind, "const": c.const}
    return s


def test_method_takes_only_public_dict_not_world():
    w = generate_worlds_v2(n=1, seed0=0)[0]
    # passing a World must be rejected (structural leakage guard)
    with pytest.raises(TypeError):
        M.run_pipeline_v2("claude", w)  # would also need CLI, but TypeError fires first
    # the public view exposes citations but NOT kind/source/parents/gold/post
    view = w.r0_view()
    blob = str(view)
    for forbidden in ("kind", "parents", "gold", "post_value", "'source'"):
        assert forbidden not in blob, forbidden
    assert all("citation" in c for c in view["claims"])


def test_independent_calculator_matches_generator_on_random_inputs():
    rng = random.Random(0)
    for _ in range(2000):
        a, b = rng.uniform(-50, 200), rng.uniform(1, 200)
        k = rng.choice([2.0, 5.0, 100.0])
        for op in ("SUM", "AVG", "DIFF", "RATIO", "SCALE", "PCT_CHANGE", "THRESHOLD"):
            args = [a] if op in ("SCALE", "THRESHOLD") else [a, b]
            assert M._calc(op, args, k) == _compute(op, args, k), (op, args, k)
    # and they are genuinely separate implementations (different source modules)
    assert M._calc.__module__ != _compute.__module__


def test_public_recompute_with_gold_structure_recovers_gold():
    """Feeding the GOLD structure into the PUBLIC-input recompute path recovers the
    gold affected set with correct values -> the public recompute is sound; the
    no-gold method differs only by INFERRING the structure (the LLM's job)."""
    for w in generate_worlds_v2(n=16, seed0=0):
        patch = M.recompute_from_public(w.r0_view(), _gold_structure(w))
        assert acr(patch, w.gold_A) == 1.0, (w.world_id, "missed affected")
        assert correct_update_recall(patch, w) == 1.0, (w.world_id, "wrong values")


def test_empty_structure_underperforms_and_curr_is_strict():
    for w in generate_worlds_v2(n=8, seed0=3):
        empty = M.recompute_from_public(w.r0_view(), {"derived": {}})
        # without inferring derived structure, downstream updates are missed
        assert correct_update_recall(empty, w) < 1.0


def test_worlds_unique_seed_independent_graphs():
    worlds = generate_worlds_v2(n=20, seed0=0)
    assert len({w.world_id for w in worlds}) == 20      # all distinct
    assert len({w.seed for w in worlds}) == 20          # one delta per seed -> independent graphs
