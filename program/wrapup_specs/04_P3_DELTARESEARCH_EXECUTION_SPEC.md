# P3 — DeltaResearch Full Execution Specification

## A. Target and decision

**Primary strict-journal venue:** Transactions of the Association for Computational Linguistics (TACL).

**Alternative:** ACL Rolling Review only if the paper is deliberately routed to an ACL conference. Do not submit to TACL and ARR simultaneously. If the work receives ARR review, TACL has a nine-month ineligibility rule tied to the ARR submission month.

Current supported observation:

> In controlled evidence-world updates, tested agents frequently fail to propagate required changes to downstream report claims while mostly preserving untouched claims.

Current unsupported claim:

> A typed graph method achieves perfect end-to-end revision.

The existing perfect result used oracle/gold information and is only a consistency upper bound.

Surviving full-paper claim:

> An end-to-end, no-gold pipeline that detects external evidence changes, constructs claim–source/dependency provenance, recomputes affected values, and performs constrained patching improves affected-claim coverage while preserving unaffected content on controlled and real versioned-evidence updates.

## B. Research questions

- **RQ1:** How often do report-revision agents miss direct versus downstream obligations under different evidence changes?
- **RQ2:** Which stage is the bottleneck: delta detection, claim extraction, dependency inference, recomputation, constrained editing, or verification?
- **RQ3:** Can predicted provenance/dependency structure improve the joint revision-quality frontier without gold affected sets, gold graphs, or gold post-update values?
- **RQ4:** Do controlled findings transfer to real official evidence revisions, documentation changes, corrections, or retractions?
- **RQ5:** Can the system produce auditable rationales linking each report edit to source versions and derivations?

## C. Formal problem

Each episode contains:

- old evidence world `W0` with versioned sources;
- old report `R0` generated or validated against `W0`;
- evidence delta `ΔW`;
- new evidence world `W1`;
- gold affected claims `A` for evaluation only;
- gold unaffected claims `U` for evaluation only;
- derivations and expected revised values for evaluation only.

The method receives only `W0`, `R0`, and observable `W1/ΔW`. It must not receive `A`, `U`, gold dependency edges, or post-update claim values.

## D. Controlled dataset

### D1. Dependency topologies

Generate diverse worlds with:

- linear chains;
- branching trees;
- diamonds/converging derivations;
- one source supporting many claims;
- one claim supported by multiple sources;
- source conflict;
- temporal supersession;
- numerical aggregation;
- ratios and percentage changes;
- threshold-triggered qualitative conclusions;
- retraction/correction propagation;
- claims repeated or paraphrased across sections;
- mixed direct and derived claims.

### D2. Delta types

- numeric revision;
- categorical status change;
- source retraction;
- source correction/erratum;
- more authoritative source appears;
- source conflict;
- time-validity expiry;
- definition/methodology change;
- unit or denominator change;
- API/documentation behavior change;
- evidence deletion/unavailability.

### D3. Report variation

Vary:

- number of claims;
- report length;
- number of sections;
- paraphrase distance;
- table versus prose expression;
- citation placement;
- derivation depth;
- irrelevant evidence distractors.

### D4. Controlled oracle

The generator must output an executable derivation graph and validate all pre/post values. Gold graphs are used only by the evaluator and oracle upper-bound conditions, never by the proposed method.

## E. Real versioned-evidence layer

Use free, public, versioned sources with clear provenance. Candidate families:

- official macroeconomic/statistical releases with later revisions;
- public government/regulatory documents with version histories;
- public API/software documentation git histories and release notes;
- arXiv version changes, formal corrections, errata, or retraction metadata;
- public benchmark/leaderboard corrections;
- product or standards documentation with archived versions.

For every case store:

```yaml
case_id:
domain:
source_uris:
source_license_or_terms:
W0_timestamp:
W0_hashes:
W1_timestamp:
W1_hashes:
delta_summary:
R0_creation_protocol:
gold_claim_inventory:
gold_affected_claims:
gold_unaffected_claims:
gold_recomputed_values:
annotation_rationale:
annotators:
adjudication_status:
```

### E1. Temporal integrity

- Use only evidence available at `W0` when constructing `R0`.
- Prevent hindsight leakage.
- Archive or hash source snapshots where permitted.
- Record source publication and revision timestamps.
- Distinguish correction of an old fact from arrival of a genuinely new fact.

### E2. Annotation

Prefer two qualified human annotators plus adjudication. Do not fabricate a second annotator. If only one human is available:

- explicitly report single-human annotation;
- use deterministic calculations and source-version checks where possible;
- arrange a blinded sample audit if a second person becomes available;
- do not state inter-annotator agreement.

Agent-generated candidate labels may accelerate annotation but must be approved by a human and labeled as assisted.

## F. End-to-end method

Implement these stages:

1. **Evidence Delta Detector** — identifies changed facts, source status, units, methods, temporal validity, and contradictions.
2. **Claim Extractor** — inventories atomic factual, numerical, comparative, causal, and recommendation claims in `R0`.
3. **Provenance Linker** — maps claims to exact source versions, spans, calculations, and intermediate claims.
4. **Typed Dependency Constructor** — predicts direct support, arithmetic derivation, temporal dependency, definitional dependency, logical implication, and conflict-resolution edges.
5. **Impact Propagator** — predicts the affected subgraph and uncertainty.
6. **Retriever/Recomputer** — re-reads changed sources and performs actual calculations using a deterministic calculator where applicable.
7. **Constrained Patcher** — edits only claims/sections predicted to require change, with explicit patch scope.
8. **Post-Update Verifier** — checks source-version alignment, calculations, contradictions, stale citations, and unintended changes.
9. **Revision Rationale Generator** — emits an auditable ledger of old claim, new claim, source delta, derivation, and confidence.

No stage may read gold evaluation labels.

## G. Baselines and upper bounds

Actual prompted/executable baselines:

1. naive “update this report” prompt;
2. full regeneration from `W1`;
3. retrieval-augmented update without dependency graph;
4. flat claim–citation ledger;
5. edit-propagation/cascade baseline comparable to closest manuscript-edit work;
6. graph without recomputation;
7. graph + recomputation without constrained patching;
8. full end-to-end method.

Oracle diagnostic conditions, always labeled upper bounds:

9. gold affected set only, no gold values;
10. gold graph/impact, actual recomputation;
11. predicted impact + gold recomputed value;
12. full gold oracle.

The paper must visibly separate baselines, ablations, and oracle diagnostics.

## H. Stage-wise diagnostics

Measure:

- delta detection precision/recall;
- claim extraction precision/recall;
- provenance link accuracy;
- dependency-edge precision/recall by type;
- affected-set precision/recall;
- recomputation correctness;
- patch correctness;
- verifier detection rate;
- final report quality.

This enables a causal error decomposition rather than inferring bottlenecks from one prompt condition.

## I. Metrics

### Primary joint outcome

Use a preregistered joint metric or decision rule that rewards required updates and penalizes harmful unnecessary changes. Do not rely on UCP alone, because a system that edits nothing can score high on preservation.

Report separately:

- affected-claim recall and precision;
- semantic preservation of unaffected claims;
- harmful edit rate;
- numerical recomputation accuracy;
- stale citation/source-version rate;
- unsupported claim rate;
- contradiction-resolution accuracy;
- provenance completeness;
- revision minimality;
- audit-rationale correctness;
- tokens, latency, and tool use.

Where an LLM semantic judge is used, validate it against genuine human labels and deterministic checks. Keep a non-LLM primary analysis wherever possible.

## J. Splits

- controlled topology holdout;
- delta-type holdout;
- source/domain holdout;
- real-world temporal holdout;
- optional model-family holdout.

Do not allow paraphrases of the same evidence world across train/test.

## K. Experimental conditions

Test at least two authorized model families for naive/full-regeneration baselines. The proposed pipeline may use a fixed model, but report whether gains come from structure versus a stronger model by crossing method and model where feasible.

Freeze:

- prompts;
- extraction schemas;
- graph types;
- calculation tools;
- patch constraints;
- judge versions;
- budgets;
- evaluation code;
- stopping rule.

## L. Statistics

- Unit: evidence world/case.
- Repeated model runs nested within world.
- Paired comparisons across methods on the same world.
- World-cluster bootstrap CIs.
- Mixed models for method, model, topology, delta type, and domain.
- Report controlled and real layers separately, then a predeclared pooled analysis if justified.
- Correct secondary comparisons.
- Conduct sensitivity to annotation disagreements and semantic-equivalence thresholds.

## M. Required outputs

Tables:

1. Controlled and real dataset composition.
2. Annotation and oracle reliability.
3. Stage-wise diagnostic accuracy.
4. Main final-report metrics on controlled holdout.
5. Main final-report metrics on real evidence updates.
6. Ablations and oracle gap.
7. Delta-type/topology/domain breakdown.
8. Cost, latency, and failure modes.

Figures:

1. Evidence-delta-to-report-patch pipeline.
2. Example claim dependency graph and propagated update.
3. Affected recall versus harmful edit frontier.
4. Stage-wise error waterfall.
5. Controlled-to-real transfer plot.
6. Failure examples: missed cascade, over-revision, stale source, wrong recomputation.

## N. P3 kill/hold gates

Set `HOLD` or `KILL` if:

- the method still consumes gold affected sets/graphs/values;
- a real versioned-evidence layer cannot be legally and reliably assembled;
- full regeneration dominates both correctness and preservation at matched budget;
- gains exist only on generator-known synthetic templates;
- primary result depends on an unvalidated LLM judge;
- annotation quality is insufficient for the central claim;
- closest work subsumes the final contribution after a fresh audit;
- independent reproduction fails.

Use `ARXIV_ONLY` for a strong empirical benchmark/pilot if the phenomenon is robust but the end-to-end method or real layer remains incomplete.

## O. P3 manuscript blueprint

Evidence-dependent title:

**DeltaResearch: Auditable Report Revision under External Evidence Updates**

Sections:

1. Introduction and exact gap relative to edit-propagation benchmarks.
2. Problem definition and evidence-world formalism.
3. Controlled and real versioned-evidence datasets.
4. End-to-end no-gold method.
5. Evaluation protocol and human/deterministic oracles.
6. Main controlled results.
7. Real-evidence transfer.
8. Stage-wise error analysis and ablations.
9. Related work: deep research, citation provenance, edit propagation, temporal knowledge, report revision.
10. Limitations, ethics, data statement, conclusion.

For TACL, keep the core manuscript focused and follow the official current page/appendix rules. Do not link supplementary repositories in the anonymized TACL submission if the current TACL rules prohibit such links; state the intended release anonymously.
