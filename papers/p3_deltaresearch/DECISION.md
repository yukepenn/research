# P3 DeltaResearch — Terminal Decision (revised after adversarial implementation audit)

**Terminal state: `HOLD-CORRECT-MAJOR`** (was ARXIV_ONLY — downgraded). A strong synthetic proof of
concept whose "no-gold" claim was OVERSTATED due to hidden-metadata leakage and whose metric/stats/
generator have correctable defects. **Do NOT post to arXiv or submit to TACL/TMLR** until the
correction gates pass and the de-leaked result is re-confirmed.

See `CORRECTION_AUDIT.md` for the full accepted findings. The audit was correct on all code-level points
(verified against the live code): the method read `claim.kind`/`claim.source` from the World; ACR is
ID-recall not report correctness; the gold shared the method's calculator; topology labels were
cosmetic; clustering double-counted shared graphs.

## Corrections applied this sprint
- Method now takes ONLY the sanitized public view (`r0_view`: claims id/text/value/CITATION, sources,
  observable delta) — never the World. Roles + claim→source inferred from VISIBLE citations.
  Enforced by a leakage test (`test_p3_v2_audit`). [`claimpatch_v2.py`]
- Independent calculator (`_calc`, not the generator's `_compute`), cross-validated on 2000 inputs.
- Primary metric = **Correct Update Recall** (identified AND correct new value/status; no vacuous 1.0).
- One delta per seed → `world_id` is an independent graph (valid cluster); CIs recomputed.
- 105 deterministic tests green.

## Decisive re-run (in progress)
The corrected, de-leaked pipeline is being re-run vs naive on real Claude+Codex. **If it still beats
naive on Correct Update Recall, the result survives (corrected) and P3 can re-enter ARXIV_ONLY
consideration. If it collapses, P3 stays HOLD and the claim is reported as not surviving de-leaking.**

## Still required before any SUBMIT_READY (deferred, larger)
True topology constructors; real end-to-end prose rewrite + citation update + verification; factorial
gold-component ablation (source-link / graph / op / value); scaffolded baselines (checklist, scratchpad-
calculator, formula-extraction-no-graph, deterministic op-solver, full regen, graph+LLM-arithmetic);
ordered-parent / full-expression stage diagnostic; harder vague (unnamed parents, ambiguous ops,
decoys, abstain); real versioned-evidence layer + 2-annotator adjudication; FRUIT/EditPropBench
head-to-head; reframe "Deep Research Agents" → "LLM-based report revision"; pinned model builds +
repeats + CI on HEAD + independent reproduction.

**arXiv now? NO.** **Confidence:** the corrected core is sound; whether the no-gold EFFECT survives
de-leaking is exactly what the in-progress re-run tests. Draft claims FROZEN until it lands.
