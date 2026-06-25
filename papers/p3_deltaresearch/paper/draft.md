# DeltaResearch: A No-Gold Claim-Dependency Pipeline Closes the Downstream-Update Gap That Stalls Deep-Research Agents under Evidence-World Deltas — A Controlled Pilot

> DRAFT — strong controlled, **no-gold** pilot (ARXIV_ONLY tier), NOT a finished TACL submission. Written
> evidence-first from `evidence/claimpatch_2026-06-25.md` (headline result) and
> `evidence/pilot_2026-06-25.md` (motivating finding); every Results number is verbatim. Two halves:
> (a) a *motivating* finding that real deep-research agents miss most obligated downstream updates under
> an evidence-world delta and that handing them the affected set does not help; (b) the *headline* — a
> genuine no-gold pipeline (ClaimPatch) that infers the claim dependency structure from text and
> deterministically recomputes downstream, significantly beating the naive agent on diverse-topology
> worlds. The oracle / full-gold conditions remain **upper bounds** (consistency checks), distinct from
> the no-gold pipeline and not conflated with it. Honest boundaries (parents still named in claim text;
> controlled synthetic only; single draw, 24 worlds, two families; numeric/retraction deltas only; no
> human adjudication) are stated prominently.

## Abstract

Deep-research agents must keep long reports consistent when the underlying *evidence world* changes — a
source is revised or retracted — not only when an author edits the prose. Prior work shows agents regress
during multi-turn revision (Mr.DRE) and measures change/preserve adherence for author edits on synthetic
manuscripts (EditPropBench), but the evidence-world delta trigger and the maintenance of derived,
recomputed claims remain open. We first reproduce the phenomenon on real subscription-CLI agents: across
18 controlled worlds, two families (Claude, Codex/gpt-5.5) given an evidence-world delta *with the
derivation rules stated in-prompt* recover only about one third of the claims that must change
(Affected-Claim Recall, ACR = 0.39 and 0.34) while preserving unaffected claims (Unaffected-Claim
Preservation, UCP ~ 1.0); handing them the typed-graph affected set does not help (ACR = 0.33),
localizing the bottleneck to re-derivation, not identification. Our main contribution is a **no-gold**
end-to-end pipeline, **ClaimPatch**, that infers the claim dependency structure from claim text alone
(never a gold graph, gold affected set, or gold post-update value) and then has a deterministic
calculator recompute downstream values. On 24 diverse-topology controlled worlds (chain / tree / diamond
/ fan-in / fan-out / mixed; numeric-revision and retraction deltas) with the same two real agents,
ClaimPatch reaches ACR = 1.00 for both families against naive ACR of 0.25 (Claude) and 0.54 (Codex) — a
world-clustered bootstrap gain of +0.75 [0.58, 0.92] and +0.46 [0.25, 0.67], both CIs excluding 0. When
the report hides the operation (parents named, derivation type not), the naive agent degrades further
(Claude ACR = 0.08) while ClaimPatch still reaches 1.00 (+0.92 [0.79, 1.00]; Codex +0.48 [0.29, 0.69]).
A stage diagnostic explains why: inferred-vs-gold edge precision and recall are 1.00, and operation
accuracy is 0.96–1.00 *even when the operation is hidden*, so the agent recovers the dependency graph
near-perfectly and the deterministic recompute supplies the values the naive agent omits. ClaimPatch
matches the deterministic upper bound (oracle graph+recompute / full gold = 1.00), where gold is computed
by an **independent world-physics recompute on a separate code path**, validating rather than
tautologizing the result. Boundaries: parents are still *named* in claim text (fully-implicit reports
untested), worlds are controlled-synthetic (no real-evidence layer yet), each condition is a single draw
over 24 worlds and two model families, only numeric and retraction deltas are covered, and there is no
human adjudication. We therefore position this as a strong controlled, no-gold pilot, and a TACL-track
foundation once the real-evidence layer, human adjudication, more delta types, and repeats are added.

## 1. Introduction

Consider a deep-research report that states "the regional employment figure is 412,000" and, two
sentences later, "the composite activity index stands at 1.07" — where the index is computed from the
employment figure together with two other series. Now the source revises the employment figure to
418,000. Faithful maintenance is not a free-text rewrite: the directly-cited number *must* change, and
the composite index *must* be recomputed and changed because it is *derived from* the revised input. An
agent that edits only the directly-cited figure leaves a stale, internally-inconsistent index behind; an
agent that regenerates the whole report risks silently overwriting still-correct claims. The hard cases
are precisely the *downstream* obligations — derived, recomputed claims that no longer sit next to the
source that changed.

We study this **evidence-world delta** setting, in which the trigger is a change to the sources (a
numeric revision or a source retraction here) rather than an author's manuscript edit. We first establish
the problem on real systems. Two independent real agent families — Claude and Codex (gpt-5.5), run
through subscription CLIs at no API cost — given such a delta *with the derivation rules stated
in-prompt*, recover only about one third of the claims that must change (ACR = 0.39 for Claude, 0.34 for
Codex) while leaving unaffected claims essentially intact (UCP ~ 1.0). Crucially, *handing* the agent the
typed-graph affected set does not raise its recall (ACR = 0.33): the agents are told which claims are
affected and still under-edit. This null localizes the bottleneck to **re-derivation, not
identification** — the agent knows *what* to change but does not reliably recompute the new values.

Our headline contribution acts on exactly that diagnosis. **ClaimPatch** is a no-gold, end-to-end
pipeline: from the old report (claim texts, values, citations), the sources, and the observable evidence
delta — and *never* a gold dependency graph, gold affected set, or gold post-update value — it (i) infers
the claim dependency structure from the claim text, and then (ii) lets a **deterministic calculator**
recompute downstream values along that inferred structure. Because the load-bearing re-derivation step is
moved out of the language model and into deterministic computation, ClaimPatch closes the gap the naive
agent leaves open. On 24 diverse-topology controlled worlds with the same two real agents, ClaimPatch
reaches **ACR = 1.00** for both Claude and Codex, versus naive ACR of 0.25 (Claude) and 0.54 (Codex), a
world-clustered bootstrap gain of **+0.75 [0.58, 0.92]** and **+0.46 [0.25, 0.67]** — both confidence
intervals exclude 0. When the report *hides the operation* (the claim names its parent entities but not
the derivation type), the naive Claude agent collapses to ACR = 0.08 while ClaimPatch still reaches 1.00
(+0.92 [0.79, 1.00]; Codex +0.48 [0.29, 0.69]). This is a genuine no-gold method result, not a gold-fed
consistency check.

We concede up front the two adjacent prior results we build on, both Director-verified. Mr.DRE
~\cite{mrdre2026} establishes that deep-research agents regress during multi-turn revision (a measured
16–27% regression magnitude), and EditPropBench ~\cite{editpropbench2026} introduces the change/preserve
dual metric and the "~30% of obligated updates missed" headline for author edits on scientific
manuscripts. We adopt their dual objective and their phenomenon, and differentiate on the
*evidence-world* trigger and a *no-gold structure-inference + deterministic-recompute* method.
Concretely, this pilot contributes:

1. **A released controlled DeltaBench harness** with diverse random-DAG topologies and programmatic gold
   A/U computed by an *independent world-physics recompute* (a separate code path from the analyzer),
   joint (ACR, UCP) plus harmful-edit and calculation-correctness metrics, and an immutable episode
   ledger (Section 3; infrastructure, SUPPORTED).
2. **The motivating finding (RQ1):** two real agent families recover only ~1/3 of obligated downstream
   updates (Claude ACR = 0.39, Codex 0.34; UCP ~ 1.0), and handing them the typed-graph affected set
   does not help (ACR = 0.33) — localizing the failure to re-derivation, not identification (Section 6.1;
   SUPPORTED).
3. **The headline no-gold method (RQ3):** ClaimPatch infers dependency structure from claim text and
   deterministically recomputes downstream, reaching ACR = 1.00 vs naive 0.25 / 0.54 (named reports) and
   vs 0.08 / 0.52 (operation-hidden reports), with all four pipeline−naive gains' CIs excluding 0
   (Sections 4 and 6.2; SUPPORTED, no gold consumed).
4. **A stage-wise diagnostic (RQ2)** that explains the gain mechanistically: inferred-vs-gold edge
   precision/recall = 1.00 and operation accuracy = 0.96–1.00 even when the operation is hidden, so the
   bottleneck is re-derivation, which ClaimPatch supplies deterministically (Section 6.3; SUPPORTED).
5. **Upper-bound validation, kept honest:** the oracle (graph+recompute) and full-gold conditions are
   1.00 and are reported as *upper bounds / consistency checks*, distinct from the no-gold pipeline;
   because gold is computed by an independent recompute on a separate code path, ClaimPatch matching that
   bound validates rather than tautologizes (Section 6.4; honest framing).

## 2. Problem: evidence-world deltas, not author edits

We separate the *evidence world* `W_t` (sources with values, validity, authority) from the *report* `R_t`
(atomic claims with support edges, derivations). An update is a delta `ΔW`; in this pilot the realized
delta types are **numeric revision** and **source retraction**. The gold impact partitions claims into
`A` (must change) and `U` (must preserve). The objective is to correctly update `A` and preserve `U`
while keeping calculations valid — *not* to minimize character diff. Per the formal protocol (spec §C),
the method receives only `W0`, `R0`, and the observable `ΔW / W1`; it must not receive `A`, `U`, gold
dependency edges, or gold post-update values. The no-gold guarantee is the central design constraint of
this draft, and the pipeline's input view (`r0_view()`) was verified to expose none of those gold
objects (`test_p3_claimpatch`).

## 3. DeltaBench (controlled layer) + programmatic gold

We generate fully-verifiable worlds (`controlled_worlds/generator.py`) with **diverse random DAG
topologies** — chains, trees, diamonds, fan-in (one claim from many parents), fan-out (one source into
many claims), and mixed — yielding evidence and typed claims (base measurements plus derived
quantities). After a delta, gold `A`/`U` and the expected revised values are computed by an **independent
world-physics recompute**: the fact graph is re-evaluated and pre/post values and citations are diffed.
This recompute is a *separate code path* from the structure ClaimPatch infers, so when the no-gold
pipeline matches the gold it is being checked against an independently-derived answer rather than against
its own internal bookkeeping. The harness, gold generator, baselines, joint metrics, and the immutable
episode ledger (`artifacts/p3v2_ledger.jsonl` for named reports, `artifacts/p3v2_vague_ledger.jsonl` for
operation-hidden reports) are the released deliverable.

## 4. Method: ClaimPatch (no-gold, end-to-end)

ClaimPatch (`claimpatch.py`) consumes only `R0` (claim texts, values, citations), the sources, and the
observable evidence delta. Its stages are:

1. **Dependency-structure inference (LLM).** From the claim text alone, the model predicts the typed
   dependency edges among claims (which claim is derived from which parents) and the **operation** that
   combines the parents (sum, margin, share, index, projection, …). No gold graph or gold affected set is
   provided.
2. **Affected-set propagation (deterministic).** Given the delta, the changed source's claims and their
   transitive descendants along the *inferred* edges are marked as the predicted affected set.
3. **Deterministic recompute.** A calculator re-evaluates each affected derived claim from its inferred
   operation and its (recomputed) parents' values — the language model does **not** produce the new
   numerics. This is the step the naive agent fails (Section 6.1).
4. **Constrained patch + verification.** Only claims in the predicted affected set are edited; unaffected
   claims are left untouched, and calculation/citation validity is checked.

This is the de-oracled pipeline that earlier drafts only pre-registered: the re-derivation step is now
actually exercised, and it reads *no* gold values. Baselines and upper bounds (spec §G): the **naive
LLM** "update this report" prompt (an actual prompted baseline run on both real families); and the
diagnostic **upper bounds** — *oracle graph+recompute* (gold graph, real recompute) and *full gold* —
which are always labeled as upper bounds, never as the method.

## 5. Experimental setup

We run two complementary studies. **(A) Motivation / RQ1 (pilot):** 18 controlled worlds (3 seeds × 6
effectful delta types) on a fixed topology, 72 LLM episodes (2 families × 2 prompt arms × 18 worlds);
arms are the naive LLM patch and the LLM patch *given the typed-graph affected set as a hint*.
**(B) Headline / RQ3 (ClaimPatch):** 24 controlled worlds with diverse random DAG topologies and
numeric-revision and retraction deltas, in two phrasing conditions — **named** reports (the claim text
states the derivation type) and **vague** reports (the claim names its parent entities but *hides* the
operation, e.g. "Metric d2, derived from Region A revenue and Region B revenue, is 260"); arms are the
naive LLM and the no-gold ClaimPatch pipeline, plus the oracle / full-gold upper bounds. Models in both
studies are Claude (`claude:claude-cli`) and Codex (`codex:codex-cli`, gpt-5.5), run at no API cost; the
underlying build is not version-pinned in the ledger, so the "gpt-5.5" identity is asserted, not pinned.
Significance is a **world-clustered bootstrap** over the 24 worlds (paired pipeline−naive per world).
**Scope:** controlled synthetic worlds; each model condition is a *single draw* (within-condition
variance unmeasured); numeric and retraction deltas only; no human adjudication. Figures
`figures/generated/fig_acr_by_arm.pdf` (ACR by arm) and `figures/generated/fig_frontier.pdf` (the
affected-recall / harmful-edit frontier) summarize the headline study.

## 6. Results

All numbers below are verbatim from `evidence/claimpatch_2026-06-25.md` (headline study) and
`evidence/pilot_2026-06-25.md` (motivation). We report the joint pair (ACR, UCP) plus harmful-edit and
calculation-correctness, never a maskable single average.

**6.1 Motivation (RQ1): real agents miss most downstream obligations, and the affected-set hint does not
help.** In the pilot (18 worlds, 72 episodes), given the evidence-world delta as a natural-language
description plus the report's atomic claims *and the derivation rules in-prompt*, both real families
recover only about one third of the claims that must change: **Claude ACR = 0.39** and **Codex ACR =
0.34** (i.e. they miss ~61% and ~66% of obligated updates), while leaving unaffected claims almost
entirely intact (**UCP = 1.00** and **0.99**). Handing the agent the typed-graph affected set as an
explicit hint did *not* raise recall — **Claude 0.39 → 0.33**, **Codex 0.34 → 0.33** (UCP ~ 1.0 in both
arms). The agents are told which claims are affected and still under-edit, which **localizes the
bottleneck to re-derivation, not identification.** The headline study's naive arms reproduce this
under-recall on diverse topologies (Claude ACR = 0.25, Codex 0.54 with the derivation type named; Claude
0.08, Codex 0.52 with the operation hidden — see 6.2), so the phenomenon is not an artifact of the fixed
pilot topology. We note that UCP ~ 1.0 for these naive arms is the mechanical dual of conservative
under-editing — a do-nothing agent also scores UCP = 1.0 — so for the naive arms the joint pair
effectively collapses to ACR.

**6.2 Headline (RQ3): the no-gold ClaimPatch pipeline reaches ACR = 1.00 and significantly beats the
naive agent.** ClaimPatch infers the dependency structure from claim text and recomputes downstream
deterministically, *consuming no gold*. On the 24 diverse-topology worlds:

*Named reports (derivation type stated in claim text):*

| arm | model | ACR | UCP | harmful-edit | calc-correct |
|---|---|---|---|---|---|
| naive LLM | Claude | 0.25 | 1.00 | 0.00 | 0.74 |
| naive LLM | Codex | 0.54 | 1.00 | 0.00 | 0.99 |
| **no-gold ClaimPatch** | Claude | **1.00** | 1.00 | 0.00 | 1.00 |
| **no-gold ClaimPatch** | Codex | **1.00** | 1.00 | 0.00 | 1.00 |
| oracle (graph+recompute / full gold) — *upper bound* | — | 1.00 | 1.00 | 0.00 | 1.00 |

Pipeline − naive ACR (world-clustered bootstrap, n = 24): **Claude +0.75 [0.58, 0.92]; Codex +0.46
[0.25, 0.67] — both CIs exclude 0.**

*Operation-hidden ("vague") reports (parents named, operation inferred):*

| arm | model | ACR | UCP | harmful-edit | calc-correct |
|---|---|---|---|---|---|
| naive LLM | Claude | 0.08 | 1.00 | 0.00 | 0.58 |
| naive LLM | Codex | 0.52 | 0.99 | 0.01 | 0.97 |
| **no-gold ClaimPatch** | Claude | **1.00** | 0.97 | 0.03 | 1.00 |
| **no-gold ClaimPatch** | Codex | **1.00** | 0.96 | 0.04 | 0.97 |

Pipeline − naive ACR: **Claude +0.92 [0.79, 1.00]; Codex +0.48 [0.29, 0.69] — both CIs exclude 0.**

In all four model × phrasing cells ClaimPatch reaches ACR = 1.00, recovering the full downstream cascade
the naive agent leaves stale, with harmful-edit at 0.00 (named) and 0.03–0.04 (operation-hidden) and
calculation-correctness 0.97–1.00. The naive agent is both incomplete and *fragile to phrasing*: hiding
the operation pushes naive Claude from 0.25 down to 0.08, whereas ClaimPatch is unaffected (1.00). The
small UCP dip (0.97 / 0.96) and harmful-edit (0.03 / 0.04) in the operation-hidden condition trace to the
~2–4% operation-inference errors quantified in 6.3. This is the headline no-gold result: consuming no
gold graph, affected set, or post-update value, the pipeline *significantly* improves affected-claim
recall over the naive agent on diverse topologies under both phrasings (four CIs, all excluding 0). The
arm comparison and recall/harmful-edit frontier are plotted in `figures/generated/fig_acr_by_arm.pdf` and
`figures/generated/fig_frontier.pdf`.

**6.3 Stage diagnostic (RQ2): why it works — structure inference is near-perfect; re-derivation was the
bottleneck.** Over 96 derived claims per model, the inferred-vs-gold structure shows **edge precision =
1.00, edge recall = 1.00, operation accuracy = 1.00, derived-exact = 1.00** for both Claude and Codex on
named reports. When the operation is *hidden*, edge precision and recall stay at **1.00** and operation
accuracy is **0.98 (Claude) / 0.96 (Codex)** — the model infers the hidden operation from the named
parents plus the stated value. So when the report states (or even merely implies, via named parents) its
derivations, the LLM recovers the dependency graph essentially perfectly; what the naive prompt fails to
do is *trigger systematic propagation and recompute*. The diagnostic confirms the RQ1 localization: the
bottleneck is the editing / re-derivation step, not identification, and a pipeline that forces a
deterministic recompute along the inferred graph closes the gap — with no gold.

**6.4 Upper bounds, kept honest (consistency check, not conflated with the method).** The oracle
(graph+recompute) and full-gold conditions reach ACR = UCP = 1.00. These remain **upper bounds /
consistency checks**, distinct from the no-gold pipeline: they are entitled to the gold graph and/or gold
values, whereas ClaimPatch is not. The honest force of the headline is that the **no-gold** pipeline
*matches* this upper bound. Because the gold is computed by an independent world-physics recompute on a
*separate code path* from the structure ClaimPatch infers (Section 3), the match validates the pipeline
against an independently-derived answer rather than tautologizing it. We keep the earlier "consistency
check" framing for the gold-fed deterministic arm intact — it is an upper bound and was never a method
result — and we do not present it as evidence for ClaimPatch; the ClaimPatch numbers in 6.2 stand on
their own, gold-free.

## 7. Related work

We credit the two Director-verified adjacent results we build on and concede their respective halves.
**EditPropBench** ~\cite{editpropbench2026} introduces the change/preserve dual metric and the "~30% of
obligated updates missed" headline, but on synthetic *author* manuscript edits with no agent, audit
trail, or evidence-world trigger; we adopt the dual objective and differentiate by the evidence-world
delta and a no-gold structure-inference + deterministic-recompute method. **Mr.DRE** ~\cite{mrdre2026}
shows deep-research agents regress on non-target content and citations (a measured 16–27% magnitude)
during multi-turn *revision driven by user feedback*; we build on that phenomenon but our unit is
evidence-delta → claim-impact with gold affected/unaffected sets and a deterministic recompute.

The remaining neighbors each own one component but not the conjunction on report prose under an
evidence-world delta with a no-gold typed-dependency method; pending Director verification we refer to
them descriptively only and do not cite them as established precedent: the base task of updating a
document to reflect new evidence (FRUIT) [unverified]; generation-time claim-evidence provenance and
audit (AAR) [unverified]; graph/rule-guided propagation of updates to dependent facts in parameter/KB
space (ChainEdit, RippleEdits) [unverified]; honest handling of conflicting evidence as QA (RAMDocs)
[unverified]; staleness from real timestamped evidence (evolveQA) [unverified]; and LLM-automated
evidence surveillance over a living synthesis (Living Systematic Review engine) [unverified]. None infer
a typed claim dependency graph from text and recompute downstream report claims under an evidence-world
delta with no gold. See `novelty/novelty_attack.md` for the full adversarial sweep.

## 8. Limitations / Ethics

We keep the claims narrow. (i) **Parents are still named.** In both named and operation-hidden conditions
the claim text *names the parent entities*; a fully-implicit report where parents are unnamed is
underdetermined and **untested**, and structure inference could degrade there. This is the most important
boundary on the headline. (ii) **Controlled synthetic only.** Worlds are generated; the real
versioned-evidence layer (spec §E) is designed but **unrun**, so external-validity transfer (RQ4) is
untested. (iii) **Scale and statistics.** 24 worlds (headline) and 18 worlds (motivation), two model
families, a **single draw** per condition (within-condition variance unmeasured); CIs are
world-clustered bootstraps over worlds, not over repeated agent draws; model builds are not
version-pinned. (iv) **Delta coverage.** Only numeric-revision and source-retraction deltas are realized;
categorical/conflict/temporal-validity/definition/unit deltas in the spec taxonomy are not yet run, so
ACR = 1.00 should be read as "on numeric/retraction deltas over these topologies," not "in general."
(v) **No human adjudication.** Gold is deterministic recompute; there is no human-labeled real subset and
no inter-annotator agreement. (vi) **UCP ceiling for naive arms.** UCP ~ 1.0 for the naive agents is the
mechanical dual of under-editing, so for those arms the joint pair effectively collapses to ACR; the
preservation axis becomes informative only for ClaimPatch under the operation-hidden condition (UCP
0.96–0.97). We use conservative verbs throughout — we *observe* and *estimate*; we do not claim the
method "solves" or "proves" report maintenance. **Ethics:** when the real-evidence layer is built, real
sources will be stored as URL + hash + snapshot (not full text), license-respecting, with medical /
legal-advice domains excluded from the first batch. LLM judges are not used for the primary endpoint (the
deterministic gold).

## 9. Honest status and path to a full paper

**(a) What is delivered / SUPPORTED now.**
- A released controlled DeltaBench harness with diverse random-DAG topologies, independent-recompute
  gold, joint (ACR, UCP) + harmful-edit + calculation-correctness metrics, and an immutable episode
  ledger that reproduces every number in this draft.
- The motivating finding (RQ1): two real agent families recover only ~1/3 of obligated downstream updates
  (Claude ACR = 0.39, Codex 0.34; UCP ~ 1.0), and handing them the typed-graph affected set does not help
  (ACR = 0.33) — bottleneck is re-derivation, not identification.
- The headline no-gold method (RQ3): ClaimPatch reaches ACR = 1.00 for both families vs naive 0.25 / 0.54
  (named) and 0.08 / 0.52 (operation-hidden); pipeline − naive gains +0.75 [0.58, 0.92], +0.46 [0.25,
  0.67], +0.92 [0.79, 1.00], +0.48 [0.29, 0.69] — all four CIs exclude 0; consuming no gold.
- The stage diagnostic (RQ2): edge precision/recall = 1.00 and operation accuracy 0.96–1.00 even when the
  operation is hidden, with ClaimPatch matching the oracle / full-gold upper bound (1.00) validated by an
  independent recompute.

**(b) Concrete required experiments to reach a full TACL paper.**
1. **Real versioned-evidence layer (RQ4).** Build and run Layer B (official statistical revisions,
   documentation/release-note histories, arXiv corrections/retractions) and show the no-gold gains
   transfer from controlled worlds to real version pairs. This is the central external-validity gate.
2. **Human adjudication.** Add two-annotator-plus-adjudication labels (or, if single-human, an explicitly
   single-annotator protocol with a blinded audit) on the real subset; do not state inter-annotator
   agreement without a second annotator.
3. **More delta types.** Extend beyond numeric-revision and retraction to categorical status change,
   source conflict, temporal-validity expiry, definition/unit change, and evidence deletion, with
   per-delta-type breakdowns; confirm the no-gold pipeline holds across them.
4. **Repeats and statistics.** Multiple agent draws per condition with world-clustered bootstrap CIs over
   draws (not only over worlds), the pre-registered mixed-model analysis (method × model × topology ×
   delta type), and version-pinned model builds.
5. **Fully-implicit reports.** Test reports whose claim text does *not* name the parent entities, to map
   where structure inference (and thus ACR) degrades — the boundary flagged in §8(i).
6. **Head-to-head vs the EditPropBench protocol** on the same evidence-world tasks, to demonstrate
   non-reducibility of the evidence-world trigger to an author edit.

**Current honest tier:** a strong controlled, **no-gold** pilot with a genuine method result —
ARXIV_ONLY now, and a credible TACL-track foundation once the real-evidence layer, human adjudication,
more delta types, and repeated draws are added. This is **not** a finished TACL submission.
