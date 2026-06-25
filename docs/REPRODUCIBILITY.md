# Reproducibility profiles (manual section 23)

Two profiles, as required by the manual:

## Small (default, no API keys, minutes)
Deterministic Tier-0: builds and verifies everything that does not need a paid model.
```
make reproduce        # validate -> pytest -> rebuild tables from ledger -> status
# or, without make (Windows):
python -m core.audit.validate
python -m pytest tests -q
python -m core.plotting.build_all
python -m core.dashboard.status
```
What it checks: run-ledger schema + append-only integrity; research contracts initialized;
secret scan; all unit/integration tests (kernel, infra, and the four papers' deterministic
components, including ToolMorph's >=15k-case state-equivalence proof); tables rebuilt strictly
from the ledger.

## Full (requires the human budget/credential gate)
The paid pilots and full studies. Blocked until a human:
1. fills `program/budget.yaml` with non-null hard ceilings,
2. copies `program/pricing.yaml.template` -> `program/pricing.yaml` with real, dated prices,
3. exports provider credentials in the environment (never committed).
Until then `core.adapters.registry.get_adapter` raises `BudgetGateError` for any paid provider,
and `core.budget.estimator.estimate_experiment` flags `requires_human_gate`.

## Pilot reproduction (subscription CLIs, no metered API cost)
The 2026-06-25 pilots used the locally-installed `claude` and `codex` CLIs (subscription-billed,
not API dollars). The plan-then-execute / -patch / -repair harness controls execution and scores
with deterministic oracles, so the same harness drives both models. Every episode is in
`artifacts/run_ledger.jsonl`; tables rebuild from it via `core.plotting.pilot_tables`.

```
# P1 ToolMorph — interactive metamorphic pilot (paired original vs transforms)
python -m papers.p1_toolmorph.pilot --models claude,codex \
  --transforms structural_nesting,enum_encoding,lexical_aliasing --interactive

# P3 DeltaResearch — report patch under evidence delta (deterministic gold)
python -m papers.p3_deltaresearch.pilot --models claude,codex --seeds 3

# P2 CrossCheck — budget-matched author-extra-compute vs cross-family review
python -m papers.p2_crosscheck.pilot --pairs claude:codex,codex:claude

# rebuild all pilot result tables from the immutable ledger
python -c "import json,core.plotting.pilot_tables as p; print(json.dumps(p.all_tables(),indent=2))"
```
Results are model/version dependent (record `model_id`/date in the ledger). The first P1 run is
archived as a documented confound (`papers/p1_toolmorph/exclusions.csv`); two P2 cases were
benchmark bugs fixed mid-pilot (`papers/p2_crosscheck/exclusions.csv`). Numbers are pilot-scale
(2 model families; ~10 tasks / 18 worlds / 10 defects); the full studies are gated.

## Environment
- Python 3.11; deps: numpy, scipy, pandas, pyyaml, jsonschema (+ pytest for dev).
- Docker is NOT required for the small profile. The full profile's sandboxing uses Docker where
  available; on hosts without Docker (e.g., this one) the runner degrades to disposable
  in-process / subprocess sandboxing — a documented isolation limitation, not a correctness one.
- Determinism: all randomness is seeded via `core.util.rng_for` / `numpy.random.default_rng(seed)`.
  Trajectories carry a volatile-free `structural_fingerprint()` so an independent reproducer can
  compare runs byte-for-byte.
