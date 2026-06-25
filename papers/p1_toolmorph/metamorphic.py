"""Metamorphic paired evaluation harness (manual 5.5, 5.13).

Runs the SAME task, same initial state, same agent under the original interface
and under a state-transition-equivalent transform, and measures the paired
success difference with a task-clustered bootstrap. This is the measurement
machinery the real-model pilot/full-study plug into; in Tier-0 it is validated
with deterministic simulated agents (sim_agents.py).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from core.adapters.base import ModelAdapter
from core.runner.loop import run_episode
from core.statistics.resampling import Interval, paired_cluster_bootstrap_diff
from papers.p1_toolmorph.oracles.state_oracle import task_passed
from papers.p1_toolmorph.tasks import SYSTEM_PROMPT
from papers.p1_toolmorph.transforms.dsl import apply_transform


def present_tools(env, transform=None):
    base = list(env.tools())
    if transform is None:
        return base
    return [apply_transform(t, transform) for t in base]


def run_task(adapter: ModelAdapter, task, transform=None, *, max_steps: int = 12, seed: int = 0):
    env = task.env_factory()
    tools = present_tools(env, transform)
    res = run_episode(adapter, env, system=SYSTEM_PROMPT, task_prompt=task.task_prompt,
                      tool_schemas=tools, max_steps=max_steps, seed=seed)
    return res, task_passed(res.final_state, task)


@dataclass
class DegradationResult:
    transform: str
    ci: Interval
    n: int
    orig_success_rate: float
    mut_success_rate: float
    per_task: list[dict]


def paired_degradation(
    agent_for: Callable[[object, object], ModelAdapter],
    tasks,
    transform,
    *,
    repeats: int = 1,
    n_boot: int = 2000,
    seed: int = 0,
) -> DegradationResult:
    """`agent_for(task, transform_or_None)` returns the adapter to use.

    Returns mean(mutated) - mean(original) with a task-clustered CI; negative
    means the transform degraded success.
    """
    a, b, clusters, per_task = [], [], [], []
    for task in tasks:
        for r in range(repeats):
            _, p_orig = run_task(agent_for(task, None), task, None, seed=seed + r)
            _, p_mut = run_task(agent_for(task, transform), task, transform, seed=seed + r)
            a.append(float(p_orig)); b.append(float(p_mut)); clusters.append(task.task_id)
            per_task.append({"task": task.task_id, "orig": p_orig, "mut": p_mut})
    ci = paired_cluster_bootstrap_diff(a, b, clusters, n_boot=n_boot, seed=seed)
    return DegradationResult(
        transform=getattr(transform, "family", "identity"), ci=ci, n=len(a),
        orig_success_rate=sum(a) / len(a), mut_success_rate=sum(b) / len(b),
        per_task=per_task)
