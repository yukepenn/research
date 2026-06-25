"""Build per-paper pilot result tables strictly from the run ledger.

Every number a draft reports must come from here (manual 3.1, 21.1). Reads the
immutable ledger entries' `result` blobs and aggregates:
  P1: paired success by (model x transform) -> degradation vs original
  P2: final-patch correctness by workflow (and by author x workflow)
  P3: ACR / UCP by (model x method) + deterministic baselines
"""
from __future__ import annotations

import os
from collections import defaultdict

from core.experiment_registry.ledger import RunLedger

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_LEDGER = os.path.join(_REPO_ROOT, "artifacts", "run_ledger.jsonl")


def _entries(paper_id, ledger_path):
    return [e for e in RunLedger(ledger_path).read_all() if e.get("paper_id") == paper_id]


def p1_table(ledger_path=DEFAULT_LEDGER) -> dict:
    rows = _entries("p1_toolmorph", ledger_path)
    # group success by (model, transform, task) -> we stored transform in result
    by = defaultdict(list)
    for e in rows:
        r = e.get("result") or {}
        model = e.get("model_id", "?")
        by[(model, r.get("transform", "?"))].append(1.0 if r.get("task_success") else 0.0)
    succ = {f"{m}|{t}": sum(v) / len(v) for (m, t), v in by.items()}
    # degradation vs original per model
    deg = {}
    models = {m for (m, _t) in by}
    for m in models:
        base = succ.get(f"{m}|original")
        if base is None:
            continue
        for (mm, t) in by:
            if mm == m and t != "original":
                deg[f"{m}|{t}"] = round(succ[f"{m}|{t}"] - base, 4)
    return {"success_rate": {k: round(v, 4) for k, v in succ.items()}, "degradation_vs_original": deg,
            "n_episodes": len(rows)}


def p2_table(ledger_path=DEFAULT_LEDGER) -> dict:
    rows = _entries("p2_crosscheck", ledger_path)
    byw = defaultdict(list)
    bya = defaultdict(list)
    for e in rows:
        r = e.get("result") or {}
        wf = r.get("workflow", "?")
        ok = 1.0 if r.get("final_correct") else 0.0
        byw[wf].append(ok)
        bya[f"{e.get('model_id','?')}|{wf}"].append(ok)
    return {"final_correct_by_workflow": {k: round(sum(v) / len(v), 4) for k, v in byw.items()},
            "by_author_workflow": {k: round(sum(v) / len(v), 4) for k, v in bya.items()},
            "n_episodes": len(rows)}


def p3_table(ledger_path=DEFAULT_LEDGER) -> dict:
    rows = _entries("p3_deltaresearch", ledger_path)
    by = defaultdict(lambda: {"acr": [], "ucp": []})
    for e in rows:
        r = e.get("result") or {}
        key = f"{e.get('model_id','?')}|{r.get('method','?')}"
        if "acr" in r:
            by[key]["acr"].append(r["acr"]); by[key]["ucp"].append(r["ucp"])
    out = {}
    for k, v in by.items():
        if v["acr"]:
            out[k] = {"acr": round(sum(v["acr"]) / len(v["acr"]), 4),
                      "ucp": round(sum(v["ucp"]) / len(v["ucp"]), 4), "n": len(v["acr"])}
    return {"acr_ucp_by_arm": out, "n_episodes": len(rows)}


def all_tables(ledger_path=DEFAULT_LEDGER) -> dict:
    return {"p1": p1_table(ledger_path), "p2": p2_table(ledger_path), "p3": p3_table(ledger_path)}


if __name__ == "__main__":  # pragma: no cover
    import json
    print(json.dumps(all_tables(), indent=2))
