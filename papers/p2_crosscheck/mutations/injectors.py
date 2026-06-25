"""Self-contained toy "repositories" + deterministic defect injectors.

Each entry is a (defect, toy_repo, hidden_test) triple where:

- ``clean_source`` is a tiny pure-python module that PASSES its hidden test;
- ``mutated_source`` injects exactly ONE defect of a known ``DefectType``;
- ``hidden_test`` is a deterministic oracle that PASSES on the clean module and
  FAILS on the mutated one (manual 5.6 / 6.7: objective hidden tests are the
  primary, LLM-free endpoint).

No external repositories, no network, no randomness. Modules are materialised
either in-process (``run_hidden_test``) or to a temp dir (``materialize_case`` /
``run_case_in_dir``) for auditability. Ten triples cover all ten defect types;
the contract only requires >= 6.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Callable

from papers.p2_crosscheck.defects.taxonomy import DefectType


@dataclass(frozen=True)
class MutationCase:
    case_id: str
    repo_id: str          # the independent unit for repo-level splits / lineage
    defect: DefectType
    clean_source: str
    mutated_source: str
    hidden_test: Callable[[dict], None]   # raises on failure
    description: str = ""


# --------------------------------------------------------------------------
# Execution helpers (in-process and temp-dir).
# --------------------------------------------------------------------------
def _exec_module(source: str) -> dict:
    ns: dict = {"__name__": "toy_module"}
    exec(compile(source, "<toy_repo>", "exec"), ns)
    return ns


def run_hidden_test(case: MutationCase, variant: str) -> bool:
    """Run ``case``'s hidden test against the given variant in-process.

    ``variant`` is "clean" or "mutated". Returns True iff the hidden test
    PASSES (no exception). Any exception (assertion or runtime) -> False.
    """
    if variant not in ("clean", "mutated"):
        raise ValueError(f"variant must be 'clean' or 'mutated', got {variant!r}")
    source = case.clean_source if variant == "clean" else case.mutated_source
    try:
        ns = _exec_module(source)
        case.hidden_test(ns)
        return True
    except Exception:
        return False


def clean_passes(case: MutationCase) -> bool:
    return run_hidden_test(case, "clean")


def mutation_fails(case: MutationCase) -> bool:
    return not run_hidden_test(case, "mutated")


def materialize_case(case: MutationCase, root_dir: str, variant: str) -> str:
    """Write the chosen variant to ``root_dir/<case_id>_<variant>.py``; return path."""
    os.makedirs(root_dir, exist_ok=True)
    source = case.clean_source if variant == "clean" else case.mutated_source
    path = os.path.join(root_dir, f"{case.case_id}_{variant}.py")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(source)
    return path


def run_case_in_dir(case: MutationCase, root_dir: str, variant: str) -> bool:
    """Materialise the variant to disk, load it, and run the hidden test."""
    path = materialize_case(case, root_dir, variant)
    with open(path, "r", encoding="utf-8") as fh:
        source = fh.read()
    try:
        ns = _exec_module(source)
        case.hidden_test(ns)
        return True
    except Exception:
        return False


# --------------------------------------------------------------------------
# Hidden tests (deterministic oracles; raise on failure).
# --------------------------------------------------------------------------
def _t_boundary(ns: dict) -> None:
    f = ns["in_range"]
    assert f(5, 0, 10) is True
    assert f(0, 0, 10) is True
    assert f(10, 0, 10) is True   # inclusive upper boundary; mutant returns False
    assert f(11, 0, 10) is False


def _t_api_misuse(ns: dict) -> None:
    f = ns["add_item"]
    assert f({}, "a", 1) == {"a": 1}   # mutant returns dict.update(...) -> None


def _t_cross_file(ns: dict) -> None:
    pwt = ns["price_with_tax"]
    disp = ns["display_rate"]
    implied_pct = int(round((pwt(100.0) / 100.0 - 1.0) * 100))
    assert disp() == f"{implied_pct}%"   # price & advertised rate must agree


def _t_state_order(ns: dict) -> None:
    withdraw = ns["withdraw"]
    acc = {"bal": 100}
    try:
        withdraw(acc, 150)
    except ValueError:
        pass
    assert acc["bal"] == 100   # rejected withdrawal must not corrupt state


def _t_exception_omission(ns: dict) -> None:
    f = ns["parse_positive"]
    assert f("5") == 5
    raised = False
    try:
        f("-3")
    except ValueError:
        raised = True
    assert raised   # mutant silently returns -3


def _t_type_serialization(ns: dict) -> None:
    f = ns["to_payload"]
    blob = json.dumps(f([3, 1, 2]))   # mutant returns a set -> TypeError here
    assert json.loads(blob) == {"items": [1, 2, 3]}


def _t_requirement_misread(ns: dict) -> None:
    f = ns["rank"]
    # spec: sort by (length, then alphabetical); mutant sorts alphabetically only
    assert f(["bbb", "a", "cc"]) == ["a", "cc", "bbb"]


def _t_collateral_regression(ns: dict) -> None:
    dedup = ns["dedup"]
    # 'A' and ' a ' must stay distinct; mutant lower-cases normalize() and merges
    assert dedup(["A", " a ", "A"]) == ["A", "a"]


def _t_missing_test(ns: dict) -> None:
    median = ns["median"]
    assert median([1, 3, 2]) == 2.0
    assert median([1, 2, 3, 4]) == 2.5   # even-length case the mutant drops


def _t_perf(ns: dict) -> None:
    fib = ns["fib"]
    calls = ns["CALLS"]
    calls["n"] = 0
    assert fib(20) == 6765
    assert calls["n"] <= 100   # exponential (un-memoised) mutant blows the budget


# --------------------------------------------------------------------------
# The toy repositories (clean + mutated source).
# --------------------------------------------------------------------------
_CASES: list[MutationCase] = [
    MutationCase(
        case_id="boundary_in_range",
        repo_id="toyrepo_numeric",
        defect=DefectType.BOUNDARY,
        clean_source=(
            "def in_range(x, lo, hi):\n"
            "    return lo <= x <= hi\n"
        ),
        mutated_source=(
            "def in_range(x, lo, hi):\n"
            "    return lo <= x < hi\n"   # excludes the upper boundary
        ),
        hidden_test=_t_boundary,
        description="inclusive range check; mutant makes upper bound exclusive.",
    ),
    MutationCase(
        case_id="missing_test_median",
        repo_id="toyrepo_numeric",
        defect=DefectType.MISSING_TEST,
        clean_source=(
            "def median(xs):\n"
            "    s = sorted(xs)\n"
            "    n = len(s)\n"
            "    if n % 2 == 1:\n"
            "        return float(s[n // 2])\n"
            "    return (s[n // 2 - 1] + s[n // 2]) / 2.0\n"
        ),
        mutated_source=(
            "def median(xs):\n"
            "    s = sorted(xs)\n"
            "    n = len(s)\n"
            "    return float(s[n // 2])\n"   # wrong for even length
        ),
        hidden_test=_t_missing_test,
        description="median of even-length list; untested edge handled wrongly.",
    ),
    MutationCase(
        case_id="perf_fib_memo",
        repo_id="toyrepo_numeric",
        defect=DefectType.PERF,
        clean_source=(
            "CALLS = {'n': 0}\n"
            "def fib(n, memo=None):\n"
            "    CALLS['n'] += 1\n"
            "    if memo is None:\n"
            "        memo = {}\n"
            "    if n < 2:\n"
            "        return n\n"
            "    if n in memo:\n"
            "        return memo[n]\n"
            "    memo[n] = fib(n - 1, memo) + fib(n - 2, memo)\n"
            "    return memo[n]\n"
        ),
        mutated_source=(
            "CALLS = {'n': 0}\n"
            "def fib(n):\n"
            "    CALLS['n'] += 1\n"
            "    if n < 2:\n"
            "        return n\n"
            "    return fib(n - 1) + fib(n - 2)\n"   # memoisation removed
        ),
        hidden_test=_t_perf,
        description="memoised fibonacci; mutant drops memo (exponential work).",
    ),
    MutationCase(
        case_id="api_misuse_add_item",
        repo_id="toyrepo_collections",
        defect=DefectType.API_MISUSE,
        clean_source=(
            "def add_item(d, k, v):\n"
            "    d[k] = v\n"
            "    return d\n"
        ),
        mutated_source=(
            "def add_item(d, k, v):\n"
            "    return d.update({k: v})\n"   # dict.update returns None
        ),
        hidden_test=_t_api_misuse,
        description="returns updated dict; mutant returns dict.update()'s None.",
    ),
    MutationCase(
        case_id="requirement_misread_rank",
        repo_id="toyrepo_collections",
        defect=DefectType.REQUIREMENT_MISREAD,
        clean_source=(
            "def rank(words):\n"
            "    return sorted(words, key=lambda w: (len(w), w))\n"
        ),
        mutated_source=(
            "def rank(words):\n"
            "    return sorted(words)\n"   # ignores the length-first requirement
        ),
        hidden_test=_t_requirement_misread,
        description="sort by (length, alpha); mutant sorts alphabetically only.",
    ),
    MutationCase(
        case_id="type_serialization_payload",
        repo_id="toyrepo_collections",
        defect=DefectType.TYPE_SERIALIZATION,
        clean_source=(
            "def to_payload(items):\n"
            "    return {'items': sorted(items)}\n"
        ),
        mutated_source=(
            "def to_payload(items):\n"
            "    return {'items': set(items)}\n"   # not JSON-serialisable
        ),
        hidden_test=_t_type_serialization,
        description="JSON payload with a list; mutant emits a set.",
    ),
    MutationCase(
        case_id="state_order_withdraw",
        repo_id="toyrepo_banking",
        defect=DefectType.STATE_ORDER,
        clean_source=(
            "def withdraw(acc, amt):\n"
            "    if amt > acc['bal']:\n"
            "        raise ValueError('insufficient funds')\n"
            "    acc['bal'] -= amt\n"
            "    return acc['bal']\n"
        ),
        mutated_source=(
            "def withdraw(acc, amt):\n"
            "    acc['bal'] -= amt\n"   # mutate BEFORE validating
            "    if acc['bal'] < 0:\n"
            "        raise ValueError('insufficient funds')\n"
            "    return acc['bal']\n"
        ),
        hidden_test=_t_state_order,
        description="check-then-debit; mutant debits first, corrupting state on error.",
    ),
    MutationCase(
        case_id="exception_omission_parse",
        repo_id="toyrepo_banking",
        defect=DefectType.EXCEPTION_OMISSION,
        clean_source=(
            "def parse_positive(s):\n"
            "    v = int(s)\n"
            "    if v <= 0:\n"
            "        raise ValueError('must be positive')\n"
            "    return v\n"
        ),
        mutated_source=(
            "def parse_positive(s):\n"
            "    return int(s)\n"   # guard removed
        ),
        hidden_test=_t_exception_omission,
        description="raises on non-positive input; mutant drops the guard.",
    ),
    MutationCase(
        case_id="cross_file_tax_rate",
        repo_id="toyrepo_pricing",
        defect=DefectType.CROSS_FILE_INCONSISTENCY,
        clean_source=(
            "RATE = 0.2\n"
            "def price_with_tax(p):\n"
            "    return round(p * (1 + RATE), 2)\n"
            "def display_rate():\n"
            "    return str(int(RATE * 100)) + '%'\n"
        ),
        mutated_source=(
            "RATE = 0.2\n"
            "def price_with_tax(p):\n"
            "    return round(p * (1 + 0.25), 2)\n"   # drifts from RATE
            "def display_rate():\n"
            "    return str(int(RATE * 100)) + '%'\n"
        ),
        hidden_test=_t_cross_file,
        description="tax rate duplicated; mutant hard-codes a drifted literal.",
    ),
    MutationCase(
        case_id="collateral_regression_dedup",
        repo_id="toyrepo_textproc",
        defect=DefectType.COLLATERAL_REGRESSION,
        clean_source=(
            "def normalize(s):\n"
            "    return s.strip()\n"
            "def dedup(xs):\n"
            "    return sorted(set(normalize(x) for x in xs))\n"
        ),
        mutated_source=(
            "def normalize(s):\n"
            "    return s.strip().lower()\n"   # 'helpful' change breaks dedup()
            "def dedup(xs):\n"
            "    return sorted(set(normalize(x) for x in xs))\n"
        ),
        hidden_test=_t_collateral_regression,
        description="edit to normalize() silently changes dedup() semantics.",
    ),
]


def all_cases() -> list[MutationCase]:
    return list(_CASES)


def cases_by_defect() -> dict[DefectType, MutationCase]:
    return {c.defect: c for c in _CASES}


def repositories() -> list[str]:
    """Distinct toy-repository ids (the independent unit for splits)."""
    seen: list[str] = []
    for c in _CASES:
        if c.repo_id not in seen:
            seen.append(c.repo_id)
    return seen
