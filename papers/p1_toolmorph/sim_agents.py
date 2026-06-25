"""Deterministic SIMULATED agents for Tier-0 pipeline validation only.

These are NOT scientific results. They validate that the metamorphic harness +
oracle + statistics behave correctly before any paid model is called:

- codec_adapter: an interface-robust oracle agent that always issues the correct
  call through whatever interface is presented -> the NEGATIVE CONTROL. If the
  harness/transforms inject any artifact, this agent would show degradation; it
  must not (manual 14.6 negative control).
- flaky_adapter: succeeds with a fixed probability, used to confirm the paired
  cluster bootstrap recovers a PLANTED degradation.
"""
from __future__ import annotations

from core.adapters.base import ModelResponse, ToolCall
from core.adapters.mock import DeterministicMockAdapter
from core.util import rng_for


def _codec_calls(task, transform):
    env = task.env_factory(); env.reset()
    canon = {t.name: t for t in env.tools()}
    calls = []
    for i, (tname, args) in enumerate(task.plan):
        if transform is None:
            calls.append(ToolCall(tname, dict(args), f"c{i}"))
        else:
            ctx = transform.prepare(canon[tname].schema)
            calls.append(ToolCall(transform.view_name(tname, ctx),
                                  transform.encode_request(dict(args), ctx), f"c{i}"))
    return calls


def codec_adapter(task, transform) -> DeterministicMockAdapter:
    """Negative control: emits the reference plan mapped through the presented
    interface (one call per step, then finishes)."""
    calls = _codec_calls(task, transform)
    state = {"i": 0}

    def policy(messages, tools):
        i = state["i"]; state["i"] += 1
        if i < len(calls):
            return ModelResponse(tool_calls=[calls[i]])
        return ModelResponse(text="done", finish_reason="stop")

    return DeterministicMockAdapter(policy=policy)


def flaky_adapter(task, transform, *, p_success: float) -> DeterministicMockAdapter:
    """Solves correctly with probability p_success (seeded by task+transform),
    otherwise gives up immediately. Used to plant a known degradation."""
    fam = getattr(transform, "family", "identity")
    succeed = rng_for(task.task_id, fam, "flaky").random() < p_success
    if succeed:
        return codec_adapter(task, transform)

    def policy(messages, tools):
        return ModelResponse(text="I cannot complete this.", finish_reason="stop")

    return DeterministicMockAdapter(policy=policy)
