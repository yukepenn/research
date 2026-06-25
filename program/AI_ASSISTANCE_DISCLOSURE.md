# AI-Assistance Disclosure (program-wide; per-paper copies reference this)

This research program was executed with substantial generative-AI assistance. This disclosure is
factual and must be kept accurate; it is referenced by each paper's `AI_ASSISTANCE_DISCLOSURE.md`.

## Tools used
- **Anthropic Claude Code** (Claude Opus 4.8) — orchestration / Research Director, code
  implementation, experiment harness, statistics, drafting, internal red-team.
- **OpenAI Codex CLI** (gpt-5.5) — used BOTH as an implementation assistant AND as one of the two
  evaluated model families in the experiments (author/reviewer/agent role).
- Subscription-billed only; **no metered API spend** was incurred for experiments.

## What the AI did
- Literature discovery and an adversarial novelty audit (every cited primary source was opened;
  the Research Director personally re-verified the load-bearing collision papers).
- Implemented the deterministic infrastructure, environments, oracles, the no-gold ClaimPatch
  pipeline, statistics, and the run ledger.
- Orchestrated the pilots (Claude + Codex via CLIs), recorded every episode in an immutable ledger,
  generated all tables/figures from that ledger.
- Ran a 3-reviewer adversarial red-team that found real integrity errors, which were then corrected
  (not concealed): P1 numbers reconciled to the ledger; P3's gold-fed "method" demoted to a labeled
  upper bound and replaced with a genuine no-gold method; P2 overclaims corrected.
- Drafted prose from generated results (Results-first, Abstract-last).

## What the AI did NOT do / what remains the human PI's responsibility
- The AI is **not an author** and is not treated as ground truth.
- The human PI must: own the research questions and final claims; verify the cited sources and key
  raw outputs; decide inclusion/exclusion; choose author list, license, ethics statements; perform
  the human annotation/adjudication required for the real-evidence layer (NOT done by the AI); and
  make the final decision to post or submit.
- No human annotation has been performed yet; any future human labels must NOT be described as
  AI-generated, and AI-suggested labels must be marked assisted and approved by a human.

## Suggested venue disclosure text (use only if every sentence is true at submission time)
> Generative AI tools (Anthropic Claude Code and OpenAI Codex) were used as assistive tools for
> literature discovery, software implementation, experiment orchestration, statistical scripting,
> figure generation, internal review, and prose drafting; OpenAI Codex (gpt-5.5) was additionally
> one of the two evaluated model families. The human author(s) selected and approved the research
> questions, experimental designs, inclusion/exclusion rules, interpretations, and final scientific
> claims; reviewed the key raw outputs and generated analyses; verified the cited sources; and assume
> full responsibility for the work. No model is listed as an author. All reported tables and figures
> were generated from auditable experiment ledgers and deterministic analysis scripts.

Adjust to each venue's current policy (TMLR first-page footnote; ACM/FSE disclosure; ARR checklist).
