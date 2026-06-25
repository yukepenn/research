# P4 HarnessGuard — KILL memo (2026-06-25)

**Decision: KILLED as a standalone paper.** Not for lack of novelty — P4 passed the novelty audit
(NARROW, no fatal collision; surviving core = edit-conditioned diversity canary selection + OOD
selector generalization). Killed on **feasibility + falsification risk** under the current
constraints (zero paid API; finish 3 papers in days).

## Why (honest)
1. **Worst fit for the zero-cost pipeline.** The cheap evidence engine is single-shot
   plan-then-execute. P4's entire thesis is that harness components (retry / verifier / stopping)
   matter only across an *interactive multi-step* loop; producing real P4 evidence needs the
   expensive interactive harness, and even then the effect is small on the easy task suite.
2. **Highest risk of failing its own kill-gate.** P4's primary hypothesis H2 ("edit-conditioned
   selection beats random canaries at fixed budget") has VERIFIED counter-evidence
   (arXiv:2409.03563, arXiv:2510.08730: selection often ties random for fine-grained deltas). Of
   the four, P4 was the most likely to honestly collapse to a negative result.
3. **Heaviest data requirement** for a flagship (>=25 independent real edits, ideally >=3 model
   families) — not achievable in the available time/compute.

This is the manual's intended behaviour: kill a line early when feasibility/evidence don't justify a
full study, rather than pad to a paper count (manual 2.0, 11.4, 29).

## What is preserved (not deleted)
The deterministic Tier-0 (`modular_harness.py`, `edit_corpus/`, `ground_truth.py`,
`feature_extraction/`, `selector.py`, `evaluate.py`, `real_pilot.py`, 16 passing tests) remains in
the repo as reusable infrastructure and a candidate appendix/tool. Reactivation condition: a budgeted
study with real harness edits across >=3 model families where a pilot shows H2 holds (selection
beats random) on an interactive task suite.

## Resources redirected to: P1 ToolMorph, P2 CrossCheck, P3 DeltaResearch.
