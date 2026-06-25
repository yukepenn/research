# DeltaResearch (pilot): Real Deep-Research Agents Recover Only ~1/3 of Obligated Downstream Updates under Evidence-World Deltas — A Controlled Harness and Empirical Note

> DRAFT — workshop-tier pilot / benchmark-and-empirical note. This is NOT a finished venue submission
> and NOT the method paper an earlier title advertised. Written evidence-first from
> `evidence/pilot_2026-06-25.md`. The two genuine deliverables are (a) a released controlled-world
> harness (world generator, typed-graph analyzer, deterministic baselines, joint metrics, immutable
> episode ledger) and (b) a pilot empirical finding on two real subscription-CLI agent families. The
> deterministic typed-graph "frontier" (1.0/1.0 vs 0.0 vs 0.13) is a **construction-determined
> consistency check, NOT an empirical comparison of run systems**, and is labeled as such throughout.
> CIs, real-evidence transfer (Layer B), a falsifiable H_DIVERGE gate, and a de-oracled end-to-end
> method are unrun and pre-registered as next steps. See `## Honest status and path to a full paper`.

## Abstract

Deep-research agents must keep long reports consistent when the underlying evidence world changes —
a source is revised, retracted, recomputed, or expires — not only when an author edits the prose.
Prior work shows that agents regress during multi-turn revision (Mr.DRE) and measures change/preserve
adherence for author edits on synthetic manuscripts (EditPropBench), but the *evidence-world* delta
trigger and the maintenance of derived, temporal, and recomputed claims remain open. We release a
controlled DeltaBench harness — a world generator, a typed claim-evidence dependency-graph analyzer,
deterministic baselines, joint (ACR, UCP) metrics, and an immutable episode ledger — and report a
**pilot**. Our central, supported finding is an empirical negative: across 18 controlled worlds
(3 seeds × 6 effectful delta types) and 72 logged episodes on two real subscription-CLI agent
families (Claude, ACR = 0.39; Codex/gpt-5.5, ACR = 0.34), the agents — given the evidence-world delta
with the derivation rules stated in-prompt — recover only about one third of the claims that *must*
change while leaving unaffected claims essentially untouched (Unaffected-Claim Preservation,
UCP ~ 1.0); handing them the typed-graph affected set does not help (ACR = 0.33). This localizes the
failure to **editing and re-derivation, not identification**. We note that UCP ~ 1.0 is the mechanical
dual of conservative under-editing — a do-nothing agent also scores UCP = 1.0 — so for the real agents
the joint pair effectively collapses to ACR. We also report that the deterministic typed-graph
analyzer matches the programmatic gold (ACR = UCP = 1.0) against a full-regeneration foil (UCP = 0.0)
and a flat claim-citation ledger (ACR = 0.13); we explicitly flag this as a **construction-determined
consistency check, not an empirical result** — the analyzer is fed the gold graph and reads gold
values straight from `world.post_values`, performing no re-derivation, and the baselines are hand-coded
foils whose 0.0/0.13 are artifacts (the 0.0 penalizes *touching* a claim, not changing it, and
contradicts Mr.DRE's measured 16–27% regression). Scope: pilot-scale, a single fixed topology,
deterministic gold, no confidence intervals; a real versioned-evidence layer, a *falsifiable*
divergence gate, and a de-oracled end-to-end method are pre-registered next steps, not claims.

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
rather than an author's manuscript edit. **Our headline, supported contribution is an empirical
negative on real systems.** Two independent real agent families — Claude and Codex (gpt-5.5), run
through subscription CLIs — given such a delta *with the derivation rules stated in-prompt*, recover
only about one third of the claims that must change (Affected-Claim Recall, ACR = 0.39 for Claude,
0.34 for Codex) while leaving unaffected claims essentially intact (UCP ~ 1.0). They recover well
above a flat direct-citation ledger (~2.6–3× its ACR = 0.13) but fall far short of complete: they fix
what is cited and miss most of the downstream cascade. Crucially, *handing* the agent the typed-graph
affected set does not raise its recall (ACR = 0.33) — an honest null that localizes the bottleneck to
editing and re-derivation, not identification, and that is the most informative result in this pilot.

We are deliberately careful about what the deterministic side of the harness does and does *not*
show. A typed dependency-graph analysis plus a constrained patch reaches ACR = UCP = 1.0 on the
controlled gold, while a full-regeneration foil scores UCP = 0.0 and a flat ledger scores ACR = 0.13.
**This is a construction-determined consistency check, not an empirical comparison of run systems:**
the typed-graph arm is fed the gold dependency graph and reads patch values directly from
`world.post_values` (the gold), so it performs no re-derivation; the full-regen and flat-ledger arms
are hand-coded foils, and their 0.0/0.13 are artifacts of the construction (Section 6.3). We report it
only to demonstrate that the analyzer and the independent gold code path agree and that a flat ledger
structurally under-recalls — *not* as a method that beats real baselines.

We concede up front the two adjacent prior results we build on, both Director-verified: Mr.DRE
~\cite{mrdre2026} establishes that deep-research agents regress during multi-turn revision (a measured
16–27% regression magnitude), and EditPropBench ~\cite{editpropbench2026} introduces the
change/preserve dual metric and the "~30% of obligated updates missed" headline for author edits on
scientific manuscripts. Concretely, this pilot contributes:

1. **A released controlled DeltaBench harness** with programmatic gold A/U/N/C computed by an
   independent world-physics recomputation, deterministic baselines, the joint (ACR, UCP) metrics, and
   an immutable 72-episode ledger that reproduces every number below (Section 3; delivered/SUPPORTED as
   infrastructure).
2. **The central empirical finding — real agents leave a stale residual:** Claude and Codex recover
   only ACR = 0.34–0.39 of obligated downstream updates at UCP ~ 1.0 on an evidence-world delta, with
   the same direction in both families (Section 6.1; P3-H1, pilot-scale, SUPPORTED).
3. **An honest negative on prompting structure:** giving the agent the typed-graph affected set does
   not raise ACR (0.33 vs 0.39), localizing the failure to edit/re-derivation rather than
   identification (Section 6.2; P3-H3, pre-registered prediction *not* supported).
4. **A construction-determined consistency check (explicitly NOT a method result):** the typed-graph
   analyzer matches the independent gold (ACR = UCP = 1.0) while a full-regen foil and a flat ledger
   fail on one axis each (UCP = 0.0; ACR = 0.13). Because the typed-graph arm is oracle-fed and the
   foils are hand-coded, this is a unit-test-style consistency check, not a demonstrated method
   (Section 6.3; reported as such, not as P3-H4 evidence).

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
temporally-scoped rate and its projection). After a delta, gold A/U/N/C are computed by an
independent world-physics recomputation (re-evaluate the fact graph, diff pre/post values and
citations) — a separate code path from the typed-graph analyzer. We caution that "separate code path"
is a *weak* independence guarantee here: both code paths encode the *same* hand-authored dependency
structure on a single fixed 10-claim topology, so analyzer ≈ gold is largely a statement about the
author's own internal consistency rather than about the world. The harness, gold generator, baselines,
metrics, and the immutable episode ledger are the released deliverable; the deterministic numbers
below should be read accordingly (Section 6.3).

## 4. Method (released as harness; end-to-end version pre-registered, not yet run)
The intended pipeline is: atomize claims → typed evidence ledger → typed dependency graph →
deterministic impact analysis → **constrained** claim-level patch (edit only authorized spans) →
post-update verifier (support, stale citations, numeric consistency, preserved-claim drift, audit
trail). We release this scaffolding (`claim_graph.py`, `baselines.py`). **Important caveat:** in the
current pilot the typed-graph patch arm is *oracle-fed* — it reads target values directly from
`world.post_values` rather than re-deriving them — so the load-bearing re-derivation step (the very
step the agents fail at, Section 6.2) is **not exercised**. A de-oracled, actually-recomputing
end-to-end method (optionally driving a real agent for the edit/derivation step) is pre-registered as
the primary required experiment, not a result of this draft. Foil baselines: full-regeneration,
naive-revise (direct-cite only), flat ledger, oracle upper bound (`baselines.py`).

## 5. Experimental setup
Plan-then-patch: the model receives the report's atomic claims + a natural-language description of
the evidence delta and returns a claim-level patch (edited ids, new numeric values, contested
flags, additions), scored by the deterministic gold (ACR/UCP + diagnostics). Arms: naive LLM patch;
LLM patch given the typed-graph impact hint; plus the deterministic consistency-check arms
(typed-graph / full-regen / flat ledger / oracle). Models: Claude (`claude:claude-cli`) and Codex
(`codex:codex-cli`); the underlying build is *not* captured in the ledger, so the "gpt-5.5" identity
is asserted, not version-pinned. **Scope:** pilot-scale, a single fixed topology, controlled worlds;
each model condition is a *single draw* (no repeats, so within-condition variance is unmeasured), and
both arms share one prompt that explicitly instructs conservatism. A real versioned-evidence layer
(Layer B) and human adjudication are gated next steps.

## 6. Results

**Pilot.** 18 controlled worlds (3 seeds × 6 effectful delta types) with programmatic gold A/U/N/C
from the independent world-physics recomputation; 72 LLM episodes (2 model families × 2 prompt arms ×
18 worlds) logged to the immutable ledger; deterministic arms computed once per world. All numbers are
the pre-registered joint pair (ACR, UCP), never a maskable single average. Two real agent families
were run through subscription CLIs at no API cost: `claude` and `codex` (gpt-5.5). The table below
separates the **empirical finding (real agents)** from the **construction-determined consistency
check (deterministic arms)**; these are not co-equal results and must not be read as a single
frontier.

*Empirical finding — real agents (pilot-scale, SUPPORTED):*

| arm | ACR | UCP |
|---|---|---|
| Claude, naive LLM patch | 0.39 | 1.00 |
| Claude + typed-graph hint | 0.33 | 1.00 |
| Codex, naive LLM patch | 0.34 | 0.99 |
| Codex + typed-graph hint | 0.33 | 1.00 |

*Construction-determined consistency check — deterministic arms (NOT an empirical comparison of run
systems; the typed-graph arm is oracle-fed, the foils are hand-coded):*

| arm | ACR | UCP |
|---|---|---|
| oracle (upper bound, reads gold) | 1.00 | 1.00 |
| typed_graph (oracle-fed; reads `world.post_values`) | 1.00 | 1.00 |
| full_regen (hand-coded foil; marks all ASSERTED edited) | 1.00 | 0.00 |
| naive_ledger / flat (hand-coded foil; direct-cite only) | 0.13 | 0.97 |

**6.1 Real agents leave a stale residual — the central finding (H1).** Given the evidence-world delta
as a natural-language description plus the report's atomic claims *and the derivation rules in-prompt*,
both real families recover only about one third of the claims that must change: Claude reaches
ACR = 0.39 and Codex ACR = 0.34, i.e. they miss ~61% and ~66% of obligated updates respectively. They
do this while leaving unaffected claims almost entirely intact (UCP = 1.00 and 0.99). The agents land
**well above the flat ledger (~2.6–3× its ACR = 0.13) but far below complete**: they fix the
directly-cited claim yet do not propagate the change to most derived, temporal, or recomputed
downstream claims. This is the stale-residual failure on evidence updates — the phenomenon Mr.DRE
~\cite{mrdre2026} reports for multi-turn revision and EditPropBench ~\cite{editpropbench2026} reports
for author edits — here reproduced on an *evidence-world* delta, consistent in direction across two
model families. We caution explicitly that **UCP ~ 1.0 here is the mechanical dual of conservative
under-editing**: a do-nothing agent that touches nothing also scores UCP = 1.0. For the real agents
UCP is pinned at the ceiling, so the "joint pair" effectively collapses to ACR alone, and the
joint-metric framing adds little for these arms. We report this as a pilot-scale empirical result
(P3-H1), supported in direction, not as a precise or CI-bounded estimate.

**6.2 The typed hint does not help — an honest negative (H3).** Handing the agent the typed-graph
affected set as an explicit hint did *not* raise recall: Claude moved from ACR = 0.39 to 0.33 and
Codex from 0.34 to 0.33 (UCP stayed ~1.0 in both arms). The hint was neutral-to-slightly negative and
never closed the gap to complete coverage. The pre-registered prediction that structure handed to the
agent would help (P3-H3) is therefore **not supported** in this pilot. The diagnostic value is the
main payoff: because the bottleneck is *not* identifying which claims are affected — the agents are
told and still under-edit — the failure lies downstream, in actually performing the edits and
re-deriving numerics. We flag two caveats so this null is not over-generalized: the hint is phrased
"*possibly* affected" alongside an instruction that unaffected claims MUST be left unchanged (a weak,
conservatism-biased design), and each condition is a single draw. A stronger ablation (authoritative
"these MUST change + recompute" hint, plan-then-edit scaffolds, an explicit recompute tool, and an
identify-vs-list-vs-recompute error decomposition) is pre-registered before concluding that structure
*cannot* help an agent. Even so, this null is what localizes the open problem to a structured,
recompute-capable maintenance pipeline rather than to better prompting.

**6.3 Construction-determined consistency check (deterministic arms — NOT an empirical result).**
Against the gold computed by the separate world-physics code path, the typed-graph analyzer plus
constrained patch shows ACR = UCP = 1.00. **This is construction-determined and must not be read as a
method beating baselines.** The analyzer is fed the gold dependency graph; its predicted affected set
equals `gold_A` by construction; and the patch reads its values directly from `world.post_values`
(the gold), so it performs **no re-derivation** — the very step the real agents fail at (Section 6.2).
The two foils are likewise hand-coded, not run systems: full_regen marks the entire ASSERTED set as
edited, so UCP = 0.00 follows by construction even though it writes the *correct* gold values — UCP
penalizes *touching* a claim, not *changing* it. That 0.0 is therefore an **upper-bound illustration,
not a realistic baseline**, and it directly contradicts Mr.DRE's *measured* regression magnitude of
16–27% ~\cite{mrdre2026} (real regeneration does not destroy 100% of preserved claims). The flat
ledger's ACR = 0.13 likewise falls out of the fixed topology (e.g. no claim directly cites the
temporal evidence, so a direct-cite-only ledger flags nothing on temporal deltas). The only honest
reading of this block is a consistency check: the analyzer agrees with the independent gold code path,
and a flat ledger structurally under-recalls on derived/temporal claims. A negative-control
(irrelevant) update yields an empty gold `A`, which the analyzer correctly predicts. We do **not**
present this as evidence for the method (P3-H4); de-oracling it is the load-bearing required
experiment (Section 9).

**6.4 The divergence gate (H_DIVERGE) — illustration only, not a passed kill-gate.** The
pre-registered gating question is whether an evidence-world delta induces a different obligated-change
set than an equivalent author-style manuscript edit (without which the evidence-world framing would be
cosmetic). The divergence harness (`diverge.py`) is built, but as implemented it **cannot fail**:
`AUTHOR_EDIT_EDGES` deliberately excludes `NUMERIC_DEPENDENCY` and `TEMPORAL_DEPENDENCY` by fiat,
while the evidence-world analyzer follows all propagating edges, so any "divergence" (e.g.
`divergence = 0.5`, `missed_by_author = ['cProj']` on the temporal case) is **manufactured by the
edge-type partition**. We therefore reframe this as an **illustration of the edge-type distinction,
not a passed kill-gate**: a real author editing "the current rate" in prose would plausibly know the
projection depends on it, which this strawman author model assumes away. The **real, falsifiable
H_DIVERGE** — divergence against a genuine author-edit reformulation (human or agent author edits) —
is **unrun**. No H_DIVERGE result is claimed here.

## 7. Related work

We credit the two Director-verified adjacent results we build on and concede their respective halves.
**EditPropBench** ~\cite{editpropbench2026} introduces the change/preserve dual metric and the "~30%
of obligated updates missed" headline, but on synthetic *author* manuscript edits with no agent, audit
trail, or evidence-world trigger; we adopt the dual objective and differentiate by the evidence-world
delta. **Mr.DRE** ~\cite{mrdre2026} shows deep-research agents regress on non-target content and
citations (a measured 16–27% magnitude) during multi-turn *revision driven by user feedback*; we build
on that phenomenon but our unit is evidence-delta → claim-impact, with gold
affected/unaffected/new/contested sets.

The remaining neighbors each own one component but not the conjunction on report prose under an
evidence-world delta; pending Director verification we refer to them descriptively only and do not
cite them as established precedent: the base task of updating a document to reflect new evidence
(FRUIT) [unverified — pending Director verification]; generation-time claim-evidence provenance and
audit (AAR) [unverified — pending Director verification]; graph/rule-guided propagation of updates to
dependent facts in parameter/KB space (ChainEdit, RippleEdits) [unverified — pending Director
verification]; honest handling of conflicting evidence as QA (RAMDocs) [unverified — pending Director
verification]; and staleness from real timestamped evidence (evolveQA) [unverified — pending Director
verification]. None revise a deep-research report under an evidence-world delta with a typed
dependency-graph patch and joint stale+spurious metric. See `novelty/novelty_attack.md` for the full
adversarial sweep.

## 8. Limitations / Ethics

This is a pilot, and we keep its claims narrow. (i) **The central claim is the empirical negative, not
a method.** The supported results are the real-agent stale residual (ACR 0.34–0.39 at UCP ~ 1.0) and
the H3 null (typed hint does not help, ACR 0.33). (ii) **The deterministic 1.0/0.0/0.13 is a
construction-determined consistency check, not a comparative result:** the typed-graph arm is
oracle-fed and reads gold values; the foils are hand-coded; the 0.0 is a touch-penalty artifact that
contradicts Mr.DRE's measured 16–27% regression; the 0.13 falls out of one fixed topology. (iii)
**Ceiling confound on UCP:** for the real agents UCP ~ 1.0 is the mechanical dual of under-editing
(a do-nothing agent scores UCP = 1.0), so the joint pair collapses to ACR; the joint-metric selling
point adds nothing for the real arms. (iv) **Scale and statistics:** 18 worlds (3 seeds × 6 delta
types) on a *single fixed 10-claim topology* (≈6 structural scenarios; seeds only reroll numbers),
72 episodes, one draw per condition, no CIs, no per-delta-type breakdown, version-unpinned product
CLIs; "reproduced across two families" should be read as *directional agreement*, not robustness.
(v) **Shared-prompt confound:** both families see the same conservatism-instructing prompt, so
cross-family agreement may partly reflect the prompt. (vi) **Synthetic worlds only:** the real
versioned-evidence layer (Layer B) is built into the design but unrun, so transfer (H5) is untested.
(vii) **H_DIVERGE is an illustration, not a passed gate:** as built it cannot fail; the falsifiable
version is unrun. LLM judges are not used for the primary endpoint (the deterministic gold); they
remain secondary and gated to the real subset with human agreement. **Ethics:** real sources will be
stored as URL + hash + snapshot (not full text), license-respecting, with medical/legal-advice
domains excluded from the first batch.

## 9. Honest status and path to a full paper

**(a) What is delivered / SUPPORTED now.**
- A released, reproducible controlled-world harness: world generator, typed-graph analyzer,
  deterministic baselines, joint (ACR, UCP) metrics, and an immutable 72-episode ledger that
  reproduces every number in this draft (infrastructure deliverable).
- The central empirical finding (pilot-scale): two real subscription-CLI agent families, given an
  evidence-world delta with derivation rules in-prompt, recover only ~1/3 of obligated downstream
  updates (Claude ACR = 0.39, Codex ACR = 0.34; UCP ~ 1.0), well above a flat ledger (~2.6–3×) but far
  below complete.
- The honest H3 null: handing the agent the typed-graph affected set does not raise recall (ACR 0.33),
  localizing the failure to edit/re-derivation, not identification.
- A construction-determined consistency check that the typed-graph analyzer agrees with the independent
  gold code path and that a flat ledger structurally under-recalls — labeled as such, not as a method
  result.

**(b) Pre-registered / unrun (NOT claimed as results).**
- A de-oracled, actually-recomputing end-to-end typed-graph + constrained-patch method (the current
  arm reads `world.post_values` and is not exercised).
- A *falsifiable* H_DIVERGE against a real author-edit reformulation (the current harness is rigged to
  pass by edge-type partition).
- The real versioned-evidence layer (Layer B) and transfer (H5).
- Confidence intervals, per-delta-type breakdown, repeated agent draws, and version-pinned model
  builds.

**(c) Concrete required experiments to become a full paper** (from the red-team review):
1. **De-oracle the method:** an end-to-end pipeline that actually recomputes values (not reading
   `world.post_values`), ideally driving a real agent for the edit/derivation step; report ACR / UCP /
   calculation_correctness as a *system*. (Load-bearing; currently missing.)
2. **Real, run baselines:** replace hand-coded full_regen / flat_ledger with prompted agent baselines
   (a real "regenerate the report" agent; a real "fix only the cited claim" agent); fix UCP to
   penalize *value change*, not mere touching (or report both).
3. **Make H_DIVERGE falsifiable:** test divergence against a real author-edit reformulation (human or
   agent author edits), not a hand-partitioned edge set that excludes numeric/temporal by fiat.
4. **Scale + statistics:** multiple report topologies (vary depth, breadth, |A|/|U|, non-arithmetic
   derivations), longer reports, more seeds; repeated agent draws per condition; world-clustered
   bootstrap CIs; per-delta-type breakdown; honor the pre-registered mixed-model analysis;
   version-pin / record exact model builds.
5. **Proper structure-help ablation (re-test H3):** authoritative hint ("these MUST change +
   recompute"), plan-then-edit scaffolds, explicit recompute tool, and an identify-vs-list-vs-recompute
   error decomposition before concluding structure cannot help an agent.
6. **Run Layer B (real versioned evidence):** transfer (H5) is the external-validity requirement and
   is entirely unrun.
7. **Head-to-head vs the EditPropBench protocol** on the same evidence-world tasks, to demonstrate
   non-reducibility.
8. **Citations:** done in this revision — the off-topic `cc02xiang2026` and `agentassay2026` citations
   are removed; only Director-verified `mrdre2026` and `editpropbench2026` are cited, with all other
   neighbors held to "[unverified — pending Director verification]".

**Current honest tier:** a workshop-tier pilot plus released dataset/harness note — a well-instrumented
empirical negative on a single fixed topology — **not** a finished venue submission and **not** the
method paper an earlier framing advertised.
