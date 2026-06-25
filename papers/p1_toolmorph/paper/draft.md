# ToolMorph: A Label-Free Semantic Normal Form for Behavior-Preserving Tool-Interface Variation

> DRAFT — current tier: **PILOT + PRE-REGISTRATION (workshop / benchmark-note)**, NOT a finished
> flagship-venue submission. What is *delivered* today is (i) a property-verified equivalence
> benchmark (SUPPORTED, deterministic, model-independent) and (ii) a small, **statistically
> non-significant** pilot signal on enum-encoding (both CIs include zero). The PRIMARY contribution —
> the STNF remedy (H5) — is a **pre-registered plan, UNRUN**. See "Honest status and path to a full
> paper" (end). Evidence-first order (manual 2.0): every number comes from the immutable run ledger
> (`artifacts/run_ledger.jsonl`, 80 episodes, paper_id=p1_toolmorph) and the Director-verified
> aggregator (`artifacts/p1_interactive_result.json`); nothing is invented or extrapolated.

## Abstract
**Context.** Tool-using LLM agents are deployed against tool interfaces whose surface form varies even
when the underlying executor — and hence the environment state transition — is identical.
**Gap.** Prior work (PIPE) shows behavior-preserving interface rewrites change agent success and
diagnoses interface reliance, but provides no normalization remedy, no formal byte-level
state-transition-equivalence guarantee, and no transfer to unseen transform families.
**Approach.** We define tool-interface equivalence by audited byte-identical environment state
transitions, build six strict transform families over three stateful environments, and propose STNF,
a label-free Semantic Tool Normal Form that re-presents a deployed interface in canonical form via a
runtime codec.
**Study.** Pilot, subscription-CLI evidence on two model families (Claude Code; Codex / gpt-5.5), 10
base tasks across calendar / inventory / helpdesk, **80 episodes (none excluded** — the single
Claude/enum failure is a max_steps timeout in which the agent looped on opaque codes, counted as a
genuine agent failure per the updated analysis plan), paired across the original interface and three
equivalent transforms.
**Primary result (with uncertainty).** Under enum-encoding (opaque numeric codes for enum values)
both models showed a small drop — Claude 1.00→0.80 (Δ −0.20, bootstrap CI [−0.50, 0.00], n=10) and
Codex 1.00→0.90 (Δ −0.10, CI [−0.30, 0.00], n=10) — that is **NOT statistically distinguishable from
zero at this sample size (both CIs include 0): a directional pilot signal, not a confirmed effect.**
Structural nesting and lexical aliasing show **no drop** (Δ 0.00), but the 1.00 baseline ceiling means
this absence-of-effect cannot be distinguished from insufficient power. Only one of three exercised
transforms moved, and it moved within noise.
**Mechanism (hypothesis, not established).** The only family that moved removes human-legible enum
tokens, which is *consistent with* a semantic-decoding rather than a structural-parsing difficulty;
but at a 1.00 ceiling and with CIs spanning zero this is a hypothesis for the pre-registered study,
not an established mechanism. We do **not** claim the structurally recoverable transforms are
"absorbed losslessly" — zero drop at a ceiling is indistinguishable from tasks too easy to break.
**Artifact (delivered, SUPPORTED).** Deterministic environments, six transform families, a
property-tested equivalence suite (>15,000 cases, zero mismatch), and the STNF compiler scaffold.
**Scope.** Pilot-scale, two model families, easy tasks (baseline 1.00), single seed, no repeats,
synthetic environments; the load-bearing test — whether label-free LLM-STNF recovers enum performance
on held-out tools and transform families — is **pre-registered and budget-gated (UNRUN)**.

## 1. Introduction
Changing how a tool is *described* to an LLM agent — without changing what the tool *does* — may
change whether the agent succeeds. In our pilot, replacing human-legible enum values with opaque
short codes — a change that leaves the environment state transition byte-identical (Section 6.1) — was
associated with a small drop in task success, from **1.00 to 0.80 for Claude** (Δ −0.20, CI
[−0.50, 0.00]) and from **1.00 to 0.90 for Codex** (Δ −0.10, CI [−0.30, 0.00]). **Both intervals
include zero**, so this is a directional pilot signal, not a confirmed effect. Two other
state-transition-equivalent changes on the same tasks — structurally nesting parameters and lexically
aliasing names — showed **no drop** (Δ 0.00) for either model, though the 1.00 baseline ceiling leaves
us unable to distinguish genuine robustness from insufficient power (Section 6.2).

So the question "is this agent robust to interface variation?" has no single answer even when the
variation is provably behavior-preserving: it depends on *which* representational axis moves. Prior
work (PIPE [pipe2026]) established that behavior-preserving interface rewrites change agent success and
used the gap to *diagnose* interface reliance, but offers no remedy. The unoccupied core is the fix: a
normalization layer that does not need to be told which transform was applied. This paper *specifies*
that design as a **pre-registered plan (the remedy itself is UNRUN — see Section 6.4 and "Honest
status")**, delivers the formal scaffolding that licenses the phrase "representation only," and reports
an honest, **non-significant** pilot signal for the phenomenon the design is meant to repair.

**Contributions** (each maps to a section/result; honestly tiered by what is *delivered*):
1. **A formal equivalence and a verified benchmark (delivered, SUPPORTED)** (Sections 2–3). We define
   tool-interface equivalence by *audited byte-identical environment state transitions* and instantiate
   six strict transform families over three stateful environments. A property suite finds zero
   mismatches over >15,000 cases plus a metamorphic negative control (P1-C0, SUPPORTED) — which rules
   out a **scoring/harness artifact** (not every possible confound; see Section 6.1). This is the one
   fully delivered contribution.
2. **A non-significant pilot phenomenon signal** (Section 6, H1). Among three exercised equivalent
   transforms, only enum-encoding showed a drop (Claude Δ −0.20, CI [−0.50, 0.00]; Codex Δ −0.10, CI
   [−0.30, 0.00]); **both CIs include zero**, so the drop is not statistically distinguishable from no
   effect at n=10. Nesting and lexical aliasing showed no drop, but at a 1.00 ceiling we cannot
   distinguish robustness from low power. We report this as a directional pilot signal, with its
   negatives, not as a confirmed phenomenon.
3. **STNF, a label-free Semantic Tool Normal Form — design + pre-registered plan, UNRUN** (Section 4):
   an oracle canonicalizer (verified-correct codec, an upper bound, **not a contribution**), a static
   canonicalizer that recovers structural wrapping but **provably abstains on semantic renaming** (the
   enum case), and an LLM-assisted compiler that is the surviving novel core relative to PIPE's
   diagnose-only stance. The compiler — the only component that can touch the one family that moved —
   is **not yet run**; its held-out transfer test (H5) is the PRIMARY claim and remains pre-registered.
4. **An honest pilot accounting and a pre-registered held-out plan** (Sections 5, 8, and "Honest
   status"). We keep the deterministic SUPPORTED infrastructure separate from pilot-scale signals,
   report the negatives (1/3 transforms moved, **within noise**; ranking is **NOT supported** by two
   models), and pre-register the load-bearing STNF transfer test as the decisive, budget-gated
   experiment.

## 2. Problem: state-transition interface equivalence
We model a stateful tool environment as states `s ∈ S`, abstract semantic actions `a`, and a
transition `T(s,a) -> (s',o)`. A tool interface `I` decodes a model's output into an abstract
action and encodes observations back to the model. Two interfaces `I1, I2` are **strictly
state-transition-equivalent** on the valid state set when there is an invertible codec such that
for every valid `s` and action `a`, `T1(s, encode_I1(a)) == T2(s, encode_I2(a))`, and the decoded
observation preserves task-relevant information.

This is a strictly stronger equivalence than schema- or description-similarity: it is defined by
the *environment's* behaviour, not by surface form. It is what licenses the claim "we changed only
the representation" (subject to the information caveat T1, Section 6.4). We distinguish **strict**
equivalence (one logical action ↦ one call, matched resource cost; our main study) from **workflow**
equivalence (split/merge granularity; extension only, reported with interaction cost — never mixed
with strict results).

## 3. The ToolMorph benchmark and equivalence proof
We build six strict transform families that change only the model-visible interface while leaving
the executor — hence the state transition — identical: lexical aliasing, structural nesting, enum
encoding, optional/default exposure, response representation, and error representation
(`papers/p1_toolmorph/transforms/families.py`).

**Verified result (SUPPORTED, deterministic, P1-C0).** A property-based suite
(`property_tests/equivalence.py`) checks, for every family and every tool across three stateful
environments (calendar, inventory, helpdesk), that a canonical call and its transformed view
produce a *byte-identical post-call hidden state*, the same error category, and a response that
decodes back to the canonical response. Over **>15,000 randomized per-call cases plus all task
scenarios, zero mismatches** were found (independently re-run by the red-team at 27,300 cases, zero
mismatch). A metamorphic negative control — an oracle agent *given* the transform, which emits the
correctly mapped calls — shows exactly zero degradation under every family. This rules out a
**scoring/harness artifact**: a later model effect is not produced by the scorer. It does **not** rule
out other confounds — e.g. that the specific opaque codes chosen are intrinsically harder, or that the
effect is an information-availability rather than a pure-representation effect (Section 6.4, T1–T2).
The equivalence proof itself (P1-C0) is SUPPORTED.

## 4. Method: Semantic Tool Normal Form (STNF)
STNF re-presents a deployed (possibly transformed) tool to the agent in a canonical normal form,
with a runtime codec mapping the agent's canonical calls back to the deployed interface.
- **Oracle canonicalizer** (upper bound, `stnf.py:OracleCanonicalizer`): uses the known transform;
  proves the codec is correct (routing a canonical call preserves the state transition — verified).
  It is an upper bound, **not a contribution**.
- **Static canonicalizer** (label-free, schema-only): recovers structural wrapping (nesting) by
  inspection; **provably abstains** on semantic renaming (lexical/enum) rather than emitting a
  dangerous guess (`STATIC_COVERAGE`: `enum_encoding: False`, `lexical_aliasing: False`). Its coverage
  table is reported, not hidden.
- **LLM-assisted compiler** (the surviving novel core, **UNRUN**): would infer a canonical contract
  from the schema+description without the transform label. This is the **only** component that can
  repair the enum case, and it is **not yet run** — its held-out transfer is the pre-registered PRIMARY
  test (H5, Section 6.4). The Claude/Codex pilot below exercises the *phenomenon* (agents on
  transformed interfaces), **not** this compiler.

## 5. Experimental setup
Unified plan-then-execute harness: the model is shown the (possibly transformed) tool schemas and a
task, returns a JSON tool-call plan, which *we* execute against the deterministic environment and
score with an invariant final-state oracle. The same harness drives every model, so scoring is
attributable to the model rather than a product loop — but note the two CLIs wrap their own internal
scaffolding/system prompts, so model differences may include product-scaffolding differences (T3,
Section 6.4). Pilot: 10 base tasks × {Claude, Codex} × {original, structural_nesting, enum_encoding,
lexical_aliasing}; every episode logged to the immutable ledger; single seed, no repeats.
**Scope:** this is pilot-scale, subscription-CLI evidence toward H1; a frozen full study (≥6 transform
families, ≥3 model families, held-out splits, repeats) requires the configured-budget gate.

## 6. Results

### 6.1 Infrastructure check (SUPPORTED, deterministic, P1-C0)
The property suite over the three stateful environments found **zero state-transition mismatches in
>15,000 randomized per-call cases plus all task scenarios** (independently re-run by the red-team at
27,300 cases, zero mismatch), and the metamorphic negative control — an oracle agent handed the
transform — degrades by exactly zero under every family. This rules out a **scoring/harness
artifact**: the model results below are not manufactured by the scorer. It does **not**, by itself,
rule out content/information confounds in the chosen codes (Section 6.4, T1–T2). This deterministic
result is reported separately from the (pilot-scale, stochastic) model results that follow, and is the
paper's **one fully delivered, SUPPORTED contribution**.

### 6.2 Pilot: a small, non-significant enum-encoding signal (H1)
We ran 10 base tasks (calendar / inventory / helpdesk) × {Claude, Codex} × {original,
structural_nesting, enum_encoding, lexical_aliasing} through the interactive plan harness
(`p1_interactive_v1`), yielding **80 episodes, none excluded**. The single Claude/enum_encoding
failure that hit the step ceiling is a **max_steps timeout** in which the agent looped on the opaque
codes; per the updated `analysis_plan.yaml` `missing_data_policy` this is a **genuine agent failure and
is COUNTED** (the agent's inability to make progress on the opaque interface is exactly the phenomenon
under study), not excluded. The earlier single-shot harness (`plan_execute_v1`) is the **only**
excluded run, archived as a setup confound: it could not reference server-assigned entity ids,
flooring baseline success at 0.40 and masking the interface effect (`exclusions.csv`). With that
confound removed, the original interface scores **1.00 for both models**, giving a clean paired
baseline.

| interface | Claude success | Δ vs original (CI) | Codex success | Δ vs original (CI) |
|---|---|---|---|---|
| original | 1.00 | — | 1.00 | — |
| structural_nesting | 1.00 | 0.00 | 1.00 | 0.00 |
| lexical_aliasing | 1.00 | 0.00 | 1.00 | 0.00 |
| **enum_encoding** | **0.80** | **−0.20, CI [−0.50, 0.00]** | **0.90** | **−0.10, CI [−0.30, 0.00]** |

All cells are **n=10, single seed, no repeats**. Two of the three exercised transforms — structural
nesting (parameters re-wrapped) and lexical aliasing (names renamed) — show **no drop** (Δ 0.00) for
either model; but because baseline is at the **1.00 ceiling**, this absence-of-effect cannot be
distinguished from insufficient power (the tasks may simply be too easy to break). Only
**enum_encoding** (string enum values replaced by opaque short codes) moved: Claude **1.00 → 0.80
(Δ −0.20, CI [−0.50, 0.00])** and Codex **1.00 → 0.90 (Δ −0.10, CI [−0.30, 0.00])**. **Both bootstrap
CIs include zero**, so this drop is **NOT statistically distinguishable from zero at this sample
size**: it is a directional pilot signal that is consistent across two model families, **not a
confirmed effect**. After counting the timeout, the signal rests on **1–2 failing task-episodes per
model**.

**Honest reading.** This is **pilot signal toward H1, not a confirmatory result**: with CIs spanning
zero we **cannot reject "no effect."** A plausible *hypothesis* for follow-up is a semantic-decoding
rather than a structural-parsing difficulty — the transforms an agent could in principle recover by
inspection (re-nesting, renaming) showed no drop, whereas the transform that strips human-legible enum
tokens is the one that moved — but we do **NOT** claim the recoverable transforms are "absorbed
losslessly" (zero drop at a 1.00 ceiling is indistinguishable from tasks too easy to break), and we do
**NOT** claim a mechanism. Threats T1–T2 (Section 6.4) — information-availability vs representation,
and an enum-code-scheme confound — remain open.

### 6.3 Ranking (H4): NOT supported
Under the original, structural_nesting, and lexical_aliasing interfaces the two models are tied at
1.00. Under enum_encoding the point estimates differ by **≤0.10** (Codex 0.90, Claude 0.80) — a gap
that is **within the bootstrap noise** (both CIs include zero) and rests on 1–2 task-episodes. We make
**no ranking claim and no "representation can reorder models" framing**: a Kendall-tau
ranking-reversal result requires **≥6 model families** with bootstrap, per the research contract. With
two ceiling-tied models this is **not supported**. P1-H4 is UNTESTED and is **not** advanced by this
pilot.

### 6.4 Threats and what the pilot does NOT yet establish (T1–T3, H3, H5)
- **T1 (representation vs information).** "Byte-identical state transitions" (P1-C0) does **NOT** imply
  equal *decodable information* in the prompt. The one family that moved removes legible enum tokens,
  i.e. it plausibly changes the information available to the model, not only its representation. So the
  central "we changed only the representation" framing is **not established for the only transform that
  moved**; the effect may be an information-availability effect (the Schema-First thesis, Section 7).
  H3 tests this and is untested.
- **T2 (enum-code confound).** The signal may be specific to the particular opaque code scheme (length,
  collisions, tokenization) rather than "removing legible enum tokens" in general. No alternative enum
  variant was tested.
- **T3 (product vs base model).** Claude Code and Codex are commercial agent products with their own
  scaffolding/system prompts; observed model differences may be product-scaffolding differences, and
  subscription-CLI single-seed runs are **not externally reproducible** without pinned versions.
- **H3 (content control)** is untested: whether the enum signal survives matching schema tokens /
  description length / information content is unknown; if it vanishes, the phenomenon claim weakens.
- **H5 (PRIMARY, the remedy) is UNRUN.** By design the static canonicalizer **provably cannot** repair
  enum_encoding — semantic renaming is exactly where it abstains (Section 4). The oracle codec is
  verified correct but is an upper bound, not a contribution. The load-bearing, budget-gated test that
  separates this work from prior diagnostics — *does the label-free LLM-STNF recover enum performance
  on held-out tools and transform families?* — is the **PRIMARY claim and remains a pre-registered
  plan, not a result.**

## 7. Related work
**Phenomenon (the credited setup).** PIPE [pipe2026] minimally rewrites agent interfaces while
preserving execution behaviour and measures a paired original-vs-rewritten gap across many models,
establishing interface reliance; it provides **no normalization remedy, no formal byte-level
state-transition equality, and no ranking-reversal characterization**, and its transform is narrower
(action-name aliasing). Metamorphic regression testing for agent workflows [agentassay2026] supplies
paired, semantics-preserving test framing but does not hold a tool's state transition identical to
vary *only* representation, nor offer a normal form. A content-constant line holds tool semantics and
information content fixed while varying interface specification and reports that the bottleneck is
semantic rather than representational (Schema First, arXiv:2603.13404 [unverified — pending Director
verification]); this motivates our content-matched control (H3) and is the basis of threat T1.

**Normalization (the contested delta).** TSCG [tscg2026] deterministically compiles tool schemas with
a fixed operator set for token efficiency; a learned tool-description rewriter that transfers to
unseen *tools* (arXiv:2602.20426 [unverified — pending Director verification]) optimizes performance
rather than producing a canonical form. Neither targets a label-free normal form transferring to
unseen *transform families* — STNF's intended (and still UNRUN) delta (Section 4).

**Two-model comparison.** We pair Claude and Codex; cross-model agentic comparison of these two
families has precedent in cross-model code review [cc02xiang2026]. Two families cannot support a
Kendall-tau ranking claim (contract H4 requires ≥6 models), so we make **no** ranking claim
(Section 6.3).

We credit these explicitly and claim only the surviving conjunction (Section 4; full novelty audit:
`papers/p1_toolmorph/novelty/novelty_attack.md`). Our own audit concedes the *phenomenon* (interface
variation changes success) is largely pre-empted by PIPE; the uncollided core is STNF transfer to
unseen transform families, which is unrun.

## 8. Limitations / Ethics
This is **pilot-scale, subscription-CLI** evidence on **two model families** (Claude Code; Codex /
gpt-5.5) over **10 base tasks** (**80 episodes, none excluded**; one Claude/enum max_steps timeout
counted as a genuine agent failure per `analysis_plan.yaml`) in **synthetic environments**; product
models are exact-snapshot-logged but provider-updatable, **single-seed, with no repeats** — so
run-to-run sampling variance is unmeasured and the numbers are not externally reproducible without
pinned versions (T3). Tasks are easy (baseline 1.00), so the enum signal is small with bootstrap CIs
that **include zero** (Claude Δ −0.20, CI [−0.50, 0.00]; Codex Δ −0.10, CI [−0.30, 0.00]) — a
directional pilot signal, **not a confirmed effect** — and only one of three exercised transforms
moved. The Δ 0.00 cells **cannot** be read as confirmed robustness because of the ceiling. **H3**
(content control) is untested and **H4** (≥6-model ranking) is **not supported** by two ceiling-tied
models — we make no ranking claim. The **PRIMARY** claim **H5** — label-free STNF recovery on held-out
transforms and tools — is **UNRUN, a pre-registered plan**: the static canonicalizer provably abstains
on semantic renaming (the enum case), the oracle codec is a verified upper bound (not a contribution),
and the LLM compiler's transfer is the pending, budget-gated decisive test (`research_contract.yaml`
kill-gates). The deterministic infrastructure (equivalence proof P1-C0; programmatic state oracle) is
reported separately as SUPPORTED and does not depend on any model. No private data; no external
services beyond the two CLIs; compute-only risk.

## Honest status and path to a full paper
**Current tier: pilot + pre-registration (workshop / benchmark-note), NOT a finished flagship-venue
submission.** The adversarial red-team scored the draft 3/10 (REJECT-as-full-paper, re-submittable
with a clear path) for two structural reasons: the PRIMARY contribution is unrun, and the headline
phenomenon is a small, non-significant signal. We state the status plainly.

**(a) Delivered and SUPPORTED now (model-independent).**
- A formal byte-identical state-transition equivalence definition and a **property-verified
  benchmark**: six behavior-preserving transform families over three stateful environments, **zero
  mismatches** over >15,000 (independently reproduced at 27,300) randomized per-call cases plus all
  task scenarios, with a metamorphic negative control that rules out a **scoring/harness artifact**
  (P1-C0). This is the paper's one fully delivered contribution.
- A deterministic plan-then-execute harness with an invariant final-state oracle.

**(b) Pre-registered / UNRUN (plans, not results).**
- **H5 (PRIMARY): the STNF remedy.** The label-free LLM-STNF compiler — the only component that can
  touch the one family that moved — is specified but **not run**. The oracle canonicalizer is a
  verified upper bound (not a contribution); the static canonicalizer provably abstains on the enum
  case. The surviving novel core is therefore a **plan, not a finding**.
- **H3 (content control)** and **H4 (≥6-model ranking)** are untested / not supported.
- The enum phenomenon is a **small, non-significant pilot signal** (both CIs include zero), largely
  pre-empted as a *phenomenon* by PIPE per our own novelty audit; the uncollided claim is STNF
  transfer, which is unrun.

**(c) Concrete experiments required to become a full paper** (from `redteam_review.md`).
1. **Run H5** — label-free LLM-STNF on **held-out transform families and held-out tools**, vs the
   strongest non-oracle baseline (token/content-matched rewrite; TSCG-style compiler); report
   Δ-recovered with task-clustered CIs against the pre-registered margin (≥5 pts or ≥20%
   sensitivity-AUC). Without this there is no tested novel result.
2. **Escape the ceiling** — harder tasks so baseline < 1.00; scale from 10 toward the planned 24–120
   tasks, giving power to detect degradation and headroom to demonstrate recovery.
3. **Repeats + multiple seeds** (≥3–5 per cell) to separate LLM sampling noise from a stable
   representational effect; report within-task variance.
4. **H3 information/content control** — a token/length/information-matched enum variant and a
   matched-legibility code scheme, to rebut the Schema-First "semantic, not representational" thesis
   (T1); if the effect vanishes, report it (the contract's own kill condition).
5. **Head-to-head vs PIPE** on overlapping environments (novelty-audit Experiment 1): show the
   non-PIPE families produce comparable/larger Δ and that STNF beats "do nothing" on PIPE-style
   aliases.
6. **Ranking (H4)** — run **≥6 model families with Kendall-τ + bootstrap, or drop ranking framing
   entirely** (currently not supported).
7. **Reproducibility** — pin model versions (API or version-hash + seeds) and disentangle base model
   from product scaffolding (T3).
8. **Numbers reconciled (done in this revision):** one timeout policy (the timeout is **counted** per
   the updated `analysis_plan.yaml`), no spurious exclusion (80 episodes), Codex corrected to
   0.90/−0.10, bootstrap CIs printed (both include zero), and "degrades" replaced with
   significance-honest language throughout.
