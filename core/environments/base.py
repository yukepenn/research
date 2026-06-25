"""Stateful environment protocol shared by ToolMorph (P1) and HarnessGuard (P4).

An Environment owns hidden authoritative state, exposes a set of tools (bound
executors) to the agent, can reset deterministically, and can report its final
state for a deterministic oracle (manual 5.6, 15.2). ToolMorph mutates only the
*model-visible schema* of these tools while keeping the bound executor's state
transition identical — that is the whole point of state-transition equivalence.
"""
from __future__ import annotations

from typing import Any, Sequence

from core.adapters.base import ToolSpec
from core.util import sha256_obj


class Environment:
    name: str = "abstract"
    version: str = "0"

    def reset(self, seed: int = 0) -> None:
        """Deterministically reset hidden state."""
        raise NotImplementedError

    def snapshot(self) -> dict:
        """Full hidden state as a JSON-serialisable dict."""
        raise NotImplementedError

    def tools(self) -> Sequence[ToolSpec]:
        """Tools exposed to the agent, with bound executors."""
        raise NotImplementedError

    def transaction_log(self) -> list[dict]:
        return getattr(self, "_log", [])

    def environment_hash(self) -> str:
        """Identity of the environment + its current schema surface."""
        return sha256_obj({
            "name": self.name,
            "version": self.version,
            "tool_schemas": [{"name": t.name, "schema": t.schema}
                             for t in self.tools()],
        })

    def final_state(self) -> dict:
        return self.snapshot()


def apply_executor(env: Environment, tool_name: str, args: dict) -> Any:
    """Locate a tool by name and run its executor against the env."""
    for t in env.tools():
        if t.name == tool_name:
            if t.executor is None:
                raise ValueError(f"tool {tool_name} has no executor")
            return t.executor(args)
    raise KeyError(f"no such tool: {tool_name}")
