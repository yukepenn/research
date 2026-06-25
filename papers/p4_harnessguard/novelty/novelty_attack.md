# HarnessGuard (p4) -- Novelty Prosecution (Adversarial)

**Prosecutor's verdict up front: NARROW (strong), bordering on MERGE.** The Scout's
"novelty survives, manage two fronts" assessment is too generous. Targeted search surfaced
**two papers the Scout missed that directly attack the core**, plus two more that strengthen
the "already done" case. The single most damaging is **AgentAssay (arXiv:2603.02601)**, which
already publishes *token-efficient regression testing for non-deterministic AI agent workflows
after changes to prompts / tools / models / orchestration*, with a **three-valued
PASS/FAIL/INCONCLUSIVE abstention**, **adaptive-budget SPRT**, and **trace reuse**. It does not
do *edit-conditioned task selection / predict-before-run / OOD selector generalization*, so it
is **not a fatal collision** -- but it strips two of our four contribution legs.

Central claim under test: after a harness component (prompt/tools/middleware/memory/retry/
verifier/stopping) is auto-edited, local gains hide cross-task regressions; structurally
representing the edit + selecting a few high-risk diverse canaries from historical traces +
escalating to full eval when uncertain finds most dangerous regressions far below full-bench cost.
Boundary excludes: auto-editing harnesses, edit self-prediction, generic self-evolving agents,
smoke/random canaries, "harness affects ranking."

---

## 1. The 10 works most likely to make a reviewer say "already done" (verified URLs)

Ranked by collision severity. Bold = newly found in this prosecution (NOT in the Scout's 12).

1. **AgentAssay: Token-Efficient Regression Testing for Non-Deterministic AI Agent Workflows**
   -- https://arxiv.org/abs/2603.02601 (Bhardwaj, 2026-03-03; verified, abstract read). **NEW. HIGHEST.**
2. Self-Harness: Harnesses That Improve Themselves
   -- https://arxiv.org/abs/2606.09498 (2026; verified). High.
3. **TDAD: Test-Driven Agentic Development -- Reducing Code Regressions in AI Coding Agents via Graph-Based Impact Analysis**
   -- https://arxiv.org/abs/2603.17973 (Alonso, Yovine, Braberman, 2026-03-18; verified, abstract read). **NEW. High.**
4. Active Evaluation Acquisition for Efficient LLM Benchmarking
   -- https://arxiv.org/abs/2410.05952 (2024; verified). Medium-high (method twin / must-beat).
5. 100 instances is all you need: predicting the success of a new LLM ... by testing on a few instances
   -- https://arxiv.org/abs/2409.03563 (2024; verified). Medium-high (method twin; finds random adequate).
6. **Risk-Aware Batch Testing for Performance Regression Detection**
   -- https://arxiv.org/abs/2604.00222 (Sayedsalehi, Rigby, Mierzwinski, 2026-03-31; verified, abstract read). **NEW. Medium.**
7. **How Reliable is Language Model Micro-Benchmarking?**
   -- https://arxiv.org/abs/2510.08730 (Yauney, Warraich, Swayamdipta, 2025-10-09, rev 2026-03-06; verified, abstract read). **NEW. Medium (threatens H2).**
8. Rapid Regression Detection in Software Deployments through Sequential Testing
   -- https://arxiv.org/abs/2205.14762 (2022; verified). Medium (escalation machinery).
9. Test Case Selection and Prioritization Using Machine Learning (SLR)
   -- https://arxiv.org/abs/2106.13891 (2021; verified). Medium ("just regression test selection").
10. When Generic Prompt Improvements Hurt: Evaluation-Driven Iteration for LLM Applications
    -- https://arxiv.org/abs/2601.22025 (2026; verified). Medium (phenomenon).

Supporting cast (cite, lower individual risk, but collectively erode the "phenomenon is novel"
and "harness optimizers don't validate OOD" framing):
- **Layer-Isolated Evaluation** -- https://arxiv.org/abs/2606.11686 (2026; verified, abstract read). **NEW.** Deterministic per-layer slices; *aggregate masks per-layer regressions* (-1.7 to -5.9pp aggregate vs -25 to -91pp on the matching slice). Cedes our "aggregate hides regressions" motivation.
- **Meta-Harness: End-to-End Optimization of Model Harnesses** -- https://arxiv.org/abs/2603.28052 (Lee, Nair, Zhang, Lee, Khattab, Finn, 2026-03-30; verified, abstract read). **NEW.** Another excluded harness optimizer; reports *held-out-model* generalization of the discovered harness on TerminalBench-2.
- Agentic Harness Engineering (AHE, ANCHOR) -- https://arxiv.org/abs/2604.25850 (verified). Creates the edits + edit self-prediction (both excluded by our boundary).
- Beyond the Mean (2604.27405), SCoRE (2603.24704), Positive-Congruent Training (2011.09161), Harness-Updating (2605.30621), VeRO (2602.22480) -- all verified by Scout; background/component/excluded-optimizer roles.

---

## 2. Per-work itemized overlap with our claim

### (1) AgentAssay -- arXiv:2603.02601 -- THE most damaging "already done"
Verbatim abstract anchors: "no principled methodology exists for verifying that an agent has not
regressed after **changes to its prompts, tools, models, or orchestration logic**"; "the **first
token-efficient framework for regression testing non-deterministic AI agent workflows**, achieving
78-100% cost reduction"; contributions include "(1) **stochastic three-valued verdicts
(PASS/FAIL/INCONCLUSIVE)** grounded in hypothesis testing; ... (6) **behavioral fingerprinting that
maps execution traces to compact vectors**, enabling multivariate regression detection; (7)
**adaptive budget optimization calibrating trial counts to behavioral variance**; and (8)
**trace-first offline analysis** enabling zero-cost testing on production traces." Evaluated across
5 models (GPT-5.2, Claude Sonnet 4.6, Mistral-Large-3, Llama-4-Maverick, Phi-4); "SPRT reduces trials by 78%."

- OVERLAP (what it already owns, for our exact unit = the agent harness):
  - Same problem: detect regressions after **harness edits** (prompts/tools/models/orchestration). This is our setting almost verbatim.
  - **Cheap/budgeted** regression testing for **stochastic** agents -- our "far below full-benchmark cost" headline. It claims **"first."**
  - **Abstain/escalate** -- our contribution (3): three-valued INCONCLUSIVE + SPRT *is* uncertainty-gated escalation, applied to agents. Strictly stronger than nn08/nn09 (which were generic/services).
  - Historical **traces** + **stochastic** regression labels -- our "historical task traces" + "stochastic regression label."
  - Multiple **model families** in the eval.
- NON-overlap (what it does NOT do -- our surviving wedge): its cost savings come from (a) SPRT
  reducing **trials-per-test** (sampling efficiency) and (b) **reusing existing traces**; it does
  **NOT select which tasks** from a large suite to run, does **NOT condition selection on a
  structured representation of the specific edit**, does **NOT predict per-task regression before
  execution to prioritize a fixed-k canary set**, and shows **no held-out edit/task/model selector
  generalization** (mutation operators *generate* synthetic faults; they do not condition on a real edit).
- BLUNT READ: AgentAssay and HarnessGuard are **orthogonal cost levers** -- they cut trials/test,
  we (claim to) cut #tests via edit-conditioned selection. A reviewer will demand we prove our lever
  adds recall *on top of* theirs, at matched budget. If we cannot, we are an AgentAssay feature request.

### (2) Self-Harness -- arXiv:2606.09498
Self-evolving per-model harness with a **regression-testing accept gate**; reports agent self-prediction
of regressions is near-random (~2x baseline). OVERLAP: establishes our motivation *and* already gates
edits with regression tests. NON-overlap: ad-hoc/full regression tests, no edit-conditioned **selection**
at fixed k, no calibrated abstention, no OOD generalization. (Motivation, not method.)

### (3) TDAD -- arXiv:2603.17973 -- edit-conditioned selection for agents already exists (different unit)
Verbatim: "performs **pre-change impact analysis** for AI coding agents"; "builds a **dependency map
between source code and tests so that before committing a patch, the agent knows which tests to verify**";
SWE-bench Verified, 2 open-weight models; "reduced regressions by 70%." OVERLAP: this is the exact
template **edit/diff -> select a subset of tests -> catch regressions before the full run, for an
agent**. NON-overlap with us: unit of analysis is the **code the agent writes** (a patch), the
selector is a **deterministic static code-dependency graph**, the tests are **deterministic unit
tests** -- not the agent's **harness** (prompt/tools/memory/retry/verifier/stopping), not a stochastic
pass->fail delta with model x harness interactions, no abstention, no OOD selector study. It nonetheless
**kills our "first to bring edit-conditioned regression foresight to agents" framing.**

### (4) Active Evaluation Acquisition -- arXiv:2410.05952
Learned RL acquisition selects a few items + predicts the rest. OVERLAP: closest "select-few-predict-rest"
method; must-beat baseline. NON-overlap: estimates **aggregate** performance of **one** model, not the
**edit-conditioned pass->fail delta between two harnesses**; no abstention.

### (5) 100 instances is all you need -- arXiv:2409.03563
Predicts per-instance success of a new model from ~100 reference instances. OVERLAP: per-instance
outcome prediction from a few tests. NON-overlap: absolute success not regression delta; not edit-conditioned;
**finds random selection adequate in-distribution** -- a verified counterexample to our H2.

### (6) Risk-Aware Batch Testing -- arXiv:2604.00222 -- the modern "just regression test selection"
Verbatim: "integrates **machine-learned commit risk** with **adaptive batching**"; "fine-tune
ModernBERT, CodeBERT, and LLaMA-3.1 ... to estimate **commit-level performance regression risk**";
"reduces total test executions by 32.4%." OVERLAP: **edit(commit)-conditioned, ML-risk-scored,
budget-aware regression-test selection** -- using LLM-based diff features. This is nn11 made concrete,
recent, and strong. NON-overlap: deterministic software, aggregate performance metric, no stochastic
agent tasks, no abstention. Strengthens the SE attack: "risk-scored edit-conditioned selection at a
budget is solved; you ported it."

### (7) How Reliable is Language Model Micro-Benchmarking? -- arXiv:2510.08730 -- threatens H2 directly
Verbatim: "no micro-benchmarking method can consistently rank model pairs 3.5 points ... apart on
MMLU-Pro"; "as many as **250 examples must be selected, at which point random sampling is competitive
with existing micro-benchmarking methods**." DOUBLE-EDGED: (a) HELPS us -- proves the cheap-eval family
(nn06/nn07/tinyBenchmarks/anchor-points) targets **aggregate ranking** and **fails at fine-grained
comparison**, which is the gap we exploit; (b) HURTS us -- verified evidence that **selection does not
beat random** for small deltas. If harness regressions look like small diffuse deltas, our H2
("selection matters") is **already falsified** and the paper has no method contribution.

### (8) Rapid Regression Detection / Sequential Testing -- arXiv:2205.14762
Anytime-valid sequential tests, FPR-controlled canary monitoring. OVERLAP: our escalation machinery +
"canary" framing. NON-overlap: aggregate service metrics, no task selection, not edit-conditioned. But
note: **AgentAssay already imports SPRT into the agent setting**, so this leg is doubly taken.

### (9) ML-TSP Systematic Literature Review -- arXiv:2106.13891
Taxonomy of ML test selection/prioritization. OVERLAP: the "this is just regression test selection"
attack. NON-overlap: deterministic code-diff features, single system. We must implement the strongest
reproducible baseline; Risk-Aware Batch (#6) is its concrete 2026 instantiation to beat.

### (10) When Generic Prompt Improvements Hurt -- arXiv:2601.22025
Documents prompt edits silently regressing apps (Qwen2.5 RAG 26/30 -> 9/30). OVERLAP: phenomenon
evidence. NON-overlap: characterization via full suite only; no prediction/selection/abstention.

---

## 3. Which specific claims we can NO LONGER make

1. **"First / novel cheap (budget-efficient) regression testing for LLM agents/harnesses."** DEAD --
   AgentAssay explicitly claims "first token-efficient framework for regression testing
   non-deterministic AI agent workflows."
2. **"We contribute a calibrated abstain/escalate decision layer for agent regression detection."**
   DEAD as a contribution -- AgentAssay already has three-valued PASS/FAIL/INCONCLUSIVE + adaptive-budget
   SPRT for agents; nn08/nn09 supply the generic guarantees. We may only claim to **adopt/extend** it.
3. **"First to bring edit/diff-conditioned test selection to agents to catch regressions before a full
   run."** DEAD -- TDAD (coding agents, pre-change impact analysis) and Risk-Aware Batch (commit-risk
   selection) already do edit-conditioned selection-before-full-run. We may only claim the
   **harness-unit + stochastic model x harness + regression-delta-objective** specialization.
4. **"Using historical traces and stochastic three-valued regression labels for agent testing is novel."**
   DEAD -- AgentAssay (trace-first, three-valued), Beyond-the-Mean, Layer-Isolated already do this.
5. **"Selection beats random canaries" as an assumed premise (H2).** CANNOT ASSUME -- 100-Instances and
   Micro-Benchmarking-Reliability provide verified evidence that selection is *not* better than random
   for fine-grained deltas. This must be **empirically won**, conceding the effect-size regime where random ties.
6. **"We are first to show aggregate scores mask per-task regressions in agents/harnesses."** DEAD --
   Layer-Isolated, Beyond-the-Mean, When-Prompts-Hurt, Self-Harness already establish it. The phenomenon
   is **motivation, not contribution.**

What we CAN still claim (the entire surviving paper):
- **Edit-CONDITIONED, diversity-aware SELECTION of a few canaries that targets the per-task pass->fail
  REGRESSION-DELTA label (not aggregate performance), PREDICTING the regression set BEFORE the full
  suite, and GENERALIZING out-of-distribution across held-out edit type / task family / model family.**
  No single neighbor does this composition. But it is now a *narrower, empirical* claim, and contingent on H2 holding.

---

## 4. Experiments we MUST add to prove the difference

1. **Beat AgentAssay head-to-head AND show orthogonality.** Implement AgentAssay's SPRT-per-test +
   trace-reuse + INCONCLUSIVE pipeline as the primary baseline. Show (a) at matched total token/trial
   budget, edit-conditioned canary **selection** reaches higher regression **recall**, and (b) selection
   stacks **on top of** their per-test trial reduction (combined > either alone). Without this, we are a feature of AgentAssay.
2. **Beat the edit-conditioned-RTS template.** Implement TDAD-style (static impact/risk) and
   Risk-Aware-Batch-style (ML commit/edit-risk -> select) selectors as the strongest must-beat baselines,
   and show that on **stochastic harness edits** the deterministic code-diff template underperforms a
   selector that models **model x harness interaction** and the **regression-delta** label.
3. **H2 under the micro-benchmarking-reliability lens.** Replicate Yauney et al.'s meta-evaluation:
   plot regression-recall vs **edit effect size**, and prove edit-conditioned selection beats **random**
   canaries at the **same budget**. Explicitly report the effect-size / budget regime where random catches
   up (it will, per 2510.08730 and 2409.03563) and confine our claim to the regime where it does not.
4. **OOD selector generalization (the headline).** Held-out **edit type**, **task family**, and **model
   family** evaluation of the *selector itself* -- none of AgentAssay/TDAD/Risk-Aware-Batch do this. This
   is the cleanest surviving differentiator and must be the main table.
5. **Edit-conditioning ablation.** Show the **structural edit representation** beats edit-agnostic
   selection (historical-failure-rate prior; diversity-only; IRT/anchor-points subset). This isolates the
   one thing nobody else has done: conditioning canary choice on the structural diff to predict the delta.
6. **Calibration-only-adoption check.** Demonstrate our abstain/escalate is at least as risk-controlled
   as AgentAssay's INCONCLUSIVE+SPRT, so reviewers cannot say we regressed the one component they own.

---

## 5. Worst case: what our contribution gets downgraded to

- **Most likely downgrade (NARROW):** from "a new problem + method (edit-conditioned regression foresight
  for evolving agent harnesses with risk-controlled deployment)" down to **"an edit-conditioned task-selection
  front-end bolted onto AgentAssay's already-published cheap-agent-regression-testing + abstention pipeline
  -- i.e., a TDAD/ML-TSP/Risk-Aware-Batch regression-test-selection variant specialized to stochastic harness
  edits, plus an OOD generalization study."** A solid empirical/systems delta (one selection module + one
  generalization result), **not a conceptual first.** Venue: applied/eval track, not a flagship "new problem."
- **Catastrophic downgrade (KILL/negative result):** if H2 fails -- i.e., **random canaries match
  edit-conditioned selection** at fixed budget (the verified default outcome in 100-Instances and
  Micro-Benchmarking-Reliability) -- the paper collapses to **"AgentAssay-style cheap testing already
  suffices; edit-conditioned selection does not help for harness regressions,"** publishable only as a
  short negative-result / reproduction note.

---

## 6. Recommendation: NARROW (with a hard kill-condition)

**Recommendation: NARROW.** Not PASS: the Scout's framing overclaims novelty that AgentAssay (cheap agent
regression testing + abstention) and TDAD / Risk-Aware Batch (edit-conditioned selection-before-full-run
for agents/software) now demonstrably own. Not KILL: no single work establishes our *full* core claim with
our unit -- nobody does **edit-conditioned canary selection on the regression-delta label for harness edits
with predict-before-suite and OOD generalization** (AgentAssay reduces trials/test and reuses traces but
does not select tasks or condition on the edit; TDAD selects deterministic unit tests for generated code,
not the stochastic harness). So `fatal_collision = false`. **But survival is conditional, not comfortable.**
The defensible paper must (i) drop the "first cheap agent regression testing" and "novel abstention" claims
and cede them to AgentAssay; (ii) drop "first edit-conditioned regression foresight for agents" and cede it
to TDAD/Risk-Aware-Batch, retaining only the harness-unit + stochastic + regression-delta + OOD wedge;
(iii) treat the hidden-regression phenomenon as motivation, not contribution; and (iv) **empirically win
H2 (selection beats random) against the verified evidence that it usually does not.** If experiments 1-5
land and H2 holds in a non-trivial effect-size regime, this is a publishable NARROW contribution. If H2
fails, it auto-converts to KILL (negative result). Freeze H2 as the gating pilot before any full study.
