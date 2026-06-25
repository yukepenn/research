"""P3 plan-then-patch pilot using subscription CLI models (no API cost).

For each controlled world: present the report's atomic claims + a natural-language
description of the evidence-WORLD delta, and ask the model for a claim-level patch
(which claims to edit, new numeric values, contested flags, additions). Score with
the deterministic gold (ACR/UCP + diagnostics) from `evaluator.metrics`.

Compares, on the SAME worlds:
  - naive LLM patch (claude / codex)               -> H1: agents miss derived/temporal claims
  - LLM patch WITH the typed-graph impact hint     -> does the structure help the agent?
  - typed_graph method (deterministic, no LLM)     -> the paper's method
  - full_regeneration / naive_revise (deterministic baselines)
  - oracle upper bound

Everything except the LLM arms is deterministic; the LLM arms are real pilot
evidence, honestly scoped.
"""
from __future__ import annotations

import json
from dataclasses import dataclass

from core.adapters.cli import cli_available, cli_complete, extract_json_plan
from core.experiment_registry.ledger import RunLedger, make_entry
from core.util import sha256_obj, short_id
from papers.p3_deltaresearch.baselines import (
    Patch, full_regeneration_patch, naive_revise_patch, oracle_upper_bound_patch,
    typed_graph_patch, typed_graph_predict)
from papers.p3_deltaresearch.controlled_worlds.generator import ASSERTED, generate_worlds
from papers.p3_deltaresearch.evaluator.metrics import combined_score, full_report

HARNESS = "p3_plan_patch_v1"
ORACLE_VERSION = "p3_gold_v1"


def describe_delta(world) -> str:
    d = world.delta
    claims = world.claims
    parts = []

    def claim_for(eid):
        return [c for c in claims if eid in claims[c].supports]

    for e in sorted(d.changed_value_evidence | d.superseded_evidence):
        owner = claim_for(e)
        val = world.evidence[e].value
        parts.append(f"- Source {e} (supporting {owner}) now reports the value {val}.")
    for e in sorted(d.retracted_evidence):
        owner = claim_for(e)
        parts.append(f"- Source {e} (supporting {owner}) has been RETRACTED.")
    for e in sorted(d.conflicted_evidence):
        owner = claim_for(e)
        parts.append(f"- A new source CONFLICTS with source {e} (supporting {owner}).")
    if d.temporal_changed_groups:
        parts.append("- A newer official rate source has become the currently-valid one.")
    if not parts:
        parts.append("- An unrelated source changed; it may not affect any claim.")
    return "\n".join(parts)


def build_prompt(world, *, typed_hint=None) -> str:
    lines = ["You maintain a research report. Its atomic claims (id: text):"]
    for cid in ASSERTED:
        lines.append(f"[{cid}] {world.claims[cid].text}")
    lines += ["", "EVIDENCE-WORLD UPDATE:", describe_delta(world), ""]
    lines.append(
        "Some claims are COMPUTED from others (a total = sum of parts; a margin = "
        "difference; a share = part/total; an index = share*100; a projection = "
        "rate*constant) and MUST be recomputed when their inputs change. Claims that "
        "are not affected MUST be left unchanged.")
    if typed_hint is not None:
        lines.append(f"A dependency analysis flags these claims as possibly affected: "
                     f"{sorted(typed_hint)}.")
    lines += [
        "",
        'Output ONLY JSON: {"edited":[claim_ids that must change], '
        '"new_values":{claim_id: numeric_value}, "flagged_contested":[claim_ids now '
        'contested], "added":[new claim_ids]}. No prose, no code fences.']
    return "\n".join(lines)


def _patch_from_output(obj: dict) -> Patch:
    edited = set(obj.get("edited", []) or [])
    nv = {}
    for k, v in (obj.get("new_values", {}) or {}).items():
        try:
            nv[k] = float(v)
        except (TypeError, ValueError):
            pass
    return Patch(edited=edited, new_values=nv,
                 flagged_contested=set(obj.get("flagged_contested", []) or []),
                 added=set(obj.get("added", []) or []))


def _extract_obj(text: str):
    # reuse the array extractor's brace-scan idea for a single object
    import re
    for m in re.finditer(r"\{.*\}", text, re.DOTALL):
        frag = m.group(0)
        # try progressively shorter prefixes ending in '}'
        for end in range(len(frag), 0, -1):
            if frag[end - 1] != "}":
                continue
            try:
                val = json.loads(frag[:end])
                if isinstance(val, dict):
                    return val
            except (json.JSONDecodeError, ValueError):
                continue
    return None


@dataclass
class P3Outcome:
    model: str
    method: str
    world_id: str
    dtype: str
    acr: float
    ucp: float
    parsed: bool


def run_llm_arm(model, world, *, method, typed_hint, ledger, git_commit, timeout=180) -> P3Outcome:
    prompt = build_prompt(world, typed_hint=typed_hint)
    res = cli_complete(model, prompt, timeout=timeout)
    obj = _extract_obj(res.text)
    patch = _patch_from_output(obj) if obj else Patch()
    cs = combined_score(patch, world)
    trace_hash = ledger.store_trace({"prompt": prompt, "raw": res.raw[:8000], "patch": obj})
    ledger.append(make_entry(
        run_id=short_id(model, method, world.world_id, HARNESS),
        paper_id="p3_deltaresearch", git_commit=git_commit,
        task_hash=sha256_obj(world.world_id)[:12], environment_hash=sha256_obj(world.dtype),
        model_provider="cli_subscription", model_id=f"{model}:{res.model_id}",
        harness_hash=HARNESS, oracle_version=ORACLE_VERSION, raw_trace_hash=trace_hash,
        status="SUCCESS" if (res.ok and obj is not None) else "AGENT_FAILURE", cost_usd=0.0,
        result={"method": method, "acr": cs.acr, "ucp": cs.ucp, "dtype": world.dtype,
                **full_report(patch, world)},
        notes="P3 plan-then-patch pilot (subscription CLI)"))
    return P3Outcome(model, method, world.world_id, world.dtype, cs.acr, cs.ucp, obj is not None)


def run_pilot(models, *, n_seeds=3, ledger_path: str, git_commit="uncommitted",
              timeout=180) -> dict:
    worlds = generate_worlds(n=n_seeds)
    ledger = RunLedger(ledger_path)
    rows = []

    # deterministic baselines (no LLM) -- computed once per world
    det = {}
    for w in worlds:
        for name, patch in (("typed_graph", typed_graph_patch(w)),
                            ("full_regen", full_regeneration_patch(w)),
                            ("naive_ledger", naive_revise_patch(w)),
                            ("oracle", oracle_upper_bound_patch(w))):
            cs = combined_score(patch, w)
            det.setdefault(name, []).append((cs.acr, cs.ucp))

    # LLM arms
    for model in models:
        if not cli_available(model):
            continue
        for w in worlds:
            rows.append(run_llm_arm(model, w, method="naive_llm", typed_hint=None,
                                    ledger=ledger, git_commit=git_commit, timeout=timeout))
            hint = typed_graph_predict(w).affected
            rows.append(run_llm_arm(model, w, method="typed_hint_llm", typed_hint=hint,
                                    ledger=ledger, git_commit=git_commit, timeout=timeout))

    # aggregate
    def mean_pair(pairs):
        n = len(pairs)
        return {"acr": sum(p[0] for p in pairs) / n, "ucp": sum(p[1] for p in pairs) / n, "n": n}

    agg = {f"det:{k}": mean_pair(v) for k, v in det.items()}
    by_arm = {}
    for r in rows:
        by_arm.setdefault(f"{r.model}:{r.method}", []).append((r.acr, r.ucp))
    for k, v in by_arm.items():
        agg[k] = mean_pair(v)
    return {"agg": agg, "n_worlds": len(worlds), "n_llm_episodes": len(rows)}


if __name__ == "__main__":  # pragma: no cover
    import argparse
    import os
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", default="claude,codex")
    ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--ledger", default="artifacts/run_ledger.jsonl")
    args = ap.parse_args()
    commit = os.popen("git rev-parse --short HEAD").read().strip() or "uncommitted"
    out = run_pilot(args.models.split(","), n_seeds=args.seeds,
                    ledger_path=args.ledger, git_commit=commit)
    print(json.dumps(out["agg"], indent=2))
    print(f"worlds={out['n_worlds']} llm_episodes={out['n_llm_episodes']}")
