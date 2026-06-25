"""Provider-agnostic model adapter interface (COMMON-003).

The agent harness only ever talks to a `ModelAdapter`. Swapping the underlying
model means swapping the adapter, never the harness (manual 5.9, 6.5: "unified
agent harness, only replace the base model"). This is what lets us attribute
effects to the model family rather than to a product harness.

A `Usage` record is attached to every response so token/cost/latency land in
the run ledger.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Callable, Sequence


@dataclass(frozen=True)
class Message:
    role: str  # "system" | "user" | "assistant" | "tool"
    content: str
    tool_call_id: str | None = None
    name: str | None = None


@dataclass(frozen=True)
class ToolSpec:
    """A tool exposed to the model. `schema` is the model-visible JSON schema.

    ToolMorph mutates exactly this schema while keeping the bound `executor`'s
    underlying state transition identical.
    """
    name: str
    description: str
    schema: dict
    executor: Callable[[dict], Any] | None = None


@dataclass(frozen=True)
class ToolCall:
    name: str
    arguments: dict
    call_id: str


@dataclass
class Usage:
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    latency_seconds: float = 0.0


@dataclass
class ModelResponse:
    text: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)
    usage: Usage = field(default_factory=Usage)
    raw: Any = None
    finish_reason: str = "stop"


class ModelAdapter:
    """Abstract base. Implementations: DeterministicMockAdapter (Tier-0),
    real providers (gated behind credentials + budget)."""

    provider: str = "abstract"

    def __init__(self, model_id: str, *, temperature: float = 0.0,
                 max_tokens: int = 2048, snapshot_date: str | None = None):
        self.model_id = model_id
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.snapshot_date = snapshot_date

    def generate(self, messages: Sequence[Message],
                 tools: Sequence[ToolSpec] | None = None,
                 **params: Any) -> ModelResponse:
        raise NotImplementedError

    # convenience: time a generate() call and stamp latency
    def timed_generate(self, messages, tools=None, **params) -> ModelResponse:
        t0 = time.perf_counter()
        resp = self.generate(messages, tools, **params)
        resp.usage.latency_seconds = round(time.perf_counter() - t0, 6)
        return resp

    def identity(self) -> dict:
        return {
            "provider": self.provider,
            "model_id": self.model_id,
            "snapshot_date": self.snapshot_date,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
