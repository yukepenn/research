"""Deterministic evaluation metrics for evidence-delta report patching.

Given a :class:`~papers.p3_deltaresearch.baselines.Patch` and the gold sets of a
:class:`~papers.p3_deltaresearch.controlled_worlds.generator.World`, compute the
pre-registered dual objective and its diagnostics:

  ACR  affected-claim recall          fraction of must-change (A) claims edited
  UCP  unaffected-claim preservation  fraction of must-preserve (U) claims left alone
  stale_residual_rate                 = 1 - ACR  (missed obligated updates)
  spurious_revision_rate              = 1 - UCP  (collateral damage to U)
  unsupported_new_rate                added claims not actually supported (hallucinated)
  citation_freshness                  edited A-claims whose citation was refreshed
  calculation_correctness             numeric A-claims edited to the correct value
  conflict_honesty                    contested (C) claims honestly flagged

The PRIMARY endpoint is ACR and UCP reported JOINTLY (a Pareto pair) -- never a
single maskable average. :func:`combined_score` returns the pair plus convenience
summaries clearly marked as secondary.

All metrics are pure set/number functions (no LLM) and treat empty denominators
as a vacuous perfect score (1.0) / zero rate.
"""
from __future__ import annotations

import math
from dataclasses import dataclass


def _as_set(x) -> set:
    return set(getattr(x, "edited", x))


# --------------------------------------------------------------------------
# Primary dual objective
# --------------------------------------------------------------------------
def acr(patch, gold_A) -> float:
    """Affected-claim recall: |edited & A| / |A|. Vacuously 1.0 if A empty."""
    gold_A = set(gold_A)
    if not gold_A:
        return 1.0
    return len(_as_set(patch) & gold_A) / len(gold_A)


def ucp(patch, gold_U) -> float:
    """Unaffected-claim preservation: |U \\ edited| / |U|. Vacuously 1.0."""
    gold_U = set(gold_U)
    if not gold_U:
        return 1.0
    return len(gold_U - _as_set(patch)) / len(gold_U)


def stale_residual_rate(patch, gold_A) -> float:
    """Fraction of must-change claims left unedited (= 1 - ACR)."""
    gold_A = set(gold_A)
    if not gold_A:
        return 0.0
    return len(gold_A - _as_set(patch)) / len(gold_A)


def spurious_revision_rate(patch, gold_U) -> float:
    """Fraction of must-preserve claims that were touched (= 1 - UCP)."""
    gold_U = set(gold_U)
    if not gold_U:
        return 0.0
    return len(_as_set(patch) & gold_U) / len(gold_U)


# --------------------------------------------------------------------------
# Diagnostics
# --------------------------------------------------------------------------
def unsupported_new_rate(patch, gold_N) -> float:
    """Of the claims the patch ADDED, fraction not actually newly supported."""
    added = set(getattr(patch, "added", set()))
    if not added:
        return 0.0
    return len(added - set(gold_N)) / len(added)


def citation_freshness(patch, world) -> float:
    """Of the A-claims whose gold citation changed, fraction the patch refreshed
    to the correct new citation. Vacuously 1.0 if none required refreshing."""
    need = {c for c in world.gold_A
            if world.post_citations.get(c) != world.pre_citations.get(c)}
    if not need:
        return 1.0
    fresh = sum(1 for c in need
                if c in patch.new_citations
                and patch.new_citations[c] == world.post_citations.get(c))
    return fresh / len(need)


def calculation_correctness(patch, world, *, tol: float = 1e-9) -> float:
    """Of the numeric A-claims with a defined post value, fraction the patch
    edited to the correct recomputed value."""
    numeric_A = [c for c in world.gold_A
                 if world.is_numeric(c) and world.post_values.get(c) is not None]
    if not numeric_A:
        return 1.0
    correct = 0
    for c in numeric_A:
        if c in patch.edited and c in patch.new_values:
            if math.isclose(float(patch.new_values[c]), float(world.post_values[c]),
                            abs_tol=tol):
                correct += 1
    return correct / len(numeric_A)


def conflict_honesty(patch, gold_C) -> float:
    """Fraction of contested (C) claims the patch honestly flagged. Vacuously
    1.0 if there is no conflict."""
    gold_C = set(gold_C)
    if not gold_C:
        return 1.0
    return len(set(patch.flagged_contested) & gold_C) / len(gold_C)


# --------------------------------------------------------------------------
# Pre-registered combined (joint) score
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class CombinedScore:
    acr: float
    ucp: float
    # secondary scalar summaries -- NEVER the primary (kept for ranking only)
    harmonic: float
    worst: float

    @property
    def joint(self) -> tuple[float, float]:
        return (self.acr, self.ucp)

    def dominates(self, other: "CombinedScore") -> bool:
        """Pareto dominance on the (ACR, UCP) pair."""
        return (self.acr >= other.acr and self.ucp >= other.ucp
                and (self.acr > other.acr or self.ucp > other.ucp))


def combined_score(patch, world) -> CombinedScore:
    """The pre-registered PRIMARY: ACR and UCP reported jointly. `harmonic` and
    `worst` are convenience summaries only; the endpoint is the (ACR, UCP) pair."""
    a = acr(patch, world.gold_A)
    u = ucp(patch, world.gold_U)
    harmonic = (2 * a * u / (a + u)) if (a + u) > 0 else 0.0
    return CombinedScore(acr=a, ucp=u, harmonic=harmonic, worst=min(a, u))


def correct_update_recall(patch, world) -> float:
    """Stricter than ACR: of the must-change claims (gold A), the fraction that the
    patch BOTH identified AND updated to the correct content — numeric value match,
    correct boolean status, or (for a retraction/loss of support, gold value None)
    at least flagged as changed. No vacuous 1.0 for empty-numeric cases."""
    A = list(world.gold_A)
    if not A:
        return 1.0
    edited = set(getattr(patch, "edited", patch))
    nv = getattr(patch, "new_values", {})
    correct = 0
    for c in A:
        pv = world.post_values.get(c)
        if pv is None:                                   # retraction / lost support
            if c in edited:
                correct += 1
        elif isinstance(pv, bool):
            if c in nv and bool(nv[c]) == pv:
                correct += 1
        elif isinstance(pv, (int, float)):
            if c in nv and abs(float(nv[c]) - float(pv)) < 1e-6:
                correct += 1
        else:                                            # categorical / textual
            if c in edited:
                correct += 1
    return correct / len(A)


def full_report(patch, world) -> dict:
    """All metrics for one (patch, world) -- the per-row record for the study."""
    return {
        "acr": acr(patch, world.gold_A),
        "ucp": ucp(patch, world.gold_U),
        "stale_residual_rate": stale_residual_rate(patch, world.gold_A),
        "spurious_revision_rate": spurious_revision_rate(patch, world.gold_U),
        "unsupported_new_rate": unsupported_new_rate(patch, world.gold_N),
        "citation_freshness": citation_freshness(patch, world),
        "calculation_correctness": calculation_correctness(patch, world),
        "conflict_honesty": conflict_honesty(patch, world.gold_C),
    }
