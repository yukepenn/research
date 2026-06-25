"""Statistical primitives shared by all four papers (manual section 14).

The manual is strict about the *unit of analysis*: repeated runs of one task are
nested observations, not independent samples (1.2). So every inferential helper
here resamples the true independent unit (task / repository / world / edit) via
cluster bootstrap, and binary rates get exact intervals. Everything is
seeded for reproducibility.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence

import numpy as np
from scipy import stats


@dataclass(frozen=True)
class Interval:
    point: float
    lo: float
    hi: float
    level: float = 0.95

    def as_tuple(self) -> tuple[float, float, float]:
        return (self.point, self.lo, self.hi)


# --------------------------------------------------------------------------
# Binary-rate confidence intervals
# --------------------------------------------------------------------------
def wilson_ci(successes: int, n: int, conf: float = 0.95) -> Interval:
    if n == 0:
        return Interval(float("nan"), 0.0, 1.0, conf)
    z = stats.norm.ppf(1 - (1 - conf) / 2)
    p = successes / n
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = (z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n))) / denom
    return Interval(p, max(0.0, center - half), min(1.0, center + half), conf)


def clopper_pearson_ci(k: int, n: int, conf: float = 0.95) -> Interval:
    """Exact binomial interval — used for false-safe rates (manual 8.15)."""
    if n == 0:
        return Interval(float("nan"), 0.0, 1.0, conf)
    alpha = 1 - conf
    lo = 0.0 if k == 0 else stats.beta.ppf(alpha / 2, k, n - k + 1)
    hi = 1.0 if k == n else stats.beta.ppf(1 - alpha / 2, k + 1, n - k)
    return Interval(k / n, float(lo), float(hi), conf)


# --------------------------------------------------------------------------
# Paired binary test
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class McNemarResult:
    n_discordant: int
    b: int  # original=pass, mutated=fail  (degradation)
    c: int  # original=fail, mutated=pass  (recovery)
    statistic: float
    p_value: float
    method: str


def mcnemar_test(b: int, c: int, exact_threshold: int = 25) -> McNemarResult:
    """Two-sided McNemar test on discordant pair counts b and c.

    b = #(original success & mutated failure), c = the reverse. Exact binomial
    for small samples; chi-square with continuity correction otherwise.
    """
    n = b + c
    if n == 0:
        return McNemarResult(0, b, c, 0.0, 1.0, "degenerate")
    if n <= exact_threshold:
        k = min(b, c)
        p = min(1.0, 2 * stats.binom.cdf(k, n, 0.5))
        return McNemarResult(n, b, c, float(k), float(p), "exact_binomial")
    stat = (abs(b - c) - 1) ** 2 / n
    p = float(stats.chi2.sf(stat, 1))
    return McNemarResult(n, b, c, float(stat), p, "chi2_continuity")


# --------------------------------------------------------------------------
# Cluster bootstrap (the workhorse)
# --------------------------------------------------------------------------
def _percentile_ci(samples: np.ndarray, point: float, conf: float) -> Interval:
    alpha = 1 - conf
    lo = float(np.quantile(samples, alpha / 2))
    hi = float(np.quantile(samples, 1 - alpha / 2))
    return Interval(point, lo, hi, conf)


def cluster_bootstrap(
    values: Sequence[float],
    clusters: Sequence,
    stat: Callable[[np.ndarray], float] | None = None,
    *,
    n_boot: int = 5000,
    conf: float = 0.95,
    seed: int = 0,
) -> Interval:
    """Bootstrap a statistic by resampling whole clusters with replacement.

    `clusters` gives each value's independent unit (task/repo/world/edit). The
    default statistic is the mean. Resampling clusters (not rows) is what keeps
    the CI honest about nested repeats (manual 1.2, 14.x).
    """
    values = np.asarray(values, dtype=float)
    clusters = np.asarray(clusters)
    stat = stat or (lambda v: float(np.mean(v)))
    uniq = np.unique(clusters)
    idx_by_cluster = {c: np.where(clusters == c)[0] for c in uniq}
    rng = np.random.default_rng(seed)
    point = stat(values)
    boot = np.empty(n_boot)
    for i in range(n_boot):
        pick = rng.choice(uniq, size=len(uniq), replace=True)
        idx = np.concatenate([idx_by_cluster[c] for c in pick])
        boot[i] = stat(values[idx])
    return _percentile_ci(boot, point, conf)


def paired_cluster_bootstrap_diff(
    cond_a: Sequence[float],
    cond_b: Sequence[float],
    clusters: Sequence,
    *,
    n_boot: int = 5000,
    conf: float = 0.95,
    seed: int = 0,
) -> Interval:
    """CI for mean(cond_b) - mean(cond_a) on paired observations sharing a
    cluster id. Resamples clusters; within a chosen cluster keeps the pairing.

    Returns the difference (b - a): for ToolMorph pass `cond_a=original`,
    `cond_b=mutated` to get the (negative) degradation directly.
    """
    a = np.asarray(cond_a, dtype=float)
    b = np.asarray(cond_b, dtype=float)
    clusters = np.asarray(clusters)
    if not (len(a) == len(b) == len(clusters)):
        raise ValueError("cond_a, cond_b, clusters must be the same length")
    uniq = np.unique(clusters)
    idx_by_cluster = {c: np.where(clusters == c)[0] for c in uniq}
    rng = np.random.default_rng(seed)
    point = float(np.mean(b) - np.mean(a))
    boot = np.empty(n_boot)
    for i in range(n_boot):
        pick = rng.choice(uniq, size=len(uniq), replace=True)
        idx = np.concatenate([idx_by_cluster[c] for c in pick])
        boot[i] = float(np.mean(b[idx]) - np.mean(a[idx]))
    return _percentile_ci(boot, point, conf)


# --------------------------------------------------------------------------
# Ranking stability (ToolMorph H4)
# --------------------------------------------------------------------------
def kendall_tau(order_a: Sequence, order_b: Sequence) -> float:
    """Kendall tau-b between two score vectors (aligned by model)."""
    tau, _ = stats.kendalltau(order_a, order_b)
    return float(tau) if tau == tau else float("nan")  # nan-guard


def kendall_tau_bootstrap(
    scores_a: np.ndarray,
    scores_b: np.ndarray,
    *,
    n_boot: int = 5000,
    conf: float = 0.95,
    seed: int = 0,
) -> Interval:
    """Bootstrap Kendall tau over tasks for ranking stability across two
    interfaces. `scores_a`/`scores_b` are shape (n_tasks, n_models): per-task,
    per-model success under each interface. Resample tasks, recompute
    model-mean scores under each interface, take tau between the two rankings.
    """
    scores_a = np.asarray(scores_a, dtype=float)
    scores_b = np.asarray(scores_b, dtype=float)
    n_tasks = scores_a.shape[0]
    rng = np.random.default_rng(seed)
    point = kendall_tau(scores_a.mean(0), scores_b.mean(0))
    boot = np.empty(n_boot)
    for i in range(n_boot):
        idx = rng.integers(0, n_tasks, n_tasks)
        boot[i] = kendall_tau(scores_a[idx].mean(0), scores_b[idx].mean(0))
    return _percentile_ci(boot[~np.isnan(boot)], point, conf)


# --------------------------------------------------------------------------
# Multiple comparison correction
# --------------------------------------------------------------------------
def benjamini_hochberg(pvals: Sequence[float], alpha: float = 0.05) -> list[bool]:
    """Return per-hypothesis reject decisions controlling FDR at alpha."""
    p = np.asarray(pvals, dtype=float)
    m = len(p)
    order = np.argsort(p)
    thresh = (np.arange(1, m + 1) / m) * alpha
    passed = p[order] <= thresh
    if not passed.any():
        return [False] * m
    kmax = np.max(np.where(passed)[0])
    reject = np.zeros(m, dtype=bool)
    reject[order[: kmax + 1]] = True
    return reject.tolist()


def holm(pvals: Sequence[float], alpha: float = 0.05) -> list[bool]:
    """Holm step-down FWER control."""
    p = np.asarray(pvals, dtype=float)
    m = len(p)
    order = np.argsort(p)
    reject = np.zeros(m, dtype=bool)
    for rank, idx in enumerate(order):
        if p[idx] <= alpha / (m - rank):
            reject[idx] = True
        else:
            break
    return reject.tolist()
