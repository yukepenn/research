# P2 CrossCheck — hard-corpus difficulty probe (2026-06-25)

Tests whether a HARDER controlled corpus can pull frontier models off the one-shot ceiling so review
workflows have headroom. 6 subtle but FULLY-SPECIFIED defects (binary-search leftmost, interval-touch
merge, half-up rounding, order-preserving dedup, 1-indexed pagination, LRU get-counts-as-use), each
verified clean-pass/mutant-fail. Real Claude+Codex, bidirectional, budget-matched. Ledger:
`artifacts/p2_hard_ledger.jsonl` (36 episodes).

## Result — final-patch correctness by workflow
| workflow | correctness | n |
|---|---|---|
| NO_REVIEW (1 call, reference) | 1.00 | 12 |
| AUTHOR_MORE_COMPUTE (2 calls) | 1.00 | 12 |
| CROSS_FAMILY_REVIEW (2 calls) | 0.92 | 12 |

Per defect: boundary / requirement_misread / state_order = 1.00 under all workflows;
type_serialization = 1.00 (no_review, author+) but **0.50 under cross_family_review** — the
cross-family reviewer broke a correct fix (a review-induced regression).

## Reading
- **The hard corpus is STILL at ceiling for no_review (1.00).** Frontier models one-shot even subtle,
  fully-specified defects. The controlled-corpus approach cannot create discriminating difficulty for
  these models — so it cannot answer the research question (when is a second model worth its budget?).
- **Only signal: cross-review can HURT.** Cross-family review (0.92) scored BELOW no-review (1.00) —
  the reviewer introduced a regression on one type_serialization case. This is consistent with the
  contract's H4 (review-induced regression) but is anecdotal (n=12, a single regression) and not a
  basis for a claim.
- **Per the P2 stop condition** ("stop the paper if the new corpus cannot discriminate workflows"),
  this is a HOLD: the decisive budget-matched comparison is unanswerable until a corpus lands
  no_review around 0.4–0.6 — which requires real multi-file repository tasks (containerized real
  issues + hidden tests), not feasible at zero cost in this sprint.

## What survives
- Deterministic LLM-free corpora (easy + hard), the budget-matched protocol, the complementarity
  decomposition and ReviewRoute router (simulator-validated only), and the honest, now-replicated
  finding that frontier models one-shot small controlled defects — a concrete difficulty bar for the
  full study.

## P2 terminal = HOLD.
