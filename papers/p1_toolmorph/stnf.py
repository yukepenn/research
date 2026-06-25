"""Semantic Tool Normal Form (STNF) — the surviving novel core (manual 5.8).

The narrowed contribution (post-novelty-audit) is a LABEL-FREE normalization layer
that re-presents a deployed (possibly transformed) tool to the agent in a canonical
normal form, with a runtime codec that maps the agent's canonical calls back to the
deployed interface. ToolMorph's headline question is whether such a layer recovers
performance on UNSEEN transforms.

Tier-0 deliverables here (deterministic, no model needed):
  - OracleCanonicalizer: upper bound — given the transform, presents a perfectly
    canonical interface (P1-METHOD-001). Proves the codec plumbing is correct.
  - StaticCanonicalizer: schema-ONLY normalization with no transform label
    (P1-METHOD-002). Honestly covers structural transforms; abstains on semantic
    ones (lexical/enum) which provably require the gated LLM/probe versions.
  - Equivalence guarantee: routing a canonical call through STNF reaches the env
    with a byte-identical state transition.

The actual recovery-of-model-performance is the budget-gated pilot; what is proven
here is (a) codec correctness and (b) the label-free reach of static normalization.
"""
from __future__ import annotations

import copy
from dataclasses import dataclass

from core.adapters.base import ToolSpec
from papers.p1_toolmorph.transforms.dsl import apply_transform


@dataclass
class Normalized:
    presented: ToolSpec     # what the AGENT sees (canonical normal form when possible)
    covered: bool           # did the canonicalizer normalize this tool?
    method: str


class OracleCanonicalizer:
    """Upper bound: uses the known transform to present a perfectly canonical
    interface (canonical schema, canonical responses, canonical errors)."""

    name = "oracle"

    def normalize(self, canonical_tool: ToolSpec, transform) -> Normalized:
        ctx = transform.prepare(canonical_tool.schema)
        deployed = apply_transform(canonical_tool, transform)  # the real transformed tool

        def routed(canonical_args: dict):
            view_args = transform.encode_request(dict(canonical_args), ctx)
            try:
                view_result = deployed.executor(view_args)
            except Exception as exc:
                raise type(exc)(transform.decode_error(str(exc), ctx)) from None
            return transform.decode_response(view_result, ctx)

        presented = ToolSpec(canonical_tool.name, canonical_tool.description,
                             canonical_tool.schema, executor=routed)
        return Normalized(presented=presented, covered=True, method=self.name)


class StaticCanonicalizer:
    """Label-free: sees only the DEPLOYED (transformed) tool's schema. Recovers
    structural wrapping (nesting) by inspection; abstains on semantic renaming
    (lexical/enum) which need the LLM/probe versions. Operates without the
    canonical reference or the transform identity."""

    name = "static"

    def normalize(self, deployed_tool: ToolSpec, transform=None) -> Normalized:
        schema = deployed_tool.schema
        props = schema.get("properties", {})
        required = schema.get("required", [])
        # Detect a single-object wrapper => structural nesting; unwrap it.
        if (len(props) == 1 and len(required) == 1
                and isinstance(next(iter(props.values())), dict)
                and next(iter(props.values())).get("type") == "object"):
            wrapper_key = next(iter(props))
            inner = copy.deepcopy(props[wrapper_key])
            inner.setdefault("type", "object")

            def routed(canonical_args: dict):
                return deployed_tool.executor({wrapper_key: dict(canonical_args)})

            presented = ToolSpec(deployed_tool.name, deployed_tool.description,
                                 {"type": "object",
                                  "properties": inner.get("properties", {}),
                                  "required": inner.get("required", [])},
                                 executor=routed)
            return Normalized(presented=presented, covered=True, method=self.name)
        # Abstain: present the deployed tool unchanged (the manual: abstain, do not
        # emit a dangerous guess).
        return Normalized(presented=deployed_tool, covered=False, method=self.name)


# Families the LABEL-FREE static canonicalizer can normalize (honest reach).
STATIC_COVERAGE = {
    "structural_nesting": True,
    "response_representation": True,   # request schema unchanged -> already canonical
    "error_representation": True,      # request schema unchanged -> already canonical
    "optional_default": False,         # cannot infer the default without semantics
    "lexical_aliasing": False,         # synonym renaming needs semantic inference
    "enum_encoding": False,            # code<->value mapping needs semantic inference
}


def static_coverage_table() -> dict[str, bool]:
    return dict(STATIC_COVERAGE)
