"""Deterministic, fully-verifiable controlled-world generator (Tier-0).

Pipeline (manual: deterministic gold, no LLM, seeded):

    latent fact graph  ->  evidence items  ->  atomic claims (typed edges)
                       ->  templated initial report
                       ->  apply an evidence-WORLD delta
                       ->  PROGRAMMATIC gold impact sets A / U / N / C

The "world physics" lives entirely in this file: the gold sets are computed by
recomputing the fact graph under the delta and diffing the pre/post claim
states. The typed-graph analyzer in ``claim_graph.py`` is a *separate* code path
operating only on typed edges, so "analyzer == gold" is a genuine check of the
graph, not a tautology.

Topology (one report, ten asserted claims):

    cA   numeric   <- e_S1                     base measurement, region A
    cB   numeric   <- e_S2                     base measurement, region B
    cR   fact      <- e_S3 (+ alt e_S4)        compliance status, redundant source
    cZ   fact      <- e_S5                     unrelated stable fact
    cCur numeric   <- e_rate_old [grp=rate]    current official rate (temporal)
    cTotal  numeric  = cA + cB                 (NUMERIC_DEPENDENCY cA,cB)
    cMargin comparison = cB - cA               (DERIVED_FROM + NUMERIC_DEPENDENCY)
    cShare  numeric  = cA / cTotal             (NUMERIC_DEPENDENCY; QUALIFIED_BY cR)
    cIndex  numeric  = cShare * 100            (NUMERIC_DEPENDENCY)  3-hop from cA
    cProj   numeric  = cCur * k                (NUMERIC + TEMPORAL_DEPENDENCY cCur)

Plus a claim-free evidence item ``e_irrel`` for the negative control, a latent
``e_rate_new`` (a not-yet-current rate source) for the temporal delta, and a
latent ``cW`` introduced by the new-authoritative-source delta.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from core.util import rng_for, short_id
from papers.p3_deltaresearch.claim_graph import (
    Claim, ClaimGraph, EdgeType, EvidenceDelta, build_graph,
)

# ---- canonical ids -------------------------------------------------------
CA, CB, CR, CZ, CCUR = "cA", "cB", "cR", "cZ", "cCur"
CTOTAL, CMARGIN, CSHARE, CINDEX, CPROJ = "cTotal", "cMargin", "cShare", "cIndex", "cProj"
CW = "cW"  # introduced by new_authoritative_source

ASSERTED = (CA, CB, CR, CZ, CCUR, CTOTAL, CMARGIN, CSHARE, CINDEX, CPROJ)
# topological order for recomputation (bases first, then derived)
_TOPO = (CA, CB, CR, CZ, CCUR, CTOTAL, CMARGIN, CSHARE, CINDEX, CPROJ)

E_S1, E_S2, E_S3, E_S4, E_S5 = "e_S1", "e_S2", "e_S3", "e_S4", "e_S5"
E_RATE_OLD, E_RATE_NEW = "e_rate_old", "e_rate_new"
E_IRREL = "e_irrel"
E_CONF, E_AUTH = "e_conf", "e_auth"

RATE_GROUP = "rate"

DELTA_TYPES = (
    "numeric_revision",
    "source_retraction",
    "source_conflict",
    "temporal_validity_change",
    "upstream_recompute",
    "new_authoritative_source",
    "irrelevant_update_negative_control",
)
# delta types that, by construction, leave a non-empty must-change set with
# derived/temporal downstream claims (i.e. NOT the negative control)
EFFECTFUL_DELTAS = DELTA_TYPES[:-1]


@dataclass
class Evidence:
    eid: str
    source: str
    timestamp: str            # ISO date the item was published
    valid_from: str           # validity interval start
    valid_to: str | None      # validity interval end (None = open)
    value: object = None      # numeric value where relevant
    authority: int = 1        # higher = more authoritative source
    temporal_group: str | None = None
    retracted: bool = False


# --------------------------------------------------------------------------
# numeric recomputation of the fact graph (handles None = unsupported)
# --------------------------------------------------------------------------
def _recompute(base: dict, k: float) -> dict:
    """Given base claim values, compute the full claim-value map via formulas.

    A value of ``None`` means 'no longer supported / uncomputable' and
    propagates downstream.
    """
    a = base[CA]; b = base[CB]; cur = base[CCUR]
    out = dict(base)
    total = None if (a is None or b is None) else a + b
    margin = None if (a is None or b is None) else b - a
    share = None if (a is None or total in (None, 0)) else a / total
    index = None if share is None else share * 100.0
    proj = None if cur is None else cur * k
    out[CTOTAL] = total
    out[CMARGIN] = margin
    out[CSHARE] = share
    out[CINDEX] = index
    out[CPROJ] = proj
    return out


def _claim_text(cid: str, value) -> str:
    templates = {
        CA: "Region A revenue is {v}.",
        CB: "Region B revenue is {v}.",
        CR: "Compliance status is {v}.",
        CZ: "Headquarters location is {v}.",
        CCUR: "The current official rate is {v}.",
        CTOTAL: "Total revenue is {v}.",
        CMARGIN: "Region B leads Region A by {v}.",
        CSHARE: "Region A share of total revenue is {v}.",
        CINDEX: "The revenue concentration index is {v}.",
        CPROJ: "Projected rate next period is {v}.",
        CW: "An independent audit confirms the figures ({v}).",
    }
    return templates[cid].format(v=value)


# --------------------------------------------------------------------------
# World
# --------------------------------------------------------------------------
@dataclass
class World:
    world_id: str
    seed: int
    dtype: str
    report_date: str
    evidence: dict[str, Evidence]
    claims: dict[str, Claim]                 # PRE-delta report claims
    graph: ClaimGraph
    delta: EvidenceDelta
    report: str
    pre_values: dict
    pre_citations: dict
    post_values: dict                        # correct post-delta values (incl. new claims)
    post_citations: dict
    new_claims: dict[str, Claim] = field(default_factory=dict)
    gold_A: frozenset = frozenset()
    gold_U: frozenset = frozenset()
    gold_N: frozenset = frozenset()
    gold_C: frozenset = frozenset()

    # convenience -----------------------------------------------------------
    def is_numeric(self, cid: str) -> bool:
        c = self.claims.get(cid) or self.new_claims.get(cid)
        return bool(c) and c.ctype in ("numeric", "comparison", "derived", "temporal")

    def all_claim_ids(self) -> frozenset:
        return frozenset(self.claims) | frozenset(self.new_claims)


def _base_edges() -> list[tuple[str, str, str]]:
    ET = EdgeType
    return [
        (CA, CTOTAL, ET.NUMERIC_DEPENDENCY),
        (CB, CTOTAL, ET.NUMERIC_DEPENDENCY),
        (CA, CMARGIN, ET.NUMERIC_DEPENDENCY),
        (CB, CMARGIN, ET.NUMERIC_DEPENDENCY),
        (CA, CMARGIN, ET.DERIVED_FROM),
        (CB, CMARGIN, ET.DERIVED_FROM),
        (CA, CSHARE, ET.NUMERIC_DEPENDENCY),
        (CTOTAL, CSHARE, ET.NUMERIC_DEPENDENCY),
        (CR, CSHARE, ET.QUALIFIED_BY),
        (CSHARE, CINDEX, ET.NUMERIC_DEPENDENCY),
        # cProj depends on cCur ONLY via NUMERIC + TEMPORAL (NOT DERIVED_FROM);
        # this is what an author-edit framing misses (see diverge.py / H_DIVERGE)
        (CCUR, CPROJ, ET.NUMERIC_DEPENDENCY),
        (CCUR, CPROJ, ET.TEMPORAL_DEPENDENCY),
    ]


def _build_pre(seed: int):
    """Build evidence, pre claims, base values and citations (delta-independent)."""
    rng = rng_for("p3_world", seed)
    report_date = "2026-03-01"

    vA = float(rng.randint(80, 120))
    vB = float(rng.randint(130, 170))
    while vB == vA:
        vB = float(rng.randint(130, 170))
    vCurOld = float(rng.randint(3, 6))
    vCurNew = float(rng.randint(7, 10))      # disjoint range => guaranteed change
    k = 2.0
    vR = "compliant"
    vZ = "Zurich"

    evidence = {
        E_S1: Evidence(E_S1, "bureau", "2026-01-10", "2026-01-10", None, vA, 1),
        E_S2: Evidence(E_S2, "bureau", "2026-01-12", "2026-01-12", None, vB, 1),
        E_S3: Evidence(E_S3, "registry", "2026-01-05", "2026-01-05", None, vR, 1),
        E_S4: Evidence(E_S4, "auditor", "2026-01-06", "2026-01-06", None, vR, 1),
        E_S5: Evidence(E_S5, "gazette", "2025-12-01", "2025-12-01", None, vZ, 1),
        E_RATE_OLD: Evidence(E_RATE_OLD, "central_bank", "2026-01-01", "2026-01-01",
                             "2026-06-30", vCurOld, 1, temporal_group=RATE_GROUP),
        # a newer rate item that is NOT yet current at report_date (valid_from later)
        E_RATE_NEW: Evidence(E_RATE_NEW, "central_bank", "2026-02-15", "2026-09-01",
                             None, vCurNew, 1, temporal_group=RATE_GROUP),
        # supports NO asserted claim -> negative-control target
        E_IRREL: Evidence(E_IRREL, "newswire", "2026-02-20", "2026-02-20", None,
                          float(rng.randint(1, 9)), 1),
    }

    base_pre = {CA: vA, CB: vB, CR: vR, CZ: vZ, CCUR: vCurOld}
    pre_values = _recompute(base_pre, k)

    pre_citations = {
        CA: E_S1, CB: E_S2, CR: E_S3, CZ: E_S5, CCUR: E_RATE_OLD,
        CTOTAL: "(derived)", CMARGIN: "(derived)", CSHARE: "(derived)",
        CINDEX: "(derived)", CPROJ: "(derived)",
    }

    ET = EdgeType
    claims = {
        CA: Claim(CA, "numeric", _claim_text(CA, pre_values[CA]), pre_values[CA],
                  supports=(E_S1,), citation=E_S1),
        CB: Claim(CB, "numeric", _claim_text(CB, pre_values[CB]), pre_values[CB],
                  supports=(E_S2,), citation=E_S2),
        CR: Claim(CR, "fact", _claim_text(CR, pre_values[CR]), pre_values[CR],
                  supports=(E_S3,), alt_supports=(E_S4,), citation=E_S3),
        CZ: Claim(CZ, "fact", _claim_text(CZ, pre_values[CZ]), pre_values[CZ],
                  supports=(E_S5,), citation=E_S5),
        CCUR: Claim(CCUR, "temporal", _claim_text(CCUR, pre_values[CCUR]), pre_values[CCUR],
                    supports=(E_RATE_OLD,), citation=E_RATE_OLD, temporal_group=RATE_GROUP),
        CTOTAL: Claim(CTOTAL, "numeric", _claim_text(CTOTAL, pre_values[CTOTAL]),
                      pre_values[CTOTAL], citation="(derived)", formula="cA + cB"),
        CMARGIN: Claim(CMARGIN, "comparison", _claim_text(CMARGIN, pre_values[CMARGIN]),
                       pre_values[CMARGIN], citation="(derived)", formula="cB - cA"),
        CSHARE: Claim(CSHARE, "numeric", _claim_text(CSHARE, pre_values[CSHARE]),
                      pre_values[CSHARE], citation="(derived)", formula="cA / (cA + cB)"),
        CINDEX: Claim(CINDEX, "numeric", _claim_text(CINDEX, pre_values[CINDEX]),
                      pre_values[CINDEX], citation="(derived)", formula="cShare * 100"),
        CPROJ: Claim(CPROJ, "numeric", _claim_text(CPROJ, pre_values[CPROJ]),
                     pre_values[CPROJ], citation="(derived)", formula="cCur * 2"),
    }
    graph = build_graph(claims, _base_edges())

    meta = {
        "vA": vA, "vB": vB, "vR": vR, "vZ": vZ,
        "vCurOld": vCurOld, "vCurNew": vCurNew, "k": k, "report_date": report_date,
        "rng": rng,
    }
    return evidence, claims, graph, pre_values, pre_citations, base_pre, meta


def _render_report(report_date: str, claims: dict[str, Claim], values: dict,
                   citations: dict) -> str:
    lines = [f"# Controlled research report (as of {report_date})"]
    for cid in _TOPO:
        c = claims[cid]
        lines.append(f"[{cid}] {_claim_text(cid, values[cid])} [cite: {citations[cid]}]")
    return "\n".join(lines)


def generate_world(seed: int = 0, dtype: str = "numeric_revision") -> World:
    """Generate one fully-verifiable world with `dtype` applied and gold sets."""
    if dtype not in DELTA_TYPES:
        raise ValueError(f"unknown delta type {dtype!r}")
    evidence, claims, graph, pre_values, pre_citations, base_pre, meta = _build_pre(seed)
    rng = meta["rng"]; k = meta["k"]
    report = _render_report(meta["report_date"], claims, pre_values, pre_citations)

    post_base = dict(base_pre)
    post_citations = dict(pre_citations)
    new_claims: dict[str, Claim] = {}
    contested: set[str] = set()
    delta_kwargs: dict = {}

    if dtype == "numeric_revision":
        dA = float(rng.choice([10.0, 20.0, -10.0, 15.0]))
        post_base[CA] = base_pre[CA] + dA
        delta_kwargs["changed_value_evidence"] = frozenset({E_S1})
        evidence[E_S1].value = post_base[CA]

    elif dtype == "upstream_recompute":
        dB = float(rng.choice([12.0, 20.0, -15.0, 18.0]))
        post_base[CB] = base_pre[CB] + dB
        delta_kwargs["changed_value_evidence"] = frozenset({E_S2})
        evidence[E_S2].value = post_base[CB]

    elif dtype == "source_retraction":
        # e_S1 is the SOLE support of cA -> cA (and all numeric downstream) lost.
        # e_S3 is the PRIMARY support of cR, but alt e_S4 survives -> cR preserved.
        evidence[E_S1].retracted = True
        evidence[E_S3].retracted = True
        post_base[CA] = None
        post_citations[CA] = None            # nothing left to cite
        post_citations[CR] = E_S4            # provenance refresh only (value preserved)
        delta_kwargs["retracted_evidence"] = frozenset({E_S1, E_S3})

    elif dtype == "source_conflict":
        vConf = base_pre[CA] + float(rng.choice([18.0, -12.0, 22.0]))
        evidence[E_CONF] = Evidence(E_CONF, "rival_bureau", "2026-02-25", "2026-02-25",
                                    None, vConf, 1)
        # the directly-supported claim becomes contested; downstream must change
        # to reflect the now-uncertain basis (recomputed toward the new figure).
        post_base[CA] = vConf
        contested.add(CA)
        delta_kwargs["conflicted_evidence"] = frozenset({E_S1})

    elif dtype == "temporal_validity_change":
        # e_rate_new's validity moves earlier so it is current at report_date;
        # the current official rate (and its projection) change.
        evidence[E_RATE_NEW].valid_from = "2026-02-01"
        post_base[CCUR] = meta["vCurNew"]
        post_citations[CCUR] = E_RATE_NEW
        delta_kwargs["validity_changed_evidence"] = frozenset({E_RATE_NEW})
        delta_kwargs["temporal_changed_groups"] = frozenset({RATE_GROUP})

    elif dtype == "new_authoritative_source":
        vAuth = base_pre[CA] + float(rng.choice([25.0, 30.0, -20.0]))
        evidence[E_AUTH] = Evidence(E_AUTH, "national_statistics_office", "2026-02-28",
                                    "2026-02-28", None, vAuth, authority=3)
        post_base[CA] = vAuth
        post_citations[CA] = E_AUTH          # more authoritative source supersedes
        # the authoritative source also introduces a brand-new supported claim
        new_claims[CW] = Claim(CW, "fact", _claim_text(CW, "audited"), "audited",
                               supports=(E_AUTH,), citation=E_AUTH)
        delta_kwargs["superseded_evidence"] = frozenset({E_S1})
        delta_kwargs["added_claim_ids"] = frozenset({CW})

    elif dtype == "irrelevant_update_negative_control":
        evidence[E_IRREL].value = float(rng.randint(10, 20))
        delta_kwargs["changed_value_evidence"] = frozenset({E_IRREL})
        # NOTE: by construction this leaves gold_A EMPTY (a correct analyzer must
        # predict 'nothing changes'); it is the negative control.

    delta = EvidenceDelta(dtype=dtype, **delta_kwargs)

    post_values = _recompute(post_base, k)
    for cid, c in new_claims.items():
        post_values[cid] = c.value
        post_citations[cid] = c.citation

    # ---- PROGRAMMATIC gold sets (world physics; diff pre vs post) ----------
    gold_A: set[str] = set()
    for cid in ASSERTED:
        if cid in contested:
            continue
        changed_value = post_values[cid] != pre_values[cid]
        changed_support = (post_citations[cid] != pre_citations[cid]
                           and post_values[cid] != pre_values[cid])
        # support loss (value -> None) and value changes are must-change;
        # a pure citation refresh while the value is preserved is NOT in A
        # (alternative-support => not necessarily affected).
        if changed_value or changed_support:
            gold_A.add(cid)
    gold_N = frozenset(new_claims)
    gold_C = frozenset(contested)
    gold_U = frozenset(c for c in ASSERTED if c not in gold_A and c not in gold_C)

    return World(
        world_id=short_id("p3_world", seed, dtype),
        seed=seed, dtype=dtype, report_date=meta["report_date"],
        evidence=evidence, claims=claims, graph=graph, delta=delta, report=report,
        pre_values=pre_values, pre_citations=pre_citations,
        post_values=post_values, post_citations=post_citations,
        new_claims=new_claims,
        gold_A=frozenset(gold_A), gold_U=gold_U, gold_N=gold_N, gold_C=gold_C,
    )


def generate_worlds(n: int = 5, dtypes=EFFECTFUL_DELTAS, seed0: int = 0) -> list[World]:
    """Deterministic batch of worlds, one per (seed, dtype)."""
    out: list[World] = []
    for s in range(seed0, seed0 + n):
        for dt in dtypes:
            out.append(generate_world(s, dt))
    return out


def world_is_consistent(w: World) -> bool:
    """Internal-consistency check: gold sets partition the asserted claims and
    derived values agree with the formulas (post recompute is idempotent)."""
    asserted = set(ASSERTED)
    if set(w.gold_A) | set(w.gold_U) | set(w.gold_C) != asserted:
        return False
    if (set(w.gold_A) & set(w.gold_U)) or (set(w.gold_A) & set(w.gold_C)) \
            or (set(w.gold_U) & set(w.gold_C)):
        return False
    if set(w.gold_N) & asserted:
        return False
    # derived post-values are consistent with their formulas
    recomputed = _recompute(
        {CA: w.post_values[CA], CB: w.post_values[CB], CR: w.post_values[CR],
         CZ: w.post_values[CZ], CCUR: w.post_values[CCUR]}, 2.0)
    for cid in (CTOTAL, CMARGIN, CSHARE, CINDEX, CPROJ):
        if recomputed[cid] != w.post_values[cid]:
            return False
    return True
