"""P1 plan-then-execute pilot using subscription CLI models (no API cost).

For each (model, task, transform): present the (possibly transformed) tool
schemas as text, ask the model for a JSON tool-call plan, execute the plan
against the deterministic environment, and score with the invariant oracle.
Every episode is written to the immutable run ledger. The paired
original-vs-transform success difference is the metamorphic sensitivity signal.

This is REAL model evidence (Claude + Codex), but PILOT-scale and product-CLI
sourced; it is interpreted per the narrowed contract (phenomenon evidence toward
H1/H3/H4), not a frozen full study.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field

from core.adapters.cli import cli_available, cli_complete, extract_json_plan
from core.experiment_registry.ledger import RunLedger, make_entry
from core.statistics.resampling import paired_cluster_bootstrap_diff
from core.util import sha256_obj, short_id
from papers.p1_toolmorph.metamorphic import present_tools
from papers.p1_toolmorph.oracles.state_oracle import ORACLE_VERSION, task_passed
from papers.p1_toolmorph.tasks import SYSTEM_PROMPT, all_tasks
from papers.p1_toolmorph.transforms.families import all_strict_transforms

HARNESS = "plan_execute_v1"


def _describe_schema(schema: dict) -> str:
    props = schema.get("properties", {})
    required = set(schema.get("required", []))
    parts = []
    for k, spec in props.items():
        t = spec.get("type", "any")
        extra = ""
        if "enum" in spec:
            extra = f" one of {spec['enum']}"
        if t == "object" and "properties" in spec:
            inner = ", ".join(f"{ik}:{iv.get('type','any')}" for ik, iv in spec["properties"].items())
            extra = f" {{{inner}}}"
        req = "" if k in required else " (optional)"
        parts.append(f"{k}:{t}{extra}{req}")
    return ", ".join(parts) if parts else "(no arguments)"


def build_prompt(task, presented_tools) -> str:
    lines = [SYSTEM_PROMPT, "", "Available tools:"]
    for t in presented_tools:
        lines.append(f"- {t.name}({_describe_schema(t.schema)}): {t.description}")
    lines += [
        "", f"TASK: {task.task_prompt}",
        "",
        "Output ONLY a JSON array of tool calls to accomplish the task, in order. "
        'Each element is {"tool": <name>, "args": {<argument map>}}. '
        "Use the exact tool names and argument names shown above. No prose, no code fences.",
    ]
    return "\n".join(lines)


def execute_plan(env, presented_tools, plan) -> tuple[int, list]:
    dispatch = {t.name: t for t in presented_tools}
    errors = []
    n = 0
    for step in plan or []:
        name = step.get("tool")
        args = step.get("args", {}) or {}
        tool = dispatch.get(name)
        if tool is None or tool.executor is None:
            errors.append(f"unknown tool {name}")
            continue
        try:
            tool.executor(args)
            n += 1
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{name}: {exc}")
    return n, errors


@dataclass
class EpisodeOutcome:
    model: str
    task_id: str
    transform: str
    rep: int
    task_success: bool
    plan_parsed: bool
    n_calls: int
    model_id: str = ""
    errors: list = field(default_factory=list)


def run_pilot_episode(model: str, task, transform, *, rep: int, ledger: RunLedger,
                      git_commit: str = "uncommitted", timeout: int = 180) -> EpisodeOutcome:
    env = task.env_factory()
    tools = present_tools(env, transform)
    prompt = build_prompt(task, tools)
    res = cli_complete(model, prompt, timeout=timeout)
    plan = extract_json_plan(res.text)

    env.reset()
    n_calls, errors = execute_plan(env, tools, plan)
    success = bool(plan is not None) and task_passed(env.final_state(), task)
    fam = getattr(transform, "family", "original")

    trace_hash = ledger.store_trace({
        "prompt": prompt, "raw_output": res.raw[:8000], "plan": plan, "errors": errors})
    status = "SUCCESS" if (res.ok and plan is not None) else "AGENT_FAILURE"
    ledger.append(make_entry(
        run_id=short_id(model, task.task_id, fam, rep, HARNESS),
        paper_id="p1_toolmorph", git_commit=git_commit,
        task_hash=sha256_obj(task.task_id)[:12], environment_hash=env.environment_hash(),
        model_provider="cli_subscription", model_id=f"{model}:{res.model_id}",
        harness_hash=HARNESS, oracle_version=ORACLE_VERSION, raw_trace_hash=trace_hash,
        status=status, cost_usd=0.0, seed=rep,
        result={"task_success": success, "transform": fam, "n_calls": n_calls,
                "plan_parsed": plan is not None, "n_errors": len(errors)},
        notes="plan-then-execute pilot (subscription CLI, no API cost)"))
    return EpisodeOutcome(model, task.task_id, fam, rep, success, plan is not None,
                          n_calls, res.model_id, errors)


def run_pilot(models, tasks=None, transforms=None, *, reps: int = 1,
              ledger_path: str, git_commit: str = "uncommitted", timeout: int = 180) -> dict:
    """Run the paired original-vs-transform pilot and return per-(model,transform)
    degradation with a task-clustered CI. Writes every episode to the ledger."""
    tasks = tasks if tasks is not None else all_tasks()
    transforms = transforms if transforms is not None else all_strict_transforms()
    ledger = RunLedger(ledger_path)
    outcomes: list[EpisodeOutcome] = []

    for model in models:
        if not cli_available(model):
            continue
        for task in tasks:
            for rep in range(reps):
                # original
                outcomes.append(run_pilot_episode(model, task, None, rep=rep, ledger=ledger,
                                                  git_commit=git_commit, timeout=timeout))
                for tr in transforms:
                    outcomes.append(run_pilot_episode(model, task, tr, rep=rep, ledger=ledger,
                                                      git_commit=git_commit, timeout=timeout))

    # analysis: paired degradation per (model, transform)
    results = {}
    for model in models:
        mo = [o for o in outcomes if o.model == model]
        orig = {(o.task_id, o.rep): o.task_success for o in mo if o.transform == "original"}
        for fam in {o.transform for o in mo if o.transform != "original"}:
            a, b, clusters = [], [], []
            for o in mo:
                if o.transform != fam:
                    continue
                key = (o.task_id, o.rep)
                if key in orig:
                    a.append(float(orig[key])); b.append(float(o.task_success))
                    clusters.append(o.task_id)
            if a:
                ci = paired_cluster_bootstrap_diff(a, b, clusters, n_boot=2000, seed=0)
                results[f"{model}|{fam}"] = {
                    "orig_success": sum(a) / len(a), "mut_success": sum(b) / len(b),
                    "degradation": ci.point, "ci_lo": ci.lo, "ci_hi": ci.hi, "n": len(a)}
    return {"results": results, "n_episodes": len(outcomes),
            "outcomes": [o.__dict__ for o in outcomes]}


if __name__ == "__main__":  # pragma: no cover
    import argparse
    import os
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", default="claude,codex")
    ap.add_argument("--n-tasks", type=int, default=0, help="0 = all")
    ap.add_argument("--transforms", default="", help="comma families, blank=all")
    ap.add_argument("--reps", type=int, default=1)
    ap.add_argument("--ledger", default="artifacts/run_ledger.jsonl")
    args = ap.parse_args()

    from papers.p1_toolmorph.transforms.families import STRICT_FAMILIES
    tasks = all_tasks()[: args.n_tasks] if args.n_tasks else all_tasks()
    if args.transforms:
        want = set(args.transforms.split(","))
        transforms = [c() for c in STRICT_FAMILIES if c().family in want]
    else:
        transforms = all_strict_transforms()
    commit = os.popen("git rev-parse --short HEAD").read().strip() or "uncommitted"
    out = run_pilot(args.models.split(","), tasks, transforms, reps=args.reps,
                    ledger_path=args.ledger, git_commit=commit)
    print(json.dumps(out["results"], indent=2))
    print(f"episodes: {out['n_episodes']}")
