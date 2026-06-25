# DeltaResearch — Novelty Attack (adversarial prosecution)

Role: Novelty Prosecutor. Mandate: kill the novelty of **p3_deltaresearch — DeltaResearch: Selective Revision of Deep-Research Reports under Evidence Updates** if it can honestly be killed.

Central claim under attack: *When underlying evidence is locally updated/corrected/retracted/conflicting, deep-research agents miss stale conclusions OR damage large amounts of correct content. Representing the report as a typed claim-evidence dependency graph and generating a constrained minimal patch improves BOTH "change what must change" and "preserve what must not" (incl. multi-hop derived/temporal/computed claims), while maintaining citation + calculation validity and honestly representing conflict.*

Sweep date: 2026-06-25. Every arXiv work below was fetched/verified this session or in the prior matrix. New this session: EditPropBench re-verified head-on (arXiv abstract fetched), ClaimFlow (2603.16073) checked and dismissed, EvoEdit (2512.04545) checked and dismissed as parameter editing, and a "Living Systematic Review Engine" preprint surfaced as a fresh reduction angle.

**Bottom line up front:** No single existing work establishes our central claim with our unit of analysis (deep-research report claims under an *evidence-world* delta) AND our method (typed dependency graph + constrained patch + audit driving an agent). So there is **no fatal single-paper collision.** But the two highest-collision papers have *already independently claimed the two most marketable halves of the contribution*: EditPropBench owns the **measurement/benchmark** half (dual change/preserve metric + the "~30% of cascade updates missed" headline), and Mr.DRE owns the **phenomenon** half (DR agents regress 16-27% on non-target content/citations during revision). What survives is an *assembly + a method*, not a discovery. The paper must NARROW accordingly or it is reducible to "EditPropBench, but for deep-research reports and an evidence-world trigger."

---

## 1. The 10 works most likely to make a reviewer say "already done" (verified URLs)

Ordered by "already done" damage, highest first.

1. **EditPropBench: Measuring Factual Edit Propagation in Scientific Manuscripts** — https://arxiv.org/abs/2605.02083 (Garvin Kruthof, 2026-05-03, verified, re-fetched this session). The paper a reviewer cites to say "the benchmark already exists."
2. **Beyond Single-shot Writing: Deep Research Agents are Unreliable at Multi-turn Report Revision (Mr.DRE)** — https://arxiv.org/abs/2601.13217 (2026-01-19, verified anchor). The paper a reviewer cites to say "the finding already exists."
3. **FRUIT: Faithfully Reflecting Updated Information in Text** — https://arxiv.org/abs/2112.08634 (NAACL 2022, verified). The paper a reviewer cites to say "update-text-given-new-evidence is a 2022 task."
4. **From Fluent to Verifiable: Claim-Level Auditability for Deep Research Agents (AAR)** — https://arxiv.org/abs/2602.13855 (2026, verified). "The claim-evidence/provenance graph + audit trail for DR agents already exists."
5. **DeepFact: Co-Evolving Benchmarks and Agents for Deep Research Factuality** — https://arxiv.org/abs/2603.05912 (2026, verified). "The versioned/auditable DR-report claim benchmark already exists."
6. **Evaluating the Ripple Effects of Knowledge Editing (RippleEdits)** — https://arxiv.org/abs/2307.12976 (TACL 2024, verified). "Derived-fact-must-change + locality (preserve-unrelated) already named and measured."
7. **ChainEdit: Propagating Ripple Effects through Logical Rule-Guided Chains** — https://arxiv.org/abs/2507.08427 (ACL 2025, verified). "Typed-graph/rule-guided propagation of an update to dependent facts already exists as a method."
8. **When Facts Change: Probing LLMs on Evolving Knowledge with evolveQA** — https://arxiv.org/abs/2510.19172 (2025, verified). "Real timestamped evidence evolution -> staleness already benchmarked."
9. **Retrieval-Augmented Generation with Conflicting Evidence (RAMDocs / MADAM-RAG)** — https://arxiv.org/abs/2504.13079 (COLM 2025, verified). "Honest handling of conflicting evidence already exists."
10. **A Living Systematic Review Engine: LLM-Automated Evidence Surveillance Validated Against a Published Meta-Analysis of Statins for Sepsis** — https://www.researchsquare.com/article/rs-9308492/v1 (Research Square preprint, 2026; **partial verification**: title + URL corroborated across two independent searches, abstract details from search snippet, full text not fetched; non-peer-reviewed, medical/workflow). The paper a reviewer cites to say "this is just living-systematic-review automation: evidence surveillance that updates a synthesis and notes when conclusions change vs stay."

Honorable mentions (lower "already done" risk, still cite to avoid being scooped on a sub-dimension): **Generation-Time vs. Post-hoc Citation** (https://arxiv.org/abs/2509.21557), **CiteCheck** (https://arxiv.org/abs/2605.27700), and the temporal free-text knowledge-editing cluster **EvoEdit** (https://arxiv.org/abs/2512.04545) + MQuAKE-style multi-hop editing. **ClaimFlow** (https://arxiv.org/abs/2603.16073) shares the typed claim-relation vocabulary (supported/extended/qualified/refuted) but only *traces* claim evolution across the literature; it does not revise a report, so it is a vocabulary neighbor, not a collision.

---

## 2. Per-work itemized overlap with our claim

### (1) EditPropBench — THE collision (re-verified this session)
**Overlaps (what they already have):**
- The exact gold-label *structure* we planned: direct-target / required-downstream / protected-unrelated, at sentence level, over a controlled fact graph.
- A **dual-sided metric**: Edit-Ripple Adherence (ERA, "fraction of required downstream updates correctly revised") **plus** preservation of protected text. This is essentially our "change A / preserve U" endpoint pair.
- The **headline finding we wanted to claim**: "even the strongest editor misses roughly 30% of required cascade updates" (ERA 0.148-0.705). Our RQ1 "local updates cause large stale residual or unaffected drift" is, at the measurement level, already demonstrated.
- The conceptual thesis: "a local factual edit creates non-local revision obligations while unrelated text must be preserved" — verbatim our framing minus the word "evidence."

**Does NOT have (our surviving delta):** input is an author-supplied **internal manuscript edit**, not an **external evidence-world delta**; no retraction / source-conflict / new-more-authoritative-source / temporal-validity / upstream-recompute / evidence-deletion-but-still-supported taxonomy; no conflict/uncertainty (C) set; no citation- or calculation-validity maintenance; **synthetic-only**, no real versioned evidence; it is a **benchmark with editing protocols and adversarial probes, not a typed-edge dependency-graph method**; **no deep-research agent in the loop and no audit trail / patch object.**

### (2) Mr.DRE — phenomenon collision (verified anchor)
**Overlaps:** same change-target-vs-preserve-non-target tension on **deep-research reports**; quantifies regression (16-27% of prior content + citation quality) under multi-turn revision; same "agents fail to preserve prior edits" observation that motivates our preserve-penalty.
**Does NOT have:** revision is driven by **user writing feedback**, not an evidence-world delta; no gold affected/unaffected/new/conflicting claim sets tied to an evidence change; no typed dependency graph; no claim-level patch; no metric jointly penalizing stale + spurious revision; no temporal/conflict/citation-validity machinery.

### (3) FRUIT — original task collision
**Overlaps:** the *task family* "update an existing document so it faithfully reflects new evidence," with a real dataset (FRUIT-WIKI, 170K pairs + 914 gold) and an editing model (EDIT5). The "edits must be supported by the evidence" constraint overlaps our citation-validity requirement.
**Does NOT have:** no claim-level dependency graph; no multi-hop derived/computed/temporal claims; **no preserve-penalty** — UpdateROUGE scores only changed sentences, so spurious revision is invisible; no retraction/conflict taxonomy; pre-DR-agent single-model generation, no patch+audit.

### (4) AAR (From Fluent to Verifiable) — method-machinery collision
**Overlaps:** the **claim-evidence / provenance graph + audit-trail** machinery as a first-class object for DR agents; claim->passage support links; contradiction transparency. This is the closest prior art to our "typed claim-evidence graph + audit."
**Does NOT have:** targets **generation-time** auditability/provenance, not selective **revision under an evidence delta**; no W_t -> W_{t+1} update; no gold affected/unaffected sets; no patch generation; no change-vs-preserve metric; no temporal-validity/recompute reasoning. Danger: a reviewer can say "the graph+audit is AAR; you only added an update step."

### (5) DeepFact — versioned-benchmark + DR-object collision
**Overlaps:** same deep-research-report object; a **versioned, auditable** claim benchmark (Audit-then-Score, revisable labels) — overlaps our "audit trail" and "versioned worlds" selling points.
**Does NOT have:** it **verifies/scores claim factuality and revises BENCHMARK LABELS**, it does not revise a *report* under an evidence delta; no evidence-delta -> affected-claim mapping; no patch; no preserve-vs-change metric on report content.

### (6) RippleEdits — concept collision (derived + locality)
**Overlaps:** the conceptual ancestor of "logically-derived facts must also change" plus **locality** (preserve unrelated) — i.e., our affected-derived-claim recall + unaffected preservation, named and measured first.
**Does NOT have:** **model-parameter** editing evaluated via QA, not report revision; no evidence world, citations, retraction, conflict, temporal validity, patch, or prose-preservation penalty.

### (7) ChainEdit — method-analogue collision
**Overlaps:** uses a **graph of typed/logical relations to propagate an update to dependent facts** — the structural core of our typed dependency graph, as a method.
**Does NOT have:** edits **model parameters** not a report; QA evaluation; no document, evidence world, citations, retraction, conflict, temporal validity, or audit. Danger: "your propagation method is ChainEdit moved from parameters to text."

### (8) evolveQA — real-temporal-evidence collision
**Overlaps:** **real timestamped evidence evolution** (AWS/Azure/WHO) — directly adjacent to our Layer-B real versioned worlds; quantifies staleness (up to 31% drop).
**Does NOT have:** unit is **QA tied to model cutoff**; it *measures* parametric staleness, does not *revise* a report given an evidence delta; no dependency graph, patch, or citation/calculation validity.

### (9) RAMDocs / MADAM-RAG — conflict-handling collision
**Overlaps:** honest handling of **conflicting/ambiguous/noisy evidence** — our C set sub-problem.
**Does NOT have:** single-turn **QA over a static conflict set**, not revision of an existing report; no temporal delta; no affected/unaffected report-claim labels; no preservation metric.

### (10) Living Systematic Review Engine — reduction collision (preprint, partial verification)
**Overlaps:** the *spirit* of our whole pitch in a real domain: LLM-automated **evidence surveillance** over a living synthesis that ingests new studies and reports when conclusions change ("newly statistically significant in 2 reviews, negated significance in 1") vs stay the same ("pooled estimate updated without changing the overall clinical conclusion"). This is "evidence update -> which conclusions must change vs stay" demonstrated end-to-end.
**Does NOT have:** it re-runs **screening/extraction/meta-analysis**, it does not revise long-form **prose** with a typed claim graph; no gold affected/unaffected claim set; no claim-level patch; no preserve-penalty metric; no general benchmark; medical/workflow, non-peer-reviewed. Danger: "isn't this just a generic version of living systematic reviews?"

---

## 3. Which specific claims we can NO LONGER make

These claims are now **owned by prior work** and must be deleted or explicitly attributed; making them invites a desk-level "already done":

1. ~~"We are the first to show editors/agents miss ~a third of obligated downstream updates while damaging protected text, measured by a dual change/preserve metric."~~ **Owned by EditPropBench** (ERA + protected-text, ~30% miss). At most we may claim this *for the evidence-world setting on DR reports*, and only after a head-to-head.
2. ~~"We are the first to formalize 'a local factual change creates non-local obligated revisions with protected unrelated text' using gold target/required-downstream/protected labels."~~ **Owned by EditPropBench.**
3. ~~"We discover that deep-research agents regress on non-target content and citation quality during revision."~~ **Owned by Mr.DRE** (16-27%).
4. ~~"We introduce the task of updating an existing document to faithfully reflect new evidence."~~ **Owned by FRUIT** (2022).
5. ~~"We introduce a claim-evidence / provenance graph with an audit trail for deep-research agents."~~ **Owned by AAR**; the graph+audit is not novel on its own.
6. ~~"We introduce versioned, auditable benchmarking for deep-research-report claims."~~ **Owned by DeepFact.**
7. ~~"We introduce the requirement that logically-derived/multi-hop facts must also change, with locality preservation."~~ **Owned by RippleEdits**; the **graph/rule-guided propagation method** for this is **owned by ChainEdit** (in parameter space).
8. ~~"We are the first to benchmark staleness from real timestamped evolving evidence."~~ **Owned by evolveQA.**
9. ~~"We introduce honest handling of conflicting evidence (a conflict/uncertainty set)."~~ **Owned by RAMDocs** (as a QA capability).
10. ~~"The contribution is a dual-sided metric that penalizes both stale and spurious revision."~~ The dual-sided idea is **owned by EditPropBench**; only the *evidence-world-specific components* (temporal-validity correctness, citation-validity maintenance, computed-claim re-calculation, honest-C scoring) can be claimed as additions.
11. ~~"We measure diff size / minimal edits as a quality signal."~~ Explicitly out per our own novelty boundary, and reductive.

**What we MAY still claim (the narrowed novelty):** (a) the **evidence-world delta taxonomy** as the trigger (numeric revision, date/validity change, **source retraction**, **new more-authoritative source**, **two-source conflict**, definition change, **upstream-fact-triggered recompute**, evidence-deletion-but-still-supported) mapped to gold **A/U/N/C** claim sets on a DR report; (b) a **typed-edge dependency-graph METHOD** (supports/derives/qualifies/contradicts/temporal-validity) that drives a **deep-research agent** to emit a **constrained claim-level patch + audit trail**, and that *beats a flat claim-citation ledger and full-regeneration*; (c) joint maintenance of **citation + calculation validity** and **temporal validity** through the update; (d) **real versioned public evidence (Layer B)** paired with controlled worlds for report revision. The novelty is the *assembly + the method*, contingent on the method ablations winning.

---

## 4. Which experiments we MUST add to prove the difference

Without these, the paper is reducible. Each targets a specific "already done."

1. **Head-to-head vs EditPropBench (mandatory, kills/saves the paper).** Re-implement ERA + protected-text on our evidence-world tasks. Then show **non-reducibility**: that evidence-world deltas (retraction, two-source conflict, temporal-validity expiry, upstream recompute) induce failure modes that an EditPropBench-style author-edit *cannot encode* (there is no "author edit" for "a source got retracted" or "two sources now conflict"). Concretely: take a fixed report and a fixed intended change; deliver it as (a) an explicit author-style manuscript edit vs (b) an evidence-world delta, and show agent behavior diverges and that only the typed-graph method recovers (b). If behavior does NOT diverge, the evidence-world framing is cosmetic and the paper dies.
2. **Method ablation ladder (RQ2 -> RQ3, isolates us from AAR/ChainEdit/FRUIT).** No-structure "update this report" prompt -> flat claim-citation ledger (AAR-style provenance) -> typed dependency graph. Must show typed edges add **affected-claim recall AND derived/temporal/computed-claim correctness** *beyond* the flat ledger. If the flat ledger ties the typed graph, the method (our core method novelty over AAR) is dead and we are a benchmark only.
3. **Patch vs full-regeneration vs "revise this report" (isolates us from Mr.DRE/FRUIT).** Show the constrained patch reduces **unaffected-claim drift** at equal-or-better affected recall, with lower token/latency. This is the only way to claim the patch+audit is load-bearing rather than a wrapper; Mr.DRE already showed plain revision regresses.
4. **Conflict (C) + temporal-validity + computed-claim endpoints (isolates us from EditPropBench/RAMDocs/evolveQA).** Dedicated subsets with their own metrics: honest-C flag rate (vs RAMDocs QA), validity-interval adherence (vs evolveQA QA), recomputation correctness for derived/computed claims, and citation-validity re-check (vs CiteCheck detection-only). These are the components EditPropBench provably lacks; they must move the headline number, not just appear in an appendix.
5. **Real versioned evidence (Layer B) external validity (isolates us from EditPropBench synthetic-only + backs H5).** Show gains transfer from controlled worlds to real version pairs (software docs/release notes, government data vintages). EditPropBench is synthetic-only; if our method only works on controlled worlds we have no advantage over it.
6. **Living-review reduction rebuttal (isolates us from the LSR engine).** Demonstrate that DeltaResearch operates at **claim-prose level with a preserve penalty** and produces an auditable claim-level patch, not a re-run meta-analysis — ideally on at least one report where the synthesis conclusion is unchanged but specific prose claims must still change (and vice versa), which a "re-run the pooled estimate" pipeline cannot represent.

---

## 5. Worst case: what our contribution gets downgraded to

If the method ablations (Experiments 2 and 3) fail — i.e., the typed dependency graph does **not** beat a flat claim-citation ledger, and the constrained patch does **not** beat full regeneration on the preserve/change tradeoff — then the central claim's *method* half collapses and the paper degrades to:

> **"EditPropBench transported from synthetic manuscripts to deep-research reports, re-triggered by an evidence-world delta instead of an author edit, with an extended update taxonomy (retraction/conflict/temporal) and a real-versioned-evidence layer."**

That is a **dataset/benchmark contribution** (an evidence-world, DR-report variant of EditPropBench + FRUIT), whose *phenomenon* (agents miss/damage during revision) was already shown by Mr.DRE and whose *dual metric and ~30%-miss headline* were already shown by EditPropBench. Realistic downgrade: a **workshop/Findings-tier "DeltaBench" dataset note**, not a method paper, with reviewers writing "incremental recombination of EditPropBench + Mr.DRE + FRUIT." If, additionally, the evidence-world vs author-edit distinction shows **no behavioral divergence** (Experiment 1 fails), even the dataset framing is reducible to "EditPropBench with new update types," and the paper should not be submitted as-is.

If the ablations succeed, the floor rises to a legitimate **method + benchmark** paper whose defensible novelty is the typed-graph-driven agentic patch under an evidence-world delta — but the framing must lead with the method and the evidence-world taxonomy, and must concede the measurement/phenomenon halves to EditPropBench/Mr.DRE up front.

---

## 6. Recommendation: NARROW

**NARROW** (one-paragraph justification): There is no fatal single-paper collision — no existing work revises a *deep-research report* under an *evidence-world* delta with a typed dependency-graph method, claim-level patch, audit trail, and joint stale+spurious metric across retraction/conflict/temporal/recompute update types over both controlled and real versioned evidence. However, the two highest-collision papers have each independently captured a marketable half of the contribution: **EditPropBench** owns the change/preserve dual-metric benchmark and the "~30% of obligated updates missed" headline, and **Mr.DRE** owns the "DR agents regress on non-target content/citations during revision" phenomenon; **FRUIT** owns the base task, **AAR/ChainEdit** own the graph+audit and graph-guided-propagation machinery, and the **LSR engine** is a credible "you reinvented living systematic reviews" reduction. The paper therefore cannot be sold as a *discovery* or as a *benchmark-first* contribution; it must be NARROWED to lead with (a) the evidence-world delta taxonomy mapped to gold A/U/N/C claim sets and (b) a typed-graph agentic patch+audit method that *demonstrably beats a flat claim-citation ledger and full regeneration*, validated on (c) real versioned evidence, with the EditPropBench/Mr.DRE measurement-and-phenomenon halves explicitly conceded. The recommendation drops to **MERGE** (fold into a DeltaBench dataset note, possibly alongside EditPropBench-style positioning) if the method ablations (Experiments 2-3) do not win, and the paper should not proceed if Experiment 1 shows no behavioral divergence between an evidence-world delta and an equivalent author edit.

---

### Verification log (this session)
- EditPropBench (2605.02083): arXiv abstract fetched; confirmed benchmark-only, internal manuscript edit, synthetic, ERA + protected-text, ~30% miss, no agent/method/audit/temporal/conflict/citation. **verified.**
- ClaimFlow (2603.16073): fetched; claim-evolution tracing across literature, no report revision/patch/graph-method. **verified, not a collision.**
- EvoEdit (2512.04545): fetched; parameter (free-text) knowledge editing, not document revision. **verified, cluster only.**
- Living Systematic Review Engine (rs-9308492): title + URL corroborated across two searches; abstract details from search snippet; full text not fetched. **partial verification — flagged.**
- All other entries carried from related_work.csv where verified=true.
