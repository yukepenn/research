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
