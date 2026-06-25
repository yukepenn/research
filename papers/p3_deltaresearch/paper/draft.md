# DeltaResearch: Typed Dependency-Graph Patching of Reports under Evidence-World Updates

> DRAFT — evidence-first order. Abstract/Intro/Results [PENDING] until ledger numbers land.

## Abstract
[PENDING]

## 1. Introduction
[PENDING — open with a propagation failure: a numeric source revision that obligates a downstream
index to change while a colocated qualitative claim must stay fixed]

## 2. Problem: evidence-world deltas, not author edits
We separate the *evidence world* `W_t` (sources with values, validity intervals, authority) from the
*report* `R_t` (atomic claims with support edges, derivations, temporal scope). An update is a delta
`ΔW` (numeric revision, source retraction, source conflict, temporal-validity change, upstream
recompute, new authoritative source). The gold impact partitions claims into `A` (must change),
`U` (must preserve), `N` (newly supported), `C` (now contested). The objective is to correctly
update `A` and `N`, preserve `U`, honestly flag `C`, and keep citations/calculations valid — *not*
to minimize character diff.

## 3. DeltaBench (controlled layer) + programmatic gold
We generate fully-verifiable worlds (`controlled_worlds/generator.py`): a latent fact graph yields
evidence and typed claims (base measurements; a total, margin, share, index by composition; a
temporally-scoped rate and its projection). After a delta, **gold A/U/N/C are computed by an
independent world-physics recomputation** (re-evaluate the fact graph, diff pre/post values and
citations) — a *separate code path* from the typed-graph analyzer, so "analyzer ≈ gold" genuinely
validates the graph rather than being tautological.

**Verified result (SUPPORTED, deterministic, P3-C0).** The typed-graph analyzer (`claim_graph.py`,
propagating through DERIVED/NUMERIC/TEMPORAL/QUALIFIED edges, respecting alternative support and
flagging conflicts) recovers the gold affected set; a **flat claim-citation ledger** that follows
only direct-support edges **strictly under-recalls** on derived/temporal claims. A negative-control
(irrelevant) update yields an empty gold `A`, which a correct analyzer must predict.

## 4. Method: ClaimPatch
Atomize claims → typed evidence ledger → typed dependency graph → deterministic impact analysis →
**constrained** claim-level patch (edit only authorized spans) → post-update verifier (support,
stale citations, numeric consistency, preserved-claim drift, audit trail). Baselines:
full-regeneration (rewrites all → spurious revision), naive-revise (direct-cite only → stale
residual), flat ledger, oracle upper bound (`baselines.py`).

## 5. Experimental setup
Plan-then-patch: the model receives the report's atomic claims + a natural-language description of
the evidence delta and returns a claim-level patch (edited ids, new numeric values, contested
flags, additions), scored by the deterministic gold (ACR/UCP + diagnostics). Arms: naive LLM patch;
LLM patch given the typed-graph impact hint; deterministic typed-graph / full-regen / oracle.
Models: Claude, Codex. **Scope:** pilot-scale, controlled worlds; a real versioned-evidence layer
(Layer B) and human adjudication are the gated next step.

## 6. Results
[PENDING — from `core.plotting.pilot_tables.p3_table`: ACR/UCP by (model × method) vs deterministic
baselines; stale-residual and spurious-revision decomposition; H_DIVERGE]

## 7. Related work
- **EditPropBench** (arXiv:2605.02083) introduces a change/preserve dual metric and the "~30% of
  obligated updates missed" headline on synthetic *manuscript edits* — we credit the dual metric and
  differentiate by the *evidence-world delta* trigger, typed-graph method, and audit trail.
- **Mr.DRE** (arXiv:2601.13217) shows deep-research agents regress 16–27% on multi-turn revision —
  the phenomenon we build on; our unit is evidence-delta→claim-impact, not writing feedback.
- FRUIT (base task), AAR (generation-time provenance), ChainEdit (KB propagation): each owns one
  half; our contribution is the conjunction on report prose. See `novelty/novelty_attack.md`.

## 8. Limitations / Ethics
Synthetic controlled layer; real layer + human adjudication pending; pilot-scale; LLM judges only
secondary (primary is deterministic gold). Sources stored as URL+hash+snapshot, license-respecting.
