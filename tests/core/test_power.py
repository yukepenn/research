"""Tests for simulation-based power analysis."""
from core.statistics.power import estimate_power, required_units


def test_power_rises_with_effect_and_n():
    # near-zero effect -> low power (~alpha); large effect -> high power
    null = estimate_power(n_units=24, effect=0.0, n_sims=120, n_boot=300, seed=1)
    big = estimate_power(n_units=72, effect=-0.20, n_sims=120, n_boot=300, seed=1)
    assert null.power < 0.2
    assert big.power > null.power
    assert big.power >= 0.6


def test_required_units_monotone_sensible():
    n_small_effect = required_units(effect=-0.08, target_power=0.8,
                                    n_sims=80, n_boot=250, seed=2)
    n_large_effect = required_units(effect=-0.25, target_power=0.8,
                                    n_sims=80, n_boot=250, seed=2)
    # a larger effect needs no more units than a smaller one (or both None)
    if n_small_effect is not None and n_large_effect is not None:
        assert n_large_effect <= n_small_effect
