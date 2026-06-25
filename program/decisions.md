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

## 2026-06-25 — cycle 2 (real-evidence pilots, no paid API)

- **D7 Zero-cost real evidence.** Per user, no metered API spend: use existing Claude + Codex
  subscriptions via their CLIs. Built a plan-then-execute / -patch / -repair harness (we control
  execution + deterministic oracles) — unified-harness, not product-loop. GitHub: pushed to
  https://github.com/yukepenn/research (private, cached GCM token).
- **D8 P1 pilot diagnosed + fixed a confound.** First (single-shot) run floored baseline at 0.40
  because the model couldn't reference server-assigned ids; rebuilt as an interactive harness
  (baseline 1.0) and excluded the confounded run (exclusions.csv). Real finding: enum-encoding
  degrades both Claude and Codex; nesting/lexical robust.
- **D9 KILL P4 HarnessGuard.** Evidence-driven early kill (NOT novelty — it passed NARROW). Reasons:
  worst fit for the zero-cost single-shot pipeline, H2 has verified counter-evidence, heaviest data
  need. Tier-0 preserved as reusable infra. See papers/p4_harnessguard/KILL_MEMO.md. Focus now:
  **P1, P2, P3 only.**

### Human decisions pending
1. Configure provider credentials + hard budget ceilings (no secrets in repo).
2. Approve the four narrowed central claims and venue targets.
3. Confirm none of the four should instead MERGE/KILL given the NARROW scope (Director recommends: proceed, with gates).
