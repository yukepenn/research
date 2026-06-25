"""Lightweight, deterministic token estimation for dry-run costing.

This is a heuristic (~4 chars/token) used ONLY for budget dry-runs and for the
mock adapter. Real adapters report exact provider usage. The manual forbids
treating estimates as ground truth (1.1), so cost reports clearly label
estimated vs metered tokens.
"""
from __future__ import annotations

import math
from typing import Any

from core.util import canonical_json

CHARS_PER_TOKEN = 4.0


def estimate_tokens_text(text: str) -> int:
    if not text:
        return 0
    return max(1, math.ceil(len(text) / CHARS_PER_TOKEN))


def estimate_tokens_obj(obj: Any) -> int:
    return estimate_tokens_text(canonical_json(obj))
