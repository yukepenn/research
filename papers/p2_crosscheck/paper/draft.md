# CrossCheck: Budget-Matched, Error-Correlation-Aware Routing for Heterogeneous Code Review

> DRAFT — pilot manuscript, written evidence-first from `evidence/pilot_2026-06-25.md`. Abstract,
> Introduction, and Results filled; the deterministic infrastructure result (P2-C0) is kept separate
> from the inconclusive, underpowered workflow pilot (P2-H2, PARTIAL). Numbers are pilot-scale; the
> differentiating empirical study is gated on a harder, mid-difficulty corpus.

## Abstract

Heterogeneous (cross-model) code review — having one model family review or repair code written by
another — is increasingly proposed as a way to make coding agents more reliable, and a concurrent
study shows that on code such review is direction-dependent and rarely beats the stronger model solo
~\cite{cc02xiang2026}. The decisive counterfactual that prior work omits is *budget*: a second model
costs an extra call, so the honest comparison is not review-versus-nothing but review-versus-giving
the same author that extra call. We add that budget-matched author-extra-compute arm, a defect-type
author×reviewer error-complementarity decomposition, and a pre-call, held-out-repository router over
review actions (ReviewRoute), on a controlled corpus of self-contained single-defect modules each
paired with a deterministic hidden test (LLM-free oracle). In a pilot of 10 controlled defect cases
× 2 author→reviewer pairs (Claude↔Codex/gpt-5.5) × 3 workflows (60 episodes), final-patch
correctness on the hidden test is **0.80 for all three workflows** — no-review, author-extra-compute,
and cross-family review tie exactly, identically for both authors. We read this as **inconclusive and
underpowered, not as a confirmation that cross-review is useless**: 8 of 10 defect types pass
one-shot (1.00) under both models and every workflow, and the only two non-ceiling cases were
*underspecified benchmark bugs* (the spec did not determine the hidden-test answer), which we fixed
and verified the model then passes one-shot — leaving an effectively all-ceiling corpus with no
headroom to separate review workflows. No author×reviewer complementarity is observable at this difficulty. The
pilot's real yield is a diagnosis and a method package: measuring when a second model is worth its
budget requires a *mid-difficulty, fairly-specified* corpus where no-review lands near 0.4–0.6, and
the budget-matched protocol, the complementarity model, and the ReviewRoute router (validated on
simulated data with a planted signal and a no-leakage repository split) are ready for it. Separately,
the deterministic infrastructure result holds: every mutation's hidden test passes on the clean
module and fails on the mutated one. Scope: pilot-scale, two model families, controlled toy corpus;
a harder natural near-miss corpus, ≥3 families, and held-out-repository router validation are the
gated full study.

## 1. Introduction

A second model is often treated as free reliability: if one coding agent can review or repair
another's patch, surely two heads beat one. But a second model is not free — it costs an extra
inference call — so the question that actually decides whether heterogeneous review is worth adopting
is not "does a reviewer help over nothing?" but "does spending that extra call on a *different* model
beat spending it on the *same* author?" A concurrent workshop study, cc02 ~\cite{cc02xiang2026}, runs
the bidirectional Claude↔Codex writer/reviewer matrix (including same-model self-review) on code and
finds that cross-model review is direction-dependent and that the stronger model solo sits on the
Pareto frontier — no reviewed condition beats it. cc02 compares review against *single-pass solo* and
against the *stronger model* solo; it never compares against giving the same author the equal extra
compute, models no mechanism for *when* a second model should help, and produces a single global
recommendation rather than a per-case router. That budget-matched counterfactual, a defect-type
complementarity mechanism, and a pre-call router are precisely the gaps this paper targets.

Our headline empirical finding is honest and negative-shaped: in a controlled pilot, no-review,
author-extra-compute, and cross-family review all reach **0.80** final-patch correctness — they are
indistinguishable. We are explicit that this does **not** confirm "cross-review is useless." It is an
underpowered result produced by a corpus that turned out to be too easy: strong models one-shot these
small, well-specified single-defect modules, so there is no regime in which any workflow can pull
ahead. Diagnosing *why* the corpus could not separate the workflows — and what a corpus that could
must look like — is the pilot's main contribution, alongside three pieces of methodology that the
nearest neighbor lacks. Concretely, this pilot contributes:

1. **A budget-matched author-extra-compute arm** (Section 4): at a fixed budget of two model calls we
   compare NO_REVIEW, AUTHOR_MORE_COMPUTE (author self-improves), and CROSS_FAMILY_REVIEW (a different
   family repairs), run bidirectionally — the counterfactual cc02 ~\cite{cc02xiang2026} and the
   adversarial cross-model critic line ~\cite{refutepromote2026} omit, and the one most likely to be
   decisive on a corpus with headroom.
2. **A deterministic, LLM-free defect corpus** (Section 3; P2-C0, SUPPORTED): self-contained modules
   with injected single defects across ten defect types, each paired with a hidden test verified to
   pass on the clean module and fail on the mutated one, giving an objective correctness endpoint that
   does not depend on an LLM judge — in the spirit of regression-testing harnesses for agent
   workflows ~\cite{agentassay2026}.
3. **A defect-type author×reviewer error-complementarity model** (Section 4): a decomposition that
   isolates the residual review gain beyond the reviewer's standalone strength (the author×reviewer
   interaction), validated on simulated data with a planted interaction; in this pilot it has no
   signal to recover because the corpus is all-ceiling.
4. **A pre-call, held-out-repository review router (ReviewRoute)** (Section 4): an interpretable
   value-based policy over review actions, trained with nested cross-validation whose outer fold is
   the repository (no repository leakage) and using only pre-review features; validated on simulated
   data against always-cross, always-self, random, and an oracle upper bound, and ready for the harder
   corpus.

The empirical reading (Section 6) and the diagnosis it forces — a mid-difficulty, fairly-specified
corpus where no-review lands near 0.4–0.6 — are reported honestly as the weakest of our pilots'
empirical findings, and as the difficulty bar the full study must clear.

## 2. Definitions
We separate latent defect, detected defect, false alarm, actionable localization, successful repair
(passes the hidden oracle), regression introduced, and spurious edit. Detection and repair are
scored separately so an accidental rewrite is not credited as review skill (manual 6.7).

## 3. Controlled defect corpus
Self-contained toy modules with injected single defects across ≥6 defect types
(`mutations/injectors.py`), each paired with a **deterministic hidden test** that passes on the
clean module and fails on the mutated one.

**Verified result (SUPPORTED, deterministic, P2-C0).** For every case the hidden test passes on the
clean variant and fails on the mutated variant; cases materialize identically in-process and in a
temp directory. This gives an objective, LLM-free correctness endpoint.

## 4. The decisive comparison: budget matching
The core methodological point cc02 lacks is a **budget-matched author-extra-compute arm**. We
compare at matched budget (2 model calls):
- `NO_REVIEW` (author once),
- `AUTHOR_MORE_COMPUTE` (author fixes, then self-improves — 2 author calls),
- `CROSS_FAMILY_REVIEW` (author fixes, a *different* model repairs — 2 calls),
run **bidirectionally** (Claude↔Codex). Final correctness is the deterministic hidden test.
Complementarity (`complementarity.py`) decomposes residual gain beyond reviewer standalone strength;
the pre-call router (`router.py`, nested CV with outer fold = repository, no leakage) selects the
review action. H2: cross-family review should NOT dominate equal author compute.

## 5. Experimental setup
Plan-then-repair harness: present the buggy module + spec, the author returns a corrected module, we
execute the hidden test. **Scope:** pilot-scale, controlled corpus, two model families; the natural
near-miss corpus, ≥3 families, 8 defect types, ≥10 repositories, and held-out-repo router validation
are the gated full study (FSE 2027 target, full paper deadline 2026-10-02 AoE).

## 6. Results

**Pilot.** Real models were run through subscription CLIs at no API cost: author/reviewer ∈ {`claude`,
`codex` (gpt-5.5)}, bidirectional. The design is 10 controlled defect cases × 2 author→reviewer pairs
× 3 workflows = 60 episodes in the immutable ledger (`paper_id=p2_crosscheck`). Final correctness is
the deterministic hidden test. We report this workflow pilot as **PARTIAL / underpowered (P2-H2)**,
and keep it strictly separate from the deterministic infrastructure result of Section 3 (P2-C0,
SUPPORTED), which does not depend on any model.

**6.1 The corpus is at the ceiling — lead with the diagnosis.** The single most important fact about
this pilot is that the corpus could not exercise the question it was built for. Per defect type, **8
of 10 defect types are solved one-shot (1.00) by *both* models under *every* workflow.** The only two
non-1.00 cells — `type_serialization` and `collateral_regression` — failed 0.00 under *all* workflows,
and on inspection both were **underspecified benchmark bugs, not model failures**:

- `type_serialization`: the spec said "a list" but the hidden test required a *sorted* list — the
  model cannot know to sort. We **fixed** the spec (it now states "sorted ascending"); Claude then
  solves it one-shot.
- `collateral_regression`: the spec ("`normalize()` silently changes dedup semantics") did not state
  that `normalize` must strip-only and not lowercase. We **fixed** the spec; Claude then solves it
  one-shot.

Both fixes were verified — with fair specs, both cases are now solved one-shot — and the two cases are
excluded from the workflow analysis (`exclusions.csv`), following the rule of fixing the benchmark
rather than charging the model for an unanswerable spec. The consequence is decisive for what this
pilot can and cannot say: after the fixes the corpus is **effectively all-ceiling**. Strong models
one-shot these small, well-specified single-defect modules, so there is no headroom in which any
review workflow can differentiate from any other.

**6.2 Final-patch correctness by workflow (matched budget = 2 model calls).** With the two benchmark-
bug cases in (8 cases at 1.00, 2 at 0.00, i.e. 8/10), the raw final-correctness rate is identical
across all three workflows:

| workflow | final correct | n |
|---|---|---|
| NO_REVIEW (author once) | 0.80 | 20 |
| AUTHOR_MORE_COMPUTE (author self-improves) | 0.80 | 20 |
| CROSS_FAMILY_REVIEW (other model repairs) | 0.80 | 20 |

The 0.80 is identical for both authors as well: Claude 0.80 / Codex 0.80 in every workflow. The two
failing cells were the *same* two (the benchmark bugs) under every workflow; once they are fixed or
excluded, all remaining cases pass under every workflow. There is therefore no workflow contrast to
report — not a small one, not a noisy one, but exactly zero spread.

**6.3 What this does and does not establish (H2, PARTIAL).** The pre-registered primary hypothesis
H2 — at matched budget, cross-family review does *not* beat author-extra-compute on average final-
patch correctness — is satisfied here only **trivially**. Cross-family review gives no net benefit
over giving the same author equal extra compute (0.80 = 0.80), which is consistent with H2 and with
cc02's "the stronger model solo is on the frontier" ~\cite{cc02xiang2026}. But both also tie
*no-review* (0.80 = 0.80 = 0.80), so the result is not "cross-review confirmed useless"; it is "no
workflow can be distinguished from any other on this corpus." That is an **underpowered** outcome
caused by the ceiling of Section 6.1, not evidence against (or for) the value of a second model. We
record P2-H2 as PARTIAL: no differentiation observed, underpowered by an all-ceiling corpus.

**6.4 No observable complementarity; mechanism and router untested on real data.** Because the same
hard cases failed under every workflow (when they existed) and everything else passes under every
workflow, there is **no author×reviewer complementarity signal to observe** at this difficulty
(P2-H3 remains UNTESTED). The complementarity decomposition (Section 4) and the ReviewRoute router
(Section 4) are therefore validated only on **simulated** outcome tables with a *planted* signal: the
decomposition recovers a planted author×reviewer×defect interaction beyond the reviewer main effect,
and the router, trained with the repository-as-outer-fold nested CV, beats always-cross, always-self,
and random on held-out repositories with no repository leakage and approaches the oracle upper bound.
These are pipeline-validation self-tests, **not findings on real model behavior** (P2-H5 remains
UNTESTED on real data); they show the analysis machinery is correct and would detect a real signal
if one existed.

**6.5 Diagnosis (the real pilot value).** Measuring when a second model is worth its extra call
requires a corpus with headroom. Concretely, the differentiating study needs a genuinely
**mid-difficulty, fairly-specified** defect corpus where NO_REVIEW lands around **0.4–0.6** — for
example the natural agent near-miss corpus on real repositories, with harder multi-file defects —
so that review workflows have room to move the correctness endpoint. The budget-matched protocol, the
author-extra-compute arm, the complementarity model, and the ReviewRoute router are ready; the
differentiating empirical result is gated on that harder corpus. This corpus-difficulty bar is the
pilot's most reusable finding: a controlled defect benchmark intended to measure review value must
first demonstrate that its no-review baseline is *not* at the ceiling.

## 7. Related work

We credit the two adjacent verified results we build on and concede their respective halves.
**cc02** (Cross-Model LLM Code Review, Xiang et al., Agentic SE @ KDD'26 ~\cite{cc02xiang2026}) runs
the bidirectional Claude↔Codex writer/reviewer/reviser matrix including same-model self-review on
code, and finds cross-model review is direction-dependent with the stronger model solo on the Pareto
frontier. We credit this headline and do not re-claim it; our contribution is the **budget-matched
author-extra-compute counterfactual** cc02 omits, a **defect-type complementarity mechanism**, and a
**pre-call held-out-repository router** over review actions — none of which cc02 has. **Refute-or-
Promote** ~\cite{refutepromote2026} uses an adversarial cross-model critic to filter false-positive
defect reports in a real field study; it owns "heterogeneous critique finds real code bugs" — a
detection/precision endpoint, not budget-matched final-patch correctness — which our boundary
explicitly does not re-claim. Our reliance on deterministic hidden tests to score non-deterministic
agents follows regression-testing practice for agent workflows ~\cite{agentassay2026}.

The remaining neighbors each own one component but not the conjunction; pending Director verification
we refer to them descriptively only. The budget-normalization stance — normalize compute and the
multi-agent advantage shrinks — has been argued for multi-hop reasoning under equal thinking-token
budgets [unverified — pending Director verification] and proven in closed form as a budget×error-
correlation phase transition for generic agent trees [unverified — pending Director verification]; we
instantiate the *code-review* case with an author-extra-compute counterfactual and a correctness
endpoint. The premise that heterogeneous models are not automatically error-diverse (population-level
correlated errors; cross-model clustering of self-review failures, e.g. r≈0.52 on code modernization)
is established prior motivation, not our contribution [unverified — pending Director verification].
Self-review unreliability and the context-separation confound (fresh-session review helps more than
re-review) motivate our same-family control [unverified — pending Director verification]. Pre-call
model routing for code exists for *which model generates* and for cost-tier selection, with OOD
generalization [unverified — pending Director verification]; our router is over a **review-action set**
(no-review / self / same-family / cross-family / test-gen / reimplementation), not single-model
selection. Controlled comparisons of multi-agent topologies for software *design*, and cross-model
disagreement as a label-free correctness signal with routing named as an application, are adjacent but
do not run the budget-matched, defect-type-conditioned, held-out review router we target [unverified —
pending Director verification]. See `novelty/novelty_attack.md` for the full adversarial sweep.

## 8. Limitations / Ethics

We keep this pilot's claims narrow, and the most important limitation is the one that shapes every
empirical reading above.

**(i) The corpus is at the ceiling — the dominant limitation.** Strong models one-shot these small,
well-specified single-defect modules, so the no-review baseline is at the ceiling (8/10 one-shot;
the two non-ceiling cases were benchmark bugs, now fixed). With no headroom, *no* review workflow can
differentiate from any other, and the workflow tie at 0.80 is **underpowered, not a negative result
about cross-review**. The differentiating study requires a mid-difficulty, fairly-specified corpus
where no-review lands near 0.4–0.6 (natural agent near-miss patches on real repositories, harder
multi-file defects); a controlled review benchmark must demonstrate its no-review baseline is off the
ceiling before any workflow contrast is meaningful.

**(ii) Scale and statistics.** Pilot-scale: 10 controlled defect cases × 2 author→reviewer pairs × 3
workflows (60 episodes), two model families; we report point values, not confidence intervals, and
the workflow contrast is exactly zero by construction of the ceiling, so no inferential test is
warranted here.

**(iii) Mechanism and router are validated only on simulated data.** The complementarity decomposition
and the ReviewRoute router recover a *planted* signal and pass a no-repository-leakage held-out split
in simulation; this is pipeline validation (P2-H3, P2-H5 UNTESTED on real data), not a finding about
real model behavior. The router has not been run on a corpus with real review-value signal.

**(iv) Toy modules and in-process execution.** Real-repository corpus is pending; in-process execution
of model-produced code is a sandboxing limitation, and the full study uses containerized repositories.

**(v) The deterministic result is separate and does hold.** The infrastructure result (P2-C0,
Section 3) — every mutation's hidden test passes on the clean module and fails on the mutated one,
materializing identically in-process and in a temp directory — is deterministic and independent of any
model; it should not be read as support for the workflow comparison, which is inconclusive.

**Ethics.** The defect study targets general correctness, not exploit development; the full study will
use only permissively-licensed, containerizable repositories with no production targets.
