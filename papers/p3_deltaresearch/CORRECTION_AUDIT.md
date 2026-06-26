# P3 Adversarial Implementation Audit — ACCEPTED (2026-06-26)

An external code-level audit found real flaws in the "no-gold" claim. Verified against the live code;
**all accepted.** Terminal state reclassified **ARXIV_ONLY → HOLD-CORRECT-MAJOR**. No LaTeX / arXiv /
submission packaging. P3 is the only active paper; P1 → internal artifact, P2 → HOLD, P4 → KILL.

## Confirmed flaws (with code locations)
1. **Hidden-metadata leakage (most serious).** `claimpatch.recompute_patch` reads `claim.kind`
   (base/derived/fact) and `claim.source` (claim→source link) from the `world` object — NOT inferred.
   So the method got the claim roles and the base→source mapping for free; the LLM-output
   `directly_changed` was never used. → "no-gold" was OVERSTATED.
2. **Not end-to-end.** Output is `Patch(edited_ids, new_values)` over pre-segmented claim ids; no claim
   extraction from prose, no text rewrite, no citation update, no verification. "end-to-end /
   constrained patch + verification" overclaimed.
3. **Metric is affected-ID recall, not report correctness.** ACR counts marked-edited affected ids;
   `calc_correctness` returns vacuous 1.0 when no numeric (e.g. retraction → post_value None excluded),
   so a retraction chain can score ACR=1 without correct new content. The headline 1.00 is ID-recall.
4. **Gold not independent.** `claimpatch` imports `_compute` from `worlds_v2`; gold post-values use the
   same `_compute`. "Independent separate code path" is inaccurate (shared arithmetic implementation).
5. **Topology cosmetic.** `topology = rng.choice([...])` is a label; the DAG sampler does not branch on
   it. "chain/tree/diamond/fan-in/fan-out/mixed" is not an implemented stratification.
6. **Statistical clustering.** Same seed generates numeric_revision AND source_retraction worlds sharing
   the graph skeleton; bootstrap clusters by `world_id` (distinct per delta), not seed/graph → nested
   observations treated as independent → CIs optimistic.
7. **Vague shortcut.** Vague still names parents + gives old values + a 7-op candidate set → op-solving,
   not implicit-dependency discovery from prose.
8. **"bottleneck = re-derivation" over-inferred** from a single hint-null; needs a factorial ablation.
9. **Stage diagnostic uses unordered parent sets** (A−B == B−A); "edge P/R=1.0" overstates.
10. **Baselines/related work thin;** "evidence-world update previously unexplored" is wrong (FRUIT 2022;
    EditPropBench). Experiments are single CLI completions, not Deep Research Agent loops.

## Correction plan (this sprint, decisive items first)
- [1] Method receives ONLY a sanitized public input (report claims with id/text/value/**citation**,
  sources, observable delta) — never the world. Roles + claim→source inferred from VISIBLE citations
  (legitimate report content). Add a runtime leakage test.
- [4] Method gets its OWN calculator (not imported from the generator); cross-validate by property test.
- [3] Replace ACR-only with **Correct Update Recall** (identified AND new value/status correct;
  retraction handled; no vacuous 1.0).
- [6] One delta per seed → `world_id` = independent graph; recompute CIs; add repeats.
- [9] Ordered-parent / full-expression match in the stage diagnostic.
- Then re-run named + (harder) vague. **If the pipeline still beats naive after de-leaking, the result
  survives (corrected). If it collapses, P3 drops further — reported honestly.**
- Deferred (larger): true topology constructors, real end-to-end prose rewrite + verification, factorial
  ablation, scaffolded baselines, real versioned-evidence layer + human adjudication, FRUIT/EditPropBench
  head-to-head. These gate any SUBMIT_READY.

Draft claims are FROZEN (no abstract rewrite) until the de-leaked re-run lands.
