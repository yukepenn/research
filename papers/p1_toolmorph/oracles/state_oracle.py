"""Deterministic final-state oracle (P1-ORACLE-001, manual 5.6).

Scores an episode by the INVARIANT predicate attached to the task, evaluated on
the environment's hidden final state — never by matching a fixed trajectory.
The oracle is versioned (its hash) so the ledger records exactly which oracle
produced a result.
"""
from __future__ import annotations

from core.util import sha256_obj

ORACLE_VERSION = "p1_state_oracle_v1"


def task_passed(final_state: dict, task) -> bool:
    try:
        return bool(task.goal(final_state))
    except Exception:
        return False


def reference_solution_passes(task) -> bool:
    """Run the task's reference plan canonically and confirm the oracle accepts
    it. Proves solvability + oracle correctness (no false negatives)."""
    env = task.env_factory()
    env.reset()
    tools = {t.name: t for t in env.tools()}
    for tool_name, args in task.plan:
        tools[tool_name].executor(args)
    return task_passed(env.final_state(), task)


def empty_state_fails(task) -> bool:
    """A do-nothing agent must FAIL the task (guards against trivial-pass bugs)."""
    env = task.env_factory()
    env.reset()
    return not task_passed(env.final_state(), task)


def oracle_fingerprint(tasks) -> str:
    return sha256_obj({"version": ORACLE_VERSION,
                       "tasks": sorted(t.task_id for t in tasks)})
