<!-- BEGIN START_CLAUDE.txt -->

Read every file in this package before modifying the research repository.
Then read the current repository's CLAUDE.md, RESEARCH_MANUAL.md, program/status.yaml,
all paper-specific research contracts, all evidence memos, all raw ledgers, and all red-team reports.

Treat 01_MASTER_WRAPUP_DIRECTIVE.md as the controlling post-pilot execution order.
Treat 02/03/04 as binding paper-specific specifications.
Treat 05 as the binding LaTeX, PDF, arXiv, artifact, and venue-packaging specification.
Treat 06 as the binding authorship, AI-disclosure, and human-signoff specification.

Do not merely summarize or propose a plan. Execute all reversible, authorized, no-extra-metered-cost work continuously and in parallel. Preserve every failed run and every negative result. Never invent data, citations, human annotations, or experimental outcomes. Never claim a paper is ready merely because a PDF compiles.

For each paper, the terminal state must be exactly one of:
SUBMIT_READY, ARXIV_ONLY, HOLD, or KILL.

Do not make an external submission, post to arXiv, choose a permanent license, sign a copyright form,
certify authorship, or publish a repository without explicit human approval.

<!-- END START_CLAUDE.txt -->


<!-- BEGIN 00_READ_ME_FIRST.md -->

# P1/P2/P3 Post-Pilot Wrap-Up Package

This package is a **post-pilot execution specification**, not a motivational research plan. It assumes the current repository already contains the first ToolMorph, CrossCheck, and DeltaResearch pilots.

## Current evidence that must not be rewritten away

- **P1 ToolMorph:** the current interface effect is directional but not statistically confirmed; structural and lexical changes are at a ceiling; the ranking-reversal hypothesis was refuted; the label-free STNF recovery experiment has not been run.
- **P2 CrossCheck:** all current workflows tie; the corpus is too easy; two apparent failures were specification defects; the existing pilot cannot support a scientific claim about heterogeneous review.
- **P3 DeltaResearch:** the current pilot shows substantial missed downstream revisions, but the perfect typed-graph result is an oracle-fed consistency check rather than end-to-end method performance. A real versioned-evidence layer and human adjudication are still missing.
- **P4 HarnessGuard:** remains killed. Do not revive it to satisfy a paper-count target.

## Venue map

- **P1 primary:** Transactions on Machine Learning Research (TMLR), rolling. Use the official TMLR style. Submit only if the controlled effect and label-free STNF recovery survive held-out evaluation.
- **P2 primary:** ACM FSE 2027 Research Track, full-paper deadline 2026-10-02 AoE. This is a top archival software-engineering conference, not a conventional journal. A strict-journal alternative is ACM TOSEM, but do not choose it merely to call every target a journal.
- **P3 primary:** Transactions of the Association for Computational Linguistics (TACL), monthly rolling deadline on the first of each month. Use TACL only if the no-gold end-to-end method and real evidence layer are complete. Otherwise use an ACL Rolling Review cycle, but never submit the same work to TACL and ARR simultaneously.

## What can realistically be completed in a 48-hour sprint

A 48-hour sprint can complete repository separation, decisive calibration experiments, frozen protocols, selected confirmatory runs, full LaTeX drafts, clean compilation, reproducibility packaging, and an honest submission decision. It **cannot guarantee** that three studies will independently produce top-tier evidence. The scientifically correct output may be one `SUBMIT_READY`, one `ARXIV_ONLY`, and one `HOLD/KILL`.

## Meaning of “aggressive”

Aggressive means parallel execution, strict prioritization, rapid falsification, minimal idle time, automation of repetitive work, exact bookkeeping, and immediate escalation of blockers. It does not mean fabricating sample size, hiding exclusions, overstating weak evidence, treating model output as human annotation, violating licenses, or forcing a submission decision.

<!-- END 00_READ_ME_FIRST.md -->


<!-- BEGIN 01_MASTER_WRAPUP_DIRECTIVE.md -->

# MASTER POST-PILOT EXECUTION DIRECTIVE

## 1. Role and mission

You are the Research Execution Lead for three independent papers:

1. P1 — ToolMorph / semantic-equivalent tool interfaces and label-free canonicalization.
2. P2 — CrossCheck / error-complementarity-aware review of coding-agent patches.
3. P3 — DeltaResearch / selective revision of reports under external evidence updates.

Your mission is to convert the current pilot repository into **three scientifically independent, auditable paper packages**, or to stop any paper that fails its scientific gate. You have authority to perform all reversible local actions, use public and properly licensed resources, create isolated repositories/worktrees, run existing authorized Claude/Codex subscription workflows, use local compute, use free CI, and restructure code. You do not have authority to fabricate results, spend metered money, violate service terms, access private systems, publish externally, select permanent licenses on the author's behalf, or certify human authorship.

The human principal investigator owns and has final responsibility for:

- the research questions and final scientific claims;
- the inclusion/exclusion policy;
- interpretation of the evidence;
- author list, conflicts, ethics statements, and licenses;
- final verification of citations and key raw outputs;
- the final click that submits or posts any work.

Your role is assistance in literature discovery, implementation, experiment orchestration, debugging, statistical scripting, artifact preparation, prose drafting, and internal review. Do not describe yourself or another model as an author.

## 2. Terminal decisions

Every paper must finish in exactly one state:

- `SUBMIT_READY`: all scientific, statistical, novelty, reproducibility, anonymity, citation, and venue-format gates pass.
- `ARXIV_ONLY`: a coherent and honest technical report exists, but one or more top-tier gates remain unmet; the report clearly identifies itself as a pilot/benchmark/negative result and does not overclaim.
- `HOLD`: the idea remains promising, but decisive data or independent validation cannot be completed with current authorized resources.
- `KILL`: the core claim is falsified, dominated by prior work, irreparably confounded, or not worth further resources.

A compiled PDF is not evidence of `SUBMIT_READY`.

## 3. Non-negotiable integrity constraints

### 3.1 Evidence

1. Every reported number must be generated from an immutable, append-only run ledger.
2. Every table cell and figure data point must have a script, input hash, run IDs, and generated artifact hash.
3. Never type an experimental number directly into LaTeX. Generate `tables/generated/*.tex` and `figures/generated/*` from the ledger.
4. Preserve failed runs. Classify them as model failure, infrastructure failure, invalid task, exclusion, or unknown. Never silently rerun until success.
5. Predeclare exclusions before sealed evaluation. If an unexpected invalid case appears, quarantine it, document the reason without looking at treatment outcomes, and report sensitivity with and without it where possible.
6. Do not call model-generated labels “human labels.”
7. Do not use a single LLM judge as the sole primary endpoint. Prefer executable tests, exact state-transition checks, source-version checks, calculators, structured gold labels, or genuine human annotation.
8. Report uncertainty. A directional mean without a confidence interval is not a confirmed effect.
9. Separate exploratory, calibration, and confirmatory runs in the ledger.
10. Do not revise a primary hypothesis after seeing confirmatory outcomes and present it as preregistered.

### 3.2 Citations

1. Open every cited primary source.
2. Record title, authors, venue/year, DOI or arXiv identifier, exact claim supported, page/section/table/figure, and verification date in `citation_ledger.csv`.
3. Prefer peer-reviewed or official primary sources; use preprints when they are the closest work and label them accurately.
4. Never cite a search snippet, a model summary, a secondary blog, or a bibliography entry that was not opened.
5. Run a final “citation entails sentence” audit. Each factual related-work sentence must be entailed by the cited source.
6. Check for retractions, newer versions, and author-name/title mismatches.
7. Run text-overlap checks against source papers and against the other two manuscripts.

### 3.3 Separation of roles

Maintain isolated contexts/worktrees for:

- Program Lead
- P1 Lead
- P2 Lead
- P3 Lead
- Novelty Prosecutor
- Data/Oracle Custodian
- Implementation Agent
- Statistician
- Independent Reproducer
- Citation Auditor
- LaTeX/Format Auditor
- Reviewer 2 / Red Team

The method-development agent must not see sealed labels. The evaluator must not modify the method. The paper writer must not invent missing results.

### 3.4 No-extra-metered-cost rule

- Use existing authorized Claude/Codex subscriptions, local compute, public datasets, free GitHub Actions, and open-source tools.
- Do not enable a paid API, cloud GPU, paid annotation service, or paid dataset.
- Record estimated subscription usage when available, but do not claim exact dollar cost unless an authoritative billing record exists.
- If a provider quota is exhausted, do not secretly spend money. Continue deterministic work, local/open-model work when feasible, manuscript engineering, or mark the experiment blocked.
- Never reduce a required sample solely to produce a positive result. Use sequential designs only if the stopping rule is frozen in advance.

## 4. Immediate repository surgery

Within the first execution block:

1. Create a read-only tag or bundle of the current monorepo state: `pilot-freeze-2026-06-25` (or the actual current date if later).
2. Generate `CURRENT_EVIDENCE_AUDIT.md` listing every existing run, claim, known error, exclusion, and unresolved contradiction.
3. Do not delete or rewrite the existing pilot ledgers.
4. Create three isolated paper roots, initially as worktrees or directories; prepare them to become separate public repositories later:

```text
p1-toolmorph/
p2-crosscheck/
p3-deltaresearch/
```

5. Each paper root must contain:

```text
CLAUDE.md
README.md
LICENSE_PLACEHOLDER.md
DATA_LICENSES.md
CITATION.cff
CHANGELOG.md
MODEL_USE.md
AI_ASSISTANCE_DISCLOSURE.md
REPRODUCIBILITY.md
SECURITY.md
pyproject.toml
uv.lock or requirements.lock
Dockerfile
Makefile
src/
tests/
data/raw/
data/interim/
data/processed/
experiments/configs/
experiments/prompts/
results/ledger/
results/generated/
analysis/
paper/sections/
paper/tables/generated/
paper/figures/generated/
paper/venue/
paper/arxiv/
artifact/anonymous/
artifact/public/
checksums/
```

6. Fix packaging. Do not retain a configuration that installs only `core` while paper modules work merely because `conftest.py` edits `sys.path`.
7. Pin exact dependencies and create a clean build container.
8. Add deterministic targets:

```text
make install-clean
make validate-data
make test
make reproduce-deterministic
make reproduce-main
make generate-paper-assets
make paper-review
make paper-arxiv
make artifact-anonymous
make artifact-public
make audit-citations
make audit-anonymity
make audit-arxiv
make full-check
```

9. `make full-check` must fail if any table is stale, any citation key is missing, any figure source is missing, any required manifest field is blank, any PDF contains unresolved references, or the source tree contains secrets/private paths.

## 5. Universal run schema

Every episode must store at least:

```yaml
run_id:
paper_id:
study_phase: exploratory | calibration | confirmatory | reproduction
protocol_version:
git_commit:
data_manifest_hash:
task_id:
task_family:
split: dev | validation | sealed_test
condition:
model_provider:
model_product:
model_exact_identifier:
model_snapshot_or_date:
cli_version:
reasoning_effort:
temperature:
seed:
system_prompt_hash:
user_prompt_hash:
harness_hash:
tool_schema_hash:
environment_image_digest:
visible_test_budget:
hidden_test_version:
input_tokens:
output_tokens:
tool_calls:
test_runs:
wall_clock_seconds:
subscription_or_cost_record:
raw_trace_path:
raw_trace_sha256:
oracle_version:
result:
exclusion_status:
exclusion_reason:
notes:
```

If the provider does not expose a field, write `unavailable` rather than guessing.

## 6. Common statistical protocol

Before sealed runs, the Statistician writes and hashes `analysis_plan.md` containing:

- unit of analysis;
- cluster and repeated-measure structure;
- primary endpoint and direction;
- primary comparison;
- minimum practically important effect;
- sample-size or sequential stopping rule;
- exclusions;
- model specification;
- uncertainty method;
- multiplicity correction for secondary tests;
- missing-data handling;
- robustness analyses;
- exact conditions that cause `SUBMIT_READY`, `ARXIV_ONLY`, `HOLD`, or `KILL`.

Preferred methods:

- paired binary outcomes: McNemar plus task-cluster bootstrap;
- repeated runs nested in tasks/repositories/worlds: hierarchical logistic or generalized mixed model;
- continuous cost/latency: paired cluster bootstrap and robust summaries;
- router evaluation: held-out calibration, risk-coverage curves, decision curves, and bootstrap CIs;
- multi-condition secondary comparisons: Holm or Benjamini–Hochberg as preregistered;
- report effect sizes and intervals, not only p-values.

Do not treat repeated stochastic executions of one task as independent tasks.

## 7. 48-hour execution board

This is a triage sequence, not a promise that evidence will cooperate.

### Block A — hours 0–3: freeze, audit, and parallelization

- Freeze current pilot state.
- Inventory current raw traces and validate hashes.
- Split paper worktrees.
- Assign the twelve agent roles.
- Update closest-work searches through the current date.
- Produce one-page research contracts with exact novelty deltas.
- Create decision dashboards for all three papers.

### Block B — hours 3–10: decisive dataset/oracle engineering

- P1: create harder non-ceiling tasks and information-matched transforms.
- P2: construct and validate a real-repository mid-difficulty corpus.
- P3: implement no-gold end-to-end pipeline and assemble controlled plus real versioned evidence.
- Build sealed manifests; do not expose test labels to method agents.
- Complete deterministic property tests and task-validity checks.

### Block C — hours 10–18: calibration only

- Run small calibration batches to tune task difficulty, detect infrastructure errors, and estimate variance.
- Do not tune methods on sealed outcomes.
- Apply predefined kill gates.
- Freeze analysis plans and code/config hashes for surviving studies.

### Block D — hours 18–32: sealed confirmatory execution

- Run confirmatory matrices with exact frozen configs.
- Use parallel workers only when they cannot share mutable state.
- Monitor for infrastructure failures, not scientific outcomes.
- Preserve all traces.
- At completion, unseal labels and run the frozen analysis.

### Block E — hours 32–39: independent reproduction and red team

- Independent Reproducer starts from a fresh checkout/container.
- Rebuild deterministic results and a stratified subset of model runs.
- Compare all hashes and metrics.
- Three red-team passes: novelty, methodology, and overclaim.
- Any fatal flaw returns the paper to experiment or `HOLD/KILL`.

### Block F — hours 39–48: manuscript and packaging

- Generate tables/figures from the ledger.
- Finish venue-native LaTeX.
- Compile review and arXiv variants in clean TeX environments.
- Build anonymous and public artifacts.
- Complete disclosure, limitations, ethics, data statements, and checklists.
- Produce per-paper terminal `DECISION.md`.

## 8. Manuscript writing rules

Each manuscript must answer, in order:

1. What exact problem is being studied?
2. Why do existing methods/benchmarks fail to answer it?
3. What is the one-sentence novelty delta relative to the closest work?
4. What is the falsifiable claim?
5. What evidence would have falsified it?
6. What data and oracles were used?
7. What is the main result with uncertainty?
8. What alternative explanations were tested?
9. Where does the method fail?
10. What can and cannot generalize beyond the tested models/tasks?

Never begin from a desired success story. Draft the Results section from generated tables first, then write the Abstract last.

Use conservative verbs:

- `we observe`, `we estimate`, `is associated with`, `improves on this benchmark`;
- avoid `proves`, `solves`, `guarantees`, `universally`, `human-level`, or `state of the art` unless literally justified.

## 9. Required paper package

For each paper produce:

```text
DECISION.md
CLAIMS.md
RESEARCH_CONTRACT.md
NOVELTY_MATRIX.md
RELATED_WORK_LEDGER.csv
ANALYSIS_PLAN.md
DATA_CARD.md
MODEL_AND_HARNESS_CARD.md
EXCLUSIONS.csv
RUN_MANIFEST.json
RESULTS_MANIFEST.json
REPRODUCTION_REPORT.md
REDTEAM_NOVELTY.md
REDTEAM_METHODS.md
REDTEAM_OVERCLAIM.md
CITATION_AUDIT.md
AI_ASSISTANCE_DISCLOSURE.md
LIMITATIONS.md
ETHICS_AND_BROADER_IMPACT.md
SUBMISSION_CHECKLIST.md
paper_review.pdf
paper_arxiv.pdf
paper_source_review.zip
paper_source_arxiv.zip
artifact_anonymous.zip
artifact_public_draft.zip
MANIFEST.sha256
```

`DECISION.md` must list:

- terminal state;
- target venue;
- one-sentence supported claim;
- strongest result with CI;
- strongest counterexample;
- remaining blockers;
- exact human decisions required;
- whether arXiv posting is recommended now;
- confidence in the decision.

## 10. Stop conditions

Stop and report rather than hallucinate completion if:

- a required public resource is inaccessible or unlicensed;
- provider quotas prevent the frozen sample size;
- a second genuine human annotator is required but unavailable;
- the primary effect does not survive matched controls;
- the proposed method relies on test labels or oracle outputs;
- the closest work subsumes the contribution;
- independent reproduction fails;
- citation audit finds unverifiable claims;
- the only way to make the paper fit is to hide negative results.

## 11. Communication protocol

Do not send generic progress prose. Maintain `program/WRAPUP_DASHBOARD.md` with:

- current state per paper;
- last verified commit;
- completed run count;
- failed/infrastructure run count;
- primary estimate and interval;
- quota/resource status;
- next executable task;
- blockers requiring human action.

Report facts, run IDs, hashes, decisions, and counterexamples. Do not report confidence based on aesthetics of a draft.

<!-- END 01_MASTER_WRAPUP_DIRECTIVE.md -->


<!-- BEGIN 02_P1_TOOLMORPH_EXECUTION_SPEC.md -->

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

<!-- END 02_P1_TOOLMORPH_EXECUTION_SPEC.md -->


<!-- BEGIN 03_P2_CROSSCHECK_EXECUTION_SPEC.md -->

# P2 — CrossCheck Full Execution Specification

## A. Target and decision

**Primary venue:** ACM FSE 2027 Research Track.

FSE is the best-fit top archival software-engineering venue. It is not a conventional journal. If a strict journal route is later preferred, evaluate ACM TOSEM only after the full empirical study exists; do not choose a venue to satisfy terminology.

**Current pilot is not a result.** It is a dataset-difficulty diagnosis. Do not present the 0.80 ties as evidence that cross-model review fails or succeeds.

Surviving claim:

> Under strict resource matching, heterogeneous review is useful only for task/defect regions where author and reviewer residual errors are complementary; a pre-call router can predict when cross-family review, same-family resampling, test generation, or no review gives the best cost-correctness tradeoff on held-out repositories.

## B. Research questions

- **RQ1:** Under matched resources, how do solo extra compute, self-review, independent same-family review, cross-family review, test generation, and reimplementation compare?
- **RQ2:** Which defect categories exhibit stable author–reviewer complementarity?
- **RQ3:** Are residual errors correlated strongly enough to explain when additional agents fail?
- **RQ4:** Can a router choose a workflow before the expensive second call and improve correctness at fixed budget on held-out repositories?
- **RQ5:** Does review introduce new regressions or over-editing?

## C. Corpus requirements

### C1. Data sources

Use free, public, reproducible software-defect resources with compatible licenses, such as appropriately selected tasks from SWE-bench Verified, BugsInPy, Defects4J, ManySStuBs4J, public issue/fix histories, or equivalent datasets. Verify every license and record it in `DATA_LICENSES.md`.

Do not merge datasets with incompatible redistribution terms. Where raw repositories cannot be redistributed, provide acquisition scripts, commit hashes, checksums, and transformed metadata.

### C2. Task construction

For each case record:

```yaml
repository:
base_commit:
issue_text:
visible_tests:
hidden_tests:
reference_fix_commit:
files_in_scope:
language:
defect_category:
expected_behavior:
prohibited_shortcuts:
license:
container_digest:
```

The author and reviewer must not see the reference patch or hidden tests.

### C3. Difficulty calibration without cherry-picking

The current corpus is at ceiling. Use dev repositories to calibrate a process that yields approximately **0.40–0.65 one-shot correctness** for the author models. Then freeze the selection algorithm and apply it to new sealed repositories. Do not manually retain only cases where cross-review looks good.

Valid screening factors include:

- issue requires multi-file reasoning;
- visible tests do not fully specify hidden behavior;
- patch is nontrivial but fits an execution budget;
- repository installs reproducibly;
- reference fix is attributable to one issue;
- issue text is sufficiently specified;
- hidden tests genuinely distinguish plausible near-misses.

Keep a screening ledger for every considered case, including rejected cases and reasons.

### C4. Independent task validation

Before any model runs:

1. reproduce the failure at base commit;
2. reproduce success at reference fix;
3. verify visible/hidden test separation;
4. have two independent validation passes assess issue sufficiency;
5. ensure no network secret or unsafe action is needed;
6. identify potential shortcut/contamination routes;
7. confirm the container can be reset deterministically.

An agent validation pass is not human annotation. If only one human is available, state that honestly and supplement with deterministic checks.

### C5. Split

Split by repository, not by individual issue:

- dev repositories for prompt/workflow design;
- validation repositories for router feature selection;
- sealed repositories for confirmatory comparison;
- optional temporal holdout using later commits.

## D. Defect taxonomy

Ensure adequate representation of:

- API semantic misuse;
- cross-file consistency;
- boundary/edge conditions;
- state mutation/order dependence;
- concurrency/asynchrony;
- exception/error handling;
- performance/resource issue;
- test omission;
- requirement misinterpretation;
- over-edit/unnecessary changes;
- regression introduced by a plausible fix;
- configuration/build/dependency issue.

Taxonomy labels may be multi-label. Freeze labeling guidelines and report agreement if more than one genuine annotator is used.

## E. Workflow arms

Implement all feasible arms with cold, isolated contexts:

1. `SOLO`: one author attempt.
2. `AUTHOR_EXTRA_REASONING`: same author with a larger but matched resource budget in one attempt.
3. `AUTHOR_INDEPENDENT_RESAMPLE`: a fresh same-model attempt with no access to first hidden reasoning.
4. `BEST_OF_K`: select among independent author attempts using visible evidence only.
5. `SELF_REVIEW`: author sees its own patch and visible evidence, then revises.
6. `SAME_FAMILY_COLD_REVIEW`: independent model instance from the same family reviews the patch.
7. `CROSS_FAMILY_COLD_REVIEW`: a different model family reviews the patch.
8. `TEST_GENERATION_ONLY`: reviewer writes additional tests/diagnostics; author applies repair.
9. `INDEPENDENT_REIMPLEMENTATION`: second model solves from scratch; an evidence-based selector chooses.
10. `ROUTER`: chooses among a subset before the second-stage call.

Do not label a second self-review call as “extra compute” if it is not a genuine independent-resample or longer-reasoning control.

## F. Resource matching

Predefine at least two analyses:

### F1. Hard-cap analysis

Match or cap:

- total input/output tokens;
- number of model calls;
- tool calls;
- visible test runs;
- wall-clock ceiling;
- repository context size;
- reasoning effort setting.

### F2. Frontier analysis

Rather than forcing exact equality when workflows have different structures, report the Pareto frontier of:

- correctness;
- total tokens;
- latency;
- test executions;
- calls;
- estimated subscription usage.

Do not report dollar efficiency unless actual authoritative cost is available.

## G. Review protocol

A reviewer may see:

- issue/task specification;
- repository snapshot;
- author patch/diff;
- visible test results;
- permitted execution tools.

A reviewer may not see:

- reference patch;
- hidden tests;
- author hidden chain-of-thought;
- sealed defect label if it would leak the answer;
- model outcome on other workflows for the same test task.

Store reviewer outputs as structured findings:

```yaml
finding_id:
file_and_location:
defect_hypothesis:
severity:
evidence:
proposed_test:
proposed_fix:
confidence:
```

Evaluate finding precision against executable outcomes, not reviewer eloquence.

## H. Complementarity analysis

Estimate for author `a`, reviewer `r`, defect type `d`:

\[
C(a,r,d)=P(r\text{ detects or repairs }d\mid a\text{ leaves }d).
\]

Also estimate:

- residual error correlation;
- conditional review benefit;
- probability of introducing a new defect;
- directionality (A reviews B versus B reviews A);
- calibration of reviewer confidence;
- benefit by task/repository complexity.

Do not train the router on sealed outcomes.

## I. Router

The router acts **before** the expensive second-stage call. Permissible features:

- repository/language metadata;
- issue length and type;
- diff size and topology;
- files/modules touched;
- visible test outcomes;
- author trajectory summaries without hidden chain-of-thought;
- static-analysis/test-coverage signals;
- author model identifier;
- uncertainty proxies available at deployment.

Not permissible:

- hidden test result;
- reference fix similarity;
- sealed defect label;
- downstream reviewer result;
- features computed from the answer the router is supposed to predict.

Use simple, auditable models first. Compare to:

- always no review;
- always self-review;
- always cross-family review;
- cheapest valid strategy;
- oracle workflow selector upper bound.

Evaluate calibration, coverage, and decision utility on repository-held-out test data.

## J. Metrics

### Primary

- final patch correctness under frozen resource regime, measured by hidden tests and repository-specific oracles;
- router correctness/resource utility on held-out repositories.

### Secondary

- defect detection recall/precision;
- new-regression rate;
- visible-versus-hidden test overfitting;
- over-edit size/unnecessary files changed;
- time/tokens/test runs;
- cost per corrected patch when real cost exists;
- directionality and defect-type complementarity;
- reviewer confidence calibration;
- router regret relative to oracle.

## K. Statistics

- Cluster by repository and task.
- Paired comparisons because workflows share tasks.
- McNemar and repository-cluster bootstrap for correctness.
- Mixed-effects logistic regression with repository/task effects and workflow/model/defect interactions.
- Bootstrap complementarity matrix uncertainty.
- Router evaluation on untouched held-out repositories only.
- Report all invalid/infrastructure failures separately.
- Do not use the same tasks to tune corpus difficulty, router, and final claim.

## L. Required outputs

Tables:

1. Corpus source, language, repository, defect taxonomy.
2. Validation and exclusion flow.
3. Workflow resource budgets.
4. Main correctness comparison.
5. Complementarity matrix with uncertainty.
6. New regressions and review precision.
7. Router held-out performance and regret.
8. Cost/latency frontier.

Figures:

1. Workflow design diagram.
2. Paired correctness plot.
3. Complementarity heatmap with confidence markers.
4. Resource–correctness Pareto frontier.
5. Router risk–coverage/decision curve.
6. Failure taxonomy and directionality.

## M. P2 kill gates

Set `HOLD` or `KILL` if:

- a valid mid-difficulty corpus cannot be assembled without outcome-based cherry-picking;
- all arms still tie after strict resource matching;
- author extra compute or best-of-k uniformly dominates review;
- complementarity is unstable across repositories;
- the router fails to beat the cheapest fixed strategy on held-out repositories;
- benchmark validity problems remain material;
- resource quotas prevent a defensible confirmatory matrix.

A scientifically valuable null result may support `ARXIV_ONLY`, but only if the corpus is valid and the null is adequately powered.

## N. P2 manuscript blueprint

Possible evidence-dependent title:

**CrossCheck: When Does Heterogeneous Model Review Improve Coding-Agent Patches?**

Sections:

1. Introduction and practical decision problem.
2. Related work: LLM code review, self-correction, multi-agent error correlation, cross-model critics.
3. Corpus and validation.
4. Budget-matched workflows.
5. Error-complementarity model and router.
6. Main empirical comparison.
7. Router results and cost frontier.
8. Failure analysis and threats to validity.
9. Data Availability statement after Conclusion as required by FSE.

FSE paper must be written as an empirical software-engineering study, not a generic agent benchmark.

<!-- END 03_P2_CROSSCHECK_EXECUTION_SPEC.md -->


<!-- BEGIN 04_P3_DELTARESEARCH_EXECUTION_SPEC.md -->

# P3 — DeltaResearch Full Execution Specification

## A. Target and decision

**Primary strict-journal venue:** Transactions of the Association for Computational Linguistics (TACL).

**Alternative:** ACL Rolling Review only if the paper is deliberately routed to an ACL conference. Do not submit to TACL and ARR simultaneously. If the work receives ARR review, TACL has a nine-month ineligibility rule tied to the ARR submission month.

Current supported observation:

> In controlled evidence-world updates, tested agents frequently fail to propagate required changes to downstream report claims while mostly preserving untouched claims.

Current unsupported claim:

> A typed graph method achieves perfect end-to-end revision.

The existing perfect result used oracle/gold information and is only a consistency upper bound.

Surviving full-paper claim:

> An end-to-end, no-gold pipeline that detects external evidence changes, constructs claim–source/dependency provenance, recomputes affected values, and performs constrained patching improves affected-claim coverage while preserving unaffected content on controlled and real versioned-evidence updates.

## B. Research questions

- **RQ1:** How often do report-revision agents miss direct versus downstream obligations under different evidence changes?
- **RQ2:** Which stage is the bottleneck: delta detection, claim extraction, dependency inference, recomputation, constrained editing, or verification?
- **RQ3:** Can predicted provenance/dependency structure improve the joint revision-quality frontier without gold affected sets, gold graphs, or gold post-update values?
- **RQ4:** Do controlled findings transfer to real official evidence revisions, documentation changes, corrections, or retractions?
- **RQ5:** Can the system produce auditable rationales linking each report edit to source versions and derivations?

## C. Formal problem

Each episode contains:

- old evidence world `W0` with versioned sources;
- old report `R0` generated or validated against `W0`;
- evidence delta `ΔW`;
- new evidence world `W1`;
- gold affected claims `A` for evaluation only;
- gold unaffected claims `U` for evaluation only;
- derivations and expected revised values for evaluation only.

The method receives only `W0`, `R0`, and observable `W1/ΔW`. It must not receive `A`, `U`, gold dependency edges, or post-update claim values.

## D. Controlled dataset

### D1. Dependency topologies

Generate diverse worlds with:

- linear chains;
- branching trees;
- diamonds/converging derivations;
- one source supporting many claims;
- one claim supported by multiple sources;
- source conflict;
- temporal supersession;
- numerical aggregation;
- ratios and percentage changes;
- threshold-triggered qualitative conclusions;
- retraction/correction propagation;
- claims repeated or paraphrased across sections;
- mixed direct and derived claims.

### D2. Delta types

- numeric revision;
- categorical status change;
- source retraction;
- source correction/erratum;
- more authoritative source appears;
- source conflict;
- time-validity expiry;
- definition/methodology change;
- unit or denominator change;
- API/documentation behavior change;
- evidence deletion/unavailability.

### D3. Report variation

Vary:

- number of claims;
- report length;
- number of sections;
- paraphrase distance;
- table versus prose expression;
- citation placement;
- derivation depth;
- irrelevant evidence distractors.

### D4. Controlled oracle

The generator must output an executable derivation graph and validate all pre/post values. Gold graphs are used only by the evaluator and oracle upper-bound conditions, never by the proposed method.

## E. Real versioned-evidence layer

Use free, public, versioned sources with clear provenance. Candidate families:

- official macroeconomic/statistical releases with later revisions;
- public government/regulatory documents with version histories;
- public API/software documentation git histories and release notes;
- arXiv version changes, formal corrections, errata, or retraction metadata;
- public benchmark/leaderboard corrections;
- product or standards documentation with archived versions.

For every case store:

```yaml
case_id:
domain:
source_uris:
source_license_or_terms:
W0_timestamp:
W0_hashes:
W1_timestamp:
W1_hashes:
delta_summary:
R0_creation_protocol:
gold_claim_inventory:
gold_affected_claims:
gold_unaffected_claims:
gold_recomputed_values:
annotation_rationale:
annotators:
adjudication_status:
```

### E1. Temporal integrity

- Use only evidence available at `W0` when constructing `R0`.
- Prevent hindsight leakage.
- Archive or hash source snapshots where permitted.
- Record source publication and revision timestamps.
- Distinguish correction of an old fact from arrival of a genuinely new fact.

### E2. Annotation

Prefer two qualified human annotators plus adjudication. Do not fabricate a second annotator. If only one human is available:

- explicitly report single-human annotation;
- use deterministic calculations and source-version checks where possible;
- arrange a blinded sample audit if a second person becomes available;
- do not state inter-annotator agreement.

Agent-generated candidate labels may accelerate annotation but must be approved by a human and labeled as assisted.

## F. End-to-end method

Implement these stages:

1. **Evidence Delta Detector** — identifies changed facts, source status, units, methods, temporal validity, and contradictions.
2. **Claim Extractor** — inventories atomic factual, numerical, comparative, causal, and recommendation claims in `R0`.
3. **Provenance Linker** — maps claims to exact source versions, spans, calculations, and intermediate claims.
4. **Typed Dependency Constructor** — predicts direct support, arithmetic derivation, temporal dependency, definitional dependency, logical implication, and conflict-resolution edges.
5. **Impact Propagator** — predicts the affected subgraph and uncertainty.
6. **Retriever/Recomputer** — re-reads changed sources and performs actual calculations using a deterministic calculator where applicable.
7. **Constrained Patcher** — edits only claims/sections predicted to require change, with explicit patch scope.
8. **Post-Update Verifier** — checks source-version alignment, calculations, contradictions, stale citations, and unintended changes.
9. **Revision Rationale Generator** — emits an auditable ledger of old claim, new claim, source delta, derivation, and confidence.

No stage may read gold evaluation labels.

## G. Baselines and upper bounds

Actual prompted/executable baselines:

1. naive “update this report” prompt;
2. full regeneration from `W1`;
3. retrieval-augmented update without dependency graph;
4. flat claim–citation ledger;
5. edit-propagation/cascade baseline comparable to closest manuscript-edit work;
6. graph without recomputation;
7. graph + recomputation without constrained patching;
8. full end-to-end method.

Oracle diagnostic conditions, always labeled upper bounds:

9. gold affected set only, no gold values;
10. gold graph/impact, actual recomputation;
11. predicted impact + gold recomputed value;
12. full gold oracle.

The paper must visibly separate baselines, ablations, and oracle diagnostics.

## H. Stage-wise diagnostics

Measure:

- delta detection precision/recall;
- claim extraction precision/recall;
- provenance link accuracy;
- dependency-edge precision/recall by type;
- affected-set precision/recall;
- recomputation correctness;
- patch correctness;
- verifier detection rate;
- final report quality.

This enables a causal error decomposition rather than inferring bottlenecks from one prompt condition.

## I. Metrics

### Primary joint outcome

Use a preregistered joint metric or decision rule that rewards required updates and penalizes harmful unnecessary changes. Do not rely on UCP alone, because a system that edits nothing can score high on preservation.

Report separately:

- affected-claim recall and precision;
- semantic preservation of unaffected claims;
- harmful edit rate;
- numerical recomputation accuracy;
- stale citation/source-version rate;
- unsupported claim rate;
- contradiction-resolution accuracy;
- provenance completeness;
- revision minimality;
- audit-rationale correctness;
- tokens, latency, and tool use.

Where an LLM semantic judge is used, validate it against genuine human labels and deterministic checks. Keep a non-LLM primary analysis wherever possible.

## J. Splits

- controlled topology holdout;
- delta-type holdout;
- source/domain holdout;
- real-world temporal holdout;
- optional model-family holdout.

Do not allow paraphrases of the same evidence world across train/test.

## K. Experimental conditions

Test at least two authorized model families for naive/full-regeneration baselines. The proposed pipeline may use a fixed model, but report whether gains come from structure versus a stronger model by crossing method and model where feasible.

Freeze:

- prompts;
- extraction schemas;
- graph types;
- calculation tools;
- patch constraints;
- judge versions;
- budgets;
- evaluation code;
- stopping rule.

## L. Statistics

- Unit: evidence world/case.
- Repeated model runs nested within world.
- Paired comparisons across methods on the same world.
- World-cluster bootstrap CIs.
- Mixed models for method, model, topology, delta type, and domain.
- Report controlled and real layers separately, then a predeclared pooled analysis if justified.
- Correct secondary comparisons.
- Conduct sensitivity to annotation disagreements and semantic-equivalence thresholds.

## M. Required outputs

Tables:

1. Controlled and real dataset composition.
2. Annotation and oracle reliability.
3. Stage-wise diagnostic accuracy.
4. Main final-report metrics on controlled holdout.
5. Main final-report metrics on real evidence updates.
6. Ablations and oracle gap.
7. Delta-type/topology/domain breakdown.
8. Cost, latency, and failure modes.

Figures:

1. Evidence-delta-to-report-patch pipeline.
2. Example claim dependency graph and propagated update.
3. Affected recall versus harmful edit frontier.
4. Stage-wise error waterfall.
5. Controlled-to-real transfer plot.
6. Failure examples: missed cascade, over-revision, stale source, wrong recomputation.

## N. P3 kill/hold gates

Set `HOLD` or `KILL` if:

- the method still consumes gold affected sets/graphs/values;
- a real versioned-evidence layer cannot be legally and reliably assembled;
- full regeneration dominates both correctness and preservation at matched budget;
- gains exist only on generator-known synthetic templates;
- primary result depends on an unvalidated LLM judge;
- annotation quality is insufficient for the central claim;
- closest work subsumes the final contribution after a fresh audit;
- independent reproduction fails.

Use `ARXIV_ONLY` for a strong empirical benchmark/pilot if the phenomenon is robust but the end-to-end method or real layer remains incomplete.

## O. P3 manuscript blueprint

Evidence-dependent title:

**DeltaResearch: Auditable Report Revision under External Evidence Updates**

Sections:

1. Introduction and exact gap relative to edit-propagation benchmarks.
2. Problem definition and evidence-world formalism.
3. Controlled and real versioned-evidence datasets.
4. End-to-end no-gold method.
5. Evaluation protocol and human/deterministic oracles.
6. Main controlled results.
7. Real-evidence transfer.
8. Stage-wise error analysis and ablations.
9. Related work: deep research, citation provenance, edit propagation, temporal knowledge, report revision.
10. Limitations, ethics, data statement, conclusion.

For TACL, keep the core manuscript focused and follow the official current page/appendix rules. Do not link supplementary repositories in the anonymized TACL submission if the current TACL rules prohibit such links; state the intended release anonymously.

<!-- END 04_P3_DELTARESEARCH_EXECUTION_SPEC.md -->


<!-- BEGIN 05_LATEX_VENUE_ARXIV_RELEASE_SPEC.md -->

# LaTeX, PDF, Venue, arXiv, and Artifact Specification

## 1. Do not use the generic article template as the submission template

A generic document beginning with `\documentclass{article}` plus `geometry`, custom fonts, and custom margins is acceptable for a private report, but it is **not reliable for venue submission**. Use the current official venue template without modifying margins, fonts, spacing, heading sizes, or page geometry.

Build common content in shared section files and separate top-level wrappers:

```text
paper/
  sections/
    abstract.tex
    introduction.tex
    related_work.tex
    method.tex
    data.tex
    experiments.tex
    results.tex
    analysis.tex
    limitations.tex
    ethics.tex
    conclusion.tex
  tables/generated/
  figures/generated/
  references.bib
  macros.tex
  venue/main.tex
  arxiv/main.tex
```

Never fork the prose into two diverging versions. Wrapper differences should be identity, disclosure placement, metadata, and venue-specific required sections.

## 2. P1 TMLR wrapper

Clone the current official TMLR style repository. Begin from its `main.tex`. The core form is:

```tex
\documentclass[10pt]{article}
\usepackage{tmlr} % anonymous review
% \usepackage[preprint]{tmlr}  % identified arXiv version
% \usepackage[accepted]{tmlr}  % accepted camera ready only

\input{macros.tex}
\usepackage{hyperref}
\usepackage{url}

\title{ToolMorph: Testing and Restoring Semantic Interface Invariance in Tool-Using Agents}

\author{...} % hidden automatically in anonymous mode; populated for preprint
\def\month{MM}
\def\year{YYYY}
\def\openreview{\url{https://openreview.net/forum?id=XXXX}}

\begin{document}
\maketitle
\input{sections/abstract}
...
\bibliography{references}
\bibliographystyle{tmlr}
\appendix
...
\end{document}
```

Rules:

- use official `tmlr.sty` and `tmlr.bst`;
- do not edit the style file;
- anonymous review uses `\usepackage{tmlr}`;
- arXiv uses `[preprint]`;
- only accepted camera-ready uses `[accepted]`;
- include the required first-page LLM/AI-assistance footnote in a manner compatible with anonymity and current TMLR policy;
- keep main content near or below 12 pages when possible because longer papers can review more slowly, but never omit necessary evidence merely to hit an arbitrary length.

## 3. P2 FSE 2027 wrapper

Use the current ACM `acmart` template and the FSE-required class:

```tex
\documentclass[acmsmall,screen,review,anonymous]{acmart}

\setcopyright{none} % only if the official review template/instructions permit; verify current sample
\acmConference[FSE 2027]{ACM International Conference on the Foundations of Software Engineering}{2027}{...}

\begin{document}
\title{CrossCheck: When Does Heterogeneous Model Review Improve Coding-Agent Patches?}
\author{Anonymous Author(s)}
\begin{abstract}
\input{sections/abstract}
\end{abstract}
\keywords{coding agents, code review, software testing, large language models}
\maketitle
...
\section{Data Availability}
An anonymized replication package is provided ...
\bibliographystyle{ACM-Reference-Format}
\bibliography{references}
\end{document}
```

Do not blindly copy metadata commands; start from the latest official `sample-acmsmall-conf.tex` and the FSE CFP. Required current constraints include:

- `acmsmall,screen,review,anonymous`;
- single-column review layout;
- at most 18 pages for text/figures plus 4 reference pages for initial submission;
- heavy double-anonymous review;
- a `Data Availability` section after the Conclusion;
- complete disclosure of generative-AI-created content under current ACM policy;
- no author-revealing repository link in the anonymized paper/package.

For an identified arXiv version, create a separate wrapper that removes `review,anonymous`, restores author metadata, and adds the public repository link. Do not make the arXiv version say “submitted to FSE.”

## 4. P3 TACL wrapper

Download the current official files from TACL:

```text
tacl2021v1.sty
acl_natbib.bst
tacl2021v1-template.tex
```

Begin from the official template and preserve all layout settings. Do not approximate the style with `geometry` or an ACL conference template.

Maintain:

- an anonymous TACL review wrapper with no author names, affiliations, acknowledgments, identifying repository links, PDF author metadata, or revealing self-citations;
- an identified arXiv wrapper using the same section sources;
- a TACL comments-to-editor record disclosing any arXiv preprint title, URL, server, and date;
- no dual submission;
- no supplementary-material link in the review manuscript when prohibited by current TACL rules;
- anonymous text stating the intended data/code release.

If P3 is routed to ARR instead of TACL, create a separate official ACL-style wrapper, respect the eight-page long-paper content limit, mandatory Limitations section, double-column appendix rules, and Responsible NLP Checklist. Never use TACL and ARR review simultaneously.

## 5. Citation system

Use BibTeX/natbib in the form required by each venue:

- narrative: `\citet{key}`;
- parenthetical: `\citep{key}`;
- multiple sources: `\citep{key1,key2}`;
- never cite a raw URL in place of a scholarly reference;
- include DOI and arXiv/eprint fields where appropriate;
- use title case/bracing carefully for model names and acronyms;
- deduplicate preprint and published versions; cite the archival version where it exists.

Create `citation_ledger.csv` columns:

```text
bibkey,title,authors,year,venue,doi_or_arxiv,primary_source_url,
claim_supported,source_location,verified_by_human,verified_date,
retraction_checked,notes
```

The Citation Auditor must:

1. open every source;
2. check every metadata field;
3. verify the cited sentence is supported;
4. detect citations to superseded versions;
5. run duplicate-key and unused-reference checks;
6. flag any bibliography item generated only from model memory.

## 6. Figure and table standards

- Prefer vector PDF figures generated by scripts.
- Use fonts embedded in the PDF.
- Make figures readable in grayscale and for common color-vision deficiencies.
- Use no decorative 3D charts.
- Show raw or paired distributions when sample size permits, not only bars.
- Include uncertainty visually.
- Every figure has a concise self-contained caption stating sample/unit and interval type.
- Every table states unit, direction, uncertainty, and whether values are exploratory or confirmatory.
- Use `booktabs`; avoid vertical lines.
- Do not shrink text below venue rules.
- Do not put a figure on TACL's final first page if current final-production rules forbid it.

## 7. Compilation pipeline

Use a clean TeX Live environment matching arXiv support, preferably TeX Live 2025 unless a venue template requires otherwise.

Commands:

```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error -file-line-error main.tex
latexmk -c
```

Run:

- `chktex` with a documented suppression file;
- unresolved citation/reference scan;
- `pdftotext` scan for `??`, `TODO`, `FIXME`, `Anonymous` in identified version, author names in anonymous version, and accidental prompt text;
- `pdfinfo` metadata audit;
- `pdffonts` to reject Type 3/unembedded fonts;
- overfull/underfull box audit;
- page-count check;
- link check;
- spelling/grammar check that does not alter technical meaning;
- clean-container rebuild and PDF checksum.

No source package may contain:

- `.aux`, `.log`, `.out`, `.synctex`, editor backups;
- private notes or comments;
- prompt transcripts;
- secrets/tokens;
- local absolute paths;
- author metadata in anonymous packages;
- unused figures/data;
- reviewer simulations or confidential memos.

## 8. Abstract construction

Write the abstract last, in one paragraph unless venue rules say otherwise. It must contain:

1. problem and why it matters;
2. exact gap;
3. method/dataset;
4. study scale described truthfully;
5. principal result with an effect and uncertainty when space permits;
6. bounded conclusion.

Never write `state-of-the-art` without a complete and fair comparison. Never include a number not generated by the final analysis script.

## 9. arXiv packaging

arXiv prefers TeX source when TeX exists. Build a minimal source archive containing:

- top-level `main.tex`;
- used section files;
- `references.bib` and/or correct `.bbl` as required;
- required venue/style files when redistribution is allowed;
- used figure files;
- used macro files;
- no extraneous outputs or private comments.

Requirements:

- safe ASCII filenames with consistent case;
- one clear top-level TeX file;
- compile in a clean TeX Live 2025 container;
- inspect arXiv-generated PDF, not only local PDF;
- verify title, abstract, authors, categories, comments, and license manually;
- do not use `\today` if a rebuild-changing date is undesirable;
- ensure all code/data links are already public and resolve;
- human chooses the permanent arXiv license;
- human presses submit.

Suggested categories, subject to human confirmation:

- P1: primary `cs.AI` or `cs.LG` based on final emphasis;
- P2: primary `cs.SE`, optional `cs.AI` cross-list;
- P3: primary `cs.CL`, optional `cs.AI` cross-list.

Do not post a preprint merely to create the appearance of completion. Recommend arXiv only when the paper is internally coherent, citation-audited, and unlikely to require a reversal of its central claim.

## 10. Anonymous versus public artifacts

### Anonymous package

- scrub git history or create a clean export;
- remove usernames, emails, organization names, GitHub URLs, local paths, model account IDs, and author-linked DOI/Zenodo metadata;
- use neutral repository/project identifiers;
- include exact reproduction instructions;
- test all links for identity leakage;
- zip and hash.

### Public package draft

- author identities and real repository URL;
- LICENSE and data licenses selected/approved by human;
- CITATION.cff;
- release notes;
- frozen tag;
- checksums;
- code of conduct/security notice as relevant;
- artifact DOI plan, if later desired;
- no secrets or redistributable-prohibited data.

## 11. Final PDF quality gate

A paper is not deliverable until:

- compilation has zero errors and no unresolved references;
- page limit and anonymity pass;
- all fonts are embedded;
- figures are legible at 100%;
- all main values match `RESULTS_MANIFEST.json`;
- every citation passes the ledger audit;
- Limitations/Ethics/Data Availability/AI disclosure are present as required;
- independent reproducer can regenerate all main tables and figures;
- Reviewer 2's fatal concerns are resolved or explicitly limit the claim.

<!-- END 05_LATEX_VENUE_ARXIV_RELEASE_SPEC.md -->


<!-- BEGIN 06_HUMAN_AUTHORSHIP_AI_DISCLOSURE_SIGNOFF.md -->

# Human Authorship, AI Assistance, and Final Sign-Off

## 1. Do not make a false disclosure

Do not write that Claude/Codex were used only for grammar if they also assisted with literature discovery, code generation, experiment orchestration, debugging, statistical scripts, tables, or prose. The disclosure must match the actual workflow.

Do not overcorrect by saying the models originated the scientific claims if the human principal investigator selected, approved, audited, and takes responsibility for them. Authorship is based on genuine human intellectual responsibility and accountability, not on who typed the first draft.

## 2. Baseline truthful disclosure text

Adapt this to each venue and to the actual record:

> Generative AI tools, including Anthropic Claude Code and OpenAI Codex, were used as assistive tools for literature discovery, code generation, experiment orchestration, debugging, statistical scripting, internal review, and prose drafting. The human author selected and approved the research questions, experimental designs, inclusion and exclusion rules, interpretations, and final scientific claims; reviewed the key raw outputs and generated analyses; verified the cited sources; and assumes full responsibility for the work. No model was listed as an author or treated as ground truth. Reported tables and figures were generated from auditable experiment ledgers and deterministic analysis scripts.

Modify any clause that is not literally true. For example, do not say every citation was human-verified until the human has actually completed that audit.

## 3. Venue placement

- **TMLR:** include the explicit first-page footnote required by current TMLR policy; preserve anonymity while accurately identifying the class of tools and scope of assistance.
- **FSE/ACM:** fully disclose generative-AI-created content under current ACM authorship policy. Include a non-identifying disclosure in the anonymous manuscript where required and a complete Acknowledgments disclosure in the identified version.
- **ARR/ACL:** complete the Responsible NLP Checklist accurately and describe writing/coding assistance in Acknowledgments/README as required.
- **TACL:** follow current ACL/TACL ethics and authorship rules; include a transparent disclosure in the appropriate non-identifying location and complete any editorial metadata honestly.
- **arXiv:** include the identified disclosure in the manuscript or a clearly visible reproducibility/acknowledgment statement.

## 4. Human intellectual contribution record

Create `HUMAN_CONTRIBUTION_RECORD.md` with dated entries for:

- initial research ideas and motivations;
- acceptance/rejection of candidate hypotheses;
- dataset/oracle design decisions;
- primary endpoint and kill-gate approval;
- interpretation of key failures/counterexamples;
- changes made after red-team review;
- final claim approval;
- authorship and venue decisions.

This is not performative paperwork. It should truthfully document human control and responsibility.

## 5. Human verification checklist

The final human author must personally:

1. Read each manuscript from beginning to end.
2. Open every cited source and verify the citation ledger.
3. Inspect all primary tables against generated files and ledger records.
4. Inspect a stratified sample of at least 10% of raw traces plus every major failure category and every excluded case.
5. Verify that no method accesses sealed labels or gold outputs.
6. Review task/data licenses and redistribution terms.
7. Approve the exact author list, order, affiliations, conflicts, funding, and acknowledgments.
8. Approve the AI-assistance disclosure as factually complete.
9. Approve limitations, ethics, and broader-impact statements.
10. Verify anonymity of review PDFs and artifacts.
11. Verify there is no overlapping archival submission.
12. Choose the arXiv license and check metadata.
13. Perform the final external submission/posting action.

Claude must not mark these steps complete merely because it thinks they are likely complete. It may prepare evidence and checklists; the human marks them.

## 6. Submission decision rubric

### `SUBMIT_READY`

All of the following:

- core claim survives confirmatory controls;
- method is end-to-end and no-gold where claimed;
- strongest baseline is fairly implemented;
- held-out generalization exists;
- uncertainty is reported;
- novelty survives a current-date audit;
- independent reproduction passes;
- paper and artifact pass venue rules;
- human signs all required checks.

### `ARXIV_ONLY`

- coherent, useful, and reproducible result;
- claims are honest and bounded;
- one or more top-tier requirements remain unmet;
- posting now would not mislead readers or permanently anchor a false central claim.

### `HOLD`

- promising direction but missing required evidence/resources/annotation;
- no pressure to post a weak PDF.

### `KILL`

- claim falsified or contribution subsumed;
- result irreparably confounded;
- full study is not worth the expected resource cost.

## 7. Final handoff from Claude

Claude's final report must not say “submitted.” It must say one of:

- `READY FOR HUMAN SUBMISSION TO [VENUE]`;
- `READY FOR HUMAN ARXIV REVIEW/POSTING`;
- `HOLD — [BLOCKERS]`;
- `KILL — [EVIDENCE]`.

For each paper, provide the exact local paths to:

- review PDF;
- arXiv PDF;
- source archives;
- anonymous artifact;
- public artifact draft;
- decision memo;
- human sign-off checklist;
- checksums.

<!-- END 06_HUMAN_AUTHORSHIP_AI_DISCLOSURE_SIGNOFF.md -->
