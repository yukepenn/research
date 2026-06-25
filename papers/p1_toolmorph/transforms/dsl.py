"""ToolMorph transformation DSL (P1-DSL-001).

A Transform produces a model-visible *view* of a canonical tool. It may change
the tool name, schema, request encoding, response encoding, and error encoding,
but the underlying executor — and therefore the environment STATE TRANSITION —
is identical. This is the formal backbone of the paper (manual 5.4):

    T1(s, encode_I1(a)) == T2(s, encode_I2(a))

`apply_transform(tool, transform)` returns a new ToolSpec whose executor is
    view_args -> encode_response( original_executor( decode_request(view_args) ) )
so feeding it `encode_request(canonical_args)` reproduces the exact canonical
call. The property-test harness verifies request/response/error round-trips and
byte-identical post-call snapshots; any nonzero mismatch is a BENCHMARK BUG to
fix, never a model error (manual 5.7).
"""
from __future__ import annotations

from core.adapters.base import ToolSpec


class EquivalenceError(Exception):
    """Raised by an executor view when a transform cannot map a call back."""


class Transform:
    family: str = "identity"
    strict: bool = True

    def __init__(self, transform_id: str | None = None):
        self.id = transform_id or self.family

    # ctx lets a transform precompute per-tool maps (e.g. enum codes)
    def prepare(self, schema: dict) -> dict:
        return {}

    def view_name(self, name: str, ctx: dict) -> str:
        return name

    def view_description(self, desc: str, ctx: dict) -> str:
        return desc

    def view_schema(self, schema: dict, ctx: dict) -> dict:
        return schema

    # request channel: canonical <-> view
    def encode_request(self, args: dict, ctx: dict) -> dict:
        return args

    def decode_request(self, args: dict, ctx: dict) -> dict:
        return args

    # response channel: canonical <-> view
    def encode_response(self, result, ctx: dict):
        return result

    def decode_response(self, result, ctx: dict):
        return result

    # error channel: canonical <-> view
    def encode_error(self, msg: str, ctx: dict) -> str:
        return msg

    def decode_error(self, msg: str, ctx: dict) -> str:
        return msg


def error_category(msg: str) -> str:
    """The canonical error category is the token before the first colon."""
    return str(msg).split(":", 1)[0].strip()


def apply_transform(tool: ToolSpec, transform: Transform) -> ToolSpec:
    """Return the model-visible transformed tool. The executor maps a view call
    back to canonical, runs the real executor, and re-encodes the response."""
    ctx = transform.prepare(tool.schema)

    def _executor(view_args: dict):
        canonical = transform.decode_request(view_args, ctx)
        if tool.executor is None:
            raise EquivalenceError(f"tool {tool.name} has no executor")
        try:
            result = tool.executor(canonical)
        except Exception as exc:  # re-encode the error surface, keep the class
            raise type(exc)(transform.encode_error(str(exc), ctx)) from None
        return transform.encode_response(result, ctx)

    return ToolSpec(
        name=transform.view_name(tool.name, ctx),
        description=transform.view_description(tool.description, ctx),
        schema=transform.view_schema(tool.schema, ctx),
        executor=_executor,
    )
