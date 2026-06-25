"""The six strict transformation families (manual 5.7).

Each is state-transition-equivalent: it changes only the model-visible surface.
All maps are bijective on valid inputs so the property-test round-trips hold and
the post-call environment snapshot is byte-identical to the canonical call.
"""
from __future__ import annotations

import copy

from papers.p1_toolmorph.transforms.dsl import Transform, error_category

# A small synonym dictionary so aliases stay clearly meaning-preserving for the
# real-model study, while remaining a strict bijection for the equivalence test.
_SYNONYMS = {
    "title": "name", "start": "begin", "end": "finish", "attendees": "participants",
    "event_id": "eid", "sku": "item", "quantity": "amount", "order_id": "oid",
    "ticket_id": "tid", "assignee": "owner", "subject": "summary",
    "priority": "severity", "status": "state",
}
_INV_SYNONYMS = {v: k for k, v in _SYNONYMS.items()}


def _alias(key: str) -> str:
    return _SYNONYMS.get(key, key + "_x")


def _unalias(key: str) -> str:
    if key in _INV_SYNONYMS:
        return _INV_SYNONYMS[key]
    return key[:-2] if key.endswith("_x") else key


# --------------------------------------------------------------------------
# 1. Lexical aliasing: rename tool + parameter names to synonyms.
# --------------------------------------------------------------------------
class LexicalAliasing(Transform):
    family = "lexical_aliasing"

    def view_name(self, name, ctx):
        return name + "_v2"

    def view_schema(self, schema, ctx):
        s = copy.deepcopy(schema)
        props = s.get("properties", {})
        s["properties"] = {_alias(k): v for k, v in props.items()}
        if "required" in s:
            s["required"] = [_alias(k) for k in s["required"]]
        return s

    def encode_request(self, args, ctx):
        return {_alias(k): v for k, v in args.items()}

    def decode_request(self, args, ctx):
        return {_unalias(k): v for k, v in args.items()}


# --------------------------------------------------------------------------
# 2. Structural nesting: wrap all top-level args under a single object.
# --------------------------------------------------------------------------
class StructuralNesting(Transform):
    family = "structural_nesting"
    GROUP = "params"

    def view_schema(self, schema, ctx):
        s = copy.deepcopy(schema)
        inner = {"type": "object", "properties": s.get("properties", {})}
        if "required" in s:
            inner["required"] = s["required"]
        return {"type": "object", "properties": {self.GROUP: inner},
                "required": [self.GROUP]}

    def encode_request(self, args, ctx):
        return {self.GROUP: dict(args)}

    def decode_request(self, args, ctx):
        if self.GROUP not in args:
            return dict(args)  # tolerate already-flat (invalid) -> executor errors
        return dict(args[self.GROUP])


# --------------------------------------------------------------------------
# 3. Enum encoding: replace enum string values with short integer codes.
# --------------------------------------------------------------------------
class EnumEncoding(Transform):
    family = "enum_encoding"

    def prepare(self, schema):
        # field -> {value: code} and inverse, derived from the canonical schema
        maps: dict[str, dict] = {}
        inv: dict[str, dict] = {}
        for field, spec in schema.get("properties", {}).items():
            if isinstance(spec, dict) and "enum" in spec:
                values = spec["enum"]
                maps[field] = {v: f"c{i}" for i, v in enumerate(values)}
                inv[field] = {f"c{i}": v for i, v in enumerate(values)}
        return {"maps": maps, "inv": inv}

    def view_schema(self, schema, ctx):
        s = copy.deepcopy(schema)
        for field, spec in s.get("properties", {}).items():
            if field in ctx["maps"]:
                spec["enum"] = list(ctx["maps"][field].values())
        return s

    def encode_request(self, args, ctx):
        out = dict(args)
        for field, m in ctx["maps"].items():
            if field in out and out[field] in m:
                out[field] = m[out[field]]
        return out

    def decode_request(self, args, ctx):
        out = dict(args)
        for field, m in ctx["inv"].items():
            if field in out and out[field] in m:
                out[field] = m[out[field]]
        return out


# --------------------------------------------------------------------------
# 4. Optional/default exposure: make a defaulted optional field explicit/required.
# --------------------------------------------------------------------------
class OptionalDefaultExposure(Transform):
    family = "optional_default"
    DEFAULTS = {"attendees": [], "priority": "medium"}

    def prepare(self, schema):
        props = schema.get("properties", {})
        required = set(schema.get("required", []))
        exposed = [k for k in props if k in self.DEFAULTS and k not in required]
        return {"exposed": exposed}

    def view_schema(self, schema, ctx):
        s = copy.deepcopy(schema)
        req = set(s.get("required", []))
        req.update(ctx["exposed"])
        s["required"] = sorted(req)
        return s

    def encode_request(self, args, ctx):
        out = dict(args)
        for k in ctx["exposed"]:
            out.setdefault(k, copy.deepcopy(self.DEFAULTS[k]))
        return out

    def decode_request(self, args, ctx):
        return dict(args)  # executor applies the same default either way


# --------------------------------------------------------------------------
# 5. Response representation: rename response keys to synonyms.
# --------------------------------------------------------------------------
class ResponseRepresentation(Transform):
    family = "response_representation"

    def _map_keys(self, obj, fn):
        if isinstance(obj, dict):
            return {fn(k): self._map_keys(v, fn) for k, v in obj.items()}
        if isinstance(obj, list):
            return [self._map_keys(v, fn) for v in obj]
        return obj

    def encode_response(self, result, ctx):
        return self._map_keys(result, _alias)

    def decode_response(self, result, ctx):
        return self._map_keys(result, _unalias)


# --------------------------------------------------------------------------
# 6. Error representation: map error category to a structured code.
# --------------------------------------------------------------------------
class ErrorRepresentation(Transform):
    family = "error_representation"
    CODES = {"invalid_argument": "E400", "conflict": "E409",
             "not_found": "E404", "permission": "E403"}
    INV = {v: k for k, v in CODES.items()}

    def encode_error(self, msg, ctx):
        cat = error_category(msg)
        detail = msg.split(":", 1)[1].strip() if ":" in msg else ""
        code = self.CODES.get(cat, "E500")
        return f"{code}: {detail}"

    def decode_error(self, msg, ctx):
        code = error_category(msg)
        detail = msg.split(":", 1)[1].strip() if ":" in msg else ""
        cat = self.INV.get(code, "unknown")
        return f"{cat}: {detail}"


STRICT_FAMILIES = [
    LexicalAliasing, StructuralNesting, EnumEncoding,
    OptionalDefaultExposure, ResponseRepresentation, ErrorRepresentation,
]


def all_strict_transforms() -> list[Transform]:
    return [cls() for cls in STRICT_FAMILIES]
