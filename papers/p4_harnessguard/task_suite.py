"""HarnessGuard task suite (P4-TASK-001, manual 8.7).

>=20 task descriptors whose pass/fail depends on harness components, so that an
edit to a component induces a *structured* regression set. Each descriptor
carries capabilities, required_components (the component demands the simulated
solver checks), risk_tags, and a deterministic baseline trace under the default
harness.

Tasks span two families (coding/terminal and stateful workspace) and the full
component ontology, so leave-one-task-family-out / component-out splits are
meaningful. Insensitive components default to always-satisfied, so each task is
sensitive to only one or two components (structured, not uniform, regressions).
"""
from __future__ import annotations

from dataclasses import dataclass, field

from papers.p4_harnessguard.modular_harness import default_harness, run_task

CAPABILITY_VOCAB = [
    "error_recovery", "verification", "long_horizon", "memory",
    "long_context", "tool_ordering", "multi_tool",
]

RISK_TAG_VOCAB = [
    "non_idempotent", "irreversible", "context_loss", "early_termination",
    "memory_overflow", "distraction", "slow", "tool_sensitive",
]

# risk tags that make a regression DANGEROUS (frozen pre-ground-truth).
HIGH_RISK_TAGS = {"irreversible", "non_idempotent"}


@dataclass
class TaskDescriptor:
    task_id: str
    family: str
    capabilities: list[str]
    required_components: dict
    risk_tags: list[str] = field(default_factory=list)
    historical_failure_modes: list[str] = field(default_factory=list)
    cost: float = 1.0
    flakiness: float = 0.0

    @property
    def key_tool(self):
        return self.required_components.get("key_tool")

    def is_high_risk(self) -> bool:
        return bool(set(self.risk_tags) & HIGH_RISK_TAGS)


def baseline_trace(task: TaskDescriptor) -> dict:
    """Deterministic OLD-harness fingerprint under the DEFAULT harness."""
    _, trace = run_task(default_harness(), task)
    return trace


def trajectory_length_baseline(task: TaskDescriptor) -> int:
    return baseline_trace(task)["n_steps"]


# --------------------------------------------------------------------------
# Builders (one component sensitivity each, occasionally a secondary).
# --------------------------------------------------------------------------
def _retry_need(i, min_retry):
    return TaskDescriptor(
        task_id=f"coding_recover_{i}", family="coding",
        capabilities=["error_recovery", "multi_tool"],
        required_components={"min_retry": min_retry, "retry_load": min_retry,
                             "steps_load": 3, "tool_calls": 4, "key_tool": "exec_cmd"},
        risk_tags=["slow"],
        historical_failure_modes=["transient_tool_error"])


def _retry_harmful(i, irreversible):
    return TaskDescriptor(
        task_id=f"workspace_nonidem_{i}", family="workspace",
        capabilities=["error_recovery"],
        # retry_max=3: a 2->3 edit is safe, a 2->5 edit duplicates a
        # non-idempotent action and breaks the task.
        required_components={"retry_max": 3, "retry_load": 2, "steps_load": 2,
                             "tool_calls": 3, "key_tool": "write_file"},
        risk_tags=["non_idempotent"] + (["irreversible"] if irreversible else []),
        historical_failure_modes=["double_write"])


def _verifier_need(i):
    return TaskDescriptor(
        task_id=f"coding_verify_{i}", family="coding",
        capabilities=["verification", "multi_tool"],
        required_components={"needs_verifier": True, "verifier_threshold_max": 0.8,
                             "verify_load": 1, "steps_load": 2, "tool_calls": 3,
                             "key_tool": "run_tests"},
        risk_tags=["slow"],
        historical_failure_modes=["unchecked_output"])


def _verifier_harmful(i, irreversible):
    return TaskDescriptor(
        task_id=f"workspace_verifyharm_{i}", family="workspace",
        capabilities=["verification"],
        # passes only when verification is OFF: adding a read-after-write
        # verification step double-acts on a non-idempotent resource.
        required_components={"verifier_harmful": True, "steps_load": 2,
                             "tool_calls": 3, "key_tool": "commit"},
        risk_tags=["non_idempotent"] + (["irreversible"] if irreversible else []),
        historical_failure_modes=["verify_side_effect"])


def _stopping_long(i):
    return TaskDescriptor(
        task_id=f"coding_longhorizon_{i}", family="coding",
        capabilities=["long_horizon", "multi_tool"],
        required_components={"stopping_max": 0.5, "steps_load": 5, "tool_calls": 5,
                             "key_tool": "search"},
        risk_tags=["slow"],
        historical_failure_modes=["premature_stop"])


def _stopping_early(i):
    return TaskDescriptor(
        task_id=f"workspace_earlystop_{i}", family="workspace",
        capabilities=["long_horizon"],
        # needs aggressive-enough stopping; running too long triggers an
        # irreversible follow-on action.
        required_components={"stopping_min": 0.2, "steps_load": 2, "tool_calls": 3,
                             "key_tool": "exec_cmd"},
        risk_tags=["irreversible", "early_termination"],
        historical_failure_modes=["overrun_irreversible"])


def _memory_need(i, min_memory):
    return TaskDescriptor(
        task_id=f"workspace_memory_{i}", family="workspace",
        capabilities=["memory"],
        required_components={"min_memory": min_memory, "memory_load": min_memory,
                             "steps_load": 2, "tool_calls": 3, "key_tool": "fetch"},
        risk_tags=["context_loss"],
        historical_failure_modes=["forgot_constraint"])


def _memory_harmful(i):
    return TaskDescriptor(
        task_id=f"coding_memharm_{i}", family="coding",
        capabilities=["memory"],
        # too-deep retrieval injects distracting context and breaks the task.
        required_components={"memory_max": 5, "memory_load": 3, "steps_load": 2,
                             "tool_calls": 3, "key_tool": "search"},
        risk_tags=["distraction", "memory_overflow"],
        historical_failure_modes=["context_distraction"])


def _context_long(i):
    return TaskDescriptor(
        task_id=f"coding_longctx_{i}", family="coding",
        capabilities=["long_context", "multi_tool"],
        # tail-truncation loses required detail; summary/none preserve it.
        required_components={"context_allowed": ["none", "summary"],
                             "context_load": 80, "steps_load": 3, "tool_calls": 4,
                             "key_tool": "read_file"},
        risk_tags=["context_loss"],
        historical_failure_modes=["truncated_spec"])


def _tool_order(i, key_tool):
    return TaskDescriptor(
        task_id=f"workspace_toolorder_{i}", family="workspace",
        capabilities=["tool_ordering", "multi_tool"],
        # key tool must be exposed within the first 3 positions.
        required_components={"tool_pos_max": 3, "key_tool": key_tool,
                             "steps_load": 2, "tool_calls": 5},
        risk_tags=["tool_sensitive"],
        historical_failure_modes=["tool_not_found_early"])


def all_tasks() -> list[TaskDescriptor]:
    tasks: list[TaskDescriptor] = []
    tasks += [_retry_need(i, mr) for i, mr in enumerate([1, 2, 1, 2], start=1)]
    tasks += [_retry_harmful(1, irreversible=True), _retry_harmful(2, irreversible=False)]
    tasks += [_verifier_need(i) for i in range(1, 5)]
    tasks += [_verifier_harmful(1, irreversible=True), _verifier_harmful(2, irreversible=False)]
    tasks += [_stopping_long(i) for i in range(1, 4)]
    tasks += [_stopping_early(1), _stopping_early(2)]
    tasks += [_memory_need(i, mm) for i, mm in enumerate([2, 3, 2], start=1)]
    tasks += [_memory_harmful(1), _memory_harmful(2)]
    tasks += [_context_long(1), _context_long(2)]
    tasks += [_tool_order(i, kt) for i, kt in
              enumerate(["read_file", "write_file", "run_tests"], start=1)]
    return tasks


def tasks_by_family() -> dict[str, list[TaskDescriptor]]:
    out: dict[str, list[TaskDescriptor]] = {}
    for t in all_tasks():
        out.setdefault(t.family, []).append(t)
    return out
