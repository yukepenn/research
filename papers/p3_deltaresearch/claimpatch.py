"""No-gold end-to-end ClaimPatch (P3 spec F).

The method sees ONLY R0 (claim texts + values + citations), the sources, and the
observable delta. It never receives gold A/U, gold dependency edges, or gold
post-update values.

Pipeline:
  1. infer_structure (LLM): from claim TEXT, predict each derived claim's parents
     + op + constant, and which base claims the delta directly changes.
  2. recompute (deterministic calculator): propagate the delta through the
     INFERRED structure and recompute downstream values. No LLM arithmetic.
  3. constrained patch: edit exactly the claims whose recomputed value changed.

Oracle diagnostics (eval-only, clearly labeled upper bounds) use the world's gold
parents/values and are NOT the method.
"""
from __future__ import annotations

import json
import re

from core.adapters.cli import cli_complete
from papers.p3_deltaresearch.baselines import Patch
from papers.p3_deltaresearch.worlds_v2 import _compute

_OPS = "SUM, DIFF, RATIO, SCALE, AVG, PCT_CHANGE, THRESHOLD"


def _extract_json_obj(text: str):
    depth = 0; start = -1; last = None
    for i, ch in enumerate(text):
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start >= 0:
                try:
                    v = json.loads(text[start:i + 1])
                    if isinstance(v, dict):
                        last = v
                except Exception:
                    pass
                start = -1
    return last


def build_structure_prompt(world) -> str:
    rv = world.r0_view()
    lines = ["A research report contains these claims (id: text [value]):"]
    for c in rv["claims"]:
        lines.append(f"  {c['id']}: {c['text']}  [value={c['value']}]")
    lines.append("\nThe evidence sources are:")
    for s, v in rv["sources"].items():
        lines.append(f"  {s}: value={v['value']} status={v['status']}")
    lines.append(f"\nEVIDENCE UPDATE: {json.dumps(rv['delta'])}")
    lines.append(
        "\nSome claims are DERIVED from other claims by an arithmetic operation named in their "
        f"text (one of: {_OPS}). For EACH derived (non-base) claim, infer which other claim ids "
        "it is computed from (its parents, in order) and the operation and any constant. Also list "
        "which base claim ids are DIRECTLY changed by the evidence update (their cited source changed "
        "or was retracted). Use ONLY the claim texts and the update; do not guess new values.\n"
        'Output ONLY JSON: {"derived": {"<id>": {"parents": ["<id>",...], "op": "<OP>", '
        '"const": <number>}}, "directly_changed": ["<base id>",...]}. No prose.')
    return "\n".join(lines)


def infer_structure(model, world, *, timeout=150):
    res = cli_complete(model, build_structure_prompt(world), timeout=timeout)
    obj = _extract_json_obj(res.text) or {}
    return obj, res.model_id, res.raw


_UNRESOLVED = "<unresolved>"


def recompute_patch(world, structure) -> Patch:
    """Deterministic propagation through the INFERRED structure (no gold).

    Base post-values come from the OBSERVABLE delta (the method sees which source
    changed/retracted). Derived values are recomputed from the LLM-inferred
    (parents, op, const). `None` (loss of support, e.g. a retraction) propagates
    downstream. Unresolvable derived claims keep their original value.
    """
    claims = world.claims
    rv_delta = world.delta
    derived = (structure or {}).get("derived", {}) or {}

    post = {}
    for cid in world.report_claims:
        c = claims[cid]
        if c.kind == "base":
            if c.source in rv_delta.get("changed", {}):
                post[cid] = rv_delta["changed"][c.source]
            elif c.source in rv_delta.get("retracted", []):
                post[cid] = None
            else:
                post[cid] = c.value
        elif c.kind == "fact":
            post[cid] = c.value
        else:
            post[cid] = _UNRESOLVED

    for _ in range(len(world.report_claims) + 2):
        progressed = False
        for cid, spec in derived.items():
            if cid not in claims or claims[cid].kind in ("base", "fact"):
                continue
            if post.get(cid) is not _UNRESOLVED:
                continue
            parents = [p for p in (spec.get("parents") or []) if p in post]
            if not parents:
                continue  # no usable parents -> cannot resolve
            if any(post[p] is _UNRESOLVED for p in parents):
                continue  # wait for parents (handles ordering)
            try:  # a None parent (retracted) yields None -> propagates the loss
                val = _compute(spec.get("op", ""), [post[p] for p in parents],
                               float(spec.get("const", 0) or 0))
            except Exception:
                val = None
            post[cid] = val
            progressed = True
        if not progressed:
            break
    for cid in world.report_claims:
        if post.get(cid) is _UNRESOLVED:
            post[cid] = claims[cid].value  # could not infer -> keep original

    edited, new_values = set(), {}
    for cid in world.report_claims:
        c = claims[cid]
        if c.kind == "fact":
            continue
        if post[cid] != c.value:
            edited.add(cid)
            if isinstance(post[cid], (int, float, bool)):
                new_values[cid] = post[cid]
    return Patch(edited=edited, new_values=new_values)


def run_pipeline(model, world, *, timeout=150):
    structure, model_id, raw = infer_structure(model, world, timeout=timeout)
    patch = recompute_patch(world, structure)
    return patch, {"structure": structure, "model_id": model_id, "raw": raw[:4000]}


# ---- oracle diagnostics (eval-only upper bounds; NOT the method) ----
def oracle_graph_recompute_patch(world) -> Patch:
    """Upper bound: use the GOLD parents/ops, deterministic recompute."""
    gold_struct = {"derived": {}, "directly_changed": []}
    for cid in world.report_claims:
        c = world.claims[cid]
        if c.kind not in ("base", "fact"):
            gold_struct["derived"][cid] = {"parents": list(c.parents), "op": c.kind, "const": c.const}
        if c.kind == "base" and (c.source in world.delta.get("changed", {})
                                 or c.source in world.delta.get("retracted", [])):
            gold_struct["directly_changed"].append(cid)
    return recompute_patch(world, gold_struct)


def oracle_full_patch(world) -> Patch:
    """Full gold: edit exactly gold_A with gold post values."""
    nv = {c: world.post_values[c] for c in world.gold_A
          if isinstance(world.post_values.get(c), (int, float, bool))}
    return Patch(edited=set(world.gold_A), new_values=nv)
