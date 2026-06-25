"""Subscription-billed CLI model access (NO extra API cost).

Drives the locally-installed `claude` and `codex` CLIs non-interactively to get a
model completion. Used for the PLAN-THEN-EXECUTE evaluation protocol: the model
is given a task + tool schemas and returns a JSON tool-call plan, which the
harness executes against its own deterministic environment + oracle. Because the
harness (ours) is identical across models and we do not use the CLIs' agentic
loops, this is a unified-harness evaluation, not a product-harness one.

Cost: these consume the user's Claude / Codex subscription limits, not metered
API dollars. Every call is still logged to the run ledger with the detected
model id, so provenance is preserved.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass

_SCRATCH = tempfile.gettempdir()


@dataclass
class CLIResult:
    text: str
    model_id: str
    ok: bool
    raw: str


def cli_available(model: str) -> bool:
    exe = "claude" if model.startswith("claude") else "codex"
    return shutil.which(exe) is not None


def _run(cmd: list[str], prompt: str, timeout: int) -> tuple[str, int]:
    proc = subprocess.run(cmd, input=prompt, capture_output=True, text=True,
                          timeout=timeout, cwd=_SCRATCH, encoding="utf-8", errors="ignore")
    return (proc.stdout or "") + ("\n" + proc.stderr if proc.returncode else ""), proc.returncode


def cli_complete(model: str, prompt: str, *, timeout: int = 180) -> CLIResult:
    """Return a single completion from the given model via its CLI.

    model: "claude" (Claude Code CLI) or "codex" (Codex CLI / gpt-5.5).
    """
    if model.startswith("claude"):
        # claude reads the prompt as arg; --output-format text => bare text
        out, rc = _run(["claude", "-p", prompt, "--output-format", "text"], "", timeout)
        return CLIResult(text=out.strip(), model_id="claude-cli", ok=(rc == 0), raw=out)
    if model.startswith("codex"):
        # codex is an npm shim (codex.cmd/.ps1) -> launch via cmd on Windows and
        # feed the prompt on STDIN (avoids arg-quoting of multi-line JSON prompts)
        base = ["codex", "exec", "--skip-git-repo-check"]
        cmd = (["cmd", "/c"] + base) if os.name == "nt" else base
        out, rc = _run(cmd, prompt, timeout)  # prompt via stdin
        mid = "codex-cli"
        m = re.search(r"^model:\s*(\S+)", out, re.MULTILINE)
        if m:
            mid = m.group(1)
        return CLIResult(text=out, model_id=mid, ok=(rc == 0), raw=out)
    raise ValueError(f"unknown CLI model {model!r}")


_FENCE = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL)


def extract_json_plan(text: str) -> list[dict] | None:
    """Extract the last valid JSON array-of-objects from `text` (tolerates code
    fences and surrounding prose / CLI logging)."""
    candidates: list[str] = []
    for m in _FENCE.finditer(text):
        candidates.append(m.group(1).strip())
    # also scan for raw bracketed arrays (balanced)
    depth = 0
    start = -1
    for i, ch in enumerate(text):
        if ch == "[":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0 and start >= 0:
                candidates.append(text[start:i + 1])
                start = -1
    plan = None
    for cand in candidates:
        try:
            val = json.loads(cand)
        except (json.JSONDecodeError, ValueError):
            continue
        if isinstance(val, list) and all(isinstance(x, dict) for x in val):
            plan = val  # keep the last valid one
    return plan
