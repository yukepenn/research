"""P2 plan-then-repair pilot using subscription CLI models (no API cost).

For each controlled defective module: an AUTHOR model produces a fix; we run the
deterministic HIDDEN TEST for final correctness. We compare, at MATCHED budget
(2 model calls each), the decisive arm cc02 lacks:

  NO_REVIEW              author fixes once (1 call)
  AUTHOR_MORE_COMPUTE    author fixes, then self-improves its own fix (2 calls)
  CROSS_FAMILY_REVIEW    author fixes, then a DIFFERENT model repairs it (2 calls)

Run bidirectionally (claude<->codex). The headline question (H2): does cross-family
review beat giving the same author equal extra compute? Final correctness is a
deterministic hidden test (LLM-free primary endpoint).
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass

from core.adapters.cli import cli_available, cli_complete
from core.experiment_registry.ledger import RunLedger, make_entry
from core.util import sha256_obj, short_id
from papers.p2_crosscheck.mutations.injectors import _exec_module, all_cases

HARNESS = "p2_plan_repair_v1"
ORACLE_VERSION = "p2_hidden_test_v1"

_CODE_FENCE = re.compile(r"```(?:python|py)?\s*(.*?)```", re.DOTALL)


def extract_code(text: str) -> str:
    blocks = _CODE_FENCE.findall(text)
    if blocks:
        return max(blocks, key=len).strip()
    return text.strip()


def correct(case, source: str) -> bool:
    try:
        ns = _exec_module(source)
        case.hidden_test(ns)
        return True
    except Exception:
        return False


def _author_prompt(case) -> str:
    return (
        "You are a software engineer. The Python module below has a defect. Fix it so it "
        f"satisfies the spec.\nSPEC: {case.description}\n\nMODULE:\n```python\n"
        f"{case.mutated_source}\n```\n\n"
        "Return ONLY the complete corrected module as one python code block. Keep all "
        "function names and signatures unchanged.")


def _improve_prompt(case, code) -> str:
    return (
        f"Review and improve your own fix. SPEC: {case.description}\n\nYour current module:\n"
        f"```python\n{code}\n```\n\nIf it still has any defect, return the fully corrected "
        "module; otherwise return it unchanged. Return ONLY one python code block.")


def _review_prompt(case, code) -> str:
    return (
        f"You are reviewing a colleague's fix. SPEC: {case.description}\n\nTheir module:\n"
        f"```python\n{code}\n```\n\nIf it still has a defect, return the fully corrected "
        "module; otherwise return it unchanged. Return ONLY one python code block.")


@dataclass
class P2Outcome:
    author: str
    reviewer: str
    workflow: str
    case_id: str
    defect: str
    final_correct: bool
    n_calls: int


def _log(ledger, author, reviewer, workflow, case, correct_flag, n_calls, trace, git_commit):
    th = ledger.store_trace(trace)
    ledger.append(make_entry(
        run_id=short_id(author, reviewer, workflow, case.case_id, HARNESS),
        paper_id="p2_crosscheck", git_commit=git_commit,
        task_hash=sha256_obj(case.case_id)[:12], environment_hash=sha256_obj(case.repo_id),
        model_provider="cli_subscription", model_id=f"author={author};reviewer={reviewer}",
        harness_hash=HARNESS, oracle_version=ORACLE_VERSION, raw_trace_hash=th,
        status="SUCCESS", cost_usd=0.0,
        result={"workflow": workflow, "final_correct": correct_flag,
                "defect": str(case.defect), "n_calls": n_calls},
        notes="P2 plan-then-repair pilot (subscription CLI)"))


def run_case(author, reviewer, case, *, ledger, git_commit, timeout=180) -> list[P2Outcome]:
    out = []
    a1 = extract_code(cli_complete(author, _author_prompt(case), timeout=timeout).text)
    c1 = correct(case, a1)
    _log(ledger, author, reviewer, "no_review", case, c1, 1,
         {"author_fix": a1[:6000]}, git_commit)
    out.append(P2Outcome(author, "-", "no_review", case.case_id, str(case.defect), c1, 1))

    # author extra compute: self-improve (2 calls), matched budget
    a2 = extract_code(cli_complete(author, _improve_prompt(case, a1), timeout=timeout).text)
    c2 = correct(case, a2)
    _log(ledger, author, author, "author_more_compute", case, c2, 2,
         {"author_fix": a1[:4000], "self_improved": a2[:4000]}, git_commit)
    out.append(P2Outcome(author, author, "author_more_compute", case.case_id,
                         str(case.defect), c2, 2))

    # cross-family review: different model repairs (2 calls), matched budget
    r1 = extract_code(cli_complete(reviewer, _review_prompt(case, a1), timeout=timeout).text)
    c3 = correct(case, r1)
    _log(ledger, author, reviewer, "cross_family_review", case, c3, 2,
         {"author_fix": a1[:4000], "reviewer_repair": r1[:4000]}, git_commit)
    out.append(P2Outcome(author, reviewer, "cross_family_review", case.case_id,
                         str(case.defect), c3, 2))
    return out


def run_pilot(pairs, *, cases=None, ledger_path: str, git_commit="uncommitted",
              timeout=180) -> dict:
    """pairs: list of (author_model, reviewer_model). Runs the bidirectional matrix."""
    cases = cases if cases is not None else all_cases()
    ledger = RunLedger(ledger_path)
    rows: list[P2Outcome] = []
    for author, reviewer in pairs:
        if not (cli_available(author) and cli_available(reviewer)):
            continue
        for case in cases:
            rows.extend(run_case(author, reviewer, case, ledger=ledger,
                                 git_commit=git_commit, timeout=timeout))

    # aggregate final correctness by workflow (and by author for the matrix)
    agg = {}
    for r in rows:
        key = r.workflow
        agg.setdefault(key, []).append(r.final_correct)
    summary = {k: {"final_correct_rate": sum(v) / len(v), "n": len(v)} for k, v in agg.items()}
    by_author = {}
    for r in rows:
        by_author.setdefault(f"{r.author}:{r.workflow}", []).append(r.final_correct)
    matrix = {k: sum(v) / len(v) for k, v in by_author.items()}
    return {"by_workflow": summary, "by_author_workflow": matrix, "n_episodes": len(rows)}


if __name__ == "__main__":  # pragma: no cover
    import argparse
    import os
    ap = argparse.ArgumentParser()
    ap.add_argument("--pairs", default="claude:codex,codex:claude")
    ap.add_argument("--ledger", default="artifacts/run_ledger.jsonl")
    args = ap.parse_args()
    pairs = [tuple(p.split(":")) for p in args.pairs.split(",")]
    commit = os.popen("git rev-parse --short HEAD").read().strip() or "uncommitted"
    out = run_pilot(pairs, ledger_path=args.ledger, git_commit=commit)
    print(json.dumps({"by_workflow": out["by_workflow"],
                      "by_author_workflow": out["by_author_workflow"]}, indent=2))
    print(f"episodes: {out['n_episodes']}")
