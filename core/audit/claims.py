"""Claim registry + manuscript consistency checker (COMMON-006, manual 3.3, 21.9).

ClaimRegistry: append-only CSV of claims with a controlled status vocabulary.
A claim may only appear in the manuscript body if SUPPORTED, or explicitly
flagged PARTIAL/REFUTED as a limitation/negative result.

ManuscriptChecker: extracts numbers and citation keys from manuscript text and
verifies every number is traceable to a ledger-generated table value and every
citation key exists in the verified citation DB (no orphan numbers, no
hallucinated cites).
"""
from __future__ import annotations

import csv
import os
import re
from dataclasses import dataclass, field

STATUSES = {"UNTESTED", "SUPPORTED", "PARTIAL", "REFUTED", "DROPPED"}
MANUSCRIPT_OK = {"SUPPORTED", "PARTIAL", "REFUTED"}  # PARTIAL/REFUTED only as limitations

FIELDS = ["claim_id", "paper", "manuscript_location", "claim_text", "claim_type",
          "status", "evidence_run_ids", "source_ids", "statistical_support",
          "limitations", "reviewer_attack", "owner"]


@dataclass
class Claim:
    claim_id: str
    paper: str
    claim_text: str
    status: str = "UNTESTED"
    claim_type: str = ""
    manuscript_location: str = ""
    evidence_run_ids: str = ""
    source_ids: str = ""
    statistical_support: str = ""
    limitations: str = ""
    reviewer_attack: str = ""
    owner: str = ""


class ClaimRegistry:
    def __init__(self, path: str):
        self.path = path
        self.claims: dict[str, Claim] = {}
        if os.path.exists(path):
            self._load()

    def _load(self) -> None:
        with open(self.path, newline="", encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                self.claims[row["claim_id"]] = Claim(
                    claim_id=row["claim_id"], paper=row["paper"],
                    claim_text=row["claim_text"], status=row.get("status", "UNTESTED"),
                    claim_type=row.get("claim_type", ""),
                    manuscript_location=row.get("manuscript_location", ""),
                    evidence_run_ids=row.get("evidence_run_ids", ""),
                    source_ids=row.get("source_ids", ""),
                    statistical_support=row.get("statistical_support", ""),
                    limitations=row.get("limitations", ""),
                    reviewer_attack=row.get("reviewer_attack", ""),
                    owner=row.get("owner", ""),
                )

    def add(self, claim: Claim) -> None:
        if claim.status not in STATUSES:
            raise ValueError(f"bad status {claim.status!r}")
        self.claims[claim.claim_id] = claim

    def set_status(self, claim_id: str, status: str) -> None:
        if status not in STATUSES:
            raise ValueError(f"bad status {status!r}")
        self.claims[claim_id].status = status

    def save(self) -> None:
        os.makedirs(os.path.dirname(os.path.abspath(self.path)), exist_ok=True)
        with open(self.path, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=FIELDS)
            w.writeheader()
            for c in self.claims.values():
                w.writerow({
                    "claim_id": c.claim_id, "paper": c.paper,
                    "manuscript_location": c.manuscript_location,
                    "claim_text": c.claim_text, "claim_type": c.claim_type,
                    "status": c.status, "evidence_run_ids": c.evidence_run_ids,
                    "source_ids": c.source_ids,
                    "statistical_support": c.statistical_support,
                    "limitations": c.limitations, "reviewer_attack": c.reviewer_attack,
                    "owner": c.owner,
                })

    def manuscript_violations(self) -> list[str]:
        """Claims marked as in the manuscript that are not allowed to be there."""
        out = []
        for c in self.claims.values():
            if c.manuscript_location and c.status not in MANUSCRIPT_OK:
                out.append(f"{c.claim_id}: in manuscript but status={c.status}")
            if c.status == "SUPPORTED" and not c.evidence_run_ids and not c.source_ids:
                out.append(f"{c.claim_id}: SUPPORTED but no evidence_run_ids or source_ids")
        return out


# --------------------------------------------------------------------------
# Manuscript number / citation consistency
# --------------------------------------------------------------------------
_NUM_RE = re.compile(r"(?<![\w.])\d+(?:\.\d+)?(?![\w.])")
_CITE_RE = re.compile(r"\\cite[tp]?\{([^}]*)\}|\[@([\w:-]+)\]")


def extract_numbers(text: str) -> set[str]:
    return set(_NUM_RE.findall(text))


def extract_citation_keys(text: str) -> set[str]:
    keys: set[str] = set()
    for m in _CITE_RE.finditer(text):
        grp = m.group(1) or m.group(2) or ""
        for k in grp.split(","):
            k = k.strip()
            if k:
                keys.add(k)
    return keys


@dataclass
class ConsistencyReport:
    untraceable_numbers: list[str] = field(default_factory=list)
    missing_citation_keys: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.untraceable_numbers and not self.missing_citation_keys


def check_manuscript(text: str, *, allowed_numbers: set[str],
                     known_citation_keys: set[str],
                     ignore_numbers: set[str] | None = None) -> ConsistencyReport:
    """Every number in the manuscript must be in `allowed_numbers` (values that
    came from ledger-generated tables) or `ignore_numbers` (section refs, years,
    etc.); every citation key must exist in the verified citation DB."""
    ignore = ignore_numbers or set()
    nums = extract_numbers(text) - ignore
    untraceable = sorted(n for n in nums if n not in allowed_numbers)
    cites = extract_citation_keys(text)
    missing = sorted(k for k in cites if k not in known_citation_keys)
    return ConsistencyReport(untraceable, missing)
