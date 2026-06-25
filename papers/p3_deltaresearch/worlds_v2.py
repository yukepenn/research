"""Diverse evidence-world generator (P3 spec D1) with method-independent gold.

Each world is a random DAG of numeric claims: base claims (one per source) and
derived claims computed from earlier claims by a typed op (SUM, DIFF, RATIO,
SCALE, AVG, PCT_CHANGE, THRESHOLD). Plus a few irrelevant fact distractors.

Claim TEXT names the derivation type in natural language (e.g. "Total of A and B")
so a method can INFER the dependency/formula from text alone — it never receives
the graph. After a delta (a base source value change / retraction), gold A/U are
computed by an INDEPENDENT deterministic recomputation of the DAG (separate code
path from any method), so "method ≈ gold" is a real test, not a tautology.

Topologies vary across seeds: chain, tree, diamond, fan-in, fan-out, mixed.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from core.util import rng_for, short_id

OPS = ("SUM", "DIFF", "RATIO", "SCALE", "AVG", "PCT_CHANGE", "THRESHOLD")


@dataclass
class V2Claim:
    cid: str
    kind: str            # "base" | op-name | "fact"
    text: str
    value: object        # float | bool | str
    parents: tuple = ()  # claim ids this is computed from (HIDDEN from method)
    const: float = 0.0   # SCALE factor / THRESHOLD level
    source: str | None = None
    citation: str | None = None


@dataclass
class V2World:
    world_id: str
    seed: int
    topology: str
    delta_type: str
    sources: dict             # source_id -> {value, status}
    claims: dict              # cid -> V2Claim  (PRE-delta report)
    report_claims: list       # ordered cids as shown in R0
    delta: dict               # observable: {changed:{src:newval}, retracted:[src], type}
    gold_A: frozenset = frozenset()   # eval only
    gold_U: frozenset = frozenset()   # eval only
    post_values: dict = field(default_factory=dict)  # eval only

    def r0_view(self) -> dict:
        """What a METHOD may see: report claims (text/value/citation) + sources +
        the observable delta. NO parents, NO formulas, NO gold, NO post values."""
        return {
            "claims": [{"id": c.cid, "text": c.text, "value": c.claims_value_str()}
                       for c in (self.claims[cid] for cid in self.report_claims)],
            "sources": {s: {"value": v["value"], "status": v["status"]}
                        for s, v in self.sources.items()},
            "delta": self.delta,
        }


def _round(x):
    return round(float(x), 4) if isinstance(x, (int, float)) and not isinstance(x, bool) else x


def _compute(op, parent_vals, const):
    a = parent_vals[0] if parent_vals else None
    if any(v is None for v in parent_vals):
        return None
    if op == "SUM":
        return _round(sum(parent_vals))
    if op == "AVG":
        return _round(sum(parent_vals) / len(parent_vals))
    if op == "DIFF":
        return _round(parent_vals[0] - parent_vals[1])
    if op == "RATIO":
        return _round(parent_vals[0] / parent_vals[1]) if parent_vals[1] else None
    if op == "SCALE":
        return _round(a * const)
    if op == "PCT_CHANGE":
        return _round((parent_vals[1] - parent_vals[0]) / parent_vals[0] * 100) if parent_vals[0] else None
    if op == "THRESHOLD":
        return bool(a >= const)
    return None


def _text(op, cid, parents, const, names, style="named"):
    pn = [names[p] for p in parents]
    if style == "vague":
        # parents named, but the OPERATION is hidden (the method must infer it)
        joined = " and ".join(pn)
        return f"Metric {cid}, derived from {joined}, is {{v}}."
    if op == "SUM":
        return f"The total of {', '.join(pn)} is {{v}}."
    if op == "AVG":
        return f"The average of {', '.join(pn)} is {{v}}."
    if op == "DIFF":
        return f"{pn[0]} exceeds {pn[1]} by {{v}}."
    if op == "RATIO":
        return f"The ratio of {pn[0]} to {pn[1]} is {{v}}."
    if op == "SCALE":
        return f"{pn[0]} scaled by {const} is {{v}}."
    if op == "PCT_CHANGE":
        return f"The percent change from {pn[0]} to {pn[1]} is {{v}} percent."
    if op == "THRESHOLD":
        return f"Whether {pn[0]} meets the threshold of {const} is {{v}}."
    return "{v}"


# add the value-string helper onto V2Claim
def _claims_value_str(self):
    v = self.value
    if isinstance(v, bool):
        return "yes" if v else "no"
    return str(v)


V2Claim.claims_value_str = _claims_value_str


_NAMEPOOL = ["Region A revenue", "Region B revenue", "Region C revenue", "Unit cost",
             "Headcount", "Defect count", "Active users", "Latency budget",
             "Baseline figure", "Updated figure"]


def generate_world_v2(seed: int = 0, delta_type: str = "numeric_revision",
                      style: str = "named") -> V2World:
    rng = rng_for("p3v2", seed)
    topology = rng.choice(["chain", "tree", "diamond", "fanin", "fanout", "mixed"])
    n_base = rng.randint(2, 4)
    n_derived = rng.randint(3, 5)

    claims: dict[str, V2Claim] = {}
    names: dict[str, str] = {}
    order: list[str] = []
    sources: dict[str, dict] = {}

    # base claims
    base_ids = []
    pool = list(_NAMEPOOL)
    rng.shuffle(pool)
    for i in range(n_base):
        cid = f"b{i}"
        sid = f"s{i}"
        val = float(rng.randint(20, 200))
        sources[sid] = {"value": val, "status": "active"}
        nm = pool[i % len(pool)]
        names[cid] = nm
        claims[cid] = V2Claim(cid, "base", f"{nm} is {{v}}.".replace("{v}", str(val)),
                              val, source=sid, citation=sid)
        base_ids.append(cid)
        order.append(cid)

    # derived claims over a random DAG (each references earlier claims)
    avail = list(base_ids)
    for j in range(n_derived):
        cid = f"d{j}"
        op = rng.choice(OPS)
        arity = 1 if op in ("SCALE", "THRESHOLD") else 2
        if len(avail) < arity:
            op, arity = "SCALE", 1
        parents = tuple(rng.sample(avail, arity))
        const = float(rng.choice([2, 3, 5, 10, 100])) if op == "SCALE" else (
            float(rng.randint(50, 300)) if op == "THRESHOLD" else 0.0)
        val = _compute(op, [claims[p].value for p in parents], const)
        nm = f"metric {cid}"
        names[cid] = nm
        txt = _text(op, cid, parents, const, names, style).replace("{v}", str(_round(val)))
        claims[cid] = V2Claim(cid, op, txt, val, parents=parents, const=const, citation="(derived)")
        order.append(cid)
        avail.append(cid)

    # a couple of irrelevant fact distractors (must be preserved)
    for k in range(rng.randint(1, 2)):
        cid = f"f{k}"
        claims[cid] = V2Claim(cid, "fact", f"The reporting office is in city-{k}.", f"city-{k}",
                              citation=f"sf{k}")
        order.append(cid)

    # ---- apply delta (observable) ----
    changed_src = rng.choice([sources_id for sources_id in sources])
    target_base = next(c for c in base_ids if claims[c].source == changed_src)
    delta = {"type": delta_type, "changed": {}, "retracted": []}
    if delta_type == "source_retraction":
        sources[changed_src]["status"] = "retracted"
        delta["retracted"] = [changed_src]
        new_base_val = None
    else:  # numeric_revision (and unit/auth variants reduce to a value change)
        delta_amt = float(rng.choice([10, 25, -15, 40, -30]))
        new_base_val = _round(claims[target_base].value + delta_amt)
        sources[changed_src]["value"] = new_base_val
        delta["changed"] = {changed_src: new_base_val}

    # ---- INDEPENDENT gold recompute (eval only) ----
    post = {}
    for cid in order:
        c = claims[cid]
        if c.kind == "base":
            post[cid] = new_base_val if c.cid == target_base else c.value
        elif c.kind == "fact":
            post[cid] = c.value
        else:
            post[cid] = _compute(c.kind, [post[p] for p in c.parents], c.const)
    gold_A = frozenset(cid for cid in order
                       if claims[cid].kind not in ("fact",) and post[cid] != claims[cid].value)
    gold_U = frozenset(cid for cid in order if cid not in gold_A)

    return V2World(
        world_id=short_id("p3v2", seed, delta_type, topology),
        seed=seed, topology=topology, delta_type=delta_type,
        sources=sources, claims=claims, report_claims=order, delta=delta,
        gold_A=gold_A, gold_U=gold_U, post_values=post)


def generate_worlds_v2(n: int = 20, seed0: int = 0,
                       delta_types=("numeric_revision", "source_retraction"),
                       style: str = "named") -> list[V2World]:
    out = []
    i = seed0
    while len(out) < n:
        for dt in delta_types:
            w = generate_world_v2(i, dt, style)
            # keep only worlds with a non-trivial downstream cascade (>=1 derived in A)
            if any(w.claims[c].kind not in ("base", "fact") for c in w.gold_A):
                out.append(w)
            if len(out) >= n:
                break
        i += 1
    return out
