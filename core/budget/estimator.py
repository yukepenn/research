"""Dry-run cost estimator + budget ledger (COMMON-007, manual 11).

estimate_experiment: from an experiment config (episodes, avg tokens, model),
estimate token volume and — only if pricing is configured — dollar cost, then
check it against the paper's budget.yaml limits. Exceeding a limit is a HUMAN
GATE, not something an agent may bypass (manual 11.2).

BudgetLedger: reads the run ledger, sums metered cost per paper, and raises
alerts at the configured fractions.
"""
from __future__ import annotations

import os
from dataclasses import dataclass

import yaml

from core.budget.pricing import cost_usd
from core.experiment_registry.ledger import RunLedger

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BUDGET_PATH = os.path.join(_REPO_ROOT, "program", "budget.yaml")


def load_budget() -> dict:
    with open(BUDGET_PATH, encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


@dataclass
class Estimate:
    episodes: int
    input_tokens: int
    output_tokens: int
    cost_usd: float | None        # None if pricing unconfigured
    limit_usd: float | None       # None if budget unconfigured
    exceeds_limit: bool
    requires_human_gate: bool
    note: str


def estimate_experiment(
    *,
    paper_id: str,
    episodes: int,
    avg_input_tokens: int,
    avg_output_tokens: int,
    model_id: str,
    budget_key: str = "pilot_api",
) -> Estimate:
    in_tok = episodes * avg_input_tokens
    out_tok = episodes * avg_output_tokens
    cost = cost_usd(model_id, in_tok, out_tok)

    budget = load_budget()
    limit = (budget.get("papers", {}).get(paper_id, {}) or {}).get(budget_key)

    if cost is None:
        return Estimate(episodes, in_tok, out_tok, None, limit, False, True,
                        "pricing unconfigured -> cannot cost; paid runs are a human gate")
    if limit is None:
        return Estimate(episodes, in_tok, out_tok, cost, None, False, True,
                        "budget limit unconfigured -> paid runs are a human gate")
    exceeds = cost > float(limit)
    return Estimate(episodes, in_tok, out_tok, cost, float(limit), exceeds, exceeds,
                    "OK within budget" if not exceeds else "exceeds limit -> human gate")


class BudgetLedger:
    def __init__(self, ledger: RunLedger):
        self.ledger = ledger

    def spent(self, paper_id: str) -> float:
        return round(sum(float(e.get("cost_usd") or 0.0)
                         for e in self.ledger.read_all()
                         if e.get("paper_id") == paper_id), 6)

    def alerts(self, paper_id: str, budget_key: str = "full_api") -> list[str]:
        budget = load_budget()
        limit = (budget.get("papers", {}).get(paper_id, {}) or {}).get(budget_key)
        if limit is None:
            return []
        fracs = budget.get("alerts_at_fraction", [0.5, 0.8, 1.0])
        spent = self.spent(paper_id)
        out = []
        for f in fracs:
            if spent >= float(limit) * float(f):
                out.append(f"{paper_id}: spent ${spent:.2f} >= {int(f*100)}% of ${limit}")
        return out
