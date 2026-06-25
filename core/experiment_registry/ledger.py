"""Immutable run ledger.

Every model call / episode the program reports a number from MUST originate
here (manual section 1.1, 3.1). The ledger is append-only JSONL; each entry is
validated against a JSON schema before it is written, and raw traces are stored
content-addressed so an entry can only reference a trace by its sha256.

Design choices:
- Append-only: we never rewrite a line. `verify()` re-validates the whole file
  and flags duplicate run_ids or schema drift.
- Self-describing: the authoritative schema lives in
  `templates/run_ledger.schema.json`; we load it at runtime and also expose a
  richer superset of optional fields from manual 3.1.
"""
from __future__ import annotations

import json
import os
from typing import Any, Iterable

import jsonschema

from core.util import canonical_json, sha256_text, utc_now_iso, write_content_addressed

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCHEMA_PATH = os.path.join(_REPO_ROOT, "templates", "run_ledger.schema.json")

# Status values that count as a genuine agent outcome vs an infra exclusion.
TERMINAL_STATUSES = {"SUCCESS", "AGENT_FAILURE", "INFRA_FAILURE", "TIMEOUT",
                     "COST_LIMIT", "REFUSAL", "EXCLUDED"}


def load_schema() -> dict:
    with open(SCHEMA_PATH, "r", encoding="utf-8") as fh:
        return json.load(fh)


class LedgerError(RuntimeError):
    pass


class RunLedger:
    """Append-only JSONL ledger with schema validation."""

    def __init__(self, path: str, trace_dir: str | None = None):
        self.path = path
        self.trace_dir = trace_dir or os.path.join(os.path.dirname(path), "traces")
        self._schema = load_schema()
        self._validator = jsonschema.Draft202012Validator(self._schema)
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)

    # ---- writing -------------------------------------------------------
    def store_trace(self, trace: Any) -> str:
        """Persist a raw trace content-addressed; return its sha256 hash."""
        payload = canonical_json(trace)
        digest, _ = write_content_addressed(self.trace_dir, payload)
        return digest

    def append(self, entry: dict) -> str:
        """Validate and append one entry. Returns the run_id."""
        entry = dict(entry)
        entry.setdefault("started_at", utc_now_iso())
        if "run_id" not in entry:
            raise LedgerError("entry requires a run_id (use make_entry to build one)")
        errors = sorted(self._validator.iter_errors(entry), key=lambda e: e.path)
        if errors:
            msgs = "; ".join(f"{list(e.path)}: {e.message}" for e in errors[:5])
            raise LedgerError(f"ledger entry failed schema validation: {msgs}")
        if entry["run_id"] in self._existing_ids():
            raise LedgerError(f"duplicate run_id {entry['run_id']} (ledger is append-only)")
        with open(self.path, "a", encoding="utf-8") as fh:
            fh.write(canonical_json(entry) + "\n")
        return entry["run_id"]

    # ---- reading -------------------------------------------------------
    def read_all(self) -> list[dict]:
        if not os.path.exists(self.path):
            return []
        out = []
        with open(self.path, "r", encoding="utf-8") as fh:
            for ln in fh:
                ln = ln.strip()
                if ln:
                    out.append(json.loads(ln))
        return out

    def _existing_ids(self) -> set[str]:
        return {e.get("run_id") for e in self.read_all()}

    # ---- integrity -----------------------------------------------------
    def verify(self) -> tuple[bool, list[str]]:
        """Re-validate every entry; detect duplicates and missing traces."""
        problems: list[str] = []
        seen: set[str] = set()
        for i, entry in enumerate(self.read_all()):
            for e in self._validator.iter_errors(entry):
                problems.append(f"line {i}: schema: {list(e.path)} {e.message}")
            rid = entry.get("run_id")
            if rid in seen:
                problems.append(f"line {i}: duplicate run_id {rid}")
            seen.add(rid)
            th = entry.get("raw_trace_hash")
            if th and self.trace_dir and not os.path.exists(
                os.path.join(self.trace_dir, f"{th}.json")
            ):
                problems.append(f"line {i}: missing trace file for {th}")
        return (len(problems) == 0, problems)


def make_entry(
    *,
    run_id: str,
    paper_id: str,
    git_commit: str,
    task_hash: str,
    environment_hash: str,
    model_provider: str,
    model_id: str,
    harness_hash: str,
    oracle_version: str,
    raw_trace_hash: str,
    status: str = "SUCCESS",
    **optional: Any,
) -> dict:
    """Build a schema-valid ledger entry with required fields + optionals.

    Optional keys (token_input, token_output, cost_usd, latency_seconds, seed,
    result, model_snapshot_date, system_prompt_hash, tool_schema_hash,
    rerun_of, notes, ...) pass straight through.
    """
    if status not in TERMINAL_STATUSES:
        raise LedgerError(f"unknown status {status!r}; allowed: {sorted(TERMINAL_STATUSES)}")
    entry = {
        "run_id": run_id,
        "paper_id": paper_id,
        "git_commit": git_commit,
        "task_hash": task_hash,
        "environment_hash": environment_hash,
        "model_provider": model_provider,
        "model_id": model_id,
        "harness_hash": harness_hash,
        "oracle_version": oracle_version,
        "raw_trace_hash": raw_trace_hash,
        "started_at": utc_now_iso(),
        "status": status,
    }
    entry.update(optional)
    return entry


def aggregate(entries: Iterable[dict]) -> dict:
    """Cheap aggregate used by the dashboard: counts, cost, success rate."""
    entries = list(entries)
    n = len(entries)
    by_status: dict[str, int] = {}
    cost = 0.0
    for e in entries:
        by_status[e.get("status", "?")] = by_status.get(e.get("status", "?"), 0) + 1
        cost += float(e.get("cost_usd") or 0.0)
    succ = by_status.get("SUCCESS", 0)
    scored = sum(by_status.get(s, 0) for s in ("SUCCESS", "AGENT_FAILURE"))
    return {
        "n_runs": n,
        "by_status": by_status,
        "total_cost_usd": round(cost, 6),
        "success_rate": (succ / scored) if scored else None,
    }
