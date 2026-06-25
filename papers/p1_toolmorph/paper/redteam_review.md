# Red-Team Review — p1_toolmorph (ToolMorph)

Reviewer role: adversarial "Reviewer 2" + skeptical methodology/statistics reviewer.
Date: 2026-06-25. Mandate: find every reason to reject or downgrade; credit honesty; cite the draft.
All numbers below were re-derived directly from `artifacts/run_ledger.jsonl` (80 rows, paper_id=p1_toolmorph),
`artifacts/p1_interactive_result.json`, and a fresh run of `property_tests/equivalence.py`.

---

## Summary

ToolMorph proposes (a) a formal "byte-identical state-transition" definition of tool-interface
equivalence, (b) a property-verified benchmark of six behavior-preserving transform families over
three stateful environments, (c) a pilot showing that one of three exercised transforms
(enum-encoding) degrades agent success, and (d) STNF, a label-free "Semantic Tool Normal Form,"
positioned as the surviving novel core relative to PIPE.

The infrastructure contribution is real and I independently reproduced it: the equivalence suite runs
27,300 randomized per-call cases (plus response/error/state checks) with **zero mismatches**
(draft says ">15,000"; the claim is conservative and SUPPORTED). The paper is also unusually honest:
it separates deterministic infra (Section 6.1) from stochastic pilot results (6.2), pre-registers the
load-bearing experiment, and flags its own negatives.

However, as a vehicle for the claims it actually prints, the paper does not stand: its **primary
contribution (H5, the STNF remedy) is entirely unrun**; the surviving novel core is a plan, not a
result. Worse, the **headline phenomenon table cannot be reproduced from the authors' own ledger** —
the Codex number is simply wrong, and the Claude number contradicts the paper's stated exclusion. The
effect that survives correction is ~−0.10 for both models with **bootstrap CIs that include zero**, at
a **ceiling baseline of 1.00**, with **n=10 tasks, a single seed, and no repeats**. The phenomenon
itself is, by the authors' own novelty audit, largely pre-empted by PIPE.

## Score: 3 / 10

## Recommendation: REJECT (re-submittable; clear, pre-registered path to a real paper)

Reject as a full-paper submission to a flagship venue because (1) the PRIMARY claimed contribution is
not tested, and (2) the central reported numbers are inconsistent with the evidence file they are
required to come from. This is a data-integrity defect plus a missing core, not merely "needs more n."
The honest framing, the genuinely verified equivalence artifact, and the pre-registered protocol keep
it off the floor and make a future resubmission credible — but they do not make the current draft
publishable.

---

## Fatal weaknesses

### F1. The PRIMARY contribution (H5 / STNF) is unrun — the paper has no tested novel result.
The contract (`research_contract.yaml`) and claim registry both mark **P1-H5 as UNTESTED and
PRIMARY**, and the draft concedes it (Section 6.4: "H5 ... is not yet run"; Limitations: "the PRIMARY
claim H5 ... is not yet run"). The novelty audit (`novelty_attack.md` §3) is explicit that the
*phenomenon* (EQ+META, ranking shift) is pre-empted and that "the single asset that keeps us above the
floor is the normalization remedy with verified transfer to unseen transform families." That asset is
not delivered. What *is* implemented in `stnf.py` is (i) an `OracleCanonicalizer` that the draft itself
calls "an upper bound, not a contribution," and (ii) a `StaticCanonicalizer` that **provably abstains
on exactly the one transform that degrades** (`STATIC_COVERAGE`: `enum_encoding: False`,
`lexical_aliasing: False`). So the only repair component that can touch the only degrading family is
the LLM compiler — which is untested. Net: the surviving novel core is a pre-registration, not a finding.

### F2. The headline phenomenon table is not reproducible from the ledger; the Codex number is wrong and the Claude number contradicts the stated exclusion.
Re-aggregating `run_ledger.jsonl` by `result.task_success`:
- The one excluded "infrastructure error" is a **TIMEOUT episode in the Claude / enum_encoding cell**
  (`run_id b4a4b7d3c373`, `episode_status: TIMEOUT`, `task_success: false`, `n_calls: 8`).
- **Claude enum** = 8/10 = **0.80 only if that TIMEOUT is COUNTED as a model failure.** If it is
  "excluded" as the draft claims ("79 valid episodes (1 infrastructure error excluded)", §6.2), Claude
  enum = 8/9 = **0.89, Δ −0.11** — half the printed effect. The draft simultaneously asserts the
  episode is excluded AND reports the figure (0.80) that only exists if it is included. Internally
  contradictory.
- **Codex enum** = 9/10 = **0.90, Δ −0.10** in both the raw ledger and the authors' own aggregator
  `p1_interactive_result.json` (`codex|enum_encoding: mut_success: 0.9, n: 10`). The draft and the
  evidence note both print **0.89, Δ −0.11**. There is **no Codex episode to exclude** (the only
  timeout is Claude's), so 0.89 for Codex is unsupported by any consistent rule.
- Under a single consistent exclusion policy the data are either {Claude 0.80, Codex 0.90} (count the
  timeout) or {Claude 0.89, Codex 0.90} (exclude it). The printed pair {Claude 0.80, Codex 0.89}
  occurs under **neither**. The draft's own rule — "Every number in the final draft must come from ...
  the run ledger" (header) — is violated.

**Falsification/fix:** run the aggregation from `run_ledger.jsonl`; adopt one timeout policy
(`analysis_plan.yaml` says API timeouts are excluded and "NOT true agent failures," which forces Claude
enum → 0.89); record the exclusion in `exclusions.csv` (it currently lists only the archived
single-shot run, not this episode); correct Codex to 0.90/−0.10. Note the consequence: under the
paper's own policy the corrected effect is **−0.11 (Claude) and −0.10 (Codex)** — essentially identical
and roughly half the abstract's "−0.20" Claude headline.

### F3. The effect does not survive its own confidence intervals.
The authors' aggregator reports the bootstrap CIs the draft omits: Claude enum Δ = −0.20, **CI
[−0.50, 0.00]**; Codex enum Δ = −0.10, **CI [−0.30, 0.00]**. Both intervals **include zero**. The
abstract and Section 6.2 nonetheless state enum-encoding "degrades success for both models." With both
CIs touching the null, "degrades" is an assertion the data do not license; the honest statement is "we
cannot reject no-effect." The draft hedges qualitatively ("wide CIs," "pilot signal, not confirmation")
but never prints the CIs and still uses the verb "degrades." After the F2 correction the effect rests
on **1–2 failing task-episodes per model**.

### F4. Ceiling confound + n=10, single seed, zero repeats → the design cannot support its conclusions.
Baseline success is **1.00 for every model × interface cell** (verified). At ceiling there is (a)
near-zero power to detect small degradations and (b) **no headroom to ever demonstrate STNF "recovery"**
(the primary endpoint) on anything except enum's one-to-two failures. "Structurally recoverable
transforms are absorbed losslessly" (abstract) is therefore not establishable: 0 degradation at a 1.00
ceiling is indistinguishable from "tasks too easy to break." The ledger confirms **one episode per
(model, transform, task) cell, seed=0, no repeats** — so run-to-run LLM sampling variance is entirely
unmeasured, and the enum "failures" cannot be distinguished from sampling noise.

---

## Overclaims (sentence-level)

1. **Abstract:** "Enum-encoding ... degrades success for both models — Claude 1.00→0.80 (Δ −0.20) and
   Codex 1.00→0.89 (Δ −0.11)." Overclaims on three counts: the verb "degrades" against CIs that include
   0 (F3); the −0.20 Claude figure depends on counting an excluded TIMEOUT as a model failure (F2); the
   Codex 0.89/−0.11 is not in the data (ledger = 0.90/−0.10).
2. **Introduction:** "dropped task success from 1.00 to 0.80 for Claude and from 1.00 to 0.89 for
   Codex." Same defect, stated as fact in the lead paragraph.
3. **§6.2 / Table & "Honest reading":** repeats the unreproducible {0.80, 0.89} pair; "directionally
   consistent across two independent model families" is the defensible part, but the magnitudes are not.
4. **Abstract / §6.2 mechanism:** "consistent with a semantic-decoding rather than a structural-parsing
   failure ... structurally recoverable transforms are absorbed losslessly." A mechanistic story built
   on ~2–3 total failure events; "losslessly" is unsupportable at a 1.00 ceiling (F4). Hedged
   ("consistent with") but still over-reaches.
5. **§3 / §6.1:** "Any model effect therefore cannot be a benchmark artifact." Too strong. The negative
   control (`sim_agents.codec_adapter`) is an oracle agent *given the transform* that emits the exactly
   correct mapped calls, so zero degradation is true **by construction**; it rules out *scoring* bugs,
   not the possibility that the specific opaque codes chosen are confounded (e.g., harder/ambiguous), or
   that the effect is an information-availability effect rather than a generic "representation" effect
   (see T1). Correct claim: "rules out a scoring/harness artifact," not "cannot be a benchmark artifact."
6. **§6.3 / Abstract scope:** framing the Claude<Codex enum gap as a "directional hint that
   representation alone can reorder models." The gap (≤0.10) is within the bootstrap noise and rests on
   1–2 tasks; calling a ceiling-tied / single-cell separation a "reorder" is generous. The draft does
   label H4 UNTESTED — credit — but the abstract still advertises "even model RANKING"-adjacent framing.

Honest-disclosure credit (do **not** penalize): the draft repeatedly says "pilot signal, not a
confirmatory result," "only one of three exercised transforms degraded," "two model families cannot
support a Kendall-tau ranking claim," and quarantines the SUPPORTED infra from the model results. This
is the right behavior and should be preserved, not punished.

---

## Citation integrity — OK (true)

Cross-checked the draft's citation keys against `artifacts/citations.sqlite` (9 sources with
`verified=1`: ahe2026, mrdre2026, tscg2026, refutepromote2026, codeasharness2026, pipe2026,
editpropbench2026, agentassay2026, cc02xiang2026).
- Cited as fact: `[pipe2026]`, `[agentassay2026]`, `[tscg2026]`, `[cc02xiang2026]` — **all verified=1**.
- `schemafirst2026` (2603.13404) and `rewritetooldesc2026` (2602.20426) are `verified=0` and are each
  explicitly tagged "[unverified — pending Director verification]" in §7. Correct, conservative handling.
- No hallucinated or unverified source is cited as fact. EditPropBench / Mr.DRE are in the registry but
  **not** cited in this draft, so they are not relevant collisions here.
- Minor note: `cc02xiang2026` is a ResearchGate publication-number URL (weaker provenance than arXiv/DOI)
  but is only used for a soft "has precedent" framing, not a load-bearing result. Acceptable.

Verdict: `citation_integrity_ok = true`.

---

## Threats / alternative explanations

- **T1 (most damaging conceptually): "representation only" ≠ "information held constant."** The draft's
  own mechanism says enum-encoding leaves "codes with no recoverable surface meaning." That is a
  concession that the *information available to the model* changed, even though the *environment state
  transition* did not. Byte-identical state transitions (P1-C0) do not imply equal decodable information
  in the prompt. So the one effect found is plausibly an *information-availability* effect — precisely
  Schema First's (2603.13404) "the bottleneck is semantic, not representational" thesis the contract
  raises as a kill-risk (H3). H3 is untested, so the central "we changed only the representation"
  framing is unestablished for the only transform that moved.
- **T2: enum-codes confound.** The effect may be specific to the particular opaque code scheme (length,
  collisions, tokenization) rather than "removing legible enum tokens" in general. No alternative
  enum-encoding variant is tested.
- **T3: product-harness vs model.** "Two model families" are two commercial agent products (Claude Code,
  Codex CLI), each with its own internal scaffolding/system prompt. The draft asserts "the same harness
  drives every model, so effects are attributable to the model," but the CLIs wrap their own loops;
  observed model differences may be product-scaffolding differences. Subscription-CLI, single-seed,
  provider-updatable models also mean the headline numbers are **not externally reproducible**.
- **T4: SUPPORTED-vs-model conflation — mostly avoided, partially reintroduced.** Credit: §6.1/§6.2 keep
  the deterministic equivalence proof separate from the stochastic pilot, and the negative control is
  clearly labeled. But the **abstract** bundles "(>15,000 cases, zero mismatch)" as an "Artifact"
  headline next to the model deltas, which can read as more empirical heft than 79 episodes provide. Keep
  the separation the body already enforces.

---

## Required for acceptance (minimum concrete changes/experiments)

1. **Run H5 — the primary claim.** Label-free LLM-STNF on **held-out transform families and held-out
   tools**, vs the strongest non-oracle baseline (token/content-matched rewrite; TSCG-style compiler).
   Report Δ-recovered with task-clustered CIs against the pre-registered margin (≥5 pts or ≥20%
   sensitivity-AUC). Without this the paper has no tested novel contribution.
2. **Fix and reconcile the numbers.** Adopt one timeout policy (per `analysis_plan.yaml`, exclude →
   Claude enum 0.89/−0.11), log it in `exclusions.csv`, correct Codex to 0.90/−0.10, and **print the
   bootstrap CIs** (both currently include 0). Replace "degrades" with a significance-honest statement.
3. **Escape the ceiling.** Harder tasks so baseline < 1.00, giving power to detect degradation and room
   to show recovery; scale from 10 toward the planned 24–120 tasks.
4. **Add repeats and multiple seeds** (≥3–5) per cell to separate sampling noise from a stable
   representational effect; report within-task variance.
5. **H3 information/content control.** A token/length/information-matched enum variant (and a
   matched-legibility code scheme) to rebut Schema First; if the effect vanishes, say so (the contract's
   own kill condition).
6. **Head-to-head vs PIPE** (novelty audit Experiment 1) on overlapping environments: show the
   non-PIPE families produce comparable/larger Δ and that STNF beats "do nothing" on PIPE-style aliases.
7. **Ranking (H4) or drop it.** ≥6 model families with Kendall-τ + bootstrap, or remove ranking framing
   entirely (currently a 2-model, ceiling-tied artifact).
8. **Reproducibility.** Pin model versions (API or version-hash + seeds); disentangle base model from
   product scaffolding (T3).

---

## Strongest surviving contribution

Two things genuinely survive, ranked by what is *actually delivered*:

- **Delivered now:** a **property-verified equivalence benchmark** — six behavior-preserving transform
  families over three stateful environments with an audited byte-identical state-transition guarantee
  (P1-C0), which I reproduced at 27,300 cases / zero mismatch, plus a metamorphic negative control. This
  is a clean, honest infrastructure/resource contribution and the paper's most defensible asset today.
- **Claimed-novel core (undemonstrated):** the **label-free Semantic Tool Normal Form (STNF) that
  transfers to UNSEEN transform families.** Per the novelty audit, no verified prior work (PIPE — diagnose
  only; TSCG — fixed operators; Rewrite-Tool-Desc — unseen *tools*, performance not canonical form) does
  this, so the conception remains uncollided. But it is a pre-registered plan (H5 UNTESTED), not a result.

`novelty_still_holds = true` in the narrow sense that the STNF-transfer core is not pre-empted by the
cited prior art; it is, however, **undemonstrated**. The *phenomenon* novelty (interface variation
changes success / ranking) is largely dead on arrival to any reviewer who knows PIPE (2602.01611), as
the authors' own audit concedes.

---

## What it honestly is right now (one paragraph)

Right now this is a carefully-built, admirably honest **pilot-and-protocol package**, not a paper with a
result. Its load-bearing scientific claim (a label-free normal form that repairs interface-induced
degradation on unseen transforms) is unrun; what is proven is that the authors' own transform codecs are
internally consistent (a 27k-case unit test of their construction, which is genuine but close to
tautological since the transforms were built to preserve state). The lone empirical "phenomenon" — that
opaque enum codes hurt — rests on one-to-two failing episodes per model, sits at a 1.00 ceiling with a
single seed and no repeats, has bootstrap CIs that include zero, and is printed with a Claude figure
that contradicts the paper's own exclusion rule and a Codex figure that does not exist in the ledger.
Strip the overclaims and the unreproducible digits and you have an honest **null/near-null pilot plus a
verified benchmark and a strong pre-registration**. That is a legitimate foundation and a credible TMLR/
workshop resource note — but it is a reject as a flagship full paper until H5 is run and the headline
numbers are corrected to match the ledger.
