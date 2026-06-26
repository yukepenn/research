# P2 CrossCheck — Terminal Decision

**Terminal state: `HOLD`.** The idea (budget-matched, error-correlation-aware review routing) remains
promising, but the decisive data cannot be obtained with the current authorized resources: a
controlled defect corpus — even a deliberately hard, fully-specified one — cannot pull frontier
models off the one-shot ceiling, so no workflow can be distinguished.

**Target venue (if revived):** FSE 2027 Research Track (full paper deadline 2026-10-02 AoE) — but only
after a corpus that actually discriminates workflows exists.

**One-sentence supported claim (current):**
> On both an easy and a deliberately hard, fully-specified controlled defect corpus, frontier coding
> agents (Claude, Codex) repair small single-defect modules one-shot, so no-review, author-extra-
> compute, and cross-family review are indistinguishable at matched budget; measuring review value
> requires a corpus whose no-review baseline is off the ceiling.

**Strongest result (with caveat):** hard corpus, n=12/workflow: NO_REVIEW 1.00, AUTHOR_MORE_COMPUTE
1.00, CROSS_FAMILY_REVIEW 0.92 (a single review-induced regression on type_serialization). The easy
corpus replicated the same 0.80 three-way tie. No discriminating signal.

**Strongest counterexample / why HOLD:** the budget-matched comparison (cross-review vs equal author
compute) — the paper's decisive contribution vs cc02 — is unanswerable at a 1.00 no-review ceiling.
The only feasible fix is a real multi-file repository corpus (containerized real issues + hidden
tests) where no-review lands ~0.4–0.6; that is heavy data engineering not feasible at zero metered
cost in this sprint.

**Remaining blockers to revival:**
1. A real-repository, mid-difficulty, fairly-specified near-miss corpus (no-review ~0.4–0.6).
2. Then: the full budget-matched bidirectional matrix, defect-type complementarity on real data, and
   held-out-repository router validation (all currently simulator-validated only).

**Exact human decisions required:**
- Decide whether to invest in building the real-repository corpus (the path off HOLD), which likely
  needs more compute/time and possibly licensed infrastructure.
- No external action is recommended in the HOLD state.

**arXiv posting recommended now?** No. There is no discriminating empirical result; only a replicated
"frontier models one-shot controlled defects" observation plus reusable methodology. Not for posting.

**Confidence:** High that the controlled-corpus approach cannot discriminate these models; the
methodology (budget-matched protocol, complementarity, router) is sound and ready for a harder corpus.
