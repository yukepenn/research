# P3 DeltaResearch — Terminal Decision

**Terminal state: `ARXIV_ONLY`** (strong controlled, no-gold result; the real-evidence layer +
human adjudication required for a full TACL submission are not yet done).

**Target venue:** TACL (after the real-evidence layer). Now: a strong controlled-study technical
report suitable for arXiv, honestly labeled as a controlled, no-gold pilot.

**One-sentence supported claim:**
> On controlled evidence-world updates, a no-gold end-to-end pipeline that infers claim
> dependencies from report text and recomputes downstream values with a deterministic calculator
> substantially and significantly improves affected-claim recall over naive report revision —
> without using gold dependency graphs or gold post-update values.

**Strongest result (with CI):** pipeline − naive affected-claim recall, world-clustered bootstrap,
n=24 worlds, real Claude+Codex:
- named reports: Claude +0.75 [0.58, 0.92], Codex +0.46 [0.25, 0.67] (pipeline ACR 1.00 vs naive 0.25/0.54).
- vague reports (operation hidden): Claude +0.92 [0.79, 1.00], Codex +0.48 [0.29, 0.69].
- mechanism (stage diagnostic): inferred-vs-gold edge precision/recall 1.00; op accuracy 0.96–1.00.

**Strongest counterexample / honest limit:** the result is on synthetic controlled worlds whose claim
texts NAME the parent entities (operation may be hidden, but parents are not). A fully-implicit report
with unnamed parents is underdetermined and untested; no real versioned-evidence layer or human
adjudication yet; single draw per condition; numeric + retraction deltas only; 2 model families.

**Remaining blockers to `SUBMIT_READY` (TACL):**
1. Real versioned-evidence layer (public, licensed, timestamped) with 2-annotator adjudication.
2. Unnamed-parent / fully-implicit report stress (the harder inference regime).
3. More delta types (conflict, temporal expiry, unit change, definition change) + repeats with CIs.
4. Official TACL LaTeX + citation-entailment audit + independent reproduction.

**Exact human decisions required:**
- Approve the central claim wording and the TACL target.
- Approve (or not) an arXiv posting of the controlled pilot — external posting is a human gate.
- Author list, license, ethics/data statement, AI-assistance disclosure sign-off.

**arXiv posting recommended now?** The RESULT is strong enough to stand as an honest controlled
no-gold pilot, but recommend posting only AFTER: official LaTeX build, citation-entailment audit,
independent reproduction, and your sign-off. Not auto-posted.

**Confidence in this decision:** High that the controlled no-gold effect is real and reproducible
(4 CIs exclude 0, clean mechanism, deterministic core verified). Moderate that it transfers to real
versioned evidence (the gated next step).
