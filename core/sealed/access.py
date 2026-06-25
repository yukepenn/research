"""Sealed-test access controls / Test Custodian (COMMON-008, manual 1.3, 9.3).

Method-building agents must NOT read sealed-test labels (hidden tests, gold
impact sets, full-suite regressions) until the protocol is frozen. Only the
Test Custodian role may write/read labels; everyone else gets aggregate metrics
only, and label access before freeze raises. Every access is logged.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any

from core.util import sha256_obj, utc_now_iso

CUSTODIAN_ROLE = "test_custodian"


class SealedAccessError(PermissionError):
    pass


@dataclass
class SealedManifest:
    paper_id: str
    frozen: bool = False
    frozen_at: str | None = None
    protocol_hash: str | None = None
    access_log: list[dict] = field(default_factory=list)


class SealedTest:
    """A sealed split for one paper. Labels live under <root>/labels/ which is
    gitignored. Manifest tracks freeze status and an access log."""

    def __init__(self, root: str, paper_id: str):
        self.root = root
        self.paper_id = paper_id
        self.labels_dir = os.path.join(root, "labels")
        self.manifest_path = os.path.join(root, "manifest.json")
        os.makedirs(self.labels_dir, exist_ok=True)
        self._manifest = self._load_manifest()

    def _load_manifest(self) -> SealedManifest:
        if os.path.exists(self.manifest_path):
            with open(self.manifest_path, encoding="utf-8") as fh:
                d = json.load(fh)
            return SealedManifest(**d)
        return SealedManifest(paper_id=self.paper_id)

    def _save_manifest(self) -> None:
        with open(self.manifest_path, "w", encoding="utf-8") as fh:
            json.dump(self._manifest.__dict__, fh, indent=2)

    @property
    def frozen(self) -> bool:
        return self._manifest.frozen

    def _log(self, role: str, action: str, split: str, granted: bool) -> None:
        self._manifest.access_log.append({
            "at": utc_now_iso(), "role": role, "action": action,
            "split": split, "granted": granted,
        })
        self._save_manifest()

    # ---- custodian-only writes ----------------------------------------
    def store_labels(self, split: str, labels: Any, *, role: str) -> None:
        if role != CUSTODIAN_ROLE:
            self._log(role, "store_labels", split, False)
            raise SealedAccessError(f"role {role!r} cannot write sealed labels")
        with open(os.path.join(self.labels_dir, f"{split}.json"), "w", encoding="utf-8") as fh:
            json.dump(labels, fh)
        self._log(role, "store_labels", split, True)

    # ---- gated reads ---------------------------------------------------
    def get_labels(self, split: str, *, role: str) -> Any:
        allowed = role == CUSTODIAN_ROLE or self._manifest.frozen
        self._log(role, "get_labels", split, allowed)
        if not allowed:
            raise SealedAccessError(
                f"label access denied for role {role!r}: protocol not frozen. "
                "Only the Test Custodian may read labels before freeze."
            )
        with open(os.path.join(self.labels_dir, f"{split}.json"), encoding="utf-8") as fh:
            return json.load(fh)

    def aggregate_metrics(self, split: str, metric_fn, predictions, *, role: str) -> dict:
        """Return ONLY aggregate metrics (no labels) — allowed pre-freeze.

        metric_fn(labels, predictions) -> dict of scalar metrics. Custodian
        evaluates internally; caller never sees labels.
        """
        with open(os.path.join(self.labels_dir, f"{split}.json"), encoding="utf-8") as fh:
            labels = json.load(fh)
        self._log(role, "aggregate_metrics", split, True)
        out = metric_fn(labels, predictions)
        if not all(isinstance(v, (int, float)) for v in out.values()):
            raise SealedAccessError("aggregate_metrics must return only scalar metrics")
        return out

    # ---- freeze --------------------------------------------------------
    def freeze(self, protocol_hash: str, *, role: str) -> None:
        if role != CUSTODIAN_ROLE:
            raise SealedAccessError("only the custodian may freeze the protocol")
        self._manifest.frozen = True
        self._manifest.frozen_at = utc_now_iso()
        self._manifest.protocol_hash = protocol_hash
        self._save_manifest()


def protocol_hash_of(analysis_plan: dict) -> str:
    """Stable hash of a frozen analysis plan, bound into the sealed manifest."""
    return sha256_obj(analysis_plan)
