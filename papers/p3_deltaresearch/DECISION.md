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

## Decisive re-run (DONE — the method advantage did NOT survive)
Corrected, de-leaked, n=24, Correct Update Recall, citation-equipped naive:
- naive CUR 0.92 (Claude) / 0.95 (Codex); pipeline 1.00 / 1.00.
- pipeline − naive: Claude +0.076 [0.000, 0.174], Codex +0.052 [0.000, 0.146] — **both CIs include 0.**
- The earlier +0.75/+0.46 (CIs exclude 0) was an ARTIFACT of leakage + ID-recall + citation-deprived naive.
- Structure inference IS real (ordered full-expression exact = 1.00), but does not yield a significant
  end-to-end advantage at this difficulty (naive already near-ceiling with citations).

**Conclusion: P3 remains `HOLD`.** The no-gold method claim is NOT supported by the corrected evidence.
The one robust, honest finding is the structure-inference capability (P3-H4c, SUPPORTED). See
`evidence/claimpatch_corrected_2026-06-26.md`. The path to a real method result requires HARDER tasks
that take naive off the 0.92-0.95 ceiling (unnamed parents, deeper cascades, ambiguous ops, real
end-to-end prose rewrite + verification) plus the real-evidence layer + human adjudication.

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
