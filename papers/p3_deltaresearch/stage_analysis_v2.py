"""Corrected stage-wise diagnostic (post-audit): ORDERED-parent + full-expression
match, not unordered parent sets. Reads the audited v2 ledger.

Reports, per model, how well the LLM infers structure:
  - unordered_parent_PR : precision/recall on the parent SET (loose)
  - ordered_parent_exact : fraction of derived claims with the EXACT ordered parents
  - op_accuracy          : correct operation
  - full_expression_exact: ordered parents AND op AND const all correct (the honest one)
"""
from __future__ import annotations

import json
import os
from collections import defaultdict

from core.experiment_registry.ledger import RunLedger
from papers.p3_deltaresearch.worlds_v2 import generate_worlds_v2


def _world_map(n=24, seed0=0, style="named"):
    return {w.world_id: w for w in generate_worlds_v2(n=n, seed0=seed0, style=style)}


def analyze(ledger_path="artifacts/p3v2_audited_ledger.jsonl", n=24, seed0=0, style="named") -> dict:
    ledger = RunLedger(ledger_path)
    wmap = _world_map(n, seed0, style)
    per = defaultdict(lambda: {"set_tp": 0, "set_fp": 0, "set_fn": 0, "ord_exact": 0,
                               "op_ok": 0, "full_exact": 0, "tot": 0})
    for e in ledger.read_all():
        r = e.get("result", {})
        if r.get("arm") != "pipeline_nogold":
            continue
        tr_path = os.path.join(ledger.trace_dir, f"{e['raw_trace_hash']}.json")
        if not os.path.exists(tr_path):
            continue
        tr = json.load(open(tr_path, encoding="utf-8"))
        w = wmap.get(tr.get("world"))
        if not w:
            continue
        inferred = (tr.get("structure") or {}).get("derived", {}) or {}
        m = per[e["model_id"]]
        for cid, c in w.claims.items():
            if c.kind in ("base", "fact"):
                continue
            m["tot"] += 1
            gold_parents = list(c.parents)
            spec = inferred.get(cid, {})
            inf_parents = list(spec.get("parents", []) or [])
            gset, iset = set(gold_parents), set(inf_parents)
            m["set_tp"] += len(gset & iset); m["set_fp"] += len(iset - gset); m["set_fn"] += len(gset - iset)
            ord_ok = inf_parents == gold_parents
            op_ok = spec.get("op") == c.kind
            const_ok = abs(float(spec.get("const", 0) or 0) - float(c.const)) < 1e-9
            m["ord_exact"] += int(ord_ok)
            m["op_ok"] += int(op_ok)
            m["full_exact"] += int(ord_ok and op_ok and const_ok)
    out = {}
    for model, m in per.items():
        tp, fp, fn, tot = m["set_tp"], m["set_fp"], m["set_fn"], m["tot"]
        out[model] = {
            "unordered_parent_precision": round(tp / (tp + fp), 4) if (tp + fp) else None,
            "unordered_parent_recall": round(tp / (tp + fn), 4) if (tp + fn) else None,
            "ordered_parent_exact": round(m["ord_exact"] / tot, 4) if tot else None,
            "op_accuracy": round(m["op_ok"] / tot, 4) if tot else None,
            "full_expression_exact": round(m["full_exact"] / tot, 4) if tot else None,
            "n_derived": tot,
        }
    return out


if __name__ == "__main__":  # pragma: no cover
    print(json.dumps(analyze(), indent=2))
