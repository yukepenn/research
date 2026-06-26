"""Run the CORRECTED no-gold ClaimPatch (post-audit) vs naive, on real models.

Method takes ONLY the sanitized public view (r0_view: claims id/text/value/citation,
sources, observable delta). Primary metric is Correct Update Recall (not ID-recall).
Worlds use one delta per seed -> world_id is a valid bootstrap cluster.
"""
from __future__ import annotations

import json
from collections import defaultdict

from core.adapters.cli import cli_available
from core.experiment_registry.ledger import RunLedger, make_entry
from core.statistics.resampling import paired_cluster_bootstrap_diff
from core.util import sha256_obj, short_id
from papers.p3_deltaresearch.claimpatch_v2 import naive_public, run_pipeline_v2
from papers.p3_deltaresearch.evaluator.metrics import (
    acr, correct_update_recall, spurious_revision_rate)
from papers.p3_deltaresearch.worlds_v2 import generate_worlds_v2

HARNESS = "p3_claimpatch_v2_audited"
ORACLE = "p3v2_gold_v2"


def _score(patch, world):
    return {"cur": correct_update_recall(patch, world), "acr": acr(patch, world.gold_A),
            "harmful": spurious_revision_rate(patch, world.gold_U)}


def run(models, *, n_worlds=24, seed0=0, style="named", ledger_path, git_commit="uncommitted",
        timeout=150):
    worlds = generate_worlds_v2(n=n_worlds, seed0=seed0, style=style)
    ledger = RunLedger(ledger_path)
    rows = []
    for model in models:
        if not cli_available(model):
            continue
        for w in worlds:
            view = w.r0_view()  # SANITIZED public input
            npatch, mid = naive_public(model, view, timeout=timeout)
            ppatch, meta = run_pipeline_v2(model, view, timeout=timeout)
            for arm, patch, extra in (("naive", npatch, {}),
                                      ("pipeline_nogold", ppatch, {"structure": meta["structure"]})):
                sc = _score(patch, w)
                th = ledger.store_trace({"world": w.world_id, "arm": arm, "style": style, **extra})
                ledger.append(make_entry(
                    run_id=short_id(model, arm, w.world_id, style, HARNESS),
                    paper_id="p3_deltaresearch", git_commit=git_commit,
                    task_hash=sha256_obj(w.world_id)[:12],
                    environment_hash=sha256_obj(w.topology + w.delta_type),
                    model_provider="cli_subscription", model_id=f"{model}:{mid}",
                    harness_hash=HARNESS, oracle_version=ORACLE, raw_trace_hash=th,
                    status="SUCCESS", cost_usd=0.0,
                    result={"arm": arm, "style": style, "topology": w.topology,
                            "delta_type": w.delta_type, "seed": w.seed, **sc},
                    notes="P3 corrected no-gold (public input, Correct Update Recall)"))
                rows.append((arm, model, w.world_id, sc))

    agg = defaultdict(lambda: defaultdict(list))
    for arm, model, wid, sc in rows:
        for k, v in sc.items():
            agg[(arm, model)][k].append(v)
    summary = {f"{arm}|{m}": {k: round(sum(v) / len(v), 4) for k, v in d.items()}
               for (arm, m), d in agg.items()}
    deltas = {}
    for model in models:
        n = {wid: sc for arm, mm, wid, sc in rows if arm == "naive" and mm == model}
        p = {wid: sc for arm, mm, wid, sc in rows if arm == "pipeline_nogold" and mm == model}
        wids = sorted(set(n) & set(p))
        if wids:
            a = [n[w]["cur"] for w in wids]; b = [p[w]["cur"] for w in wids]
            ci = paired_cluster_bootstrap_diff(a, b, wids, n_boot=3000, seed=0)
            deltas[model] = {"cur_pipeline_minus_naive": round(ci.point, 4),
                             "ci": [round(ci.lo, 4), round(ci.hi, 4)], "n_worlds": len(wids)}
    return {"summary": summary, "pipeline_minus_naive_CUR": deltas, "n_worlds": len(worlds)}


if __name__ == "__main__":  # pragma: no cover
    import argparse
    import os
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", default="claude,codex")
    ap.add_argument("--n", type=int, default=24)
    ap.add_argument("--seed0", type=int, default=0)
    ap.add_argument("--style", default="named")
    ap.add_argument("--ledger", default="artifacts/p3v2_audited_ledger.jsonl")
    args = ap.parse_args()
    commit = os.popen("git rev-parse --short HEAD").read().strip() or "uncommitted"
    out = run(args.models.split(","), n_worlds=args.n, seed0=args.seed0, style=args.style,
              ledger_path=args.ledger, git_commit=commit)
    print(json.dumps(out, indent=2))
