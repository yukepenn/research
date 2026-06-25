"""Canary risk model, diverse selector, and sequential policy (manual 8.11).

- PairRiskModel: a from-scratch numpy logistic regression predicting
  P(regression | edit, task, old-trace). Standardised features, full-batch
  gradient descent with L2, fully deterministic.
- diverse_canary_select: greedy budgeted-max-coverage / facility-location that
  balances predicted risk with capability/tool diversity (manual 8.11 Module 4).
- baselines: random k, historical-difficulty.
- SequentialPolicy: ACCEPT / REJECT / ESCALATE with a calibrated abstention
  threshold via Clopper-Pearson on observed canary regressions (Module 5/6).
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from core.statistics.resampling import clopper_pearson_ci
from core.util import rng_for
from papers.p4_harnessguard.feature_extraction import features as F


# --------------------------------------------------------------------------
# Pairwise regression-risk model (numpy logistic regression)
# --------------------------------------------------------------------------
class PairRiskModel:
    def __init__(self, *, l2: float = 1.0, lr: float = 0.3, n_iter: int = 800):
        self.l2 = l2
        self.lr = lr
        self.n_iter = n_iter
        self.w = None
        self.b = 0.0
        self.mu = None
        self.sd = None

    @staticmethod
    def _sigmoid(z):
        return 1.0 / (1.0 + np.exp(-np.clip(z, -30, 30)))

    def fit(self, X: np.ndarray, y: np.ndarray) -> "PairRiskModel":
        X = np.asarray(X, dtype=float)
        y = np.asarray(y, dtype=float)
        n, d = X.shape
        self.mu = X.mean(axis=0)
        sd = X.std(axis=0)
        sd[sd < 1e-9] = 1.0  # guard constant columns (e.g. unseen one-hots)
        self.sd = sd
        Xs = (X - self.mu) / self.sd
        w = np.zeros(d)
        b = 0.0
        for _ in range(self.n_iter):
            p = self._sigmoid(Xs @ w + b)
            err = p - y
            grad_w = Xs.T @ err / n + self.l2 * w / n
            grad_b = float(err.mean())
            w -= self.lr * grad_w
            b -= self.lr * grad_b
        self.w = w
        self.b = b
        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        X = np.asarray(X, dtype=float)
        Xs = (X - self.mu) / self.sd
        return self._sigmoid(Xs @ self.w + self.b)


# --------------------------------------------------------------------------
# Diverse canary selector (greedy facility-location / budgeted max coverage)
# --------------------------------------------------------------------------
def diverse_canary_select(risk: dict, capabilities_by_task: dict, k: int,
                          *, alpha: float = 0.05) -> list[str]:
    """Greedily pick up to k tasks maximising predicted risk + alpha * NEW
    capability coverage. Returns an ORDERED list (selection order)."""
    remaining = list(risk.keys())
    selected: list[str] = []
    covered: set = set()
    while remaining and len(selected) < k:
        best = None
        best_key = None
        for t in remaining:
            new_caps = set(capabilities_by_task.get(t, [])) - covered
            gain = float(risk[t]) + alpha * len(new_caps)
            # deterministic tie-break: gain, then risk, then task_id asc
            key = (gain, float(risk[t]), [-ord(c) for c in t])
            if best_key is None or key > best_key:
                best_key, best = key, t
        selected.append(best)
        covered |= set(capabilities_by_task.get(best, []))
        remaining.remove(best)
    return selected


def select_random(task_ids, k: int, *, seed: int = 0) -> list[str]:
    rng = rng_for("p4_random_canary", seed)
    pool = list(task_ids)
    rng.shuffle(pool)
    return pool[:k]


def select_difficulty(difficulty_by_task: dict, k: int) -> list[str]:
    """Historical-difficulty baseline: pick the longest-trajectory tasks."""
    order = sorted(difficulty_by_task.items(), key=lambda kv: (-kv[1], kv[0]))
    return [tid for tid, _ in order[:k]]


# --------------------------------------------------------------------------
# HarnessGuard selector: model -> per-task risk -> diverse selection
# --------------------------------------------------------------------------
class HarnessGuardSelector:
    def __init__(self, model: PairRiskModel, old_traces: dict, *, alpha: float = 0.05):
        self.model = model
        self.old_traces = old_traces
        self.alpha = alpha

    def task_risks(self, edit, tasks) -> dict:
        rows = [F.pair_vector(edit, t, self.old_traces[(edit.edit_id, t.task_id)])
                for t in tasks]
        X = np.vstack(rows)
        p = self.model.predict_proba(X)
        return {t.task_id: float(p[i]) for i, t in enumerate(tasks)}

    def select(self, edit, tasks, k: int) -> list[str]:
        risk = self.task_risks(edit, tasks)
        caps = {t.task_id: list(t.capabilities) for t in tasks}
        return diverse_canary_select(risk, caps, k, alpha=self.alpha)


def train_risk_model(train_edits, tasks, gt, old_traces, **model_kw) -> PairRiskModel:
    """Fit the pair risk model on the given TRAIN edits only (no held-out edit
    labels). `gt` provides regression labels; `old_traces` the feature source."""
    X, index = F.build_matrix(train_edits, tasks, old_traces)
    y = np.array([gt.regression_row(eid)[gt.task_ids.index(tid)]
                  for (eid, tid) in index], dtype=float)
    return PairRiskModel(**model_kw).fit(X, y)


# --------------------------------------------------------------------------
# Sequential ACCEPT / REJECT / ESCALATE policy
# --------------------------------------------------------------------------
@dataclass
class PolicyDecision:
    decision: str           # ACCEPT | REJECT | ESCALATE
    n_canaries: int
    n_regressions: int
    upper_bound: float      # CP upper bound on regression rate when 0 observed
    selected: list


class SequentialPolicy:
    """Run selected canaries; decide.

    - >=1 observed pass->fail regression  -> REJECT (a real regression exists).
    - 0 regressions and CP-upper(regression rate) <= accept_tol -> ACCEPT.
    - otherwise -> ESCALATE (insufficient evidence, run more / full suite).

    accept_tol is the calibrated abstention threshold (tune on validation edits;
    here it is a frozen constant honouring the false-safe budget). The bound is
    an empirical/statistical risk bound, NOT a claim of absolute safety.
    """

    def __init__(self, *, accept_tol: float = 0.30, max_budget: int = 12,
                 conf: float = 0.95):
        self.accept_tol = accept_tol
        self.max_budget = max_budget
        self.conf = conf

    def decide(self, edit, selector: HarnessGuardSelector, tasks,
               run_canary) -> PolicyDecision:
        budget = min(self.max_budget, len(tasks))
        ordered = selector.select(edit, tasks, budget)
        n = 0
        regs = 0
        for tid in ordered:
            r = int(run_canary(edit.edit_id, tid))
            n += 1
            regs += r
            if regs >= 1:
                return PolicyDecision("REJECT", n, regs, float("nan"), ordered[:n])
        ub = clopper_pearson_ci(0, n, self.conf).hi if n > 0 else 1.0
        if ub <= self.accept_tol:
            return PolicyDecision("ACCEPT", n, 0, float(ub), ordered)
        return PolicyDecision("ESCALATE", n, 0, float(ub), ordered)


def calibrate_accept_tol(n_canaries: int, *, target_false_safe: float = 0.30,
                         conf: float = 0.95) -> float:
    """Smallest accept tolerance achievable (CP upper bound for 0/n) given a
    canary budget; used to document the budget needed for a false-safe target."""
    ub = clopper_pearson_ci(0, max(1, n_canaries), conf).hi
    return float(max(ub, target_false_safe))
