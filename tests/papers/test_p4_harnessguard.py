"""P4 HarnessGuard Tier-0 tests.

Validates the controlled corpus + the H2 measurement machinery:
- a non-trivial fraction of edits cause hidden pass->fail regressions,
- the regression matrix is reproducible,
- on the controlled (structured) corpus the edit-conditioned selector beats
  random at fixed budget (the H2 machinery CAN detect when selection helps),
- leave-one-lineage-out runs with NO leakage and still generalizes,
- the sequential policy REJECTs a planted dangerous edit and ACCEPTs a safe one,
- statistics bootstrap over EDITS, not task runs.

The simulated task-solver is a deterministic fixture (NOT a scientific result);
it exists only to make the H2 measurement valid and testable in Tier-0.
"""
import tempfile

import numpy as np
import pytest

from core.sealed.access import SealedAccessError
from papers.p4_harnessguard import evaluate as EV
from papers.p4_harnessguard.edit_corpus.edits import (
    all_edits, edits_by_lineage, get_edit, lineages)
from papers.p4_harnessguard.feature_extraction import features as F
from papers.p4_harnessguard.ground_truth import (
    Custodian, build_ground_truth, run_pair)
from papers.p4_harnessguard.modular_harness import (
    COMPONENTS, HarnessConfig, default_harness, run_task)
from papers.p4_harnessguard.selector import (
    HarnessGuardSelector, PairRiskModel, SequentialPolicy, diverse_canary_select,
    train_risk_model)
from papers.p4_harnessguard.task_suite import all_tasks


# --------------------------------------------------------------------------
# Module-scoped fixtures (build the corpus + model once)
# --------------------------------------------------------------------------
@pytest.fixture(scope="module")
def corpus():
    edits = all_edits()
    tasks = all_tasks()
    gt = build_ground_truth(edits, tasks)
    return edits, tasks, gt


@pytest.fixture(scope="module")
def model(corpus):
    edits, tasks, gt = corpus
    return train_risk_model(edits, tasks, gt, gt.old_traces)


# --------------------------------------------------------------------------
# Corpus shape & edit contract
# --------------------------------------------------------------------------
def test_corpus_sizes_and_contract(corpus):
    edits, tasks, _ = corpus
    assert len(edits) >= 12
    assert len({e.component for e in edits}) >= 4
    assert len(tasks) >= 20
    # each edit carries the full structured contract
    for e in edits:
        assert e.component in COMPONENTS
        assert e.natural_language_intent
        assert isinstance(e.expected_improvements, list)
        assert isinstance(e.expected_risks, list)
        for key in ("lines_changed", "prompt_tokens_changed", "tools_affected"):
            assert key in e.static_features
        assert e.intended_effect in {"improvement", "neutral", "harmful"}
        assert e.new_config != e.base_config  # the edit actually changes H
    # edits are grouped into lineages
    by_lin = edits_by_lineage()
    assert len(by_lin) >= 4
    assert sum(len(v) for v in by_lin.values()) == len(edits)


def test_task_components_are_structured(corpus):
    """Each task is sensitive to a small set of components (structured, not
    uniform) — so edits induce concentrated regressions."""
    _, tasks, _ = corpus
    fams = {t.family for t in tasks}
    assert len(fams) >= 2  # >=2 task families for family splits
    caps = set()
    for t in tasks:
        caps |= set(t.capabilities)
    # every component capability is exercised by at least one task
    from papers.p4_harnessguard.modular_harness import COMPONENT_CAPABILITY
    for cap in COMPONENT_CAPABILITY.values():
        assert cap in caps, cap


# --------------------------------------------------------------------------
# H1 / regression phenomenon
# --------------------------------------------------------------------------
def test_at_least_a_quarter_of_edits_regress(corpus):
    edits, _, gt = corpus
    n_reg = len(gt.edits_with_regression())
    frac = n_reg / len(edits)
    assert frac >= 0.25, f"only {frac:.2%} of edits regress (need >=25%)"


def test_regression_matrix_reproducible(corpus):
    edits, tasks, gt = corpus
    gt2 = build_ground_truth(edits, tasks)
    assert gt.fingerprint() == gt2.fingerprint()
    assert np.array_equal(gt.matrix, gt2.matrix)
    # paired runner is itself deterministic
    e, t = edits[0], tasks[0]
    assert run_pair(e, t, seed=0).regression == run_pair(e, t, seed=0).regression


def test_edits_change_outcomes_structurally(corpus):
    _, tasks, gt = corpus
    # a harmful retry edit flips exactly the retry-sensitive tasks
    drop = get_edit("e_retry_drop")
    flipped = [t for t in tasks
               if run_task(drop.base_config, t)[0] and not run_task(drop.new_config, t)[0]]
    assert flipped, "retry-drop edit should regress some task"
    assert all("recover" in t.task_id for t in flipped)  # only error_recovery tasks
    # a neutral edit changes NOTHING
    neutral = get_edit("e_retry_neutral")
    assert gt.n_regressions(neutral.edit_id) == 0
    for t in tasks:
        assert run_task(neutral.base_config, t)[0] == run_task(neutral.new_config, t)[0]


# --------------------------------------------------------------------------
# Features: no new-harness peeking
# --------------------------------------------------------------------------
def test_feature_matrix_shape_and_old_trace_only(corpus):
    edits, tasks, gt = corpus
    X, index = F.build_matrix(edits, tasks, gt.old_traces)
    assert X.shape == (len(edits) * len(tasks), len(F.feature_names()))
    assert len(index) == X.shape[0]
    # old traces come from the BASE harness; a verifier-add edit (base verifier
    # off) must show ZERO verification actions in its old trace
    add = get_edit("e_verifier_add")
    vh = next(t for t in tasks if t.task_id.startswith("workspace_verifyharm"))
    assert gt.old_traces[(add.edit_id, vh.task_id)]["n_verification_actions"] == 0


# --------------------------------------------------------------------------
# H2: edit-conditioned selection beats random at fixed budget
# --------------------------------------------------------------------------
def test_h2_selector_beats_random_at_budget(corpus, model):
    edits, tasks, gt = corpus
    res = EV.run_h2_evaluation(edits, tasks, gt, gt.old_traces,
                               n_random_seeds=8, model=model)
    for k in (1, 2, 4):
        assert res.harnessguard[k] > res.random[k] + 0.10, (
            k, res.harnessguard[k], res.random[k])
    # full budget recovers everything for every selector
    assert res.harnessguard["full"] == pytest.approx(1.0)
    assert res.random["full"] == pytest.approx(1.0)


def test_h2_paired_edit_bootstrap_excludes_zero(corpus, model):
    edits, tasks, gt = corpus
    rnd = EV.random_select_fn([t.task_id for t in tasks], seed=7)
    hg = EV.harnessguard_select_fn(model, gt.old_traces, tasks)
    ci, n_edits = EV.paired_selector_advantage(rnd, hg, edits, tasks, gt, 2,
                                               n_boot=800, seed=1)
    assert ci.point > 0
    assert ci.lo > 0, ci          # selector advantage CI excludes 0
    assert n_edits == len(gt.edits_with_regression())


def test_diverse_selector_balances_risk_and_coverage():
    # two high-risk near-duplicates vs a slightly lower-risk diverse task
    risk = {"a": 0.9, "b": 0.88, "c": 0.7}
    caps = {"a": ["x"], "b": ["x"], "c": ["y"]}
    # pure risk (alpha=0) -> top two by risk
    assert diverse_canary_select(risk, caps, 2, alpha=0.0) == ["a", "b"]
    # with diversity -> second pick switches to the uncovered capability
    assert diverse_canary_select(risk, caps, 2, alpha=0.3) == ["a", "c"]


# --------------------------------------------------------------------------
# OOD generalization: leave-one-edit-lineage-out, no leakage
# --------------------------------------------------------------------------
def test_leave_one_lineage_out_no_leakage(corpus):
    edits, tasks, gt = corpus
    lolo = EV.leave_one_lineage_out(edits, tasks, gt, gt.old_traces, alpha=0.05)
    assert not lolo.leakage_detected
    # every lineage's train/test edit sets are disjoint (the no-leakage guard)
    for lin, info in lolo.per_lineage.items():
        assert not (set(info["train_ids"]) & set(info["test_ids"]))
    assert set(lolo.per_lineage) == set(lineages())
    # held-out recall is finite and beats random at a small budget (OOD signal)
    rnd = EV.random_recall_at_budgets(edits, tasks, gt, n_seeds=8)
    assert lolo.held_out_recall[2] > rnd[2]


# --------------------------------------------------------------------------
# Sequential policy: REJECT dangerous, ACCEPT safe
# --------------------------------------------------------------------------
def test_policy_rejects_dangerous_accepts_safe(corpus, model):
    edits, tasks, gt = corpus
    cust = Custodian(gt)
    sel = HarnessGuardSelector(model, gt.old_traces)
    policy = SequentialPolicy(accept_tol=0.30, max_budget=12)

    dangerous = get_edit("e_retry_drop")
    assert gt.is_dangerous(dangerous.edit_id)
    d = policy.decide(dangerous, sel, tasks, cust.run_canary)
    assert d.decision == "REJECT"
    assert d.n_regressions >= 1

    safe = get_edit("e_retry_neutral")
    assert not gt.is_dangerous(safe.edit_id)
    s = policy.decide(safe, sel, tasks, cust.run_canary)
    assert s.decision == "ACCEPT"
    assert s.n_regressions == 0
    assert s.upper_bound <= 0.30


def test_false_safe_curve_controls_dangerous_acceptance(corpus, model):
    edits, tasks, gt = corpus
    cust = Custodian(gt)
    sel = HarnessGuardSelector(model, gt.old_traces)
    curve = EV.false_safe_curve(edits, tasks, gt, sel, cust)
    assert curve[0].n_dangerous >= 5
    # the selector finds the planted regressions, so no dangerous edit is
    # falsely accepted at any tolerance; coverage is monotone non-decreasing
    covs = [p.coverage for p in curve]
    assert covs == sorted(covs)
    for p in curve:
        assert p.false_safe == 0.0


# --------------------------------------------------------------------------
# Statistics unit = EDIT
# --------------------------------------------------------------------------
def test_bootstrap_is_over_edits_not_task_runs(corpus, model):
    edits, tasks, gt = corpus
    hg = EV.harnessguard_select_fn(model, gt.old_traces, tasks)
    rec = EV.per_edit_recall(hg, edits, tasks, gt, 2)
    ci, n_clusters = EV.bootstrap_recall_over_edits(rec, n_boot=500, seed=0)
    # the bootstrap unit count equals the number of EDITS (with regressions),
    # NOT the number of edit x task run pairs
    assert n_clusters == len(gt.edits_with_regression())
    assert n_clusters < len(edits) * len(tasks)
    assert 0.0 <= ci.lo <= ci.point <= ci.hi <= 1.0


def test_pair_risk_model_learns_separable_signal():
    # sanity: the from-scratch logistic actually fits a separable signal
    X = np.array([[0.0], [0.1], [0.9], [1.0]])
    y = np.array([0.0, 0.0, 1.0, 1.0])
    m = PairRiskModel(n_iter=500).fit(X, y)
    p = m.predict_proba(X)
    assert p[0] < 0.5 < p[-1]


# --------------------------------------------------------------------------
# Sealed custodian gate
# --------------------------------------------------------------------------
def test_sealed_custodian_blocks_pre_freeze_label_read(corpus):
    _, _, gt = corpus
    cust = Custodian(gt)
    root = tempfile.mkdtemp()
    st = cust.seal(root)
    with pytest.raises(SealedAccessError):
        st.get_labels("test_edits", role="builder")
    labels = st.get_labels("test_edits", role="test_custodian")
    assert len(labels["matrix"]) == len(gt.edit_ids)


def test_harness_config_hash_stable():
    a = default_harness()
    b = HarnessConfig()
    assert a.harness_hash() == b.harness_hash()
    assert a.with_changes(retry_count=9).harness_hash() != a.harness_hash()
    with pytest.raises(ValueError):
        a.with_changes(nonexistent_field=1)
