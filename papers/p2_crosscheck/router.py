"""ReviewRoute: a pre-call, held-out-repository review router (manual 6.10; H5).

Three pieces, kept deliberately simple (manual 6.10: "prove a simple router
transfers before reaching for deep models"):

1. A PRE-REVIEW feature extractor. It may only read information available BEFORE
   any reviewer is called -- issue/diff/test/author-trajectory signals. It must
   NOT read hidden tests, gold labels, realized outcomes, or the repository id
   (those would leak). ``FORBIDDEN_KEYS`` documents the ban and
   ``extract_features`` simply never touches them.

2. An interpretable multinomial logistic-regression policy (softmax) implemented
   in numpy. Standardisation statistics are fit on TRAIN folds only.

3. A nested cross-validation harness whose OUTER split is BY REPOSITORY (whole
   repos held out -> no repo leakage), with an inner repo-grouped CV to pick the
   L2 strength. Policies are scored by

        U = P(final_correct) - lambda_cost * cost - lambda_latency * latency

   and the router is compared against always-cross, always-self, random, and an
   (oracle, label-using) upper bound.
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field

import numpy as np

from papers.p2_crosscheck.budget import WorkflowCondition

# Ordered list of the pre-review features the router is allowed to use.
PRE_REVIEW_FEATURES = [
    "diff_size",
    "n_files",
    "module_span",
    "touches_api",
    "touches_state",
    "touches_serialization",
    "visible_test_count",
    "visible_test_failures",
    "author_family_code",
    "n_retries",
    "n_exceptions",
    "author_confidence",
]

# Keys the extractor must never look at (label / outcome / identity leakage).
FORBIDDEN_KEYS = frozenset({
    "repo_id", "task_id", "category", "best_action",
    "final_correct", "correct", "cost", "latency", "outcomes",
    "author_produced_defect", "reviewer_detected", "defect_type",
    "hidden_test", "gold",
})


def uses_only_pre_review_features() -> bool:
    """Static guard: the feature set is disjoint from the forbidden/label set."""
    return set(PRE_REVIEW_FEATURES).isdisjoint(FORBIDDEN_KEYS)


def extract_features(record: dict) -> np.ndarray:
    """Map a pre-review patch record to a feature vector (label-free)."""
    return np.array([float(record[name]) for name in PRE_REVIEW_FEATURES],
                    dtype=float)


def feature_matrix(records) -> np.ndarray:
    return np.vstack([extract_features(r) for r in records]) if records else np.empty((0, len(PRE_REVIEW_FEATURES)))


# --------------------------------------------------------------------------
# Interpretable softmax (multinomial logistic) regression in numpy
# --------------------------------------------------------------------------
class SoftmaxRegression:
    def __init__(self, n_classes: int, *, l2: float = 1e-2, lr: float = 0.5,
                 n_iter: int = 400, seed: int = 0):
        self.n_classes = n_classes
        self.l2 = l2
        self.lr = lr
        self.n_iter = n_iter
        self.seed = seed
        self.W: np.ndarray | None = None      # (d+1, K) incl. bias row
        self.mean_: np.ndarray | None = None
        self.std_: np.ndarray | None = None

    def _standardize(self, X: np.ndarray) -> np.ndarray:
        Xs = (X - self.mean_) / self.std_
        return np.hstack([np.ones((Xs.shape[0], 1)), Xs])

    @staticmethod
    def _softmax(Z: np.ndarray) -> np.ndarray:
        Z = Z - Z.max(axis=1, keepdims=True)
        E = np.exp(Z)
        return E / E.sum(axis=1, keepdims=True)

    def fit(self, X: np.ndarray, y: np.ndarray) -> "SoftmaxRegression":
        X = np.asarray(X, dtype=float)
        y = np.asarray(y, dtype=int)
        self.mean_ = X.mean(axis=0)
        std = X.std(axis=0)
        std[std == 0] = 1.0
        self.std_ = std
        Xb = self._standardize(X)
        n, d = Xb.shape
        K = self.n_classes
        rng = np.random.default_rng(self.seed)
        self.W = rng.normal(0.0, 0.01, size=(d, K))
        Y = np.zeros((n, K))
        Y[np.arange(n), y] = 1.0
        for _ in range(self.n_iter):
            P = self._softmax(Xb @ self.W)
            grad = Xb.T @ (P - Y) / n
            reg = self.l2 * self.W
            reg[0, :] = 0.0   # do not regularise the bias row
            self.W -= self.lr * (grad + reg)
        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        Xb = self._standardize(np.asarray(X, dtype=float))
        return self._softmax(Xb @ self.W)

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.predict_proba(X).argmax(axis=1)

    def feature_importance(self) -> dict:
        """Mean |weight| per feature across classes (interpretability)."""
        imp = np.abs(self.W[1:, :]).mean(axis=1)
        return {name: float(v) for name, v in zip(PRE_REVIEW_FEATURES, imp)}


class BinaryLogistic:
    """Interpretable binary logistic regression (numpy GD, standardised, L2)."""

    def __init__(self, *, l2: float = 1e-2, lr: float = 0.5, n_iter: int = 400,
                 seed: int = 0):
        self.l2 = l2
        self.lr = lr
        self.n_iter = n_iter
        self.seed = seed
        self.w: np.ndarray | None = None
        self.mean_: np.ndarray | None = None
        self.std_: np.ndarray | None = None
        self._const: float | None = None   # set if y is single-valued

    def _standardize(self, X: np.ndarray) -> np.ndarray:
        Xs = (X - self.mean_) / self.std_
        return np.hstack([np.ones((Xs.shape[0], 1)), Xs])

    def fit(self, X: np.ndarray, y: np.ndarray) -> "BinaryLogistic":
        X = np.asarray(X, dtype=float)
        y = np.asarray(y, dtype=float)
        self.mean_ = X.mean(axis=0)
        std = X.std(axis=0)
        std[std == 0] = 1.0
        self.std_ = std
        # degenerate label column -> predict the (clamped) base rate constantly
        if y.min() == y.max():
            self._const = float(np.clip(y.mean(), 1e-4, 1 - 1e-4))
            return self
        Xb = self._standardize(X)
        n, d = Xb.shape
        rng = np.random.default_rng(self.seed)
        self.w = rng.normal(0.0, 0.01, size=d)
        for _ in range(self.n_iter):
            p = 1.0 / (1.0 + np.exp(-(Xb @ self.w)))
            grad = Xb.T @ (p - y) / n
            reg = self.l2 * self.w
            reg[0] = 0.0
            self.w -= self.lr * (grad + reg)
        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        X = np.asarray(X, dtype=float)
        if self._const is not None:
            return np.full(X.shape[0], self._const)
        Xb = self._standardize(X)
        return 1.0 / (1.0 + np.exp(-(Xb @ self.w)))


@dataclass
class ReviewRouter:
    """Value-based, interpretable policy: one logistic correctness model per
    action predicts P(final_correct | pre-review features); the policy routes to

        argmax_a  P_hat_correct(a | x) - lambda_cost*cost(a) - lambda_latency*lat(a)

    i.e. the U formula of manual 6.10. Training uses outcome labels; PREDICTION
    uses only pre-review features. (A direct/value method avoids the cheap-action
    bias of classifying per-patch realized argmax labels.)
    """
    models: dict
    mean_cost: np.ndarray
    mean_latency: np.ndarray
    actions: list
    lam_cost: float
    lam_latency: float

    @classmethod
    def fit(cls, X, correct, cost, latency, actions, *, lam_cost, lam_latency,
            l2: float = 1e-2, seed: int = 0) -> "ReviewRouter":
        K = correct.shape[1]
        models = {a: BinaryLogistic(l2=l2, seed=seed + a).fit(X, correct[:, a])
                  for a in range(K)}
        return cls(models=models, mean_cost=cost.mean(axis=0),
                   mean_latency=latency.mean(axis=0), actions=list(actions),
                   lam_cost=lam_cost, lam_latency=lam_latency)

    def expected_utility(self, X) -> np.ndarray:
        X = np.asarray(X, dtype=float)
        K = len(self.actions)
        U = np.zeros((X.shape[0], K))
        for a in range(K):
            p = self.models[a].predict_proba(X)
            U[:, a] = (p - self.lam_cost * self.mean_cost[a]
                       - self.lam_latency * self.mean_latency[a])
        return U

    def route(self, X) -> np.ndarray:
        return self.expected_utility(X).argmax(axis=1)

    def correctness_importance(self) -> dict:
        """Per-action mean |weight| over features (interpretability)."""
        out = {}
        for a, m in self.models.items():
            cond = self.actions[a]
            if m.w is None:
                out[str(cond)] = {f: 0.0 for f in PRE_REVIEW_FEATURES}
            else:
                out[str(cond)] = {f: float(abs(v))
                                  for f, v in zip(PRE_REVIEW_FEATURES, m.w[1:])}
        return out


# --------------------------------------------------------------------------
# Utility & dataset
# --------------------------------------------------------------------------
def utility(final_correct, cost, latency, lam_cost: float, lam_latency: float):
    """U = correct - lambda_cost*cost - lambda_latency*latency (vectorised)."""
    return (np.asarray(final_correct, dtype=float)
            - lam_cost * np.asarray(cost, dtype=float)
            - lam_latency * np.asarray(latency, dtype=float))


@dataclass
class RouterDataset:
    """A label-free feature matrix X plus per-action realized outcomes.

    correct/cost/latency are (n_patches, n_actions). ``actions`` lists the
    WorkflowCondition for each column. repo_ids gives the independent unit for
    the outer split. ``records`` keeps the raw pre-review dicts.
    """
    records: list
    repo_ids: np.ndarray
    X: np.ndarray
    correct: np.ndarray
    cost: np.ndarray
    latency: np.ndarray
    actions: list
    lam_cost: float = 0.05
    lam_latency: float = 0.0

    def utility_table(self) -> np.ndarray:
        return utility(self.correct, self.cost, self.latency,
                       self.lam_cost, self.lam_latency)

    def best_action_labels(self) -> np.ndarray:
        """Per-patch utility-maximising action (training target)."""
        return self.utility_table().argmax(axis=1)

    def n_actions(self) -> int:
        return len(self.actions)


# --------------------------------------------------------------------------
# Policy evaluation & fixed baselines
# --------------------------------------------------------------------------
def policy_realized_utility(action_per_patch: np.ndarray, util_table: np.ndarray) -> float:
    """Mean realized utility of choosing ``action_per_patch[i]`` for patch i."""
    idx = np.asarray(action_per_patch, dtype=int)
    return float(util_table[np.arange(len(idx)), idx].mean())


def _action_index(actions: list, cond: WorkflowCondition) -> int:
    return actions.index(cond)


def baseline_actions(name: str, n: int, actions: list, *, seed: int = 0) -> np.ndarray:
    """Fixed-policy action vectors: always-cross / always-self / random / no-review."""
    if name == "always_cross":
        return np.full(n, _action_index(actions, WorkflowCondition.CROSS_FAMILY_REVIEW))
    if name == "always_self":
        return np.full(n, _action_index(actions, WorkflowCondition.SELF_REVIEW))
    if name == "always_no_review":
        return np.full(n, _action_index(actions, WorkflowCondition.NO_REVIEW))
    if name == "random":
        rng = np.random.default_rng(seed)
        return rng.integers(0, len(actions), size=n)
    raise ValueError(f"unknown baseline {name!r}")


# --------------------------------------------------------------------------
# Repository-grouped folds (no leakage across the independent unit)
# --------------------------------------------------------------------------
def group_folds(groups, k: int, seed: int = 0):
    """Partition unique group ids into k buckets; yield (train_idx, test_idx)."""
    groups = np.asarray(groups)
    uniq = sorted(set(groups.tolist()))
    rng = random.Random(seed)
    shuffled = uniq[:]
    rng.shuffle(shuffled)
    k = min(k, len(shuffled))
    buckets = [shuffled[i::k] for i in range(k)]
    folds = []
    for b in buckets:
        if not b:
            continue
        test_mask = np.isin(groups, b)
        folds.append((np.where(~test_mask)[0], np.where(test_mask)[0], list(b)))
    return folds


# --------------------------------------------------------------------------
# Nested CV: OUTER fold = repository
# --------------------------------------------------------------------------
@dataclass
class NestedCVResult:
    mean_utility: dict          # policy -> mean realized utility (pooled held-out)
    per_fold: list = field(default_factory=list)
    no_repo_leakage: bool = True
    chosen_l2: list = field(default_factory=list)

    def router_beats(self, *others: str, margin: float = 0.0) -> bool:
        r = self.mean_utility["router"]
        return all(r > self.mean_utility[o] + margin for o in others)


def _fit_review_router(dataset, idx, l2, seed) -> ReviewRouter:
    return ReviewRouter.fit(
        dataset.X[idx], dataset.correct[idx], dataset.cost[idx],
        dataset.latency[idx], dataset.actions,
        lam_cost=dataset.lam_cost, lam_latency=dataset.lam_latency,
        l2=l2, seed=seed)


def _inner_select_l2(dataset, train_idx, candidates, inner_k, seed) -> float:
    """Pick the L2 maximising the value-based router's realized held-out utility
    over an inner repo-grouped CV on the TRAINING repos (no outer-test leakage)."""
    best_l2, best_score = candidates[0], -np.inf
    repos = dataset.repo_ids[train_idx]
    util_table = dataset.utility_table()
    folds = group_folds(repos, inner_k, seed=seed)
    if not folds:
        return best_l2
    for l2 in candidates:
        scores = []
        for tr_rel, te_rel, _ in folds:
            tr = train_idx[tr_rel]
            te = train_idx[te_rel]
            if len(tr) == 0 or len(te) == 0:
                continue
            router = _fit_review_router(dataset, tr, l2, seed)
            acts = router.route(dataset.X[te])
            scores.append(policy_realized_utility(acts, util_table[te]))
        score = float(np.mean(scores)) if scores else -np.inf
        if score > best_score:
            best_score, best_l2 = score, l2
    return best_l2


def nested_cv_by_repo(
    dataset: RouterDataset,
    *,
    outer_k: int = 4,
    inner_k: int = 3,
    l2_candidates=(1e-2, 1e-1, 1.0),
    seed: int = 0,
    baselines=("always_cross", "always_self", "random", "always_no_review"),
) -> NestedCVResult:
    """Run nested CV with the OUTER fold split by repository.

    Returns pooled held-out mean utility for the router, each fixed baseline, and
    an (oracle) upper bound, plus a hard check that no repository appears in both
    train and test of any outer fold.
    """
    util_table = dataset.utility_table()
    repos = dataset.repo_ids

    pooled: dict = {"router": [], "oracle": []}
    for b in baselines:
        pooled[b] = []
    per_fold = []
    chosen_l2 = []
    no_leak = True

    outer = group_folds(repos, outer_k, seed=seed)
    for fold_i, (tr, te, test_repos) in enumerate(outer):
        if len(tr) == 0 or len(te) == 0:
            continue
        train_repos = set(repos[tr].tolist())
        if train_repos & set(test_repos):
            no_leak = False

        # inner CV (also repo-grouped) on the TRAINING repos to pick L2
        l2 = _inner_select_l2(dataset, tr, list(l2_candidates), inner_k,
                              seed + fold_i + 1)
        chosen_l2.append(l2)

        router = _fit_review_router(dataset, tr, l2, seed + 100 + fold_i)
        pred = router.route(dataset.X[te])

        ut_te = util_table[te]
        fold_scores = {"router": policy_realized_utility(pred, ut_te)}
        # oracle upper bound (uses held-out outcomes; reference only)
        fold_scores["oracle"] = policy_realized_utility(ut_te.argmax(axis=1), ut_te)
        for name in baselines:
            acts = baseline_actions(name, len(te), dataset.actions,
                                    seed=seed + fold_i + 7)
            fold_scores[name] = policy_realized_utility(acts, ut_te)

        for k_, v_ in fold_scores.items():
            pooled[k_].append(v_)
        per_fold.append({"fold": fold_i, "test_repos": test_repos,
                         "l2": l2, "n_test": int(len(te)), **fold_scores})

    mean_utility = {k_: float(np.mean(v_)) for k_, v_ in pooled.items() if v_}
    return NestedCVResult(mean_utility=mean_utility, per_fold=per_fold,
                          no_repo_leakage=no_leak, chosen_l2=chosen_l2)
