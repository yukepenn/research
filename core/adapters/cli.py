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

from core.adapters.base import ModelAdapter, ModelResponse, ToolCall

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


def describe_tool_schema(schema: dict) -> str:
    props = schema.get("properties", {})
    required = set(schema.get("required", []))
    parts = []
    for k, spec in props.items():
        t = spec.get("type", "any")
        extra = f" one of {spec['enum']}" if "enum" in spec else ""
        if t == "object" and "properties" in spec:
            inner = ", ".join(f"{ik}:{iv.get('type','any')}"
                              for ik, iv in spec["properties"].items())
            extra = f" {{{inner}}}"
        parts.append(f"{k}:{t}{extra}{'' if k in required else ' (optional)'}")
    return ", ".join(parts) if parts else "(no arguments)"


def _extract_object(text: str):
    depth = 0
    start = -1
    last = None
    for i, ch in enumerate(text):
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start >= 0:
                try:
                    val = json.loads(text[start:i + 1])
                    if isinstance(val, dict):
                        last = val
                except (json.JSONDecodeError, ValueError):
                    pass
                start = -1
    return last


class CLIChatAdapter(ModelAdapter):
    """A ModelAdapter that drives `claude`/`codex` interactively, one tool call per
    step, by re-serialising the conversation each turn (the CLIs are stateless to
    us). This removes single-shot confounds (e.g. unseen server-assigned ids):
    the model sees each tool result before choosing the next action."""

    provider = "cli_subscription"

    def __init__(self, cli_model: str, *, timeout: int = 150, **kw):
        super().__init__(model_id=cli_model, **kw)
        self.cli_model = cli_model
        self.timeout = timeout
        self.detected_model_id = cli_model

    def _render(self, messages, tools) -> str:
        sys = next((m.content for m in messages if m.role == "system"), "")
        lines = [sys, "", "Available tools:"]
        for t in tools:
            lines.append(f"- {t.name}({describe_tool_schema(t.schema)}): {t.description}")
        lines.append("\nConversation so far:")
        for m in messages:
            if m.role == "user":
                lines.append(f"TASK: {m.content}")
            elif m.role == "assistant" and m.content:
                lines.append(f"assistant: {m.content}")
            elif m.role == "tool":
                lines.append(f"tool[{m.name}] -> {m.content}")
        lines.append(
            '\nChoose the NEXT single tool call to make progress. Use the EXACT tool and '
            "argument names listed, and use ids returned by previous tool calls. "
            'Output ONLY one JSON object: {"tool": <name>, "args": {<map>}}. '
            'If the task is already fully complete, output {"done": true}.')
        return "\n".join(lines)

    def generate(self, messages, tools=None, **params) -> ModelResponse:
        tools = list(tools or [])
        prompt = self._render(messages, tools)
        res = cli_complete(self.cli_model, prompt, timeout=self.timeout)
        self.detected_model_id = res.model_id
        obj = _extract_object(res.text) or {}
        if obj.get("done") or "tool" not in obj:
            return ModelResponse(text=str(obj.get("text", "done")), finish_reason="stop",
                                 raw=res.raw[:4000])
        step = sum(1 for m in messages if m.role == "tool")
        tc = ToolCall(name=obj.get("tool", ""), arguments=obj.get("args", {}) or {},
                      call_id=f"c{step}")
        return ModelResponse(tool_calls=[tc], raw=res.raw[:4000])


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
