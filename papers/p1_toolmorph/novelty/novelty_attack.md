# ToolMorph (p1_toolmorph) — Novelty Attack (Adversarial Prosecution)

Prepared 2026-06-25 by the Novelty Prosecutor. Mandate: kill the paper's novelty if it can honestly be killed. Every URL below was fetched and verified during this audit (abstracts read verbatim where load-bearing). New papers added beyond the Scout's matrix: **2602.01611 (PIPE)** and **2603.13173 (Semantic Invariance in Agentic AI)** — both materially damaging. Two papers the Scout flagged as unverified (2605.26165, 2510.03992) were fetched and are **non-collisions**.

**Our central claim (verbatim restatement).** With the underlying tool STATE TRANSITION held identical, changing only the model-visible interface representation significantly changes agent success, error types, cost, and even model RANKING; a semantic normalization layer that does NOT depend on transform labels and works on held-out tools/transforms reduces this sensitivity.

**Bottom line up front.** The Scout's central defensive recommendation — "lead with EQ+META as an inseparable, unoccupied combination" — is **broken**. A single February-2026 paper (PIPE, 2602.01611) already rewrites the model-visible interface while keeping execution behavior/state identical and measures a paired original-vs-rewritten gap across many models. That is EQ+META. It does NOT, however, do the normalization remedy, a ranking-reversal characterization, a formal state-transition-equivalence definition, or a broad transform family. So the phenomenon side of our claim is largely pre-empted; the **fix** (label-free normal form transferring to unseen transforms) is what genuinely survives. Recommendation: **NARROW**.

---

## 1. The 10 works most likely to make a reviewer say "already done" (verified URLs)

Ranked by damage to our central claim, not by topical similarity.

1. **PIPE — "What Do Agents Learn from Trajectory-SFT: Semantics or Interfaces?"** (Gu et al., 2026) — https://arxiv.org/abs/2602.01611 — **CRITICAL / new.** Occupies EQ+META.
2. **ReliabilityBench** (Gupta, 2026) — https://arxiv.org/abs/2601.06112 — **HIGH.** Names "metamorphic relations" + scores by end-state equivalence.
3. **Schema First Tool APIs** (Sigdel & Baral, 2026) — https://arxiv.org/abs/2603.13404 — **HIGH.** Holds tool semantics/information content constant, varies only the interface spec.
4. **Semantic Invariance in Agentic AI** (de Zarzà, de Curtò, Cabot, Manzoni, Calafate, 2026) — https://arxiv.org/abs/2603.13173 — **HIGH / new.** Metamorphic + 8 semantics-preserving transforms on agents + an explicit model-rank inversion.
5. **Natural Language Tools** (Johnson, Pain, West, 2025) — https://arxiv.org/abs/2510.14453 — **HIGH.** Interface representation swap (JSON→NL) reorders models; open-weight surpasses closed-weight.
6. **TSCG: Deterministic Tool-Schema Compilation** (Sakizli, 2026; verified anchor) — https://arxiv.org/abs/2605.04107 — **HIGH.** Deterministic, label-free transform of tool interface representation.
7. **Learning to Rewrite Tool Descriptions** (Guo, Dong, Gao, Das, 2026) — https://arxiv.org/abs/2602.20426 — **HIGH.** Automatic interface rewriter that transfers to unseen tools without per-tool traces.
8. **When Benchmarks are Targets** (Alzahrani et al., 2024) — https://arxiv.org/abs/2402.01781 — **MEDIUM.** Canonical "format changes ranking" result (up to 8 positions).
9. **AgentAtlas** (Mazaheri & Mazaheri, 2026) — https://arxiv.org/abs/2605.20530 — **MEDIUM.** Methodology/prompt-format choices reorder agent rankings.
10. **Multi-Agent LLM Metamorphic Testing for REST APIs (ARMeta)** (Khan et al., 2026) — https://arxiv.org/abs/2605.28321 — **MEDIUM.** Metamorphic testing of tools/APIs framing. (Companion threat to our META framing: **AgentAssay**, https://arxiv.org/abs/2603.02601, explicitly defines "metamorphic relations for agent workflows.")

Honorable mentions still relevant as baselines/foundations, not novelty threats: tau-bench (https://arxiv.org/abs/2406.12045, final-DB-state oracle + pass^k), ToolSandbox (https://arxiv.org/abs/2408.04682, stateful infra + "Canonicalization" task), MCP Smelly (https://arxiv.org/abs/2602.14878), On the Robustness of Agentic Function Calling (https://arxiv.org/abs/2504.00914), ToolMisuseBench (https://arxiv.org/abs/2604.01508, fault-injection incl. "interface drift").

**Verified non-collisions (do not let the Scout's titles mislead):**
- arXiv 2605.26165 = "Tool-Schema Compression Enables Agentic RAG Under Constrained Context Budgets" — pure context-budget schema compression. None of EQ/META/RANK/NORM-transfer.
- arXiv 2510.03992 = "Quantitative Certification of Agentic Tool Selection" (LLMCert-T) — statistical safety certification of tool-selection under tool-pool distribution shift. Not interface representation, not metamorphic, not normalization.
- arXiv 2604.20560 = "LLM StructCore" — clinical CRF extraction; deterministic compile of a 9-key form. Irrelevant to tool interfaces.

---

## 2. Per-work itemized overlap with our claim

Legend: EQ = equivalence by environment state-transition equality; META = paired metamorphic over behavior-preserving interface transforms; RANK = ranking reversal from representation alone; NORM = label-free canonical normal form transferring to unseen transforms/tools.

### (1) PIPE — 2602.01611 — the paper that hurts most
Verbatim abstract: "...benchmark scores alone are not identifiable evidence of environment-invariant capability. We propose PIPE, a protocol-level evaluation augmentation for diagnosing interface reliance by **minimally rewriting environment interfaces while preserving task semantics and execution behavior**. Across 16 environments from AgentBench and AgentGym and a range of open-source and API-based agents, PIPE reveals that trajectory-SFT substantially amplifies interface shortcutting..." Verbatim body: "The rewrite changes action names in {Di}, **while keeping the executable action behaviors, tasks, and observations unchanged**." Verbatim eval: "We evaluate an agent on both ℰ and ℰ′ and consider the performance gap Δ(πθ;ℰ)=Score(πθ;ℰ)−Score(πθ;ℰ′)."
- **EQ: OCCUPIED (informally).** "Keeping executable action behaviors unchanged" while changing the model-visible action names = the state transition is held identical and only the representation changes. They do not give a *formal* state-transition-equality definition or audit byte-equality, but the operational content is ours.
- **META: OCCUPIED.** Paired contrast ℰ vs ℰ′ on the same task with a behavior-preserving rewrite, reported as a gap Δ. This is metamorphic paired evaluation over interface transforms in all but name.
- **RANK: PARTIAL.** They show trajectory-SFT agents degrade sharply while non-trajectory-trained models stay stable — a *model-class difference in sensitivity*, not a reordered leaderboard. No Kendall-τ / rank-reversal table from representation alone.
- **NORM: ABSENT.** They offer only a diagnostic metric (Interface Reliance, an alias-based counterbalanced score). No normalization layer, no canonical form, no transfer-to-unseen-transforms remedy.
- **Net:** Kills our "EQ+META is an unoccupied combination." Leaves NORM and ranking-reversal-characterization open. Their transform is narrow (action-name aliases; observations unchanged); ours is a broad family — but that is a *breadth* argument, not a *kind* argument.

### (2) ReliabilityBench — 2601.06112
- **META: OCCUPIED (vocabulary).** Literally "Action Metamorphic Relations." **EQ: PARTIAL** — scores by end-state equivalence. **RANK/NORM: ABSENT.**
- **Defense (still valid):** they perturb tasks (eps) and inject API/tool faults (lambda), including schema *drift as a failure*; these *change* the state transition. We hold it identical. Real distinction, but it shares the metamorphic+end-state vocabulary, so "metamorphic agent eval with state-equivalence scoring" is no longer novel terminology.

### (3) Schema First — 2603.13404
- **Design overlap: HIGH.** Explicitly "preserve identical tool semantics and information content" while varying the interface specification (NL docs vs JSON Schema vs JSON+diagnostics). That is our exact manipulation.
- **EQ: ABSENT** (no state-transition-equality construct). **META: PARTIAL** (controlled, not paired-metamorphic over equivalence classes). **RANK: ABSENT** (single model × 3 seeds). **NORM: ABSENT.**
- **Damaging finding for us:** their result is that schema formalization fixes *interface* misuse but **not** semantic misuse, and success stays ~0 — i.e., the bottleneck is semantic, not representational. A reviewer will use this to argue our "representation alone moves success" effect may be small or task-specific.

### (4) Semantic Invariance in Agentic AI — 2603.13173
- **META: OCCUPIED.** Metamorphic framework with 8 semantics-preserving transforms (identity, paraphrase, fact reordering, expansion, contraction, two context shifts, contrastive). **RANK: OCCUPIED (in spirit).** Reports a rank inversion — smaller Qwen3-30B-A3B is the most invariant; larger models more fragile.
- **EQ: ABSENT** (no state-transition equality). **NORM: ABSENT** (diagnostic only). **Unit mismatch:** they perturb *problem formulations* over 19 multi-step reasoning problems, **not tool interfaces**.
- **Damage:** the *combination* "metamorphic + semantics-preserving + agentic + rank inversion" is already published. Our META+RANK story is therefore an extension to the tool-interface channel, not a new idea.

### (5) Natural Language Tools — 2510.14453
- **RANK: OCCUPIED (single swap).** JSON→NL representation lifts accuracy 18.4 pts, cuts variance 70%, and open-weight models surpass flagship closed-weight ones — a representation-induced reordering. **EQ/META/NORM: ABSENT.** Single proposed representation, not a sweep.

### (6) TSCG — 2605.04107 (anchor)
- **NORM: PARTIAL.** Deterministic, label-free transform of tool-schema representation with a formal ≥51% compression bound; restores Phi-4 14B from 0%→84.4%. **EQ/META/RANK: ABSENT.**
- **Inside our stated boundary** (schema textualization/compression with fixed operators). Distinct from us only because it is a *fixed operator set optimizing tokens*, not a canonical normal form that transfers to *unseen transform families*. Reviewers will demand we show the difference empirically.

### (7) Learning to Rewrite Tool Descriptions — 2602.20426
- **NORM: PARTIAL.** Learned rewriter (Trace-Free+) that transfers to **unseen tools** without per-tool traces. **EQ/META/RANK: ABSENT.**
- **Inside our boundary** (rewriting descriptions). Distinct only by: canonical normal form (not perf-tuned rewrite) + transfer to unseen **transforms** (not just tools) + label-independence. That is a narrow, contestable delta.

### (8) When Benchmarks are Targets — 2402.01781
- **RANK: OCCUPIED (QA).** Format perturbations move models up to 8 leaderboard positions. The canonical "ranking is fragile to format" citation. Not tools, no EQ/META/NORM.

### (9) AgentAtlas — 2605.20530
- **RANK: PARTIAL.** Prompt-format/labeling/axis choices reorder agent rankings. Evaluation-protocol variable, not the tool interface. No EQ/META/NORM.

### (10) ARMeta — 2605.28321 (+ AgentAssay 2603.02601)
- **META: PARTIAL (framing).** ARMeta = metamorphic testing of REST APIs with the API as system-under-test and the LLM as test generator. AgentAssay = "metamorphic relations for agent workflows" for regression testing across 5 models. Neither holds a tool's state transition identical to vary interface representation; no RANK/NORM. They erode the claim that "metamorphic testing for agents/tools" is itself novel.

---

## 3. Which specific claims we can NO LONGER make

These must be struck from the paper or reframed as explicit extensions. Each is killed by a verified work.

1. ~~"We are the first to hold the underlying state transition identical and change only the model-visible interface representation."~~ — **DEAD.** PIPE (2602.01611) rewrites action names while "keeping the executable action behaviors, tasks, and observations unchanged"; Schema First (2603.13404) holds "identical tool semantics and information content."
2. ~~"We are the first to evaluate agents with a paired/metamorphic contrast over behavior-preserving interface transforms."~~ — **DEAD.** PIPE's Δ(ℰ,ℰ′); ReliabilityBench's "Action Metamorphic Relations"; Semantic Invariance's 8 semantics-preserving transforms.
3. ~~"EQ + META is an unoccupied combination / our inseparable novel unit."~~ — **DEAD.** PIPE occupies it operationally (behavior-preserving interface rewrite + paired gap + multi-model). This was the Scout's headline defense; it no longer holds.
4. ~~"Showing that representation alone changes model ranking is new."~~ — **DEAD.** When Benchmarks are Targets (QA), Natural Language Tools (JSON→NL), AgentAtlas (protocol), and Semantic Invariance (semantics-preserving transforms → rank inversion). RANK is, at best, an *extension to behavior-preserving tool-interface transforms*.
5. ~~"Applying metamorphic semantic-invariance testing to agents (and finding rank inversions) is new."~~ — **DEAD.** Semantic Invariance in Agentic AI (2603.13173) does exactly this for reasoning tasks.
6. ~~"An automatic interface transform that generalizes is novel."~~ — **DEAD.** TSCG (deterministic, generalizes) and Rewrite-Tool-Desc (learned, generalizes to unseen tools). Generalization per se is not our delta.
7. ~~"Showing schema/interface drift degrades agents is a contribution."~~ — **DEAD.** ReliabilityBench, ToolMisuseBench, MCP Smelly, TSCG, Robust FC. Explicitly in our own stated novelty boundary.
8. ~~"We introduce metamorphic testing / end-state-equivalence scoring to tool-agent evaluation."~~ — **DEAD as terminology.** ReliabilityBench + tau-bench (final-DB-state oracle) + ToolSandbox (stateful + "Canonicalization") already supply these.

**What we may still claim (the surviving, defensible deltas):**
- (A) A **formal** definition of tool-interface equivalence by *audited byte-level environment state-transition equality*, instantiated over a **broad family** of behavior-preserving transforms (schema structure, parameter renaming, type representation, field ordering, verbosity, JSON↔NL) — strictly broader than PIPE's action-name aliasing (which leaves observations unchanged) and sharper than ReliabilityBench's informal end-state scoring. (Delta = formality + breadth, not kind.)
- (B) **The remedy: a label-free semantic NORMAL FORM that reduces sensitivity and transfers to UNSEEN transform families and unseen tools.** No verified work does this. PIPE only diagnoses (IR metric); TSCG is fixed operators for tokens; Rewrite-Tool-Desc transfers to unseen tools for performance, not a canonical form across unseen transforms. **This is the paper's strongest remaining contribution and should become the headline.**
- (C) A **ranking-reversal characterization** across a metamorphic family of state-equivalent tool interfaces (magnitude, direction, Kendall-τ), *with a normalization fix that restores rank stability* — an extension of known format-fragility, made non-trivial only by the fix in (B).

---

## 4. Experiments we MUST add to prove the difference

Without these, the paper is a re-run of PIPE + the ranking-fragility cluster with a heavier vocabulary.

1. **Head-to-head against PIPE (2602.01611).** Reproduce PIPE-style action-name aliasing as one transform family inside our suite, on overlapping environments (AgentBench/AgentGym), and show: (i) our transform families that PIPE does NOT cover (schema structure, types, ordering, verbosity, JSON↔NL) produce comparable or larger Δ; (ii) **our normalization layer recovers performance on PIPE-style aliases that PIPE leaves unaddressed.** If our normal form cannot beat "do nothing" on PIPE's own perturbation, the contribution collapses.
2. **NORM transfer to held-out transforms (load-bearing).** Derive the normal form using transform families A only; evaluate on disjoint held-out families B **and** held-out tools, with **no transform labels at inference**. Primary endpoint: reduction in paired sensitivity (shrinkage of Δ and of rank instability) on *unseen* families. This is the one result that separates us from TSCG (fixed operators, no unseen-transform transfer) and Rewrite-Tool-Desc (unseen tools only). Pre-register the held-out split before any runs.
3. **Ranking-reversal table with ≥6–8 models.** Report Kendall-τ / Spearman between the original-interface leaderboard and each transformed-interface leaderboard; quantify position swaps and any sign reversals; then show normalization restores τ→~1. Explicitly cite When-Benchmarks, NLTools, AgentAtlas, Semantic Invariance as the baseline that we *extend*, not rediscover.
4. **State-transition-equality audit.** Demonstrate byte-identical environment transition logs across all interface variants of each tool (the formal EQ that PIPE/ReliabilityBench do not establish). This is what licenses "representation only" and rebuts "you actually changed information content."
5. **Information-content control (rebut Schema First).** Show the effect persists when information content is held equal across variants (token-matched / content-matched), since Schema First found semantics — not representation — is the bottleneck and success stayed ~0. If our effect vanishes under content-matching, the central claim fails.
6. **Beyond binary success: paired error-type and cost deltas.** Report error-type migration and token/step cost per paired contrast, not just success, to distinguish from the success-only degradation papers and to substantiate the "changes error types and cost" portion of the claim.

Kill conditions to pre-register: if (2) shows no significant Δ-shrinkage on unseen transform families, **NORM is dead and only a benchmark remains**; if (5) shows the effect is driven by information content, **the "representation alone" claim is dead**.

---

## 5. Worst case: what our contribution gets downgraded to

If reviewers accept PIPE as prior art for EQ+META and the RANK cluster for ranking fragility (both honest reads), ToolMorph downgrades, in three steps of severity:

- **Mild downgrade:** "An empirical robustness study that extends interface-reliance probing (PIPE) and format-ranking-fragility from QA/single-swap settings to a *broader family* of behavior-preserving tool-schema transforms, plus a label-free semantic normalization layer that transfers to unseen transforms." Novelty = breadth + the fix. Publishable at a workshop / mid-tier venue if the fix transfers.
- **Severe downgrade (if NORM transfer is weak):** "Yet another tool-interface robustness benchmark," landing in an already-crowded room with ReliabilityBench, ToolMisuseBench, Schema First, Robust FC, and PIPE — where the only differentiator (the normalization remedy) underperforms. This is a desk-reject-risk framing at a top venue.
- **Floor:** If both (a) content-matching erases the effect (Schema First's bottleneck-is-semantic finding generalizes) and (b) the normal form fails to beat "do nothing" on PIPE's own aliases, the paper has **no defensible core** and becomes a negative/replication note.

The single asset that keeps us above the floor is the **normalization remedy with verified transfer to unseen transform families** — it is the only element no verified competitor possesses. The phenomenon (sensitivity, paired metamorphic, ranking shift) is now a *motivating, largely-known* setup, not the contribution.

---

## 6. Recommendation: NARROW

**NARROW** (not KILL, not PASS, not MERGE).

Not KILL: no single verified work establishes the *full* central claim. PIPE comes closest but lacks the normalization remedy, a formal state-transition-equivalence definition, a ranking-reversal characterization, and breadth beyond action-name aliasing; the NORM cluster (TSCG, Rewrite-Tool-Desc) lacks state-equivalence, pairing, and transform-transfer; the RANK cluster is QA/protocol/single-swap. The conjunction — *broad behavior-preserving tool-interface family + audited state-transition equality + ranking-reversal characterization + a label-free canonical normal form that transfers to unseen transforms and fixes the sensitivity* — is unoccupied. Not PASS: the Scout's headline defense (EQ+META as an unoccupied novel unit) is dead on arrival to any reviewer who knows PIPE (2602.01611), so the paper cannot ship on that framing. Not MERGE: there is no single neighbor whose scope subsumes enough of ours to merge into.

Concretely: **re-architect the paper around the normalization remedy (NORM) as the headline contribution**, demote EQ+META to a *carefully-cited setup* that explicitly credits PIPE/ReliabilityBench/Schema First and claims only *formality + breadth*, and frame RANK as an *extension with a fix* citing the four ranking-fragility works. Then the paper must pass Experiments 1, 2, and 5 (head-to-head vs PIPE; NORM transfer to held-out transforms; information-content control). If Experiment 2 fails at the pilot gate, **escalate to KILL** — without transferable normalization, ToolMorph is a redundant robustness benchmark. fatal_collision = **false**: damaging, survivable, conditional on the normalization result.
