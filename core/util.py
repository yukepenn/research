"""Shared utilities: deterministic hashing, canonical JSON, content addressing, seeds.

These primitives are used everywhere the manual requires an immutable,
auditable trail (run ledger, trace hashes, environment hashes, prompt hashes).
Hashing must be stable across processes and OSes, so we canonicalise JSON
(sorted keys, no whitespace, UTF-8) before hashing.
"""
from __future__ import annotations

import hashlib
import json
import os
import random
from datetime import datetime, timezone
from typing import Any


def canonical_json(obj: Any) -> str:
    """Stable JSON string: sorted keys, compact separators, UTF-8 safe."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_obj(obj: Any) -> str:
    """Content hash of any JSON-serialisable object."""
    return sha256_text(canonical_json(obj))


def sha256_file(path: str, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(chunk), b""):
            h.update(block)
    return h.hexdigest()


def utc_now_iso() -> str:
    """ISO-8601 UTC timestamp with second precision."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def short_id(*parts: Any, length: int = 12) -> str:
    """Deterministic short id from the given parts (NOT random)."""
    return sha256_text("|".join(str(p) for p in parts))[:length]


def stable_seed(*parts: Any) -> int:
    """Map arbitrary parts to a stable 32-bit seed for reproducible RNG."""
    return int(sha256_text("|".join(str(p) for p in parts))[:8], 16)


def rng_for(*parts: Any) -> random.Random:
    """A seeded python Random bound to the given identity parts."""
    return random.Random(stable_seed(*parts))


def write_content_addressed(directory: str, payload: str) -> tuple[str, str]:
    """Write payload to <directory>/<sha256>.json and return (hash, path).

    Idempotent: re-writing identical content is a no-op. This is how raw
    traces are stored so a ledger entry can reference them by hash.
    """
    os.makedirs(directory, exist_ok=True)
    digest = sha256_text(payload)
    path = os.path.join(directory, f"{digest}.json")
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(payload)
    return digest, path
