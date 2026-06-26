# P3 — CORRECTED no-gold ClaimPatch evidence (2026-06-26, post-audit)

Supersedes `claimpatch_2026-06-25.md` (which was INFLATED by hidden-metadata leakage + a lax
ID-recall metric + a citation-deprived naive baseline). This is the honest, de-leaked result.

Method (`claimpatch_v2.py`) receives ONLY the sanitized public view (claims id/text/value/CITATION,
sources, observable delta) — never the World, never claim.kind/claim.source/gold. Independent
calculator. Primary metric = **Correct Update Recall (CUR)**. One delta per seed (independent graphs).
24 named worlds, real Claude+Codex. Ledger: `artifacts/p3v2_audited_ledger.jsonl`.

## Result (Correct Update Recall)
| arm | Claude | Codex |
|---|---|---|
| naive (citation-equipped) | 0.92 | 0.95 |
| no-gold pipeline | 1.00 (harmful-edit 0.017) | 1.00 (harmful-edit 0.017) |

**pipeline − naive CUR (world-clustered bootstrap, n=24): Claude +0.076 [0.000, 0.174];
Codex +0.052 [0.000, 0.146] — BOTH CIs INCLUDE 0 (not significant).**

Stage diagnostic (ordered-parent + full-expression, n=92 derived/model): unordered P/R 1.00,
ordered-parent-exact 1.00, op-accuracy 1.00, **full-expression-exact 1.00** — the LLM infers the
dependency structure perfectly even with ordered/full-expression scoring.

## Honest reading (the audit was right; the dramatic effect was an artifact)
- The earlier headline (pipeline-naive +0.75/+0.46, CIs exclude 0) does NOT hold once corrected. It
  was inflated by: (1) the method reading hidden claim.kind/claim.source; (2) ACR (ID-recall) instead
  of Correct Update Recall; (3) a naive baseline that, unlike the pipeline, was not shown the report's
  citations. With all three fixed, **naive is already near-ceiling (0.92-0.95) and the pipeline's
  marginal gain is small and statistically non-significant.**
- What IS real: the LLM infers the claim dependency structure perfectly from text (full-expression
  exact 1.0), and the deterministic recompute then yields perfect CUR. But this capability does not
  produce a significant end-to-end advantage over a fair naive baseline at this controlled difficulty.
- The pipeline also introduces a small harmful-edit rate (0.017) that naive (0.005) does not.

## Conclusion: P3 = HOLD (method claim NOT supported by corrected evidence)
The no-gold pipeline does not significantly outperform a citation-equipped naive agent on these
controlled worlds. To establish a method advantage, the task must be HARDER for naive (off the
0.92-0.95 ceiling): unnamed/implicit parents, deeper multi-hop cascades, ambiguous operations,
decoys, conflicts/retraction chains with required new text, and a real end-to-end prose-rewrite +
verification pipeline (not ID/value patching). Plus the real versioned-evidence layer + human
adjudication. Until then, the honest claim is narrow: "an LLM can infer explicit-derivation structure
from report text with high accuracy; a structured recompute then achieves perfect controlled-world
update recall, but does not significantly beat a citation-equipped naive baseline at this difficulty."
