# Red-Team Review — p2_crosscheck

**Paper:** CrossCheck: Budget-Matched, Error-Correlation-Aware Routing for Heterogeneous Code Review
**Reviewer:** Adversarial Reviewer 2 / skeptical methodology-statistics reviewer
**Date:** 2026-06-25
**Recommendation:** REJECT (as a full-paper submission). As a *pilot / registered report*, closest to major-revision; the honesty and the verified deterministic component keep it from a desk-reject.
**Score:** 3 / 10

---

## Summary

This is an honest, well-scoped, and almost entirely *negative/inconclusive* pilot. It builds a small
deterministic single-defect corpus (10 toy modules, 10 defect types) with LLM-free hidden tests, runs
real Claude/Codex models via subscription CLIs over a 60-episode bidirectional matrix, and finds that
NO_REVIEW = AUTHOR_MORE_COMPUTE = CROSS_FAMILY_REVIEW = **0.80** final-patch correctness with *exactly
zero* spread. The authors correctly diagnose this as an **all-ceiling corpus** (8/10 cases one-shot;
the 2 non-ceiling cases were underspecified-spec benchmark bugs), not as evidence against cross-review.
They keep the deterministic infrastructure result (P2-C0, SUPPORTED) cleanly separate from the
underpowered workflow pilot (P2-H2, PARTIAL), and they validate the complementarity decomposition and
the ReviewRoute router only on *self-planted simulated data*, labelling them as pipeline self-tests.

I verified the evidence directly: the ledger holds 60 p2 episodes; 16/20 = 0.80 in every workflow; 8
defects at 1.00 and 2 (`type_serialization`, `collateral_regression`) at 0.00; all three \cite keys
are among the 9 verified registry sources; the deterministic corpus claim reproduces (all 10 cases
clean-pass and mutant-fail). The numbers in the draft match the evidence note. The problem is not
fabrication — it is that **the pilot delivers no novel empirical finding**, several headline framings
overstate the delta versus cc02, and the one claim the "all-ceiling" conclusion leans on (the two
fixed cases "now solved one-shot") is **not in the immutable ledger**.

This is the kind of pilot that should be *credited for honesty but rejected as a full paper*: it is a
method package plus a diagnosis, not a result.

---

## 1. Novelty — is the surviving contribution real, or engineering?

The novelty sweep (`novelty/novelty_attack.md`) is correct that cc02 (Xiang et al., KDD'26) already
publishes the bidirectional Claude↔Codex writer/reviewer matrix *including same-model self-review* and
the headline "cross-review is direction-dependent; the stronger model solo is on the Pareto frontier."
The surviving contribution is therefore **only the conjunction** (budget-matched author-extra-compute
arm + defect-type complementarity mechanism + held-out review-action router). I accept that no *single*
prior work has the exact conjunction, so `novelty_still_holds = true` **as a design**. But as *realized
in this pilot* the conjunction is hollow:

- **The budget-matched arm, as implemented, is self-review — which cc02 already has.**
  `AUTHOR_MORE_COMPUTE` is a single self-improve pass (`pilot.py:_improve_prompt`, "Review and improve
  your own fix"). That is operationally cc02's same-model self-review condition. The draft's claim (§1)
  that cc02 "never compares against giving the same author the equal extra compute" is **overstated**:
  cc02 explicitly includes Claude-reviews-Claude / Codex-reviews-Codex, i.e. a same-author second pass.
  The genuine delta the novelty attack demanded (resample-k / best-of-k / extended-thinking at equal
  *token/$* budget — `novelty_attack.md` §4.1) is **not implemented**. So the paper's flagship
  differentiator vs cc02 is, right now, a relabel of cc02's self-review.
- **The complementarity model and router are validated only against a signal the authors planted in
  their own simulator** (`sim_outcomes.py`: `_CORRECT` tables are hand-designed so cross-family is best
  on serialization/api, then `router.py` "discovers" it). Recovering your own planted signal is a unit
  test, not validation. These are engineering deliverables (clean, repository-grouped nested CV with a
  documented leakage ban — genuinely good code), but they are **not empirical contributions**.

**Verdict:** the *novel empirical claim is untested*; what remains is (i) reusable methodology/code and
(ii) an honest diagnosis. That is an engineering + methodology contribution, not a discovery.

## 2. Evidence / statistics

- **Sample size.** "n = 20 per workflow" overstates the independent unit: it is 10 tasks × 2 authors,
  clustered, and after the authors' own exclusions only **8 distinct tasks** carry any information — all
  at the ceiling. With two model families and zero variance, no inferential statistic is possible (the
  draft concedes this).
- **The 0.80 headline mixes denominators.** §6.2 reports 0.80 "with the two benchmark-bug cases in,"
  but those two cases are *excluded* from the analysis (`exclusions.csv`). By the authors' own logic the
  within-analysis rate is **1.00 / 1.00 / 1.00 on 8 cases**, not 0.80. Leading the abstract with 0.80
  reports a number the methodology says to drop.
- **The "post-fix solved one-shot" claim is not ledgered.** I checked git: the pilot ran at commit
  `e511132` (pre-fix specs); the spec fix landed in `67a866d`; **no post-fix re-run exists** in
  `run_ledger.jsonl` (zero `type_serialization`/`collateral_regression` rows with `final_correct=true`).
  The "we fixed the spec; Claude then solves it one-shot" assertion (abstract, §6.1, `exclusions.csv`)
  is therefore an **unlogged side-verification**. The entire "effectively all-ceiling" conclusion rests
  partly on it.
- **Budget is not actually matched.** §4 and §6.2's header say "matched budget = 2 model calls," but
  NO_REVIEW is **1 call** (`pilot.py`, `n_calls=1`; confirmed in the ledger). Only the decisive
  author_more vs cross comparison is matched at 2 calls; including NO_REVIEW under a "2 calls" header is
  inaccurate in a paper whose entire thesis is budget matching. (`claim_registry.csv` even pre-flags
  "budget not truly matched.")
- **Product-CLI, not API → not reproducible.** Subscription CLIs give no temperature/seed/version
  control; the Claude version is unpinned and "codex = gpt-5.5" is an assumption not recorded in the
  ledger (`model_id` is just `codex`). The result is not re-runnable to the same numbers.
- **No CIs, no held-out, no real-data router run** (all conceded).

## 3. Overclaims (specific sentences)

1. §1: "*cc02 ... never compares against giving the same author the equal extra compute*." — False/misleading;
   cc02 includes same-model self-review, which is a same-author second pass, and is what `AUTHOR_MORE_COMPUTE`
   implements.
2. Abstract / §4 / §6.2 header: "*at a fixed budget of two model calls we compare NO_REVIEW, ...*" /
   "*matched budget = 2 model calls*." — NO_REVIEW is 1 call; not matched.
3. Abstract / §6.1: "*which we fixed and verified the model then passes one-shot*" / "*Claude then solves
   it one-shot*." — the verification is not in the ledger; should be re-run and logged or softened to
   "expected to be solvable; not yet re-ledgered."
4. §1 (contributions 3, 4) and §6.4: "*validated on simulated data*" / router "*beats always-cross,
   always-self, and random on held-out repositories ... approaches the oracle upper bound*." — "validated"
   overstates "passes a self-test against a self-planted signal." The clause reads as a capability claim;
   the next sentence walks it back, but the contributions list does not.
5. Abstract: "*leaving an effectively all-ceiling corpus with no headroom*." — depends on the unlogged
   post-fix solve and on reclassifying the only two informative cases as benchmark bugs (see Threats).

To be fair, the **headline empirical framing is not overclaimed**: the draft repeatedly and correctly
calls the tie "inconclusive and underpowered, not a confirmation that cross-review is useless." That
restraint is exactly what a pilot should do and I am crediting it, not punishing it.

## 4. Citation integrity — `citation_integrity_ok = true`

The draft cites exactly three keys as fact: `cc02xiang2026`, `refutepromote2026`, `agentassay2026`. All
three are in the verified-source registry (`artifacts/citations.sqlite`, verified=1; exactly 9 such
sources). Every other neighbor in §7 is referenced descriptively and explicitly tagged "[unverified —
pending Director verification]." No hallucinated citation is asserted as fact. Caveats (not fatal):
- **cc02 is triangulated, not fully verified.** The registry marks it verified=1, but `related_work.csv`
  still lists cc02 as verified=no with authors "Unknown," and `novelty_attack.md` says only its
  *existence + qualitative finding* are confirmed (PDF 403; numbers unconfirmed). The draft is careful
  to cite cc02 only for the qualitative finding and never a number — consistent with the triangulation —
  but the cross-file status inconsistency should be reconciled.
- The `r≈0.52` statistic in §7 originates from cc07 (not among the 9 verified) but is explicitly flagged
  unverified, so it is not cited as fact.

## 5. Threats / alternative explanations

- **The excluded cases carried the only (weak) negative signal.** Pre-fix, the two hard cases failed
  0.00 under *every* workflow — including cross-family review, which did **not** rescue them. Reclassifying
  them as benchmark bugs and excluding them is a defensible call (the specs were genuinely
  underspecified), but it is a researcher-degree-of-freedom decision that removes the only cases with
  headroom, and the removed evidence pointed *against* cross-review helping. A skeptic reads the data as
  "a weak negative signal, suppressed by exclusion," not purely "no signal."
- **Ceiling confound is real and admitted.** The corpus cannot exercise its own question; the tie is an
  artifact of difficulty, correctly diagnosed.
- **Deterministic SUPPORTED infra is NOT conflated with the model findings** — credit. §3 (P2-C0),
  §6 (P2-H2), the abstract, and §8(v) all keep the deterministic corpus result (which I reproduced: all
  10 cases clean-pass + mutant-fail) separate from the inconclusive workflow comparison. This is exactly
  the discipline many pilots get wrong.
- **Router/complementarity "validation" is circular** and should never be read as evidence of real-world
  routing utility (the draft says as much, but readers skim).

## 6. Required for acceptance (minimum to become a publishable full paper)

1. **A mid-difficulty, fairly-specified corpus** (real-repo agent near-miss patches, containerized) where
   NO_REVIEW lands ~0.4–0.6, so a workflow contrast is measurable. Report effect sizes + CIs and the
   pre-registered mixed-effects model (workflow×author×reviewer + defect_type + (1|repo)+(1|task)).
2. **A real budget-matched author-extra-compute arm** — resample-k / best-of-k / extended-thinking at
   equal token/$ — explicitly distinguished from cc02's self-review; not a single self-improve pass.
3. **≥3 model families, full bidirectional matrix**; fit reviewer-strength main effect + author×reviewer
   interaction and show the interaction survives controlling for reviewer strength (or honestly report it
   does not, per the kill-gate).
4. **Run the complementarity decomposition and ReviewRoute on real outcome data**, not self-planted sim;
   the router must beat always-stronger-solo (the cc02 heuristic) and a cc13 disagreement router on
   held-out repositories at matched budget.
5. **Ledger the post-fix re-run** of the two fixed cases (or drop the "solved one-shot" claim); pin model
   versions / use API with fixed seeds; report CIs; fix the "matched budget = 2 calls" mislabel.
6. **Containerized execution** of model-produced code (the in-process `exec` is both a sandboxing risk
   and an external-validity limit).

## 7. Strongest surviving contribution

The **deterministic, LLM-free defect corpus (P2-C0, verified)** plus the **honest, well-diagnosed
negative finding** that strong models one-shot easy controlled single-defect modules — which yields a
concrete, reusable methodological bar: *a review-value benchmark must first demonstrate its no-review
baseline is off the ceiling.* That diagnosis, the clean separation of deterministic infrastructure from
model behavior, and the leakage-disciplined router/complementarity scaffolding are genuinely useful to
the next study. They are scaffolding and a caution, not a finding.

## 8. What it honestly is right now

This is a **negative/underpowered pilot plus a method package**: a deterministic toy-defect corpus and a
clean Tier-0 harness (budget-matched protocol, defect-type complementarity decomposition, and a
held-out-repository review-action router) that currently pass only **self-tests on self-planted simulated
signals**, attached to a single real-model experiment that produced an **exact three-way tie at 0.80 on
an all-ceiling corpus** and therefore tells us nothing new about cross-model review beyond what cc02
already established. Its real value is diagnostic and infrastructural: it proves the deterministic oracle
works, shows that easy controlled defects cannot separate review workflows, and lays out exactly the
harder corpus and experiments needed. It is honestly written, does not overclaim its headline, and
properly quarantines its one solid (deterministic) result — which is why it earns credit rather than a
desk-reject — but as a full-paper claim of "budget-matched, error-correlation-aware routing" it is
**unrealized** and must be rejected until the gated full study returns real, powered, multi-family,
held-out evidence.
