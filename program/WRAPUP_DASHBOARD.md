# Wrap-up Dashboard — post-pilot sprint (started 2026-06-25)

Terminal goal per paper: exactly one of SUBMIT_READY / ARXIV_ONLY / HOLD / KILL.
Constraints: no metered API (Claude+Codex subscriptions only); no external submission / arXiv /
publish / license / authorship sign-off without the human PI. A compiled PDF ≠ SUBMIT_READY.

| Paper | State | Last verified | Primary estimate (CI) | Next executable task | Blocker |
|---|---|---|---|---|---|
| P1 ToolMorph | PILOT → go/no-go | (this sprint) | enum drop Claude −0.20[−0.50,0], Codex −0.10[−0.30,0] (CIs incl 0) | harder non-ceiling tasks + info-matched enum control + label-free LLM-STNF held-out recovery | none (compute = subscription) |
| P2 CrossCheck | PILOT → likely HOLD | (this sprint) | all workflows tie 0.80 (ceiling) | rebuild a fair mid-difficulty real-ish corpus (no-review ~0.4–0.6); if it can't discriminate → HOLD | discriminating corpus |
| P3 DeltaResearch | PILOT → build no-gold method | (this sprint) | agents miss ~2/3 updates (ACR 0.34–0.39); deterministic "method" was gold-fed (demoted) | build no-gold end-to-end ClaimPatch + diverse topologies; run vs naive/full-regen/flat; stage-wise error decomp | none (compute = subscription) |

## Freeze
- `pilot-freeze-2026-06-25` tags the pilot state before this sprint.
- Pilot ledgers preserved; new confirmatory runs appended, study_phase-tagged.

## Honest expected outcome (per my red-team + the directive's stop conditions)
- P3: best shot at ARXIV_ONLY, possibly SUBMIT_READY-track if the no-gold method beats naive on
  controlled holdout + a small real layer.
- P1: clean go/no-go — STNF recovery on held-out upgrades; matched-control killing the effect → KILL/benchmark.
- P2: most likely HOLD unless a fair corpus discriminates workflows.

Updated each block. No external action without human sign-off.
