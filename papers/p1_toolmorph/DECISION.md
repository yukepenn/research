# P1 ToolMorph — Terminal Decision

**Terminal state: `ARXIV_ONLY`** — as a (1) property-verified state-transition-equivalence benchmark
plus (2) a clean NEGATIVE result. The proposed STNF method is **retired** (its premise is falsified by
the paper's own information-matched control). NOT a method paper.

**Target venue:** none for a method claim. The benchmark + negative result is a coherent, honest
technical report suitable for arXiv (or a short benchmarks/negative-results venue), clearly labeled.

**One-sentence supported claim:**
> On six property-verified, byte-identical state-transition-equivalent tool-interface transforms,
> frontier tool-using agents (Claude, Codex) show no degradation from representation changes that
> preserve information; the one apparent exception (opaque enum codes) is eliminated by restoring a
> legend, so it is information-hiding rather than representation — a label-free semantic normalizer
> therefore has nothing to recover.

**Strongest result (with CI):** information-matched control, n=20/cell, real Claude+Codex:
- enum-opaque: Claude −0.20 [−0.50, 0.00] (non-significant), Codex 0.00.
- enum-legend (same codes, information restored): Claude 0.00, Codex 0.00 — degradation eliminated.
- Equivalence benchmark (P1-C0, SUPPORTED): >15,000 randomized cases, zero state mismatch.

**Strongest counterexample / why the method died:** the pre-registered KILL gate ("content-matching
erases the effect AND label-free STNF cannot beat the alternative") is met: the legend (content
restoration) erases the effect, and opaque codes carry no recoverable information for a label-free
normalizer. There is no representation-only degradation for STNF to fix.

**Remaining blockers (would be needed to revive any method claim):**
1. Harder, non-ceiling tasks where representation might matter even with information preserved.
2. A transform family that genuinely changes representation while provably preserving information AND
   still degrades agents — none found here.
(These are speculative; current evidence is a clean negative.)

**Exact human decisions required:**
- Approve framing as a benchmark + negative result (not a method paper).
- Approve (or not) an arXiv posting of the benchmark + negative result — external posting is a human gate.
- Author list / license / disclosure sign-off.

**arXiv posting recommended now?** Reasonable as an honest benchmark + negative result AFTER citation
audit, LaTeX, and your sign-off. The negative result is genuinely useful (it adjudicates
representation-vs-information with a clean control). Not auto-posted.

**Confidence:** High that the STNF method is not supported by current evidence and that the benchmark
is sound. The negative result is bounded to these models/tasks (1.00 ceiling), stated honestly.
