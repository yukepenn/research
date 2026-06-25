# Risk Register — 2026-06-25

| ID | Risk | Likelihood | Impact | Mitigation / trigger |
|---|---|---|---|---|
| R1 | P1 STNF fails to transfer to unseen transforms (the only surviving core) | Med | High | Pre-registered NORM-transfer split is the PRIMARY endpoint; KILL gate if it + content-control both fail |
| R2 | P2 budget-matched arm erases all cross-review gain | Med | High | Treat as a publishable confirmatory negative result (code port of cc04/cc05); pre-register the reframe |
| R3 | P3 evidence-world delta behaves identically to an author edit (framing cosmetic) | Med | High | H_DIVERGE is a gating experiment; do not proceed past pilot if it fails |
| R4 | P4 H2 fails: selection ties random (verified counter-evidence 2409.03563, 2510.08730) | Med-High | High | H2 is a HARD KILL GATE in the pilot; auto-convert to negative-result note |
| R5 | Cannot collect ≥25 independent harness edits → P4 flagship not viable | Med | Med | Mix real + controlled + optimizer-generated; fall back to TMLR or descriptive corpus |
| R6 | No paid budget configured → no pilots can run | High (now) | Blocking | Human gate; all Tier-0 deterministic work proceeds without it |
| R7 | Docker absent → weaker sandbox isolation / reproducibility | High (now) | Low-Med | Local disposable subprocess sandbox; ship container recipe in artifact |
| R8 | New collision paper appears (fast-moving area) | Med | Med | Re-run nearest-neighbor sweep at every major gate and before submission |
| R9 | Model snapshots drift, invalidating results | Med | Med | Record exact model id/date in ledger; re-run robustness on version update |
| R10 | LLM judge bias contaminates secondary metrics | Med | Low | Primary endpoints are deterministic oracles; judges secondary + human-audited |
