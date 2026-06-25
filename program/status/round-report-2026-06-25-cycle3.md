# Research Status — 2026-06-25 (cycle 3: real pilots → drafts → red-team → honest correction)

Scope: **P1, P2, P3** (P4 KILLED, evidence-driven). All model evidence is real (Claude + Codex/gpt-5.5
via subscription CLIs), **zero metered API cost**, in the immutable ledger. GitHub: pushed to
https://github.com/yukepenn/research after every step.

## What each paper HONESTLY is now (after a 3-reviewer adversarial red-team + correction pass)

### P3 DeltaResearch — strongest (red-team: major_revision 4/10; confidence 0.55)
- **Real, genuine finding:** two real agents, given an evidence-WORLD delta with the derivation rules
  stated in-prompt, recover only **~1/3 of obligated downstream updates** (Claude ACR 0.39, Codex 0.34;
  UCP ~1.0), and **handing them the typed affected set does not help** (ACR 0.33) → the bottleneck is
  edit/re-derivation, not identification. Direction-consistent across two families. (P3-H1 SUPPORTED, pilot-scale.)
- **Corrected:** the deterministic "method dominates 1.0/0.0/0.13" was TAUTOLOGICAL (analyzer is gold-fed,
  reads gold values, re-derives nothing) → demoted to a labeled consistency check. H_DIVERGE is an
  edge-partition illustration, not a passed gate. Off-topic citations removed.
- Honest tier: **well-instrumented empirical pilot + released harness** (workshop/findings), NOT yet the
  method paper the title advertised. De-oracle the method + scale + real-evidence layer = path to full.

### P1 ToolMorph — benchmark + signal + plan (red-team: reject 3/10; confidence 0.40)
- **Delivered/SUPPORTED:** a property-verified state-transition-equivalence benchmark (6 transform
  families × 3 envs; **>15k cases, 0 mismatch**, independently reproduced). This is the one fully
  delivered contribution.
- **Pilot signal (not significant):** enum-encoding shows a small paired drop — Claude −0.20 [−0.50,0],
  Codex −0.10 [−0.30,0] — **both CIs include 0**; structural/lexical show no drop (at a 1.0 ceiling).
  Corrected from the earlier mis-stated numbers (Codex was wrongly 0.89; timeout wrongly called "excluded").
- **PRIMARY claim (H5, the STNF remedy) is UNRUN** — a pre-registered plan. H4 ranking NOT supported.
- Honest tier: **benchmark-note + pre-registration**. Run H5 + escape the ceiling = path to full.

### P2 CrossCheck — honest null + methodology (red-team: reject 3/10; confidence 0.30)
- **Delivered/SUPPORTED:** a deterministic LLM-free defect corpus (hidden tests pass-clean/fail-mutant).
- **Honest null:** all workflows tie at 0.80 — corpus at ceiling (8/10 one-shot; 2 cases were
  benchmark bugs, found+fixed). Cannot distinguish workflows.
- **Corrected:** the "budget-matched author-extra-compute" arm is currently a self-improve pass
  (≈ cc02's self-review); the genuine resample-k arm is UNIMPLEMENTED. Complementarity + ReviewRoute are
  simulator self-tests, not empirical.
- Honest tier: **honest negative + methodology + corpus-difficulty diagnosis**. A mid-difficulty
  fairly-specified corpus (no-review ~0.4–0.6) = path to a real workflow contrast.

## Integrity actions this cycle (the red-team caught real errors; all fixed)
- P1 headline numbers reconciled to the ledger (Codex 0.90/−0.10; 80 episodes, none excluded; max_steps
  timeout counted as a genuine agent failure); bootstrap CIs added (both enum CIs include 0); "degrades"
  → non-significant directional signal.
- P3 tautological frontier demoted; P2 budget-arm overclaim corrected; off-topic P3 citations removed.
- All three drafts have a "## Honest status and path to a full paper" section with the required experiments.
- Confounds caught & excluded with memos: P1 single-shot id confound; 2 P2 benchmark-bug specs (fixed).

## Honest ceiling (unchanged)
These are **pilot/workshop-grade**: real but small (2 model families, ~10 tasks / 18 worlds / 10 defects),
no held-out, product-CLI models. NOT full-study submittable to FSE/ARR/MLSys without the gated scale-up
(≥3 families, hundreds of items, P3 real-evidence layer + human annotation, P1's STNF run) and human sign-off.
The strongest genuinely-publishable nugget today is **P3's "agents miss ~2/3 of evidence-delta updates,
and telling them which claims changed doesn't fix it."**

## Tests/infra: 97 passing, `make validate` OK. All artifacts on GitHub.
