"""SIMULATED author/reviewer outcome generators -- PIPELINE VALIDATION ONLY.

NOT SCIENTIFIC RESULTS. These deterministic, seeded generators plant a KNOWN
signal so the Tier-0 harness can be checked end to end:

  * ``generate_complementarity_table`` plants an author x reviewer x defect
    interaction (a specific cross-family pair is far better on one defect than
    the reviewer's standalone strength) so ``complementarity.py`` can be shown to
    recover it beyond the reviewer main effect (H3 mechanism check).

  * ``generate_router_dataset`` plants a feature -> best-action signal that is a
    function of pre-review features only (never the repo id), so ``router.py``
    trained on TRAIN repositories can be shown to beat always-cross / always-self
    / random on HELD-OUT repositories with no repo leakage (H5 plumbing check).

Every number produced here is a harness self-test, never a finding.
"""
from __future__ import annotations

import numpy as np

from core.util import rng_for
from papers.p2_crosscheck.budget import WorkflowCondition
from papers.p2_crosscheck.defects.taxonomy import DefectType
from papers.p2_crosscheck.router import PRE_REVIEW_FEATURES, RouterDataset, extract_features

# ==========================================================================
# 1. Complementarity table with a planted author x reviewer x defect signal
# ==========================================================================
# Two authors and two reviewers spanning two model "families".
_AUTHORS = [("A_fam1", "fam1"), ("A_fam2", "fam2")]
_REVIEWERS = [("R_fam1", "fam1"), ("R_fam2", "fam2")]
# Reviewer standalone strength is a clean MAIN EFFECT (constant across defects).
_STRENGTH = {"R_fam1": 0.50, "R_fam2": 0.55}
# Defects used in the table; serialization carries the planted interaction.
_COMP_DEFECTS = [
    DefectType.TYPE_SERIALIZATION,   # PLANTED cell lives here
    DefectType.BOUNDARY,
    DefectType.STATE_ORDER,
]
# The planted pair-specific complementarity: cross-family A_fam1 x R_fam2 is a
# near-perfect detector on serialization, far above R_fam2's strength (0.55).
PLANTED_CELL = ("A_fam1", "R_fam2", DefectType.TYPE_SERIALIZATION.value)
_PLANTED_P = 0.95
_SAME_FAMILY_PENALTY = 0.15   # shared blind spots
_CROSS_FAMILY_BONUS = 0.10    # mild generic cross-review benefit
# A confusable defect the reviewer sometimes mislabels detected defects as.
_CONFUSABLE = {
    DefectType.TYPE_SERIALIZATION.value: DefectType.API_MISUSE.value,
    DefectType.BOUNDARY.value: DefectType.MISSING_TEST.value,
    DefectType.STATE_ORDER.value: DefectType.EXCEPTION_OMISSION.value,
}


def _detect_prob(author, author_fam, reviewer, reviewer_fam, defect_val) -> float:
    if (author, reviewer, defect_val) == PLANTED_CELL:
        return _PLANTED_P
    base = _STRENGTH[reviewer]
    if author_fam == reviewer_fam:
        return max(0.0, base - _SAME_FAMILY_PENALTY)
    return min(1.0, base + _CROSS_FAMILY_BONUS)


def generate_complementarity_table(*, n_per_cell: int = 200, seed: int = 0) -> list[dict]:
    """One row per (author, reviewer, defect, replicate). All rows are produced
    near-misses (author_produced_defect=True) so detection complementarity is
    well defined. Deterministic given ``seed``."""
    rows: list[dict] = []
    for author, a_fam in _AUTHORS:
        for reviewer, r_fam in _REVIEWERS:
            for defect in _COMP_DEFECTS:
                d = defect.value
                p = _detect_prob(author, a_fam, reviewer, r_fam, d)
                reg_rate = 0.10 if reviewer == "R_fam2" else 0.05
                for i in range(n_per_cell):
                    rng = rng_for("p2_comp", seed, author, reviewer, d, i)
                    detected = rng.random() < p
                    if detected:
                        claimed = d if rng.random() < 0.9 else _CONFUSABLE[d]
                    else:
                        claimed = None
                    regression = rng.random() < reg_rate
                    rows.append({
                        "author": author,
                        "author_family": a_fam,
                        "reviewer": reviewer,
                        "reviewer_family": r_fam,
                        "same_family": a_fam == r_fam,
                        "defect_type": d,
                        "author_produced_defect": True,
                        "reviewer_detected": bool(detected),
                        "reviewer_claimed_defect": claimed,
                        "review_induced_regression": bool(regression),
                    })
    return rows


# ==========================================================================
# 2. Router dataset with a planted feature -> best-action signal
# ==========================================================================
# Router action space (the core review conditions; ROUTER itself is not an arm).
ROUTER_ACTIONS = [
    WorkflowCondition.NO_REVIEW,
    WorkflowCondition.SELF_REVIEW,
    WorkflowCondition.SAME_FAMILY_FRESH,
    WorkflowCondition.TEST_GENERATION_ONLY,
    WorkflowCondition.CROSS_FAMILY_REVIEW,
]
_A = {c: i for i, c in enumerate(ROUTER_ACTIONS)}

# Relative compute cost per action (no_review cheapest, cross-review priciest).
_COST = {
    WorkflowCondition.NO_REVIEW: 1.0,
    WorkflowCondition.SELF_REVIEW: 2.0,
    WorkflowCondition.SAME_FAMILY_FRESH: 3.0,
    WorkflowCondition.TEST_GENERATION_ONLY: 3.0,
    WorkflowCondition.CROSS_FAMILY_REVIEW: 4.0,
}

# Latent category -> P(final_correct) per action. Hand-designed so the
# utility-maximising action differs by category (given lambda_cost=0.05):
#   trivial        -> NO_REVIEW           (already correct, save compute)
#   serialization  -> CROSS_FAMILY_REVIEW (only cross-family catches it)
#   api            -> CROSS_FAMILY_REVIEW
#   state          -> TEST_GENERATION_ONLY (tests catch it cheaper than cross)
_CORRECT = {
    "trivial":       {WorkflowCondition.NO_REVIEW: 0.97, WorkflowCondition.SELF_REVIEW: 0.97,
                      WorkflowCondition.SAME_FAMILY_FRESH: 0.97,
                      WorkflowCondition.TEST_GENERATION_ONLY: 0.97,
                      WorkflowCondition.CROSS_FAMILY_REVIEW: 0.98},
    "serialization": {WorkflowCondition.NO_REVIEW: 0.30, WorkflowCondition.SELF_REVIEW: 0.35,
                      WorkflowCondition.SAME_FAMILY_FRESH: 0.45,
                      WorkflowCondition.TEST_GENERATION_ONLY: 0.55,
                      WorkflowCondition.CROSS_FAMILY_REVIEW: 0.92},
    "api":           {WorkflowCondition.NO_REVIEW: 0.35, WorkflowCondition.SELF_REVIEW: 0.45,
                      WorkflowCondition.SAME_FAMILY_FRESH: 0.55,
                      WorkflowCondition.TEST_GENERATION_ONLY: 0.60,
                      WorkflowCondition.CROSS_FAMILY_REVIEW: 0.90},
    "state":         {WorkflowCondition.NO_REVIEW: 0.40, WorkflowCondition.SELF_REVIEW: 0.55,
                      WorkflowCondition.SAME_FAMILY_FRESH: 0.65,
                      WorkflowCondition.TEST_GENERATION_ONLY: 0.88,
                      WorkflowCondition.CROSS_FAMILY_REVIEW: 0.85},
}
_CATEGORIES = ["trivial", "serialization", "api", "state"]
_CAT_WEIGHTS = [0.34, 0.22, 0.22, 0.22]


def _features_for_category(cat: str, rng) -> dict:
    """Build a pre-review feature record consistent with a latent category,
    plus genuine noise features so routing is a real learning problem."""
    ser = 1 if cat == "serialization" else 0
    api = 1 if cat == "api" else 0
    state = 1 if cat == "state" else 0
    if cat == "trivial":
        diff = rng.randint(3, 25)
        n_files = 1
        span = 1
    else:
        diff = rng.randint(40, 400)
        n_files = rng.randint(2, 6)
        span = rng.randint(1, 4)
    return {
        "diff_size": float(diff),
        "n_files": float(n_files),
        "module_span": float(span),
        "touches_api": float(api),
        "touches_state": float(state),
        "touches_serialization": float(ser),
        "visible_test_count": float(rng.randint(0, 12)),
        "visible_test_failures": float(rng.randint(0, 3)),
        "author_family_code": float(rng.randint(0, 1)),
        "n_retries": float(rng.randint(0, 5)),         # noise
        "n_exceptions": float(rng.randint(0, 4)),      # noise
        "author_confidence": round(rng.random(), 3),   # noise
    }


def generate_router_dataset(
    *,
    n_repos: int = 8,
    tasks_per_repo: int = 28,
    lam_cost: float = 0.05,
    lam_latency: float = 0.0,
    seed: int = 0,
) -> RouterDataset:
    """Generate a repo-structured dataset of pre-review features + per-action
    realized outcomes. The best action is a deterministic function of FEATURES
    (via the latent category), not of the repo id -> the signal transfers to
    held-out repositories. Deterministic given ``seed``."""
    records: list[dict] = []
    repo_ids: list[str] = []
    correct_rows: list[list[float]] = []
    cost_rows: list[list[float]] = []
    lat_rows: list[list[float]] = []

    for r in range(n_repos):
        repo_id = f"repo_{r:02d}"
        for t in range(tasks_per_repo):
            rng = rng_for("p2_router", seed, repo_id, t)
            cat = rng.choices(_CATEGORIES, weights=_CAT_WEIGHTS, k=1)[0]
            feats = _features_for_category(cat, rng)
            records.append(feats)
            repo_ids.append(repo_id)

            crow, krow, lrow = [], [], []
            for action in ROUTER_ACTIONS:
                p = _CORRECT[cat][action]
                arng = rng_for("p2_router_out", seed, repo_id, t, action.value)
                correct = 1.0 if arng.random() < p else 0.0
                # cost/latency are deterministic per action (+ tiny jitter)
                base_cost = _COST[action]
                jitter = 1.0 + 0.05 * (arng.random() - 0.5)
                crow.append(base_cost * jitter)
                krow.append(base_cost * jitter)  # latency tracks cost in this sim
                lrow.append(correct)
            correct_rows.append(lrow)
            cost_rows.append(crow)
            lat_rows.append(krow)

    X = np.vstack([extract_features(rec) for rec in records])
    return RouterDataset(
        records=records,
        repo_ids=np.array(repo_ids),
        X=X,
        correct=np.array(correct_rows, dtype=float),
        cost=np.array(cost_rows, dtype=float),
        latency=np.array(lat_rows, dtype=float),
        actions=list(ROUTER_ACTIONS),
        lam_cost=lam_cost,
        lam_latency=lam_latency,
    )
