# CrossCheck — Novelty Attack (Adversarial Prosecution)

**Paper:** CrossCheck: Error-Correlation-Aware Heterogeneous Review for Coding Agents
**Central claim under attack:** Heterogeneous-model review is *not* inherently better than same-model self-review or giving the author more compute; net benefit depends on author–reviewer error **complementarity per defect type**. With strict budget matching, a full bidirectional author–reviewer matrix, and held-out-repository routing, we can predict when calling a second model is worth it.
**Prosecutor's date:** 2026-06-25
**Verdict (preview):** **NARROW.** Not a fatal single-work collision, but the headline framing is now pre-empted by a verified concurrent workshop paper (cc02). Three of our four deltas survive; one (the bidirectional 2×2 and the "not inherently better" headline) is partially burned.

---

## 0. What changed during this sweep (read this first)

The Scout left cc02 ("Cross-Model LLM Code Review: Should you use Claude to review Codex or vice versa?") as UNVERIFIED (ResearchGate 403). **I have now triangulated it and treat its existence and qualitative finding as VERIFIED**, while its exact numbers remain unconfirmed:

- **Existence + authorship + venue confirmed** via Google Scholar and the KDD'26 workshop record: authors **Zuodong Xiang, Yike Zhang, YueMing Zhang, Hailu Xu**; accepted/presented at **Agentic Software Engineering (SE 3.0) @ KDD '26**, Jeju, Korea, **2026-08-10**. (The workshop is co-located with SIGKDD'26 and anchored on the AIDev agentic-PR dataset.)
- **Setup confirmed:** writer→reviewer(→reviser) with a **single model pair, Claude Opus 4.7 ↔ Codex GPT-5.5**, evaluated on **LiveCodeBench**, including both cross orderings *and* same-model self-review (Claude-reviews-Claude, Codex-reviews-Codex).
- **Headline finding confirmed (qualitatively):** the value is **asymmetric/direction-dependent** — Claude reviewing Codex lifts Codex drafts substantially, the reverse degrades Claude — and crucially **"Claude Opus 4.7 solo sits on the Pareto frontier; no reviewed condition matched or exceeded it in accuracy."**
- **Still unverified:** the ResearchGate PDF body (HTTP 403); the exact pass-rate numbers (search mirrors disagree: 91.4%/82.8% vs 71.6%→89.7% on 116 tasks vs LiveCodeBench) — so I do **not** cite specific figures, only the qualitative result, which is what damages us.

Caveat for honesty: KDD'26 is **after** our sweep date (Aug 10 vs Jun 25), but the ResearchGate preprint is already public, so this is concurrent-to-just-prior art and a reviewer **will** know it by the time we submit.

I also surfaced one additional verified routing-on-code paper not in the Scout set — **Triage** (arXiv 2604.07494, Madeyski, 2026-04-08), which routes SE tasks across cost tiers using code-health signals on SWE-bench Lite. It reinforces that **cost-aware model routing for code is already a populated space** (relevant to our delta 4).

---

## 1. The 10 works most likely to make a reviewer say "already done" (verified URLs)

Ranked by damage to *our specific* contribution, not by general fame.

1. **Cross-Model LLM Code Review: Should you use Claude to review Codex or vice versa?** (cc02) — Xiang, Zhang, Zhang, Xu, Agentic SE @ KDD'26.
   https://www.researchgate.net/publication/407032793_Cross-Model_LLM_Code_Review_Should_you_use_Claude_to_review_Codex_or_vice_versa (PDF 403; corroborated at https://agent-se.github.io/ )
   **Most damaging.** Bidirectional cross-model + self-review on code, finds cross-review is *not* inherently better than the stronger model solo.
2. **Phase Transition for Budgeted Multi-Agent Synergy** (cc04) — Liu, Kong, Pei, 2026. https://arxiv.org/abs/2601.17311
   Closed-form theory: collaboration helps iff error correlation is low enough relative to budget. This *is* our mechanism, in theory form.
3. **Single-Agent LLMs Outperform MAS Under Equal Thinking-Token Budgets** (cc05) — Tran, Kiela, 2026. https://arxiv.org/abs/2604.02460
   The budget-matching move (delta 1): normalize compute and the multi-agent advantage disappears.
4. **Refute-or-Promote** (cc01, VERIFIED ANCHOR) — Agarwal, 2026. https://arxiv.org/abs/2604.19049
   Cross-model critic for code defects in a real field study. Owns "heterogeneous critique finds code bugs."
5. **Agent-as-a-Router: Agentic Model Routing for Coding Tasks** (cc03) — Zhou et al., 2026. https://arxiv.org/abs/2606.22902
   Pre-call routing across heterogeneous models for code with OOD generalization (delta 4).
6. **Correlated Errors in Large Language Models** (cc06) — Kim, Garg, Peng, Garg, ICML 2025. https://arxiv.org/abs/2506.07962
   Heterogeneous models are *not* error-diverse; correlation rises with accuracy (delta 3 premise — and it is *not ours*).
7. **Articulate but Wrong: Self-Review Failures in LLM Code Modernization** (cc07) — Reddy, Lolla, Sanku, 2026. https://arxiv.org/abs/2605.21537
   Self-review unreliable AND failures cluster across models (r=0.52): our premise *and* part of our correlation argument.
8. **LLM Critics Help Catch LLM Bugs** (cc09) — McAleese et al. (OpenAI), 2024. https://arxiv.org/abs/2407.00215
   Boundary: trained critics beat humans at finding code bugs. Forbidden territory.
9. **LLM Consortium for Software Design Refinement (topologies)** (cc12) — Kanamarlapudi, K., 2026. https://arxiv.org/abs/2606.01490
   Controlled comparison of multi-agent topologies for code work; cross-model review ranked as a topology (delta 2 adjacent).
10. **Cross-Model Disagreement as a Label-Free Correctness Signal** (cc13) — Gorbett, Jana, 2026. https://arxiv.org/abs/2603.25450
    "When does a second model add value," via cross-model disagreement, with routing named as the application (delta 4 adjacent).

Honorable mentions (cite-and-scope, lower individual risk): **Triage** (https://arxiv.org/abs/2604.07494, cost-tier routing for code), **Cross-Context Review** cc08 (https://arxiv.org/abs/2603.12123, context-separation confound), **c-CRAB** cc10 (https://arxiv.org/abs/2603.23448, eval substrate + human/agent complementarity), **Sphinx** cc11 (https://arxiv.org/abs/2601.04252).

---

## 2. Per-work itemized overlap with our claim

Yardstick = our four deltas: **(1)** strict budget matching vs author extra-compute; **(2)** full bidirectional author↔reviewer matrix; **(3)** defect-type-level error correlation; **(4)** pre-call held-out routing.

### cc02 — Cross-Model LLM Code Review (THE collision)
- **Shares:** the *exact* question ("should model A review model B's code, or vice versa?"), on code, with **both cross orderings AND same-model self-review baselines**. Establishes — on code, empirically — that **cross-model review is not inherently better than the stronger model alone** and that **its value is asymmetric/direction-dependent**. That is a large fraction of our headline ("heterogeneous review is not inherently better than self-review").
- **Delta 1 (budget):** NOT matched. Compares review conditions to *single-pass solo* and to the *stronger model* solo — not to "give the same author more compute / resample-k / independent redo at equal $." **Our delta survives.**
- **Delta 2 (matrix):** PARTIALLY DONE. A full **2×2 bidirectional** comparison exists — but for **one pair (Claude Opus 4.7 ↔ Codex GPT-5.5)** only, and it attributes the result to a global "stronger model" effect. **The basic bidirectional contrast is no longer novel; the multi-family matrix that statistically separates "stronger reviewer" from "complementary pairing" is.** Delta partially burned.
- **Delta 3 (defect-type correlation):** NOT done. No error-correlation modeling, no per-defect-type analysis; explanation is "stronger model wins." **Our delta survives fully.**
- **Delta 4 (router):** NOT done. Produces a *global* recommendation ("use the stronger model; cross-review the weaker one"), not a *per-case* pre-call router validated on held-out repositories. **Our delta survives fully.**
- **Endpoint:** benchmark pass rate (LiveCodeBench), not budget-matched final-patch-correctness with a regression guard. Adjacent but not identical.

### cc04 — Phase Transition for Budgeted Multi-Agent Synergy
- **Shares:** the *thesis in theory form* — synergy is governed by **error correlation + budget**, with a closed-form routing condition (s>β). This is the conceptual core of "complementarity, not heterogeneity, drives benefit."
- **Misses:** not code/coding-agents; correlation is a **scalar tree parameter**, not **per-defect-type author↔reviewer** correlation conditioned on a patch; no bidirectional code matrix; no held-out empirical router; no patch-correctness endpoint.
- **Risk:** a reviewer will say "your mechanism is cc04 applied to code." Our defense must be that we *measure* defect-type-conditioned correlation empirically and turn it into a *working* router with a correctness endpoint — neither of which cc04 does.

### cc05 — Single-Agent vs MAS at Equal Tokens
- **Shares:** delta-1 stance and rhetorical move ("normalize compute and the multi-agent advantage disappears"), with an information-theoretic (DPI) argument.
- **Misses:** multi-hop reasoning, not code review/repair; MAS-vs-SAS topology, not author↔reviewer cross-model; no correlation modeling; no routing; budget unit is thinking tokens, not author-extra-compute vs second-model cost.
- **Risk:** kills any claim that *budget-normalized skepticism* is itself novel. We may only claim the *code-review instantiation* of it.

### cc01 — Refute-or-Promote (anchor)
- **Shares:** cross-model critic for code defects; multiple families as critics; real targets.
- **Misses:** all four deltas (no equal-budget vs author compute; no bidirectional matrix; no defect-type correlation; no pre-call routing; precision/external-acceptance endpoint, not budget-matched correctness).
- **Risk:** owns "heterogeneous critique finds real code bugs" — a claim our boundary already forbids.

### cc03 — Agent-as-a-Router
- **Shares:** pre-call routing across heterogeneous models for code, exploiting complementary strengths, with OOD/held-out generalization (delta 4 skeleton).
- **Misses:** routes **which model GENERATES**, not whether/which model **REVIEWS** an existing patch; no review action set; no budget matching vs author compute; no defect-type correlation.
- **Risk:** owns "OOD-generalizing model router for code." Our router must be over a **review-action set** (no-review/self/same-family/cross-family/test-gen/reimplementation), not single-model selection, or it reads as cc03 with a relabeled target.

### cc06 — Correlated Errors in LLMs
- **Shares:** the empirical premise for delta 3 (heterogeneous ≠ error-diverse; correlation grows with accuracy across providers).
- **Misses:** not code/review; population-level, not per-defect-type author↔reviewer conditioned on a patch; no budget; no intervention; no routing.
- **Risk:** we cannot claim to have *discovered* that LLM errors are correlated. It is cited motivation, not contribution.

### cc07 — Articulate but Wrong
- **Shares:** self-review is unreliable (silent self-endorsement) AND **failures cluster across models (r=0.52)** — i.e., cross-model error correlation on code, already measured.
- **Misses:** narrow Py2→3 task; same-model self-review only; detection-only (no budget-matched correctness); no bidirectional matrix; no routing; clustering is across-model snippet-level, not per-defect-type author↔reviewer.
- **Risk:** pre-empts "self-review fails" *and* "code errors correlate across models." Our correlation contribution must be **per-defect-type, author↔reviewer-conditioned, and predictive of review lift** — strictly more than cc07's r=0.52 clustering.

### cc09 — LLM Critics Help Catch LLM Bugs
- **Boundary.** Owns "LLM critics find code bugs." Same-family; no budget; no correlation; no routing; critique-quality endpoint. Must be cited to scope *out* the generic claim.

### cc12 — LLM Consortium Topologies
- **Shares:** controlled comparison of multi-agent/review topologies for code work; cross-model review is one ranked topology (delta 2 adjacent).
- **Misses:** software *design* not defect patches with hidden tests; rubric-score not patch correctness; no budget matching; no correlation; no per-case routing (ranks topologies globally).

### cc13 — Cross-Model Disagreement as a Label-Free Signal
- **Shares:** "when does a second model add value," via cross-model disagreement; names routing as the application.
- **Misses:** reasoning/QA not code/patch review; passive uncertainty signal, not an author↔reviewer action producing a corrected patch; no budget; no defect-type correlation; router only *named*, not built/evaluated on held-out repos.
- **Risk:** a reviewer may propose cc13's disagreement signal as a trivial baseline router — we must beat it.

---

## 3. Which specific claims we can NO LONGER make

These must be struck from the abstract/intro or reframed as cited prior results:

1. **"We are the first to show that heterogeneous/cross-model code review is not inherently better than using the stronger model / self-review."** — **GONE.** cc02 shows exactly this on code (bidirectional + self-review, Pareto-frontier solo). cc05 shows it for reasoning under equal budget; cc04 predicts it in theory.
2. **"We are the first to run a bidirectional author↔reviewer (writer/reviewer-swap) cross-model code-review comparison."** — **GONE for the 2-model case.** cc02 already does the 2×2; cc12 ranks cross-model review as a topology. We may only claim the **multi-family matrix that separates reviewer-strength from pairing-complementarity**.
3. **"We discover that cross-model review value is asymmetric / direction-dependent."** — **GONE.** cc02's headline.
4. **"We show LLM errors are correlated / heterogeneous models are not error-diverse."** — **GONE.** cc06 (population), cc07 (code, r=0.52). Premise, not contribution.
5. **"We show self-review is unreliable / silently endorses its own errors."** — **GONE.** cc07, cc08.
6. **"We are the first to tie error correlation + budget to when collaboration pays off."** — **GONE as a conceptual claim.** cc04 owns the theory; cc05 the empirics in reasoning. We can only claim the **defect-type-conditioned, code-specific, empirically-measured** instantiation.
7. **"We are the first to route across heterogeneous models for coding tasks with held-out/OOD generalization."** — **GONE.** cc03 (generation routing), Triage (cost-tier routing). We may only claim routing over a **review-action set** keyed on defect-type complementarity.
8. **"Heterogeneous/cross-model critics can find code defects."** — Forbidden by our own boundary; owned by cc01/cc09.
9. **"Budget-normalizing erases the multi-agent advantage" (as a finding).** — cc05 owns it; we may only confirm it in the review setting.

**What we CAN still claim (the surviving conjunction):** a **strict budget-matched** comparison of cross-review against **giving the same author more compute** (resample-k / longer reasoning / independent redo) — a counterfactual cc02/cc01/cc12 never run; a **full multi-family bidirectional matrix** that statistically isolates a **complementarity interaction** beyond reviewer-strength main effects; **per-defect-type author↔reviewer error-correlation** that **predicts review lift better than global accuracy**; and a **pre-call router over review actions** validated on **held-out repositories** against **final-patch-correctness with a regression-rate guard**, beating the cc02 "use the stronger model" heuristic per-case.

---

## 4. Experiments we MUST add to prove the difference

Each maps to a competitor we must beat. Without these, the listed prior work sinks us.

1. **Budget-matched author-extra-compute arm (vs cc02, cc01, cc05).** For every patch, compare cross-review against the **same author given the equal token/$ budget**: resample-k self-consistency, extended reasoning, and independent self-redo — *not* just "the other model solo." Report final-patch-correctness at **matched cost**. This is the single most important experiment: cc02 only compared to solo single-pass and to the stronger model, never to "more compute to the same author." If cross-review does not beat author-extra-compute at equal budget, our value claim collapses (see Worst Case).

2. **Full multi-family bidirectional matrix with effect decomposition (vs cc02, cc12).** ≥3–4 families (e.g., Claude / Codex-GPT / Gemini / open-weight), every model as both author and reviewer. Fit a model with **reviewer-strength main effect + author×reviewer interaction**; demonstrate a **statistically significant complementarity interaction that survives after controlling for reviewer strength**. cc02 attributes everything to "stronger model" on one pair — we must show residual pairing-specific lift that the stronger-model rule cannot explain. If the interaction vanishes, cc02's global rule already covers us.

3. **Defect-type-conditioned error-correlation model that is *predictive* (vs cc04, cc06, cc07).** Estimate per-defect-type author↔reviewer conditional error correlation and show it **predicts review lift better than (a) global accuracy gap, (b) cc04's scalar correlation, (c) cc06/cc07-style population/snippet clustering, (d) cc13 disagreement entropy.** The deliverable is a calibrated "expected lift" per (author, reviewer, defect-type), not a post-hoc correlation report.

4. **Pre-call router over the review-action set on held-out repositories (vs cc03, cc13, cc02).** Train the router on defect-type complementarity; evaluate on **repositories never seen in training** with a **final-patch-correctness endpoint and a regression-rate guard**. It must beat: always-cross, always-self, always-stronger-solo (the cc02 heuristic), a cc03-style generation-router transplant, and a cc13 disagreement-signal router — *on held-out repos at matched budget*. Routing target must be {no-review/self/same-family/cross-family/test-gen/reimplementation}, not single-model selection.

5. **Correctness endpoint discipline (vs cc01, cc09, cc11, cc12).** Primary metric = **final-patch correctness via hidden tests under matched budget**, plus regression rate. Detection precision / critique preference / checklist coverage / design rubric are at most secondary. This is the endpoint none of the neighbors share.

6. **Direct cc02 reproduction as a baseline.** Reproduce the Claude↔Codex single-pair 2×2 (including self-review) and show our framework adds value **beyond cc02's global "use the stronger model" rule** — i.e., the per-case router strictly dominates the stronger-model heuristic on held-out repos. If it does not, we are a code-specific replication of cc02.

7. **Context-separation confound control (vs cc08).** Include a same-family fresh-session reviewer so any cross-model gain is not merely cc08's context-separation effect.

---

## 5. Worst case: what our contribution gets downgraded to

- **If the multi-family complementarity interaction (Exp. 2) is weak:** we collapse to **"a code-specific, multi-pair replication of cc02"** — confirming that cross-model review is direction-dependent and rarely beats the stronger model solo. That headline is cc02's, already accepted at KDD'26. Contribution downgrades from *discovery* to *replication-at-scale*.
- **If cross-review loses to author-extra-compute at matched budget (Exp. 1):** the paper becomes a **negative result**: "for coding agents, a second model is usually not worth it vs more compute to the author" — which is cc05 (reasoning) + cc02 (code, vs stronger solo) + cc04 (theory) combined. Useful, but framed as *confirmatory*, and a reviewer can call it "cc05 ported to code review."
- **If the router (Exp. 4) fails to beat always-stronger-solo on held-out repos:** the defect-type correlation becomes a **descriptive post-hoc analysis**, and the routing contribution evaporates into "cc03/cc13 told us routing is possible; we didn't deliver a winning one."
- **Most likely realistic downgrade:** an **empirical/engineering instantiation** paper — "we operationalize cc04's budget-vs-correlation theory on repository patches with a defect-type-conditioned, budget-matched, held-out-validated review router" — accepted at a workshop/empirical-SE venue, not a conceptual-novelty headline at a top venue. The novelty lives entirely in the **conjunction + the correctness/budget endpoint + the working router**, and is fragile if any one of Exps. 1, 2, or 4 comes back null.

---

## 6. Recommendation: **NARROW**

**Not KILL, not PASS, not MERGE.** No single existing work establishes our *core* claim with our *unit of analysis and method*: cc02 — the closest — does the bidirectional 2×2 on one pair but has **no budget-matched author-extra-compute counterfactual, no defect-type error-correlation mechanism, and no pre-call held-out router**; cc04 has the mechanism only in scalar theory on generic agents; cc05 has budget-matching only for reasoning topology; cc03 routes generation not review. So **fatal_collision = false**. But the sweep materially burned our headline: cc02 has already published, on code, bidirectionally, that **cross-model review is not inherently better than the stronger model solo and is direction-dependent** — which is how reviewers will read our title. We must therefore **NARROW the contribution to the surviving conjunction** and lead with what no neighbor has: **(i) the strict budget-matched comparison against giving the same author more compute** (the counterfactual cc02 omits and the one most likely to be decisive), **(ii) a defect-type-conditioned author↔reviewer error-correlation model that *predicts* review lift**, and **(iii) a pre-call router over review actions validated on held-out repositories with a final-patch-correctness + regression-guard endpoint** that beats the cc02 "use the stronger model" heuristic per-case. Reframe the bidirectional matrix as *multi-family interaction decomposition* (separating reviewer-strength from complementarity), not as "first bidirectional study." Cite cc02/cc04/cc05/cc01/cc09 explicitly to scope out the forbidden generic claims. The paper survives **only as the conjunction**, and it is **conditional on Exps. 1, 2, and 4 returning positive** — if the budget-matched arm or the router comes back null, downgrade to a confirmatory/negative-result framing (Section 5) rather than withdrawing.
