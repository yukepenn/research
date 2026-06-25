# CrossCheck: Budget-Matched, Error-Correlation-Aware Routing for Heterogeneous Code Review

> DRAFT — evidence-first order. Abstract/Intro/Results [PENDING] until ledger numbers land.

## Abstract
[PENDING]

## 1. Introduction
[PENDING — frame: a second model is not free reliability; the right comparison is equal extra
compute to the author]

## 2. Definitions
We separate latent defect, detected defect, false alarm, actionable localization, successful repair
(passes the hidden oracle), regression introduced, and spurious edit. Detection and repair are
scored separately so an accidental rewrite is not credited as review skill (manual 6.7).

## 3. Controlled defect corpus
Self-contained toy modules with injected single defects across ≥6 defect types
(`mutations/injectors.py`), each paired with a **deterministic hidden test** that passes on the
clean module and fails on the mutated one.

**Verified result (SUPPORTED, deterministic, P2-C0).** For every case the hidden test passes on the
clean variant and fails on the mutated variant; cases materialize identically in-process and in a
temp directory. This gives an objective, LLM-free correctness endpoint.

## 4. The decisive comparison: budget matching
The core methodological point cc02 lacks is a **budget-matched author-extra-compute arm**. We
compare at matched budget (2 model calls):
- `NO_REVIEW` (author once),
- `AUTHOR_MORE_COMPUTE` (author fixes, then self-improves — 2 author calls),
- `CROSS_FAMILY_REVIEW` (author fixes, a *different* model repairs — 2 calls),
run **bidirectionally** (Claude↔Codex). Final correctness is the deterministic hidden test.
Complementarity (`complementarity.py`) decomposes residual gain beyond reviewer standalone strength;
the pre-call router (`router.py`, nested CV with outer fold = repository, no leakage) selects the
review action. H2: cross-family review should NOT dominate equal author compute.

## 5. Experimental setup
Plan-then-repair harness: present the buggy module + spec, the author returns a corrected module, we
execute the hidden test. **Scope:** pilot-scale, controlled corpus, two model families; the natural
near-miss corpus, ≥3 families, 8 defect types, ≥10 repositories, and held-out-repo router validation
are the gated full study (FSE 2027 target, full paper deadline 2026-10-02 AoE).

## 6. Results
[PENDING — from `core.plotting.pilot_tables.p2_table`: final-correctness by workflow; the
author_more_compute vs cross_family_review contrast at matched budget; defect-type heterogeneity]

## 7. Related work
- **cc02** (Cross-Model LLM Code Review, KDD'26, Xiang et al.) runs a bidirectional Claude↔Codex 2×2
  including self-review and finds cross-model review is direction-dependent and not inherently better
  than the stronger model solo — we credit it and add the budget-matched author-extra-compute
  counterfactual, defect-type complementarity, and a pre-call held-out router it lacks.
- **Refute-or-Promote** (arXiv:2604.19049): adversarial cross-model critique for high-precision
  detection — detection, not budget-matched final correctness.
See `novelty/novelty_attack.md`.

## 8. Limitations / Ethics
Toy modules (real-repo corpus pending); pilot-scale; in-process execution of model-produced code is
a sandboxing limitation (full study uses containerized repos). Defect study targets general
correctness, not exploit development.
