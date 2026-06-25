"""Workflow conditions + budget-matching accounting (manual 6.7 / 6.8; H2 PRIMARY-A).

The decisive arm cc02 lacks is AUTHOR_MORE_COMPUTE: giving the *same author* the
same extra token/$ budget that a reviewer would have consumed, instead of a
second model. A fair claim that "cross review helps" must therefore compare
review workflows against an author-extra-compute baseline at MATCHED budget.

This module:
  - enumerates the 8 workflow conditions;
  - models per-workflow cost (tokens / $ / wall-clock) with a ``WorkflowCost``;
  - composes author + reviewer costs into a review-workflow total;
  - constructs the matched AUTHOR_MORE_COMPUTE counterfactual;
  - decides whether two workflows are token-matched and/or dollar-matched within
    a relative tolerance.

Wall-clock is reported but NOT used for matching (parallel reviewers can raise
cost while lowering latency -- manual 6.8).
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from core.adapters.base import Usage


class WorkflowCondition(str, Enum):
    NO_REVIEW = "no_review"
    AUTHOR_MORE_COMPUTE = "author_more_compute"
    SELF_REVIEW = "self_review"
    SAME_FAMILY_FRESH = "same_family_fresh"
    CROSS_FAMILY_REVIEW = "cross_family_review"
    TEST_GENERATION_ONLY = "test_generation_only"
    INDEPENDENT_REIMPLEMENTATION = "independent_reimplementation"
    ROUTER = "router"

    def __str__(self) -> str:
        return self.value


# The "review" workflows that consume an extra (reviewer-side) budget on top of
# the author's first pass. AUTHOR_MORE_COMPUTE matches the budget of these.
REVIEW_CONDITIONS = (
    WorkflowCondition.SELF_REVIEW,
    WorkflowCondition.SAME_FAMILY_FRESH,
    WorkflowCondition.CROSS_FAMILY_REVIEW,
    WorkflowCondition.TEST_GENERATION_ONLY,
    WorkflowCondition.INDEPENDENT_REIMPLEMENTATION,
)


@dataclass
class WorkflowCost:
    condition: WorkflowCondition
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    latency_seconds: float = 0.0

    @property
    def total_tokens(self) -> int:
        return int(self.input_tokens) + int(self.output_tokens)

    @classmethod
    def from_usage(cls, condition: WorkflowCondition, usage: Usage) -> "WorkflowCost":
        return cls(
            condition=WorkflowCondition(condition),
            input_tokens=usage.input_tokens,
            output_tokens=usage.output_tokens,
            cost_usd=usage.cost_usd,
            latency_seconds=usage.latency_seconds,
        )


def combine(condition: WorkflowCondition, *costs: WorkflowCost) -> WorkflowCost:
    """Sum several stage costs (e.g. author + reviewer) into one workflow total.

    Latency is summed by default (sequential stages); pass already-parallelised
    latencies in the stage costs if a workflow runs reviewers concurrently.
    """
    return WorkflowCost(
        condition=WorkflowCondition(condition),
        input_tokens=sum(c.input_tokens for c in costs),
        output_tokens=sum(c.output_tokens for c in costs),
        cost_usd=round(sum(c.cost_usd for c in costs), 8),
        latency_seconds=round(sum(c.latency_seconds for c in costs), 6),
    )


def review_workflow_cost(
    author_first_pass: WorkflowCost,
    reviewer_pass: WorkflowCost,
    condition: WorkflowCondition = WorkflowCondition.CROSS_FAMILY_REVIEW,
) -> WorkflowCost:
    """Total cost of a review workflow = author first pass + reviewer pass."""
    return combine(condition, author_first_pass, reviewer_pass)


def author_more_compute_cost(
    author_first_pass: WorkflowCost,
    extra_budget: WorkflowCost,
) -> WorkflowCost:
    """The matched counterfactual: give the AUTHOR an extra budget equal to what
    a reviewer would have consumed (``extra_budget``), rather than a 2nd model.

    By construction this is token/$-matched to ``review_workflow_cost(author,
    extra_budget)``: same totals, attributed entirely to the author.
    """
    return combine(WorkflowCondition.AUTHOR_MORE_COMPUTE, author_first_pass, extra_budget)


@dataclass(frozen=True)
class BudgetMatch:
    token_ratio: float
    dollar_ratio: float | None
    token_matched: bool
    dollar_matched: bool | None
    matched: bool
    rel_tol: float


def _rel_diff(a: float, b: float) -> float:
    denom = max(abs(a), abs(b))
    if denom == 0:
        return 0.0
    return abs(a - b) / denom


def budget_match(
    a: WorkflowCost,
    b: WorkflowCost,
    *,
    rel_tol: float = 0.05,
    compare: str = "both",
) -> BudgetMatch:
    """Decide whether two workflows are budget-matched within ``rel_tol``.

    ``compare`` in {"tokens", "dollars", "both"}. Dollar matching is only
    evaluated when both workflows carry a positive cost (pricing configured);
    otherwise ``dollar_matched`` is None and "both" falls back to token matching.
    """
    token_ratio = _rel_diff(a.total_tokens, b.total_tokens)
    token_matched = token_ratio <= rel_tol

    if a.cost_usd > 0 and b.cost_usd > 0:
        dollar_ratio: float | None = _rel_diff(a.cost_usd, b.cost_usd)
        dollar_matched: bool | None = dollar_ratio <= rel_tol
    else:
        dollar_ratio = None
        dollar_matched = None

    if compare == "tokens":
        matched = token_matched
    elif compare == "dollars":
        matched = bool(dollar_matched)
    elif compare == "both":
        matched = token_matched and (dollar_matched if dollar_matched is not None else True)
    else:
        raise ValueError(f"compare must be tokens|dollars|both, got {compare!r}")

    return BudgetMatch(
        token_ratio=token_ratio,
        dollar_ratio=dollar_ratio,
        token_matched=token_matched,
        dollar_matched=dollar_matched,
        matched=matched,
        rel_tol=rel_tol,
    )
