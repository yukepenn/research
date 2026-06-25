"""Trajectory event schema and hashing.

The manual requires preserving the full raw trace and a stable hash of it
(1.1, 3.1). We separate:
- the *full* trace (with timestamps/latency) -> stored content-addressed,
- a *structural fingerprint* that excludes volatile wall-clock fields, so two
  deterministic reruns of the same episode produce the SAME fingerprint. This
  is what the Independent Reproducer compares (manual 23).
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from core.util import sha256_obj, utc_now_iso


@dataclass
class Event:
    step: int
    type: str  # model_call | tool_call | tool_result | error | final
    payload: dict
    at: str = field(default_factory=utc_now_iso)

    def structural(self) -> dict:
        """Volatile-free view for reproducible hashing."""
        return {"step": self.step, "type": self.type,
                "payload": _strip_volatile(self.payload)}


_VOLATILE_KEYS = {"latency_seconds", "at", "cost_usd", "input_tokens",
                  "output_tokens", "wall_clock"}


def _strip_volatile(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: _strip_volatile(v) for k, v in obj.items()
                if k not in _VOLATILE_KEYS}
    if isinstance(obj, list):
        return [_strip_volatile(v) for v in obj]
    return obj


@dataclass
class Trajectory:
    events: list[Event] = field(default_factory=list)

    def record(self, step: int, type: str, payload: dict) -> None:
        self.events.append(Event(step=step, type=type, payload=payload))

    def to_dict(self) -> dict:
        return {"events": [asdict(e) for e in self.events]}

    def structural_fingerprint(self) -> str:
        return sha256_obj([e.structural() for e in self.events])
