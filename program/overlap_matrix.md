# Cross-Paper Overlap Matrix (anti-salami, manual 9.4)

Maintained to prove the four papers are scientifically independent. Regenerate and re-check
before any submission. Shared assets are INFRASTRUCTURE only (no shared primary result).

## Per-paper distinctness

| Dimension | P1 ToolMorph | P2 CrossCheck | P3 DeltaResearch | P4 HarnessGuard |
|---|---|---|---|---|
| Central question | Does label-free normalization recover agents under unseen equivalent tool-interface transforms? | When is heterogeneous code review worth it vs more author compute (budget-matched)? | Which report claims must change / must not, under an evidence-WORLD delta? | Which canaries reveal hidden regressions before shipping a harness edit? |
| Primary intervention unit | tool-interface transform / STNF | review workflow / router | evidence delta / typed-graph patch | harness edit / canary selector |
| Primary result unit | task × model × transform | repository / patch × workflow | evidence world × update | harness edit × task regression |
| Primary endpoint | STNF recovery on held-out transforms | equal-budget final-patch correctness + router frontier | joint ACR/UCP under evidence delta | regression recall @ budget + false-safe |
| Main method | semantic normal form + metamorphic protocol | error-correlation model + ReviewRoute | typed dependency graph + constrained patcher | edit-conditioned diverse canary selector |
| Main figure | recovery–cost frontier (held-out) | cost–correctness Pareto | ACR–UCP Pareto | risk–coverage curve |
| Target venue | MLSys/ICLR or TMLR | FSE 2027 | ARR Oct 2026 | MLSys/ICLR or TMLR |

## Shared infrastructure (allowed)
`core/` (adapters, ledger, tracing, runner, statistics incl. resampling+power, sealed access,
citations, audit, budget, dashboard, plotting). Each paper builds its OWN data split, oracle,
and primary metric on top.

## Pairwise merge-risk check
- P1 vs P4 both use stateful tool environments, BUT P1's unit is the *interface transform* and
  P4's is the *harness edit*; task suites and primary metrics differ; **no merge**.
- P2 vs P4 both touch coding/regression, BUT P2 is *review-workflow value* and P4 is *pre-ship
  canary selection*; disjoint data and endpoints; **no merge**.
- P3 stands alone (evidence-world report revision); **no merge**.

## Status
No MERGE triggered (2026-06-25). `MERGE_REVIEW` to be re-run if any two papers begin to share a
primary result, main table, or decisive experiment.
