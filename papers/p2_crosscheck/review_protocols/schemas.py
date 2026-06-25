"""Detection-only verdict + repair schemas (manual 6.7).

All reviewers first emit a *detection-only* verdict; repair is a separate,
separately-scored stage so "happened to rewrite it correctly" is not counted as
review skill (manual 6.7). Both stages are pinned to JSON schemas validated with
``jsonschema`` and mirrored by small dataclasses for ergonomic construction.

Verdict (detection):
  verdict in {correct, defective, uncertain}
  findings[]: {file, line, defect_type (taxonomy enum), evidence, confidence, [claim]}
  recommended_tests[]: str
  estimated_risk in {low, medium, high}

Repair:
  patch: str (diff/text)
  rationale: str
  addressed_defect_types[]: taxonomy enum
  new_tests[]: str
  estimated_risk in {low, medium, high}
"""
from __future__ import annotations

from dataclasses import dataclass, field

import jsonschema

from papers.p2_crosscheck.defects.taxonomy import DefectType, all_defect_values

VERDICT_VALUES = ("correct", "defective", "uncertain")
RISK_VALUES = ("low", "medium", "high")


# --------------------------------------------------------------------------
# JSON schemas
# --------------------------------------------------------------------------
def finding_schema() -> dict:
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "file": {"type": "string"},
            "line": {"type": "integer", "minimum": 0},
            "defect_type": {"enum": all_defect_values()},
            "evidence": {"type": "string"},
            "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
            "claim": {"type": "string"},
        },
        "required": ["file", "line", "defect_type", "evidence", "confidence"],
    }


def verdict_schema() -> dict:
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "verdict": {"enum": list(VERDICT_VALUES)},
            "findings": {"type": "array", "items": finding_schema()},
            "recommended_tests": {"type": "array", "items": {"type": "string"}},
            "estimated_risk": {"enum": list(RISK_VALUES)},
        },
        "required": ["verdict", "findings", "recommended_tests", "estimated_risk"],
    }


def repair_schema() -> dict:
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "patch": {"type": "string"},
            "rationale": {"type": "string"},
            "addressed_defect_types": {
                "type": "array",
                "items": {"enum": all_defect_values()},
            },
            "new_tests": {"type": "array", "items": {"type": "string"}},
            "estimated_risk": {"enum": list(RISK_VALUES)},
        },
        "required": ["patch", "rationale"],
    }


# --------------------------------------------------------------------------
# Validation
# --------------------------------------------------------------------------
def _errors(payload: dict, schema: dict) -> list[str]:
    validator = jsonschema.Draft202012Validator(schema)
    errs = sorted(validator.iter_errors(payload), key=lambda e: list(e.path))
    return [f"{list(e.path)}: {e.message}" for e in errs]


def validate_verdict(payload: dict) -> list[str]:
    """Return a list of human-readable schema errors (empty == valid)."""
    return _errors(payload, verdict_schema())


def validate_repair(payload: dict) -> list[str]:
    return _errors(payload, repair_schema())


# --------------------------------------------------------------------------
# Dataclasses
# --------------------------------------------------------------------------
@dataclass
class Finding:
    file: str
    line: int
    defect_type: DefectType
    evidence: str
    confidence: float
    claim: str = ""

    def to_dict(self) -> dict:
        out = {
            "file": self.file,
            "line": int(self.line),
            "defect_type": DefectType(self.defect_type).value,
            "evidence": self.evidence,
            "confidence": float(self.confidence),
        }
        if self.claim:
            out["claim"] = self.claim
        return out


@dataclass
class DetectionVerdict:
    verdict: str
    findings: list[Finding] = field(default_factory=list)
    recommended_tests: list[str] = field(default_factory=list)
    estimated_risk: str = "low"

    def to_dict(self) -> dict:
        return {
            "verdict": self.verdict,
            "findings": [f.to_dict() for f in self.findings],
            "recommended_tests": list(self.recommended_tests),
            "estimated_risk": self.estimated_risk,
        }

    def validate(self) -> list[str]:
        return validate_verdict(self.to_dict())


@dataclass
class RepairProposal:
    patch: str
    rationale: str
    addressed_defect_types: list[DefectType] = field(default_factory=list)
    new_tests: list[str] = field(default_factory=list)
    estimated_risk: str = "low"

    def to_dict(self) -> dict:
        return {
            "patch": self.patch,
            "rationale": self.rationale,
            "addressed_defect_types": [
                DefectType(d).value for d in self.addressed_defect_types
            ],
            "new_tests": list(self.new_tests),
            "estimated_risk": self.estimated_risk,
        }

    def validate(self) -> list[str]:
        return validate_repair(self.to_dict())
