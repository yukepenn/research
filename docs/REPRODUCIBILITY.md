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

## Environment
- Python 3.11; deps: numpy, scipy, pandas, pyyaml, jsonschema (+ pytest for dev).
- Docker is NOT required for the small profile. The full profile's sandboxing uses Docker where
  available; on hosts without Docker (e.g., this one) the runner degrades to disposable
  in-process / subprocess sandboxing — a documented isolation limitation, not a correctness one.
- Determinism: all randomness is seeded via `core.util.rng_for` / `numpy.random.default_rng(seed)`.
  Trajectories carry a volatile-free `structural_fingerprint()` so an independent reproducer can
  compare runs byte-for-byte.
