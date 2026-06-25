"""Seed the citation DB with sources.

Integrity rule (manual 12.4): verified=True ONLY for sources the Research Director
personally opened and checked against the original. Agent-cited secondary papers are
stored verified=False (pending Director re-verification before any manuscript citation).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.citations.db import CitationDB, Source  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(REPO, "artifacts", "citations.sqlite")
BIB_PATH = os.path.join(REPO, "program", "references.bib")

# (source_id, title, authors, year, venue, url, director_verified)
DIRECTOR_VERIFIED = [
    ("ahe2026", "Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses",
     "Lin et al.", "2026", "arXiv preprint", "https://arxiv.org/abs/2604.25850", True),
    ("mrdre2026", "Beyond Single-shot Writing: Deep Research Agents are Unreliable at Multi-turn Report Revision",
     "Chen et al.", "2026", "arXiv preprint", "https://arxiv.org/abs/2601.13217", True),
    ("tscg2026", "TSCG: Deterministic Tool-Schema Compilation for Agentic LLM Deployments",
     "Sakizli", "2026", "arXiv preprint", "https://arxiv.org/abs/2605.04107", True),
    ("refutepromote2026", "Refute-or-Promote: An Adversarial Stage-Gated Multi-Agent Review Methodology",
     "Agarwal", "2026", "arXiv preprint", "https://arxiv.org/abs/2604.19049", True),
    ("codeasharness2026", "Code as Agent Harness",
     "Ning et al.", "2026", "arXiv preprint", "https://arxiv.org/abs/2605.18747", True),
    ("pipe2026", "What Do Agents Learn from Trajectory-SFT: Semantics or Interfaces? (PIPE)",
     "Gu et al.", "2026", "arXiv preprint", "https://arxiv.org/abs/2602.01611", True),
    ("editpropbench2026", "EditPropBench: Measuring Factual Edit Propagation in Scientific Manuscripts",
     "Kruthof", "2026", "arXiv preprint", "https://arxiv.org/abs/2605.02083", True),
    ("agentassay2026", "AgentAssay: Token-Efficient Regression Testing for Non-Deterministic AI Agent Workflows",
     "Bhardwaj", "2026", "arXiv preprint", "https://arxiv.org/abs/2603.02601", True),
    ("cc02xiang2026", "Cross-Model LLM Code Review: Should you use Claude to review Codex or vice versa?",
     "Xiang, Zhang, Zhang, Xu", "2026", "KDD'26 Agentic-SE workshop",
     "https://www.researchgate.net/publication/407032793", True),
]

# Agent-cited, NOT yet Director-verified -> verified=False, must be checked before citing.
PENDING = [
    ("schemafirst2026", "Schema First (identical tool semantics/info content)", "unknown", "2026",
     "arXiv (agent-cited, pending verification)", "https://arxiv.org/abs/2603.13404", False),
    ("semanticinvariance2026", "Semantic Invariance in Agentic AI", "unknown", "2026",
     "arXiv (agent-cited, pending verification)", "https://arxiv.org/abs/2603.13173", False),
    ("rewritetooldesc2026", "Learning to Rewrite Tool Descriptions", "unknown", "2026",
     "arXiv (agent-cited, pending verification)", "https://arxiv.org/abs/2602.20426", False),
    ("tdad2026", "TDAD: pre-change impact-analysis test selection for coding agents", "unknown", "2026",
     "arXiv (agent-cited, pending verification)", "https://arxiv.org/abs/2603.17973", False),
    ("riskawarebatch2026", "Risk-Aware Batch Testing", "unknown", "2026",
     "arXiv (agent-cited, pending verification)", "https://arxiv.org/abs/2604.00222", False),
    ("hundredinstances2024", "100 Instances (selection vs random for fine-grained deltas)", "unknown", "2024",
     "arXiv (agent-cited, pending verification)", "https://arxiv.org/abs/2409.03563", False),
    ("microbench2025", "Micro-Benchmarking Reliability", "unknown", "2025",
     "arXiv (agent-cited, pending verification)", "https://arxiv.org/abs/2510.08730", False),
    ("selfharness2026", "Self-Harness (self-evolving harness w/ regression gate)", "unknown", "2026",
     "arXiv (agent-cited, pending verification)", "https://arxiv.org/abs/2606.09498", False),
]


def main():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    db = CitationDB(DB_PATH)
    for sid, title, authors, year, venue, url, verified in DIRECTOR_VERIFIED + PENDING:
        db.add(Source(source_id=sid, title=title, authors=authors, year=year,
                      venue_or_status=venue, url=url, verified=False))
        if verified:
            db.mark_verified(sid)
    with open(BIB_PATH, "w", encoding="utf-8") as fh:
        fh.write("% Auto-generated from verified citation DB. Only Director-verified sources.\n\n")
        fh.write(db.to_bibtex() + "\n")
    print(f"verified sources: {len(db.all()) - len(db.unverified())} / {len(db.all())}")
    print(f"DB: {DB_PATH}")
    print(f"BibTeX: {BIB_PATH}")


if __name__ == "__main__":
    main()
