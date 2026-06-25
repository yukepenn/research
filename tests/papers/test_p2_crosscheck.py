"""P2 CrossCheck Tier-0 tests.

Covers the deterministic, LLM-free core: defect taxonomy, mutation injectors
(each hidden test passes clean / fails mutated), detection & repair schemas,
budget-matching accounting, defect-conditioned author x reviewer complementarity
recovery, and the held-out-repository ReviewRoute router (nested CV, outer fold =
repository, no leakage). The planted-signal generators in ``sim_outcomes`` are
PIPELINE VALIDATION, not scientific results.
"""
import numpy as np
import pytest

from core.adapters.base import Message, Usage
from core.adapters.mock import DeterministicMockAdapter

from papers.p2_crosscheck import complementarity as comp
from papers.p2_crosscheck import router as R
from papers.p2_crosscheck.budget import (
    REVIEW_CONDITIONS, WorkflowCondition, WorkflowCost, author_more_compute_cost,
    budget_match, combine, review_workflow_cost)
from papers.p2_crosscheck.defects.taxonomy import (
    ALL_DEFECTS, DefectType, all_defect_values, defect_index, spec)
from papers.p2_crosscheck.mutations.injectors import (
    all_cases, clean_passes, mutation_fails, repositories, run_case_in_dir)
from papers.p2_crosscheck.review_protocols.schemas import (
    DetectionVerdict, Finding, RepairProposal, validate_repair, validate_verdict)
from papers.p2_crosscheck.sim_outcomes import (
    PLANTED_CELL, generate_complementarity_table, generate_router_dataset)


# ==========================================================================
# 1. Defect taxonomy
# ==========================================================================
def test_taxonomy_has_at_least_eight_categories():
    assert len(ALL_DEFECTS) >= 8
    vals = all_defect_values()
    assert len(vals) == len(set(vals))            # unique values
    for required in ("boundary", "api_misuse", "cross_file_inconsistency",
                     "state_order", "exception_omission", "type_serialization",
                     "requirement_misread", "collateral_regression",
                     "missing_test", "perf"):
        assert required in vals
    # str(enum) is the bare value (JSON-friendly)
    assert str(DefectType.BOUNDARY) == "boundary"
    assert spec(DefectType.TYPE_SERIALIZATION).touches_serialization is True
    assert set(defect_index().values()) == set(range(len(vals)))


# ==========================================================================
# 2. Mutation injectors: clean passes, mutated fails its hidden test
# ==========================================================================
def test_at_least_six_distinct_defect_triples():
    cases = all_cases()
    assert len(cases) >= 6
    assert len({c.defect for c in cases}) >= 6
    assert len(repositories()) >= 2          # repo-level lineage exists


def test_each_mutation_breaks_its_hidden_test_and_clean_passes():
    for case in all_cases():
        assert clean_passes(case), f"{case.case_id}: clean variant failed hidden test"
        assert mutation_fails(case), f"{case.case_id}: mutated variant did NOT fail"


def test_materialize_to_temp_dir_matches_inprocess(tmp_path):
    case = all_cases()[0]
    assert run_case_in_dir(case, str(tmp_path), "clean") is True
    assert run_case_in_dir(case, str(tmp_path), "mutated") is False


# ==========================================================================
# 3. Review protocol schemas
# ==========================================================================
def _good_verdict():
    return DetectionVerdict(
        verdict="defective",
        findings=[Finding(file="m.py", line=12,
                          defect_type=DefectType.BOUNDARY,
                          evidence="off-by-one at upper bound", confidence=0.8)],
        recommended_tests=["assert in_range(10,0,10)"],
        estimated_risk="medium").to_dict()


def test_verdict_schema_accepts_good_payload():
    assert validate_verdict(_good_verdict()) == []


@pytest.mark.parametrize("mutate", [
    lambda p: p.update({"verdict": "broken"}),                 # bad enum
    lambda p: p.pop("estimated_risk"),                         # missing required
    lambda p: p["findings"][0].update({"defect_type": "nope"}),   # bad defect enum
    lambda p: p["findings"][0].update({"confidence": 2.0}),    # out of range
    lambda p: p["findings"][0].pop("evidence"),               # missing finding field
    lambda p: p.update({"surprise": 1}),                      # additionalProperties
])
def test_verdict_schema_rejects_bad_payloads(mutate):
    payload = _good_verdict()
    mutate(payload)
    assert validate_verdict(payload), "schema should have rejected the payload"


def test_repair_schema_good_and_bad():
    good = RepairProposal(patch="--- a\n+++ b\n", rationale="fix boundary",
                          addressed_defect_types=[DefectType.BOUNDARY],
                          new_tests=["t"], estimated_risk="low").to_dict()
    assert validate_repair(good) == []
    assert validate_repair({"rationale": "no patch"})            # missing patch
    assert validate_repair({"patch": "p", "rationale": "r",
                            "addressed_defect_types": ["bogus"]})  # bad enum


# ==========================================================================
# 4. Budget-matching accounting
# ==========================================================================
def test_eight_workflow_conditions_and_review_set():
    assert len(list(WorkflowCondition)) == 8
    for c in ("no_review", "author_more_compute", "self_review",
              "same_family_fresh", "cross_family_review", "test_generation_only",
              "independent_reimplementation", "router"):
        assert c in {w.value for w in WorkflowCondition}
    assert WorkflowCondition.CROSS_FAMILY_REVIEW in REVIEW_CONDITIONS
    assert WorkflowCondition.AUTHOR_MORE_COMPUTE not in REVIEW_CONDITIONS


def test_author_extra_compute_is_budget_matched_to_cross_review():
    author = WorkflowCost(WorkflowCondition.NO_REVIEW, 1000, 200, 0.0120, 1.0)
    reviewer = WorkflowCost(WorkflowCondition.CROSS_FAMILY_REVIEW, 800, 150, 0.0096, 1.1)

    cross = review_workflow_cost(author, reviewer)
    amc = author_more_compute_cost(author, reviewer)

    # by construction the author-extra-compute arm matches the review arm
    m = budget_match(amc, cross)
    assert m.matched and m.token_matched and m.dollar_matched
    assert m.token_ratio < 1e-9 and m.dollar_ratio < 1e-9

    # the naive (unfair) comparison author-once vs author+reviewer is NOT matched
    assert budget_match(author, cross).matched is False
    assert budget_match(author, cross).token_matched is False


def test_budget_match_tolerance_and_dollar_fallback():
    a = WorkflowCost(WorkflowCondition.AUTHOR_MORE_COMPUTE, 2000, 150)  # 2150 tok
    b = WorkflowCost(WorkflowCondition.CROSS_FAMILY_REVIEW, 2050, 150)  # 2200 tok
    assert budget_match(a, b, rel_tol=0.05).token_matched     # ~2.3% apart
    assert not budget_match(a, b, rel_tol=0.01).token_matched
    # no pricing configured -> dollar_matched is None, "both" falls back to tokens
    m = budget_match(a, b, rel_tol=0.05)
    assert m.dollar_matched is None and m.matched is True


def test_combine_and_from_usage_integrates_with_mock_adapter():
    adapter = DeterministicMockAdapter("mock-author",
                                       cost_per_mtok_in=1.0, cost_per_mtok_out=2.0)
    resp = adapter.generate([Message("system", "s"), Message("user", "do it")])
    wc = WorkflowCost.from_usage(WorkflowCondition.NO_REVIEW, resp.usage)
    assert wc.total_tokens == resp.usage.input_tokens + resp.usage.output_tokens
    summed = combine(WorkflowCondition.CROSS_FAMILY_REVIEW, wc, wc)
    assert summed.total_tokens == 2 * wc.total_tokens


# ==========================================================================
# 5. Complementarity recovers a planted author x reviewer x defect interaction
# ==========================================================================
def test_complementarity_recovers_planted_interaction():
    table = generate_complementarity_table(n_per_cell=200, seed=0)
    a, r, d = PLANTED_CELL

    # detection is far above the reviewer's standalone strength on this defect
    detect = comp.detection_complementarity(table, a, r, d)
    strength = comp.reviewer_standalone_strength(table, r, d)
    assert detect > 0.85
    assert detect > strength + 0.2

    # the planted residual interaction is clearly positive and larger than a
    # non-planted cell for the SAME (author, reviewer) on another defect
    planted_resid = comp.residual_complementarity(table, a, r, d)
    other_resid = comp.residual_complementarity(table, a, r, "boundary")
    assert planted_resid > 0.10
    assert planted_resid > other_resid + 0.05


def test_same_vs_cross_error_correlation_and_matrices():
    table = generate_complementarity_table(n_per_cell=200, seed=0)
    ec = comp.same_vs_cross_error_correlation(table)
    # cross-family pairs miss fewer defects (complementary) than same-family ones
    assert ec.cross_family_miss_rate < ec.same_family_miss_rate
    assert ec.phi > 0.0          # same-family membership correlates with misses

    labels, cm = comp.defect_confusion(table)
    assert cm.shape == (len(labels), len(labels))
    ser = defect_index()["type_serialization"]
    assert cm[ser].sum() > 0
    assert int(np.argmax(cm[ser])) == ser   # detected serialization mostly labelled right

    rows, defects, rm = comp.review_induced_regression_matrix(table)
    assert rm.shape == (len(rows), len(defects))
    assert np.all((rm >= 0) & (rm <= 1))


def test_complementarity_is_deterministic():
    t1 = generate_complementarity_table(n_per_cell=120, seed=3)
    t2 = generate_complementarity_table(n_per_cell=120, seed=3)
    a, r, d = PLANTED_CELL
    assert (comp.residual_complementarity(t1, a, r, d)
            == comp.residual_complementarity(t2, a, r, d))


# ==========================================================================
# 6. ReviewRoute router: held-out repos, nested CV, no leakage
# ==========================================================================
def test_feature_extractor_is_label_free_and_repo_agnostic():
    assert R.uses_only_pre_review_features()
    base = {f: 1.0 for f in R.PRE_REVIEW_FEATURES}
    rec_a = dict(base, repo_id="repo_00", final_correct=1, defect_type="boundary")
    rec_b = dict(base, repo_id="repo_99", final_correct=0, defect_type="perf")
    # identical pre-review features -> identical vectors regardless of repo/labels
    assert np.array_equal(R.extract_features(rec_a), R.extract_features(rec_b))
    assert len(R.extract_features(rec_a)) == len(R.PRE_REVIEW_FEATURES)


def test_binary_logistic_handles_degenerate_labels():
    X = np.random.default_rng(0).normal(size=(20, 3))
    clf = R.BinaryLogistic().fit(X, np.ones(20))
    assert np.allclose(clf.predict_proba(X), clf.predict_proba(X)[0])
    assert clf.predict_proba(X)[0] > 0.9


def test_router_beats_baselines_on_heldout_repos_without_leakage():
    ds = generate_router_dataset(seed=0)          # 8 repos x 28 patches (scale later)
    res = R.nested_cv_by_repo(ds, seed=0)

    # OUTER fold = repository, and no repo appears in train and test together
    assert res.no_repo_leakage is True

    u = res.mean_utility
    # router beats always-cross, always-self, and random on held-out repos
    assert res.router_beats("always_cross", "always_self", "random", margin=0.02)
    # sanity: bounded above by the (label-using) oracle, above naive no-review
    assert u["router"] < u["oracle"]
    assert u["router"] > u["always_no_review"]


def test_outer_folds_partition_repositories_disjointly():
    ds = generate_router_dataset(seed=0)
    folds = R.group_folds(ds.repo_ids, k=4, seed=0)
    for tr, te, test_repos in folds:
        train_repos = set(ds.repo_ids[tr].tolist())
        assert train_repos.isdisjoint(set(test_repos))


def test_router_nested_cv_is_deterministic():
    ds = generate_router_dataset(seed=0)
    r1 = R.nested_cv_by_repo(ds, seed=0).mean_utility
    r2 = R.nested_cv_by_repo(ds, seed=0).mean_utility
    assert r1 == r2
