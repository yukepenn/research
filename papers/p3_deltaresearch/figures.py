"""Generate P3 figures strictly from the run ledger (no hand-typed numbers).

Fig 1: affected-claim recall (ACR) by arm x model (naive vs no-gold pipeline vs oracle).
Fig 2: ACR vs harmful-edit frontier.
Outputs PDF+PNG to paper/figures/generated/.
"""
from __future__ import annotations

import os
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from core.experiment_registry.ledger import RunLedger  # noqa: E402

_OUT = os.path.join(os.path.dirname(__file__), "paper", "figures", "generated")


def _agg(ledger_path):
    by = defaultdict(lambda: defaultdict(list))
    for e in RunLedger(ledger_path).read_all():
        r = e.get("result", {})
        if "acr" not in r:
            continue
        key = (r["arm"], e["model_id"].split(":")[0])
        by[key]["acr"].append(r["acr"]); by[key]["harmful"].append(r.get("harmful", 0))
    return {k: {m: sum(v) / len(v) for m, v in d.items()} for k, d in by.items()}


def build(ledger_path="artifacts/p3v2_ledger.jsonl"):
    os.makedirs(_OUT, exist_ok=True)
    agg = _agg(ledger_path)
    arms = ["naive_llm", "pipeline_nogold"]
    models = sorted({k[1] for k in agg})
    # Fig 1: grouped bars ACR
    fig, ax = plt.subplots(figsize=(5.2, 3.2))
    x = range(len(arms))
    w = 0.35
    for i, m in enumerate(models):
        vals = [agg.get((a, m), {}).get("acr", 0) for a in arms]
        ax.bar([xi + i * w for xi in x], vals, w, label=m)
    ax.set_xticks([xi + w / 2 for xi in x])
    ax.set_xticklabels(["naive LLM", "no-gold ClaimPatch"])
    ax.set_ylabel("Affected-claim recall (ACR)")
    ax.set_ylim(0, 1.05)
    ax.set_title("No-gold ClaimPatch vs naive (controlled, named reports)")
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(_OUT, f"fig_acr_by_arm.{ext}"), dpi=150)
    plt.close(fig)

    # Fig 2: ACR vs harmful-edit frontier
    fig2, ax2 = plt.subplots(figsize=(4.6, 3.4))
    for (arm, m), d in agg.items():
        ax2.scatter(d.get("harmful", 0), d.get("acr", 0), s=60,
                    marker="o" if "pipeline" in arm else "x")
        ax2.annotate(f"{arm.split('_')[0]}/{m}", (d.get("harmful", 0), d.get("acr", 0)),
                     fontsize=7, xytext=(3, 3), textcoords="offset points")
    ax2.set_xlabel("Harmful-edit rate (lower better)")
    ax2.set_ylabel("ACR (higher better)")
    ax2.set_xlim(-0.05, 1.0); ax2.set_ylim(0, 1.05)
    ax2.set_title("Recall vs harmful-edit frontier")
    fig2.tight_layout()
    for ext in ("pdf", "png"):
        fig2.savefig(os.path.join(_OUT, f"fig_frontier.{ext}"), dpi=150)
    plt.close(fig2)
    return sorted(os.listdir(_OUT))


if __name__ == "__main__":  # pragma: no cover
    print("wrote:", build())
