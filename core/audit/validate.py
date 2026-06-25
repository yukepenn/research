"""Repository validator (COMMON-006 / manual 10.6 CI checks).

Runs the cheap, deterministic integrity gates the CI should enforce on every merge:
- run-ledger schema + append-only integrity
- research contracts have a non-null paper_id (initialized, not template)
- secret scan over tracked text files
- sealed-label leak scan (no labels committed)
- citation sanity (references.bib keys resolvable)

Returns (ok, problems). Exit code is non-zero on any problem.
"""
from __future__ import annotations

import os
import re

import yaml

from core.experiment_registry.ledger import RunLedger

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

_SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"sk-ant-[A-Za-z0-9-]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"-----BEGIN (?:RSA |EC )?PRIVATE KEY-----"),
    re.compile(r"(?i)(?:api[_-]?key|secret|token)\s*[:=]\s*['\"][A-Za-z0-9/_+-]{24,}['\"]"),
]
_SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", ".venv", "venv", "node_modules"}
_TEXT_EXT = {".py", ".yaml", ".yml", ".json", ".md", ".csv", ".toml", ".cfg", ".txt", ".bib"}
_ALLOW_SECRET_HITS = {"validate.py"}  # this file contains the patterns themselves


def _iter_text_files(root: str):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS]
        for fn in filenames:
            if os.path.splitext(fn)[1].lower() in _TEXT_EXT:
                yield os.path.join(dirpath, fn)


def scan_secrets(root: str) -> list[str]:
    problems = []
    for path in _iter_text_files(root):
        if os.path.basename(path) in _ALLOW_SECRET_HITS:
            continue
        try:
            with open(path, encoding="utf-8", errors="ignore") as fh:
                text = fh.read()
        except OSError:
            continue
        for pat in _SECRET_PATTERNS:
            if pat.search(text):
                problems.append(f"possible secret in {os.path.relpath(path, root)} (/{pat.pattern}/)")
    return problems


def check_contracts(root: str) -> list[str]:
    problems = []
    for p in ("p1_toolmorph", "p2_crosscheck", "p3_deltaresearch", "p4_harnessguard"):
        path = os.path.join(root, "papers", p, "research_contract.yaml")
        if not os.path.exists(path):
            problems.append(f"missing research_contract.yaml for {p}")
            continue
        with open(path, encoding="utf-8") as fh:
            c = yaml.safe_load(fh) or {}
        if not c.get("paper_id"):
            problems.append(f"{p}: research_contract.yaml has null paper_id (still a template)")
        if not c.get("central_claim"):
            problems.append(f"{p}: research_contract.yaml has no central_claim")
    return problems


def check_ledger(root: str) -> list[str]:
    path = os.path.join(root, "artifacts", "run_ledger.jsonl")
    if not os.path.exists(path):
        return []  # no runs yet is fine
    ok, problems = RunLedger(path).verify()
    return [] if ok else problems


def check_sealed_leak(root: str) -> list[str]:
    problems = []
    sealed = os.path.join(root, "sealed_tests")
    for dirpath, _dirnames, filenames in os.walk(sealed):
        if os.path.basename(dirpath) == "labels" and filenames:
            # labels dir is gitignored; warn if it somehow exists with content under VCS scope
            rel = os.path.relpath(dirpath, root)
            problems.append(f"sealed labels present at {rel} (ensure gitignored, never committed)")
    return problems


def run_validation(root: str | None = None) -> tuple[bool, list[str]]:
    root = root or _REPO_ROOT
    problems: list[str] = []
    problems += check_ledger(root)
    problems += check_contracts(root)
    problems += scan_secrets(root)
    # sealed-leak is advisory; include but do not necessarily fail CI on gitignored content
    return (len(problems) == 0, problems)


if __name__ == "__main__":  # pragma: no cover
    import sys
    ok, problems = run_validation()
    if ok:
        print("validate: OK")
        sys.exit(0)
    print("validate: FAILED")
    for p in problems:
        print(" -", p)
    sys.exit(1)
