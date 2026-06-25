"""A tiny modular agent harness with parameterized components (P4-DATA-002).

The harness is a *configuration* of independently-editable components:

    retry_count, verifier_on/threshold, stopping_aggressiveness,
    context_truncation, memory_topk, tool_ordering

A task is run by a DETERMINISTIC simulated task-solver: given a HarnessConfig
and a task descriptor it returns a deterministic pass/fail and a structured
trace. Editing one component therefore changes outcomes in a *structured* way
(only the tasks that exercise / depend on that component move), which is exactly
the controlled corpus HarnessGuard needs to make the H2 measurement valid.

This module imports NO paper-specific task code (tasks are duck-typed: anything
with `.task_id`, `.capabilities`, `.required_components`) so it stays a generic
substrate and avoids circular imports.

NOTE: the simulated solver is NOT a scientific result. It is a deterministic
fixture that produces a controlled, structured regression signal for pipeline
validation (manual 11.1 / Tier-0).
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any

from core.util import sha256_obj

# The harness component ontology (manual 18.1 / P4-SPEC-001, restricted to the
# subset realised in the modular harness).
COMPONENTS = ["retry", "verifier", "stopping", "memory", "context", "tool_ordering"]

# Each component "owns" a capability tag; a task that needs the capability is
# sensitive to edits of that component.
COMPONENT_CAPABILITY = {
    "retry": "error_recovery",
    "verifier": "verification",
    "stopping": "long_horizon",
    "memory": "memory",
    "context": "long_context",
    "tool_ordering": "tool_ordering",
}

# Fixed tool universe; orderings are permutations of it. tool_ordering edits
# permute this list, moving a task's key tool earlier / later.
TOOL_UNIVERSE = [
    "read_file", "write_file", "run_tests", "search",
    "exec_cmd", "summarize", "fetch", "commit",
]

ORDERINGS: dict[str, list[str]] = {
    "default": list(TOOL_UNIVERSE),
    "alpha": sorted(TOOL_UNIVERSE),
    "reversed": list(reversed(TOOL_UNIVERSE)),
    "priority": ["run_tests", "exec_cmd", "read_file", "write_file",
                 "search", "commit", "summarize", "fetch"],
}

CONTEXT_MODES = ["none", "summary", "tail"]


@dataclass(frozen=True)
class HarnessConfig:
    """A point in harness-configuration space. Frozen so it can be hashed and
    so an edit always produces a *new* config rather than mutating in place."""
    retry_count: int = 2
    verifier_on: bool = True
    verifier_threshold: float = 0.5
    stopping_aggressiveness: float = 0.3
    context_truncation: str = "summary"
    memory_topk: int = 3
    tool_ordering: str = "default"

    def to_dict(self) -> dict:
        return asdict(self)

    def with_changes(self, **changes: Any) -> "HarnessConfig":
        bad = set(changes) - set(self.to_dict())
        if bad:
            raise ValueError(f"unknown harness fields: {sorted(bad)}")
        return HarnessConfig(**{**self.to_dict(), **changes})

    def harness_hash(self) -> str:
        return sha256_obj(self.to_dict())


def default_harness() -> HarnessConfig:
    return HarnessConfig()


def _req(task) -> dict:
    return getattr(task, "required_components", {}) or {}


def _tool_position(ordering: str, key_tool: str | None) -> int:
    order = ORDERINGS.get(ordering, ORDERINGS["default"])
    if key_tool is None or key_tool not in order:
        return 0
    return order.index(key_tool)


def run_task(config: HarnessConfig, task, *, seed: int = 0) -> tuple[bool, dict]:
    """Run one task under a harness configuration.

    Returns (passed, trace). The trace is the OLD-harness fingerprint source for
    feature extraction; it records how strongly the task exercises each
    component, NEVER any new-harness outcome.

    Pass logic: the task passes iff every component it depends on is provided
    adequately by the harness. Each requirement is a threshold; insensitive
    components default to always-satisfied.
    """
    req = _req(task)

    # ---- loads (how much the task exercises each component) ----------------
    retry_load = int(req.get("retry_load", req.get("min_retry", 0)))
    verify_load = int(req.get("verify_load", 0))
    memory_load = int(req.get("memory_load", req.get("min_memory", 0)))
    steps_load = int(req.get("steps_load", 1))
    context_load = int(req.get("context_load", 16))
    tool_calls = int(req.get("tool_calls", 2))
    key_tool = req.get("key_tool")

    n_retries = min(int(config.retry_count), retry_load)
    n_verification_actions = verify_load if (config.verifier_on and verify_load > 0) else 0
    memory_lookups = min(int(config.memory_topk), memory_load)
    key_tool_position = _tool_position(config.tool_ordering, key_tool)
    n_steps = 1 + steps_load + n_retries + (1 if n_verification_actions else 0)
    n_errors = retry_load

    # ---- component checks --------------------------------------------------
    ok = True

    # retry: need at least min_retry available; too many retries harms
    # non-idempotent tasks (retry_max).
    if not (int(config.retry_count) >= int(req.get("min_retry", 0))):
        ok = False
    if not (int(config.retry_count) <= int(req.get("retry_max", 99))):
        ok = False

    # verifier: verification-dependent tasks need it ON and not over-strict;
    # verifier-harmful (non-idempotent) tasks break when verification is added.
    if req.get("needs_verifier", False):
        if not (config.verifier_on
                and config.verifier_threshold <= float(req.get("verifier_threshold_max", 1.0))):
            ok = False
    if req.get("verifier_harmful", False) and config.verifier_on:
        ok = False

    # stopping: long-horizon tasks need un-aggressive stopping; early-stop
    # tasks need aggressive-enough stopping (irreversible-action guard).
    if not (float(req.get("stopping_min", 0.0)) <= config.stopping_aggressiveness
            <= float(req.get("stopping_max", 1.0))):
        ok = False

    # memory: retrieval depth band.
    if not (int(req.get("min_memory", 0)) <= int(config.memory_topk)
            <= int(req.get("memory_max", 99))):
        ok = False

    # context: long-context tasks fail under lossy truncation modes.
    allowed_ctx = req.get("context_allowed")
    if allowed_ctx is not None and config.context_truncation not in allowed_ctx:
        ok = False

    # tool ordering: key tool must appear early enough to be reached.
    if key_tool is not None and key_tool_position >= int(req.get("tool_pos_max", 99)):
        ok = False

    # optional, off-by-default stochastic flakiness (kept 0 for the controlled
    # corpus so regressions are structural & reproducible, not noise).
    flakiness = float(getattr(task, "flakiness", 0.0))
    if ok and flakiness > 0.0:
        from core.util import rng_for
        if rng_for(getattr(task, "task_id", "?"), config.harness_hash(), seed).random() < flakiness:
            ok = False

    trace = {
        "passed": bool(ok),
        "n_steps": int(n_steps),
        "n_retries": int(n_retries),
        "n_verification_actions": int(n_verification_actions),
        "memory_lookups": int(memory_lookups),
        "context_length": int(context_load),
        "n_tool_calls": int(tool_calls),
        "n_errors": int(n_errors),
        "key_tool_position": int(key_tool_position),
        "key_tool": key_tool,
    }
    return bool(ok), trace


# Mapping from a component to the trace signal that measures how strongly a task
# exercises it (used by feature extraction to build the OOD-generalizing
# component-match feature without peeking at the new harness).
COMPONENT_TRACE_SIGNAL = {
    "retry": "n_retries",
    "verifier": "n_verification_actions",
    "stopping": "n_steps",
    "memory": "memory_lookups",
    "context": "context_length",
    "tool_ordering": "n_tool_calls",
}
