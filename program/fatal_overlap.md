# Fatal-Overlap / Novelty Audit Result — 2026-06-25

Source: background workflow `novelty-audit` (8 agents: scout + adversarial prosecutor per
paper, 240 tool calls, web-verified). Full per-paper artifacts in
`papers/<paper>/novelty/{related_work.csv, novelty_matrix.md, novelty_attack.md}`.

**Bottom line: NO fatal single-paper collision for any project. All four are NARROW
(re-architect around a surviving core), none KILLED, none MERGED.** Every "most damaging"
paper below was independently fetched and verified to exist by the Research Director before
acting on it.

| Paper | Verdict | Most damaging prior work (verified) | Surviving core (the only defensible novelty) | Hard kill gate |
|---|---|---|---|---|
| P1 ToolMorph | NARROW | PIPE — *What Do Agents Learn from Trajectory-SFT* (arXiv 2602.01611, verified) — behavior-preserving interface rewrite + paired gap + multi-model | Label-free **STNF that transfers to UNSEEN transform families/tools** (PIPE only diagnoses; TSCG fixed operators; Rewrite-Tool-Desc unseen-tools only) | Content-control erases effect **AND** STNF can't beat description-rewrite |
| P2 CrossCheck | NARROW | cc02 — *Cross-Model LLM Code Review: Claude↔Codex* (KDD'26 Agentic-SE, Xiang et al., verified) — bidirectional 2×2 incl. self-review, direction-dependent | Conjunction: **budget-matched author-extra-compute arm + defect-type complementarity interaction + pre-call held-out router** | Gains vanish at matched budget **AND** router fails on held-out repos → negative result |
| P3 DeltaResearch | NARROW | EditPropBench (arXiv 2605.02083, verified) — change/preserve dual metric, ~30% miss; Mr.DRE (2601.13217) owns the phenomenon | **Typed dependency-graph patch+audit beating flat ledger + full regen on an evidence-WORLD delta**, transfer controlled→real | No behavioral divergence between evidence-world delta and author edit (H_DIVERGE) |
| P4 HarnessGuard | NARROW | AgentAssay (arXiv 2603.02601, verified) — first token-efficient agent regression testing + 3-valued + SPRT; TDAD (2603.17973) diff-conditioned RTS | **Edit-conditioned diversity canary SELECTION on the regression-delta label + OOD selector generalization**; stacks on AgentAssay's trials-per-test lever | H2 fails: random ties selection at fixed budget (counter-evidence: 2409.03563, 2510.08730) |

## Required actions (folded into each research_contract.yaml)
- **P1**: head-to-head vs PIPE; pre-registered NORM-transfer-to-unseen split as PRIMARY; ranking-reversal table ≥6 models; byte-identical state-transition audit (DONE in Tier-0 equivalence proof); information-content control (H3).
- **P2**: add `AUTHOR_MORE_COMPUTE` arm (decisive, cc02 lacks it); ≥3–4-family bidirectional matrix with interaction isolation; defect-type error-correlation that PREDICTS lift; pre-call router on held-out repos; correctness+regression endpoint.
- **P3**: H_DIVERGE gating experiment (evidence-world delta vs author edit); ablation ladder no-structure→flat ledger→typed graph; patch vs full-regen; conflict/temporal/computed/citation endpoints; controlled→real transfer.
- **P4**: H2 as gating pilot (selection vs random at matched budget); AgentAssay-style sequential baseline + stacking; TDAD/Risk-Aware-Batch must-beat baselines; OOD selector study as main table; edit-conditioning ablation.

## Anti-salami check
Central questions, primary endpoints, main figures, and primary methods remain disjoint across
the four (see `program/overlap_matrix.md` to be generated before any submission). No MERGE
triggered. Shared assets are infrastructure only (adapters, ledger, runner, stats).
