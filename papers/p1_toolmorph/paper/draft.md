# ToolMorph: A State-Transition-Equivalence Benchmark and a Negative Result on Representation-Induced Fragility in Tool-Using Agents

> DRAFT — current tier: **ARXIV_ONLY (benchmark + negative result)**, NOT a method paper. What is
> *delivered* is (i) a property-verified, byte-identical state-transition-equivalence benchmark
> (SUPPORTED, deterministic, model-independent) and (ii) a clean **negative result**: on these tasks,
> frontier tool-using agents show no degradation from representation-equivalent, information-preserving
> interface transforms, and the one apparent exception is hidden information, not representation. A
> pre-registered remedy — STNF, a label-free Semantic Tool Normal Form — is **RETIRED**: the paper's own
> information-matched control falsifies its premise (no representation-only degradation to recover).
> Every Results number is quoted verbatim from the immutable run ledgers (`artifacts/run_ledger.jsonl`,
> `artifacts/p1_control_ledger.jsonl`, paper_id=p1_toolmorph) and the Director-verified property suite;
> nothing is invented, re-rounded, or extrapolated.

## Abstract
**Context.** Tool-using LLM agents are deployed against tool interfaces whose surface form varies even
when the underlying executor — and hence the environment state transition — is identical.
**Gap.** Prior work (PIPE) shows behavior-preserving interface rewrites change agent success and
diagnoses interface reliance, but does not separate two confounded causes: a change in *representation*
(which a label-free normalizer could in principle undo) from a change in the *information* available to
the model (which it cannot). There is no formal byte-level state-transition-equivalence guarantee and
no controlled representation-vs-information adjudication.
**Approach.** We (1) define tool-interface equivalence by audited byte-identical state transitions, (2)
build and property-verify six strict transform families over three stateful environments, and (3) run an
information-matched control that holds the *representation* fixed (opaque enum codes) while restoring the
*information* (a legend), isolating which cause is operative.
**Result (negative).** Across the representation-equivalent families, two frontier agents (Claude,
Codex) show no degradation. The only apparent effect is enum-opaque (Claude **−0.20, CI [−0.50, 0.00]**,
non-significant; Codex **0.00**); restoring a legend over the *same* opaque codes eliminates it entirely
(enum-legend: Claude **0.00**, Codex **0.00**). The effect is therefore **information-hiding, not
representation** — consistent with the Schema-First thesis that semantics, not representation, is the
bottleneck.
**Retired hypothesis.** We pre-registered STNF, a label-free normalizer intended to recover
representation-induced degradation. The control triggers its pre-registered kill-gate: a legend
(content) erases the effect, and a label-free normalizer cannot recover information hidden in opaque
codes. STNF is reported honestly as a falsified hypothesis, **not** a contribution or a working method.
**Artifact (delivered, SUPPORTED).** Deterministic environments, six transform families, and a
property-tested equivalence suite (**>15,000 cases, zero mismatch**) with a metamorphic negative
control.
**Scope.** Easy tasks (baseline at the **1.00** ceiling), two model families, synthetic environments,
the enum effect itself non-significant; the negative result is bounded to this regime and stated as
such.

## 1. Introduction
Changing how a tool is *described* to an LLM agent — without changing what the tool *does* — can change
whether the agent succeeds. The natural diagnosis is that the agent is fragile to *representation*: the
surface encoding of an interface that leaves its behaviour fixed. But "representation" and
"information" are routinely confounded. When an interface rewrite removes human-legible enum tokens
(e.g. `priority="low"` becomes the code `c0`), it changes the surface form, but it may also remove
*information the model needs to act*. These are different failure modes with opposite remedies: a
representational change can be normalized away by a layer that re-presents the interface in canonical
form; an information change cannot, because the information is simply gone from the prompt.

This paper asks that question directly and answers it with a controlled experiment. We define
tool-interface equivalence by *audited byte-identical state transitions* (Section 2), build and verify
six strict transform families (Section 3), and run an **information-matched control** (Section 6.3)
comparing the original interface, an enum-**opaque** interface (string enums replaced by opaque codes
`c0, c1, …`), and an enum-**legend** interface (the *same* opaque codes, with a legend in the tool
description restoring `c0 = low`, etc. — identical representation, information restored).

The answer is clean and negative. Across the representation-equivalent families the two frontier agents
(Claude, Codex) show no degradation; the only family that appears to move is enum-opaque (Claude
**−0.20, CI [−0.50, 0.00]**, non-significant; Codex **0.00**), and restoring the legend over the *same*
codes eliminates it entirely (enum-legend: Claude **0.00**, Codex **0.00**). So the apparent fragility
is **information-hiding, not representation**: on these tasks, frontier tool-using agents are robust to
behaviour-preserving interface *representation*, and the bottleneck — when there is one — is *semantics*
(the Schema-First thesis, Section 7). PIPE [pipe2026] established the phenomenon (rewrites move success)
and used it to diagnose interface reliance, but left this adjudication open; the controlled answer is
the contribution here.

This result also retires a method we pre-registered: STNF, a label-free Semantic Tool Normal Form
intended to *recover* representation-induced degradation. The control falsifies its premise — there is
no representation-only degradation to recover, and a label-free normalizer provably cannot recover
information hidden in opaque codes — so per the pre-registered kill-gate, STNF is retired (Section 4).
We report it honestly as a falsified hypothesis, not a working contribution.

**Contributions** (honestly tiered by what is *delivered*):
1. **A formal equivalence and a property-verified benchmark (delivered, SUPPORTED)** (Sections 2–3). We
   define tool-interface equivalence by audited byte-identical state transitions and instantiate six
   strict transform families over three stateful environments. A property suite finds **zero mismatches
   over >15,000 randomized cases** plus a metamorphic negative control (P1-C0, SUPPORTED). This is the
   paper's one fully delivered artifact.
2. **A clean negative result** (Section 6). On these tasks, two frontier agents show **no degradation**
   from representation-equivalent, information-preserving interface transforms; the sole apparent effect
   is small and non-significant.
3. **An information-vs-representation adjudication** (Section 6.3, the control). Holding the opaque-code
   *representation* fixed while restoring the *information* (a legend) eliminates the only effect
   (Claude enum-opaque **0.80 → 1.00**), attributing it to hidden information rather than
   representation.
4. **A retired-hypothesis accounting (honest)** (Section 4 and "Honest status"). The pre-registered STNF
   remedy is described as a hypothesis the control *falsified*, with the mechanism explained
   (information vs representation) and the pre-registered kill-gate documented. We do **not** present
   STNF as a method.

## 2. Problem: state-transition interface equivalence
We model a stateful tool environment as states `s ∈ S`, abstract semantic actions `a`, and a transition
`T(s, a) -> (s', o)`. A tool interface `I` decodes a model's output into an abstract action and encodes
observations back to the model. Two interfaces `I1, I2` are **strictly state-transition-equivalent** on
the valid state set when there is an invertible codec such that for every valid `s` and action `a`,
`T1(s, encode_I1(a)) == T2(s, encode_I2(a))`, and the decoded observation preserves task-relevant
information.

This is a strictly stronger equivalence than schema- or description-similarity: it is defined by the
*environment's* behaviour, not by surface form. It licenses the claim "we changed only the
representation" at the level of the executor — but, crucially, **byte-identical state transitions do not
imply equal decodable information in the prompt** (the central caveat this paper turns into a measured
result, Section 6.3). We distinguish **strict** equivalence (one logical action ↦ one call, matched
resource cost; our study) from **workflow** equivalence (split/merge granularity; out of scope here).

## 3. The ToolMorph benchmark and equivalence proof
We build six strict transform families that change only the model-visible interface while leaving the
executor — hence the state transition — identical: lexical aliasing, structural nesting, enum encoding,
optional/default exposure, response representation, and error representation
(`papers/p1_toolmorph/transforms/families.py`).

**Verified result (SUPPORTED, deterministic, P1-C0).** A property-based suite
(`property_tests/equivalence.py`) checks, for every family and every tool across three stateful
environments (calendar, inventory, helpdesk), that a canonical call and its transformed view produce a
*byte-identical post-call hidden state*, the same error category, and a response that decodes back to
the canonical response. Over **>15,000 randomized per-call cases plus all task scenarios, zero
mismatches** were found (independently re-run by the red-team at **27,300 cases, zero mismatch**). A
metamorphic negative control — an oracle agent *given* the transform, which emits the correctly mapped
calls — shows exactly zero degradation under every family. This rules out a **scoring/harness artifact**:
any later model effect is not manufactured by the scorer. The equivalence proof itself (P1-C0) is
SUPPORTED and model-independent; it is the paper's one fully delivered contribution. It does **not**, by
itself, establish that the transforms preserve decodable *information* — that is exactly what the
control in Section 6.3 tests.

## 4. A pre-registered remedy hypothesis (STNF) and why it does not apply here
Before the control, we pre-registered a remedy and a kill-gate. We record it honestly because the
paper's value includes the *adjudication* that retired it — not because STNF is a working method.
**It is not.**

**The hypothesis (H5, now REFUTED).** If agents degrade under behaviour-preserving interface transforms
*because of representation*, then a runtime layer that re-presents the deployed interface in a canonical
normal form — without being told which transform was applied — should recover the lost performance. STNF
(`stnf.py`) specifies an **oracle canonicalizer** (verified-correct codec using the known transform; an
upper bound, explicitly **not** a contribution), a **static canonicalizer** (schema-only, label-free)
that recovers structural wrapping but **provably abstains** on semantic renaming (`STATIC_COVERAGE`:
`enum_encoding: False`), and an **LLM-assisted compiler** that was the surviving novel core relative to
PIPE's diagnose-only stance.

**Why the control retires it.** The premise is that representation-induced degradation exists to
recover. The control (Section 6.3) shows the opposite here: the only apparent degradation (enum-opaque)
is **eliminated by restoring a legend over the same codes**, so the effect is *information-hiding*, not
representation. This meets the pre-registered kill-gate in two ways: (i) content-matching (the legend)
erases the effect, and (ii) a label-free normalizer cannot recover information that has been hidden —
opaque codes carry no recoverable meaning without a legend or executable probes, which is precisely why
the static canonicalizer *provably abstains* on the enum case, and the LLM compiler could at best
re-attach a legend it cannot derive from an opaque-by-construction schema. There is therefore **no
representation-only degradation for STNF to fix**. Per the pre-registered gate
(`research_contract.yaml`), STNF is **RETIRED**: not run as a contribution, not claimed to work.

## 5. Experimental setup
A unified plan-then-execute interactive harness (`p1_interactive_v1`): the model is shown the (possibly
transformed) tool schemas and a task, sees each tool result before the next call, and *we* execute the
calls against the deterministic environment and score with an invariant final-state oracle. The same
harness drives every model, so scoring is attributable to the model rather than a product loop — but the
two CLIs (Claude Code; Codex / gpt-5.5) wrap their own scaffolding/system prompts, so model differences
may include product-scaffolding differences (T2 below), and subscription-CLI runs are not externally
reproducible without pinned versions.

Two studies feed the results:
- **Pilot** (`artifacts/run_ledger.jsonl`): 10 base tasks (calendar / inventory / helpdesk) × {Claude,
  Codex} × {original, structural_nesting, enum_encoding, lexical_aliasing}; **80 episodes, none
  excluded**; single seed, no repeats.
- **Information-matched control** (`artifacts/p1_control_ledger.jsonl`): 10 tasks × {Claude, Codex} ×
  {original, enum-opaque, enum-legend}, **2 reps (n=20 per cell)**, task-clustered bootstrap CIs. This
  is the decisive go/no-go for representation vs information.

## 6. Results

### 6.1 Infrastructure check (SUPPORTED, deterministic, P1-C0)
The property suite over the three stateful environments found **zero state-transition mismatches in
>15,000 randomized per-call cases plus all task scenarios** (independently re-run by the red-team at
**27,300 cases, zero mismatch**), and the metamorphic negative control — an oracle agent handed the
transform — degrades by exactly zero under every family. This rules out a **scoring/harness artifact**:
the model results below are not manufactured by the scorer. This deterministic result is reported
separately from the (stochastic) model results and is the paper's one fully delivered, SUPPORTED
contribution.

### 6.2 Pilot: only enum-encoding shows any apparent effect (small, non-significant)
We ran the pilot through the interactive harness, yielding **80 episodes, none excluded**. The single
Claude/enum_encoding failure that hit the step ceiling is a **max_steps timeout** in which the agent
looped on the opaque codes; per `analysis_plan.yaml` `missing_data_policy` this is a **genuine agent
failure and is COUNTED**, not excluded. With the original interface, both models score **1.00**, giving
a clean paired baseline.

| interface | Claude success | Δ vs original (CI) | Codex success | Δ vs original (CI) |
|---|---|---|---|---|
| original | 1.00 | — | 1.00 | — |
| structural_nesting | 1.00 | 0.00 | 1.00 | 0.00 |
| lexical_aliasing | 1.00 | 0.00 | 1.00 | 0.00 |
| **enum_encoding** | **0.80** | **−0.20, CI [−0.50, 0.00]** | **0.90** | **−0.10, CI [−0.30, 0.00]** |

All cells are **n=10, single seed, no repeats**. Two of the three exercised transforms — structural
nesting and lexical aliasing — show **no drop** (Δ 0.00) for either model. Only **enum_encoding** moved:
Claude **1.00 → 0.80 (Δ −0.20, CI [−0.50, 0.00])** and Codex **1.00 → 0.90 (Δ −0.10, CI [−0.30, 0.00])**.
**Both bootstrap CIs include zero**, so this drop is **not statistically distinguishable from zero at
this sample size**: a directional pilot signal across two model families, **not a confirmed effect**,
resting on 1–2 failing task-episodes per model at a 1.00 ceiling. The Δ 0.00 cells likewise **cannot**
be read as confirmed robustness at the ceiling — they are consistent with tasks too easy to break. The
pilot motivated, but does not by itself settle, the decisive question: is even this small enum effect
about *representation* or *information*?

### 6.3 The decisive control: information, not representation (negative result)
We hold the opaque-code *representation* fixed and vary only the *information*: original, enum-opaque
(string enums → opaque codes `c0, c1, …`), and enum-legend (the **same** opaque codes plus a legend in
the tool description restoring `c0 = low`, etc.). Real Claude + Codex, interactive harness, **2 reps, 10
tasks, n=20 per cell**, task-clustered CIs (`artifacts/p1_control_ledger.jsonl`).

| condition | Claude | Δ (CI) | Codex | Δ (CI) |
|---|---|---|---|---|
| original | 1.00 | — | 1.00 | — |
| enum-opaque | 0.80 | −0.20 [−0.50, 0.00] | 1.00 | 0.00 |
| **enum-legend (info restored, same codes)** | **1.00** | **0.00** | **1.00** | **0.00** |

**Reading (decisive).** Restoring the information (a legend) while keeping the coded representation
**eliminates the degradation entirely** (Claude enum-opaque **0.80 → enum-legend 1.00**; Codex shows no
drop in either condition). The effect is therefore **information-hiding, not representation.** Combined
with the pilot — where the other exercised representation-equivalent transforms (structural nesting,
lexical aliasing) caused **no drop** — the honest conclusion is: **on these tasks, frontier tool-using
agents (Claude, Codex) are robust to behaviour-preserving interface representation changes; the only
apparent fragility comes from hidden information**, consistent with Schema First (semantics, not
representation, is the bottleneck; Section 7). This is a useful, clean adjudication: a controlled
experiment that separates two routinely confounded causes and finds the representational one inert in
this regime.

### 6.4 No ranking claim
Under original, structural_nesting, and lexical_aliasing the two models are tied at 1.00; under enum the
point estimates differ by ≤0.10 within bootstrap noise (CIs include zero). A Kendall-τ ranking-reversal
result requires **≥6 model families** with bootstrap (per the research contract). With two ceiling-tied
models, **no ranking claim is made** (P1-H4 REFUTED for this evidence).

### 6.5 Threats
- **T1 (regime / ceiling).** Tasks are easy (baseline 1.00) and the enum effect is itself
  non-significant; the negative result is bounded to these models, tasks, and synthetic environments —
  it shows representation does not matter *here*, not that it can never matter.
- **T2 (product vs base model).** Claude Code and Codex are commercial products with their own
  scaffolding; observed differences may be product-scaffolding differences, and single-seed
  subscription-CLI runs are not externally reproducible without pinned versions.
- **T3 (code-scheme generality).** The control restores information for one opaque code scheme; we did
  not sweep alternative lengths / tokenizations. The conclusion (legend erases the effect) holds within
  the tested scheme.

## 7. Related work
**Phenomenon (the credited setup).** PIPE [pipe2026] minimally rewrites agent interfaces while
preserving execution behaviour and measures a paired original-vs-rewritten gap across many models,
establishing interface reliance; it provides **no formal byte-level state-transition equality and no
controlled representation-vs-information adjudication**, and its transform is narrower (action-name
aliasing). Our delivered delta over PIPE is (i) the property-verified byte-level equivalence benchmark
and (ii) the information-matched control that adjudicates *why* a rewrite moves success.

**The bottleneck our control corroborates.** A content-constant line holds tool semantics and
information content fixed while varying interface specification and reports that the bottleneck is
semantic rather than representational (Schema First, arXiv:2603.13404 [unverified — pending Director
verification]). Our control is an independent, byte-equivalence-anchored confirmation of that direction:
when information is restored over a fixed representation, the effect vanishes.

**Normalization (now moot for this evidence).** TSCG [tscg2026] deterministically compiles tool schemas
with a fixed operator set for token efficiency; a learned tool-description rewriter that transfers to
unseen *tools* (arXiv:2602.20426 [unverified — pending Director verification]) optimizes performance
rather than producing a canonical form. We had positioned STNF as a label-free normal form transferring
to unseen transform *families*; the control retires that goal here, because there is no
representation-only degradation to normalize.

## 8. Limitations / Ethics
This is **subscription-CLI** evidence on **two model families** (Claude Code; Codex / gpt-5.5) over **10
base tasks** in **synthetic environments**; pilot is single-seed (80 episodes, none excluded), control
is 2 reps (n=20/cell). Tasks are easy (baseline **1.00**), so the only apparent effect (enum-opaque:
Claude **−0.20, CI [−0.50, 0.00]**, non-significant; Codex **0.00**) is small and the Δ 0.00 cells
cannot be read as confirmed robustness at the ceiling. The negative result is **bounded to this
regime**: for these models and tasks, behaviour-preserving representation changes do not degrade agents
and the one apparent exception is information-hiding — it does **not** establish that representation can
never matter. Numbers are not externally reproducible without pinned versions (T2). The deterministic
benchmark (P1-C0) is model-independent and reported separately as SUPPORTED; the pre-registered STNF
remedy is **retired** (P1-H5 REFUTED). No private data; no external services beyond the two CLIs;
compute-only risk.

## Honest status and path to a full paper
**Current tier: ARXIV_ONLY — a property-verified benchmark plus a clean negative result, clearly
labeled. This is NOT a method paper.**

**Delivered and SUPPORTED (model-independent):** the formal byte-identical state-transition-equivalence
definition and **property-verified benchmark** — six transform families over three stateful
environments, **zero mismatches** over **>15,000** (independently reproduced at **27,300**) randomized
cases plus all task scenarios, with a metamorphic negative control (P1-C0) — and a deterministic
plan-then-execute harness with an invariant final-state oracle.

**Delivered as a negative / adjudication result (bounded to this regime):** two frontier agents show
**no degradation** from representation-equivalent, information-preserving transforms, and the
information-matched control attributes the only apparent effect to **hidden information, not
representation** (Claude enum-opaque 0.80 → enum-legend 1.00; Codex 0.00 throughout), corroborating the
Schema-First direction.

**Retired (falsified hypothesis, not a contribution):** **STNF (P1-H5)**. The premise — recoverable
representation-induced degradation — is falsified by the control; a legend (content) erases the effect,
and a label-free normalizer cannot recover information hidden in opaque codes. Killed per the
pre-registered gate.

**Path to a fuller paper — NOT "run STNF" (retired).** The open question this evidence cannot settle is
*whether representation EVER matters once information is preserved*. The path is: (1) **harder,
non-ceiling tasks** (baseline < 1.00, scaling from 10 toward 24–120) so degradation is detectable and
the Δ 0.00 cells become informative; (2) **an information-preserving representational stressor** — a
transform that provably preserves decodable information (a legend/probe is always available) yet still
changes representation — to test whether any representational fragility survives content-matching (none
was found here); (3) **repeats + multiple seeds** (≥3–5/cell) and **≥6 model families** for power and to
license any ranking framing; (4) **reproducibility** via pinned versions/seeds, disentangling base model
from product scaffolding (T2). If, under those conditions, an information-matched representational
transform still degraded agents, *then* a normalization remedy would have something to recover. On the
current evidence it does not, and we say so.
