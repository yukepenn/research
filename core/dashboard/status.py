"""Automatic status dashboard (COMMON-010, manual section 20).

Reads program state + run ledger + artifact presence and renders the daily
research-status report in the manual's mandated format. Refuses to invent
progress: every paper line is derived from status.yaml and on-disk artifacts.
"""
from __future__ import annotations

import os

import yaml

from core.experiment_registry.ledger import RunLedger, aggregate

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PAPERS = ["p1_toolmorph", "p2_crosscheck", "p3_deltaresearch", "p4_harnessguard"]
GATE_ARTIFACTS = {
    "NOVELTY_PASS": ["novelty/related_work.csv", "novelty/novelty_matrix.md",
                     "novelty/novelty_attack.md"],
}


def _load_yaml(path: str) -> dict:
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def artifact_presence(repo_root: str) -> dict[str, dict[str, bool]]:
    out: dict[str, dict[str, bool]] = {}
    for p in PAPERS:
        base = os.path.join(repo_root, "papers", p)
        out[p] = {
            rel: os.path.exists(os.path.join(base, rel))
            for arts in GATE_ARTIFACTS.values() for rel in arts
        }
    return out


def build_status_report(repo_root: str | None = None, ledger_path: str | None = None) -> str:
    repo_root = repo_root or _REPO_ROOT
    status = _load_yaml(os.path.join(repo_root, "program", "status.yaml"))
    budget = _load_yaml(os.path.join(repo_root, "program", "budget.yaml"))
    deadlines = _load_yaml(os.path.join(repo_root, "program", "deadlines.yaml"))
    portfolio = status.get("portfolio", {})
    presence = artifact_presence(repo_root)

    lp = ledger_path or os.path.join(repo_root, "artifacts", "run_ledger.jsonl")
    agg = aggregate(RunLedger(lp).read_all()) if os.path.exists(lp) else {
        "n_runs": 0, "by_status": {}, "total_cost_usd": 0.0, "success_rate": None}

    lines = [f"# Research Status — {status.get('program_date', 'n/a')}", "", "## Portfolio"]
    for p in PAPERS:
        st = portfolio.get(p, {})
        lines.append(f"- {p}: {st.get('state', '?')}, confidence {st.get('confidence', '?')}, "
                     f"next_gate {st.get('next_gate', '?')}")
    lines += ["", "## Novelty artifacts (gate inputs)"]
    for p in PAPERS:
        done = sum(presence[p].values())
        total = len(presence[p])
        lines.append(f"- {p}: {done}/{total} novelty artifacts present")
    lines += ["", "## Evidence ledger",
              f"- runs: {agg['n_runs']}  |  by_status: {agg['by_status']}  "
              f"|  cost: ${agg['total_cost_usd']}",
              "", "## Budget",
              f"- state: {status.get('common', {}).get('budget_state', '?')}  "
              f"(portfolio_limit: {budget.get('portfolio_limit')})",
              "", "## Deadlines (verified official)"]
    for v, meta in (deadlines.get("venues", {}) or {}).items():
        lines.append(f"- {v}: {meta.get('paper', meta.get('papers'))} "
                     f"-> {meta.get('full_submission_aoe', meta.get('submission', meta.get('deadline', meta.get('schedule', 'n/a'))))} "
                     f"[{meta.get('status')}]")
    hd = status.get("human_decisions_required", []) or []
    lines += ["", "## Human decisions required"]
    lines += [f"- {h}" for h in hd] if hd else ["- none"]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":  # pragma: no cover
    print(build_status_report())
