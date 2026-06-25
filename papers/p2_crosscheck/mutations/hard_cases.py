"""Harder, fully-specified defect cases for the P2 difficulty probe.

Goal: test whether a controlled corpus can pull frontier models off the one-shot
ceiling (no-review ~0.4-0.6) so review workflows have headroom. Each bug is
SUBTLE but the spec + hidden test FULLY determine the intended behaviour (a
careful reader can fix it), so 0% would be a fair model failure, not a benchmark
bug. If models still one-shot these, P2 is HOLD (controlled corpus can't
discriminate frontier models; needs real multi-file repository tasks).
"""
from __future__ import annotations

from papers.p2_crosscheck.defects.taxonomy import DefectType
from papers.p2_crosscheck.mutations.injectors import MutationCase


def _t_binsearch(ns):
    f = ns["first_index"]
    assert f([1, 2, 2, 2, 3], 2) == 1          # leftmost, not any
    assert f([1, 2, 2, 2, 3], 4) == -1
    assert f([], 1) == -1
    assert f([5], 5) == 0


def _t_interval(ns):
    f = ns["merge_intervals"]
    assert f([[1, 2], [2, 3]]) == [[1, 3]]      # touching merges
    assert f([[1, 5], [2, 3]]) == [[1, 5]]
    assert f([[1, 2], [4, 5]]) == [[1, 2], [4, 5]]


def _t_roundhalfup(ns):
    f = ns["round_half_up"]
    assert f(2.5) == 3 and f(3.5) == 4          # half-UP, not banker's
    assert f(2.4) == 2 and f(-2.5) == -2        # -2.5 -> -2 (toward +inf on .5)


def _t_dedup(ns):
    f = ns["dedup"]
    assert f([3, 1, 3, 2, 1]) == [3, 1, 2]      # first-occurrence order preserved


def _t_pagination(ns):
    f = ns["page"]
    # 1-indexed page, size 3; page 2 of [1..7] -> [4,5,6]; page 3 -> [7]
    assert f(list(range(1, 8)), 2, 3) == [4, 5, 6]
    assert f(list(range(1, 8)), 3, 3) == [7]
    assert f(list(range(1, 8)), 4, 3) == []


def _t_lru(ns):
    LRU = ns["LRU"]
    c = LRU(2)
    c.put("a", 1); c.put("b", 2); c.get("a"); c.put("c", 3)  # 'b' is LRU -> evicted
    assert c.get("b") is None and c.get("a") == 1 and c.get("c") == 3


def hard_cases() -> list[MutationCase]:
    return [
        MutationCase(
            "hard_binsearch", "hard_repo", DefectType.BOUNDARY,
            "def first_index(a, x):\n"
            "    lo, hi = 0, len(a)\n"
            "    while lo < hi:\n"
            "        m = (lo + hi) // 2\n"
            "        if a[m] < x: lo = m + 1\n"
            "        else: hi = m\n"
            "    return lo if lo < len(a) and a[lo] == x else -1\n",
            "def first_index(a, x):\n"
            "    lo, hi = 0, len(a) - 1\n"
            "    while lo <= hi:\n"
            "        m = (lo + hi) // 2\n"
            "        if a[m] == x: return m\n"
            "        elif a[m] < x: lo = m + 1\n"
            "        else: hi = m - 1\n"
            "    return -1\n",
            _t_binsearch,
            description="first_index(sorted_list, x) must return the index of the FIRST "
                        "(leftmost) occurrence of x among duplicates, or -1 if absent. "
                        "E.g. first_index([1,2,2,2,3],2)==1."),
        MutationCase(
            "hard_interval", "hard_repo", DefectType.BOUNDARY,
            "def merge_intervals(iv):\n"
            "    iv = sorted(iv); out = []\n"
            "    for s, e in iv:\n"
            "        if out and s <= out[-1][1]: out[-1][1] = max(out[-1][1], e)\n"
            "        else: out.append([s, e])\n"
            "    return out\n",
            "def merge_intervals(iv):\n"
            "    iv = sorted(iv); out = []\n"
            "    for s, e in iv:\n"
            "        if out and s < out[-1][1]: out[-1][1] = max(out[-1][1], e)\n"
            "        else: out.append([s, e])\n"
            "    return out\n",
            _t_interval,
            description="merge_intervals must merge intervals that OVERLAP OR TOUCH "
                        "(share an endpoint): merge_intervals([[1,2],[2,3]])==[[1,3]]."),
        MutationCase(
            "hard_roundhalfup", "hard_repo", DefectType.TYPE_SERIALIZATION,
            "import math\n"
            "def round_half_up(x):\n"
            "    return math.floor(x + 0.5)\n",
            "def round_half_up(x):\n"
            "    return round(x)\n",
            _t_roundhalfup,
            description="round_half_up(x) must round to the nearest integer with ties going "
                        "toward +infinity (half-UP, NOT Python banker's rounding): "
                        "round_half_up(2.5)==3, round_half_up(-2.5)==-2."),
        MutationCase(
            "hard_dedup", "hard_repo", DefectType.REQUIREMENT_MISREAD,
            "def dedup(xs):\n"
            "    seen = set(); out = []\n"
            "    for x in xs:\n"
            "        if x not in seen: seen.add(x); out.append(x)\n"
            "    return out\n",
            "def dedup(xs):\n"
            "    return sorted(set(xs))\n",
            _t_dedup,
            description="dedup(xs) must remove duplicates while preserving the order of FIRST "
                        "occurrence: dedup([3,1,3,2,1])==[3,1,2]."),
        MutationCase(
            "hard_pagination", "hard_repo2", DefectType.BOUNDARY,
            "def page(items, p, size):\n"
            "    start = (p - 1) * size\n"
            "    return items[start:start + size]\n",
            "def page(items, p, size):\n"
            "    start = p * size\n"
            "    return items[start:start + size]\n",
            _t_pagination,
            description="page(items, p, size) returns the p-th page (p is 1-indexed) of `size` "
                        "items: page([1..7],2,3)==[4,5,6], page([1..7],3,3)==[7]."),
        MutationCase(
            "hard_lru", "hard_repo2", DefectType.STATE_ORDER,
            "class LRU:\n"
            "    def __init__(self, cap): self.cap=cap; self.d={}\n"
            "    def get(self, k):\n"
            "        if k not in self.d: return None\n"
            "        v=self.d.pop(k); self.d[k]=v; return v\n"
            "    def put(self, k, v):\n"
            "        if k in self.d: self.d.pop(k)\n"
            "        elif len(self.d)>=self.cap: self.d.pop(next(iter(self.d)))\n"
            "        self.d[k]=v\n",
            "class LRU:\n"
            "    def __init__(self, cap): self.cap=cap; self.d={}\n"
            "    def get(self, k):\n"
            "        return self.d.get(k)\n"
            "    def put(self, k, v):\n"
            "        if k in self.d: self.d.pop(k)\n"
            "        elif len(self.d)>=self.cap: self.d.pop(next(iter(self.d)))\n"
            "        self.d[k]=v\n",
            _t_lru,
            description="LRU(cap) is a least-recently-used cache. get(k) must COUNT as a use "
                        "(mark k most-recently-used); put evicts the least-recently-used when "
                        "full. After put a,put b,get a,put c -> 'b' is evicted."),
    ]
