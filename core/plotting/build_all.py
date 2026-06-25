"""Rebuild paper tables strictly from the run ledger (manual 3.1, 10.5).

`make reproduce-main-tables` calls this. Tier-0 implementation produces an
aggregate table per paper (n runs, status mix, success rate, cost) into
generated/<paper>/aggregate.csv so that NO number in a manuscript is hand-typed:
tables come only from the immutable ledger.
"""
from __future__ import annotations

import csv
import os

from core.experiment_registry.ledger import RunLedger, aggregate

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def build_aggregate_table(ledger_path: str, paper_id: str, out_dir: str) -> str:
    entries = [e for e in RunLedger(ledger_path).read_all()
               if e.get("paper_id") == paper_id]
    agg = aggregate(entries)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "aggregate.csv")
    with open(out_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["metric", "value"])
        w.writerow(["n_runs", agg["n_runs"]])
        w.writerow(["success_rate", agg["success_rate"]])
        w.writerow(["total_cost_usd", agg["total_cost_usd"]])
        for status, n in sorted(agg["by_status"].items()):
            w.writerow([f"status::{status}", n])
    return out_path


def build_all(repo_root: str | None = None) -> list[str]:
    repo_root = repo_root or _REPO_ROOT
    ledger_path = os.path.join(repo_root, "artifacts", "run_ledger.jsonl")
    written = []
    for p in ("p1_toolmorph", "p2_crosscheck", "p3_deltaresearch", "p4_harnessguard"):
        out_dir = os.path.join(repo_root, "generated", p)
        if os.path.exists(ledger_path):
            written.append(build_aggregate_table(ledger_path, p, out_dir))
    return written


if __name__ == "__main__":  # pragma: no cover
    for path in build_all():
        print("wrote", path)
