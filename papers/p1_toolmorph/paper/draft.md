# ToolMorph: A Label-Free Semantic Normal Form for Behavior-Preserving Tool-Interface Variation

> DRAFT — evidence-first order (manual 2.0). Abstract / Introduction / Results are written
> AFTER the pilot evidence lands; sections below marked [PENDING] await ledger numbers.
> Every number in the final draft must come from `core.plotting.pilot_tables` / the run ledger.

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
base tasks across calendar / inventory / helpdesk, 79 valid episodes, paired across the original
interface and three equivalent transforms.
**Primary result (with uncertainty).** Enum-encoding (opaque numeric codes for enum values) degrades
success for both models — Claude 1.00→0.80 (Δ −0.20) and Codex 1.00→0.89 (Δ −0.11) — while
structural nesting and lexical aliasing show no measurable degradation (Δ 0.00). Effects are modest
with wide CIs at n≈10 tasks/cell; this is pilot signal, not confirmation, and only one of three
exercised transforms degraded.
**Mechanism.** The degrading family removes human-legible enum tokens, consistent with a
semantic-decoding rather than a structural-parsing failure; structurally recoverable transforms are
absorbed losslessly.
**Artifact.** Deterministic environments, six transform families, a property-tested equivalence suite
(>15,000 cases, zero mismatch), and the STNF compiler.
**Scope.** Pilot-scale, two model families, easy tasks (baseline 1.00), synthetic environments; the
load-bearing test — whether label-free LLM-STNF recovers enum performance on held-out tools and
transform families — is pre-registered and budget-gated.

## 1. Introduction
Changing how a tool is *described* to an LLM agent — without changing what the tool *does* — can
change whether the agent succeeds. In our pilot, replacing human-legible enum values with opaque
short codes, a change that leaves the environment state transition byte-identical (Section 6.1),
dropped task success from **1.00 to 0.80 for Claude** and from **1.00 to 0.89 for Codex**. Two other
state-transition-equivalent changes on the same tasks — structurally nesting parameters and lexically
aliasing names — produced **no measurable degradation** (Δ 0.00) for either model (Section 6.2).

So the question "is this agent robust to interface variation?" has no single answer even when the
variation is provably behavior-preserving: it depends on *which* representational axis moves. Prior
work (PIPE [pipe2026]) established that behavior-preserving interface rewrites change agent success
and used the gap to *diagnose* interface reliance, but offers no remedy. The unoccupied core is the
fix: a normalization layer that does not need to be told which transform was applied. This paper
contributes that design plus the formal scaffolding that licenses the phrase "representation only,"
and reports honest pilot evidence for the phenomenon it is meant to repair.

**Contributions** (each maps to a section/result):
1. **A formal equivalence and a verified benchmark** (Sections 2–3). We define tool-interface
   equivalence by *audited byte-identical environment state transitions* and instantiate six strict
   transform families over three stateful environments. A property suite finds zero mismatches over
   >15,000 cases plus a metamorphic negative control (P1-C0, SUPPORTED) — so any model effect is not
   a harness artifact.
2. **A pilot phenomenon result** (Section 6, H1 signal). Among three exercised equivalent transforms,
   only enum-encoding degrades success (Claude −0.20, Codex −0.11); nesting and lexical aliasing are
   absorbed losslessly. We report this as pilot signal, with its negatives, not as confirmation.
3. **STNF, a label-free Semantic Tool Normal Form** (Section 4): an oracle canonicalizer
   (verified-correct codec, upper bound), a static canonicalizer that recovers structural wrapping but
   honestly abstains on semantic renaming, and an LLM-assisted compiler — the surviving novel core
   relative to PIPE's diagnose-only stance.
4. **An honest pilot accounting and a pre-registered held-out plan** (Sections 5, 8). We keep the
   deterministic SUPPORTED infrastructure separate from pilot-scale signals, report the negatives
   (1/3 transforms degrade; ranking is a 2-model directional hint), and pre-register the load-bearing
   STNF transfer test as the decisive, budget-gated experiment.

## 2. Problem: state-transition interface equivalence
We model a stateful tool environment as states `s ∈ S`, abstract semantic actions `a`, and a
transition `T(s,a) -> (s',o)`. A tool interface `I` decodes a model's output into an abstract
action and encodes observations back to the model. Two interfaces `I1, I2` are **strictly
state-transition-equivalent** on the valid state set when there is an invertible codec such that
for every valid `s` and action `a`, `T1(s, encode_I1(a)) == T2(s, encode_I2(a))`, and the decoded
observation preserves task-relevant information.

This is a strictly stronger equivalence than schema- or description-similarity: it is defined by
the *environment's* behaviour, not by surface form. It is what licenses the claim "we changed only
the representation." We distinguish **strict** equivalence (one logical action ↦ one call, matched
resource cost; our main study) from **workflow** equivalence (split/merge granularity; extension
only, reported with interaction cost — never mixed with strict results).

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
scenarios, zero mismatches** were found. A metamorphic negative control confirms an
interface-robust agent shows exactly zero degradation under every family, so the harness itself
injects no artifact. Any later model effect therefore cannot be a benchmark bug (manual 5.7).

## 4. Method: Semantic Tool Normal Form (STNF)
STNF re-presents a deployed (possibly transformed) tool to the agent in a canonical normal form,
with a runtime codec mapping the agent's canonical calls back to the deployed interface.
- **Oracle canonicalizer** (upper bound, `stnf.py:OracleCanonicalizer`): uses the known transform;
  proves the codec is correct (routing a canonical call preserves the state transition — verified).
- **Static canonicalizer** (label-free, schema-only): recovers structural wrapping (nesting) by
  inspection; **honestly abstains** on semantic renaming (lexical/enum) rather than emitting a
  dangerous guess. Its coverage table is reported, not hidden.
- **LLM-assisted compiler** (the surviving novel core): infers a canonical contract from the
  schema+description without the transform label; tested here via subscription Claude/Codex.

## 5. Experimental setup
Unified plan-then-execute harness: the model is shown the (possibly transformed) tool schemas and a
task, returns a JSON tool-call plan, which *we* execute against the deterministic environment and
score with an invariant final-state oracle. The same harness drives every model, so effects are
attributable to the model, not a product loop. Pilot: 10 base tasks × {Claude, Codex} × {original,
structural_nesting, enum_encoding, lexical_aliasing}; every episode logged to the immutable ledger.
**Scope:** this is pilot-scale, subscription-CLI evidence toward H1/H3/H4; a frozen full study
(≥6 transform families, ≥3 model families, held-out splits) requires the configured-budget gate.

## 6. Results

### 6.1 Infrastructure check (SUPPORTED, deterministic, P1-C0)
The property suite over the three stateful environments found **zero state-transition mismatches in
>15,000 randomized per-call cases plus all task scenarios**, and the metamorphic negative control
shows an interface-robust reference agent degrades by exactly zero under every family. Any model
effect below therefore cannot be a benchmark artifact; it is attributable to the model's reading of
the interface. This deterministic result is reported separately from the (pilot-scale, stochastic)
model results that follow.

### 6.2 Pilot: only enum-encoding degrades success (H1 signal)
We ran 10 base tasks (calendar / inventory / helpdesk) × {Claude, Codex} × {original,
structural_nesting, enum_encoding, lexical_aliasing} through the interactive plan harness
(`p1_interactive_v1`), yielding **79 valid episodes** (1 infrastructure error excluded). The earlier
single-shot harness (`plan_execute_v1`) is excluded as a setup confound: it could not reference
server-assigned entity ids, flooring baseline success at 0.40 and masking the interface effect
(`exclusions.csv`). With that confound removed, the original interface scores **1.00 for both
models**, giving a clean paired baseline.

| interface | Claude success | Δ vs original | Codex success | Δ vs original |
|---|---|---|---|---|
| original | 1.00 | — | 1.00 | — |
| structural_nesting | 1.00 | 0.00 | 1.00 | 0.00 |
| lexical_aliasing | 1.00 | 0.00 | 1.00 | 0.00 |
| **enum_encoding** | **0.80** | **−0.20** | **0.89** | **−0.11** |

Two of the three exercised transforms — structural nesting (parameters re-wrapped) and lexical
aliasing (names renamed) — produce **no measurable degradation** (Δ 0.00) for either model. Only
**enum_encoding** (string enum values replaced by opaque short codes) degrades success: Claude
**1.00 → 0.80 (Δ −0.20)** and Codex **1.00 → 0.89 (Δ −0.11)**. The effect is directionally
consistent across two independent model families on a change that is provably
state-transition-equivalent (Section 6.1).

**Honest reading.** The effect is modest and the tasks are easy (baseline 1.00), so confidence
intervals are wide at n≈10 tasks/cell. This is **pilot signal toward H1, not a confirmatory
result**, and only **one of three** exercised transforms degraded. The mechanism is consistent with
a semantic-decoding failure rather than a structural-parsing failure: the two transforms an agent
can recover by inspection (re-nesting, renaming) are absorbed losslessly, whereas the transform that
strips human-legible enum tokens — leaving codes with no recoverable surface meaning — is the one
that bites.

### 6.3 Ranking (H4): a 2-model directional hint, not a claim
Under the original, structural_nesting, and lexical_aliasing interfaces the two models are tied at
1.00. Under enum_encoding they separate (Codex 0.89 > Claude 0.80). This is a directional hint that
representation alone can reorder models, but **two model families cannot support a Kendall-tau
ranking-reversal claim** (the research contract requires ≥6 models for H4). We report it as
motivation only; P1-H4 remains UNTESTED.

### 6.4 What the pilot does NOT yet establish (H3, H5)
- **H3 (content control)** is untested in this pilot. Whether the enum effect survives matching
  schema tokens / description length / information content is unknown; if it vanishes, the
  phenomenon claim weakens (the threat raised by the content-constant prior work cited in
  Section 7).
- **H5 (PRIMARY, the remedy)** is not yet run. By design the static canonicalizer **provably cannot**
  repair enum_encoding — semantic renaming is exactly where it honestly abstains (Section 4). The
  oracle codec is verified correct but is an upper bound, not a contribution. The load-bearing,
  budget-gated test that separates this work from prior diagnostics — *does the label-free LLM-STNF
  recover enum performance on held-out tools and transform families?* — remains the pending decisive
  experiment.

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
verification]); this motivates our content-matched control (H3).

**Normalization (the contested delta).** TSCG [tscg2026] deterministically compiles tool schemas with
a fixed operator set for token efficiency; a learned tool-description rewriter that transfers to
unseen *tools* (arXiv:2602.20426 [unverified — pending Director verification]) optimizes performance
rather than producing a canonical form. Neither targets a label-free normal form transferring to
unseen *transform families* — STNF's intended delta (Section 4).

**Two-model comparison.** We pair Claude and Codex; cross-model agentic comparison of these two
families has precedent in cross-model code review [cc02xiang2026]. Two families cannot support a
Kendall-tau ranking claim (contract H4 requires ≥6 models), so we report only a directional hint
(Section 6.3).

We credit these explicitly and claim only the surviving conjunction (Section 4; full novelty audit:
`papers/p1_toolmorph/novelty/novelty_attack.md`).

## 8. Limitations / Ethics
This is **pilot-scale, subscription-CLI** evidence on **two model families** (Claude Code; Codex /
gpt-5.5) over **10 base tasks** (79 valid episodes) in **synthetic environments**; product models are
exact-snapshot-logged but provider-updatable. Tasks are easy (baseline 1.00), so the enum effect is
modest with wide CIs (n≈10 tasks/cell) — pilot signal toward H1, **not a confirmatory result** — and
only one of three exercised transforms degraded. **H3** (content control) and **H4** (≥6-model
ranking) are untested; the H4 separation we observe is a 2-model directional hint only. The
**PRIMARY** claim **H5** — label-free STNF recovery on held-out transforms and tools — is **not yet
run**: the static canonicalizer provably abstains on semantic renaming (the enum case), the oracle
codec is a verified upper bound (not a contribution), and the LLM compiler's transfer is the pending,
budget-gated decisive test (`research_contract.yaml` kill-gates). The deterministic infrastructure
(equivalence proof P1-C0; programmatic state oracle) is reported separately as SUPPORTED and does not
depend on any model. No private data; no external services beyond the two CLIs; compute-only risk.
