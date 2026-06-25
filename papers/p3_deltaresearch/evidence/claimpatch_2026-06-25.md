# P3 DeltaResearch — no-gold ClaimPatch evidence (2026-06-25)

Addresses the red-team's #1 kill-condition (the prior "method" read gold). The method here
(`claimpatch.py`) receives ONLY R0 (claim texts + values + citations), the sources, and the
observable evidence delta — never gold A/U, gold dependency edges, or gold post-update values
(verified: `r0_view()` exposes none; test_p3_claimpatch). It infers the dependency structure from
claim text, then a DETERMINISTIC calculator recomputes downstream values.

Real models via subscription CLIs (no API cost): `claude`, `codex` (gpt-5.5). Ledger:
`artifacts/p3v2_ledger.jsonl` (named) and `artifacts/p3v2_vague_ledger.jsonl` (vague). 24 worlds
each, diverse random DAG topologies (chain/tree/diamond/fan-in/fan-out/mixed), numeric-revision and
source-retraction deltas. Gold by independent recompute.

## Main result — "named" reports (derivation type stated in claim text)
| arm | model | ACR | UCP | harmful-edit | calc-correct |
|---|---|---|---|---|---|
| naive LLM | Claude | 0.25 | 1.00 | 0.00 | 0.74 |
| naive LLM | Codex | 0.54 | 1.00 | 0.00 | 0.99 |
| **no-gold pipeline** | Claude | **1.00** | 1.00 | 0.00 | 1.00 |
| **no-gold pipeline** | Codex | **1.00** | 1.00 | 0.00 | 1.00 |
| oracle (graph+recompute / full) | — | 1.00 | 1.00 | 0.00 | 1.00 |

**Pipeline − naive ACR (world-clustered bootstrap, n=24): Claude +0.75 [0.58, 0.92]; Codex
+0.46 [0.25, 0.67] — both CIs EXCLUDE 0.**

### Stage-wise diagnostic (why it works; RQ2)
Inferred-vs-gold structure over 96 derived claims/model: **edge precision 1.00, edge recall 1.00,
op accuracy 1.00, derived-exact 1.00** for both Claude and Codex. So when the report states its
derivations semantically, the LLM recovers the dependency graph perfectly; the naive prompt simply
fails to TRIGGER systematic propagation+recompute. The bottleneck is the editing/re-derivation step,
not identification — and a structured pipeline that forces it closes the gap, with no gold.

## Stress test — "vague" reports (operation hidden; model must infer the op)
[PENDING — `artifacts/p3v2_vague_ledger.jsonl`; maps the boundary of structure inference]

## Honest reading
- This is a genuine NO-GOLD result: the pipeline dramatically and significantly beats the naive
  agent (CIs exclude 0) on diverse topologies, with a clean mechanistic explanation.
- Scope/limits: claim texts use semantic phrasing that names the operation type and parent entities
  (realistic for reports, but easier than fully-implicit prose). The vague stress test quantifies how
  much structure-inference (and thus ACR) degrades when the operation is hidden. Pilot-scale
  (24 worlds, 2 model families, single draw); controlled synthetic only (no real-evidence layer yet);
  numeric/retraction deltas only. These bound the claim to a controlled, no-gold pilot — strong enough
  for ARXIV_ONLY and a TACL-track foundation, not yet a full TACL submission (real layer + human
  adjudication + more delta types + repeats remain).
