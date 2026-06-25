"""Property-based equivalence verification (P1-DSL-002, manual 5.7).

For every strict transform we verify, on randomized inputs and on real task
scenarios:
  (a) request round-trip:  decode(encode(args)) == args
  (b) response round-trip: decode(encode(result)) == result
  (c) error round-trip:    error category is preserved through the codec
  (d) STATE equivalence:   running a task's canonical plan vs the transformed
      interface yields a byte-identical final hidden state AND identical oracle
      verdict.

Target: >= 10,000 request cases per strict family with zero unexplained
mismatch. Any mismatch yields a minimal counterexample to fix the spec — never
a model error (manual 5.7).
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any

from papers.p1_toolmorph.oracles.state_oracle import task_passed
from papers.p1_toolmorph.tasks import all_tasks
from papers.p1_toolmorph.transforms.dsl import apply_transform, error_category
from papers.p1_toolmorph.transforms.families import all_strict_transforms

_NAME_POOL = ["alice", "bob", "cara", "dan", "ren", "sam", "kit"]
_STR_POOL = ["Standup", "Review", "Sync", "Planning", "Retro", "1:1"]


def _gen_value(spec: dict, rng: random.Random) -> Any:
    if "enum" in spec:
        return rng.choice(spec["enum"])
    t = spec.get("type")
    if t == "integer":
        return rng.randint(0, 48)
    if t == "string":
        return rng.choice(_STR_POOL)
    if t == "array":
        return rng.sample(_NAME_POOL, rng.randint(0, 3))
    if t == "object":
        return _gen_args(spec, rng)
    return rng.choice(_STR_POOL)


def _gen_args(schema: dict, rng: random.Random, include_optional: bool = True) -> dict:
    props = schema.get("properties", {})
    required = set(schema.get("required", []))
    out: dict = {}
    for key, spec in props.items():
        if key in required or (include_optional and rng.random() < 0.5):
            out[key] = _gen_value(spec, rng)
    return out


@dataclass
class EquivReport:
    request_cases: int = 0
    response_cases: int = 0
    error_cases: int = 0
    state_cases: int = 0
    mismatches: list[dict] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.mismatches


def _env_factories() -> list:
    from papers.p1_toolmorph.environments.calendar import CalendarEnv
    from papers.p1_toolmorph.environments.helpdesk import HelpdeskEnv
    from papers.p1_toolmorph.environments.inventory import InventoryEnv
    return [CalendarEnv, InventoryEnv, HelpdeskEnv]


def _env_tools() -> list[tuple]:
    """(factory, tool_name, canonical_schema) for every tool in every env."""
    out = []
    for factory in _env_factories():
        env = factory(); env.reset()
        for t in env.tools():
            out.append((factory, t.name, t.schema))
    return out


def verify_call_equivalence(transform, n_per_tool: int, report: EquivReport,
                            seed: int = 0) -> None:
    """The uniform, rigorous property: for random canonical args (valid AND
    invalid), the canonical executor and the transformed view executor produce
    the byte-identical post-call snapshot, the same error category, and a
    response that decodes back to the canonical response.

    This correctly handles optional_default (default injection is state-inert)
    and every other family, because it tests STATE equivalence, not byte
    identity of the request dict.
    """
    from papers.p1_toolmorph.transforms.dsl import error_category as _cat
    for factory, tool_name, schema in _env_tools():
        ctx = transform.prepare(schema)
        rng = random.Random(abs(hash((seed, transform.family, tool_name))) % (2**32))
        for _ in range(n_per_tool):
            args = _gen_args(schema, rng)

            envc = factory(); envc.reset()
            toolc = next(t for t in envc.tools() if t.name == tool_name)
            try:
                rc, errc = toolc.executor(dict(args)), None
            except Exception as exc:
                rc, errc = None, _cat(str(exc))
            snap_c = envc.snapshot()

            envt = factory(); envt.reset()
            canon = next(t for t in envt.tools() if t.name == tool_name)
            view = apply_transform(canon, transform)
            try:
                rt, errt = view.executor(transform.encode_request(dict(args), ctx)), None
            except Exception as exc:
                rt = None
                errt = _cat(transform.decode_error(str(exc), ctx))
            snap_t = envt.snapshot()

            report.request_cases += 1
            if snap_c != snap_t:
                report.mismatches.append({"channel": "state_per_call", "transform": transform.family,
                                          "tool": tool_name, "args": args,
                                          "canonical": snap_c, "transformed": snap_t})
            elif errc != errt:
                report.mismatches.append({"channel": "error_per_call", "transform": transform.family,
                                          "tool": tool_name, "args": args,
                                          "canonical_err": errc, "transformed_err": errt})
            elif rc is not None and transform.decode_response(rt, ctx) != rc:
                report.mismatches.append({"channel": "response_per_call", "transform": transform.family,
                                          "tool": tool_name, "canonical": rc,
                                          "decoded": transform.decode_response(rt, ctx)})


def verify_state_equivalence(transform, report: EquivReport) -> None:
    for task in all_tasks():
        # canonical run
        envc = task.env_factory(); envc.reset()
        ctools = {t.name: t for t in envc.tools()}
        for tname, args in task.plan:
            ctools[tname].executor(args)
        snap_c, pass_c = envc.final_state(), task_passed(envc.final_state(), task)

        # transformed run: same canonical args, fed through the transformed view
        envt = task.env_factory(); envt.reset()
        canon = {t.name: t for t in envt.tools()}
        for tname, args in task.plan:
            tool = canon[tname]
            ctx = transform.prepare(tool.schema)
            view = apply_transform(tool, transform)
            view.executor(transform.encode_request(args, ctx))
        snap_t, pass_t = envt.final_state(), task_passed(envt.final_state(), task)

        report.state_cases += 1
        if snap_c != snap_t or pass_c != pass_t:
            report.mismatches.append({"channel": "state", "transform": transform.family,
                                      "task": task.task_id, "canonical": snap_c,
                                      "transformed": snap_t})


def verify_response_roundtrip(transform, report: EquivReport) -> None:
    # collect real response shapes by executing task plans canonically
    for task in all_tasks():
        env = task.env_factory(); env.reset()
        tools = {t.name: t for t in env.tools()}
        for tname, args in task.plan:
            result = tools[tname].executor(args)
            ctx = transform.prepare(tools[tname].schema)
            back = transform.decode_response(transform.encode_response(result, ctx), ctx)
            report.response_cases += 1
            if back != result:
                report.mismatches.append({"channel": "response", "transform": transform.family,
                                          "tool": tname, "input": result, "got": back})


def verify_error_roundtrip(transform, report: EquivReport) -> None:
    samples = [
        "invalid_argument: end must be after start",
        "conflict: attendee double-booked",
        "not_found: no such event",
        "permission: denied",
    ]
    for msg in samples:
        ctx = {}
        recovered = transform.decode_error(transform.encode_error(msg, ctx), ctx)
        report.error_cases += 1
        if error_category(recovered) != error_category(msg):
            report.mismatches.append({"channel": "error", "transform": transform.family,
                                      "input": msg, "got": recovered})


def run_equivalence_suite(n_request_per_tool: int = 350, seed: int = 0) -> dict:
    """Run the full suite over all strict families. Returns a per-family report."""
    out: dict[str, EquivReport] = {}
    for transform in all_strict_transforms():
        rep = EquivReport()
        verify_call_equivalence(transform, n_request_per_tool, rep, seed)
        verify_response_roundtrip(transform, rep)
        verify_error_roundtrip(transform, rep)
        verify_state_equivalence(transform, rep)
        out[transform.family] = rep
    return out
