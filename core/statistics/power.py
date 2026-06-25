"""Simulation-based power analysis for paired, task-clustered binary designs.

The manual (14.4) requires deciding the full-study sample size by SIMULATED power,
not a textbook formula, because the unit is the task cluster with nested repeats.
This module is shared by all four papers: estimate power at a given number of
independent units (tasks/repos/worlds/edits) and a hypothesized paired effect.

All randomness is seeded -> reproducible. Effects/variances are INPUTS (filled from
pilot estimates); nothing here fabricates an effect.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from core.statistics.resampling import paired_cluster_bootstrap_diff


def _simulate_paired_dataset(rng, n_units, repeats, base_rate_mean, base_rate_sd, effect):
    """Per-unit base success rate ~ clipped Normal; condition A = base, condition B =
    base + effect (effect typically negative for a degradation). Repeats are nested
    Bernoulli draws within a unit (correlated through the shared unit rate)."""
    a_vals, b_vals, clusters = [], [], []
    for u in range(n_units):
        p_a = float(np.clip(rng.normal(base_rate_mean, base_rate_sd), 0.02, 0.98))
        p_b = float(np.clip(p_a + effect, 0.0, 1.0))
        for _ in range(repeats):
            a_vals.append(float(rng.random() < p_a))
            b_vals.append(float(rng.random() < p_b))
            clusters.append(u)
    return a_vals, b_vals, clusters


@dataclass
class PowerResult:
    n_units: int
    repeats: int
    effect: float
    power: float
    n_sims: int


def estimate_power(*, n_units: int, effect: float, repeats: int = 2,
                   base_rate_mean: float = 0.7, base_rate_sd: float = 0.15,
                   n_sims: int = 200, n_boot: int = 600, alpha: float = 0.05,
                   seed: int = 0) -> PowerResult:
    """Fraction of simulations whose (1-alpha) paired cluster-bootstrap CI for
    mean(B)-mean(A) excludes 0 in the hypothesized direction."""
    rng = np.random.default_rng(seed)
    detect = 0
    for s in range(n_sims):
        a, b, cl = _simulate_paired_dataset(rng, n_units, repeats,
                                            base_rate_mean, base_rate_sd, effect)
        ci = paired_cluster_bootstrap_diff(a, b, cl, n_boot=n_boot,
                                           conf=1 - alpha, seed=int(rng.integers(1e9)))
        if effect < 0 and ci.hi < 0:
            detect += 1
        elif effect > 0 and ci.lo > 0:
            detect += 1
    return PowerResult(n_units, repeats, effect, detect / n_sims, n_sims)


def required_units(*, effect: float, target_power: float = 0.8,
                   candidates=(12, 24, 36, 48, 72, 96, 120),
                   **kw) -> int | None:
    """Smallest candidate unit count reaching target power; None if none suffice."""
    for n in candidates:
        if estimate_power(n_units=n, effect=effect, **kw).power >= target_power:
            return n
    return None
