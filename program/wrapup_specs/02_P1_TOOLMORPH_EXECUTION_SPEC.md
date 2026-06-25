# P1 — ToolMorph Full Execution Specification

## A. Target and decision

**Primary venue:** Transactions on Machine Learning Research (TMLR).

**Permitted terminal outcomes:** `SUBMIT_READY`, `ARXIV_ONLY`, `HOLD`, `KILL`.

**Do not revive the refuted ranking-reversal claim** unless a new, preregistered held-out study independently supports it. The paper is not “interfaces matter”; closest work already studies behavior-preserving interface rewrites. The surviving contribution must be:

> Under information- and readability-matched, state-transition-equivalent interface transformations, tool-using agents exhibit measurable behavioral non-invariance; a label-free semantic canonicalizer restores performance on unseen tools and unseen transformations better than simple description rewriting or examples.

## B. Research questions

- **RQ1 — Controlled non-invariance:** Do semantically equivalent tool interfaces change task success when information content, token budget, tool semantics, and environment state transitions are matched?
- **RQ2 — Mechanism:** Which transformation dimensions predict failures: opacity, nesting, granularity, result representation, error representation, defaults, or composition depth?
- **RQ3 — Recovery:** Can a label-free semantic normalizer/canonicalizer recover performance without being told the transformation class or gold mapping?
- **RQ4 — Generalization:** Does recovery transfer to held-out tools, transformation compositions, task domains, and at least one held-out model family?
- **RQ5 — Cost:** Does recovery improve the success–token–latency frontier rather than merely adding more context and retries?

## C. Hypotheses

Freeze one primary hypothesis after calibration:

- **H1 primary:** On sealed tasks, transformed interfaces reduce paired task success relative to original interfaces under matched information controls, and label-free STNF recovers a preregistered fraction of the loss.

Secondary:

- H2: the controlled effect remains after matching description length/readability and providing complete codebooks.
- H3: STNF outperforms description rewrite, few-shot examples, and static heuristics on held-out transformation compositions.
- H4: STNF abstention is calibrated; high-confidence outputs are more reliable than low-confidence outputs.
- H5: recovery is not solely explained by additional tokens or tool-call budget.

Do not define a minimum effect after seeing sealed data. During calibration, select and document a practically meaningful threshold, such as an absolute success difference or recovery fraction, based on task cost and pilot variance.

## D. Task suite

### D1. Difficulty calibration

The current baseline is at a ceiling. Build tasks until the **original-interface development success rate is approximately 0.55–0.85** for each tested model family. This is a calibration target, not a test-set selection criterion.

Use at least three stateful domains, such as:

- calendar/scheduling;
- inventory/order management;
- issue tracker/helpdesk;
- file/workspace operations;
- lightweight database administration;
- structured research retrieval with deterministic records.

Each task should require at least two of:

- dynamic entity IDs discovered at runtime;
- multiple dependent tool calls;
- read-modify-verify behavior;
- partial failure or recoverable error;
- selection among similar entities;
- a transaction with an observable final state;
- a constraint that makes naive retries dangerous;
- a final verification step.

### D2. Specification validation

For every task:

1. Write a machine-readable intent and required final-state predicate.
2. Write forbidden side effects.
3. Provide a deterministic oracle independent of the model trajectory.
4. Execute a reference program against all interface variants.
5. Verify the task has at least one valid solution.
6. Have an independent agent review ambiguity without seeing model outcomes.
7. Quarantine any task with multiple incompatible interpretations.

### D3. Split design

Create group-disjoint splits:

- dev: tools and base transforms available to method development;
- validation: unseen tasks within seen tool families;
- sealed test A: unseen tools in seen domains;
- sealed test B: unseen compositions of transformations;
- sealed test C: unseen domain where feasible;
- model holdout: at least one model family not used to tune STNF.

Near-duplicate tasks, aliases, and generated variants of the same state machine must remain in one split.

## E. Transformation DSL

Implement transformations as executable bidirectional codecs with property tests. Include:

1. argument nesting/flattening;
2. semantically neutral renaming/aliasing;
3. enum/value encoding with an explicit, information-complete codebook;
4. optional/default parameter re-expression;
5. tool split into atomic calls;
6. tool merge into a composite/transaction call;
7. sequential versus batch form;
8. response JSON/table/text representation;
9. exception versus status-code versus structured-error representation;
10. reordered fields and equivalent schema constraints;
11. wrapper layers and namespace changes;
12. two- and three-way transformation compositions.

Every transform object must expose:

```python
encode_request()
decode_request()
encode_response()
decode_response()
map_error()
reference_equivalence_test()
state_transition_equivalence_test()
information_content_report()
readability_control_report()
```

### E1. Matched controls

The enum pilot may merely reflect opacity. Include all of:

- opaque codes with full codebook;
- human-readable aliases;
- random code assignment per task;
- token-length-matched descriptions;
- description-informativeness-matched controls;
- explicit example versus no example;
- same semantics expressed with different syntax but equal documentation.

Report whether the effect survives each control.

## F. Conditions

At minimum:

1. Original interface.
2. Transformed interface.
3. Transformed + description rewrite.
4. Transformed + few-shot tool-use examples.
5. Transformed + static hand-coded canonicalizer.
6. Transformed + oracle canonicalizer upper bound.
7. Transformed + label-free STNF.
8. Original + equal extra token budget control.

The oracle canonicalizer is an upper bound and must never be described as the proposed method.

## G. Label-free STNF requirements

STNF must not receive:

- the transformation label;
- the original schema at test time unless this is explicitly the deployment setting and given to all baselines;
- a gold argument mapping;
- hidden task state;
- test-set examples;
- post-hoc human corrections.

A valid STNF may use:

- tool names/descriptions/schemas visible to the agent;
- declared types and constraints;
- a small dev library of generic canonical forms;
- deterministic parsing and static analysis;
- model-assisted schema interpretation, provided its budget and model are recorded;
- calibrated abstention.

Implement a typed semantic intermediate representation containing:

- action intent;
- entity type;
- operation type;
- argument roles;
- value domains;
- preconditions;
- effects;
- error semantics;
- idempotency/reversibility metadata;
- response fields.

### G1. STNF ablations

- no descriptions;
- schema only;
- descriptions only;
- no error normalization;
- no response normalization;
- no action granularity normalization;
- no abstention;
- deterministic only;
- model-assisted only;
- full system.

## H. Experimental execution

### H1. Calibration

- Start with a small balanced set.
- Adjust task difficulty only using dev outcomes.
- Estimate intraclass correlation across repeated runs.
- Decide repeats per task and number of task clusters before sealed runs.
- Freeze model identifiers, prompts, budgets, and stopping rule.

### H2. Confirmatory matrix

Use at least two currently authorized model families; add a third only if available without additional metered cost. Claims must be scoped to the tested families.

Balance:

- task domain;
- transformation class;
- transformation depth;
- model;
- condition;
- seed/repetition.

Randomize condition order and reset environment state between episodes. Prevent cross-run memory/caches from leaking answers.

## I. Metrics

### Primary

- paired task success difference: transformed versus original;
- STNF recovery fraction, defined and bounded before analysis;
- held-out recovery on unseen transformation compositions.

A possible recovery definition is:

\[
R = \frac{S_{\text{STNF}} - S_{\text{transformed}}}
         {S_{\text{original}} - S_{\text{transformed}}},
\]

but define handling for zero/negative denominators before use. Also report absolute success changes.

### Secondary

- invalid tool-call rate;
- argument semantic error rate;
- state-transition correctness;
- error recovery success;
- number of actions/retries;
- input/output tokens;
- latency;
- abstention and conditional accuracy;
- per-transform and per-domain heterogeneity;
- rank stability only as exploratory unless newly confirmed.

## J. Statistics

- Unit: task, with repeated model runs nested within task.
- Paired comparisons on the same task/transform.
- Task-cluster bootstrap CIs.
- McNemar for paired binary summaries.
- Hierarchical logistic model with task random intercept and fixed effects for model, transform, condition, and interactions.
- Correct secondary comparisons using Holm or a frozen FDR rule.
- Report sensitivity excluding ambiguous/infrastructure-failed cases.
- Do not call a result significant merely because a model-level average differs.

## K. Required outputs

Tables:

1. Dataset/task/transform taxonomy.
2. Property-based equivalence and oracle validation.
3. Original versus transformed paired outcomes with CIs.
4. Matched-control analysis.
5. STNF versus baselines on held-out tools/transforms.
6. Ablations.
7. Cost/latency and abstention.
8. Failure taxonomy.

Figures:

1. Transformation and semantic-IR schematic.
2. Per-task paired effect plot.
3. Recovery with CIs by held-out category.
4. Risk–coverage curve for abstention.
5. Error mechanism decomposition.

## L. P1 kill gates

Set `KILL` or `ARXIV_ONLY` if any holds:

- difficulty remains at ceiling/floor after legitimate calibration;
- information/readability controls erase the effect;
- effect appears only for opaque enums and not broader semantic-equivalent changes;
- STNF is no better than simple description rewrite or equal extra compute;
- STNF does not generalize to held-out tools/transforms;
- method relies on transform labels or gold mappings;
- independent reproduction fails.

## M. P1 manuscript blueprint

Suggested title only if evidence supports it:

**ToolMorph: Testing and Restoring Semantic Interface Invariance in Tool-Using Agents**

Sections:

1. Introduction and three precise contributions.
2. Problem definition and invariance criterion.
3. Transformation DSL and state-transition equivalence.
4. Label-free STNF.
5. Experimental protocol.
6. Main controlled non-invariance results.
7. Recovery and generalization.
8. Mechanism, ablation, cost, and failure analysis.
9. Related work, explicitly comparing PIPE and adjacent schema/compiler work.
10. Limitations, broader impact, and conclusion.

Do not claim universal agent invariance. Scope conclusions to the tested task and model families.
