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

## Stress test — "vague" reports (operation hidden; model must INFER the op)
Claim text names the parent entities but NOT the operation (e.g. "Metric d2, derived from Region A
revenue and Region B revenue, is 260").
| arm | model | ACR | UCP | harmful | calc |
|---|---|---|---|---|---|
| naive LLM | Claude | 0.08 | 1.00 | 0.00 | 0.58 |
| naive LLM | Codex | 0.52 | 0.99 | 0.01 | 0.97 |
| **no-gold pipeline** | Claude | **1.00** | 0.97 | 0.03 | 1.00 |
| **no-gold pipeline** | Codex | **1.00** | 0.96 | 0.04 | 0.97 |

**Pipeline − naive ACR: Claude +0.92 [0.79, 1.00]; Codex +0.48 [0.29, 0.69] — CIs exclude 0.**
Stage diagnostic: edge precision/recall still **1.00**; **op accuracy 0.98 (Claude) / 0.96 (Codex)**
— the LLM infers the HIDDEN operation from the parents + the stated value. The small UCP dip
(0.96–0.97) and harmful-edit (0.03–0.04) trace to the ~2–4% op-inference errors. Naive agents get
WORSE under vague phrasing (Claude 0.08).

## Honest reading (final)
- The no-gold pipeline beats naive massively and significantly under BOTH named and vague phrasing
  (4 CIs, all exclude 0), on diverse topologies, with a clean mechanistic explanation (structure
  inference + deterministic recompute). This is a genuine method result with NO gold.
- Remaining boundaries (honest): parents are still NAMED in the text (a fully-implicit report where
  parents are unnamed is underdetermined and untested); controlled synthetic only (no real
  versioned-evidence layer yet); single draw per condition, 24 worlds, 2 model families;
  numeric/retraction deltas only; no human adjudication.
- These bound the contribution to a STRONG controlled, no-gold pilot — ARXIV_ONLY now, and a credible
  TACL-track foundation once the real-evidence layer, human adjudication, more delta types, and
  repeats are added.

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
