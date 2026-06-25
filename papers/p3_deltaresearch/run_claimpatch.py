"""Run the no-gold ClaimPatch vs naive vs oracle diagnostics on v2 worlds.

Conditions (P3 spec G):
  naive_llm           : LLM gets R0+delta, emits a patch directly (no structure)  [REAL model]
  pipeline_nogold     : infer structure (LLM, no gold) + deterministic recompute  [REAL model]
  oracle_graph_recomp : gold structure + deterministic recompute (upper bound)    [no model]
  oracle_full         : gold A + gold values (upper bound)                        [no model]

Primary: affected-claim recall (ACR) with harmful-edit rate (spurious revision)
and numeric recomputation correctness, world-clustered. Pipeline vs naive is the
de-oracled method test the red-team demanded.
"""
from __future__ import annotations

import json
from collections import defaultdict

from core.adapters.cli import cli_available, cli_complete
from core.experiment_registry.ledger import RunLedger, make_entry
from core.statistics.resampling import paired_cluster_bootstrap_diff
from core.util import sha256_obj, short_id
from papers.p3_deltaresearch.baselines import Patch
from papers.p3_deltaresearch.claimpatch import (
    _extract_json_obj, oracle_full_patch, oracle_graph_recompute_patch, run_pipeline)
from papers.p3_deltaresearch.evaluator.metrics import acr, spurious_revision_rate, ucp
from papers.p3_deltaresearch.worlds_v2 import generate_worlds_v2

HARNESS = "p3_claimpatch_v2"
ORACLE = "p3v2_gold"


def calc_correctness(patch: Patch, world) -> float:
    numeric_A = [c for c in world.gold_A
                 if isinstance(world.post_values.get(c), (int, float))
                 and not isinstance(world.post_values.get(c), bool)]
    if not numeric_A:
        return 1.0
    ok = sum(1 for c in numeric_A
             if c in patch.new_values and abs(patch.new_values[c] - world.post_values[c]) < 1e-6)
    return ok / len(numeric_A)


def naive_patch(model, world, *, timeout=150):
    rv = world.r0_view()
    lines = ["A research report has these claims (id: text [value]):"]
    for c in rv["claims"]:
        lines.append(f"  {c['id']}: {c['text']} [value={c['value']}]")
    lines.append(f"\nEVIDENCE UPDATE: {json.dumps(rv['delta'])}")
    lines.append("\nSome claims are computed from others and must be recomputed if their inputs "
                 "change; unaffected claims must be left unchanged. Output ONLY JSON: "
                 '{"edited": ["<id>",...], "new_values": {"<id>": <number>}}. No prose.')
    res = cli_complete(model, "\n".join(lines), timeout=timeout)
    obj = _extract_json_obj(res.text) or {}
    nv = {}
    for k, v in (obj.get("new_values", {}) or {}).items():
        try:
            nv[k] = float(v)
        except (TypeError, ValueError):
            pass
    return Patch(edited=set(obj.get("edited", []) or []), new_values=nv), res.model_id


def _score(patch, world):
    return {"acr": acr(patch, world.gold_A), "ucp": ucp(patch, world.gold_U),
            "harmful": spurious_revision_rate(patch, world.gold_U),
            "calc": calc_correctness(patch, world)}


def run(models, *, n_worlds=20, seed0=0, ledger_path, git_commit="uncommitted", timeout=150,
        style="named"):
    worlds = generate_worlds_v2(n=n_worlds, seed0=seed0, style=style)
    ledger = RunLedger(ledger_path)
    rows = []  # (arm, model, world_id, scores)

    # deterministic oracle diagnostics (once per world, no model)
    for w in worlds:
        for arm, patch in (("oracle_graph_recompute", oracle_graph_recompute_patch(w)),
                           ("oracle_full", oracle_full_patch(w))):
            rows.append((arm, "deterministic", w.world_id, _score(patch, w)))

    for model in models:
        if not cli_available(model):
            continue
        for w in worlds:
            npatch, mid = naive_patch(model, w, timeout=timeout)
            ns = _score(npatch, w)
            ppatch, meta = run_pipeline(model, w, timeout=timeout)
            ps = _score(ppatch, w)
            for arm, sc, extra in (("naive_llm", ns, {}),
                                   ("pipeline_nogold", ps, {"structure": meta["structure"]})):
                th = ledger.store_trace({"world": w.world_id, "arm": arm, **extra})
                ledger.append(make_entry(
                    run_id=short_id(model, arm, w.world_id, HARNESS),
                    paper_id="p3_deltaresearch", git_commit=git_commit,
                    task_hash=sha256_obj(w.world_id)[:12],
                    environment_hash=sha256_obj(w.topology + w.delta_type),
                    model_provider="cli_subscription", model_id=f"{model}:{mid}",
                    harness_hash=HARNESS, oracle_version=ORACLE, raw_trace_hash=th,
                    status="SUCCESS", cost_usd=0.0,
                    result={"arm": arm, "topology": w.topology, "delta_type": w.delta_type, **sc},
                    notes="P3 no-gold ClaimPatch (subscription CLI)"))
            rows.append(("naive_llm", model, w.world_id, ns))
            rows.append(("pipeline_nogold", model, w.world_id, ps))

    # aggregate + paired bootstrap (pipeline - naive) ACR per model, world-clustered
    agg = defaultdict(lambda: defaultdict(list))
    for arm, model, wid, sc in rows:
        for k, v in sc.items():
            agg[(arm, model)][k].append(v)
    summary = {f"{arm}|{model}": {k: round(sum(v) / len(v), 4) for k, v in d.items()}
               for (arm, model), d in agg.items()}

    deltas = {}
    for model in models:
        n = {(wid): sc for arm, m, wid, sc in rows if arm == "naive_llm" and m == model}
        p = {(wid): sc for arm, m, wid, sc in rows if arm == "pipeline_nogold" and m == model}
        wids = sorted(set(n) & set(p))
        if wids:
            a = [n[w]["acr"] for w in wids]
            b = [p[w]["acr"] for w in wids]
            ci = paired_cluster_bootstrap_diff(a, b, wids, n_boot=3000, seed=0)
            deltas[model] = {"acr_pipeline_minus_naive": round(ci.point, 4),
                             "ci": [round(ci.lo, 4), round(ci.hi, 4)], "n_worlds": len(wids)}
    return {"summary": summary, "pipeline_minus_naive": deltas, "n_worlds": len(worlds)}


if __name__ == "__main__":  # pragma: no cover
    import argparse
    import os
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", default="claude,codex")
    ap.add_argument("--n", type=int, default=20)
    ap.add_argument("--seed0", type=int, default=0)
    ap.add_argument("--style", default="named")
    ap.add_argument("--ledger", default="artifacts/run_ledger.jsonl")
    args = ap.parse_args()
    commit = os.popen("git rev-parse --short HEAD").read().strip() or "uncommitted"
    out = run(args.models.split(","), n_worlds=args.n, seed0=args.seed0,
              ledger_path=args.ledger, git_commit=commit, style=args.style)
    print(json.dumps(out, indent=2))
