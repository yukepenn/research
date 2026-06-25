"""Unified agent tool-use loop (COMMON-004 harness, manual 5.9 / 6.5 / 10.x).

ONE harness for every model. Swapping the model swaps the adapter only; the
instruction, task text, tool ordering, and loop are identical, so effects are
attributable to the model — not a product harness. The loop records a full
trajectory and aggregate usage for the ledger.

This is provider-free and runs entirely against the deterministic mock in
Tier-0; real models drop in via the budget-gated registry.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

from core.adapters.base import Message, ModelAdapter, ToolSpec, Usage
from core.environments.base import Environment, apply_executor
from core.tracing.events import Trajectory


@dataclass
class EpisodeResult:
    status: str  # SUCCESS | AGENT_FAILURE | TIMEOUT | REFUSAL | INFRA_FAILURE
    n_steps: int
    final_state: dict
    trajectory: Trajectory
    usage: Usage
    final_text: str = ""
    error: str | None = None
    meta: dict = field(default_factory=dict)


def run_episode(
    adapter: ModelAdapter,
    env: Environment,
    *,
    system: str,
    task_prompt: str,
    max_steps: int = 12,
    tool_schemas: Sequence[ToolSpec] | None = None,
    seed: int = 0,
) -> EpisodeResult:
    """Run one tool-use episode.

    `tool_schemas` lets ToolMorph present MUTATED (model-visible) schemas while
    the executors still come from `env` — the harness maps a model tool call
    back through whatever codec the provided schema implies (executors here are
    expected to already be the equivalence-preserving ones bound by the env or
    a transform wrapper).
    """
    env.reset(seed=seed)
    tools = list(tool_schemas if tool_schemas is not None else env.tools())
    traj = Trajectory()
    usage = Usage()
    messages = [Message("system", system), Message("user", task_prompt)]

    status = "AGENT_FAILURE"
    final_text = ""
    error = None

    for step in range(max_steps):
        resp = adapter.timed_generate(messages, tools)
        usage.input_tokens += resp.usage.input_tokens
        usage.output_tokens += resp.usage.output_tokens
        usage.cost_usd += resp.usage.cost_usd
        usage.latency_seconds += resp.usage.latency_seconds
        traj.record(step, "model_call", {
            "text": resp.text,
            "tool_calls": [{"name": tc.name, "arguments": tc.arguments}
                           for tc in resp.tool_calls],
            "latency_seconds": resp.usage.latency_seconds,
        })

        if resp.finish_reason == "refusal":
            status, final_text = "REFUSAL", resp.text
            traj.record(step, "final", {"reason": "refusal"})
            break

        if not resp.tool_calls:
            status, final_text = "SUCCESS", resp.text
            traj.record(step, "final", {"text": resp.text})
            break

        messages.append(Message("assistant", resp.text or ""))
        for tc in resp.tool_calls:
            traj.record(step, "tool_call", {"name": tc.name, "arguments": tc.arguments})
            try:
                result = apply_executor(env, tc.name, tc.arguments)
                payload = {"name": tc.name, "ok": True, "result": result}
            except Exception as exc:  # noqa: BLE001 - record, don't crash the loop
                payload = {"name": tc.name, "ok": False, "error": str(exc)}
                error = str(exc)
            traj.record(step, "tool_result", payload)
            messages.append(Message("tool", str(payload.get("result", payload.get("error"))),
                                    tool_call_id=tc.call_id, name=tc.name))
    else:
        status = "TIMEOUT"
        traj.record(max_steps, "final", {"reason": "max_steps"})

    return EpisodeResult(
        status=status,
        n_steps=len([e for e in traj.events if e.type == "model_call"]),
        final_state=env.final_state(),
        trajectory=traj,
        usage=usage,
        final_text=final_text,
        error=error,
        meta={"environment_hash": env.environment_hash()},
    )
