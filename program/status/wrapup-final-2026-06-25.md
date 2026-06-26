# Wrap-up Sprint — Final Terminal Outcome (2026-06-25)

Three papers, each driven to a terminal decision per the master directive. Zero metered API cost
(Claude + Codex/gpt-5.5 subscriptions). No external submission/arXiv/publish without human sign-off
(see program/HUMAN_SIGNOFF_TEMPLATE.md). All evidence in immutable ledgers; all numbers ledger-derived.

## Terminal decisions

| Paper | Terminal state | One-line outcome |
|---|---|---|
| **P3 DeltaResearch** | **ARXIV_ONLY** | Genuine NO-GOLD method result: ClaimPatch (infer structure from text + deterministic recompute) beats naive revision significantly (4 CIs exclude 0); pipeline ACR 1.00 vs naive 0.08–0.54. The program's real win. |
| **P1 ToolMorph** | **ARXIV_ONLY** | Verified equivalence benchmark (>15k cases, 0 mismatch) + a clean NEGATIVE result: representation-equivalent transforms don't degrade frontier agents; the one apparent effect is information-hiding (enum-legend control erases it). STNF method RETIRED by its own pre-registered kill-gate. |
| **P2 CrossCheck** | **HOLD** | Honest null: even a hard fully-specified corpus is one-shot-solved by frontier models (no_review=1.00), so workflows can't be discriminated. Needs a real multi-file repository corpus (gated). Methodology preserved. |

This is the evidence-driven outcome the directive anticipated: **one real result, one honest negative
+ benchmark, one hold — none inflated.**

## P3 — the result (real, no-gold)
- 24 diverse-topology controlled worlds; method sees only R0 + sources + observable delta (verified
  no gold leakage). LLM infers dependency structure from claim text; deterministic calculator recomputes.
- named reports: naive ACR Claude 0.25 / Codex 0.54 -> pipeline 1.00/1.00; pipeline-naive +0.75[0.58,0.92] / +0.46[0.25,0.67].
- vague reports (operation hidden): naive 0.08 / 0.52 -> pipeline 1.00/1.00; +0.92[0.79,1.0] / +0.48[0.29,0.69].
- mechanism: inferred-vs-gold edge P/R = 1.00; op accuracy 0.96–1.00. Bottleneck is re-derivation, not identification.
- Path to full TACL: real versioned-evidence layer + human adjudication + more delta types + repeats + unnamed-parent stress.

## P1 — the negative result (clean adjudication)
- Info-matched control: enum-opaque Claude -0.20 (non-sig) -> enum-legend (same codes, info restored) 0.00.
- Conclusion: representation is not the cause; information is (supports Schema First). STNF has nothing
  label-free to recover -> retired per the pre-registered gate. Benchmark + negative result survive.

## P2 — HOLD
- Easy and hard controlled corpora both one-shot-solved (no_review 0.80 then 1.00). Only signal:
  cross-family review can slightly hurt (0.92 < 1.00, one regression; anecdotal). Stop condition met.

## Integrity record (this sprint)
- Deterministic gates + the adversarial red-team caught REAL problems and they were fixed, not hidden:
  P1 number reconciliation; P3's gold-fed "method" (tautology) -> replaced with a genuine no-gold
  method; P2 budget-arm overclaim; 2 P2 benchmark-bug specs; a single-shot id confound; a retraction
  propagation bug (caught by a deterministic test before any model ran).
- Citations: only the 9 Director-verified sources cited as fact across drafts; others flagged unverified.

## Per-paper packages present
DECISION.md, evidence/*, claim_registry.csv, paper/draft.md, novelty/*, analysis_plan.yaml,
figures (P3), exclusions where applicable. Remaining for any SUBMIT_READY: official venue LaTeX
(no local TeX toolchain — sources gated), citation-entailment audit, independent reproduction,
and the human sign-off sheet. No external action taken.

## Honest bottom line
The strongest genuinely-publishable result is **P3's no-gold ClaimPatch** (an ARXIV_ONLY-strong
controlled result, TACL-track). P1 is an honest benchmark + negative result (ARXIV_ONLY). P2 is HOLD.
None overclaimed. Everything on GitHub (private). External posting awaits the human PI.
