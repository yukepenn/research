"""Deterministic mock adapter (Tier-0).

Lets us build and test the runner, oracles, environments, transformation DSL,
and the whole pipeline with zero paid API calls and perfect reproducibility.
The manual mandates exhausting Tier-0 engineering bugs before spending on
models (11.1).

Two usage modes:
- scripted: hand it a list of ModelResponses (or a policy callable) to drive an
  exact agent trajectory in tests.
- echo: with no policy, returns a deterministic textual response keyed by a
  hash of the conversation, useful for plumbing tests.
"""
from __future__ import annotations

from typing import Callable, Sequence

from core.adapters.base import Message, ModelAdapter, ModelResponse, ToolSpec, Usage
from core.adapters.tokens import estimate_tokens_obj, estimate_tokens_text

Policy = Callable[[Sequence[Message], Sequence[ToolSpec]], ModelResponse]


class DeterministicMockAdapter(ModelAdapter):
    provider = "mock"

    def __init__(self, model_id: str = "mock-1", *, policy: Policy | None = None,
                 cost_per_mtok_in: float = 0.0, cost_per_mtok_out: float = 0.0,
                 **kw):
        super().__init__(model_id, **kw)
        self._policy = policy
        self.cost_per_mtok_in = cost_per_mtok_in
        self.cost_per_mtok_out = cost_per_mtok_out

    def generate(self, messages, tools=None, **params) -> ModelResponse:
        tools = list(tools or [])
        messages = list(messages)
        if self._policy is not None:
            resp = self._policy(messages, tools)
        else:
            convo = "\n".join(f"{m.role}:{m.content}" for m in messages)
            resp = ModelResponse(text=f"[mock:{self.model_id}] ack({len(convo)} chars)")
        # stamp deterministic usage/cost
        in_tok = sum(estimate_tokens_text(m.content) for m in messages)
        in_tok += sum(estimate_tokens_obj(t.schema) for t in tools)
        out_tok = estimate_tokens_text(resp.text) + sum(
            estimate_tokens_obj(tc.arguments) for tc in resp.tool_calls
        )
        cost = (in_tok / 1e6) * self.cost_per_mtok_in + (out_tok / 1e6) * self.cost_per_mtok_out
        resp.usage = Usage(input_tokens=in_tok, output_tokens=out_tok, cost_usd=round(cost, 8))
        return resp


def scripted_policy(steps: Sequence[ModelResponse]) -> Policy:
    """Return a policy that yields the given responses in order, repeating the
    last one once exhausted. Lets a test script an exact agent trajectory."""
    state = {"i": 0}

    def _policy(messages, tools) -> ModelResponse:
        i = min(state["i"], len(steps) - 1)
        state["i"] += 1
        s = steps[i]
        # return a shallow copy so usage stamping doesn't mutate the script
        return ModelResponse(text=s.text, tool_calls=list(s.tool_calls),
                             finish_reason=s.finish_reason, raw=s.raw)

    return _policy
