# ToolMorph: A Label-Free Semantic Normal Form for Behavior-Preserving Tool-Interface Variation

> DRAFT — evidence-first order (manual 2.0). Abstract / Introduction / Results are written
> AFTER the pilot evidence lands; sections below marked [PENDING] await ledger numbers.
> Every number in the final draft must come from `core.plotting.pilot_tables` / the run ledger.

## Abstract
[PENDING — write last, from results]

## 1. Introduction
[PENDING — write after results; lead with a concrete failure figure, not a grand claim]

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
[PENDING — from `core.plotting.pilot_tables.p1_table`: paired degradation per (model × transform),
ranking comparison, STNF recovery on held-out transforms]

## 7. Related work
- **PIPE** (Gu et al., arXiv:2602.01611) minimally rewrites agent interfaces preserving execution
  behaviour and measures a paired gap across models — it establishes interface reliance but offers
  **no normalization remedy, no formal state-transition-equality, no ranking-reversal characterization**.
- **TSCG** (Sakizli, arXiv:2605.04107) deterministically compiles tool schemas with a fixed operator
  set; **Learning to Rewrite Tool Descriptions** (arXiv:2602.20426) learns description rewrites that
  transfer to unseen *tools*. Neither targets a label-free normal form transferring to unseen
  *transform families*.
- **Schema First** (arXiv:2603.13404) holds tool semantics/information content constant and varies
  interface specification, motivating our content-matched control (H3).
We credit these explicitly and claim only the surviving conjunction (Section 4, novelty audit:
`papers/p1_toolmorph/novelty/novelty_attack.md`).

## 8. Limitations / Ethics
Synthetic environments; pilot-scale; subscription-CLI (product models, exact snapshots logged but
provider-updatable); STNF semantic coverage demonstrated via LLM compiler, not a guarantee. See
`research_contract.yaml` kill-gates. No private data; no external services.
