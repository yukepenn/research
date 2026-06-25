"""Model pricing snapshot (COMMON-007).

Prices are NOT hard-coded here on purpose: list prices change and fabricating
them would violate the manual's no-fabrication rule (1.1, 6.8 "use exact run
date & price snapshot"). Prices are loaded from program/pricing.yaml which the
human fills in from the provider's official page, with a snapshot date. Until
configured, cost estimates return None (token estimates are still produced).
"""
from __future__ import annotations

import os

import yaml

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PRICING_PATH = os.path.join(_REPO_ROOT, "program", "pricing.yaml")


def load_pricing() -> dict:
    """Return {model_id: {in_per_mtok, out_per_mtok}, _snapshot_date: ...} or {}."""
    if not os.path.exists(PRICING_PATH):
        return {}
    with open(PRICING_PATH, encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def price_for(model_id: str) -> tuple[float, float] | None:
    pricing = load_pricing()
    entry = pricing.get(model_id)
    if not entry:
        return None
    return (float(entry["in_per_mtok"]), float(entry["out_per_mtok"]))


def cost_usd(model_id: str, input_tokens: int, output_tokens: int) -> float | None:
    p = price_for(model_id)
    if p is None:
        return None
    return (input_tokens / 1e6) * p[0] + (output_tokens / 1e6) * p[1]
