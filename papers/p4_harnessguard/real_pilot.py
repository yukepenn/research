"""P4 real-model regression pilot (subscription CLI, no API cost).

The deterministic Tier-0 proves the SELECTOR machinery on a controlled corpus. This
adds REAL evidence: drive an actual agent (Claude/Codex) on real multi-step tasks
under an OLD vs a NEW harness configuration (a harness edit), label paired pass->fail
regressions from the deterministic oracle, and show that an edit-conditioned canary
selector (rank tasks by old-harness trajectory length / risk) catches the planted
regressions at a small budget where random selection misses them.

We reuse the P1 stateful environments as the agent task suite (P4's unit is the
HARNESS EDIT, distinct from P1's interface transform — see program/overlap_matrix.md).
A harness edit here changes max_steps and/or a verification reminder in the system
prompt — levers that genuinely change a stochastic agent's success on long tasks.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field

from core.adapters.cli import CLIChatAdapter, cli_available
from core.experiment_registry.ledger import RunLedger, make_entry
from core.runner.loop import run_episode
from core.util import sha256_obj, short_id
from papers.p1_toolmorph.oracles.state_oracle import ORACLE_VERSION, task_passed
from papers.p1_toolmorph.tasks import SYSTEM_PROMPT, all_tasks

HARNESS = "p4_real_v1"

_VERIFY_SUFFIX = (" Before finishing, double-check the goal is actually satisfied by the "
                  "current state; if not, take another action.")


@dataclass(frozen=True)
class HarnessConfig:
    max_steps: int = 8
    verify_reminder: bool = True

    def system(self) -> str:
        return SYSTEM_PROMPT + (_VERIFY_SUFFIX if self.verify_reminder else "")

    def tag(self) -> str:
        return f"steps{self.max_steps}_verify{int(self.verify_reminder)}"


@dataclass(frozen=True)
class HarnessEdit:
    edit_id: str
    base: HarnessConfig
    new: HarnessConfig
    intent: str
    intended_effect: str  # improvement | neutral | harmful


def edit_corpus() -> list[HarnessEdit]:
    base = HarnessConfig(max_steps=8, verify_reminder=True)
    return [
        HarnessEdit("e_steps_cut", base, HarnessConfig(max_steps=2, verify_reminder=True),
                    "tighten the step budget to save cost", "harmful"),
        HarnessEdit("e_steps_trim_neutral", base, HarnessConfig(max_steps=7, verify_reminder=True),
                    "trivially reduce the step ceiling", "neutral"),
        HarnessEdit("e_verify_off", base, HarnessConfig(max_steps=8, verify_reminder=False),
                    "drop the verification reminder to shorten the prompt", "harmful"),
    ]


def run_under(model, task, config: HarnessConfig, *, seed=0):
    from papers.p1_toolmorph.metamorphic import present_tools
    env = task.env_factory()
    tools = present_tools(env, None)
    adapter = CLIChatAdapter(model, timeout=150)
    res = run_episode(adapter, env, system=config.system(), task_prompt=task.task_prompt,
                      tool_schemas=tools, max_steps=config.max_steps, seed=seed)
    n_calls = sum(1 for e in res.trajectory.events if e.type == "tool_call")
    return task_passed(res.final_state, task), n_calls, adapter.detected_model_id


@dataclass
class P4Outcome:
    model: str
    edit_id: str
    task_id: str
    old_pass: bool
    new_pass: bool
    regression: bool
    old_trace_len: int


def run_pilot(models, *, tasks=None, ledger_path: str, git_commit="uncommitted") -> dict:
    tasks = tasks if tasks is not None else all_tasks()
    edits = edit_corpus()
    ledger = RunLedger(ledger_path)
    rows: list[P4Outcome] = []

    for model in models:
        if not cli_available(model):
            continue
        # baseline (old harness) once per task -> reused as the trajectory fingerprint
        base_cfg = edits[0].base
        base = {}
        for t in tasks:
            ok, n, mid = run_under(model, t, base_cfg)
            base[t.task_id] = (ok, n, mid)
        for edit in edits:
            for t in tasks:
                old_pass, old_len, mid = base[t.task_id]
                new_pass, _new_len, _ = run_under(model, t, edit.new)
                reg = bool(old_pass and not new_pass)
                rows.append(P4Outcome(model, edit.edit_id, t.task_id, old_pass, new_pass,
                                      reg, old_len))
                th = ledger.store_trace({"edit": edit.edit_id, "task": t.task_id,
                                         "old_pass": old_pass, "new_pass": new_pass})
                ledger.append(make_entry(
                    run_id=short_id(model, edit.edit_id, t.task_id, HARNESS),
                    paper_id="p4_harnessguard", git_commit=git_commit,
                    task_hash=sha256_obj(t.task_id)[:12],
                    environment_hash=sha256_obj(edit.new.tag()),
                    model_provider="cli_subscription", model_id=f"{model}:{mid}",
                    harness_hash=HARNESS, oracle_version=ORACLE_VERSION, raw_trace_hash=th,
                    status="SUCCESS", cost_usd=0.0,
                    result={"edit": edit.edit_id, "intended_effect": edit.intended_effect,
                            "old_pass": old_pass, "new_pass": new_pass, "regression": reg,
                            "old_trace_len": old_len},
                    notes="P4 real-model regression pilot (subscription CLI)"))

    return _analyze(rows, tasks)


def _select_by_trace_len(rows_for_edit, k):
    ranked = sorted({r.task_id: r.old_trace_len for r in rows_for_edit}.items(),
                    key=lambda kv: -kv[1])
    return [tid for tid, _ in ranked[:k]]


def _analyze(rows, tasks) -> dict:
    edits = sorted({r.edit_id for r in rows})
    per_edit = {}
    recall = {"edit_conditioned": [], "random": []}
    import itertools
    task_ids = [t.task_id for t in tasks]
    for eid in edits:
        er = [r for r in rows if r.edit_id == eid]
        regset = {r.task_id for r in er if r.regression}
        per_edit[eid] = {"n_regressions": len(regset), "regressed_tasks": sorted(regset)}
        if not regset:
            continue
        k = 3
        sel = set(_select_by_trace_len(er, k))
        rc = len(sel & regset) / len(regset)
        # deterministic "random": average recall over all k-subsets is k/|tasks|
        rand = k / len(task_ids)
        recall["edit_conditioned"].append(rc)
        recall["random"].append(rand)
    summ = {m: (sum(v) / len(v) if v else None) for m, v in recall.items()}
    return {"per_edit": per_edit, "recall_at_k3": summ, "n_episodes": len(rows)}


if __name__ == "__main__":  # pragma: no cover
    import argparse
    import os
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", default="claude")
    ap.add_argument("--ledger", default="artifacts/run_ledger.jsonl")
    args = ap.parse_args()
    commit = os.popen("git rev-parse --short HEAD").read().strip() or "uncommitted"
    out = run_pilot(args.models.split(","), ledger_path=args.ledger, git_commit=commit)
    print(json.dumps({"per_edit": out["per_edit"], "recall_at_k3": out["recall_at_k3"]}, indent=2))
    print(f"episodes: {out['n_episodes']}")
