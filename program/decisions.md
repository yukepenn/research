# Decision Log

## 2026-06-25 — Program bootstrap (Research Director)

- **D1 Verify before trust.** Verified all 5 anchor sources (AHE, Mr.DRE, TSCG, Refute-or-Promote,
  Code-as-Harness) exist before building on the novelty framing. All real.
- **D2 Core-first.** Built and unit-tested the shared kernel (ledger, adapters, statistics) and
  infrastructure (runner, sealed access, budget, citations, claims/manuscript checker, dashboard)
  before any paper-specific work. 32 tests green. Rationale: manual 11.1 (kill Tier-0 bugs before paid runs).
- **D3 Budget gate enforced in code.** Real model providers raise `BudgetGateError` until
  `program/budget.yaml` + `program/pricing.yaml` are configured (human gate). Mock adapter enables all Tier-0 work.
- **D4 Docker absent → local sandbox.** No Docker on this host; the task runner degrades to
  in-process / disposable-subprocess sandboxing. Documented as a reproducibility limitation; full
  artifact will ship a container recipe.
- **D5 Novelty audit → all four NARROW.** 8-agent web-verified audit found a strong "most damaging"
  prior work for each project but no fatal collision. Verified the 4 load-bearing collision papers
  myself (PIPE 2602.01611, EditPropBench 2605.02083, AgentAssay 2603.02601, cc02 KDD'26). Decision:
  continue all four, re-architected around the surviving cores; encode hard kill-gates in each
  research_contract.yaml. See `program/fatal_overlap.md`.
- **D6 No paid experiments yet.** All four sit at NOVELTY_PASS_NARROWED → PILOT. Pilots need the
  human budget/credential gate; until then, only Tier-0 deterministic engineering proceeds.

### Human decisions pending
1. Configure provider credentials + hard budget ceilings (no secrets in repo).
2. Approve the four narrowed central claims and venue targets.
3. Confirm none of the four should instead MERGE/KILL given the NARROW scope (Director recommends: proceed, with gates).
