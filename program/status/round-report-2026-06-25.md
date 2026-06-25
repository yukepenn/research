# Research Status — 2026-06-25 (cycle 1)

## Portfolio
- P1 ToolMorph:    NOVELTY_PASS_NARROWED, confidence 0.45 — Tier-0 complete, next gate PILOT (budget-gated)
- P2 CrossCheck:   NOVELTY_PASS_NARROWED, confidence 0.45 — Tier-0 complete, next gate PILOT (budget-gated)
- P3 DeltaResearch: NOVELTY_PASS_NARROWED, confidence 0.45 — Tier-0 complete, next gate PILOT (budget-gated)
- P4 HarnessGuard: NOVELTY_PASS_NARROWED, confidence 0.40 — Tier-0 complete, next gate PILOT (budget-gated)

## Completed evidence (issue / artifact / commit / acceptance)
- COMMON kernel+infra: run-ledger, adapters(+budget gate), statistics(resampling+power), runner,
  sealed access, citations, claims/manuscript checker, dashboard, validator, CI — 38 tests — commits 07d4af8, 53e9435, 1fa62e8, c8c56d1
- Anchor + collision verification: 9 papers personally web-verified (5 anchors + 4 collisions) — artifacts/citations.sqlite, program/references.bib
- Novelty audit (8 agents, 240 tool calls): papers/*/novelty/{related_work.csv,novelty_matrix.md,novelty_attack.md}; program/fatal_overlap.md — commit b3159e5
- P1 ToolMorph Tier-0: 3 envs, 6-family DSL, >15k-case equivalence proof (0 mismatch), metamorphic harness, STNF layer — 11 tests — commits 645abaa, c6eb722
- P2/P3/P4 Tier-0: mutation injectors+router(no-leakage), evidence-world generator(independent gold)+typed-graph+evaluator+H_DIVERGE, edit-corpus+canary selector(H2+leave-one-lineage-out) — 56 tests — commit ef3f35c
- 97/97 tests passing (independently re-run by Director); `make validate` OK

## Strongest new finding (verified)
- The deterministic state-transition-equivalence proof (P1) and the independent-gold world generator (P3)
  establish that, where these papers later report a model effect, it CANNOT be a benchmark artifact:
  transforms are byte-identical state transitions (>15k cases), and P3's gold is computed by separate
  world-physics, not by the method. This is the credibility precondition the manual demands before paid runs.
- Classification: confirmatory for the INFRASTRUCTURE claims (deterministic, reproduced in-suite);
  the scientific phenomena remain UNTESTED (need models, budget-gated).

## Failures and counterexamples (kept, not hidden)
- Self-tests caught two real bugs during the build, both fixed: (1) P1 `cal_cancel` invariant was vacuously
  true on empty state; (2) the generic "request round-trip == identity" property was wrong for the
  optional_default transform — replaced with a uniform per-call STATE-equivalence property.
- Runner originally dispatched transformed tool calls by canonical name; fixed to use each presented tool's
  own codec-bound executor.

## Novelty changes (the headline of this cycle)
All four projects collided with a strong, VERIFIED prior work and were NARROWED (none fatal, none killed):
- P1 vs PIPE (2602.01611): EQ+META is occupied -> re-architect around label-free STNF transfer to UNSEEN transforms.
- P2 vs cc02 (KDD'26): bidirectional 2x2 occupied -> survive via budget-matched author-extra-compute + defect-type complementarity + held-out router.
- P3 vs EditPropBench (2605.02083) + Mr.DRE: dual metric & phenomenon occupied -> survive via typed-graph patch beating flat ledger on an evidence-WORLD delta.
- P4 vs AgentAssay (2603.02601) + TDAD: cheap testing/abstention & diff-conditioned RTS occupied -> survive via edit-conditioned diversity canary selection + OOD selector.
Each surviving core has a HARD KILL-GATE encoded in research_contract.yaml.

## Budget
- spent $0 / committed $0 / projected: pilots require human budget+pricing+credentials (UNCONFIGURED).

## Decisions made
- CONTINUE all four (narrowed), no MERGE, no KILL — justification in program/decisions.md and fatal_overlap.md.
- Enforced the paid-provider budget gate in code (BudgetGateError) so no spend can occur accidentally.

## Next executable queue (ranked; all Tier-0 / reversible until the budget gate)
1. [HUMAN] configure program/budget.yaml + program/pricing.yaml + credentials -> unblocks all pilots.
2. P3 H_DIVERGE expansion + real versioned-evidence inventory (Layer B) — partly deterministic, no model needed.
3. P1 LLM-assisted + probe STNF compiler stubs behind the gate; oracle-canonicalizer recovery harness scale-up.
4. P2 controlled-defect corpus expansion + retention-funnel logging for natural near-miss mining.
5. P4 optimizer-generated + real-historical edit mining to reach >=25 independent edits (flagship gate).
6. Per-paper pilot configs + power simulation using core.statistics.power once pilot variance exists.
7. Re-run nearest-neighbor sweep before each gate (fast-moving area).

## Human decisions required (true gates only)
- Configure provider credentials + hard budget ceilings (no secrets in repo).
- Approve the four narrowed central claims and venue targets.
- Confirm proceed-vs-merge/kill given the NARROW scope (Director recommends proceed, with the encoded gates).
