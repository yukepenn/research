"""Stage-wise diagnostic for the no-gold ClaimPatch (P3 spec H / RQ2).

The pipeline's quality reduces to how well the LLM infers the dependency
structure from claim text. This module reads the pipeline episodes' stored
inferred structure and compares it to the gold structure (parents + op) to
produce a causal error decomposition:

  - parent-edge precision / recall  (did it find the right dependencies?)
  - op accuracy                     (did it name the right operation?)
  - structure-exact rate            (fraction of derived claims fully correct)

This explains the end-to-end ACR rather than asserting a bottleneck from one
prompt. Deterministic; reads the immutable ledger + content-addressed traces.
"""
from __future__ import annotations

import json
import os
from collections import defaultdict

from core.experiment_registry.ledger import RunLedger
from papers.p3_deltaresearch.worlds_v2 import generate_worlds_v2


def _world_map(n=24, seed0=0):
    return {w.world_id: w for w in generate_worlds_v2(n=n, seed0=seed0)}


def _load_trace(trace_dir, h):
    p = os.path.join(trace_dir, f"{h}.json")
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def analyze(ledger_path="artifacts/p3v2_ledger.jsonl", n=24, seed0=0) -> dict:
    ledger = RunLedger(ledger_path)
    trace_dir = ledger.trace_dir
    wmap = _world_map(n, seed0)
    per_model = defaultdict(lambda: {"edge_tp": 0, "edge_fp": 0, "edge_fn": 0,
                                     "op_ok": 0, "op_tot": 0, "derived_exact": 0,
                                     "derived_tot": 0})
    for e in ledger.read_all():
        if e.get("result", {}).get("arm") != "pipeline_nogold":
            continue
        tr = _load_trace(trace_dir, e["raw_trace_hash"])
        if not tr:
            continue
        w = wmap.get(tr.get("world"))
        if not w:
            continue
        inferred = (tr.get("structure") or {}).get("derived", {}) or {}
        m = per_model[e["model_id"]]
        for cid, c in w.claims.items():
            if c.kind in ("base", "fact"):
                continue
            m["derived_tot"] += 1
            gold_parents = set(c.parents)
            spec = inferred.get(cid, {})
            inf_parents = set(spec.get("parents", []) or [])
            m["edge_tp"] += len(gold_parents & inf_parents)
            m["edge_fp"] += len(inf_parents - gold_parents)
            m["edge_fn"] += len(gold_parents - inf_parents)
            m["op_tot"] += 1
            if spec.get("op") == c.kind:
                m["op_ok"] += 1
            if inf_parents == gold_parents and spec.get("op") == c.kind:
                m["derived_exact"] += 1
    out = {}
    for model, m in per_model.items():
        tp, fp, fn = m["edge_tp"], m["edge_fp"], m["edge_fn"]
        out[model] = {
            "edge_precision": round(tp / (tp + fp), 4) if (tp + fp) else None,
            "edge_recall": round(tp / (tp + fn), 4) if (tp + fn) else None,
            "op_accuracy": round(m["op_ok"] / m["op_tot"], 4) if m["op_tot"] else None,
            "derived_exact_rate": round(m["derived_exact"] / m["derived_tot"], 4) if m["derived_tot"] else None,
            "n_derived": m["derived_tot"],
        }
    return out


if __name__ == "__main__":  # pragma: no cover
    print(json.dumps(analyze(), indent=2))
