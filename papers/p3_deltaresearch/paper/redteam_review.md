# Red-Team Review — p3_deltaresearch

**Paper:** *DeltaResearch: Typed Dependency-Graph Patching of Reports under Evidence-World Updates*
**Reviewer role:** adversarial Reviewer 2 + skeptical methodology/statistics reviewer
**Date:** 2026-06-25
**Verdict:** Major revision (as a *full method paper / venue submission*, this is currently a reject; as an honestly-scoped pilot it is salvageable).
**Score:** 4 / 10

---

## Summary

The paper studies a genuinely interesting setting — keeping a research report consistent when the *evidence world* changes (revision, retraction, conflict, temporal expiry, upstream recompute), not when an author edits prose. It contributes (a) a deterministic controlled-world generator with programmatic gold A/U/N/C, (b) a typed claim-evidence dependency-graph analyzer + constrained patcher, and (c) a 72-episode pilot across two subscription-CLI agent families (Claude, "Codex/gpt-5.5"). The headline empirical finding is honest and real: both agents recover only ~1/3 of obligated downstream updates (ACR 0.33–0.39) while leaving everything else untouched (UCP ~1.0), and handing them the affected set does not help (an honest null on H3).

The draft is unusually candid: it cleanly separates the deterministic infrastructure result (P3-C0) from the real-agent findings, flags H_DIVERGE as untested, retains the H3 negative, discloses no-CIs/pilot-scale/synthetic-only/Layer-B-unrun, and hedges unverified neighbors as "pending Director verification." I credit that honesty and it is the reason this is a major-revision rather than a flat reject.

However, the **central method claim is currently undemonstrated**, and the abstract/contributions lead with three numbers (typed-graph 1.0/1.0, full-regen 0.0, flat ledger 0.13) that are **tautological consequences of the construction**, not results. The one surviving novelty the prior-art sweep allows (a typed-graph-driven agentic patch that beats a flat ledger and full regen *as real systems*, on real versioned evidence, with a non-cosmetic evidence-vs-author distinction) is exactly what is *not* shown.

---

## Fatal weaknesses

**F1. The "deterministic method" reaching ACR = UCP = 1.0 is oracle-fed, and the whole deterministic frontier is tautological by construction.**
Verified in code: `baselines.typed_graph_patch` calls `oracle_patcher`, which fills `patch.new_values` directly from `world.post_values` (the gold), and its predicted affected set is literally equal to `gold_A` (`typed_graph predicted affected == gold_A → True`). So the paper's marquee "method" performs **no actual re-derivation** — the very step the draft identifies as the agents' bottleneck (§6.3) — it reads the gold values. ACR/UCP/calculation_correctness = 1.0 is therefore guaranteed, not earned. Worse, *all* deterministic arms (`typed_graph`, `full_regen`, `naive_ledger`, `oracle`) are fed gold values; they differ only in which claims they *mark* edited. The "deterministic frontier" of §6.1 is thus a set-membership exercise on **one hand-built 10-claim topology** whose typed edges (`_base_edges`) were authored to mirror the gold formulas (`_recompute`). Contribution #4 ("a deterministic typed-graph + constrained-patch method that attains ACR = UCP = 1.0 … Pareto-dominating …") is presented as a finding but is a unit test. The claim registry itself names this attack ("gold == method (tautology)"); the "separate code path" defense is weak because both code paths encode the *same* hand-specified dependency structure.

**F2. The kill-gate (H_DIVERGE) cannot fail as implemented.**
`diverge.AUTHOR_EDIT_EDGES = {DERIVED_FROM, QUALIFIED_BY}` deliberately *excludes* `NUMERIC_DEPENDENCY` and `TEMPORAL_DEPENDENCY`, while the evidence-world analyzer follows all propagating edges. Divergence is therefore manufactured by the edge-type partition (`divergence = 0.5, missed_by_author = ['cProj']` on the temporal case). The contract makes H_DIVERGE a *do-not-proceed* gate ("if not, the framing is cosmetic"), but a gate that is rigged to pass by definition cannot discharge that risk. The draft is honest that H_DIVERGE is "not quantified" — but even when quantified with this harness it will be vacuous. A real author editing "the current rate" in prose would plausibly know the projection depends on it; the strawman author-edit model assumes otherwise.

**F3. Strawman deterministic baselines; the dramatic 0.0 / 0.13 are simulation artifacts.**
`full_regeneration_patch` marks `set(ASSERTED)` as edited, so UCP = 0.0 by construction — yet it writes the *correct* gold values. UCP penalizes *touching* a claim, not *changing* it (`ucp = |U \ edited|/|U|`), so a full regeneration that re-emits an identical correct sentence is scored as "destroying every preserved claim." That is not what real regeneration does — Mr.DRE's *measured* regression is 16–27%, not 100%. Likewise `naive_ledger` ACR = 0.13 follows from the topology (e.g., no claim directly cites the temporal evidence, so the flat ledger flags nothing on temporal deltas). These are hand-coded foils, not run systems; the abstract's "against full regeneration (UCP = 0.0)… and a flat ledger (ACR = 0.13)" reads as empirical comparison but is definitional.

**F4. Scale and design do not support the empirical claims.**
"18 controlled worlds" = 6 effectful delta types × 3 seeds on a **single fixed topology**; the seeds only reroll random numbers, not structure. The cascade is always the same arithmetic chain (cA/cB → cTotal/cMargin/cShare/cIndex; cCur → cProj), with |A| ∈ {2,4,5}. Effective structural diversity ≈ 6 scenarios. The agents are stochastic but each condition is a **single draw** (no repeats → within-condition variance unmeasured), there are **no CIs**, **no held-out**, **no per-delta-type breakdown** (the 0.33–0.39 average hides heterogeneity; the ledger shows ACR = 1.0 on some numeric_revision worlds), and the models are **product CLIs, version-unpinned** (`model_id = "claude:claude-cli" / "codex:codex-cli"` — the "gpt-5.5" identity is asserted, never captured). "Reproduced across two independent families" overstates robustness from n = 18 with a shared, conservatism-inducing prompt.

**F5. The surviving contribution is undemonstrated, and its only real-agent test is a null.**
Per the novelty sweep, the *only* defensible novelty is the **method** (typed-graph structure helping a real agent beat a flat-ledger/full-regen agent) plus real-evidence transfer. In the pilot, the deterministic "win over flat ledger" is tautological (F1), and the meaningful version — does typed structure help a real agent? — is the H3 **honest null**. So the central claim is simultaneously (a) trivially true deterministically and (b) not shown for any real system. The contract's own kill condition ("typed graph does not beat flat ledger → downgrade to dataset note") is, in the only non-tautological reading available, currently *triggered*.

---

## Overclaims (sentence-level, vs the evidence note + code)

1. **Abstract / §6.1:** "the deterministic typed-graph analysis plus constrained patch instead reaches ACR = UCP = 1.0, against full regeneration (UCP = 0.0) … and a flat claim-citation ledger (ACR = 0.13)." → Construction-determined; the method is oracle-fed (F1); 0.0 is a touch-penalty artifact (F3). Not a comparative result.
2. **Intro contribution #4:** "A deterministic typed-graph + constrained-patch method that attains ACR = UCP = 1.0 … Pareto-dominating …" → It re-derives nothing; it reads `world.post_values`. The claimed contribution (re-derivation under constraint) is not exercised.
3. **§6.1:** "full regeneration … rewrites every preserved claim (UCP = 0.00) — the spurious-revision failure" and "Only the typed graph is Pareto-dominant." → True only among three hand-coded strategies on one topology; "destroys every preserved claim" contradicts the cited Mr.DRE magnitude (16–27%).
4. **Abstract / Intro:** "reproduced across two independent model families" / "two independent real agent families." → n = 18, single draw each, shared prompt, unpinned models → directional agreement, not reproduction/robustness.
5. **Abstract:** "preserving unaffected claims (Unaffected-Claim Preservation ~1.0)" presented as a virtue. → UCP ~1.0 is the *mechanical dual* of conservative under-editing (a do-nothing agent scores UCP = 1.0); for the real agents UCP is pinned at ceiling, so the "joint pair" collapses to ACR alone. Ceiling confound not acknowledged.
6. **§6.2:** "the agents behave like a conservative near-flat-ledger." → Agents (0.33–0.39) are ~2.6–3× the flat ledger (0.13); "near-flat-ledger" understates and is internally inconsistent with the paper's own contrast.
7. **§6.3:** "the bottleneck is not identifying which claims are affected — the agents are told and still under-edit." → The hint is phrased "**possibly** affected" and sits next to "Claims that are not affected MUST be left unchanged," i.e., a weak, conservatism-biased hint. Concluding "structure handed to the agent does not help" is over-generalized from one under-powered hint design (could be a prompt artifact).
8. **Abstract:** "(Claude and Codex/gpt-5.5)." → Model build not recorded in the ledger; provenance unverifiable.

I confirmed the *quantitative* numbers in the draft faithfully match the ledger (Claude naive 0.389→0.39, Claude+hint 0.333, Codex naive 0.344→0.34, Codex+hint 0.333; UCP 1.00/1.00/0.99/1.00; 72 SUCCESS episodes, 36+36). The problem is **interpretation and framing**, not number-fabrication.

---

## Citation integrity

`citation_integrity_ok = FALSE` (borderline, not fraud). The two **load-bearing factual** attributions are correct: EditPropBench ("~30% missed", `editpropbench2026`) and Mr.DRE ("16–27% regression", `mrdre2026`) are both verified in `related_work.csv` and used accurately. The unverified neighbors (FRUIT, AAR, ChainEdit, RippleEdits, RAMDocs, evolveQA) are appropriately hedged as "[unverified — pending Director verification]" — good practice. **But** the draft also `\cite`s two sources *as established methodological precedent* that are outside this paper's verified set and absent from its own `related_work.csv` / novelty sweep: `cc02xiang2026` ("Cross-Model LLM Code Review", a KDD'26 workshop / ResearchGate item — a **cross-domain** code-review paper pressed into service to justify two-family *report-revision* evaluation) and `agentassay2026` (regression-testing for agent workflows). They exist in `program/references.bib` but were not verified for this paper, and one has weak provenance and tangential relevance. Trim or properly verify both before they are cited as fact.

---

## Threats to validity / alternative explanations

- **Conflation of infra and model findings.** The draft mostly separates them, but the abstract and contributions still *lead* with the deterministic 1.0/0.0/0.13 (P3-C0/H4) as if co-equal results. A skimming reader will read "our method gets 1.0" as a model result. Foreground the real-agent ACR and demote the deterministic table to "consistency check."
- **Shared-prompt confound.** Both families see the same prompt that explicitly instructs conservatism ("not affected MUST be left unchanged") and a "possibly affected" hint. Cross-family agreement may reflect the prompt, not a model property. No temperature/prompt/sampling robustness.
- **Ceiling confound.** UCP ceiling (F4/Overclaim 5) means the only informative axis for agents is ACR; the joint-metric selling point adds nothing for the real arms.
- **H3 mechanism unprobed.** If told the affected set, an obedient agent would echo it into `edited` and reach ACR ≈ 1.0; that it stays at 0.33 is interesting but unexplained — could be hint phrasing, JSON formatting, or genuine refusal. No error decomposition (identify vs. list vs. recompute).
- **Construction leakage.** Because gold, analyzer, baselines, and the divergence harness all derive from one hand-authored dependency structure, *every* deterministic claim is a statement about the author's own consistency, not about the world.

---

## Required for acceptance (minimum concrete work)

1. **De-oracle the method.** Implement the typed-graph + constrained-patch as an **end-to-end pipeline that actually recomputes** values (not reading `world.post_values`) and, ideally, drives a real agent for the edit/derivation step; report its ACR/UCP/calculation_correctness as a *system*. This is the load-bearing experiment and is currently missing.
2. **Real, run baselines.** Replace hand-coded `full_regen`/`flat_ledger` with **prompted agent baselines** (a real "regenerate the report" agent; a real "fix only the cited claim" agent) so the frontier reflects systems, not constructions. Fix UCP so it penalizes *value change*, not mere touching (or report both).
3. **Make H_DIVERGE falsifiable.** Test divergence with a real author-edit reformulation (or human/agent author edits), not a hand-partitioned edge set that excludes numeric/temporal by fiat. The gate must be able to fail.
4. **Scale + statistics.** Multiple report topologies (vary depth, breadth, |A|/|U|, non-arithmetic derivations), longer reports, more seeds; **repeated agent draws** per condition; world-clustered bootstrap CIs; **per-delta-type breakdown**; pre-registered analysis honored (the analysis_plan mixed model is not yet run). Version-pin / record exact model builds.
5. **Proper structure-help ablation (re-test H3).** Authoritative hint ("these MUST change + recompute"), plan-then-edit scaffolds, explicit recompute tool; plus an error decomposition localizing identify vs. list vs. recompute failures, before concluding structure cannot help an agent.
6. **Run Layer B (real versioned evidence).** Transfer (H5) is the novelty sweep's external-validity requirement and is entirely unrun.
7. **Head-to-head vs EditPropBench protocol** on the same evidence-world tasks, to demonstrate non-reducibility (the sweep's mandatory experiment).
8. **Citations:** verify or remove `cc02xiang2026` and `agentassay2026`; keep the "pending verification" hedges until the Director pass completes.

---

## Strongest surviving contribution

The **honest empirical negative**: two real subscription-CLI agents, given an evidence-world delta *with the derivation rules stated in-prompt*, recover only ~1/3 of obligated downstream (derived/temporal/recomputed) updates and leave the rest untouched, and **handing them the affected set does not close the gap** — localizing the failure to edit/re-derivation rather than identification. Paired with a clean, released controlled-world harness and a pre-registered joint (ACR, UCP) objective, this is a credible, well-instrumented pilot/workshop finding (the ledger reproduces the draft's numbers exactly). It is *not* the method paper the title and contributions advertise.

## Novelty

`novelty_still_holds = TRUE` but *undemonstrated*. The sweep correctly finds no fatal single-paper collision: EditPropBench owns the dual metric + ~30% headline, Mr.DRE owns the phenomenon, FRUIT the base task, AAR/ChainEdit the graph+audit/propagation machinery. The narrowed survivor (typed-graph agentic patch beating a flat ledger + full regen, on an evidence-world delta, with real-evidence transfer and a non-cosmetic divergence) is real *as a claim* — but in this pilot it is shown only tautologically (deterministic) or refuted (the H3 null). Until F1/F2/F5 are addressed, a reviewer can fairly say the contribution has not yet been exhibited.

---

## What it honestly is right now (one paragraph)

A well-engineered, unusually candid pilot harness with **one genuine empirical negative** — real CLI agents miss ~2/3 of obligated downstream updates on evidence-world deltas, and a (gold) affected-set hint doesn't help — measured on a **single fixed 10-claim arithmetic-cascade topology**, n = 18, one draw per condition, two version-unpinned product models, no CIs. Around that sits a **deterministic infrastructure result that is tautological by construction**: the typed analyzer matches a gold that shares its own hand-authored dependency structure, its "patch" is fed gold values, and it beats two intentionally-crippled strawman baselines whose 0.0/0.13 scores are definitional artifacts. The surviving novelty — a typed-graph-driven agentic patch that beats a flat ledger and full regeneration *as real systems*, validated on real versioned evidence, with an evidence-vs-author divergence that can actually fail — is precisely what is **not yet demonstrated** (the only real-agent structure test is a null, the kill-gate is unquantified and, as built, cannot fail, and Layer B is unrun). So it is today a promising **workshop-tier pilot + released dataset/harness note**, honestly labeled as such in its limitations but **over-framed in its abstract and contributions** as a method paper. Reward the honesty; do not accept the framing until the method is de-oracled and run.
