"""Corrected no-gold ClaimPatch (post-audit, 2026-06-26).

Fixes the hidden-metadata leakage: the method receives ONLY the sanitized public
input (claims with id/text/value/CITATION, the cited sources, and the observable
delta) — never the World, never claim.kind / claim.source / gold / post_values.

- Claim ROLE (sourced vs derived) and the claim->source link are read from the
  VISIBLE citation (legitimate report content): a claim citing "(derived)" is
  derived; otherwise it cites a source id.
- Base/sourced post-values come from the OBSERVABLE delta (which cited source
  changed/was retracted).
- The LLM infers each DERIVED claim's (parents, op, const) from the claim TEXTS.
- A SEPARATE calculator (`_calc`, not the generator's `_compute`) recomputes.

Leakage is enforced structurally: every entry point takes a plain dict and is
covered by `test_p3_leakage`.
"""
from __future__ import annotations

import json
import math
import re

from core.adapters.cli import cli_complete
from papers.p3_deltaresearch.baselines import Patch

_OPS = "SUM, DIFF, RATIO, SCALE, AVG, PCT_CHANGE, THRESHOLD"
_UNRESOLVED = "<unresolved>"


def _calc(op, args, const):
    """Independent calculator (deliberately NOT the generator's _compute)."""
    if any(a is None for a in args):
        return None
    try:
        if op == "SUM":
            return round(math.fsum(args), 4)
        if op == "AVG":
            return round(math.fsum(args) / len(args), 4)
        if op == "DIFF":
            return round(args[0] - args[1], 4)
        if op == "RATIO":
            return round(args[0] / args[1], 4) if args[1] else None
        if op == "SCALE":
            return round(args[0] * const, 4)
        if op == "PCT_CHANGE":
            return round((args[1] - args[0]) / args[0] * 100.0, 4) if args[0] else None
        if op == "THRESHOLD":
            return bool(args[0] >= const)
    except (TypeError, ZeroDivisionError, IndexError):
        return None
    return None


def _parse_value(s):
    if isinstance(s, (int, float, bool)):
        return s
    t = str(s).strip()
    if t in ("yes", "no"):
        return t == "yes"
    try:
        return float(t)
    except ValueError:
        return t  # categorical / fact string


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


def build_structure_prompt(public_input) -> str:
    claims = public_input["claims"]
    derived = [c["id"] for c in claims if c.get("citation") == "(derived)"]
    lines = ["A research report contains these claims (id: text [value], cited source):"]
    for c in claims:
        lines.append(f"  {c['id']}: {c['text']} [value={c['value']}] (cited: {c.get('citation')})")
    lines.append("\nThe evidence sources are:")
    for s, v in public_input["sources"].items():
        lines.append(f"  {s}: value={v['value']} status={v['status']}")
    lines.append(f"\nEVIDENCE UPDATE: {json.dumps(public_input['delta'])}")
    lines.append(
        f"\nClaims cited as \"(derived)\" are computed from OTHER claims by an arithmetic operation "
        f"(one of: {_OPS}). For EACH derived claim {derived}, infer which other claim ids it is "
        "computed from (parents, in order) and the operation + any constant, using ONLY the claim "
        "texts/values. Do not output new values.\n"
        'Output ONLY JSON: {"derived": {"<id>": {"parents": ["<id>",...], "op": "<OP>", '
        '"const": <number>}}}. No prose.')
    return "\n".join(lines)


def infer_structure_public(model, public_input, *, timeout=150):
    res = cli_complete(model, build_structure_prompt(public_input), timeout=timeout)
    obj = _extract_json_obj(res.text) or {}
    return obj, res.model_id, res.raw


def recompute_from_public(public_input, structure) -> Patch:
    """Deterministic propagation using ONLY public input + the inferred structure."""
    claims = public_input["claims"]
    delta = public_input["delta"]
    cmap = {c["id"]: c for c in claims}
    order = [c["id"] for c in claims]
    derived = (structure or {}).get("derived", {}) or {}
    changed = delta.get("changed", {}) or {}
    retracted = set(delta.get("retracted", []) or [])

    orig = {cid: _parse_value(cmap[cid]["value"]) for cid in order}
    post = {}
    for cid in order:
        cit = cmap[cid].get("citation")
        if cit == "(derived)":
            post[cid] = _UNRESOLVED
        elif cit in changed:                 # sourced claim, its source revised
            post[cid] = changed[cit]
        elif cit in retracted:               # sourced claim, its source retracted
            post[cid] = None
        else:                                # sourced claim, source unchanged (incl. facts)
            post[cid] = orig[cid]

    for _ in range(len(order) + 2):
        progressed = False
        for cid, spec in derived.items():
            if cid not in cmap or post.get(cid) is not _UNRESOLVED:
                continue
            parents = [p for p in (spec.get("parents") or []) if p in post]
            if not parents or any(post[p] is _UNRESOLVED for p in parents):
                continue
            post[cid] = _calc(spec.get("op", ""), [post[p] for p in parents],
                              float(spec.get("const", 0) or 0))
            progressed = True
        if not progressed:
            break
    for cid in order:
        if post.get(cid) is _UNRESOLVED:
            post[cid] = orig[cid]

    edited, new_values = set(), {}
    for cid in order:
        if post[cid] != orig[cid]:
            edited.add(cid)
            if isinstance(post[cid], (int, float, bool)):
                new_values[cid] = post[cid]
    return Patch(edited=edited, new_values=new_values)


def run_pipeline_v2(model, public_input, *, timeout=150):
    """The corrected no-gold method. `public_input` MUST be a sanitized dict
    (e.g. World.r0_view()), never a World."""
    if not isinstance(public_input, dict):
        raise TypeError("run_pipeline_v2 takes the sanitized public dict, not a World")
    structure, model_id, raw = infer_structure_public(model, public_input, timeout=timeout)
    patch = recompute_from_public(public_input, structure)
    return patch, {"structure": structure, "model_id": model_id, "raw": raw[:4000]}


def naive_public(model, public_input, *, timeout=150):
    claims = public_input["claims"]
    lines = ["A research report has these claims (id: text [value], cited source):"]
    for c in claims:
        lines.append(f"  {c['id']}: {c['text']} [value={c['value']}] (cited: {c.get('citation')})")
    lines.append(f"\nEVIDENCE UPDATE: {json.dumps(public_input['delta'])}")
    lines.append('\nSome claims are computed from others and must be recomputed if their inputs '
                 'change; unaffected claims must be left unchanged. Output ONLY JSON: '
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
