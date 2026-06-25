# DeltaResearch: Typed Dependency-Graph Patching of Reports under Evidence-World Updates

> DRAFT — pilot manuscript, written evidence-first from `evidence/pilot_2026-06-25.md`. Abstract,
> Introduction, and Results filled; deterministic infrastructure result (P3-C0) kept separate from
> the pilot-scale real-agent findings. Numbers are pilot-scale; CIs, real-evidence transfer, and the
> H_DIVERGE gate are pending.

## Abstract

Deep-research agents must keep long reports consistent when the underlying evidence world changes —
a source is revised, retracted, recomputed, or expires — not only when an author edits the prose.
Prior work shows that agents regress during multi-turn revision (Mr.DRE) and measures change/preserve
adherence for author edits on synthetic manuscripts (EditPropBench), but the *evidence-world* delta
trigger and a method that maintains derived, temporal, and recomputed claims remain open. We model a
report as a *typed* claim-evidence dependency graph and emit a constrained, audited claim-level patch
in response to the delta, and we build a controlled DeltaBench layer whose gold change/preserve/new/
contested claim sets are computed by an *independent* world-physics recomputation (a separate code
path from the analyzer, so validation is not circular). In a pilot of 18 controlled worlds (3 seeds ×
6 effectful delta types) with 72 LLM episodes across two real subscription-CLI agent families (Claude
and Codex/gpt-5.5), real agents recover only about one third of the claims that must change
(Affected-Claim Recall 0.33-0.39, range across families and prompt arms) while preserving unaffected
claims (Unaffected-Claim Preservation ~1.0) — the stale-residual failure. Handing the agent the
typed-graph affected set does not raise recall (ACR 0.33 vs 0.39), so the bottleneck is editing and
re-derivation, not identification; the deterministic typed-graph analysis plus constrained patch
instead reaches ACR = UCP = 1.0, against full regeneration (UCP = 0.0, the spurious-revision failure)
and a flat claim-citation ledger (ACR = 0.13). We release the world generator, typed-graph analyzer,
baselines, and metrics. Scope: this is pilot-scale, controlled-world, deterministic-gold evidence on
two model families; a real versioned-evidence layer, the divergence gate (evidence-world vs author
edit), and human adjudication are gated next steps.

## 1. Introduction

Consider a deep-research report that states "the regional employment figure is 412,000" and, two
sentences later, "the composite activity index stands at 1.07" — where the index is computed from the
employment figure together with two other series — and, alongside, the qualitative judgment "the
labour market remains tight." Now the source revises the employment figure to 418,000. Faithful
maintenance is not a free-text rewrite: the numeric claim *must* change, the composite index *must*
be recomputed and changed (it is derived from the revised input), and the qualitative judgment *must*
stay fixed (the revision is too small to flip it). An agent that edits only the directly-cited number
leaves a stale, internally-inconsistent index behind; an agent that regenerates the whole report
risks silently overwriting the still-correct qualitative claim. The hard cases are precisely the
*downstream* obligations — derived, temporal, and recomputed claims — that no longer sit next to the
source that changed.

We study this **evidence-world delta** setting, in which the trigger is a change to the sources
(a numeric revision, retraction, source conflict, temporal-validity change, or upstream recompute)
rather than an author's manuscript edit. Our headline pilot finding is that two independent real
agent families — Claude and Codex (gpt-5.5), run through subscription CLIs — given such a delta
recover only about one third of the claims that must change (Affected-Claim Recall, ACR = 0.33-0.39)
while leaving unaffected claims essentially intact (Unaffected-Claim Preservation, UCP ~ 1.0). They
behave like a conservative direct-citation ledger: they fix what is cited and miss the downstream
cascade. Against a deterministic gold computed by an *independent* world-physics recomputation, a
typed dependency-graph analysis plus a constrained, audited claim-level patch reaches ACR = UCP = 1.0,
whereas full regeneration destroys every preserved claim (UCP = 0.0) and a flat claim-citation ledger
misses ~87% of the downstream (ACR = 0.13). Notably, simply *handing* the agent the typed-graph
affected set does not raise its recall — an honest negative that localizes the bottleneck to editing
and re-derivation, not identification, and motivates a structured pipeline rather than better
prompting.

We concede up front the two adjacent prior results we build on: Mr.DRE ~\cite{mrdre2026} establishes
that deep-research agents regress during multi-turn revision, and EditPropBench ~\cite{editpropbench2026}
introduces the change/preserve dual metric and the "~30% of obligated updates missed" headline for
author edits on scientific manuscripts. Our contribution is the *evidence-world* trigger, the typed
dependency-graph method that beats both a flat ledger and full regeneration on the joint objective,
and the controlled DeltaBench layer with non-tautological gold. Concretely, this pilot contributes:

1. **A controlled DeltaBench layer with programmatic gold A/U/N/C** computed by an independent
   world-physics recomputation — a *separate code path* from the typed-graph analyzer, so "analyzer ≈
   gold" genuinely validates the graph rather than being circular (Section 3; P3-C0, SUPPORTED).
2. **Evidence that real agents leave a stale residual:** Claude and Codex recover only ACR = 0.33-0.39
   of obligated downstream updates at UCP ~ 1.0, reproduced across two model families on an
   evidence-world delta (Section 6.2; P3-H1, pilot-scale).
3. **An honest negative on prompting structure:** giving the agent the typed-graph affected set does
   not raise ACR (0.33 vs 0.39), localizing the failure to edit/re-derivation rather than
   identification (Section 6.3; P3-H3, not supported).
4. **A deterministic typed-graph + constrained-patch method** that attains ACR = UCP = 1.0 on the
   controlled gold, Pareto-dominating full regeneration (UCP = 0.0) and the flat ledger (ACR = 0.13)
   on the joint objective (Sections 3-4, 6.1; P3-H4 at the deterministic level).

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

**Pilot.** 18 controlled worlds (3 seeds × 6 effectful delta types) with programmatic gold A/U/N/C
from the independent world-physics recomputation; 72 LLM episodes (2 model families × 2 prompt arms ×
18 worlds) logged to the immutable ledger; deterministic baselines computed once per world. All
numbers are the pre-registered joint pair (ACR, UCP), never a maskable single average. Two real agent
families were run through subscription CLIs at no API cost: `claude` and `codex` (gpt-5.5).

| arm | ACR | UCP |
|---|---|---|
| oracle (upper bound) | 1.00 | 1.00 |
| typed_graph (our method, deterministic) | 1.00 | 1.00 |
| full_regen (deterministic) | 1.00 | 0.00 |
| naive_ledger / flat (deterministic) | 0.13 | 0.97 |
| Claude, naive LLM patch | 0.39 | 1.00 |
| Claude + typed-graph hint | 0.33 | 1.00 |
| Codex, naive LLM patch | 0.34 | 0.99 |
| Codex + typed-graph hint | 0.33 | 1.00 |

**6.1 The deterministic frontier (SUPPORTED, P3-C0/H4).** Against the gold computed by the separate
world-physics code path, the typed-graph analyzer plus constrained patch attains ACR = UCP = 1.00,
matching the oracle upper bound. The two structure-poor baselines each fail on exactly one side of
the joint objective: full regeneration catches every obligated change (ACR = 1.00) but rewrites every
preserved claim (UCP = 0.00) — the spurious-revision failure — while the flat claim-citation ledger,
which follows only direct-support edges, preserves almost everything (UCP = 0.97) but recovers only
ACR = 0.13, missing ~87% of the downstream (derived/temporal/recomputed) claims. The joint pair
therefore separates the methods cleanly: no single scalar would, since full regen and the flat ledger
are each perfect on one axis. Only the typed graph is Pareto-dominant. This is the deterministic,
infrastructure-level result and is reported as SUPPORTED.

**6.2 Real agents leave a stale residual (H1).** Given the evidence-world delta as a natural-language
description plus the report's atomic claims, both real families recover only about one third of the
claims that must change: Claude reaches ACR = 0.39 and Codex ACR = 0.34, i.e. they miss ~61% and ~66%
of obligated updates respectively. They do this while leaving unaffected claims almost entirely
intact (UCP = 1.00 and 0.99). In other words, the agents behave like a conservative near-flat-ledger:
they fix the directly-cited claim but do not propagate the change to derived, temporal, or recomputed
downstream claims. This is the stale-residual failure on evidence updates — the phenomenon Mr.DRE
~\cite{mrdre2026} reports for multi-turn revision and EditPropBench ~\cite{editpropbench2026} reports
for author edits — here reproduced on an *evidence-world* delta across two independent model families.
We report this as a pilot-scale empirical result (P3-H1), consistent in direction across both
families.

**6.3 The typed hint does not help — an honest negative (H3).** Handing the agent the typed-graph
affected set as an explicit hint did *not* raise recall: Claude moved from ACR = 0.39 to 0.33 and
Codex from 0.34 to 0.33 (UCP stayed ~1.0 in both arms). The hint, if anything, was neutral-to-slightly
negative and never closed the gap to the deterministic 1.00. The pre-registered prediction that
structure handed to the agent would help (P3-H3) is therefore **not supported** in this pilot. The
diagnostic value is large: because the bottleneck is *not* identifying which claims are affected —
the agents are told and still under-edit — the failure lies downstream, in actually performing the
edits and re-deriving numerics. This localizes the contribution to the structured, mostly-deterministic
maintenance pipeline (analyze → constrained patch → verify), not to better prompting of an agent.

**6.4 Status of the divergence gate (H_DIVERGE).** The pre-registered gating question — whether an
evidence-world delta induces a different obligated-change set than an equivalent author-style
manuscript edit (without which the evidence-world framing would be cosmetic) — is *not* quantified in
this pilot. The divergence harness (`diverge.py`) is built, but no H_DIVERGE number is reported here;
it remains UNTESTED (P3-HDIV) and is part of the gated next step. The numbers above are confined to
the controlled layer with deterministic gold.

## 7. Related work

We credit the two adjacent results we build on and concede their respective halves. **EditPropBench**
~\cite{editpropbench2026} introduces the change/preserve dual metric and the "~30% of obligated
updates missed" headline, but on synthetic *author* manuscript edits with no agent, audit trail, or
evidence-world trigger; we adopt the dual objective and differentiate by the evidence-world delta,
the typed-graph method, and the constrained-patch audit. **Mr.DRE** ~\cite{mrdre2026} shows
deep-research agents regress on non-target content and citations during multi-turn *revision driven
by user feedback*; we build on that phenomenon but our unit is evidence-delta → claim-impact, with
gold affected/unaffected/new/contested sets. Our two-family (Claude/Codex) setup follows
cross-model agent evaluation practice ~\cite{cc02xiang2026}, and our reliance on a deterministic gold
to score non-deterministic agents is in the spirit of regression testing for agent workflows
~\cite{agentassay2026}.

The remaining neighbors each own one component but not the conjunction on report prose under an
evidence-world delta; pending Director verification we refer to them descriptively only: the base
task of updating a document to reflect new evidence (FRUIT) [unverified — pending Director
verification]; generation-time claim-evidence provenance and audit (AAR) [unverified — pending
Director verification]; graph/rule-guided propagation of updates to dependent facts in parameter/KB
space (ChainEdit, RippleEdits) [unverified — pending Director verification]; honest handling of
conflicting evidence as QA (RAMDocs) [unverified — pending Director verification]; and staleness from
real timestamped evidence (evolveQA) [unverified — pending Director verification]. None revise a
deep-research report under an evidence-world delta with a typed dependency-graph patch and joint
stale+spurious metric. See `novelty/novelty_attack.md` for the full adversarial sweep.

## 8. Limitations / Ethics

This is a pilot, and we keep its claims narrow. (i) **Scale and statistics:** 18 controlled worlds
(3 seeds × 6 delta types), 72 LLM episodes, two model families; we report point values and ranges,
not confidence intervals — more seeds for world-clustered CIs are the immediate next step, and the
real agent numbers should be read as directional rather than precise. (ii) **Synthetic worlds only:**
all reported numbers are on the controlled DeltaBench layer; the real versioned-evidence layer
(Layer B) is built into the design but unrun, so transfer (H5) is untested. (iii) **The divergence
gate is unquantified:** H_DIVERGE — whether an evidence-world delta truly induces a different
obligated-change set than an equivalent author edit — is a kill-gate that this pilot does not yet
measure; if it fails, the evidence-world framing is cosmetic. (iv) **The deterministic 1.0 is the
infrastructure result, not the real-agent result:** the typed-graph + constrained-patch arm runs the
gold-aligned analysis end to end, so ACR = UCP = 1.0 reflects the controlled gold; the open problem
is closing the gap between that frontier and the real agents (ACR 0.33-0.39), which the typed-hint
arm shows is *not* closed by simply telling the agent which claims are affected. (v) **Honest
negatives retained:** P3-H3 (typed hint helps) is not supported, and only the deterministic baselines
exhibit the full failure spectrum (full regen UCP = 0.0; flat ledger ACR = 0.13). LLM judges are not
used for the primary endpoint, which is the deterministic gold; they remain secondary and gated to
the real subset with human agreement. **Ethics:** real sources will be stored as URL + hash +
snapshot (not full text), license-respecting, with medical/legal-advice domains excluded from the
first batch.
