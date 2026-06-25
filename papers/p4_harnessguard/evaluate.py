"""H2 evaluation: recall@budget, risk-coverage, OOD selector generalization.

Everything here resamples the true independent unit = the EDIT (manual 8.15:
"bootstrap over edits, never treat task runs as independent edit samples").

Provides:
- per_edit_recall / recall_at_budgets for {random, difficulty, edit-conditioned}
- paired edit-bootstrap CI for selector - random recall difference (H2)
- false_safe / risk-coverage curve over the sequential policy
- leave_one_lineage_out selector generalization (no leakage)
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from core.statistics.resampling import (
    Interval, cluster_bootstrap, paired_cluster_bootstrap_diff)
from core.util import stable_seed
from papers.p4_harnessguard.selector import (
    HarnessGuardSelector, SequentialPolicy, select_difficulty, select_random,
    train_risk_model)
from papers.p4_harnessguard.task_suite import trajectory_length_baseline

DEFAULT_BUDGETS = (1, 2, 4, 8, "full")


def _k(k, n_tasks):
    return n_tasks if k == "full" else int(k)


# --------------------------------------------------------------------------
# Selector builders -> select(edit, k) -> ordered task_ids
# --------------------------------------------------------------------------
def random_select_fn(task_ids, *, seed=0):
    return lambda edit, k: select_random(task_ids, k,
                                          seed=stable_seed(edit.edit_id, seed))


def difficulty_select_fn(tasks):
    diff = {t.task_id: trajectory_length_baseline(t) for t in tasks}
    return lambda edit, k: select_difficulty(diff, k)


def harnessguard_select_fn(model, old_traces, tasks, *, alpha=0.05):
    sel = HarnessGuardSelector(model, old_traces, alpha=alpha)
    return lambda edit, k: sel.select(edit, tasks, k)


# --------------------------------------------------------------------------
# Recall@budget
# --------------------------------------------------------------------------
def per_edit_recall(select_fn, edits, tasks, gt, k) -> dict:
    """recall = |selected ∩ regression_set| / |regression_set| per edit (only
    edits that have >=1 regression)."""
    kk = _k(k, len(tasks))
    out = {}
    for e in edits:
        G = gt.regression_set(e.edit_id)
        if not G:
            continue
        sel = set(select_fn(e, kk))
        out[e.edit_id] = len(sel & G) / len(G)
    return out


def recall_at_budgets(select_fn, edits, tasks, gt, budgets=DEFAULT_BUDGETS) -> dict:
    out = {}
    for k in budgets:
        vals = list(per_edit_recall(select_fn, edits, tasks, gt, k).values())
        out[k] = float(np.mean(vals)) if vals else float("nan")
    return out


def random_recall_at_budgets(edits, tasks, gt, budgets=DEFAULT_BUDGETS,
                             *, n_seeds=16) -> dict:
    """Average random recall over seeds for a stable estimate."""
    task_ids = [t.task_id for t in tasks]
    acc = {k: [] for k in budgets}
    for s in range(n_seeds):
        sf = random_select_fn(task_ids, seed=1000 + s)
        r = recall_at_budgets(sf, edits, tasks, gt, budgets)
        for k in budgets:
            acc[k].append(r[k])
    return {k: float(np.nanmean(v)) for k, v in acc.items()}


@dataclass
class H2Result:
    random: dict
    difficulty: dict
    harnessguard: dict


def run_h2_evaluation(edits, tasks, gt, old_traces, *, budgets=DEFAULT_BUDGETS,
                      alpha=0.05, n_random_seeds=16, model=None) -> H2Result:
    if model is None:
        model = train_risk_model(edits, tasks, gt, old_traces)
    hg = harnessguard_select_fn(model, old_traces, tasks, alpha=alpha)
    return H2Result(
        random=random_recall_at_budgets(edits, tasks, gt, budgets, n_seeds=n_random_seeds),
        difficulty=recall_at_budgets(difficulty_select_fn(tasks), edits, tasks, gt, budgets),
        harnessguard=recall_at_budgets(hg, edits, tasks, gt, budgets),
    )


# --------------------------------------------------------------------------
# Edit-level bootstrap (the unit of analysis)
# --------------------------------------------------------------------------
def bootstrap_recall_over_edits(recall_by_edit: dict, *, n_boot=2000, seed=0,
                                conf=0.95) -> tuple[Interval, int]:
    """Bootstrap mean recall by resampling EDITS. Returns (Interval, n_edits)."""
    ids = sorted(recall_by_edit)
    vals = [recall_by_edit[i] for i in ids]
    ci = cluster_bootstrap(vals, ids, n_boot=n_boot, conf=conf, seed=seed)
    return ci, len(ids)


def paired_selector_advantage(select_a, select_b, edits, tasks, gt, k, *,
                              n_boot=2000, seed=0, conf=0.95):
    """Edit-clustered paired bootstrap CI for mean(recall_b - recall_a) at
    budget k (e.g. a=random, b=harnessguard). Positive => b beats a."""
    ra = per_edit_recall(select_a, edits, tasks, gt, k)
    rb = per_edit_recall(select_b, edits, tasks, gt, k)
    ids = sorted(set(ra) & set(rb))
    a = [ra[i] for i in ids]
    b = [rb[i] for i in ids]
    ci = paired_cluster_bootstrap_diff(a, b, ids, n_boot=n_boot, conf=conf, seed=seed)
    return ci, len(ids)


# --------------------------------------------------------------------------
# Risk-coverage / false-safe curve over the sequential policy
# --------------------------------------------------------------------------
@dataclass
class CurvePoint:
    accept_tol: float
    coverage: float       # fraction of edits auto-decided (not ESCALATE)
    false_safe: float     # fraction of DANGEROUS edits ACCEPTed
    n_dangerous: int


def false_safe_curve(edits, tasks, gt, selector, custodian, *,
                     tols=(0.15, 0.20, 0.30, 0.40, 0.55), max_budget=12) -> list[CurvePoint]:
    dangerous = [e for e in edits if gt.is_dangerous(e.edit_id)]
    points = []
    for tol in tols:
        policy = SequentialPolicy(accept_tol=tol, max_budget=max_budget)
        decided = 0
        false_safe = 0
        for e in edits:
            d = policy.decide(e, selector, tasks, custodian.run_canary)
            if d.decision != "ESCALATE":
                decided += 1
        for e in dangerous:
            d = policy.decide(e, selector, tasks, custodian.run_canary)
            if d.decision == "ACCEPT":
                false_safe += 1
        points.append(CurvePoint(
            accept_tol=tol, coverage=decided / len(edits),
            false_safe=(false_safe / len(dangerous)) if dangerous else 0.0,
            n_dangerous=len(dangerous)))
    return points


# --------------------------------------------------------------------------
# Leave-one-edit-lineage-out generalization of the SELECTOR (no leakage)
# --------------------------------------------------------------------------
@dataclass
class LOLOResult:
    per_lineage: dict           # lineage -> {recall, n_test_edits}
    held_out_recall: dict       # budget -> mean recall over all held-out edits
    leakage_detected: bool


def leave_one_lineage_out(edits, tasks, gt, old_traces, *, budgets=DEFAULT_BUDGETS,
                          alpha=0.05) -> LOLOResult:
    lineages = []
    for e in edits:
        if e.lineage not in lineages:
            lineages.append(e.lineage)

    per_lineage = {}
    pooled = {k: [] for k in budgets}
    leakage = False
    for lin in lineages:
        train = [e for e in edits if e.lineage != lin]
        test = [e for e in edits if e.lineage == lin]
        train_ids = {e.edit_id for e in train}
        test_ids = {e.edit_id for e in test}
        if train_ids & test_ids:           # split sanity
            leakage = True
        model = train_risk_model(train, tasks, gt, old_traces)
        hg = harnessguard_select_fn(model, old_traces, tasks, alpha=alpha)
        rec = recall_at_budgets(hg, test, tasks, gt, budgets)
        test_with_reg = [e.edit_id for e in test if gt.n_regressions(e.edit_id) >= 1]
        per_lineage[lin] = {"recall": rec, "n_test_edits": len(test_with_reg),
                            "train_ids": sorted(train_ids), "test_ids": sorted(test_ids)}
        for k in budgets:
            pr = per_edit_recall(hg, test, tasks, gt, k)
            pooled[k].extend(pr.values())
    held = {k: (float(np.mean(v)) if v else float("nan")) for k, v in pooled.items()}
    return LOLOResult(per_lineage=per_lineage, held_out_recall=held,
                      leakage_detected=leakage)
